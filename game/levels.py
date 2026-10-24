"""The eleven Brain Lab levels drawn on a tkinter canvas.

Each class here is the view of the level of the same name in level_engine.py, which holds the
rules, win conditions and scoring. A view builds the widgets, forwards input to the engine and
redraws from the engine's state.
"""
import tkinter as tk

import numpy as np

import level_engine as engine
import sim
from level_engine import TICK_MS

W, H = 660, 440

# Palette: a stained histology slide (glass, cresyl violet, eosin pink)
GLASS, LILAC, MUTED, VIOLET, PINK, INK = "#F7F2F6", "#E6DCEE", "#8A82A6", "#5B3A8C", "#D9637E", "#2A2550"
UI = ("Bahnschrift", 11)
UI_BOLD = ("Bahnschrift SemiBold", 12)
SMALL = ("Bahnschrift", 9)
PROSE = ("Cambria", 12)


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


class Level(engine.Level):
    def __init__(self, parent, done, seed=None):
        self.done = done
        self.canvas = tk.Canvas(parent, width=W, height=H, bg=GLASS, highlightthickness=1,
                                highlightbackground=LILAC)
        self.canvas.pack(side="left", padx=(24, 16), pady=8)
        self.side = tk.Frame(parent, bg=GLASS, width=270)
        self.side.pack(side="left", fill="y", pady=8)
        tk.Label(self.side, text=self.goal, font=UI_BOLD, fg=INK, bg=GLASS, wraplength=260,
                 justify="left", anchor="w").pack(fill="x", pady=(0, 12))
        self.status = tk.Label(self.side, font=UI, fg=INK, bg=GLASS, wraplength=260,
                               justify="left", anchor="nw")
        self.hint_label = tk.Label(self.side, font=SMALL, fg=VIOLET, bg=GLASS, wraplength=260,
                                   justify="left", anchor="w")
        super().__init__(seed)
        self.build()
        self.status.pack(fill="both", expand=True, pady=(12, 0))

    def build(self):
        pass

    def say(self, text):
        super().say(text)
        self.status.config(text=text)

    def show_hint(self):
        if self.hint and not self.hint_text:
            super().show_hint()
            self.hint_label.config(text=self.hint_text)
            self.hint_label.pack(fill="x", side="bottom", pady=(8, 0))

    def win(self, stars, text=""):
        if not self.over:
            super().win(stars, text)
            self.done(stars)

    def button(self, text, command):
        b = tk.Button(self.side, text=text, command=command, font=UI, fg=INK, bg=LILAC,
                      activebackground=VIOLET, activeforeground=GLASS, relief="flat",
                      padx=10, pady=6, anchor="w", takefocus=0, cursor="hand2")
        b.pack(fill="x", pady=3)
        return b

    def check(self, text, attr):
        """A checkbox that keeps the engine's boolean self.<attr> in step."""
        var = tk.BooleanVar(value=getattr(self, attr))
        tk.Checkbutton(self.side, text=text, variable=var, command=lambda: setattr(self, attr, var.get()),
                       font=UI, fg=INK, bg=GLASS, activebackground=GLASS, selectcolor=LILAC, anchor="w",
                       takefocus=0).pack(fill="x", pady=2)
        return var

    def slider(self, label, lo, hi, value, resolution=1, command=None, **kw):
        if label:
            tk.Label(self.side, text=label, font=UI, fg=INK, bg=GLASS, anchor="w").pack(fill="x")
        s = tk.Scale(self.side, from_=lo, to=hi, resolution=resolution, orient="horizontal", bg=GLASS,
                     troughcolor=LILAC, highlightthickness=0, activebackground=VIOLET, sliderrelief="flat",
                     length=240, command=command, **kw)
        s.set(value)
        s.pack(fill="x")
        return s


class Spark(Level, engine.Spark):
    def build(self):
        self.button("Inject current  (Space)", self.click)
        self.canvas.bind("<Button-1>", lambda e: self.click())
        c = self.canvas
        for v, label, dash in ((sim.V_TH, "threshold  -55 mV", (6, 4)), (sim.V_REST, "rest  -70 mV", (2, 4))):
            c.create_line(60, self.y(v), W - 20, self.y(v), fill=MUTED, dash=dash)
            c.create_text(W - 20, self.y(v) - 10, text=label, anchor="e", font=SMALL, fill=MUTED)
        for ms in range(0, self.WINDOW + 1, 100):
            c.create_text(self.x(ms), H - 22, text=f"{ms} ms", font=SMALL, fill=MUTED)
        c.create_text(W / 2, 24, text="Click anywhere on the slide to inject current", font=UI, fill=MUTED)
        self.line = c.create_line(0, 0, 0, 0, fill=VIOLET, width=2)

    def x(self, t):
        return 60 + t * (W - 110) / self.WINDOW

    def y(self, v):
        return H - 50 - (v + 80) * (H - 100) / 45

    def tick(self):
        drawn = len(self.spike_times)
        super().tick()
        for t in self.spike_times[drawn:]:
            self.canvas.create_line(self.x(t), self.y(sim.V_TH), self.x(t), self.y(-40), fill=PINK, width=4)
        if len(self.points) > 1:
            self.canvas.coords(self.line, *[c for t, v in self.points for c in (self.x(t), self.y(v))])


class Wire(Level, engine.Wire):
    ROWS = {0: ("Input A", 90), 1: ("Input B", 170), 2: ("Output", 250)}

    def build(self):
        self.button("Fire input A  (A)", lambda: self.fire(0))
        self.button("Fire input B  (B)", lambda: self.fire(1))
        self.button("Fire output  (Space)", lambda: self.fire(2))
        c = self.canvas
        for label, y in self.ROWS.values():
            c.create_text(20, y, text=label, anchor="w", font=UI, fill=INK)
            c.create_line(100, y, 470, y, fill=LILAC)
        c.create_text(285, 300, text=f"last {int(self.SPAN)} ms, newest on the right", font=SMALL, fill=MUTED)
        c.create_text(285, 330, text="Shaded band: the 20 ms before each output spike. Inputs inside it get stronger.",
                      font=SMALL, fill=MUTED)
        for i, x in enumerate((540, 610)):
            c.create_rectangle(x - 18, 60, x + 18, 360, outline=MUTED)
            c.create_text(x, 380, text="AB"[i], font=UI_BOLD, fill=INK)
        c.create_line(510, self.wy(0.8), 640, self.wy(0.8), fill=VIOLET, dash=(4, 3))
        c.create_line(510, self.wy(0.2), 640, self.wy(0.2), fill=PINK, dash=(4, 3))
        c.create_text(575, 40, text="synapse strength", font=SMALL, fill=MUTED)

    @staticmethod
    def wy(w):
        return 360 - w * 300

    def tick(self):
        super().tick()
        c = self.canvas
        c.delete("live")
        x = lambda t: 470 - (self.t - t) * 370 / self.SPAN
        for t, who in self.events:
            if self.t - t > self.SPAN:
                continue
            label, y = self.ROWS[who]
            if who == 2:
                c.create_rectangle(x(t - 20), 70, x(t), 190, fill=LILAC, outline="", tags="live")
            c.create_line(x(t), y - 18, x(t), y + 18, fill=PINK if who == 2 else VIOLET, width=3, tags="live")
        c.tag_lower("live")
        for i, xc in enumerate((540, 610)):
            c.create_rectangle(xc - 17, self.wy(self.syn.w[i]), xc + 17, 359,
                               fill=VIOLET, outline="", tags="live")


REGIONS = engine.REGIONS


class Lesion(Level, engine.Lesion):
    def build(self):
        self.boxes, self.labels, self.names = {}, {}, {}
        c = self.canvas
        c.create_oval(50, 50, 620, 350, outline=MUTED, width=2, fill=mix(GLASS, LILAC, 0.4))
        c.create_rectangle(350, 330, 410, 420, outline=MUTED, width=2, fill=mix(GLASS, LILAC, 0.4))
        c.create_text(70, 30, text="front", anchor="w", font=SMALL, fill=MUTED)
        c.create_text(600, 30, text="back", anchor="e", font=SMALL, fill=MUTED)
        for name, ((x, y), *_) in REGIONS.items():
            self.boxes[name] = c.create_rectangle(x - 80, y - 17, x + 80, y + 17, fill=GLASS, outline=VIOLET, width=2)
            self.labels[name] = c.create_text(x, y, text="?", font=SMALL, fill=INK, width=150)
            for item in (self.boxes[name], self.labels[name]):
                c.tag_bind(item, "<Button-1>", lambda e, n=name: self.lesion(n))
        self.job = c.create_text(16, 362, anchor="nw", font=UI, fill=INK, width=270)
        grid = tk.Frame(self.side, bg=GLASS)
        grid.pack(fill="x")
        for k, name in enumerate(self.rng.permutation(list(REGIONS))):
            self.names[name] = tk.Button(grid, text=name, command=lambda n=name: self.name(n), font=SMALL,
                                         fg=INK, bg=LILAC, activebackground=VIOLET, activeforeground=GLASS,
                                         relief="flat", takefocus=0, cursor="hand2", wraplength=125, pady=1)
            self.names[name].grid(row=k // 2, column=k % 2, sticky="nswe", padx=1, pady=1)
        grid.columnconfigure((0, 1), weight=1)
        self.draw()

    def lesion(self, name):
        super().lesion(name)
        self.draw()

    def name(self, guess):
        super().name(guess)
        self.draw()

    def draw(self):
        c = self.canvas
        for n, box in self.boxes.items():
            c.itemconfig(box, fill=PINK if n == self.cut else LILAC if n in self.named else GLASS)
            c.itemconfig(self.labels[n], text=n if n in self.named else "?")
            if n in self.named:
                self.names[n].config(state="disabled", bg=GLASS)
        text, broken = self.jobs()
        c.itemconfig(self.job, text=text, fill=PINK if broken else INK)


class Dopamine(Level, engine.Dopamine):
    ZERO, SCALE, X0, STEP = 160, 100, 70, 52

    def build(self):
        self.button("Ring bell, give juice", lambda: self.trial(True, True))
        self.button("Ring bell, no juice", lambda: self.trial(True, False))
        self.button("Juice, no bell", lambda: self.trial(False, True))
        self.draw()

    def trial(self, bell, juice):
        super().trial(bell, juice)
        self.draw()

    def draw(self):
        d, bell, juice = self.last
        c = self.canvas
        c.delete("all")
        c.create_line(40, self.ZERO, W - 30, self.ZERO, fill=MUTED)
        c.create_text(40, 30, text="dopamine (TD error) this trial", anchor="w", font=SMALL, fill=MUTED)
        for t, v in enumerate(d):
            x = self.X0 + t * self.STEP
            if abs(v) > 1e-3:
                c.create_rectangle(x - 14, self.ZERO, x + 14, self.ZERO - v * self.SCALE,
                                   fill=PINK if v > 0 else VIOLET, outline="")
        for t, label, on in ((sim.T_BELL, "bell", bell), (sim.T_JUICE, "juice", juice)):
            x = self.X0 + t * self.STEP
            c.create_text(x, self.ZERO + self.SCALE + 20, text=label, font=UI,
                          fill=INK if on else MUTED)
        top, bot = 340, 430
        c.create_text(40, top - 14, text="across trials:  at bell (violet), at juice time (pink)",
                      anchor="w", font=SMALL, fill=MUTED)
        c.create_line(40, (top + bot) / 2, W - 30, (top + bot) / 2, fill=LILAC)
        if len(self.history) > 1:
            n = max(len(self.history) - 1, 1)
            for i, color in ((0, VIOLET), (1, PINK)):
                pts = [c2 for k, h in enumerate(self.history)
                       for c2 in (40 + k * (W - 70) / max(n, 30), (top + bot) / 2 - h[i] * (bot - top) / 2)]
                c.create_line(*pts, fill=color, width=2)


class Remember(Level, engine.Remember):
    CELL, X0, Y0 = 40, 30, 40

    def build(self):
        c = self.canvas
        self.cells = [c.create_rectangle(self.X0 + (i % 8) * self.CELL, self.Y0 + (i // 8) * self.CELL,
                                         self.X0 + (i % 8 + 1) * self.CELL, self.Y0 + (i // 8 + 1) * self.CELL,
                                         outline=LILAC) for i in range(64)]
        c.create_text(self.X0, 20, text="drawing / recall", anchor="w", font=SMALL, fill=MUTED)
        c.bind("<Button-1>", lambda e: self.at_cell(e, self.press))
        c.bind("<B1-Motion>", lambda e: self.at_cell(e, self.drag))
        self.button("Store drawing", self.store)
        self.button("Store a random pattern", self.store_random)
        self.button("Recall from drawing", self.recall)
        self.button("Test all memories", self.test)
        self.button("Clear drawing", lambda: self.show(-np.ones(64)))
        self.show(self.state)

    def at_cell(self, e, action):
        col, row = (e.x - self.X0) // self.CELL, (e.y - self.Y0) // self.CELL
        if 0 <= col < 8 and 0 <= row < 8:
            action(row * 8 + col)

    def drag(self, i):
        super().drag(i)
        self.canvas.itemconfig(self.cells[i], fill=VIOLET if self.state[i] > 0 else GLASS)

    def show(self, s):
        super().show(s)
        for item, v in zip(self.cells, self.state):
            self.canvas.itemconfig(item, fill=VIOLET if v > 0 else GLASS)

    def store(self):
        super().store()
        self.draw_memories()

    def test(self):
        super().test()
        self.draw_memories()

    def tick(self):
        if self.canvas.winfo_exists():
            super().tick()

    def draw_memories(self):
        c = self.canvas
        c.delete("mem")
        c.create_text(390, 20, text="stored memories", anchor="w", font=SMALL, fill=MUTED, tags="mem")
        for k, p in enumerate(self.net.patterns[:24]):
            x0, y0 = 390 + (k % 5) * 52, 40 + (k // 5) * 52
            color = MUTED
            if k < len(self.results):
                color = VIOLET if self.results[k] > 0.95 else PINK
            c.create_rectangle(x0 - 3, y0 - 3, x0 + 43, y0 + 43, outline=color, width=2, tags="mem")
            for i in np.flatnonzero(p > 0):
                c.create_rectangle(x0 + (i % 8) * 5, y0 + (i // 8) * 5, x0 + (i % 8) * 5 + 5,
                                   y0 + (i // 8) * 5 + 5, fill=INK, outline="", tags="mem")


class Sleep(Level, engine.Sleep):
    def build(self):
        self.check("Sleep replay of task A", "replay")
        self.button("Learn task B for a day", self.day)
        self.draw()

    def day(self):
        super().day()
        self.draw()

    def draw(self):
        c = self.canvas
        c.delete("all")
        x = lambda d: 60 + d * (W - 100) / self.DAYS
        y = lambda acc: 380 - acc * 320
        for acc in (0, 0.5, 1):
            c.create_text(50, y(acc), text=f"{acc:.0%}", anchor="e", font=SMALL, fill=MUTED)
        c.create_line(x(0), y(0.8), x(self.DAYS), y(0.8), fill=VIOLET, dash=(4, 3))
        c.create_line(x(0), y(0.9), x(self.DAYS), y(0.9), fill=PINK, dash=(4, 3))
        for d in range(self.DAYS + 1):
            c.create_text(x(d), 400, text=str(d), font=SMALL, fill=MUTED)
        c.create_text(x(self.DAYS / 2), 425, text="day", font=SMALL, fill=MUTED)
        for i, color, name in ((0, VIOLET, "task A"), (1, PINK, "task B")):
            pts = [v for d, h in enumerate(self.hist) for v in (x(d), y(h[i]))]
            if len(pts) > 2:
                c.create_line(*pts, fill=color, width=3)
            for d, h in enumerate(self.hist):
                c.create_oval(x(d) - 4, y(h[i]) - 4, x(d) + 4, y(h[i]) + 4, fill=color, outline="")
            c.create_text(x(0) + 10 + i * 90, 30, text=name, anchor="w", font=UI, fill=color)


class Predict(Level, engine.Predict):
    TRACK_Y = 140

    def build(self):
        self.slider("Trust in your senses", 1, 100, 3, command=self.set_gain, showvalue=False)
        c = self.canvas
        lo, hi = sim.DotWorld.OCCLUDER
        c.create_line(self.x(0), self.TRACK_Y, self.x(1), self.TRACK_Y, fill=LILAC, width=2)
        self.obs_dot = c.create_oval(0, 0, 0, 0, fill=PINK, outline="")
        self.belief = c.create_oval(0, 0, 0, 0, outline=VIOLET, width=3)
        c.create_rectangle(self.x(lo), self.TRACK_Y - 50, self.x(hi), self.TRACK_Y + 50,
                           fill=MUTED, outline="")
        c.tag_raise(self.belief)
        c.create_text(40, 240, text="error over the last 12 s", anchor="w", font=SMALL, fill=MUTED)
        c.create_line(40, self.ey(0.05), W - 30, self.ey(0.05), fill=PINK, dash=(4, 3))
        c.create_text(W - 30, self.ey(0.05) - 8, text="0.05", anchor="e", font=SMALL, fill=PINK)
        self.err_line = c.create_line(0, 0, 0, 0, fill=VIOLET, width=2)

    @staticmethod
    def x(pos):
        return 40 + pos * (W - 70)

    @staticmethod
    def ey(err):
        return 420 - min(err, 0.15) * 1050

    def tick(self):
        if self.over:
            return
        super().tick()
        c = self.canvas
        y = self.TRACK_Y
        if self.obs is None:
            c.coords(self.obs_dot, 0, 0, 0, 0)
        else:
            c.coords(self.obs_dot, self.x(self.obs) - 5, y - 5, self.x(self.obs) + 5, y + 5)
        c.coords(self.belief, self.x(self.pos) - 14, y - 14, self.x(self.pos) + 14, y + 14)
        if len(self.errs) > 1:
            k = 30   # smooth the plotted error over 0.6 s
            sm = np.convolve(self.errs, np.ones(k) / k, mode="valid") if len(self.errs) > k else self.errs[-1:] * 2
            step = (W - 70) / self.WINDOW
            c.coords(self.err_line, *[v for i, e in enumerate(sm) for v in (40 + i * step, self.ey(e))])


class TinyBrain(Level, engine.TinyBrain):
    CELL, X0, Y0 = 64, 40, 30

    def build(self):
        self.check("Dopamine (learning signal)", "dopamine")
        self.check("Eligibility trace (memory of recent moves)", "trace")
        self.button("Run", self.run)
        self.draw()

    def tick(self):
        f = self.agent
        if self.over or f is None:
            return
        super().tick()
        self.draw(f)   # the run just ended still shows its last frame

    def draw(self, f=None):
        c = self.canvas
        c.delete("all")
        f, n = f or self.agent, 5
        vmax = max(f.V.max(), 1e-6) if f else 1
        for i in range(n * n):
            gx, gy = i % n, i // n
            fill = mix(GLASS, VIOLET, 0.75 * f.V[i] / vmax) if f else GLASS
            c.create_rectangle(self.X0 + gx * self.CELL, self.Y0 + gy * self.CELL,
                               self.X0 + (gx + 1) * self.CELL, self.Y0 + (gy + 1) * self.CELL,
                               fill=fill, outline=LILAC)
        fx, fy = self.X0 + 4.5 * self.CELL, self.Y0 + 4.5 * self.CELL
        c.create_rectangle(fx - 12, fy - 12, fx + 12, fy + 12, fill=INK, outline="")
        if f:
            ax, ay = self.X0 + (f.pos[0] + 0.5) * self.CELL, self.Y0 + (f.pos[1] + 0.5) * self.CELL
            c.create_oval(ax - 16, ay - 16, ax + 16, ay + 16, fill=PINK, outline="")
        c.create_text(380, 40, text="Shading: how much food each square predicts (learned value).",
                      anchor="w", font=SMALL, fill=MUTED, width=250)
        c.create_text(40, 365, text="dopamine, last 150 steps", anchor="w", font=SMALL, fill=MUTED)
        base = 405
        c.create_line(40, base, W - 30, base, fill=LILAC)
        for k, d in enumerate(self.deltas[-150:]):
            if abs(d) > 0.01:
                x = 40 + k * 4
                c.create_line(x, base, x, base - max(min(d, 1), -1) * 25, fill=PINK if d > 0 else VIOLET, width=3)


class Pattern(Level, engine.Pattern):
    CX, CY, DOT, ARROW = 230, 220, 40, 120   # px per input unit, px per weight unit

    def build(self):
        self.check("Oja's forgetting term (−y²w)", "decay")
        self.slider("Learning rate", 1, 50, round(self.rate * 1000), font=SMALL, fg=MUTED,
                    command=lambda v: setattr(self, "rate", float(v) / 1000))
        self.feed = self.button("Feed inputs  (Space)", self.toggle)
        self.button("Reset weights", self.reset)
        c = self.canvas
        c.create_oval(self.CX - self.ARROW, self.CY - self.ARROW, self.CX + self.ARROW, self.CY + self.ARROW,
                      outline=MUTED, dash=(2, 4))
        c.create_text(self.CX + self.ARROW * 0.72, self.CY - self.ARROW * 0.72 - 12, text="|w| = 1",
                      font=SMALL, fill=MUTED)
        c.create_text(20, 20, text="dots: inputs the neuron sees     arrow: its two synaptic weights",
                      anchor="w", font=SMALL, fill=MUTED)
        self.arrow = c.create_line(0, 0, 0, 0, fill=VIOLET, width=4, arrow="last", arrowshape=(14, 16, 6))
        self.draw()

    def toggle(self):
        super().toggle()
        self.feed.config(text="Pause  (Space)" if self.running else "Feed inputs  (Space)")

    def tick(self):
        if self.over or not self.running:
            return
        super().tick()
        self.draw()

    def draw(self):
        c = self.canvas
        c.delete("dots")
        for x, y in self.recent:
            px, py = self.CX + x * self.DOT, self.CY - y * self.DOT
            if 0 < px < W and 0 < py < H:
                c.create_oval(px - 2, py - 2, px + 2, py + 2, fill=PINK, outline="", tags="dots")
        c.tag_lower("dots")
        wx, wy = self.w * self.ARROW
        c.coords(self.arrow, self.CX, self.CY, self.CX + wx, self.CY - wy)


class Zoo(Level, engine.Zoo):
    TOP, BOTTOM, LEFT = 130, 330, 40   # y of the two traces' resting lines, x of their start

    def build(self):
        self.sliders = {name: self.slider(name, lo, hi, val, res, font=SMALL, fg=MUTED)
                        for name, lo, hi, res, val in self.PARAMS}
        self.button("Run 300 ms  (Space)", self.run)

    def set(self, current, a, c, d):
        super().set(current, a, c, d)
        for name, v in self.params.items():
            self.sliders[name].set(v)

    def run(self):
        self.params = {name: s.get() for name, s in self.sliders.items()}
        super().run()
        if self.last:
            self.draw(*self.last)

    def draw(self, lif, lif_kind, izh, izh_kind):
        c = self.canvas
        c.delete("all")
        for y0, (spikes, v), label in ((self.TOP, lif, "leaky integrate-and-fire"), (self.BOTTOM, izh, "Izhikevich")):
            kind = lif_kind if y0 == self.TOP else izh_kind
            c.create_text(self.LEFT, y0 - 100, text=f"{label}:  {kind}", anchor="w", font=UI, fill=INK)
            pts = [p for i in range(len(v))
                   for p in (self.LEFT + i * (W - self.LEFT - 20) / len(v), y0 - (v[i] + 70) * 0.8)]
            c.create_line(*pts, fill=VIOLET, width=2)
            for t in spikes:
                x = self.LEFT + t / sim.ZOO_T * (W - self.LEFT - 20)
                c.create_line(x, y0 + 22, x, y0 + 34, fill=PINK, width=2)
        for ms in range(0, int(sim.ZOO_T) + 1, 100):
            c.create_text(self.LEFT + ms / sim.ZOO_T * (W - self.LEFT - 20), H - 14, text=f"{ms} ms",
                          font=SMALL, fill=MUTED)


class Home(Level, engine.Home):
    AX, AY, SIDE = 30, 20, 400

    def build(self):
        self.check("Landmark correction (place cells)", "landmarks")
        self.button("Head home  (H)", self.go_home)
        c = self.canvas
        n = 40   # one grid cell's firing map, drawn as the arena's background
        cell = self.SIDE / n
        for i in range(n):
            for j in range(n):
                rate = sim.grid_rate(((i + 0.5) / n, 1 - (j + 0.5) / n))
                c.create_rectangle(self.AX + i * cell, self.AY + j * cell, self.AX + (i + 1) * cell,
                                   self.AY + (j + 1) * cell, fill=mix(GLASS, LILAC, rate), outline="")
        c.create_rectangle(self.AX, self.AY, self.AX + self.SIDE, self.AY + self.SIDE, outline=MUTED, width=2)
        r = sim.PLACE_R * self.SIDE
        for lx, ly in sim.LANDMARKS:
            x, y = self.px(lx, ly)
            c.create_oval(x - r, y - r, x + r, y + r, outline=VIOLET, dash=(4, 3))
            c.create_rectangle(x - 5, y - 5, x + 5, y + 5, fill=INK, outline="")
        x, y = self.px(*sim.NEST)
        r = self.HOME_R * self.SIDE
        c.create_oval(x - r, y - r, x + r, y + r, fill=mix(GLASS, PINK, 0.25), outline=PINK)
        c.create_text(x, y, text="nest", font=SMALL, fill=INK)
        for k, line in enumerate(("pink dot: where it is", "ring: where it thinks it is",
                                  "squares: landmark posts", "dashed circles: their place fields",
                                  "shading: one grid cell's firing fields")):
            c.create_text(450, 40 + k * 22, text=line, anchor="w", font=SMALL, fill=MUTED)
        self.path = c.create_line(0, 0, 0, 0, fill=PINK, width=2)
        self.ring = c.create_oval(0, 0, 0, 0, outline=VIOLET, width=3)
        self.dot = c.create_oval(0, 0, 0, 0, fill=PINK, outline="")
        self.food_drawn = False
        self.draw()

    def px(self, x, y):
        return self.AX + x * self.SIDE, self.AY + (1 - y) * self.SIDE

    def move(self, dx, dy):
        super().move(dx, dy)
        if self.found and not self.food_drawn:
            self.food_drawn = True
            x, y = self.px(*self.food)
            self.canvas.create_oval(x - 9, y - 9, x + 9, y + 9, fill=INK, outline="")
        self.draw()

    def go_home(self):
        taken = self.run_home is not None
        super().go_home()
        if self.run_home is not None and not taken:
            start, end = self.run_home
            self.canvas.create_line(*self.px(*start), *self.px(*end), fill=VIOLET, width=3,
                                    dash=(8, 4), arrow="last")
            self.draw()

    def draw(self):
        c = self.canvas
        c.coords(self.path, *[v for p in self.trail for v in self.px(*p)] * (1 if len(self.trail) > 1 else 2))
        x, y = self.px(*self.nav.true)
        c.coords(self.dot, x - 6, y - 6, x + 6, y + 6)
        x, y = self.px(*self.nav.est)
        c.coords(self.ring, x - 12, y - 12, x + 12, y + 12)
        c.tag_raise(self.ring)


LEVELS = [Spark, Wire, Lesion, Dopamine, Remember, Sleep, Predict, TinyBrain, Pattern, Zoo, Home]
