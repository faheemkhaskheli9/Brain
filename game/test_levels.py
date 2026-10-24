"""Winnability check: a scripted good play wins every level. Run: python game/test_levels.py

Plays the level engine (level_engine.py), so it needs no display and no tkinter. A level's
stars are None until it is won. test_levels_ui.py checks the Tk views on top of the engine.
"""
import level_engine as levels
import sim


def ticks(lvl, n):
    for _ in range(n):
        if lvl.over:
            break
        lvl.tick()


def play_spark(clicks_per_burst):
    lvl = levels.Spark()
    for t in range(levels.Spark.WINDOW):
        if t % 50 == 0 and t < 250:   # a burst every 50 ms, five bursts
            for _ in range(clicks_per_burst):
                lvl.click()
        ticks(lvl, 1)
    return lvl.stars


def test_spark():
    assert play_spark(2) == 3, "double clicks every 50 ms should fire exactly 5 spikes"
    assert play_spark(1) is None, "single 10 ms pulses stay below threshold"


def test_wire():
    lvl = levels.Wire()
    for _ in range(8):
        lvl.fire(0); ticks(lvl, 2)    # A, then output 4 ms later: A strengthens
        lvl.fire(2); ticks(lvl, 1)
        lvl.fire(1); ticks(lvl, 50)   # B 2 ms after the output: B weakens; then let traces fade
        if lvl.stars:
            break
    assert lvl.stars and lvl.stars >= 1, lvl.syn.w


def test_lesion():
    lvl = levels.Lesion()
    lvl.name("Thalamus")                  # nothing lesioned yet: not a mistake
    for name in levels.REGIONS:
        lvl.lesion(name)
        text, broken = lvl.jobs()
        assert broken and levels.REGIONS[name][1] in text, "the lesioned region's job must break"
        lvl.name(name)
    assert lvl.stars == 3 and lvl.mistakes == 0
    lvl = levels.Lesion()
    lvl.lesion("Hippocampus")
    for _ in range(4):
        lvl.name("Amygdala")
    assert lvl.over and lvl.stars is None, "a 4th wrong name fails the level"


def test_dopamine():
    lvl = levels.Dopamine()
    while not lvl.learned:
        lvl.trial(True, True)
        assert lvl.trials < 30, "the burst never moved to the bell"
    lvl.trial(False, True)
    lvl.trial(True, False)
    assert lvl.stars == 3


def test_remember():
    lvl = levels.Remember(seed=0)
    for _ in range(3):
        lvl.store_random()
    lvl.test()
    assert lvl.passed and lvl.stars is None, "3 random patterns must pass the recall test"
    while lvl.stars is None:
        lvl.store_random()
        lvl.test()
        assert len(lvl.net.patterns) < 30, "recall never broke"
    assert lvl.stars >= 1


def test_remember_draw_and_recall():
    lvl = levels.Remember(seed=0)
    for i in range(16):                   # draw the top two rows in one stroke
        (lvl.press if i == 0 else lvl.drag)(i)
    assert (lvl.state[:16] == 1).all() and (lvl.state[16:] == -1).all()
    lvl.store()
    lvl.show(-sim.np.ones(64))
    for i in range(8):                    # cue with the top row only
        (lvl.press if i == 0 else lvl.drag)(i)
    lvl.recall()
    ticks(lvl, 10)
    assert lvl.completed and (lvl.state[:16] == 1).all(), "recall should complete the stored drawing"


def play_sleep(replay):
    lvl = levels.Sleep()
    lvl.replay = replay
    while not lvl.over:
        lvl.day()
    return lvl.stars


def test_sleep():
    assert play_sleep(True), "replay should keep task A while B is learned"
    assert not play_sleep(False), "without replay task A should be forgotten"


def play_predict(percent):
    lvl = levels.Predict()
    lvl.world = sim.DotWorld(seed=0)
    lvl.set_gain(percent)
    ticks(lvl, 3 * levels.Predict.WINDOW)
    return lvl.stars


def test_predict():
    assert play_predict(20), "a mid gain should track the dot"
    assert not play_predict(100), "full trust in noisy senses should not"


def play_tiny_brain(dopamine, trace, seed=0):
    lvl = levels.TinyBrain()
    lvl.dopamine, lvl.trace = dopamine, trace
    lvl.run(seed)
    ticks(lvl, levels.TinyBrain.BUDGET)
    return lvl.stars


def test_tiny_brain():
    assert play_tiny_brain(True, True), "dopamine and trace together should win"
    assert not play_tiny_brain(False, True), "no dopamine, no learning"


def play_pattern(decay, rate):
    lvl = levels.Pattern(seed=0)
    lvl.decay, lvl.rate = decay, rate / 1000
    lvl.toggle()
    ticks(lvl, 1000)
    return lvl


def test_pattern():
    for rate in (1, 10, 50):
        lvl = play_pattern(False, rate)
        assert lvl.stars is None and lvl.ran_away, f"pure Hebb at rate {rate} should run away, never win"
    lvl = play_pattern(True, 10)
    assert lvl.stars == 2 and lvl.samples <= 300, (lvl.stars, lvl.samples)   # efficient, but no runaway seen


def test_zoo():
    lvl = levels.Zoo()
    lvl.run()                                    # default sliders are already regular spiking
    lvl.set(20, 0.12, -65, 0)                    # strong current, fast recovery: fast spiking
    lvl.run()
    assert lvl.stars is None and lvl.found == {"regular spiking", "fast spiking"}, lvl.found
    for a, _, c, d in list(sim.IZH_PRESETS.values())[1:3]:
        lvl.set(10, a, c, d)
        lvl.run()
    assert lvl.stars == 3 and lvl.runs == 4, (lvl.stars, lvl.runs)


def walk_to(lvl, target):
    """Arrow-key walk to a point (true position) along x, then y."""
    for axis, keys in ((0, ("Left", "Right")), (1, ("Down", "Up"))):
        while abs(lvl.nav.true[axis] - target[axis]) > levels.Home.STEP / 2:
            lvl.key(keys[int(lvl.nav.true[axis] < target[axis])])


def play_home(landmarks, via_landmark, seed=0):
    lvl = levels.Home()
    lvl.nav = sim.Navigator(seed=seed)
    lvl.food = sim.np.array([0.9, 0.55])
    lvl.landmarks = landmarks
    lvl.key("h")                                   # before the food: not allowed yet
    assert not lvl.over
    for spot in [(0.9, 0.1), (0.9, 0.9), (0.1, 0.9), (0.9, 0.55)]:   # a long search
        walk_to(lvl, spot)
    if via_landmark:
        walk_to(lvl, sim.LANDMARKS[0])
    lvl.key("h")
    return lvl


def test_home():
    lvl = play_home(True, True)
    assert lvl.stars == 3, (lvl.stars, lvl.nav.travelled, lvl.fixed)   # long route, landmark fixed real drift
    lvl = levels.Home()
    lvl.food = sim.np.array([0.6, 0.55])
    walk_to(lvl, lvl.food)
    walk_to(lvl, sim.NEST)                         # walk back by sight, then press H
    lvl.key("h")
    assert lvl.found and not lvl.over, "H next to the nest is refused: no map needed there"
    misses = sum(play_home(False, False, seed).stars is None for seed in range(10))
    assert misses >= 6, f"pure path integration over a long route should usually miss, missed {misses}/10"


def test_debrief_sweeps_show_the_lesson():
    *_, xs, ys = levels.Predict.sweep()
    best = ys.index(min(ys))
    assert 0 < best < len(xs) - 1, "tracking error should have a sweet spot inside the gain range"
    *_, xs, ys = levels.Remember.sweep()
    assert ys[2] > 0.95 and ys[-1] < 0.8, "3 memories recall, 20 do not"
    *_, xs, ys = levels.Home.sweep()
    assert ys[-1] > 2 * ys[0], "path-integration error should grow with distance walked"


def test_hint_on_failure():
    assert all(cls.hint for cls in levels.LEVELS), "every level needs a hint"
    lvl = levels.Lesion()
    lvl.lesion("Hippocampus")
    for _ in range(4):
        lvl.name("Amygdala")
    assert lvl.hint_text == "Hint: " + levels.Lesion.hint


def test_same_seed_same_level():
    a, b = levels.Home(seed=3), levels.Home(seed=3)
    assert (a.food == b.food).all()
    for lvl in (a, b):
        for k in ("Right", "Up") * 10:
            lvl.key(k)
    assert (a.nav.est == b.nav.est).all(), "a seeded level replays exactly"


def test_engine_has_no_ui():
    import sys
    assert "tkinter" not in sys.modules, "level_engine.py must not import tkinter"


def test_every_level_covered():
    played = {"Spark", "Wire", "Lesion", "Dopamine", "Remember", "Sleep", "Predict", "TinyBrain", "Pattern", "Zoo", "Home"}
    assert {cls.__name__ for cls in levels.LEVELS} == played


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
