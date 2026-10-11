"""Headless winnability check: a scripted good play wins every level. Run: python game/test_levels.py

Needs a display for tkinter (the root window is withdrawn). On a headless Linux box use
xvfb-run python game/test_levels.py.
"""
import tkinter as tk

import levels
import sim

ROOT = tk.Tk()
ROOT.withdraw()


def start(cls):
    frame = tk.Frame(ROOT)
    won = []
    return cls(frame, won.append), won


def ticks(lvl, n):
    for _ in range(n):
        if lvl.over:
            break
        lvl.tick()


def play_spark(clicks_per_burst):
    lvl, won = start(levels.Spark)
    for t in range(levels.Spark.WINDOW):
        if t % 50 == 0 and t < 250:   # a burst every 50 ms, five bursts
            for _ in range(clicks_per_burst):
                lvl.click()
        ticks(lvl, 1)
    return won


def test_spark():
    assert play_spark(2) == [3], "double clicks every 50 ms should fire exactly 5 spikes"
    assert play_spark(1) == [], "single 10 ms pulses stay below threshold"


def test_wire():
    lvl, won = start(levels.Wire)
    for _ in range(8):
        lvl.fire(0); ticks(lvl, 2)    # A, then output 4 ms later: A strengthens
        lvl.fire(2); ticks(lvl, 1)
        lvl.fire(1); ticks(lvl, 50)   # B 2 ms after the output: B weakens; then let traces fade
        if won:
            break
    assert won and won[0] >= 1, lvl.syn.w


def test_brain_map():
    lvl, won = start(levels.BrainMap)
    while lvl.order:
        lvl.pick(lvl.order[0])
    assert won == [3]


def test_dopamine():
    lvl, won = start(levels.Dopamine)
    while not lvl.learned:
        lvl.trial(True, True)
        assert lvl.trials < 30, "the burst never moved to the bell"
    lvl.trial(False, True)
    lvl.trial(True, False)
    assert won == [3]


def test_remember():
    lvl, won = start(levels.Remember)
    lvl.rng = sim.np.random.default_rng(0)
    for _ in range(3):
        lvl.store_random()
    lvl.test()
    assert lvl.passed and not won, "3 random patterns must pass the recall test"
    while not won:
        lvl.store_random()
        lvl.test()
        assert len(lvl.net.patterns) < 30, "recall never broke"
    assert won[0] >= 1


def play_sleep(replay):
    lvl, won = start(levels.Sleep)
    lvl.replay.set(replay)
    while not lvl.over:
        lvl.day()
    return won


def test_sleep():
    assert play_sleep(True), "replay should keep task A while B is learned"
    assert not play_sleep(False), "without replay task A should be forgotten"


def play_predict(percent):
    lvl, won = start(levels.Predict)
    lvl.world = sim.DotWorld(seed=0)
    lvl.set_gain(percent)
    ticks(lvl, 3 * levels.Predict.WINDOW)
    return won


def test_predict():
    assert play_predict(20), "a mid gain should track the dot"
    assert not play_predict(100), "full trust in noisy senses should not"


def play_tiny_brain(dopamine, trace, seed=0):
    lvl, won = start(levels.TinyBrain)
    lvl.dopamine.set(dopamine)
    lvl.trace.set(trace)
    lvl.run()
    lvl.agent = sim.Forager(dopamine=dopamine, trace=trace, seed=seed)
    ticks(lvl, levels.TinyBrain.BUDGET)
    return won


def test_tiny_brain():
    assert play_tiny_brain(True, True), "dopamine and trace together should win"
    assert not play_tiny_brain(False, True), "no dopamine, no learning"


def test_every_level_covered():
    played = {"Spark", "Wire", "BrainMap", "Dopamine", "Remember", "Sleep", "Predict", "TinyBrain"}
    assert {cls.__name__ for cls in levels.LEVELS} == played


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
