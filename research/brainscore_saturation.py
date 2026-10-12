"""Has the ImageNet-accuracy to Brain-Score link saturated? (issue #88)

Reads a dated snapshot of the public Brain-Score vision leaderboard (one row per model: ImageNet top-1,
the average, neural and behavioural scores, and V1, V2, V4, IT). For each score it fits a straight line
and a hinge (two lines joined at a breakpoint k, grid-searched) against top-1, compares them by BIC, and
bootstraps the breakpoint and the slope above it. Then, among models at or above 70% top-1 (the point
where Schrimpf et al. 2018 saw the correlation weaken), it asks whether accuracy or parameter count still
rank the scores. Method pre-registered on issue #88. The leaderboard changes; every result names its
snapshot date. Scores on the leaderboard are rounded to 2 decimals.

Run: python research/brainscore_saturation.py [--fetch] [--boot N]
     --fetch downloads today's leaderboard into research/data/ and analyses it.
"""
import argparse
import csv
import datetime
import json
import re
import urllib.request
from pathlib import Path

import numpy as np

DATA = Path(__file__).parent / "data"
URL = "https://www.brain-score.org/vision/leaderboard/content/"
SCORES = {"average": "average_vision_v0", "neural": "neural_vision_v0", "behavior": "behavior_vision_v0",
          "V1": "V1_v0", "V2": "V2_v0", "V4": "V4_v0", "IT": "IT_v0"}
COLS = ["model", "submitted", "architecture", "params", "imagenet_top1"] + list(SCORES)
HIGH = 0.70   # Schrimpf et al. 2018: "correlation weakened at >= 70% top-1"
BINS = (0.0, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 1.0)
BIG = r"clip|laion|openai|12k|22k|wsl|ig1b|ig_|jft|swag|dino|semi|ssl|datacomp|webli"


def fetch():
    """Save today's leaderboard as research/data/brainscore_vision_<date>.csv and return its path."""
    req = urllib.request.Request(URL, headers={"User-Agent": "Brain-KB research script (issue #88)"})
    html = urllib.request.urlopen(req, timeout=120).read().decode("utf-8")
    rows = json.loads(re.search(r'id="ld-row-data">(.*?)</script>', html, re.S).group(1))
    val = lambda r, k: (r.get(k) or {}).get("value", "") if isinstance(r.get(k), dict) else ""
    num = lambda v: v if re.fullmatch(r"-?\d+(\.\d+)?", str(v)) else ""   # "X" = failed, "" = not run
    path = DATA / f"brainscore_vision_{datetime.date.today()}.csv"
    DATA.mkdir(exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLS)
        for r in rows:
            m = r.get("metadata") or {}
            w.writerow([r["model"]["name"], r["submission_timestamp"][:10], m.get("architecture") or "",
                        m.get("total_parameter_count") or "", num(val(r, "ImageNet-top1_v1"))]
                       + [num(val(r, k)) for k in SCORES.values()])
    return path


def load(path):
    """Columns as arrays. Top-1 of 0.00 means the model has no ImageNet readout (self-supervised
    backbones, seed variants), not 0% accuracy, so it is treated as missing (a deviation from #88's plan,
    decided after seeing the data)."""
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    col = lambda k: np.array([float(r[k]) if r[k] else np.nan for r in rows])
    d = {k: col(k) for k in COLS[3:]}
    zero = d["imagenet_top1"] == 0
    print(f"{len(rows)} models, {(~np.isnan(d['imagenet_top1'])).sum()} with a top-1; "
          f"{zero.sum()} at 0.00 (no readout) dropped")
    d["imagenet_top1"][zero] = np.nan
    # Exploratory, not pre-registered: name tags for pretraining beyond ImageNet-1k.
    d["big_data"] = np.array([bool(re.search(BIG, r["model"], re.I)) for r in rows])
    return d


def hinge_fit(x, y, ks):
    """Best hinge y = a + b x + c max(0, x - k) over the grid ks: (sse, k, slope below, slope above)."""
    best = (np.inf,)
    for k in ks:
        X = np.column_stack([np.ones_like(x), x, np.maximum(0, x - k)])
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        sse = ((X @ coef - y) ** 2).sum()
        if sse < best[0]:
            best = (sse, k, coef[1], coef[1] + coef[2])
    return best


def line_sse(x, y):
    X = np.column_stack([np.ones_like(x), x])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return ((X @ coef - y) ** 2).sum(), coef[1]


def bic(sse, n, p):
    return n * np.log(sse / n) + p * np.log(n)


def ranks(a):
    r = np.empty(len(a)); r[np.argsort(a, kind="stable")] = np.arange(len(a))
    for v in np.unique(a):   # average ties (scores are rounded, so ties are common)
        r[a == v] = r[a == v].mean()
    return r


def spearman(a, b, rng, perms=2000):
    """Spearman rho and a two-sided permutation p."""
    ra, rb = ranks(a), ranks(b)
    rho = np.corrcoef(ra, rb)[0, 1]
    null = np.array([np.corrcoef(ra, rng.permutation(rb))[0, 1] for _ in range(perms)])
    return rho, (1 + (np.abs(null) >= abs(rho)).sum()) / (perms + 1)


def analyse(d, boot, rng):
    print(f"{'score':>8} {'n':>4} {'r':>5} | {'dBIC':>6} {'k':>5} [95% CI]     {'slope<k':>7} {'slope>k':>7} [95% CI]"
          f"    | top-1 >= {HIGH:.2f}: rho(top-1) p     rho(log params) p   n")
    for name in SCORES:
        ok = ~np.isnan(d["imagenet_top1"]) & ~np.isnan(d[name])
        x, y = d["imagenet_top1"][ok], d[name][ok]
        n, ks = len(x), np.quantile(x, np.linspace(0.1, 0.9, 41))
        sse_l, _ = line_sse(x, y)
        sse_h, k, below, above = hinge_fit(x, y, ks)
        dbic = bic(sse_h, n, 4) - bic(sse_l, n, 2)   # < 0 favours the hinge; k counts as a parameter
        bs = []
        for _ in range(boot):
            i = rng.integers(0, n, n)
            bs.append(hinge_fit(x[i], y[i], ks)[1:])
        bs = np.array(bs)
        kl, kh = np.percentile(bs[:, 0], [2.5, 97.5])
        al, ah = np.percentile(bs[:, 2], [2.5, 97.5])
        hi = x >= HIGH
        rho_a, p_a = spearman(x[hi], y[hi], rng)
        p = d["params"][ok][hi]
        has = ~np.isnan(p)
        rho_p, p_p = spearman(np.log10(p[has]), y[hi][has], rng)
        print(f"{name:>8} {n:>4} {np.corrcoef(x, y)[0, 1]:5.2f} | {dbic:6.1f} {k:5.3f} [{kl:.3f}, {kh:.3f}] "
              f"{below:7.2f} {above:7.2f} [{al:+.2f}, {ah:+.2f}] | "
              f"{rho_a:+.2f} {p_a:.3f} (n {hi.sum()})   {rho_p:+.2f} {p_p:.3f}   {has.sum()}")


def binned(d):
    x = d["imagenet_top1"]
    print("\nmean score per top-1 bin (n in the header):")
    heads = [f"[{lo:.2f},{hi:.2f}) {((x >= lo) & (x < hi)).sum():>3}" for lo, hi in zip(BINS, BINS[1:])]
    print(" " * 9 + " | ".join(heads))
    for name in SCORES:
        print(f"{name:>8} " + " | ".join(f"{np.nanmean(d[name][(x >= lo) & (x < hi)]):>16.3f}"
                                         for lo, hi in zip(BINS, BINS[1:])))


def big_data(d, rng, cut=0.75, perms=5000):
    """Exploratory: at equal top-1, do models pretrained beyond ImageNet-1k score higher? The groups differ
    in top-1, so the test is on residuals of a line fit of score on top-1 (permutation p)."""
    hi = d["imagenet_top1"] >= cut
    g = d["big_data"][hi]
    print(f"\nexploratory, top-1 >= {cut}: pretrained beyond ImageNet-1k (by name) n {g.sum()}, "
          f"ImageNet-1k only n {(~g).sum()}; mean top-1 {np.mean(d['imagenet_top1'][hi][g]):.3f} vs "
          f"{np.mean(d['imagenet_top1'][hi][~g]):.3f}")
    print(f"{'score':>8} {'big':>5} {'in1k':>5}  {'raw diff':>8}  {'diff at equal top-1':>19}  p")
    for name in SCORES:
        y, x = d[name][hi], d["imagenet_top1"][hi]
        ok = ~np.isnan(y)
        y, x, gg = y[ok], x[ok], g[ok]
        res = y - np.polyval(np.polyfit(x, y, 1), x)
        diff = res[gg].mean() - res[~gg].mean()
        null = np.array([(lambda p: res[p].mean() - res[~p].mean())(rng.permutation(gg)) for _ in range(perms)])
        print(f"{name:>8} {y[gg].mean():.3f} {y[~gg].mean():.3f}  {y[gg].mean() - y[~gg].mean():+8.3f}  "
              f"{diff:+19.3f}  {(1 + (np.abs(null) >= abs(diff)).sum()) / (perms + 1):.4f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="download today's leaderboard first")
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    path = fetch() if a.fetch else sorted(DATA.glob("brainscore_vision_*.csv"))[-1]
    print(f"snapshot: {path.name}")
    d, rng = load(path), np.random.default_rng(0)
    print()
    analyse(d, a.boot, rng)
    print("dBIC = BIC(hinge) - BIC(line); below -10 is strong evidence for a breakpoint. Slopes are score per"
          " unit top-1.\nrho columns: Spearman among models at or above 70% top-1, with a permutation p.")
    binned(d)
    big_data(d, rng)


if __name__ == "__main__":
    # Self-check: on a synthetic plateau the hinge must find the knee and a flat slope above it.
    g = np.random.default_rng(1)
    x = g.uniform(0.4, 0.9, 300)
    y = 0.1 + 0.6 * np.minimum(x, 0.7) + g.normal(0, 0.01, 300)
    sse, k, below, above = hinge_fit(x, y, np.linspace(0.45, 0.85, 81))
    assert abs(k - 0.7) < 0.02 and abs(below - 0.6) < 0.05 and abs(above) < 0.05, (k, below, above)
    assert bic(sse, 300, 4) < bic(line_sse(x, y)[0], 300, 2) - 10
    main()
