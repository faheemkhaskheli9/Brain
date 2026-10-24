"""Do local credit-assignment rules reproduce here? H001-H003 of learning-algorithm-hypotheses.md (issue #92)

H001: predictive coding (PC) weight updates converge to backprop's gradients (Whittington & Bogacz 2017).
H002: feedback alignment (FA) trains hidden layers through fixed random feedback (Lillicrap et al. 2016).
H003: direct feedback alignment (DFA) sends the output error straight to each hidden layer (Nøkland 2016).
Method pre-registered on issue #92. A replication in a toy: it says what works here, not what cortex does.
Data: sklearn's bundled 8x8 digits (no download; pip install ".[research]").

Run: python research/credit_assignment.py [--seeds N] [--quick] [--out FILE.json]
--out writes the H002/H003 runs as the shared result file (#104): python research/result_schema.py FILE.json
"""
import argparse
import json
import sys

import numpy as np

try:
    from sklearn.datasets import load_digits
except ImportError:
    raise SystemExit('needs scikit-learn for the digits data: pip install ".[research]"') from None

from replay_selection import sign_flip
from result_schema import make_result

X_ALL, Y_ALL = load_digits(return_X_y=True)
X_ALL = X_ALL / 16.0
STEPS_T, NUDGE, PC_LR = (1, 10, 100, 1000), 0.01, 0.1
H, LR, BATCH, EPOCHS, N_TRAIN = 64, 0.05, 32, 30, 1197
RULES = ("bp", "fa", "dfa", "readout")


def cos(a, b):
    return float((a * b).sum() / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


# ---------- H001: PC updates vs backprop gradients (64-32-32-10, tanh, squared error) ----------
def pc_vs_bp(seed, T, nudge, var_out=1.0):
    """Cosine of the PC update with -grad, per weight matrix, after T inference steps.

    var_out is the output layer's variance in the energy (hidden layers have 1). The exploratory
    run sets it large: Whittington & Bogacz's limit, where the output error barely moves hidden nodes.
    """
    var = [1.0, 1.0, 1.0, var_out]
    rng = np.random.default_rng(seed)
    sizes = [64, 32, 32, 10]
    W = [rng.normal(size=(sizes[i], sizes[i + 1])) / np.sqrt(sizes[i]) for i in range(3)]
    i = rng.choice(len(Y_ALL), 32, replace=False)
    x0, y = X_ALL[i], np.eye(10)[Y_ALL[i]]
    phi = [lambda v: v, np.tanh, np.tanh]            # activation applied to layer l before it feeds l+1
    dphi = [None, lambda v: 1 - np.tanh(v) ** 2, lambda v: 1 - np.tanh(v) ** 2]
    # feedforward pass; x_l holds pre-activations, as in the PC network of section 2 of the topic file
    x = [x0]
    for l in range(3):
        x.append(phi[l](x[l]) @ W[l])
    out = x[3]
    target = out + nudge * (y - out) if nudge else y
    # backprop on L = 1/2 |target - out|^2
    d = [None] * 4
    d[3] = target - out
    for l in (2, 1):
        d[l] = dphi[l](x[l]) * (d[l + 1] @ W[l].T)
    bp = [phi[l](x[l]).T @ d[l + 1] for l in range(3)]
    # PC: clamp output, relax hidden nodes on the energy 1/2 sum |x_l - mu_l|^2
    x[3] = target
    for _ in range(T):
        e = [None] + [(x[l + 1] - phi[l](x[l]) @ W[l]) / var[l + 1] for l in range(3)]   # precision-weighted
        for l in (1, 2):
            x[l] = x[l] + PC_LR * (-e[l] + dphi[l](x[l]) * (e[l + 1] @ W[l].T))
    e = [None] + [(x[l + 1] - phi[l](x[l]) @ W[l]) / var[l + 1] for l in range(3)]
    pc = [phi[l](x[l]).T @ e[l + 1] for l in range(3)]   # local: presynaptic activity x own error
    return [cos(p, b) for p, b in zip(pc, bp)], cos(rng.normal(size=bp[0].shape), bp[0])


# ---------- H002, H003: BP vs FA vs DFA vs readout only (64-64-64-10, softmax) ----------
def train(seed, rule):
    """Return (test error, cosine of this rule's last-hidden error signal with backprop's on the test set)."""
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(Y_ALL))
    tr, te = perm[:N_TRAIN], perm[N_TRAIN:]
    W = [rng.normal(size=s) / np.sqrt(s[0]) for s in ((64, H), (H, H), (H, 10))]
    b = [np.zeros(H), np.zeros(H), np.zeros(10)]
    fb = np.random.default_rng(seed + 1000)          # fixed random feedback, same for every rule
    B3, B2, B1d = fb.normal(size=(10, H)) / np.sqrt(10), fb.normal(size=(H, H)) / np.sqrt(H), fb.normal(size=(10, H)) / np.sqrt(10)

    def fwd(x):
        h1 = np.tanh(x @ W[0] + b[0]); h2 = np.tanh(h1 @ W[1] + b[1])
        z = h2 @ W[2] + b[2]; z -= z.max(1, keepdims=True)
        p = np.exp(z); return h1, h2, p / p.sum(1, keepdims=True)

    def deltas(x, y):
        h1, h2, p = fwd(x)
        e = p.copy(); e[np.arange(len(y)), y] -= 1; e /= len(y)
        if rule == "dfa":
            d2 = (e @ B3) * (1 - h2 ** 2); d1 = (e @ B1d) * (1 - h1 ** 2)
        elif rule == "fa":
            d2 = (e @ B3) * (1 - h2 ** 2); d1 = (d2 @ B2) * (1 - h1 ** 2)
        else:   # bp (readout uses only e)
            d2 = (e @ W[2].T) * (1 - h2 ** 2); d1 = (d2 @ W[1].T) * (1 - h1 ** 2)
        return h1, h2, e, d1, d2

    for _ in range(EPOCHS):
        order = rng.permutation(tr)
        for k in range(0, len(order), BATCH):
            j = order[k:k + BATCH]
            x, y = X_ALL[j], Y_ALL[j]
            h1, h2, e, d1, d2 = deltas(x, y)
            W[2] -= LR * h2.T @ e; b[2] -= LR * e.sum(0)
            if rule != "readout":
                W[1] -= LR * h1.T @ d2; b[1] -= LR * d2.sum(0)
                W[0] -= LR * x.T @ d1; b[0] -= LR * d1.sum(0)
    xt, yt = X_ALL[te], Y_ALL[te]
    err = float((fwd(xt)[2].argmax(1) != yt).mean())
    _, h2, p = fwd(xt)
    e = p.copy(); e[np.arange(len(yt)), yt] -= 1
    true_d2 = (e @ W[2].T) * (1 - h2 ** 2)
    own_d2 = (e @ B3) * (1 - h2 ** 2) if rule in ("fa", "dfa") else true_d2
    return err, cos(own_d2, true_d2)


T975 = (12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262)   # t(0.975) for df 1-9


def ci95(v):
    """Half-width of the 95% t interval; table for df <= 9, Cornish-Fisher expansion above (error < 0.2%)."""
    v = np.asarray(v); df = len(v) - 1; z = 1.96
    t = T975[df - 1] if df <= 9 else z + (z ** 3 + z) / (4 * df) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * df ** 2)
    return t * v.std(ddof=1) / np.sqrt(len(v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--quick", action="store_true", help="2 seeds: a smoke run")
    ap.add_argument("--out", help="write the H002/H003 runs as a brain-result/1 file")
    a = ap.parse_args()
    seeds = range(1, 3 if a.quick else a.seeds + 1)

    print("H001: cosine(PC update, -backprop gradient) per weight matrix, median [min] over seeds")
    for nudge, name in ((NUDGE, f"small error (target {NUDGE:.0%} of the way)"), (0, "full error (target as given)")):
        print(f"  {name}")
        for T in STEPS_T:
            res = [pc_vs_bp(s, T, nudge) for s in seeds]
            c = np.array([r[0] for r in res])
            cols = "  ".join(f"W{l + 1} {np.median(c[:, l]):.4f} [{c[:, l].min():.4f}]" for l in range(3))
            print(f"    T={T:>4}  {cols}")
    print(f"  random-matrix baseline: median {np.median([pc_vs_bp(s, 1, NUDGE)[1] for s in seeds]):+.4f}")
    print("  exploratory (not pre-registered): full error, output variance raised, T=1000")
    for v in (10, 100, 1000):
        c = np.array([pc_vs_bp(s, 1000, 0, v)[0] for s in seeds])
        print(f"    var_out={v:>4}  " + "  ".join(f"W{l + 1} {np.median(c[:, l]):.4f} [{c[:, l].min():.4f}]" for l in range(3)))

    print("\nH002/H003: test error on digits, mean +/- 95% CI over seeds; paired vs readout only")
    res = {r: [train(s, r) for s in seeds] for r in RULES}
    ro = np.array([v[0] for v in res["readout"]])
    for r in RULES:
        err = np.array([v[0] for v in res[r]])
        line = f"  {r:>8} {err.mean():.4f} +/- {ci95(err):.4f}  align(h2) {np.mean([v[1] for v in res[r]]):.3f}"
        if r != "readout":
            d = err - ro
            line += f"  vs readout {d.mean():+.4f} (sign-flip p {sign_flip(d):.4f})"
        print(line)
    if a.out:
        runs = [{"arm": r, "seed": s, "status": "ok", "scores": {"error": v[0], "align_h2": v[1]}}
                for r in RULES for s, v in zip(seeds, res[r])]
        out = make_result("credit-assignment", "python research/" + " ".join(sys.argv),
                          {"rules": RULES, "hidden": H, "lr": LR, "batch": BATCH, "epochs": EPOCHS,
                           "n_train": N_TRAIN, "data": "sklearn digits 8x8", "seeds": list(seeds)},
                          {"epochs": EPOCHS}, {"error": "lower"}, runs, baseline="readout")
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)


if __name__ == "__main__":
    # Self-check: PC must match backprop in the theorem's regime, and backprop must beat readout only.
    assert min(pc_vs_bp(1, 1000, NUDGE)[0]) > 0.9, "PC does not approach backprop even for a small error"
    assert train(1, "bp")[0] < train(1, "readout")[0], "hidden layers do not help: the task is too easy"
    main()
