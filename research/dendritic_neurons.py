"""Point neurons vs dendritic (two-layer) neurons at equal parameters (issue #85).

Three arms at one parameter budget per task, all plain masked MLPs. Widths are integers, so parameters
match to within 10% and multiply-adds are reported, not matched (dend uses 3-20% fewer):
  point-1  dense, one hidden tanh layer
  point-2  dense, two hidden tanh layers of equal width (the "is it just depth?" control)
  dend     each neuron splits a random partition of all inputs over k branches; tanh per branch
           (Poirazi, Brannon & Mel 2003), learnable branch-to-soma weights, tanh at the soma
Tasks: 8-bit parity (train accuracy, a capacity test), a sparse feature-conjunction task, and sklearn's
8x8 digits (a stand-in for MNIST). Learning: backprop and feedback alignment. Method pre-registered on #85.
A computational result about network design, not a claim about cortex.

Run: python research/dendritic_neurons.py [--seeds N] [--quick] [--out FILE.json]
--out writes the shared result file (#104), one row per arm/rule x seed with the task as the split:
python research/result_schema.py FILE.json
"""
import argparse
import itertools
import json
import sys

import numpy as np
from sklearn.datasets import load_digits

from result_schema import make_result

LRS, TUNE_SEEDS, BATCH = (0.03, 0.1, 0.3), (101, 102, 103), 32
TASKS = {  # name: (budget, branches k, epochs)
    "parity": (80, 2, 500), "conjunction": (400, 4, 60), "digits": (2000, 4, 60)}
ARMS, RULES = ("point-1", "point-2", "dend"), ("bp", "fa")


def make_task(name, rng):
    """(x_train, y_train, x_val, y_val, x_test, y_test, classes)."""
    if name == "parity":   # every pattern; train = val = test, since parity is about capacity
        # Bits are 0/1, not -1/+1: with +-1 inputs and zero biases every tanh net is odd in x while
        # 8-bit parity is even, and backprop sat at exactly chance (first run, logged on #85).
        x = np.array(list(itertools.product((0.0, 1.0), repeat=8)))
        y = x.sum(1).astype(int) % 2
        return x, y, x, y, x, y, 2
    if name == "conjunction":   # label = OR over 5 fixed disjoint pairs of (a AND b)
        pairs = rng.permutation(40)[:10].reshape(5, 2)

        def sample(n):
            x = (rng.random((n, 40)) < 0.15).astype(float)
            force = rng.random(n) < 0.5
            x[np.flatnonzero(force)[:, None], pairs[rng.integers(5, size=force.sum())]] = 1
            return x, x[:, pairs].prod(2).max(1).astype(int)
        (xt, yt), (xs, ys) = sample(2000), sample(2000)
        return xt[:1600], yt[:1600], xt[1600:], yt[1600:], xs, ys, 2
    d = load_digits()
    x, y = d.data / 16.0, d.target
    i = rng.permutation(len(y))
    return x[i[:1000]], y[i[:1000]], x[i[1000:1200]], y[i[1000:1200]], x[i[1200:]], y[i[1200:]], 10


def masks(arm, D, C, w, k, rng):
    """Connectivity masks, input to output, for an arm of width w."""
    if arm == "point-1":
        return [np.ones((D, w)), np.ones((w, C))]
    if arm == "point-2":
        return [np.ones((D, w)), np.ones((w, w)), np.ones((w, C))]
    branch, soma = np.zeros((D, w * k)), np.zeros((w * k, w))
    for n in range(w):
        for j, part in enumerate(np.array_split(rng.permutation(D), k)):
            branch[part, n * k + j] = 1
        soma[n * k:(n + 1) * k, n] = 1
    return [branch, soma, np.ones((w, C))]


def n_params(M):
    return int(sum(m.sum() + m.shape[1] for m in M))   # weights + biases


def count(arm, D, C, w, k):
    """n_params(masks(...)) in closed form (self_check confirms they agree)."""
    return {"point-1": D * w + w, "point-2": D * w + w + w * w + w,
            "dend": D * w + 2 * w * k + w}[arm] + w * C + C


def width_for(arm, D, C, k, budget):
    return min(range(1, 400), key=lambda w: abs(count(arm, D, C, w, k) - budget))


def init(M, rng):
    W = [rng.normal(size=m.shape) / np.sqrt(m.sum(0, keepdims=True)) * m for m in M]
    B = [rng.normal(size=m.shape) / np.sqrt(m.sum(0, keepdims=True)) * m for m in M]   # FA feedback
    return W, [np.zeros(m.shape[1]) for m in M], B


def forward(W, b, x):
    hs = [x]
    for l in range(len(W)):
        z = hs[-1] @ W[l] + b[l]
        hs.append(np.tanh(z) if l < len(W) - 1 else z)
    return hs


def grads(W, b, B, M, x, y, rule):
    """Cross-entropy gradients; FA sends the error back through the fixed matrices B, not W.T."""
    hs = forward(W, b, x)
    z = hs[-1] - hs[-1].max(1, keepdims=True)
    p = np.exp(z); p /= p.sum(1, keepdims=True)
    g = p; g[np.arange(len(y)), y] -= 1; g /= len(y)
    gW, gb = [None] * len(W), [None] * len(W)
    for l in reversed(range(len(W))):
        gW[l], gb[l] = hs[l].T @ g * M[l], g.sum(0)
        if l:
            g = (g @ (W[l] if rule == "bp" else B[l]).T) * (1 - hs[l] ** 2)
    return gW, gb


def acc(W, b, x, y):
    return float((forward(W, b, x)[-1].argmax(1) == y).mean())


def run(task, arm, rule, seed, lr, epochs=None):
    """Train one network; return (validation accuracy, test accuracy)."""
    budget, k, ep = TASKS[task]
    xt, yt, xv, yv, xs, ys, C = make_task(task, np.random.default_rng(seed))
    rng = np.random.default_rng([seed, ARMS.index(arm), RULES.index(rule)])
    M = masks(arm, xt.shape[1], C, width_for(arm, xt.shape[1], C, k, budget), k, rng)
    W, b, B = init(M, rng)
    for _ in range(epochs or ep):
        order = rng.permutation(len(yt))
        for s in range(0, len(yt), BATCH):
            i = order[s:s + BATCH]
            gW, gb = grads(W, b, B, M, xt[i], yt[i], rule)
            for l in range(len(W)):
                W[l] -= lr * gW[l]; b[l] -= lr * gb[l]
    return acc(W, b, xv, yv), acc(W, b, xs, ys)


def sign_flip(d):
    """Exact two-sided paired sign-flip p for mean(d) != 0."""
    d = np.asarray(d); obs = abs(d.sum())
    sums = [abs((d * s).sum()) for s in itertools.product((1, -1), repeat=len(d))]
    return float(np.mean(np.array(sums) >= obs - 1e-12))


def self_check():
    """Masked backprop matches finite differences on a small dendritic net; param budgets are matched."""
    rng = np.random.default_rng(0)
    x, y = rng.normal(size=(5, 6)), rng.integers(3, size=5)
    M = masks("dend", 6, 3, 2, 3, rng)
    W, b, B = init(M, rng)

    def loss():
        z = forward(W, b, x)[-1]; z = z - z.max(1, keepdims=True)
        return float(np.mean(np.log(np.exp(z).sum(1)) - z[np.arange(5), y]))
    gW, _ = grads(W, b, B, M, x, y, "bp")
    for l, (r, c) in ((0, tuple(np.argwhere(M[0])[0])), (1, (0, 0)), (2, (1, 2))):
        W[l][r, c] += 1e-6; up = loss(); W[l][r, c] -= 2e-6; dn = loss(); W[l][r, c] += 1e-6
        assert abs((up - dn) / 2e-6 - gW[l][r, c]) < 1e-6, f"layer {l} gradient wrong"
    for task, (budget, k, _) in TASKS.items():
        D, C = (8, 2) if task == "parity" else (40, 2) if task == "conjunction" else (64, 10)
        for arm in ARMS:
            w = width_for(arm, D, C, k, budget)
            p = n_params(masks(arm, D, C, w, k, rng))
            assert p == count(arm, D, C, w, k), f"{task} {arm}: closed-form count is wrong"
            assert abs(p - budget) <= 0.1 * budget, f"{task} {arm}: {p} params vs budget {budget}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--quick", action="store_true", help="2 seeds, lr 0.1, 1/10 of the epochs: a smoke run")
    ap.add_argument("--out", help="write a brain-result/1 file")
    a = ap.parse_args()
    seeds = range(1, 3 if a.quick else a.seeds + 1)
    runs, chosen = [], {}   # for --out; chosen: the tuned learning rate per task, arm and rule
    for task, (budget, k, ep) in TASKS.items():
        D, C = (8, 2) if task == "parity" else (40, 2) if task == "conjunction" else (64, 10)
        print(f"\n{task}: budget {budget} params, k = {k} branches, {ep} epochs"
              f" ({'train' if task == 'parity' else 'test'} accuracy, mean over {len(seeds)} seeds)")
        print(f"{'arm':>8} {'width':>5} {'params':>6} {'MACs':>5} {'tanh':>5}   "
              + "   ".join(f"{r}: lr  acc (sd)  vs point-1 / point-2" for r in RULES))
        res, lines = {}, {}
        for arm in ARMS:
            w = width_for(arm, D, C, k, budget)
            M = masks(arm, D, C, w, k, np.random.default_rng(0))
            lines[arm] = f"{arm:>8} {w:>5} {n_params(M):>6} {int(sum(m.sum() for m in M)):>5}" \
                         f" {sum(m.shape[1] for m in M[:-1]):>5}"
            for rule in RULES:
                lr = 0.1 if a.quick else max(LRS, key=lambda lr: np.mean(
                    [run(task, arm, rule, s, lr)[0] for s in TUNE_SEEDS]))
                res[arm, rule] = lr, np.array([run(task, arm, rule, s, lr, ep // 10 if a.quick else None)[1]
                                               for s in seeds])
                chosen[f"{task}/{arm}/{rule}"] = lr
                runs += [{"arm": f"{arm}/{rule}", "seed": s, "split": task, "status": "ok", "scores": {"acc": float(v)}}
                         for s, v in zip(seeds, res[arm, rule][1])]
        for arm in ARMS:
            for rule in RULES:
                lr, r = res[arm, rule]
                lines[arm] += f"   {lr:>4} {r.mean():.3f} ({r.std():.3f})"
                if arm == "dend":
                    for ref in ("point-1", "point-2"):
                        d = r - res[ref, rule][1]
                        lines[arm] += f" {d.mean():+.3f} p{sign_flip(d):.3f}"
            print(lines[arm])
    if a.out:
        out = make_result("dendritic-neurons", "python research/" + " ".join(sys.argv),
                          {"tasks": {t: {"budget": b, "branches": k, "epochs": e} for t, (b, k, e) in TASKS.items()},
                           "arms": ARMS, "rules": RULES, "lr_grid": LRS, "tune_seeds": list(TUNE_SEEDS),
                           "lr_chosen": chosen, "quick": a.quick, "seeds": list(seeds)},
                          {"params_per_task": {t: b for t, (b, _, _) in TASKS.items()}}, {"acc": "higher"},
                          runs, baseline="point-1/bp")
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)


if __name__ == "__main__":
    self_check()
    main()
