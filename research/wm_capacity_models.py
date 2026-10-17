"""Working-memory capacity: slots or resource? Four models re-fitted to public colour-wheel data (issue #90)

Delayed estimation: a person sees N coloured squares, then reports the colour of one of them on a colour
wheel. The response error (report - true colour, radians) is fitted per subject with four models:

  slots       K slots, each holding one item at precision J1; items without a slot are guessed
              (uniform). Same precision at every set size (Zhang & Luck 2008, without averaging).
  slots+avg   As slots, but when N < K the spare slots go to items and their precisions add
              (Zhang & Luck 2008, "slots plus averaging").
  vp          Variable precision, no capacity limit: every item is stored, precision J ~ Gamma with mean
              J1 * N^-alpha and scale tau (van den Berg et al. 2012, "VP-A" in van den Berg et al. 2014).
  tcc         Target confusability competition (Schurgin, Wixted & Brady 2020): each of 180 wheel colours
              gets a familiarity signal d'(N) * f(distance to the target) + N(0, 1) noise and the report
              is the most familiar colour, d'(N) = d1 * N^-beta. The similarity f is not measured here (no
              similarity data come with these sets), so f(x) = exp(-|x| / s) with s fitted per subject;
              a deviation from the published TCC, which fixes f from a separate similarity experiment.

Precision J is Fisher information; a von Mises with concentration kappa has J = kappa I1(kappa)/I0(kappa)
(van den Berg et al. 2012). No model includes swaps (reports of a non-target colour) or motor noise, so
the comparison is like-for-like on that point.

Pre-registered (written 2026-10-15, before the real-data run; also in function/attention-and-working-memory.md):
  data      Zhang & Luck 2008 Exp. 2 (8 subjects, N = 1, 2, 3, 6) and Oberauer & Lin 2017 Exp. 1 (19
            subjects, N = 1-8) are primary. Bays, Catalao & Husain 2009 (12 subjects, N = 1, 2, 4, 6) is
            secondary: only the 500 and 2000 ms sample durations, pooled (100 ms may cut encoding short).
            All trials are used; no exclusions.
  score     5-fold cross-validated log-likelihood per subject (folds stratified by set size, seed 0),
            summed over held-out trials, in nats. AIC on the full fit is reported as a check.
  tests     Per dataset: the number of subjects each model wins; and for (best slot model vs vp) and
            (tcc vs vp), the mean per-subject difference in held-out log-likelihood with a two-sided
            sign-flip permutation test across subjects.
  predicts  From van den Berg et al. (2014): vp beats both slot models in most subjects. Counts against it:
            a slot model wins most subjects with a significant difference. tcc vs vp: no directional
            prediction.
  check     --synthetic first: simulate 6 subjects from each model (150 trials per set size, N = 1, 2, 4,
            6) and require the fitter to pick the generating model for at least 75% of them (model recovery). Synthetic numbers are a test of the code,
            not a finding.

Data: the three sets are taken from the CRAN packages bmm (GPL-2; Zhang & Luck, Oberauer & Lin) and mixtur
(GPL-3; Bays et al., who released them at https://osf.io/c2yx5/), through GitHub's read-only CRAN mirror,
pinned to a commit. They are cached as CSV in research/data/delayed_estimation/ (git-ignored: licences
differ from this repo's). Converting the .rda files needs `pip install rdata` once.

Run: python research/wm_capacity_models.py [--synthetic] [--quick] [--datasets zl2008 ol2017 bays2009]
"""
import argparse
import csv
import io
import urllib.request
import warnings
from pathlib import Path

import numpy as np
from scipy import optimize, special, stats

HERE = Path(__file__).parent
CACHE = HERE / "data" / "delayed_estimation"
OUT = HERE / "data" / "wm_capacity_cvll.csv"
BMM = "https://raw.githubusercontent.com/cran/bmm/861dd1c631f5256d54647c76b0aeb8c704dd3341/data/"
MIXTUR = "https://raw.githubusercontent.com/cran/mixtur/d750e8ce83d51147c66140312526ff44d95308a3/data/"
SOURCES = {"zl2008": (BMM + "zhang_luck_2008.rda", "zhang_luck_2008"),
           "ol2017": (BMM + "oberauer_lin_2017.rda", "oberauer_lin_2017"),
           "bays2009": (MIXTUR + "bays2009_full.rda", "bays2009_full")}
MODELS = ("slots", "slots+avg", "vp", "tcc")
NPAR = {"slots": 2, "slots+avg": 2, "vp": 3, "tcc": 3}
KMAX = 8
M = 180                                   # colour-wheel bins for TCC (2 degrees, as the wheels used)
GRID = (np.arange(M) - M // 2) * 2 * np.pi / M
LOG2PI = np.log(2 * np.pi)

# ---------- precision J <-> von Mises kappa ----------
_KAP = np.logspace(-4, 4.5, 4000)
_J = _KAP * special.i1e(_KAP) / special.i0e(_KAP)


def kappa_of(J):
    return np.interp(np.log(np.maximum(J, 1e-12)), np.log(_J), _KAP, left=0.0)


def vm_logpdf(err, kappa):
    kappa = np.asarray(kappa, float)
    return kappa * (np.cos(err) - 1) - LOG2PI - np.log(special.i0e(kappa))


def wrap(x):
    return (np.asarray(x, float) + np.pi) % (2 * np.pi) - np.pi


# ---------- per-trial log-likelihood of each model ----------
# A subject is (err, N): arrays of response errors (rad) and set sizes. Parameters live in an unbounded space.

def ll_slots(theta, err, N, K, average):
    J1 = np.exp(theta[0])
    out = np.empty_like(err)
    for n in np.unique(N):
        e = err[N == n]
        if n >= K:
            p = K / n
            lv = vm_logpdf(e, kappa_of(J1))
            out[N == n] = np.logaddexp(np.log(p) + lv, np.log1p(-p) - LOG2PI) if p < 1 else lv
        elif not average:
            out[N == n] = vm_logpdf(e, kappa_of(J1))
        else:   # K slots over n < K items: K mod n items get floor(K/n) + 1 slots, the rest floor(K/n)
            lo, frac = K // n, (K % n) / n
            l_lo = vm_logpdf(e, kappa_of(lo * J1))
            out[N == n] = l_lo if frac == 0 else np.logaddexp(np.log1p(-frac) + l_lo,
                                                               np.log(frac) + vm_logpdf(e, kappa_of((lo + 1) * J1)))
    return out


_Q = (np.arange(40) + 0.5) / 40            # gamma quantile midpoints for the VP integral


def ll_vp(theta, err, N):
    J1, alpha, tau = np.exp(theta[0]), theta[1], np.exp(theta[2])
    out = np.empty_like(err)
    for n in np.unique(N):
        Jbar = J1 * n ** -alpha
        J = stats.gamma.ppf(_Q, a=max(Jbar / tau, 1e-6), scale=tau)
        lv = vm_logpdf(err[N == n][:, None], kappa_of(J)[None, :])
        out[N == n] = special.logsumexp(lv, axis=1) - np.log(len(_Q))
    return out


DZ = 0.1                                   # integration step for TCC (checked against 0.02: same to 1e-6)


def tcc_probs(dprime, s):
    """P(report bin k | target at 0) for TCC: argmax of independent N(d' f(x_k), 1) signals.
    P(k) = integral of pdf(z - mu_k) * prod_{j != k} cdf(z - mu_j) dz, over z spanning every mu +- 7."""
    mu = dprime * np.exp(-np.abs(GRID) / s)
    z = np.arange(mu.min() - 7, mu.max() + 7, DZ)[:, None]
    logcdf = special.log_ndtr(z - mu[None, :])                       # (Z, M)
    tot = logcdf.sum(1, keepdims=True)
    logpdf = -0.5 * (z - mu[None, :]) ** 2 - 0.5 * LOG2PI
    p = np.trapezoid(np.exp(logpdf + tot - logcdf), dx=DZ, axis=0)
    p = np.maximum(p, 1e-300)
    return p / p.sum()


def ll_tcc(theta, err, N):
    d1, beta, s = np.exp(theta[0]), theta[1], np.exp(theta[2])
    idx = np.round(err / (2 * np.pi / M)).astype(int) % M
    idx = (idx + M // 2) % M
    out = np.empty_like(err)
    for n in np.unique(N):
        p = tcc_probs(d1 * n ** -beta, s)
        out[N == n] = np.log(p[idx[N == n]] * M / (2 * np.pi))       # density per radian
    return out


# ---------- fitting ----------

def _minimize(f, starts):
    best = None
    for x0 in starts:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = optimize.minimize(f, x0, method="Nelder-Mead", options={"xatol": 1e-3, "fatol": 1e-3, "maxiter": 800})
        if best is None or r.fun < best.fun:
            best = r
    return best


def fit(model, err, N):
    """Maximum-likelihood fit; returns (negative log-likelihood, params dict, per-trial ll function)."""
    if model in ("slots", "slots+avg"):
        avg = model == "slots+avg"
        best = None
        for K in range(1, KMAX + 1):
            f = lambda t, K=K: -ll_slots(t, err, N, K, avg).sum()
            r = optimize.minimize_scalar(lambda x, f=f: f([x]), bounds=(-3, 8), method="bounded")
            if best is None or r.fun < best[0]:
                best = (r.fun, {"K": K, "J1": float(np.exp(r.x))}, (lambda e, n, x=r.x, K=K: ll_slots([x], e, n, K, avg)))
        return best
    if model == "vp":
        f = lambda t: -ll_vp(t, err, N).sum()
        r = _minimize(f, [[np.log(10), 1.0, np.log(5)], [np.log(30), 1.5, np.log(20)], [np.log(5), 0.5, np.log(2)]])
        return r.fun, {"J1": float(np.exp(r.x[0])), "alpha": float(r.x[1]), "tau": float(np.exp(r.x[2]))}, \
            (lambda e, n, x=r.x: ll_vp(x, e, n))
    f = lambda t: -ll_tcc(t, err, N).sum()
    r = _minimize(f, [[np.log(3), 0.5, np.log(0.5)], [np.log(5), 1.0, np.log(0.3)], [np.log(2), 0.2, np.log(1.0)]])
    return r.fun, {"d1": float(np.exp(r.x[0])), "beta": float(r.x[1]), "s": float(np.exp(r.x[2]))}, \
        (lambda e, n, x=r.x: ll_tcc(x, e, n))


def folds(N, k=5, seed=0):
    rng = np.random.default_rng(seed)
    f = np.empty(len(N), int)
    for n in np.unique(N):
        i = np.flatnonzero(N == n)
        f[rng.permutation(i)] = np.arange(len(i)) % k
    return f


def score_subject(err, N, k=5, models=MODELS):
    """{model: (held-out ll, full-fit AIC, params)}."""
    fo = folds(N, k)
    res = {}
    for m in models:
        cv = 0.0
        for j in range(k):
            tr = fo != j
            _, _, llf = fit(m, err[tr], N[tr])
            cv += llf(err[~tr], N[~tr]).sum()
        nll, par, _ = fit(m, err, N)
        res[m] = (cv, 2 * nll + 2 * NPAR[m], par)
    return res


# ---------- simulation (for model recovery) ----------

def simulate(model, par, N, rng):
    n = len(N)
    if model in ("slots", "slots+avg"):
        K, J1 = par["K"], par["J1"]
        err = np.empty(n)
        for i, s in enumerate(N):
            if s >= K:
                err[i] = rng.vonmises(0, kappa_of(J1)) if rng.random() < K / s else rng.uniform(-np.pi, np.pi)
            else:
                slots = 1 if model == "slots" else K // s + (rng.random() < (K % s) / s)
                err[i] = rng.vonmises(0, kappa_of(slots * J1))
        return err
    if model == "vp":
        Jbar = par["J1"] * N.astype(float) ** -par["alpha"]
        J = rng.gamma(Jbar / par["tau"], par["tau"])
        return rng.vonmises(0, kappa_of(J))
    err = np.empty(n)
    for s in np.unique(N):
        p = tcc_probs(par["d1"] * s ** -par["beta"], par["s"])
        k = rng.choice(M, size=(N == s).sum(), p=p)
        err[N == s] = GRID[k] + rng.uniform(-np.pi / M, np.pi / M, k.size)
    return err


def random_params(model, rng):
    if model in ("slots", "slots+avg"):
        return {"K": int(rng.integers(2, 6)), "J1": float(rng.uniform(5, 20))}
    if model == "vp":
        return {"J1": float(rng.uniform(15, 40)), "alpha": float(rng.uniform(0.8, 1.6)), "tau": float(rng.uniform(5, 25))}
    return {"d1": float(rng.uniform(3, 6)), "beta": float(rng.uniform(0.3, 0.7)), "s": float(rng.uniform(0.3, 0.8))}


def model_recovery(n_subj, trials, sizes=(1, 2, 4, 6), seed=1):
    print(f"SYNTHETIC model recovery (tests the code, not the brain): {n_subj} simulated subjects per model, "
          f"{trials} trials per set size, set sizes {sizes}")
    rng = np.random.default_rng(seed)
    N = np.repeat(np.array(sizes), trials)
    conf = np.zeros((4, 4), int)
    for gi, g in enumerate(MODELS):
        for _ in range(n_subj):
            par = random_params(g, rng)
            res = score_subject(simulate(g, par, N, rng), N)
            conf[gi, MODELS.index(max(res, key=lambda m: res[m][0]))] += 1
    print("generating model (rows) x model with best held-out log-likelihood (columns)")
    print(f"{'':>10} " + " ".join(f"{m:>9}" for m in MODELS))
    for gi, g in enumerate(MODELS):
        print(f"{g:>10} " + " ".join(f"{c:>9d}" for c in conf[gi]))
    rate = np.trace(conf) / conf.sum()
    print(f"recovered {np.trace(conf)}/{conf.sum()} ({rate:.0%})")
    return conf


# ---------- real data ----------

def fetch(name):
    """Download one dataset's .rda from the pinned CRAN mirror commit and cache it as CSV (subject, N, err)."""
    path = CACHE / f"{name}.csv"
    if path.exists():
        return path
    import rdata   # lazy: only needed once, to convert R's format

    url, obj = SOURCES[name]
    raw = urllib.request.urlopen(url, timeout=120).read()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df = rdata.read_rda(io.BytesIO(raw))[obj]
    if name == "zl2008":
        rows = zip(df["subID"], df["setsize"].astype(int), df["response_error"])
    elif name == "ol2017":
        rows = zip(df["ID"], df["set_size"].astype(int), df["dev_rad"])
    else:
        keep = df["duration"].isin([500.0, 2000.0])
        df = df[keep]
        rows = zip(df["id"], df["set_size"].astype(int), wrap(df["response"] - df["target"]))
    CACHE.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["subject", "set_size", "error_rad"])
        for s, n, e in rows:
            w.writerow([int(s), int(n), f"{float(e):.6f}"])
    return path


def load(name):
    with open(fetch(name), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    subj = np.array([int(r["subject"]) for r in rows])
    N = np.array([int(r["set_size"]) for r in rows])
    err = wrap(np.array([float(r["error_rad"]) for r in rows]))
    return {s: (err[subj == s], N[subj == s]) for s in np.unique(subj)}


def signflip(d, n=100000, seed=0):
    """Two-sided sign-flip permutation p for mean(d) = 0 (exact when 2^len(d) <= n)."""
    d = np.asarray(d, float)
    if 2 ** len(d) <= n:
        signs = np.array(np.meshgrid(*[[-1, 1]] * len(d))).reshape(len(d), -1).T
    else:
        signs = np.random.default_rng(seed).choice([-1, 1], size=(n, len(d)))
    null = np.abs((signs * d).mean(1))
    return (np.sum(null >= abs(d.mean()) - 1e-12) + 1) / (len(null) + 1)


def analyse(name, quick=False):
    subjects = load(name)
    if quick:
        subjects = dict(list(subjects.items())[:2])
    print(f"\n== {name}: {len(subjects)} subjects, {sum(len(v[0]) for v in subjects.values())} trials, "
          f"set sizes {sorted(set(np.concatenate([v[1] for v in subjects.values()])))}")
    rows = []
    for s, (err, N) in subjects.items():
        res = score_subject(err, N)
        rows.append((s, len(err), res))
        par = {m: res[m][2] for m in MODELS}
        print(f"subject {s:>3}: held-out ll " + "  ".join(f"{m} {res[m][0]:8.1f}" for m in MODELS)
              + f" | K {par['slots+avg']['K']} alpha {par['vp']['alpha']:.2f} beta {par['tcc']['beta']:.2f}")
    cv = np.array([[r[2][m][0] for m in MODELS] for r in rows])
    aic = np.array([[r[2][m][1] for m in MODELS] for r in rows])
    wins = np.bincount(cv.argmax(1), minlength=4)
    aic_wins = np.bincount(aic.argmin(1), minlength=4)
    print("subjects won (held-out ll): " + ", ".join(f"{m} {w}" for m, w in zip(MODELS, wins)))
    print("subjects won (AIC, full fit): " + ", ".join(f"{m} {w}" for m, w in zip(MODELS, aic_wins)))
    best_slot = np.maximum(cv[:, 0], cv[:, 1])
    for label, d in (("vp - best slot model", cv[:, 2] - best_slot), ("tcc - vp", cv[:, 3] - cv[:, 2]),
                     ("slots+avg - slots", cv[:, 1] - cv[:, 0])):
        print(f"{label:>22}: mean {d.mean():+7.2f} nats/subject (range {d.min():+.1f} to {d.max():+.1f}), "
              f"{(d > 0).sum()}/{len(d)} positive, sign-flip p = {signflip(d):.4f}")
    return [(name, s, n, *[r[m][0] for m in MODELS], *[r[m][1] for m in MODELS],
             r["slots+avg"][2]["K"], r["vp"][2]["alpha"], r["tcc"][2]["beta"], r["tcc"][2]["s"]) for s, n, r in rows]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--synthetic", action="store_true", help="model recovery on simulated subjects only")
    ap.add_argument("--quick", action="store_true", help="smoke run: fewer subjects")
    ap.add_argument("--datasets", nargs="+", default=["zl2008", "ol2017", "bays2009"], choices=list(SOURCES))
    a = ap.parse_args()
    if a.synthetic:
        conf = model_recovery(2 if a.quick else 6, 60 if a.quick else 150)
        if not a.quick:
            assert np.trace(conf) / conf.sum() >= 0.75, "model recovery below the pre-registered 75%"
        return
    allrows = []
    for name in a.datasets:
        allrows += analyse(name, a.quick)
    if not a.quick:
        with open(OUT, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["dataset", "subject", "trials"] + [f"cvll_{m}" for m in MODELS] + [f"aic_{m}" for m in MODELS]
                       + ["K_slots_avg", "alpha_vp", "beta_tcc", "s_tcc"])
            for r in allrows:
                w.writerow([r[0], r[1], r[2]] + [f"{v:.2f}" if isinstance(v, float) else v for v in r[3:]])
        print(f"\nper-subject table written to {OUT.relative_to(HERE.parent)}")


if __name__ == "__main__":
    main()
