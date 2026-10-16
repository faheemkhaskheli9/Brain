"""How much stimulus information does spike timing carry beyond spike counts, per mouse visual area? (issue #86)

Data: Allen Brain Observatory Visual Coding Neuropixels (Siegle et al. 2021), brain_observatory_1.1 sessions,
118 natural scenes (250 ms each, ~50 repeats) and drifting gratings (8 directions x 5 temporal frequencies,
15 repeats). For each area (LGd, VISp, VISl, VISrl, VISal, VISpm, VISam) and session, draw N units at random
(the same N in every area), take the first 250 ms after stimulus onset, and decode stimulus identity with one
decoder (shrinkage LDA, 5-fold stratified CV) from six codes of the same spikes:
  count      spikes in 0-250 ms, one number per unit            (a: the rate code)
  bins50     counts in 50 ms bins (5 per unit)                  coarse time course
  bins10     counts in 10 ms bins (25 per unit)                 (b: timing, primary)
  bins5      counts in 5 ms bins (50 per unit)                  (b: timing, secondary)
  latency    first-spike time after onset, 250 ms if no spike   (c)
  count+lat  count and latency together                         (does latency add to the count?)
  jit50      bins10 after moving each spike to a random time inside its own 50 ms bin (added after the smoke
             run, not pre-registered): same dimension as bins10, same 50 ms counts, no finer timing
Timing gain = accuracy(code) - accuracy(count) per session, averaged over unit draws; fine timing =
accuracy(bins10) - accuracy(jit50). 95% CIs bootstrap the sessions. The primary family (bins10 gain, 7 areas x 2
stimulus sets = 14 contrasts) also gets Bonferroni percentile CIs at alpha = 0.05/14 from the same resamples;
every other gain is exploratory and uncorrected. Units pass the Siegle et al. 2021 filters
(ISI violations < 0.5, amplitude cutoff < 0.1, presence ratio > 0.95) and are labelled "good". Method
pre-registered in function/neural-coding-and-computation.md.

Data access needs no allensdk: the script reads each session NWB file with h5py over plain HTTPS range
requests from the Allen S3 bucket and fetches only the spike trains of the units it uses (about 150 MB per
session instead of the 2-3 GB file; about 10 minutes per session on a slow link). It caches the spikes inside
the response windows in ~/.cache/brain-kb/allen-neuropixels/session_<id>_windows.npz (about 20 MB each). A whole
NWB file already placed in that folder as session_<id>.nwb is read locally instead. Per-session accuracies are
cached there too (result_<id>_n<N>_r<R>.json), so a rerun only prints the tables. The caches are keyed by
session, N and R only: delete them after changing the window, MAXU, the unit filters, the codes or the decoder.

Run: python research/timing_vs_count.py [--quick] [--sessions K] [--units N] [--draws R] [--jobs J] [--data-dir DIR]
     --quick: one session, 8 units, 1 draw (a smoke run). Runtime: see function/neural-coding-and-computation.md.
"""
import argparse
import http.client
import io
import json
import os
import time
import urllib.request
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # sessions run in parallel processes, one BLAS thread each
import h5py
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import StratifiedKFold, cross_val_score

URL = ("https://allen-brain-observatory.s3.us-west-2.amazonaws.com/visual-coding-neuropixels/"
       "ecephys-cache/session_{0}/session_{0}.nwb")
# brain_observatory_1.1 sessions with the most of the 7 areas holding >= 20 filtered units, ranked from the
# Allen cache tables (sessions.csv, units.csv, channels.csv, probes.csv in the same bucket).
SESSIONS = (755434585, 756029989, 750749662, 754312389, 715093703, 751348571, 760345702, 799864342,
            791319847, 750332458)
AREAS = ("LGd", "VISp", "VISl", "VISrl", "VISal", "VISpm", "VISam")
WIN, MAXU = 0.25, 40          # response window (s); at most 40 units per area are fetched per session
CODES = ("count", "bins50", "bins10", "bins5", "latency", "count+lat", "jit50")
FAMILY = 14                   # primary contrasts: bins10 gain, 7 areas x 2 stimulus sets (Bonferroni)


class HTTPRange(io.RawIOBase):
    """Read-only seekable file over HTTP range requests (64 kB block cache), so h5py can read a remote NWB."""
    B = 2**16

    def __init__(self, url):
        self.url, self.pos, self.cache, self.nbytes = url, 0, {}, 0
        head = urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=60)
        self.size = int(head.headers["Content-Length"])

    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.pos

    def seek(self, off, whence=0):
        self.pos = (off, self.pos + off, self.size + off)[whence]
        return self.pos

    def get(self, a, b):
        for k in range(10):                   # retry for about 4 minutes (DNS and S3 hiccups)
            try:
                req = urllib.request.Request(self.url, headers={"Range": f"bytes={a}-{b - 1}"})
                with urllib.request.urlopen(req, timeout=300) as r:
                    d = r.read()
                if len(d) == b - a:
                    self.nbytes += len(d)
                    return d
            except (OSError, http.client.HTTPException):
                if k == 9:
                    raise
            time.sleep(min(2 ** k, 60))
        raise OSError(f"short read {a}-{b} from {self.url}")

    def readinto(self, buf):
        n = min(len(buf), self.size - self.pos)
        if n <= 0:
            return 0
        if n > 8 * self.B:   # big read (spike trains): one request, not cached
            buf[:n] = self.get(self.pos, self.pos + n)
        else:
            i0, i1 = self.pos // self.B, (self.pos + n - 1) // self.B
            miss = [i for i in range(i0, i1 + 1) if i not in self.cache]
            if miss:
                d = self.get(miss[0] * self.B, min((miss[-1] + 1) * self.B, self.size))
                for k, i in enumerate(range(miss[0], miss[-1] + 1)):
                    self.cache[i] = d[k * self.B:(k + 1) * self.B]
            o = self.pos - i0 * self.B
            buf[:n] = b"".join(self.cache[i] for i in range(i0, i1 + 1))[o:o + n]
        self.pos += n
        return n


def load(sid, data_dir):
    """Units (area, spikes inside the response windows) and stimulus tables of one session, cached as .npz."""
    cache = data_dir / f"session_{sid}_windows.npz"
    if not cache.exists():
        nwb = data_dir / f"session_{sid}.nwb"
        src = open(nwb, "rb") if nwb.exists() else HTTPRange(URL.format(sid))
        t0 = time.time()
        with h5py.File(src, "r") as h:
            u, e = h["units"], h["general/extracellular_ephys/electrodes"]
            area_of = dict(zip(e["id"][:], e["location"][:].astype(str), strict=True))
            area = np.array([area_of.get(c, "") for c in u["peak_channel_id"][:]])
            ok = ((u["quality"][:].astype(str) == "good") & (u["isi_violations"][:] < 0.5)
                  & (u["amplitude_cutoff"][:] < 0.1) & (u["presence_ratio"][:] > 0.95) & np.isin(area, AREAS))
            rng = np.random.default_rng(sid)
            keep = np.concatenate([rng.permutation(np.flatnonzero(ok & (area == a)))[:MAXU] for a in AREAS])
            keep.sort()
            ns, dg = h["intervals/natural_scenes_presentations"], h["intervals/drifting_gratings_presentations"]
            ns_t, ns_y = ns["start_time"][:], ns["frame"][:]
            dg_t, ori, tf = dg["start_time"][:], dg["orientation"][:], dg["temporal_frequency"][:]
            good = np.isfinite(ori) & np.isfinite(tf)                     # drop blank sweeps
            dg_t, ori, tf = dg_t[good], ori[good], tf[good]
            dg_y = np.unique(ori, return_inverse=True)[1] * 10 + np.unique(tf, return_inverse=True)[1]
            ns_t, ns_y = ns_t[ns_y >= 0], ns_y[ns_y >= 0]                  # frame -1 is the blank screen
            onsets = np.sort(np.concatenate([ns_t, dg_t]))
            end = h["units/spike_times_index"][:]
            st = h["units/spike_times"]
            off = st.id.get_offset()
            assert st.chunks is None and st.compression is None and st.dtype == "<f8"
            start = np.concatenate([[0], end[:-1]])
            spikes = []
            for i in keep:                                                 # one range request per unit
                src.seek(off + 8 * start[i])
                s = np.frombuffer(src.read(8 * (end[i] - start[i])), "<f8")
                j = np.searchsorted(onsets, s, side="right") - 1           # keep spikes inside some window
                spikes.append(s[(j >= 0) & (s - onsets[np.maximum(j, 0)] < WIN)])
        nbytes = getattr(src, "nbytes", 0)
        src.close()
        n = np.array([len(s) for s in spikes])
        tmp = cache.with_suffix(f".{os.getpid()}.tmp.npz")
        np.savez_compressed(tmp, area=area[keep], n=n, spikes=np.concatenate(spikes),
                            ns_t=ns_t, ns_y=ns_y.astype(int), dg_t=dg_t, dg_y=dg_y)
        tmp.replace(cache)
        print(f"  session {sid}: {len(keep)} units, {nbytes / 1e6:.0f} MB fetched in {time.time() - t0:.0f} s")
    z = np.load(cache)
    spikes = np.split(z["spikes"], np.cumsum(z["n"])[:-1])
    return z["area"], spikes, {"scenes": (z["ns_t"], z["ns_y"]), "gratings": (z["dg_t"], z["dg_y"])}


def binned(spikes, onsets, nb):
    """Spike counts in nb equal bins of the window: trials x units x nb."""
    edges = onsets[:, None] + np.arange(nb + 1) * (WIN / nb)
    return np.stack([np.diff(np.searchsorted(s, edges), axis=1) for s in spikes], 1)


def jitter(s, onsets, rng, w=0.05):
    """Move each spike in a window to a random time inside its own 50 ms bin: keeps bins50, removes finer timing."""
    on = np.sort(onsets)
    j = np.searchsorted(on, s, side="right") - 1
    rel = s - on[np.maximum(j, 0)]
    m = (j >= 0) & (rel < WIN)
    s = s.copy()
    s[m] = on[j[m]] + (rel[m] // w + rng.random(m.sum())) * w
    return np.sort(s)


def codes(spikes, onsets, rng):
    """Every code of the same spikes: dict name -> (trials, features)."""
    x5 = binned(spikes, onsets, 50)                                        # 5 ms bins
    first = np.stack([np.append(s, np.inf)[np.searchsorted(s, onsets)] - onsets for s in spikes], 1)
    lat = np.minimum(first, WIN)
    t, n = x5.shape[:2]
    count = x5.sum(2)
    return {"count": count, "bins50": x5.reshape(t, n, 5, 10).sum(3).reshape(t, -1),
            "bins10": x5.reshape(t, n, 25, 2).sum(3).reshape(t, -1), "bins5": x5.reshape(t, -1),
            "latency": lat, "count+lat": np.hstack([count, lat]),
            "jit50": binned([jitter(s, onsets, rng) for s in spikes], onsets, 25).reshape(t, -1)}


def decode(x, y, seed):
    cv = StratifiedKFold(5, shuffle=True, random_state=seed)
    lda = LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")
    return cross_val_score(lda, x, y, cv=cv, error_score="raise").mean()


def onset_latency(spikes, onsets):
    """Population PSTH half-rise time (ms) after onset: a pipeline check (LGN and V1 should lead).
    Baseline = the mean of the first 20 ms after onset (2 ms bins, 10 ms box smoothing), taken as activity
    before the visual response arrives. The cache keeps no spikes before onset, so the grey period itself is
    not used; a response that starts within 20 ms would inflate the baseline and delay the half-rise."""
    s, onsets = np.concatenate(spikes), np.sort(onsets)
    j = np.searchsorted(onsets, s, side="right") - 1
    rel = s - onsets[np.maximum(j, 0)]
    h = np.histogram(rel[(j >= 0) & (rel < WIN)] * 1000, bins=np.arange(0, 251, 2))[0].astype(float)
    h = np.convolve(h, np.ones(5) / 5, "same")
    base = h[:10].mean()
    return 2 * int(np.argmax(h > base + 0.5 * (h.max() - base)))


def boot_ci(v, rng, b=10000):
    """Percentile CIs of the mean from b resamples of sessions: uncorrected 95% (lo, hi), then Bonferroni
    family-wise 95% at alpha = 0.05 / FAMILY (lo, hi), both from the same resamples."""
    m = rng.choice(v, (b, len(v))).mean(1)
    a = 5 / FAMILY
    return np.percentile(m, [2.5, 97.5, a / 2, 100 - a / 2])


def selfcheck():
    """Codes on synthetic spikes: counts add up, jitter keeps 50 ms counts and moves spikes within them."""
    rng = np.random.default_rng(1)
    onsets = np.arange(20) * 0.3
    spikes = [np.sort(rng.uniform(0, 6, 400)) for _ in range(3)]
    c = codes(spikes, onsets, rng)
    assert (c["bins10"].reshape(20, 3, 25).sum(2) == c["count"]).all() and c["bins5"].shape == (20, 150)
    j = [jitter(s, onsets, rng) for s in spikes]
    assert (binned(j, onsets, 5) == binned(spikes, onsets, 5)).all() and (c["latency"] <= WIN).all()
    assert (binned(j, onsets, 25) != binned(spikes, onsets, 25)).any()


def run_session(sid, units, draws, data_dir):
    """Accuracy per code for each "stimulus|area" of one session, averaged over unit draws (cached as JSON),
    and the PSTH latency check per area (on gratings: each follows 1 s of grey, so the first 20 ms after onset
    reflect grey-screen activity; scenes follow each other with no gap)."""
    area, spikes, stims = load(sid, data_dir)
    for stim, (onsets, y) in stims.items():   # blanks must be gone; windows must (almost) never overlap (jit50):
        overlap = (np.diff(np.sort(onsets)) < WIN).mean()   # session 756029989 has one 233 ms scene gap in 5899
        assert overlap < 0.001 and len(np.unique(y)) == {"scenes": 118, "gratings": 40}[stim]
    keep = [ar for ar in AREAS if (area == ar).sum() >= units]
    lat = {ar: onset_latency([spikes[i] for i in np.flatnonzero(area == ar)], stims["gratings"][0]) for ar in keep}
    done = data_dir / f"result_{sid}_n{units}_r{draws}.json"
    if done.exists() and json.loads(done.read_text())["codes"] == list(CODES):
        return json.loads(done.read_text())["acc"], lat
    rng, out = np.random.default_rng(sid), {}
    for ar in keep:
        idx = np.flatnonzero(area == ar)
        for stim, (onsets, y) in stims.items():
            acc = np.zeros(len(CODES))
            for r in range(draws):
                c = codes([spikes[i] for i in rng.choice(idx, units, replace=False)], onsets, rng)
                acc += [decode(c[k], y, r) for k in CODES]
            out[f"{stim}|{ar}"] = list(acc / draws)
            print(f"  {sid} {stim:8s} {ar:5s} "
                  + " ".join(f"{k}={v:.3f}" for k, v in zip(CODES, acc / draws, strict=True)), flush=True)
    tmp = done.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_bytes(json.dumps({"codes": list(CODES), "acc": out}).encode())
    tmp.replace(done)
    return out, lat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="1 session, 8 units, 1 draw")
    ap.add_argument("--sessions", type=int, default=len(SESSIONS))
    ap.add_argument("--units", type=int, default=20, help="matched unit count per area")
    ap.add_argument("--draws", type=int, default=5, help="random unit subsets per session and area")
    ap.add_argument("--jobs", type=int, default=4, help="sessions processed in parallel")
    ap.add_argument("--data-dir", type=Path, default=Path.home() / ".cache/brain-kb/allen-neuropixels")
    a = ap.parse_args()
    if not 1 <= a.units <= MAXU:
        ap.error(f"--units must be between 1 and {MAXU}: load() fetches at most {MAXU} units per area")
    selfcheck()
    if a.quick:
        a.sessions, a.units, a.draws = 1, 8, 1
    a.data_dir.mkdir(parents=True, exist_ok=True)
    t0, rng = time.time(), np.random.default_rng(0)
    res, lat = {}, {}   # "stim|area" -> per-session accuracy vectors over CODES; area -> latencies
    with ProcessPoolExecutor(a.jobs) as ex:
        for out, la in ex.map(run_session, SESSIONS[:a.sessions], repeat(a.units), repeat(a.draws),
                              repeat(a.data_dir)):
            for k, v in out.items():
                res.setdefault(k, []).append(v)
            for k, v in la.items():
                lat.setdefault(k, []).append(v)
    print("\nPSTH half-rise latency, drifting gratings (ms, median over sessions): "
          + ", ".join(f"{ar} {np.median(lat[ar]):.0f}" for ar in AREAS if ar in lat))
    fam = {}   # (stim, area) -> bins10 gain, uncorrected CI, Bonferroni CI
    for stim, chance in (("scenes", 1 / 118), ("gratings", 1 / 40)):
        print(f"\n{stim}: {a.units} units per area, {a.draws} draws, chance {chance:.3f}. Accuracy (mean over "
              "sessions); gain = code - count; fine = bins10 - jit50; mean [uncorrected 95% bootstrap CI over "
              "sessions]")
        gains = list(CODES[1:6])
        print("| Area | Sessions | " + " | ".join(CODES) + " | " + " | ".join(f"{k} gain" for k in gains)
              + " | fine |")
        print("|---|---|" + "---|" * (len(CODES) + len(gains) + 1))
        for ar in AREAS:
            v = np.array(res.get(f"{stim}|{ar}", []))
            if len(v) == 0:
                continue
            g = [v[:, CODES.index(k)] - v[:, 0] for k in gains] + [v[:, 2] - v[:, CODES.index("jit50")]]
            cis = [boot_ci(d, rng) for d in g]
            fam[(stim, ar)] = (g[1].mean(), *cis[1])                      # g[1] = bins10 gain
            print(f"| {ar} | {len(v)} | " + " | ".join(f"{m:.3f}" for m in v.mean(0)) + " | "
                  + " | ".join(f"{d.mean():+.3f} [{c[0]:+.3f}, {c[1]:+.3f}]" for d, c in zip(g, cis, strict=True))
                  + " |")
    print(f"\nPrimary family: bins10 gain, {len(fam)} contrasts. Uncorrected 95% CI, then Bonferroni percentile CI at "
          f"alpha = 0.05/{FAMILY} from the same session resamples (family-wise 95%); * = Bonferroni CI excludes 0. "
          "All other columns are exploratory and uncorrected.")
    for (stim, ar), (m, lo, hi, blo, bhi) in fam.items():
        print(f"  {stim:8s} {ar:5s} {m:+.3f} [{lo:+.3f}, {hi:+.3f}]  Bonferroni [{blo:+.3f}, {bhi:+.3f}]"
              + (" *" if blo > 0 or bhi < 0 else ""))
    print(f"\nruntime {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
