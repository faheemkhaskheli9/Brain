"""Smoke test of the Tk views in levels.py. Run: python game/test_levels_ui.py

Needs a display for tkinter (the root window is withdrawn). On a headless Linux box use
xvfb-run python game/test_levels_ui.py. The rules are tested without a display in test_levels.py.
"""
import tkinter as tk

import levels
import sim

ROOT = tk.Tk()
ROOT.withdraw()


def start(cls, seed=0):
    won = []
    return cls(tk.Frame(ROOT), won.append, seed), won


def test_every_view_builds_ticks_and_takes_keys():
    for cls in levels.LEVELS:
        lvl, won = start(cls)
        for k in ("space", "a", "b", "Left", "Up", "h"):
            lvl.key(k)
        for _ in range(5):
            lvl.tick()
        ROOT.update()
        assert lvl.status["text"] == lvl.message, cls.__name__


def test_controls_drive_the_engine():
    lvl, _ = start(levels.Sleep)
    lvl.side.winfo_children()[-2].invoke()       # the replay checkbox
    assert lvl.replay is True
    lvl, _ = start(levels.Zoo)
    lvl.set(20, 0.12, -65, 0)
    lvl.run()
    assert lvl.params["current"] == 20 and "fast spiking" in lvl.found


def test_win_reaches_the_shell():
    lvl, won = start(levels.Lesion)
    for name in levels.REGIONS:
        lvl.lesion(name)
        assert levels.REGIONS[name][1] in lvl.canvas.itemcget(lvl.job, "text")
        lvl.name(name)
    assert won == [3] and all(str(b["state"]) == "disabled" for b in lvl.names.values())


def test_hint_shown_on_failure():
    lvl, won = start(levels.Lesion)
    lvl.lesion("Hippocampus")
    for _ in range(4):
        lvl.name("Amygdala")
    assert not won and lvl.hint_label["text"] == "Hint: " + levels.Lesion.hint


def test_home_draws_the_run():
    lvl, won = start(levels.Home)
    lvl.food = sim.np.array([0.9, 0.55])
    while lvl.nav.true[0] < 0.9:
        lvl.key("Right")
    while lvl.nav.true[1] < 0.55:
        lvl.key("Up")
    assert lvl.found and lvl.food_drawn
    lvl.key("h")
    assert lvl.over and lvl.run_home is not None


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
