"""Brain-match scorecard: each Brain Lab model against published experimental data.

test_sim.py checks that a lesson holds inside its model. This checks a model against
what real brains were recorded doing, one row per reference. It is a per-level table,
not one "brain-likeness" score: neural and behavioural scores barely correlate
(Ahlert et al. 2024, https://arxiv.org/abs/2407.07530).

Run: python game/eval.py   (exits 1 if any row fails)
"""
import sys

import numpy as np

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


MURRE = "Murre & Dros 2015 (PLOS ONE 10:e0120644), Table 3"
# Savings at 20 min, 1 h, 9 h, 1 d, 2 d, 6 d, 31 d, read from the table image (doi:10.1371/journal.pone.0120644.t003).
SAVINGS_DAYS = [20 / 1440, 1 / 24, 9 / 24, 1, 2, 6, 31]
SAVINGS = {"Ebbinghaus 1885": [0.582, 0.442, 0.358, 0.337, 0.278, 0.254, 0.211],
           "Dros 2015": [0.472, 0.373, 0.276, 0.317, 0.230, 0.168, 0.041]}


def front_loaded(t, y):
    """Share of the total loss already gone 1/8 of the way through the span (time axes rescaled)."""
    t_eighth = t[0] + (t[-1] - t[0]) / 8
    return (y[0] - np.interp(t_eighth, t, y)) / (y[0] - y[-1])


def level6_forgetting():
    """Level 6 forgetting of task A vs the human savings curve (issue #27). Shape only."""
    DAYS, curves = 8, {}   # level 6's day budget (levels.Sleep.DAYS; levels imports tkinter)
    for replay in (False, True):
        a, b = sim.make_tasks()
        net = sim.Associator()
        net.train(*a, 50)
        curves[replay] = [net.accuracy(*a)]
        for _ in range(DAYS):
            sim.sleep_day(net, a, b, replay)
            curves[replay].append(net.accuracy(*a))
    plain = curves[False]
    model = front_loaded(np.arange(DAYS + 1), plain)
    human = ", ".join(f"{k} {front_loaded(SAVINGS_DAYS, v):.0%}" for k, v in SAVINGS.items())
    return [
        # The day mapping is arbitrary and the model is a linear associator, so only the shape counts.
        (6, MURRE, "qualitative: without replay, A decays fast then slowly (share of loss in first 1/8 of span)",
         f"model {model:.0%} (A {plain[0]:.0%} -> {plain[-1]:.0%}); {human}",
         all(x >= y for x, y in zip(plain, plain[1:])) and model >= 0.5),
        # Murre & Dros review the evidence that sleep reduces forgetting (Jenkins & Dallenbach 1924
        # onward) and find a jump at 24 h in Dros's curve. Replay as the cause is a hypothesis, and
        # the model never shows the jump: accuracy only falls.
        (6, MURRE, "qualitative, hypothesis: sleep replay sharply reduces forgetting",
         f"A after {DAYS} days: {curves[True][-1]:.0%} with replay, {plain[-1]:.0%} without",
         curves[True][-1] >= 0.8 > plain[-1]),
    ]


ROWS = [level4_td, level6_forgetting]


def main():
    rows = [r for fn in ROWS for r in fn()]
    for level, ref, metric, score, ok in rows:
        print(f"L{level}  {'pass' if ok else 'FAIL'}  {metric}: {score}\n         {ref}")
    failed = sum(not r[-1] for r in rows)
    print(f"\n{len(rows) - failed}/{len(rows)} rows pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
