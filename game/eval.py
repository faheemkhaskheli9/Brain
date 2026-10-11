"""Brain-match scorecard: each Brain Lab model against published experimental data.

test_sim.py checks that a lesson holds inside its model. This checks a model against
what real brains were recorded doing, one row per reference. It is a per-level table,
not one "brain-likeness" score: neural and behavioural scores barely correlate
(Ahlert et al. 2024, https://arxiv.org/abs/2407.07530).

Run: python game/eval.py   (exits 1 if any row fails)
"""
import sys

import sim

SCHULTZ = "Schultz, Dayan & Montague 1997 (Science 275:1593)"
HOLLERMAN = "Hollerman & Schultz 1998 (Nat Neurosci 1:304)"


def level4_td():
    """Level 4 TD learner vs dopamine-neuron recordings in monkeys (issue #26)."""
    V = sim.td_values()
    first = sim.td_trial(V, bell=True, juice=True)
    trials = 1
    while trials < 200:
        d = sim.td_trial(V, bell=True, juice=True)
        trials += 1
        if d[sim.T_BELL] >= 0.8 and abs(d[sim.T_JUICE]) <= 0.2:
            break
    omit = sim.td_trial(V.copy(), bell=True, juice=False)
    late = sim.td_trial(V.copy(), bell=True, juice=True, t_juice=sim.T_JUICE + 2)
    j, b = sim.T_JUICE, sim.T_BELL
    return [
        (4, SCHULTZ, "before learning: burst at reward, none at cue",
         f"reward {first[j]:+.2f}, cue {first[b]:+.2f}", first[j] > 0.5 and abs(first[b]) < 0.1),
        (4, SCHULTZ, "after learning: burst at cue, none at predicted reward",
         f"cue {d[b]:+.2f}, reward {d[j]:+.2f} after {trials} trials (game gain, not animal trials)",
         d[b] > 0.5 and abs(d[j]) < 0.2),
        (4, SCHULTZ, "reward withheld: dip when it was due",
         f"{omit[j]:+.2f}", omit[j] < -0.5),
        # Early reward is left out: they saw a burst at the new time but no dip at the old
        # one, and this tapped-delay-line TD model predicts a dip there.
        (4, HOLLERMAN, "reward delayed: dip at the usual time, burst at the new time",
         f"usual {late[j]:+.2f}, new {late[j + 2]:+.2f}", late[j] < -0.5 and late[j + 2] > 0.5),
    ]


ROWS = [level4_td]


def main():
    rows = [r for fn in ROWS for r in fn()]
    for level, ref, metric, score, ok in rows:
        print(f"L{level}  {'pass' if ok else 'FAIL'}  {metric}: {score}\n         {ref}")
    failed = sum(not r[-1] for r in rows)
    print(f"\n{len(rows) - failed}/{len(rows)} rows pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
