"""Which replay selection rule protects old tasks best, and does SHY-style downscaling change that? (issue #84)

A numpy MLP learns 5 tasks in a row. While it learns task t, each step also replays b stored samples of
the earlier tasks, chosen by one of four rules; optionally every weight and bias (as pre-registered) is
scaled by DOWN after each task
(a "night" of synaptic downscaling, Tononi & Cirelli 2014). Method pre-registered on issue #84.
A computational result: it says which rule works in this toy, not what the hippocampus selects.

Run: python research/replay_selection.py [--seeds N] [--quick] [--out FILE.json]
--out writes the shared result file (#104): python research/result_schema.py FILE.json
"""
import argparse
import itertools
import json
import sys

import numpy as np

from result_schema import make_result

T, D, H, STEPS, BATCH, LR, MEM, DOWN = 5, 20, 64, 300, 16, 0.05, 50, 0.8
RULES = ("random", "recent", "error", "rare")
BUDGETS = (1, 4, 16)


def make_tasks(rng, n=400):
    """Task t: x ~ N(c_t, I), |c_t| = 3, label = side of a random hyperplane through c_t."""
    tasks = []
    for _ in range(T):
        c = rng.normal(size=D); c *= 3 / np.linalg.norm(c)
        w = rng.normal(size=D)
        x = c + rng.normal(size=(2 * n, D))
        y = ((x - c) @ w > 0).astype(int)
        tasks.append((x[:n], y[:n], x[n:], y[n:]))   # train, test
    return tasks


def forward(P, x):
    h = np.maximum(0, x @ P["W1"] + P["b1"])
    z = h @ P["W2"] + P["b2"]
    z -= z.max(1, keepdims=True)
    p = np.exp(z); p /= p.sum(1, keepdims=True)
    return h, p


def sgd(P, x, y):
    h, p = forward(P, x)
    g = p.copy(); g[np.arange(len(y)), y] -= 1; g /= len(y)
    gh = (g @ P["W2"].T) * (h > 0)
    P["W2"] -= LR * h.T @ g; P["b2"] -= LR * g.sum(0)
    P["W1"] -= LR * x.T @ gh; P["b1"] -= LR * gh.sum(0)


def acc(P, x, y):
    return float((forward(P, x)[1].argmax(1) == y).mean())


def pick(rule, rng, mx, my, mtask, count, t, P, b):
    """Indices of b memory items to replay while learning task t (memory holds tasks < t)."""
    if rule == "random":
        w = np.ones(len(my))
    elif rule == "recent":   # each older task half as likely as the one after it
        w = 0.5 ** (t - 1 - mtask)
    elif rule == "error":    # current cross-entropy, as prioritized replay with alpha = 1
        w = -np.log(forward(P, mx)[1][np.arange(len(my)), my] + 1e-9) + 1e-6
    else:                    # rare: the least replayed first
        w = 1 / (1 + count)
    return rng.choice(len(my), size=b, p=w / w.sum())


def run(seed, rule=None, b=0, down=False):
    """Train the 5 tasks in order; return (backward transfer, final mean accuracy, samples replayed)."""
    rng = np.random.default_rng(seed)
    tasks = make_tasks(rng)
    P = {"W1": rng.normal(size=(D, H)) / np.sqrt(D), "b1": np.zeros(H),
         "W2": rng.normal(size=(H, 2)) / np.sqrt(H), "b2": np.zeros(2)}
    R = np.zeros((T, T))   # R[i, j]: accuracy on task j after learning task i
    mx, my, mtask = np.empty((0, D)), np.empty(0, int), np.empty(0, int)
    count, replayed = np.empty(0), 0
    for t, (x, y, _, _) in enumerate(tasks):
        for _ in range(STEPS):
            i = rng.integers(len(y), size=BATCH)
            bx, by = x[i], y[i]
            if rule and t:
                j = pick(rule, rng, mx, my, mtask, count, t, P, b)
                np.add.at(count, j, 1); replayed += b
                bx, by = np.concatenate([bx, mx[j]]), np.concatenate([by, my[j]])
            sgd(P, bx, by)
        R[t] = [acc(P, tx, ty) for _, _, tx, ty in tasks]
        keep = rng.choice(len(y), MEM, replace=False)
        mx, my = np.concatenate([mx, x[keep]]), np.concatenate([my, y[keep]])
        mtask, count = np.concatenate([mtask, np.full(MEM, t)]), np.concatenate([count, np.zeros(MEM)])
        if down and t < T - 1:   # a night of proportional downscaling before the next task
            for k in P:
                P[k] *= DOWN
    bwt = float(np.mean([R[-1, j] - R[j, j] for j in range(T - 1)]))
    return bwt, float(R[-1].mean()), replayed


def sign_flip(d):
    """Exact two-sided paired sign-flip p for mean(d) != 0."""
    d = np.asarray(d); obs = abs(d.sum())
    sums = [abs((d * s).sum()) for s in itertools.product((1, -1), repeat=len(d))]
    return float(np.mean(np.array(sums) >= obs - 1e-12))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--quick", action="store_true", help="2 seeds, budget 4 only: a smoke run")
    ap.add_argument("--out", help="write a brain-result/1 file")
    a = ap.parse_args()
    seeds = range(1, 3 if a.quick else a.seeds + 1)
    budgets = (4,) if a.quick else BUDGETS
    runs = []   # for --out: arm "none" or "<rule>-b<budget>", "+down" with downscaling

    def record(arm, res):
        runs.extend({"arm": arm, "seed": s, "status": "ok", "scores": {"bwt": r[0], "final": r[1], "replayed": r[2]}}
                    for s, r in zip(seeds, res))

    for down in (False, True):
        base = [run(s, down=down) for s in seeds]
        record("none" + "+down" * down, base)
        print(f"\ndownscaling {'x' + str(DOWN) + ' after each task' if down else 'off'}:"
              f" no replay BWT {np.mean([r[0] for r in base]):+.3f}, final acc {np.mean([r[1] for r in base]):.3f}")
        print(f"{'budget':>6} {'rule':>7} {'BWT':>7} {'final':>6} {'gain/1k':>8}  vs random (paired)")
        for b in budgets:
            res = {rule: [run(s, rule, b, down) for s in seeds] for rule in RULES}
            for rule in RULES:
                record(f"{rule}-b{b}" + "+down" * down, res[rule])
            for rule in RULES:
                bwt = np.array([r[0] for r in res[rule]])
                gain = np.mean([(r[0] - n[0]) / (r[2] / 1000) for r, n in zip(res[rule], base)])
                line = f"{b:>6} {rule:>7} {bwt.mean():+.3f} {np.mean([r[1] for r in res[rule]]):.3f} {gain:+8.4f}"
                if rule != "random":
                    d = bwt - np.array([r[0] for r in res["random"]])
                    line += f"  BWT {d.mean():+.3f} (p {sign_flip(d):.3f})"
                print(line)
    if a.out:
        r = make_result("replay-selection", "python research/" + " ".join(sys.argv),
                        {"T": T, "D": D, "H": H, "steps": STEPS, "batch": BATCH, "lr": LR, "mem": MEM, "down": DOWN,
                         "rules": RULES, "budgets": budgets, "seeds": list(seeds)},
                        {"steps_per_task": STEPS, "memory_per_task": MEM}, {"bwt": "higher", "final": "higher"},
                        runs, baseline="none")
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(r, fh, indent=1)


if __name__ == "__main__":
    # Self-check: replay must cut forgetting in this toy, or the comparison means nothing.
    no, rep = run(1), run(1, "random", 16)
    assert no[0] < -0.05, f"no forgetting without replay (BWT {no[0]:+.3f}): the tasks do not interfere"
    assert rep[0] > no[0], "random replay did not reduce forgetting"
    main()
