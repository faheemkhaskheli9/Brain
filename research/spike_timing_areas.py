"""How much stimulus information does spike timing add to spike counts, per mouse visual area? (issue #86)

Allen Brain Observatory Visual Coding - Neuropixels (Siegle et al. 2021), the 32 "brain_observatory_1.1"
sessions. In each area (LGN, V1, LM, RL, AL, PM, AM; LP as an extra), decode which stimulus was shown
from 20 simultaneously recorded units, four ways, with the same decoder:
  (a) count     spikes in the 0-250 ms window after onset (one number per unit)
  (b) bins10    spike counts in 10 ms bins (25 per unit); bins5 = 5 ms bins (50 per unit)
  (c) latency   time of the first spike in the window (250 ms if none)
  (a+c)         count and latency together (exploratory)
Timing gain = accuracy(bins10) - accuracy(count). The binned code contains the count (the bins sum to
it), so a gain is information in *when* the spikes came, minus what the decoder loses to the extra
dimensions; it is a lower bound on the information in timing, for this decoder.

Pre-registered (written here and in the issue plan before the real-data run):
  Stimuli    natural scenes (118 images, 250 ms each, ~50 repeats; blank excluded) and drifting gratings
             (8 directions x 5 temporal frequencies at 0.8 contrast, ~15 repeats; blank excluded). Same
             0-250 ms window after onset for both. Presentations overlapping an invalid interval dropped.
  Units      Allen's default quality filter (ISI violations < 0.5, amplitude cutoff < 0.1, presence ratio
             > 0.9), assigned to an area by their peak channel. N = 20 units per area per session; sessions
             with fewer are skipped; 5 random draws of 20 per session, accuracies averaged over draws.
  Decoder    shrinkage LDA (Ledoit-Wolf, no tuning; numpy), features z-scored on the training folds,
             5-fold cross-validation stratified by stimulus.
  Statistic  per area: mean over sessions of the timing gain, 95% CI from 10,000 session bootstraps.
             Secondary: bins5 - count, latency - count, (a+c) - count; Spearman rank correlation of the
             per-area gain with the anatomical hierarchy order (LGd < VISp < VISl < VISrl < VISal <
             VISpm < VISam, the order used by Siegle et al. 2021).
  Prediction timing adds information in LGN and V1 (whose responses lock to grating phase, Siegle et
             al. 2021), less up the hierarchy. Counts against it: CIs that include 0 everywhere, or no
             decline with hierarchy.

A deviation from the issue: it named `allensdk`. The script reads the same NWB files straight from the
Allen S3 bucket with h5py + remfile (byte-range reads, only the needed arrays), because allensdk does not
install on current Python and api.brain-map.org was not reachable from where this was first run.

Run: python research/spike_timing_areas.py              # decode from the extracted cache, print the table
     python research/spike_timing_areas.py --fetch      # first extract trial-aligned spikes from S3
     python research/spike_timing_areas.py --synthetic  # pipeline check on SYNTHETIC data (not a result)
Needs numpy; --fetch also needs pandas, h5py and remfile (pip install pandas h5py remfile).
"""
import argparse
import csv
import datetime
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

S3 = "https://allen-brain-observatory.s3.amazonaws.com/visual-coding-neuropixels/ecephys-cache/"
CACHE = Path(os.environ.get("BRAIN_KB_CACHE", Path.home() / ".cache" / "brain-kb")) / "allen-vcn"
DATA = Path(__file__).parent / "data"
AREAS = ("LGd", "VISp", "VISl", "VISrl", "VISal", "VISpm", "VISam", "LP")
HIERARCHY = ("LGd", "VISp", "VISl", "VISrl", "VISal", "VISpm", "VISam")   # rank order, Siegle et al. 2021
WIN_MS, N_UNITS, DRAWS, FOLDS, BOOT = 250, 20, 5, 5, 10000
CODES = ("count", "bins10", "bins5", "latency", "count+latency")
STIMS = ("natural_scenes", "drifting_gratings")


# ---------------------------------------------------------------- data download / extraction
def units_table(cache):
    """Quality units of the brain_observatory_1.1 sessions in the target areas: (session, unit id, area)."""
    import pandas as pd
    import urllib.request
    cache.mkdir(parents=True, exist_ok=True)
    for f in ("sessions.csv", "units.csv", "channels.csv", "probes.csv"):
        if not (cache / f).exists():
            urllib.request.urlretrieve(S3 + f, cache / f)
    s = pd.read_csv(cache / "sessions.csv")
    u = pd.read_csv(cache / "units.csv")
    c = pd.read_csv(cache / "channels.csv")[["id", "ecephys_probe_id", "ecephys_structure_acronym"]]
    p = pd.read_csv(cache / "probes.csv")[["id", "ecephys_session_id"]]
    u = u.merge(c.rename(columns={"id": "ecephys_channel_id"}), on="ecephys_channel_id")
    u = u.merge(p.rename(columns={"id": "ecephys_probe_id"}), on="ecephys_probe_id")
    u = u[u.ecephys_session_id.isin(s.id[s.session_type == "brain_observatory_1.1"])]
    u = u[(u.isi_violations < 0.5) & (u.amplitude_cutoff < 0.1) & (u.presence_ratio > 0.9)]
    return u[u.ecephys_structure_acronym.isin(AREAS)][["ecephys_session_id", "id", "ecephys_structure_acronym"]]


def extract_session(sid, units, out):
    """Trial-aligned spikes of one session, read by byte ranges from the session NWB on S3."""
    import h5py
    import remfile
    url = f"{S3}session_{sid}/session_{sid}.nwb"
    with h5py.File(remfile.File(url), "r") as f:
        ids = f["units/id"][()]
        idx = f["units/spike_times_index"][()]
        row = {u: i for i, u in enumerate(ids)}
        bad = np.zeros((0, 2))
        if "invalid_times" in f["intervals"]:
            iv = f["intervals/invalid_times"]
            bad = np.column_stack([iv["start_time"][()], iv["stop_time"][()]])
        stims = {}
        ns = f["intervals/natural_scenes_presentations"]
        frame, t0 = ns["frame"][()], ns["start_time"][()]
        stims["natural_scenes"] = (t0[frame >= 0], frame[frame >= 0].astype(int))
        dg = f["intervals/drifting_gratings_presentations"]
        ori, tf, t0 = dg["orientation"][()], dg["temporal_frequency"][()], dg["start_time"][()]
        if ori.dtype.kind in "SO":
            ori = np.array([float(x) if x not in (b"null", "null") else np.nan for x in ori])
            tf = np.array([float(x) if x not in (b"null", "null") else np.nan for x in tf])
        ok = ~np.isnan(ori) & ~np.isnan(tf)
        lab = np.unique(np.column_stack([ori[ok], tf[ok]]), axis=0, return_inverse=True)[1].ravel()
        stims["drifting_gratings"] = (t0[ok], lab)
        res = {"unit_ids": units.id.to_numpy(), "areas": units.ecephys_structure_acronym.to_numpy().astype(str)}
        trains = []
        for u in units.id:
            r = row[u]
            lo = idx[r - 1] if r else 0
            trains.append(f["units/spike_times"][lo:idx[r]])
    for name, (t0, lab) in stims.items():
        keep = ~((t0[:, None] < bad[None, :, 1]) & (t0[:, None] + WIN_MS / 1000 > bad[None, :, 0])).any(1)
        t0, lab = t0[keep], lab[keep]
        tr, un, ms = [], [], []
        for k, st in enumerate(trains):
            a = np.searchsorted(st, t0)
            b = np.searchsorted(st, t0 + WIN_MS / 1000)
            for i in np.flatnonzero(b > a):
                d = ((st[a[i]:b[i]] - t0[i]) * 1000).astype(np.int16)
                tr.append(np.full(len(d), i, np.int32)); un.append(np.full(len(d), k, np.int16)); ms.append(d)
        cat = lambda x, t: np.concatenate(x) if x else np.zeros(0, t)
        res[f"{name}_labels"] = lab.astype(np.int16)
        res[f"{name}_spikes"] = np.column_stack([cat(tr, np.int32), cat(un, np.int16), cat(ms, np.int16)])
    np.savez_compressed(out, **res)


def fetch(cache):
    units = units_table(cache)
    sessions = sorted(units.ecephys_session_id.unique())
    print(f"{len(sessions)} brain_observatory_1.1 sessions, {len(units)} quality units in {AREAS}")
    for k, sid in enumerate(sessions):
        out = cache / f"session_{sid}_trials.npz"
        if not out.exists():
            extract_session(sid, units[units.ecephys_session_id == sid], out)
        print(f"  {k + 1}/{len(sessions)} session {sid} extracted", flush=True)


# ---------------------------------------------------------------- features and decoder
def features(spikes, labels, units, code):
    """Trials x features matrix for a subset of units (indices into the session's unit list)."""
    n, k = len(labels), len(units)
    pos = np.full(spikes[:, 1].max(initial=0) + 1 if len(spikes) else 1, -1)
    pos[units] = np.arange(k)
    s = spikes[(spikes[:, 1] < len(pos))]
    s = s[pos[s[:, 1]] >= 0]
    tr, un, ms = s[:, 0], pos[s[:, 1]], s[:, 2].astype(int)
    if code.startswith("bins"):
        w = int(code[4:])
        nb = WIN_MS // w
        X = np.zeros((n, k * nb))
        np.add.at(X, (tr, un * nb + np.minimum(ms // w, nb - 1)), 1)
        return X
    cnt = np.zeros((n, k))
    np.add.at(cnt, (tr, un), 1)
    lat = np.full((n, k), float(WIN_MS))
    np.minimum.at(lat, (tr, un), ms)
    return {"count": cnt, "latency": lat, "count+latency": np.hstack([cnt, lat])}[code]


def lda_cv(X, y, rng, folds=FOLDS):
    """Cross-validated accuracy of shrinkage LDA (Ledoit-Wolf), folds stratified by class."""
    fold = np.empty(len(y), int)
    for c in np.unique(y):
        i = np.flatnonzero(y == c)
        fold[rng.permutation(i)] = np.arange(len(i)) % folds
    correct = 0
    for f in range(folds):
        tr, te = fold != f, fold == f
        mu, sd = X[tr].mean(0), X[tr].std(0)
        sd[sd == 0] = 1
        Xtr, Xte = (X[tr] - mu) / sd, (X[te] - mu) / sd
        cls, yi = np.unique(y[tr], return_inverse=True)
        M = np.zeros((len(cls), X.shape[1]))
        np.add.at(M, yi, Xtr)
        M /= np.bincount(yi)[:, None]
        Z = Xtr - M[yi]
        n, p = Z.shape
        S = Z.T @ Z / n
        m = np.trace(S) / p
        d2 = (S ** 2).sum() - p * m ** 2
        b2 = ((Z ** 2).sum(1) ** 2).sum() / n ** 2 - (S ** 2).sum() / n
        lam = 1.0 if d2 <= 0 else float(np.clip(b2 / d2, 0, 1))
        C = (1 - lam) * S + lam * m * np.eye(p)
        W = np.linalg.solve(C + 1e-9 * np.eye(p), M.T)
        score = Xte @ W - 0.5 * (M * W.T).sum(1) + np.log(np.bincount(yi) / n)
        correct += (cls[score.argmax(1)] == y[te]).sum()
    return correct / len(y)


def decode_session(path, seed=0):
    """Rows (session, stimulus, area, n_units, draws, accuracy per code) for one extracted session."""
    d = np.load(path, allow_pickle=False)
    rows = []
    rng = np.random.default_rng(seed)
    for stim in STIMS:
        y, sp = d[f"{stim}_labels"].astype(int), d[f"{stim}_spikes"]
        for area in AREAS:
            pool = np.flatnonzero(d["areas"] == area)
            if len(pool) < N_UNITS:
                continue
            acc = np.zeros((DRAWS, len(CODES)))
            for r in range(DRAWS):
                units = rng.choice(pool, N_UNITS, replace=False)
                for c, code in enumerate(CODES):
                    acc[r, c] = lda_cv(features(sp, y, units, code), y, np.random.default_rng(r))
            rows.append([Path(path).stem.split("_")[1], stim, area, len(pool), DRAWS] + acc.mean(0).round(4).tolist())
    return rows


# ---------------------------------------------------------------- summary
def summarise(rows, boot=BOOT, seed=0):
    """Per stimulus x area: mean accuracy per code and gains vs count with session-bootstrap CIs."""
    rng = np.random.default_rng(seed)
    out = {}
    for stim in STIMS:
        k = 118 if stim == "natural_scenes" else 40
        print(f"\n{stim} (chance {1 / k:.3f}); accuracy, then gain over count with 95% session-bootstrap CI")
        print(f"{'area':6s} {'n':>3s} " + " ".join(f"{c:>13s}" for c in CODES)
              + f" {'bins10-count':>24s} {'bins5-count':>24s} {'latency-count':>24s}")
        for area in AREAS:
            r = np.array([x[5:] for x in rows if x[1] == stim and x[2] == area], float)
            if not len(r):
                continue
            gains = {}
            line = f"{area:6s} {len(r):3d} " + " ".join(f"{m:13.3f}" for m in r.mean(0))
            for c in ("bins10", "bins5", "latency"):
                g = r[:, CODES.index(c)] - r[:, 0]
                bs = np.array([rng.choice(g, len(g)).mean() for _ in range(boot)])
                lo, hi = np.percentile(bs, [2.5, 97.5])
                gains[c] = (g.mean(), lo, hi)
                line += f" {g.mean():+8.3f} [{lo:+.3f},{hi:+.3f}]"
            out[(stim, area)] = gains
            print(line)
        h = [a for a in HIERARCHY if (stim, a) in out]
        if len(h) >= 4:
            rank = lambda v: np.argsort(np.argsort(v))
            g = np.array([out[(stim, a)]["bins10"][0] for a in h])
            rho = np.corrcoef(rank(np.arange(len(h))), rank(g))[0, 1]
            print(f"Spearman rho, bins10 gain vs hierarchy rank ({len(h)} areas): {rho:+.2f}")
    return out


def save_rows(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["session", "stimulus", "area", "n_quality_units", "draws"] + [f"acc_{c}" for c in CODES])
        w.writerows(rows)


# ---------------------------------------------------------------- synthetic check
def synthetic_session(path, seed):
    """SYNTHETIC data, not Allen: area 'VISp' carries stimulus identity in spike *latency* only (same
    rate for every stimulus); area 'VISam' carries it in rate only (latency fixed)."""
    rng = np.random.default_rng(seed)
    res = {"unit_ids": np.arange(60), "areas": np.array(["VISp"] * 30 + ["VISam"] * 30)}
    for stim, k, reps in (("natural_scenes", 20, 30), ("drifting_gratings", 10, 15)):
        y = np.repeat(np.arange(k), reps)
        lat_pref = rng.uniform(30, 120, (60, k))         # ms; used by the timing area
        rate_pref = rng.uniform(2, 10, (60, k))          # spikes per window; used by the rate area
        tr, un, ms = [], [], []
        for i, s in enumerate(y):
            for u in range(60):
                timing = u < 30
                n = rng.poisson(6 if timing else rate_pref[u, s])
                t0 = lat_pref[u, s] if timing else 60.0
                t = np.sort(t0 + rng.exponential(25, n)) if n else np.zeros(0)
                t = t[t < WIN_MS]
                tr += [i] * len(t); un += [u] * len(t); ms += t.astype(int).tolist()
        res[f"{stim}_labels"] = y.astype(np.int16)
        res[f"{stim}_spikes"] = np.column_stack([tr, un, ms]).astype(np.int32)
    np.savez_compressed(path, **res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="extract trial-aligned spikes from the S3 NWB files")
    ap.add_argument("--synthetic", action="store_true", help="run the pipeline on SYNTHETIC sessions only")
    ap.add_argument("--cache", type=Path, default=CACHE, help="where extracted sessions go")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    args = ap.parse_args()
    if args.synthetic:
        global AREAS, HIERARCHY
        print("SYNTHETIC DATA - checks the code, says nothing about the brain")
        AREAS, HIERARCHY = ("VISp", "VISam"), ()
        syn = args.cache / "synthetic"
        syn.mkdir(parents=True, exist_ok=True)
        paths = [syn / f"session_{s}_trials.npz" for s in range(4)]
        for s, p in enumerate(paths):
            synthetic_session(p, s)
        rows = [r for p in paths for r in decode_session(p)]
        out = summarise(rows, boot=1000)
        for stim in STIMS:
            assert out[(stim, "VISp")]["latency"][1] > 0.1, "planted latency code not found"
            assert out[(stim, "VISp")]["bins10"][1] > 0, "planted timing code not found by bins"
            assert out[(stim, "VISam")]["latency"][2] < 0, "rate-only area should decode worse from latency"
        print("synthetic check passed: timing gain where timing was planted, none where only rate was")
        return
    if args.fetch:
        fetch(args.cache)
    paths = sorted(args.cache.glob("session_*_trials.npz"))
    if not paths:
        raise SystemExit(f"no extracted sessions in {args.cache}: run with --fetch first (or --synthetic)")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    with ProcessPoolExecutor(args.jobs) as ex:
        rows = [r for rs in ex.map(decode_session, paths) for r in rs]
    DATA.mkdir(exist_ok=True)
    out = DATA / f"allen_vcn_timing_{datetime.date.today()}.csv"
    save_rows(rows, out)
    print(f"{len(paths)} sessions decoded; per-session accuracies saved to {out}")
    summarise(rows)


if __name__ == "__main__":
    main()
