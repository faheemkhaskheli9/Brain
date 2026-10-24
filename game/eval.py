"""Brain-match scorecard: each Brain Lab model against published experimental data.

test_sim.py checks that a lesson holds inside its model. This checks a model against
what real brains were recorded doing, one row per reference. It is a per-level table,
not one "brain-likeness" score: neural and behavioural scores barely correlate
(Ahlert et al. 2024, https://arxiv.org/abs/2407.07530).

Run: python game/eval.py   (exits 1 if any row fails)
"""
import sys

import numpy as np

import level_engine
import sim

ALLEN = "Allen Cell Types Database, mouse L2/3 cell 490170480 (Cux2), GLIF1 model 491611694"
# api.brain-map.org, fetched 2026-10-11. EphysSweep: 1 s long-square sweeps 30-37, spike count
# = rate in Hz (repeat sweeps 38-44 left out). EphysFeature 490171104: rheobase, input resistance,
# tau, Vrest, threshold. GLIF1 neuron_config (well_known_file 501129012): R_input, C,
# th_inf x coeffs.th_inf, reset to rest, spike_cut_length 94 x dt 0.05 ms.
FI_PA = [70, 90, 110, 130, 150, 170, 190, 210]
FI_HZ = [1, 9, 14, 18, 23, 26, 31, 34]
RHEOBASE_PA = 70
CELL = dict(tau_m=20.05, r=199.3, v_th=sim.V_REST + (-49.78 + 77.29), v_reset=sim.V_REST)
GLIF1 = dict(tau_m=181.73 * 0.07294, r=181.73, v_th=sim.V_REST + 30.115 * 1.06096,
             v_reset=sim.V_REST, t_ref=94 * 0.05)


def fi_rate(params, pa, ms=1000.0, dt=0.05):
    """Spikes per second for a 1 s current step of pa picoamps."""
    n = sim.LIF(**params)
    return sum(n.step(pa / 1000, dt) for _ in range(int(ms / dt))) * 1000 / ms


def rheobase(params):
    """Smallest step that ever fires a linear LIF: (threshold - rest) / R, in pA."""
    p = dict(r=sim.R, v_th=sim.V_TH) | params
    return round((p["v_th"] - sim.V_REST) / p["r"] * 1000)


def level1_lif():
    """Level 1 LIF neuron vs a recorded mouse cortical neuron (issue #24)."""
    def rmse(params):
        return np.sqrt(np.mean([(fi_rate(params, pa) - hz) ** 2 for pa, hz in zip(FI_PA, FI_HZ)]))
    ours, base = rmse(CELL), rmse(GLIF1)
    rheo = {name: rheobase(p) for name, p in (("game", {}), ("cell-params", CELL), ("GLIF1", GLIF1))}
    return [
        # Neither model is fitted to these steps: ours takes the cell's own passive features, GLIF1
        # was fitted by Allen to noise stimuli. Spike-time match on a held-out sweep is left out:
        # spike times are only in the NWB file, and the game keeps no Allen SDK dependency.
        (1, ALLEN, "f-I curve: LIF with the cell's measured R, tau and threshold vs Allen's GLIF1 fit",
         f"RMSE {ours:.1f} Hz vs GLIF1 {base:.1f} Hz over {FI_PA[0]}-{FI_PA[-1]} pA", ours <= base),
        # A linear membrane predicts a rheobase of (threshold - rest) / R; the real cell fires
        # sooner because its membrane is not linear near threshold. The game's R of 10 MOhm is
        # about 20x below this cell's input resistance, so its neuron needs nA, not pA.
        (1, ALLEN, "rheobase: smallest 1 s step that fires",
         f"cell {RHEOBASE_PA} pA; " + ", ".join(f"{k} {v} pA" for k, v in rheo.items()), None),
    ]


BI_POO = "Bi & Poo 1998 (J Neurosci 18:10464), Fig. 7 text and Figs. 2C, 3C"
# Stated in the paper's text, not digitized from the Fig. 7 scatter: LTP when post fires within
# 20 ms after pre, LTD within 20 ms before, "essentially absent" outside the 40 ms window.
# Mean change after 60 pairings at about +5 ms (Fig. 2C) and -5/-6 ms (Fig. 3C).
LTP_PCT, LTD_PCT = 48.4, -18.0


def stdp_pairing(dt):
    """Weight change from one pre/post pairing; dt = t_post - t_pre in ms."""
    s = sim.STDP(1)
    first, second = (lambda: s.pre(0), s.post) if dt > 0 else (s.post, lambda: s.pre(0))
    first()
    s.decay(abs(dt))
    second()
    return s.w[0] - 0.5


def level2_stdp():
    """Level 2 STDP rule vs the spike-timing window in rat hippocampal cultures (issue #25)."""
    bins = [5, 10, 15, 20]
    signs = sum(stdp_pairing(t) > 0 for t in bins) + sum(stdp_pairing(-t) < 0 for t in bins)
    peak = stdp_pairing(5)
    edge = max(abs(stdp_pairing(40)), abs(stdp_pairing(-40))) / peak
    ratio = stdp_pairing(5) / -stdp_pairing(-5)
    return [
        (2, BI_POO, "sign: pre-then-post potentiates, post-then-pre depresses (|dt| 5-20 ms)",
         f"{signs}/{2 * len(bins)} bins agree", signs == 2 * len(bins)),
        # "Outside the 40 msec window" may mean +-20 ms or +-40 ms; at +-40 ms this rule still
        # keeps exp(-35/20) of its peak, so the threshold is "under a fifth", not zero.
        (2, BI_POO, "window: change at +-40 ms under a fifth of the peak at +5 ms",
         f"{edge:.0%} of peak (e-fold {sim.TAU_STDP:.0f} ms)", edge < 0.2),
        # Game rule uses one gain and one time constant for both sides, so it cannot be asymmetric.
        (2, BI_POO, "magnitude: potentiation larger than depression (+5 vs -5 ms)",
         f"model LTP/LTD {ratio:.1f}, paper {LTP_PCT / -LTD_PCT:.1f}", None),
    ]


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


AMIT = "Amit, Gutfreund & Sompolinsky 1985 (Phys Rev Lett 55:1530), theory, not recordings"


def hopfield_capacity(n, seed, ok=0.9):
    """Random patterns stored before mean recall overlap (10% of bits flipped) drops below ok."""
    rng = np.random.default_rng(seed)
    net = sim.Hopfield(n)
    while True:
        net.store(rng.choice([-1.0, 1.0], n))
        if np.mean(net.test(seed=seed)) < ok:
            return len(net.patterns) - 1


def level5_hopfield():
    """Level 5 Hopfield net vs its theoretical capacity (issue #28). No human dataset fits."""
    n, seeds = 64, 10   # level 5's network size
    caps = [hopfield_capacity(n, s) for s in range(seeds)]
    alpha = np.mean(caps) / n
    return [
        # 0.138 N is the limit for large N; small nets hold somewhat more on this lenient
        # criterion (mean overlap, not every pattern), so the band is 0.10-0.20 N.
        (5, AMIT, "internal check: capacity near 0.138 N random patterns",
         f"{alpha:.3f} N ({min(caps)}-{max(caps)} of {n} over {seeds} seeds)", 0.10 <= alpha <= 0.20),
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
    DAYS, curves = level_engine.Sleep.DAYS, {}   # level 6's day budget
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


PURSUIT = "Becker & Fuchs 1985 (Exp Brain Res 57:562); Orban de Xivry et al. 2006 (J Neurophysiol 95:418)"


def level7_occlusion(gain=0.2, seconds=12.0, dt=0.02):
    """Level 7 tracker behind the occluder vs human smooth pursuit of a hidden target (issue #28)."""
    world, tr = sim.DotWorld(0), sim.Tracker(gain)
    err, frozen, runs, last = [], [], [], None   # runs: belief velocities, one list per occlusion
    hidden = False
    for _ in range(int(seconds / dt)):
        obs = world.step(dt)
        pos = tr.step(obs, dt)
        if obs is not None:
            last, hidden = obs, False
            continue
        if not hidden:
            runs.append([])
            hidden = True
        err.append(abs(pos - world.x))
        frozen.append(abs(last - world.x))
        runs[-1].append((world.v, tr.vel))
    same_dir = all(np.sign(v) == np.sign(b) for run in runs for v, b in run)
    ratio = np.mean([run[-1][1] / run[0][1] for run in runs])
    return [
        # Eyes keep moving with a hidden target instead of stopping where it vanished.
        (7, PURSUIT, "prediction continues while hidden: belief moves with the target, beats freeze-at-last-seen",
         f"direction {'right' if same_dir else 'WRONG'} throughout, error {np.mean(err):.3f} vs frozen {np.mean(frozen):.3f}",
         same_dir and np.mean(err) < np.mean(frozen)),
        # Human eye velocity decays toward a plateau scaled to target speed; the alpha-beta
        # tracker coasts at a constant velocity until the target reappears.
        (7, PURSUIT, "velocity decays during occlusion",
         f"belief speed at end / start of each occlusion {ratio:.2f} (1.00 = no decay)", None),
    ]


HOWE = "Howe et al. 2013 (Nature 500:575); Hamid et al. 2016 (Nat Neurosci 19:117)"


def level8_ramp(learn=3000, probe=2000):
    """Level 8 forager vs striatal dopamine ramps as rats approach a goal (issue #28)."""
    f = sim.Forager(seed=0)
    for _ in range(learn):
        f.step()
    V, delta = {}, {}
    for _ in range(probe):
        d = 2 * (f.size - 1) - f.pos[0] - f.pos[1]   # steps to food
        V.setdefault(d, []).append(f.V[f._s(f.pos)])
        delta.setdefault(d, []).append(f.step())
    dist = sorted(V)
    v = [np.mean(V[d]) for d in dist]
    td = [np.mean(delta[d]) for d in dist]
    return [
        # Hamid et al. read the ramp as value; reading model V as dopamine is that hypothesis.
        (8, HOWE, "hypothesis (dopamine = value): signal ramps up as the goal nears",
         f"V {v[-1]:.2f} at {dist[-1]} steps -> {v[0]:.2f} at {dist[0]}",
         all(a > b for a, b in zip(v, v[1:]))),
        # Plain TD error goes flat once every state's value is learned, so it cannot ramp.
        (8, HOWE, "TD error itself ramps up as the goal nears",
         f"mean TD error {td[-1]:+.3f} at {dist[-1]} steps, {td[0]:+.3f} at {dist[0]}", None),
    ]


ROWS = [level1_lif, level2_stdp, level4_td, level5_hopfield, level6_forgetting, level7_occlusion, level8_ramp]


def main():
    rows = [r for fn in ROWS for r in fn()]
    for level, ref, metric, score, ok in rows:
        status = "gap " if ok is None else "pass" if ok else "FAIL"   # gap: known mismatch, not scored
        print(f"L{level}  {status}  {metric}: {score}\n         {ref}")
    scored = [r for r in rows if r[-1] is not None]
    failed = sum(not r[-1] for r in scored)
    print(f"\n{len(scored) - failed}/{len(scored)} rows pass, {len(rows) - len(scored)} known gaps")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
