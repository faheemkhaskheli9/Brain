"""Working-memory capacity: slots or resource? A cross-validated re-fit on open colour-wheel data (issue #90)

Fits four models of delayed-estimation (colour-wheel) errors to every subject, jointly across set sizes:
slots (item limit), slots + averaging, variable precision (VP; van den Berg et al. 2012) and TCC (target
confusability competition, uncorrelated noise, published colour similarity function; Schurgin, Wixted &
Brady 2020). Scores each by 10-fold cross-validated log likelihood. Data: the colour-wheel sets of the
van den Berg, Awh & Ma (2014) benchmark (E1, E2, E3, E8) and the Schurgin et al. (2020) set-size
experiment. Neither source states a licence, so the raw data stay in the cache; only per-subject scores
are written to research/data/. Method pre-registered in function/attention-and-working-memory.md.
A descriptive result: it says which account of the error distributions generalises, not what neurons do.

Run: python research/wm_capacity.py [--quick] [--folds 10] [--recovery 10] [--jobs N] [--data-dir DIR]
     Downloads about 180 MB on the first run (mostly the TCC OSF archive). Full run with 6 workers on a busy
     machine: about 25 minutes for the fits plus 40 for the recovery control (--recovery 0 skips it);
     --quick: about 3 minutes.
"""
import argparse
import csv
import hashlib
import os
import urllib.request
import zipfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy import io, optimize, special

BENCH = ("vdb2014", "https://github.com/NYUMaLab/delayed_estimation_benchmark/archive/refs/heads/master.zip",
         "benchmark.zip")
TCC_OSF = ("schurgin2020", "https://osf.io/download/y32c8/", "TCC_Code_InManuscriptOrder.zip")
SETS = {"E1": "Wilken & Ma 2004", "E2": "Zhang & Luck 2008", "E3": "Bays et al. 2009",
        "E8": "van den Berg et al. 2012", "SWB": "Schurgin et al. 2020"}
MODELS = ("slots", "slots+avg", "VP", "TCC")
OUT = Path(__file__).parent / "data" / "wm_capacity_results.csv"

E = np.arange(360)                                   # bin k = error of k degrees (mod 360)
COS = np.cos(np.deg2rad(E))
SIGNED = np.where(E > 180, E - 360, E)
CIRC = (E[None, :] - E[:, None]) % 360               # kernel[CIRC] is the circulant convolution matrix
KAP = np.logspace(-4, 4.5, 4000)                     # von Mises concentration grid
JOFK = KAP * special.i1e(KAP) / special.i0e(KAP)     # Fisher information J(kappa) = kappa I1/I0
DGRID = np.linspace(0, 10, 1001)                     # TCC d' table grid
Q = 40                                               # gamma quantiles for VP
LO, HI = np.log(0.01), np.log(3e4)
TCC_TABLE = LOG_TABLE = None                         # set per process by _init


# ---------------------------------------------------------------- data
def fetch(data_dir, spec):
    sub, url, name = spec
    path = Path(data_dir) / sub / name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading {url} -> {path}")
        urllib.request.urlretrieve(url, f"{path}.part")
        os.replace(f"{path}.part", path)          # an interrupted download never looks finished
    return path


def load_subjects(data_dir):
    """List of dicts: set, id, N (set size per trial), err (degrees), res (bin width in degrees)."""
    subs = []
    with zipfile.ZipFile(fetch(data_dir, BENCH)) as z:
        for exp in ("E1", "E2", "E3", "E8"):
            names = sorted((n for n in z.namelist() if f"/data/{exp}_subject_" in n),
                           key=lambda n: int(n.rsplit("_", 1)[1][:-4]))
            for n in names:
                d = io.loadmat(z.open(n), squeeze_me=True, struct_as_record=False)["data"]
                err = np.rad2deg(np.asarray(d.error_vec, float))
                res = 2 if exp in ("E2", "E8") else 1      # E2, E8 stimuli take 180 values (2-degree steps)
                subs.append(dict(set=exp, id=n.rsplit("/", 1)[1][:-4], N=np.asarray(d.N, int), err=err, res=res))
    with zipfile.ZipFile(fetch(data_dir, TCC_OSF)) as z:
        d = io.loadmat(z.open("Figure3/A_InLabHighSetSize.mat"), squeeze_me=True)
        for i in range(d["errors"].shape[0]):
            ok = ~np.isnan(d["errors"][i])
            subs.append(dict(set="SWB", id=f"SWB_subject_{i + 1}", N=d["setSize"][i][ok].astype(int),
                             err=d["errors"][i][ok].astype(float), res=1))
    return subs


def similarity(data_dir):
    """TCC's measured colour similarity f(error), from the authors' archive, on the bins E."""
    with zipfile.ZipFile(fetch(data_dir, TCC_OSF)) as z:
        v = io.loadmat(z.open("Model/Color_ConfusionVector.mat"), squeeze_me=True)["confusionVector"]
    return np.asarray(v, float)[SIGNED + 179]           # authors' index i <-> error i - 179 degrees


# ---------------------------------------------------------------- model predictions: rows of P(bin | N)
def vm(kappa):
    k = np.atleast_1d(kappa)[:, None]
    p = np.exp(k * (COS - 1))
    return p / p.sum(1, keepdims=True)


def conv(P, kernel):
    """Circular convolution as a circulant matmul: no FFT round-off, so tiny tail probabilities stay exact."""
    out = P @ kernel[CIRC]
    return out / out.sum(-1, keepdims=True)


def kappa_of_j(J):
    return np.interp(J, JOFK, KAP)


def motor_kernel(sd=2.0):
    """Gaussian motor noise, s.d. 2 degrees, truncated at 3 s.d., as in the TCC authors' code."""
    g = np.where(np.abs(SIGNED) <= 3 * sd, np.exp(-0.5 * (SIGNED / sd) ** 2), 0)
    return g / g.sum()


def tcc_table(f):
    """P(report bin | d') for uncorrelated-noise TCC on DGRID, then 2-degree motor noise."""
    m = np.linspace(-4, 16, 801)[:, None]
    rows = []
    for d in DGRID:
        z = m - d * f[None, :]
        lphi_cdf = special.log_ndtr(z)
        integrand = np.exp(-0.5 * z ** 2 - 0.5 * np.log(2 * np.pi) - lphi_cdf + lphi_cdf.sum(1, keepdims=True))
        rows.append(integrand.sum(0))   # uniform m grid; rows are normalised below
    P = np.array(rows)
    return conv(P / P.sum(1, keepdims=True), motor_kernel())


def tcc_rows(dprime):
    x = np.clip(np.asarray(dprime, float), 0, DGRID[-1]) / (DGRID[1] - DGRID[0])
    i = np.minimum(x.astype(int), len(DGRID) - 2)
    w = (x - i)[:, None]
    return (1 - w) * TCC_TABLE[i] + w * TCC_TABLE[i + 1]


def predict(model, th, ns, K=None):
    """P(bin | N) for each set size in ns. th is the unconstrained parameter vector."""
    ns = np.asarray(ns, float)
    uni = np.full(360, 1 / 360)
    if model == "slots":
        pm = np.minimum(1, K / ns)[:, None]
        return pm * vm(np.exp(th[0])) + (1 - pm) * uni
    if model == "slots+avg":
        J1, kr = np.exp(th[0]), np.exp(th[1])
        rows = []
        for n in ns:
            if n >= K:   # K items get one quantum each, the rest are guessed
                rows.append(K / n * vm(kappa_of_j(J1))[0] + (1 - K / n) * uni)
            else:        # quanta spread as evenly as possible: K mod n items get one extra
                hi = (K % n) / n
                m = K // n
                rows.append(hi * vm(kappa_of_j((m + 1) * J1))[0] + (1 - hi) * vm(kappa_of_j(m * J1))[0])
        return conv(np.array(rows), vm(kr)[0])
    if model == "VP":
        J1, alpha, tau, kr = np.exp(th[0]), th[1], np.exp(th[2]), np.exp(th[3])
        u = (np.arange(Q) + 0.5) / Q
        rows = [vm(kappa_of_j(special.gammaincinv(J1 * n ** -alpha / tau, u) * tau)).mean(0) for n in ns]
        return conv(np.array(rows), vm(kr)[0])
    if model == "TCC":
        return tcc_rows(th[0] * ns ** -th[1])
    if model == "TCC-free":
        return tcc_rows(th)
    raise ValueError(model)


# ---------------------------------------------------------------- fitting
def bins(P, res):
    """Probabilities of the data bins: 1-degree bins as is; 2-degree bins centred on even errors."""
    if res == 1:
        return P
    return (P + 0.5 * np.roll(P, 1, -1) + 0.5 * np.roll(P, -1, -1))[:, ::2]


def counts(s, idx):
    ns = np.unique(s["N"])
    b = np.round(s["err"][idx] / s["res"]).astype(int) % (360 // s["res"])
    C = np.zeros((len(ns), 360 // s["res"]))
    np.add.at(C, (np.searchsorted(ns, s["N"][idx]), b), 1)
    return ns, C


def loglik(model, th, ns, C, res, K=None):
    return float((C * np.log(np.maximum(bins(predict(model, th, ns, K), res), 1e-300))).sum())


BOUNDS = {"slots": [(LO, HI)], "slots+avg": [(LO, HI), (np.log(0.5), HI)],
          "VP": [(LO, HI), (-2, 5), (LO, HI), (np.log(0.5), HI)], "TCC": [(0, 10), (-2, 5)]}
STARTS = {"slots": [[np.log(5)], [np.log(30)]],
          "slots+avg": [[np.log(5), np.log(50)], [np.log(30), np.log(500)], [np.log(2), np.log(10)],
                        [np.log(1e4), np.log(5)]],   # near-perfect quanta, all noise at report: the slots corner
          "VP": [[np.log(10), 1.0, np.log(10), np.log(50)], [np.log(40), 1.5, np.log(40), np.log(500)],
                 [np.log(5), 0.5, np.log(2), np.log(20)], [np.log(100), 2.0, np.log(300), np.log(100)],
                 [np.log(20), 1.0, np.log(100), np.log(1000)], [np.log(60), 1.2, np.log(5), np.log(30)]],
          "TCC": [[1.5, 0.3], [3.0, 0.6], [5.0, 1.0]]}
KS = {"slots": range(1, 9), "slots+avg": range(1, 13)}


def fit(model, ns, C, res):
    """Maximum-likelihood fit. Returns (log likelihood, params, K)."""
    if model == "TCC-free":   # d' per set size is separable: exact search on the table grid
        j = (C @ LOG_TABLE[res].T).argmax(1)
        th = DGRID[j]
        return loglik(model, th, ns, C, res), th, None
    best = (-np.inf, None, None)
    for K in KS.get(model, [None]):
        for x0 in STARTS[model]:
            r = optimize.minimize(lambda th, K=K: -loglik(model, th, ns, C, res, K) / C.sum(), x0,
                                  method="L-BFGS-B", bounds=BOUNDS[model])
            ll = -r.fun * C.sum()
            if ll > best[0]:
                best = (ll, r.x, K)
    return best


def folds_of(s, k, seed):
    """Fold index per trial, stratified by set size."""
    rng = np.random.default_rng(seed)
    f = np.empty(len(s["N"]), int)
    for n in np.unique(s["N"]):
        idx = np.flatnonzero(s["N"] == n)
        f[rng.permutation(idx)] = np.arange(len(idx)) % k
    return f


def fit_subject(job):
    s, k, seed, models = job
    allidx = np.arange(len(s["N"]))
    folds = folds_of(s, k, seed)
    out = {"set": s["set"], "id": s["id"], "trials": len(allidx)}
    for m in models:
        cv = 0.0
        for j in range(k):
            ns, Ctr = counts(s, allidx[folds != j])
            _, Cte = counts(s, allidx[folds == j])
            _, th, K = fit(m, ns, Ctr, s["res"])
            cv += loglik(m, th, ns, Cte, s["res"], K)
        ns, C = counts(s, allidx)
        ll, th, K = fit(m, ns, C, s["res"])
        out[m] = cv
        out[m + " params"] = (K, np.round(th, 3).tolist())
    return out


def _init(table):
    global TCC_TABLE, LOG_TABLE
    TCC_TABLE = table
    LOG_TABLE = {r: np.log(np.maximum(bins(table, r), 1e-300)) for r in (1, 2)}


# ---------------------------------------------------------------- simulation for model recovery
def simulate(model, th, K, N, res, rng):
    """Errors drawn from the same binned distribution the likelihood scores."""
    ns = np.unique(N)
    P = bins(predict(model, th, ns, K), res)
    err = np.empty(len(N))
    for i, n in enumerate(ns):
        idx = np.flatnonzero(N == n)
        err[idx] = rng.choice(P.shape[1], size=len(idx), p=P[i]) * res
    return np.where(err > 180, err - 360, err)


# ---------------------------------------------------------------- report
def boot_ci(x, n=10000, seed=0):
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, len(x), (n, len(x)))].mean(1)
    return np.percentile(means, [2.5, 97.5])


def report(rows, models, ref="VP"):
    groups = [(g, [r for r in rows if r["set"] == g]) for g in SETS] + [("all", rows)]
    print(f"\nDelta CV-LL vs {ref} (nats per subject; positive = better than {ref}), mean [95% bootstrap CI]")
    print(f"{'set':5} {'n':>3} " + " ".join(f"{m:>25}" for m in models if m != ref))
    for g, rs in groups:
        if not rs:
            continue
        cells = []
        for m in models:
            if m == ref:
                continue
            d = np.array([r[m] - r[ref] for r in rs])
            lo, hi = boot_ci(d)
            cells.append(f"{d.mean():+8.1f} [{lo:+7.1f},{hi:+7.1f}]")
        print(f"{g:5} {len(rs):3d} " + " ".join(f"{c:>25}" for c in cells))
    prim = [m for m in models if m in MODELS]
    print("\nSubjects won (highest CV-LL among " + ", ".join(prim) + ")")
    for g, rs in groups:
        if rs:
            w = [prim[int(np.argmax([r[m] for m in prim]))] for r in rs]
            print(f"{g:5} {len(rs):3d}  " + "  ".join(f"{m} {w.count(m):2d}" for m in prim))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quick", action="store_true", help="2 subjects per set, 2 folds, no recovery")
    ap.add_argument("--folds", type=int, default=10)
    ap.add_argument("--recovery", type=int, default=10, help="synthetic subjects per generating model")
    ap.add_argument("--jobs", type=int, default=min(6, os.cpu_count() or 1), help="worker processes")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--data-dir", default=os.path.expanduser("~/.cache/brain-kb"))
    a = ap.parse_args()
    if a.folds < 2:
        ap.error("--folds must be at least 2")   # 0 skips the CV loop (scores of 0), 1 leaves nothing to train on
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(v, "1")    # workers inherit this: one BLAS thread each, no oversubscription

    subs = load_subjects(a.data_dir)
    f = similarity(a.data_dir)
    key = hashlib.sha1(f.tobytes() + DGRID.tobytes() + b"m801 motor2").hexdigest()[:10]
    cache = Path(a.data_dir) / TCC_OSF[0] / f"tcc_table_{key}.npy"
    if cache.exists():
        table = np.load(cache)
    else:
        print("computing the TCC table (once)")
        table = tcc_table(f)
        np.save(f"{cache}.tmp.npy", table)
        os.replace(f"{cache}.tmp.npy", cache)
    _init(table)
    if a.quick:
        subs = [s for g in SETS for s in [x for x in subs if x["set"] == g][:2]]
        a.folds, a.recovery = 2, 0
    for g in SETS:
        ss = [s for s in subs if s["set"] == g]
        print(f"{g:4} {SETS[g]:26} {len(ss):3d} subjects, {sum(len(s['N']) for s in ss):6d} trials, "
              f"set sizes {np.unique(np.concatenate([s['N'] for s in ss])).tolist()}, {ss[0]['res']}-degree bins")

    # self-checks: every prediction is a distribution; TCC at d'=0 is flat
    for m, th, K in (("slots", [3.0], 3), ("slots+avg", [2.0, 4.0], 5), ("VP", [3.0, 1.2, 2.0, 4.0], None),
                     ("TCC", [2.0, 0.5], None)):
        P = predict(m, np.array(th), [1, 4, 8], K)
        assert np.allclose(P.sum(1), 1) and (P >= 0).all(), m
    assert np.allclose(TCC_TABLE[0], 1 / 360, atol=1e-6)
    delta = np.eye(360)[[1]]                       # a 1-degree error splits evenly into the 0 and 2 bins
    assert np.allclose(bins(delta, 2)[0, :2], 0.5) and np.isclose(bins(delta, 2).sum(), 1)

    models = MODELS + ("TCC-free",)
    jobs = [(s, a.folds, a.seed * 1000 + i, models) for i, s in enumerate(subs)]
    with ProcessPoolExecutor(a.jobs, initializer=_init, initargs=(table,)) as ex:
        rows = list(ex.map(fit_subject, jobs))
    print(f"\n{len(rows)} subjects, {a.folds}-fold CV stratified by set size, seed {a.seed}")
    report(rows, models)

    print("\nFull-data fits, median across subjects [IQR]:")
    for g in list(SETS) + ["all"]:
        rs = [r for r in rows if g in ("all", r["set"])]
        if not rs:
            continue
        med = lambda v: f"{np.median(v):.2f} [{np.percentile(v, 25):.2f}-{np.percentile(v, 75):.2f}]"
        print(f"{g:5} slots K {med([r['slots params'][0] for r in rs])}  "
              f"slots+avg K {med([r['slots+avg params'][0] for r in rs])}  "
              f"VP alpha {med([r['VP params'][1][1] for r in rs])}  "
              f"TCC beta {med([r['TCC params'][1][1] for r in rs])}")

    if not a.quick:
        OUT.parent.mkdir(exist_ok=True)
        with open(OUT, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["set", "subject", "trials"] + [f"cvll_{m}" for m in models]
                       + ["K_slots", "K_slots_avg", "vp_alpha", "tcc_d1", "tcc_beta"])
            for r in rows:
                w.writerow([r["set"], r["id"], r["trials"]] + [f"{r[m]:.3f}" for m in models]
                           + [r["slots params"][0], r["slots+avg params"][0], r["VP params"][1][1],
                              r["TCC params"][1][0], r["TCC params"][1][1]])
        print(f"\nper-subject scores written to {OUT}")

    if a.recovery:
        rng = np.random.default_rng(a.seed + 1)
        sim_jobs, gen = [], []
        for m in MODELS:
            for i in range(a.recovery):
                j = int(rng.integers(len(subs)))
                K, th = rows[j][m + " params"]
                s = subs[j]
                fake = dict(s, err=simulate(m, np.array(th), K, s["N"], s["res"], rng), id=f"sim_{m}_{i}")
                sim_jobs.append((fake, a.folds, 10**6 + len(sim_jobs), MODELS))
                gen.append(m)
        with ProcessPoolExecutor(a.jobs, initializer=_init, initargs=(table,)) as ex:
            sims = list(ex.map(fit_subject, sim_jobs))
        print(f"\nModel recovery ({a.recovery} synthetic subjects per model, designs and parameters of random "
              f"real subjects): rows = generating model, columns = CV winner")
        print(f"{'':10}" + "".join(f"{m:>11}" for m in MODELS))
        for m in MODELS:
            w = [MODELS[int(np.argmax([r[x] for x in MODELS]))] for r, g in zip(sims, gen) if g == m]
            print(f"{m:10}" + "".join(f"{w.count(x):11d}" for x in MODELS))


if __name__ == "__main__":
    main()
