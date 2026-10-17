"""Do co-tuned inputs cluster on the same dendritic branch? MICrONS cubic millimetre (issue #87)

For every postsynaptic neuron that receives synapses from at least two proofread, functionally
coregistered presynaptic neurons, take each pair of those input synapses (from two *different*
presynaptic neurons), measure how far apart they sit along the dendrite (skeleton path length) and
how similar their presynaptic neurons' tuning is. If co-tuned inputs cluster, nearby pairs should be
more similar than pairs on the same neuron in general.

Pre-registered (written into this docstring and the issue plan before the real-data run):
  Data       Ding et al. 2025 release (node_data_v1 / edge_data_v1: 148 proofread presynaptic neurons
             with digital-twin tuning, their connected partners), and the v661 pcg_skel meshworks of the
             postsynaptic neurons (skeleton + every input synapse mapped onto it).
  Neurons    postsynaptic neurons with a v661 meshwork and >= 2 distinct coregistered presynaptic
             neurons among their dendritic input synapses. Synapses on the axon or on the soma (the
             skeleton root, a 10 um collapsed sphere) are dropped.
  Similarity primary: in-silico signal correlation (Pearson r of the two neurons' digital-twin
             responses to the same natural movie, Ding et al.'s main metric). Secondary: readout
             (feature) similarity, receptive-field centre distance, in-vivo signal correlation.
  Near       primary: path distance <= 10 um along the skeleton. Secondary: same skeleton segment
             (the cable between two branch points), and the curve over distance bins.
  Statistic  T = mean similarity of near pairs - mean similarity of all pairs (pairs pooled).
  Null       within each postsynaptic neuron, permute which presynaptic neuron sits at which of its
             coregistered synapse sites (sites, branch lengths and synapse counts kept), 1,000 times.
             One-sided p for T > 0 (clustering), plus the two-sided p.
  Counts as  T at or below the null (p > 0.05): no evidence that co-tuned inputs share a branch at
  against    this scale, in this sample.

A deviation from the issue: the issue named `caveclient`. The CAVE servers were not reachable from
where this was first run, so the script reads the same tables from the public static release on
BossDB's S3 bucket (v661 meshworks, Ding et al. pickles). The pickles are loaded with a restricted
unpickler that only allows the pandas/numpy classes a DataFrame needs (pickle can run code).

Run: python research/cotuned_inputs.py               # analyse the saved snapshot in research/data/
     python research/cotuned_inputs.py --fetch       # download (~1 GB tables + ~5 GB meshworks), rebuild it
     python research/cotuned_inputs.py --synthetic   # pipeline check on SYNTHETIC neurons (not a result)
Needs numpy and scipy; --fetch also needs pandas and h5py.
"""
import argparse
import io
import os
import pickle
import re
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

S3 = "https://bossdb-open-data.s3.amazonaws.com/"
FC = "iarpa_microns/minnie/functional_data/functional_connectomics/node_and_edge_properties/v1/"
MW = "iarpa_microns/minnie/minnie65/skeletons/v661/meshworks/"
DATA = Path(__file__).parent / "data"
SNAP = DATA / "microns_cotuned_inputs_v661.npz"
CACHE = Path(os.environ.get("BRAIN_KB_CACHE", Path.home() / ".cache" / "brain-kb")) / "microns"
NEAR_UM, SHUFFLES = 10.0, 1000
SIMS = ("sig_corr_insilico", "readout_sim", "rf_dist_neg", "sig_corr_invivo")
BINS_UM = (0, 10, 25, 50, 100, 200, 400, np.inf)


# ---------------------------------------------------------------- download and build the snapshot
def get(key, dest):
    """Download one S3 object to dest (skipped if present)."""
    dest = Path(dest)
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        with urllib.request.urlopen(S3 + key, timeout=600) as r, open(tmp, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
        tmp.rename(dest)
    return dest


def list_keys(prefix):
    """All keys under an S3 prefix (public ListObjectsV2, paged)."""
    keys, token = [], None
    while True:
        q = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            q["continuation-token"] = token
        xml = urllib.request.urlopen(S3 + "?" + urllib.parse.urlencode(q), timeout=120).read().decode()
        keys += re.findall(r"<Key>([^<]*)</Key>", xml)
        m = re.search(r"<NextContinuationToken>([^<]*)</NextContinuationToken>", xml)
        if not m:
            return keys
        token = m.group(1)


def load_pickle(path):
    """Ding et al.'s DataFrames, unpickled with an allow-list (no arbitrary callables)."""
    import pandas as pd
    from pandas.compat import pickle_compat
    allow = {("pandas.core.frame", "DataFrame"), ("pandas.core.internals.managers", "BlockManager"),
             ("pandas._libs.internals", "_unpickle_block"), ("numpy.core.numeric", "_frombuffer"),
             ("numpy._core.numeric", "_frombuffer"), ("numpy", "dtype"), ("builtins", "slice"),
             ("pandas._libs.arrays", "__pyx_unpickle_NDArrayBacked"),
             ("pandas.core.arrays.categorical", "Categorical"), ("pandas.core.dtypes.dtypes", "CategoricalDtype"),
             ("pandas.core.indexes.base", "_new_Index"), ("pandas.core.indexes.base", "Index"),
             ("numpy.core.multiarray", "_reconstruct"), ("numpy._core.multiarray", "_reconstruct"),
             ("numpy", "ndarray"), ("pandas.core.indexes.numeric", "Int64Index"),
             ("pandas.core.indexes.range", "RangeIndex")}

    class Restricted(pickle_compat.Unpickler):
        def find_class(self, module, name):
            if (module, name) not in allow:
                raise pickle.UnpicklingError(f"refusing to load {module}.{name}")
            if name == "Int64Index":          # removed in pandas 2
                return pd.Index
            return super().find_class(module, name)

    with open(path, "rb") as f:
        return Restricted(f).load()


def pre_similarity(node, pre_nucs):
    """Matrices (n_pre x n_pre) of each similarity measure, larger = more alike."""
    node = node.set_index("nucleus_id").loc[pre_nucs]
    z = lambda X: (X - X.mean(1, keepdims=True)) / X.std(1, keepdims=True)
    unit = lambda X: X / np.linalg.norm(X, axis=1, keepdims=True)
    R = z(np.stack(node.in_silico_resp.to_numpy()).astype(float))
    V = z(np.stack(node.in_vivo_mean_resp.to_numpy()).astype(float))
    W = unit(np.stack([np.ravel(w) for w in node.readout_cvt]).astype(float))
    P = np.stack(node.position_stim_cvt.to_numpy()).astype(float).reshape(len(node), -1)[:, :2]
    rf = np.sqrt(((P[:, None] - P[None]) ** 2).sum(-1))
    return np.stack([R @ R.T / R.shape[1], W @ W.T, -rf, V @ V.T / V.shape[1]])


def neuron_sites(path, pre_root_to_idx):
    """Coregistered dendritic input synapses of one postsynaptic neuron.
    Returns (pre index per synapse, seg id per synapse, path-distance matrix in um), or None."""
    import h5py
    import pandas as pd
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    with h5py.File(path, "r") as f:
        tab = lambda k: pd.read_json(io.StringIO(f[f"annotations/{k}/data"][()].decode()))
        syn = tab("post_syn")
        syn = syn[syn.pre_pt_root_id.isin(pre_root_to_idx)]
        if syn.pre_pt_root_id.nunique() < 2:
            return None
        v = f["skeleton/vertices"][()]
        e = f["skeleton/edges"][()]
        m2s = f["skeleton/mesh_to_skel_map"][()]
        root = int(f["skeleton/root"][()])
        axon = set(m2s[tab("is_axon").mesh_index.to_numpy().astype(int)].tolist()) if "is_axon" in f["annotations"] else set()
        seg = tab("segment_properties").set_index("mesh_ind").seg_num
    sk = m2s[syn.post_pt_mesh_ind.to_numpy()]
    keep = np.array([s != root and s not in axon for s in sk])
    syn, sk = syn[keep], sk[keep]
    if syn.pre_pt_root_id.nunique() < 2:
        return None
    w = np.linalg.norm(v[e[:, 0]] - v[e[:, 1]], axis=1) / 1000.0     # nm -> um
    G = coo_matrix((w, (e[:, 0], e[:, 1])), shape=(len(v), len(v))).tocsr()
    D = dijkstra(G, directed=False, indices=np.unique(sk))
    col = {s: i for i, s in enumerate(np.unique(sk))}
    dist = D[[col[s] for s in sk]][:, sk]
    pre = np.array([pre_root_to_idx[r] for r in syn.pre_pt_root_id])
    return pre, seg.reindex(syn.post_pt_mesh_ind.to_numpy()).fillna(-1).to_numpy().astype(int), dist


def fetch(cache):
    """Download what the analysis needs and save the compact snapshot to research/data/."""
    node = load_pickle(get(FC + "node_data_v1.pkl", cache / "node_data_v1.pkl"))
    edge = load_pickle(get(FC + "edge_data_v1.pkl", cache / "edge_data_v1.pkl"))
    conn = edge[edge.population == "Connected"]
    pres = np.array(sorted(conn.pre_nucleus_id.unique()))
    print(f"Ding et al. 2025: {len(node)} coregistered neurons, {len(pres)} proofread presynaptic, "
          f"{len(conn)} connected pairs")
    listing = cache / "meshworks_v661.txt"
    if not listing.exists():
        listing.write_text("\n".join(k.rsplit("/", 1)[1] for k in list_keys(MW) if k.endswith(".h5")))
    by_nuc = {}
    for name in listing.read_text().split():
        root, nuc = name[:-3].split("_")
        by_nuc[int(nuc)] = (int(root), name)
    pre_root_to_idx = {by_nuc[n][0]: i for i, n in enumerate(pres) if n in by_nuc}
    k = conn.groupby("post_nucleus_id").pre_nucleus_id.nunique()
    posts = [int(p) for p in k[k >= 2].index if p in by_nuc]
    print(f"{len(posts)} postsynaptic neurons with >= 2 coregistered inputs in Ding et al.'s table")
    out = {"post": [], "pre": [], "seg": [], "i": [], "j": [], "path_um": []}
    n_syn = 0
    for c, post in enumerate(posts):
        name = by_nuc[post][1]
        path = get(MW + name, cache / "meshworks" / name)
        r = neuron_sites(path, pre_root_to_idx)
        if r is not None:
            pre, seg, dist = r
            i, j = np.triu_indices(len(pre), 1)
            out["post"] += [post] * len(pre); out["pre"] += pre.tolist(); out["seg"] += seg.tolist()
            out["i"] += (i + n_syn).tolist(); out["j"] += (j + n_syn).tolist(); out["path_um"] += dist[i, j].tolist()
            n_syn += len(pre)
        if c % 200 == 0:
            print(f"  {c}/{len(posts)} neurons, {n_syn} coregistered dendritic synapses so far")
    DATA.mkdir(exist_ok=True)
    np.savez_compressed(SNAP, pre_nucleus_id=pres, sim=pre_similarity(node, pres), sim_names=np.array(SIMS),
                        **{k: np.array(v) for k, v in out.items()})
    print(f"saved {SNAP}")


# ---------------------------------------------------------------- analysis
def load_snapshot(path):
    d = np.load(path)
    return {k: d[k] for k in d.files}


def stats(d, sim, pre, rng=None):
    """T (near - all) and T_seg (same segment - all) over pairs from different presynaptic neurons.
    With rng, the presynaptic labels are first permuted within each postsynaptic neuron."""
    if rng is not None:                      # shuffle labels within each postsynaptic neuron, vectorised
        new = pre.copy()
        new[d["order"]] = pre[np.lexsort((rng.random(len(pre)), d["post"]))]
        pre = new
    a, b = pre[d["i"]], pre[d["j"]]
    ok = a != b
    x = sim[a[ok], b[ok]]
    near, same = d["path_um"][ok] <= NEAR_UM, d["same_seg"][ok]
    return x[near].mean() - x.mean(), x[same].mean() - x.mean()


def prep(d):
    """Add the per-neuron ordering and the same-segment flag that stats() uses."""
    d["n_post"] = len(np.unique(d["post"]))
    d["order"] = np.argsort(d["post"], kind="stable")
    d["same_seg"] = (d["seg"][d["i"]] == d["seg"][d["j"]]) & (d["seg"][d["i"]] >= 0)
    return d["post"]


def analyse(d, shuffles=SHUFFLES, seed=0, label=""):
    """Print the pre-registered table; return {measure: (T, p_one_sided)}."""
    post = prep(d)
    a, b = d["pre"][d["i"]], d["pre"][d["j"]]
    ok = a != b
    near = d["path_um"][ok] <= NEAR_UM
    print(f"{label}{d['n_post']} postsynaptic neurons, {len(post)} coregistered dendritic synapses, "
          f"{ok.sum()} pairs from different presynaptic neurons ({near.sum()} within {NEAR_UM:g} um, "
          f"{d['same_seg'][ok].sum()} on the same segment)")
    rng = np.random.default_rng(seed)
    res = {}
    print(f"{'measure':18s} {'all':>7s} {'<=10um':>7s} {'T':>7s} {'p(T>0)':>7s} {'p two':>6s}"
          f" | {'same seg T':>10s} {'p(T>0)':>7s}")
    for k, name in enumerate(d["sim_names"]):
        sim = d["sim"][k]
        x = sim[a[ok], b[ok]]
        t, ts = stats(d, sim, d["pre"])
        null = np.array([stats(d, sim, d["pre"], rng) for _ in range(shuffles)])
        p1 = (1 + (null[:, 0] >= t).sum()) / (1 + shuffles)
        p2 = (1 + (np.abs(null[:, 0] - null[:, 0].mean()) >= abs(t - null[:, 0].mean())).sum()) / (1 + shuffles)
        ps = (1 + (null[:, 1] >= ts).sum()) / (1 + shuffles)
        res[str(name)] = (t, p1)
        print(f"{str(name):18s} {x.mean():7.3f} {x[near].mean() if near.any() else np.nan:7.3f} {t:+7.3f} {p1:7.3f}"
              f" {p2:6.3f} | {ts:+10.3f} {ps:7.3f}")
    sim = d["sim"][0]
    x, dist = sim[a[ok], b[ok]], d["path_um"][ok]
    print("primary similarity by path distance (um): " + "  ".join(
        f"{lo:g}-{hi:g}: {x[(dist > lo) & (dist <= hi)].mean():+.3f} (n={((dist > lo) & (dist <= hi)).sum()})"
        if lo else f"<= {hi:g}: {x[dist <= hi].mean():+.3f} (n={(dist <= hi).sum()})"
        for lo, hi in zip(BINS_UM[:-1], BINS_UM[1:]) if ((dist > lo) & (dist <= hi)).any()))
    return res


# ---------------------------------------------------------------- synthetic check
def synthetic(effect, seed=0, n_post=300, n_pre=150):
    """SYNTHETIC data, not MICrONS: random tuning, random dendrites. With effect > 0, each input synapse
    is moved next to an earlier input from the most similar presynaptic neuron with probability `effect`."""
    rng = np.random.default_rng(seed)
    R = rng.normal(size=(n_pre, 5)) @ rng.normal(size=(5, 200)) + rng.normal(size=(n_pre, 200))   # low-rank tuning
    R = (R - R.mean(1, keepdims=True)) / R.std(1, keepdims=True)
    sim = np.stack([R @ R.T / R.shape[1]] * len(SIMS))
    out = {"post": [], "pre": [], "seg": [], "i": [], "j": [], "path_um": []}
    n = 0
    for p in range(n_post):
        k = rng.integers(2, 12)
        pre = rng.choice(n_pre, k)
        seg = rng.integers(0, 40, k)                 # 40 segments of 50 um hanging off the soma
        pos = rng.uniform(0, 50, k)
        for s in range(1, k):
            if rng.random() < effect:
                best = np.argmax(sim[0, pre[s], pre[:s]] - 10 * (pre[:s] == pre[s]))
                seg[s], pos[s] = seg[best], np.clip(pos[best] + rng.normal(0, 3), 0, 50)
        dist = np.where(seg[:, None] == seg[None], np.abs(pos[:, None] - pos[None]), pos[:, None] + pos[None])
        i, j = np.triu_indices(k, 1)
        out["post"] += [p] * k; out["pre"] += pre.tolist(); out["seg"] += seg.tolist()
        out["i"] += (i + n).tolist(); out["j"] += (j + n).tolist(); out["path_um"] += dist[i, j].tolist()
        n += k
    d = {k: np.array(v) for k, v in out.items()}
    d.update(sim=sim, sim_names=np.array(SIMS), pre_nucleus_id=np.arange(n_pre))
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="download the release and rebuild the snapshot")
    ap.add_argument("--synthetic", action="store_true", help="run the pipeline on SYNTHETIC neurons only")
    ap.add_argument("--shuffles", type=int, default=SHUFFLES)
    ap.add_argument("--cache", type=Path, default=CACHE, help="where downloads go (default ~/.cache/brain-kb)")
    args = ap.parse_args()
    if args.synthetic:
        print("SYNTHETIC DATA - checks the code, says nothing about the brain")
        analyse(synthetic(0.0), args.shuffles, label="[synthetic, no clustering] ")
        plant = analyse(synthetic(0.3), args.shuffles, label="[synthetic, clustering planted] ")
        assert plant["sig_corr_insilico"][1] < 0.01, "planted clustering not detected"
        ps = []                                  # calibration: the null should reject ~5% of the time
        for seed in range(1, 41):
            d = synthetic(0.0, seed=seed)
            prep(d)
            t = stats(d, d["sim"][0], d["pre"])[0]
            rng = np.random.default_rng(seed)
            null = np.array([stats(d, d["sim"][0], d["pre"], rng)[0] for _ in range(200)])
            ps.append((1 + (null >= t).sum()) / 201)
        rate = np.mean(np.array(ps) < 0.05)
        print(f"[synthetic] false-positive rate at p < 0.05 over 40 no-clustering datasets: {rate:.2f}")
        assert rate <= 0.15, "null is miscalibrated"
        print("synthetic check passed: planted clustering found, the null rejects at about the nominal rate")
        return
    if args.fetch:
        fetch(args.cache)
    if not SNAP.exists():
        raise SystemExit(f"{SNAP} missing: run with --fetch first (or --synthetic for a pipeline check)")
    analyse(load_snapshot(SNAP), args.shuffles)


if __name__ == "__main__":
    main()
