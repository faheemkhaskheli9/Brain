"""Headless checks for every Brain Lab model. Run: python game/test_sim.py"""
import numpy as np

import sim


def test_lif():
    n = sim.LIF()
    assert not any(n.step(1.0, 1.0) for _ in range(500)), "below threshold must never spike"
    n = sim.LIF()   # one 10 ms click pulse peaks just under threshold (level 1 needs 2 clicks)
    assert not any(n.step(2.0 if t < 10 else 0.0, 1.0) for t in range(50))
    n = sim.LIF()
    spikes = [t for t in range(200) if n.step(2.0, 1.0)]
    assert len(spikes) >= 3 and min(np.diff(spikes)) > sim.T_REF, "steady drive fires, refractory spaced"


def test_stdp():
    s = sim.STDP(2)
    s.pre(0); s.decay(5); s.post()                       # pre then post
    assert s.w[0] > 0.5 and s.w[1] == 0.5
    s = sim.STDP(2)
    s.post(); s.decay(5); s.pre(1)                       # post then pre
    assert s.w[1] < 0.5 and s.w[0] == 0.5
    s = sim.STDP(1)
    s.pre(0); s.decay(200); s.post()                     # far outside the ~20 ms window
    assert abs(s.w[0] - 0.5) < 1e-3


def test_td_dopamine_moves_to_the_bell():
    V = sim.td_values()
    first = sim.td_trial(V, bell=True, juice=True)
    assert first[sim.T_JUICE] == 1.0 and first[sim.T_BELL] == 0.0
    for _ in range(30):
        d = sim.td_trial(V, bell=True, juice=True)
    assert d[sim.T_BELL] > 0.9 and abs(d[sim.T_JUICE]) < 0.1
    assert sim.td_trial(V.copy(), bell=True, juice=False)[sim.T_JUICE] < -0.9   # omission dip
    assert sim.td_trial(V.copy(), bell=False, juice=True)[sim.T_JUICE] == 1.0   # unpredicted juice


def test_hopfield_recall_and_capacity():
    rng = np.random.default_rng(1)
    h = sim.Hopfield(64)
    for _ in range(3):
        h.store(rng.choice([-1, 1], 64))
    assert min(h.test()) > 0.95
    for _ in range(17):   # 20 patterns, far past ~0.14 * 64 = 9
        h.store(rng.choice([-1, 1], 64))
    assert min(h.test()) < 0.8


def test_replay_prevents_forgetting():
    a, b = sim.make_tasks()
    result = {}
    for replay in (False, True):
        net = sim.Associator()
        net.train(*a, 50)
        assert net.accuracy(*a) == 1.0
        for _ in range(3):
            sim.sleep_day(net, a, b, replay)
        result[replay] = net.accuracy(*a), net.accuracy(*b)
    assert result[False][0] < 0.7 and result[False][1] > 0.9, result   # B learned, A forgotten
    assert result[True][0] > 0.8 and result[True][1] > 0.9, result     # both kept


def test_tracking_gain_has_a_sweet_spot():
    best = sim.tracking_error(0.2)
    assert best < 0.035
    assert sim.tracking_error(0.02) > 2 * best and sim.tracking_error(1.0) > 2 * best


def test_forager_needs_dopamine_and_trace():
    def steps(**kw):
        out = []
        for seed in range(10):
            f = sim.Forager(seed=seed, **kw)
            while f.eaten < 10 and f.steps < 3000:
                f.step()
            out.append(f.steps)
        return np.median(out)
    full, no_trace, no_da = steps(), steps(trace=False), steps(dopamine=False)
    assert full < 400 < no_trace < no_da, (full, no_trace, no_da)


def test_oja_finds_pc1_and_hebb_explodes():
    X = np.random.default_rng(0).multivariate_normal([0, 0], sim.OJA_COV, size=2000)
    w = h = np.array([0.1, -0.5])
    for x in X:
        w = sim.oja_step(w, x, 0.005)
    assert sim.alignment(w) > 0.99 and abs(np.linalg.norm(w) - 1) < 0.1, w
    for x in X[:500]:
        h = sim.oja_step(h, x, 0.005, decay=False)
    assert np.linalg.norm(h) > 5, "pure Hebb should grow without bound"


def test_izhikevich_presets_fire_their_patterns_and_lif_never_bursts():
    for kind, params in sim.IZH_PRESETS.items():
        assert sim.firing_pattern(sim.izhikevich(*params, 10)[0]) == kind, kind
    lif = {sim.firing_pattern(sim.lif_run(I)[0]) for I in range(21)}
    assert lif <= {"too few spikes", "regular spiking", "fast spiking"}, lif


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
