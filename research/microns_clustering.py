"""Do co-tuned inputs cluster on the same dendritic branch? A MICrONS test (issue #87).

For each excitatory neuron in the MICrONS cubic millimetre that gets synapses from at least 3 different
functionally imaged neurons with proofread axons, every pair of those input synapses gets (a) a tuning
similarity of the two presynaptic neurons and (b) a geometry on the postsynaptic dendrite: path distance
along the skeleton, same unbranched segment, same primary dendrite. If co-tuned inputs cluster, nearby
pairs are more similar than the same synapses with their presynaptic labels shuffled within the neuron.

Tuning comes from the MICrONS digital twin (Wang et al. 2025; Ding et al. 2025): feature similarity =
cosine of the 512-d readout weights (primary), RF-centre distance (readout location), and the difference
in preferred orientation for pairs where both are tuned (gOSI >= 0.25).
Null A (from #87): permute which presynaptic neuron sits at which synapse position within each neuron,
which keeps positions, branch lengths, synapse counts and partner sets. Null B: the same, but only among
synapses on the same primary dendrite. 1,000 shuffles, one-sided p. Method pre-registered on #87 plus an
addendum written before any synapse position was read (thresholds, metrics, null B; see the topic file).
Exploratory, added after the first result: distance between the presynaptic somata, and RF distance minus
its mean at that soma distance (25-um bins), to ask whether RF clustering is more than retinotopy.

Data: all public, no CAVE token. Materialization v1300 synapses and cell table, v1412 manual coregistration
table, the digital twin v2 export, and v1300 dendrite skeletons (SWC, one per neuron). MICrONS data are
CC BY 4.0 (microns-explorer.org/terms-and-conditions); cite MICrONS Consortium 2025, doi:10.1038/s41586-025-08790-w.

Run: python research/microns_clustering.py --download   # one-off: 20.0 GB, about 2 h at 3 MB/s, then a
                                                        # ~20-min filter to a 100 MB synapse file
     python research/microns_clustering.py              # analysis: fetches 22,767 skeletons (3.3 GB,
                                                        # ~20 min), then ~15 min CPU (an hour on a busy machine)
     python research/microns_clustering.py --quick      # 100 neurons, 50 shuffles
     python research/microns_clustering.py --selftest   # planted-clustering check, no data needed
Options: --min-inputs N, --proofread-dendrites, --shuffles N, --data-dir PATH, --out CSV.
"""
import argparse
import http.client
import struct
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

MAT = "https://storage.googleapis.com/mat_dbs/public/minnie65_phase3_v1"
DT = "https://bossdb-open-data.s3.amazonaws.com/iarpa_microns/minnie/functional_data/digital_twin_properties/v2"
SWC = "https://storage.googleapis.com/microns-static-links/skel/swc/dendrite"
SYN = "v1300/synapses_pni_2_v1_filtered_view"
FILES = {f"{t}{s}": f"{MAT}/{t}{s}" for t in (SYN, "v1300/aibs_cell_info", "v1412/coregistration_manual_v4_merged")
         for s in (".csv.gz", "_header.csv")}
FILES.update({f"dt_v2/{p}": f"{DT}/{p}" for p in ("readout/readout_weights.npy", "readout/readout_locations.npy",
                                                   "readout/units.csv", "performance/units.csv", "ori_dir_tuning/units.csv")})
VOXEL_UM = np.array([0.004, 0.004, 0.040])   # synapse positions are in 4 x 4 x 40 nm voxels; SWC is in um
MAX_SNAP_UM = 5.0                            # synapse farther than this from the skeleton: dropped
BINS = (0, 5, 10, 20, 50, 100, 200, np.inf)  # path-distance bins, um
UNIT_KEY = ["session", "scan_idx", "unit_id"]


def fetch(url, path, tries=30):
    """Download url to path through path.part, resuming after dropped connections. A body shorter than
    Content-Length is resumed, never renamed to the final name."""
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + ".part")
    for _ in range(tries):
        have = part.stat().st_size if part.exists() else 0
        req = urllib.request.Request(url, headers={"Range": f"bytes={have}-"} if have else {})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                have = have if r.status == 206 else 0                    # 200: server sent the whole file
                n = r.headers.get("Content-Length")
                with open(part, "ab" if have else "wb") as f:
                    while chunk := r.read(1 << 22):
                        f.write(chunk)
            if n is None or part.stat().st_size == have + int(n):
                part.replace(path)
                return path
            print(f"  retry {path.name}: short read")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise FileNotFoundError(url) from e
            if e.code == 416:                                           # stale .part: start again
                part.unlink()
            print(f"  retry {path.name}: {e}")
        except (OSError, http.client.HTTPException) as e:               # URLError, timeouts, resets, IncompleteRead
            print(f"  retry {path.name}: {e}")
        time.sleep(10)
    raise RuntimeError(f"could not download {url}")


def read_mat(d, name, **kw):
    """A materialization dump: headerless .csv.gz plus a (column, type) header file."""
    cols = list(pd.read_csv(d / f"{name}_header.csv", header=None)[0])
    return pd.read_csv(d / f"{name}.csv.gz", header=None, names=cols, **kw)


def cells(d):
    """v1300 cell table indexed by nucleus id, one nucleus per root id."""
    c = read_mat(d, "v1300/aibs_cell_info")
    c = c[(c.pt_root_id != 0) & ~c.pt_root_id.duplicated(keep=False)]
    return c.set_index("id")


def download(d):
    for rel, url in FILES.items():
        print("fetch", rel)
        fetch(url, d / rel)
    out = d / "synapses_axon_proofread_v1300.csv"
    if out.exists():
        return
    roots = set(cells(d).query("axon_cleaned == 't'").pt_root_id)   # every proofread axon, coregistered or not
    use = ["id", "post_pt_position_x", "post_pt_position_y", "post_pt_position_z", "size", "pre_pt_root_id",
           "post_pt_root_id"]
    keep, n, t0 = [], 0, time.time()
    for ch in read_mat(d, SYN, usecols=use, chunksize=5_000_000):
        keep.append(ch[ch.pre_pt_root_id.isin(roots)])
        n += len(ch)
        print(f"  filtered {n / 1e6:.0f} M synapses, kept {sum(map(len, keep)):,} ({time.time() - t0:.0f} s)")
    pd.concat(keep).to_csv(out, index=False)


def tuning(d):
    """Per coregistered nucleus: digital-twin row, cc, RF location, gOSI and preferred orientation."""
    co = read_mat(d, "v1412/coregistration_manual_v4_merged")[["target_id"] + UNIT_KEY]
    rows = pd.read_csv(d / "dt_v2/readout/units.csv").reset_index(names="row")
    f = (co.merge(rows, on=UNIT_KEY).merge(pd.read_csv(d / "dt_v2/performance/units.csv"), on=UNIT_KEY)
         .merge(pd.read_csv(d / "dt_v2/ori_dir_tuning/units.csv"), on=UNIT_KEY))
    f = f[(f.cc_abs > 0.2) & (f.cc_max > 0.4)]                       # Ding et al. 2025 inclusion thresholds
    return f.sort_values("cc_abs").drop_duplicates("target_id", keep="last").set_index("target_id")


def load_swc(path):
    """(xyz um, parent row or -1, soma row) from a SWC file. The soma is the first root node."""
    a = np.loadtxt(path, comments="#", ndmin=2)
    row = {int(n): i for i, n in enumerate(a[:, 0])}
    par = np.array([row.get(int(p), -1) for p in a[:, 6]])
    return a[:, 2:5], par, int(np.flatnonzero(par < 0)[0])


def tree_labels(par, soma):
    """Unbranched-segment id and primary-dendrite id per node; -1 where not connected to the soma."""
    n = len(par)
    kids = [[] for _ in range(n)]
    for c, p in enumerate(par):
        if p >= 0:
            kids[p].append(c)
    seg, stem = np.full(n, -1), np.full(n, -1)
    stack, nseg = [], 0
    for c in kids[soma]:
        seg[c] = stem[c] = nseg
        nseg += 1
        stack.append(c)
    while stack:
        p = stack.pop()
        for c in kids[p]:
            stem[c] = stem[p]
            if len(kids[p]) == 1:
                seg[c] = seg[p]
            else:
                seg[c], nseg = nseg, nseg + 1
            stack.append(c)
    return seg, stem


def neuron_pairs(xyz, par, soma, syn_um):
    """Snap synapses to the skeleton. Returns the kept-synapse mask, the primary-dendrite id of each kept
    synapse, and for every pair (i < j) of kept synapses: path distance, same segment, same dendrite."""
    dist, node = cKDTree(xyz).query(syn_um)
    seg, stem = tree_labels(par, soma)
    ok = (dist <= MAX_SNAP_UM) & (node != soma) & (stem[node] >= 0)
    node = node[ok]
    i, j = np.triu_indices(len(node), 1)
    if len(i) == 0:
        return ok, stem[node], i, j, np.zeros(0), np.zeros(0, bool), np.zeros(0, bool)
    c = np.flatnonzero(par >= 0)
    w = np.linalg.norm(xyz[c] - xyz[par[c]], axis=1) + 1e-9          # tiny offset keeps zero-length edges
    g = csr_matrix((w, (c, par[c])), shape=(len(par),) * 2)
    u, inv = np.unique(node, return_inverse=True)
    pd_ = dijkstra(g, directed=False, indices=u)[:, u][inv[i], inv[j]]
    return ok, stem[node], i, j, pd_, seg[node[i]] == seg[node[j]], stem[node[i]] == stem[node[j]]


def permute_within(groups, rng):
    """Index array p such that x[p] shuffles x only among entries with the same group."""
    base = np.argsort(groups, kind="stable")
    order = np.lexsort((rng.random(len(groups)), groups))
    p = np.empty_like(order)
    p[base] = order
    return p


def run_tests(pre, groups_a, groups_b, pi, pj, masks, metrics, n_shuffle, rng):
    """Observed mean per (metric, mask) over pairs from different presynaptic cells, and both nulls."""
    m = np.asarray(list(masks.values()), np.float64)

    def stats(lab):
        a, b = lab[pi], lab[pj]
        out = []
        for M in metrics.values():
            v = M[a, b]
            ok = (a != b) & ~np.isnan(v)
            out.append((m @ np.where(ok, v, 0.0)) / np.maximum(m @ ok, 1))
        return np.array(out)

    obs = stats(pre)
    nulls = {k: np.array([stats(pre[permute_within(g, rng)]) for _ in range(n_shuffle)])
             for k, g in (("A", groups_a), ("B", groups_b))}
    a, b = pre[pi], pre[pj]
    counts = np.array([[int(((a != b) & ~np.isnan(M[a, b]) & mk).sum()) for mk in masks.values()]
                       for M in metrics.values()])
    return obs, nulls, counts


def report(obs, nulls, counts, masks, metrics, higher):
    rows = []
    for a, met in enumerate(metrics):
        for c, mask in enumerate(masks):
            if counts[a, c] == 0:                                       # empty category: no mean to test
                continue
            r = {"metric": met, "pairs": mask, "n_pairs": counts[a, c], "observed": obs[a, c]}
            for k, nl in nulls.items():
                x = nl[:, a, c]
                tail = (x >= obs[a, c]) if higher[met] else (x <= obs[a, c])
                r |= {f"null{k}_mean": x.mean(), f"null{k}_lo": np.percentile(x, 2.5),
                      f"null{k}_hi": np.percentile(x, 97.5), f"p{k}": (1 + tail.sum()) / (1 + len(x))}
            rows.append(r)
    return pd.DataFrame(rows)


def masks_for(dist, same_seg, same_stem):
    m = {f"{lo:g}-{hi:g} um": (dist >= lo) & (dist < hi) for lo, hi in zip(BINS[:-1], BINS[1:])}
    return {"<=10 um": dist <= 10, **m, "same segment": same_seg, "same dendrite": same_stem,
            "other dendrite": ~same_stem, "all": np.ones_like(same_seg)}


def analyse(d, min_inputs, proofread_dendrites, n_shuffle, quick, seed, out):
    rng = np.random.default_rng(seed)
    c, f = cells(d), tuning(d)
    pre_cells = c[(c.axon_cleaned == "t") & (c.broad_type == "excitatory") & c.index.isin(f.index)]
    post_cells = c[c.broad_type == "excitatory"]
    if proofread_dendrites:
        post_cells = post_cells[post_cells.dendrite_cleaned == "t"]
    syn = pd.read_csv(d / "synapses_axon_proofread_v1300.csv")
    pre_idx = pd.Series(np.arange(len(pre_cells)), index=pre_cells.pt_root_id.values)
    syn = syn[syn.pre_pt_root_id.isin(pre_idx.index) & syn.post_pt_root_id.isin(post_cells.pt_root_id)
              & (syn.pre_pt_root_id != syn.post_pt_root_id)]
    syn = syn.assign(pre=pre_idx.loc[syn.pre_pt_root_id].values)
    k = syn.groupby("post_pt_root_id").pre.nunique()
    posts = np.sort(k.index[k >= min_inputs].values)
    print(f"presynaptic cells: {len(pre_cells)} (axon proofread, coregistered, cc_abs > 0.2, cc_max > 0.4)")
    print(f"synapses from them onto excitatory cells: {len(syn):,}; postsynaptic cells with >= {min_inputs} "
          f"distinct inputs: {len(posts)}")
    if quick:
        posts = posts[:100]

    def swc(r):
        try:
            return fetch(f"{SWC}/{r}.swc", d / "swc_v1300" / f"{r}.swc")
        except FileNotFoundError:
            return None

    with ThreadPoolExecutor(64) as ex:   # ~23k small files: latency-bound, so many parallel requests
        have = np.array([p is not None for p in ex.map(swc, posts)], bool)
    print(f"no public v1300 skeleton for {(~have).sum()} of them; skipped")
    posts = posts[have]

    lab, ga, gb, PI, PJ, D, SS, ST = [], [], [], [], [], [], [], []
    n_syn = n_drop = n_used = off = 0
    xyz_cols = ["post_pt_position_x", "post_pt_position_y", "post_pt_position_z"]
    for r, s in syn[syn.post_pt_root_id.isin(posts)].groupby("post_pt_root_id"):
        xyz, par, soma = load_swc(d / "swc_v1300" / f"{r}.swc")
        ok, stem, i, j, dist, same_seg, same_stem = neuron_pairs(xyz, par, soma, s[xyz_cols].values * VOXEL_UM)
        n_syn, n_drop = n_syn + len(s), n_drop + int((~ok).sum())
        p = s.pre.values[ok]
        if len(np.unique(p)) < min_inputs:
            continue
        lab.append(p)
        ga.append(np.full(len(p), n_used))
        gb.append(n_used * 100000 + stem)                               # (neuron, primary dendrite) groups
        PI.append(i + off)
        PJ.append(j + off)
        D.append(dist)
        SS.append(same_seg)
        ST.append(same_stem)
        n_used, off = n_used + 1, off + len(p)
    pre, ga, gb = map(np.concatenate, (lab, ga, gb))
    pi, pj, dist, same_seg, same_stem = map(np.concatenate, (PI, PJ, D, SS, ST))
    print(f"synapses {n_syn:,}, dropped (off skeleton, soma, detached) {n_drop:,}; neurons used {n_used}; "
          f"input synapses {len(pre):,}; pairs {len(pi):,}")

    w = np.load(d / "dt_v2/readout/readout_weights.npy", mmap_mode="r", allow_pickle=False)
    loc = np.load(d / "dt_v2/readout/readout_locations.npy", allow_pickle=False)
    fr = f.loc[pre_cells.index]
    wv = np.asarray(w[fr.row.values], np.float64)
    wv /= np.linalg.norm(wv, axis=1, keepdims=True)
    xy = loc[fr.row.values]
    ori = np.where(fr.gOSI.values >= 0.25, fr.pref_ori.values % 180, np.nan)   # degrees, 0-180
    dori = np.abs(ori[:, None] - ori[None, :])
    rf = np.linalg.norm(xy[:, None] - xy[None, :], axis=2)
    # exploratory: soma distance, and RF distance relative to its mean at that soma distance (retinotopy)
    soma = np.array([struct.unpack("<3d", bytes.fromhex(h)[5:29]) for h in pre_cells.pt_position]) * VOXEL_UM
    sd = np.linalg.norm(soma[:, None] - soma[None, :], axis=2)
    sbin = np.minimum(sd // 25, 40).astype(int)
    iu = np.triu_indices(len(sd), 1)
    rf_at = np.bincount(sbin[iu], rf[iu], 41) / np.maximum(np.bincount(sbin[iu], minlength=41), 1)
    metrics = {"feature similarity": wv @ wv.T, "RF distance": rf, "delta ori (deg)": np.minimum(dori, 180 - dori),
               "soma distance (um)": sd, "RF distance - mean at soma distance": rf - rf_at[sbin]}
    higher = {m: m == "feature similarity" for m in metrics}
    masks = masks_for(dist, same_seg, same_stem)
    obs, nulls, counts = run_tests(pre, ga, gb, pi, pj, masks, metrics, n_shuffle, rng)
    res = report(obs, nulls, counts, masks, metrics, higher)
    with pd.option_context("display.width", 200, "display.max_rows", 100, "display.float_format", "{:.4f}".format):
        print(res.to_string(index=False))
    if out:
        res.to_csv(out, index=False, float_format="%.5g", lineterminator="\n")
        print("saved", out)
    return res


def selftest():
    """Planted clustering must be found and a random layout must not be."""
    rng = np.random.default_rng(1)
    n_pre, n_neur, per = 40, 60, 12
    tune = rng.normal(size=(n_pre, 8))
    tune /= np.linalg.norm(tune, axis=1, keepdims=True)
    metrics = {"sim": tune @ tune.T}
    for planted in (True, False):
        lab, ga, PI, PJ, D = [], [], [], [], []
        for k in range(n_neur):
            p = rng.choice(n_pre, per, replace=False)
            pos = rng.uniform(0, 300, per)                              # positions on one 300-um dendrite
            if planted:   # order inputs along the dendrite by their first tuning axis: neighbours co-tuned
                pos = np.sort(pos)[np.argsort(np.argsort(tune[p, 0]))]
            i, j = np.triu_indices(per, 1)
            off = k * per
            lab.append(p)
            ga.append(np.full(per, k))
            PI.append(i + off)
            PJ.append(j + off)
            D.append(np.abs(pos[i] - pos[j]))
        pre, ga = np.concatenate(lab), np.concatenate(ga)
        dist = np.concatenate(D)
        masks = {"<=10 um": dist <= 10}
        obs, nulls, counts = run_tests(pre, ga, ga, np.concatenate(PI), np.concatenate(PJ), masks, metrics, 200, rng)
        p = report(obs, nulls, counts, masks, metrics, {"sim": True}).pA.iloc[0]
        print(f"selftest planted={planted}: near-pair similarity {obs[0, 0]:.3f}, null {nulls['A'][:, 0, 0].mean():.3f}, p = {p:.3f}")
        assert (p < 0.01) if planted else (p > 0.01)
    x = np.array([0, 0, 1, 1, 1, 2])
    q = permute_within(x, rng)
    assert all(sorted(q[x == g]) == sorted(np.flatnonzero(x == g)) for g in range(3))
    xyz = np.array([[0, 0, 0], [10, 0, 0], [20, 0, 0], [10, 5, 0], [-10, 0, 0]], float)
    par = np.array([-1, 0, 1, 1, 0])                                   # soma, a fork at node 1, a second dendrite
    ok, stem, i, j, dist, ss, st = neuron_pairs(xyz, par, 0, xyz[[2, 3, 4]] + 0.1)
    assert ok.all() and np.allclose(dist, [15, 30, 25], atol=0.5) and list(ss) == [False, False, False]
    assert list(st) == [True, False, False] and stem[0] == stem[1] != stem[2]
    print("selftest passed")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--download", action="store_true", help="fetch the public tables and filter the synapses")
    ap.add_argument("--quick", action="store_true", help="100 postsynaptic neurons, 50 shuffles")
    ap.add_argument("--selftest", action="store_true", help="synthetic checks only, no data")
    ap.add_argument("--min-inputs", type=int, default=3)
    ap.add_argument("--proofread-dendrites", action="store_true", help="only postsynaptic cells with cleaned dendrites")
    ap.add_argument("--shuffles", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--data-dir", type=Path, default=Path.home() / ".cache/brain-kb/microns")
    ap.add_argument("--out", type=Path, help="save the result table as CSV")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.download:
        download(a.data_dir)
    analyse(a.data_dir, a.min_inputs, a.proofread_dendrites, 50 if a.quick else a.shuffles, a.quick, a.seed, a.out)


if __name__ == "__main__":
    main()
