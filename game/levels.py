"""The ten Brain Lab levels. Each one drives a model from sim.py on a tkinter canvas."""
import tkinter as tk

import numpy as np

import sim

TICK_MS = 20
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


class Level:
    title = goal = intro = debrief = kb = hint = ""
    tag, tag_note = "ESTABLISHED", ""
    timed = False   # runs on its own clock, so the shell offers pause and step

    @staticmethod
    def sweep():
        """Optional debrief chart: (title, x label, y label, xs, ys) from the level's model."""
        return None

    def __init__(self, parent, done):
        self.done, self.over = done, False
        self.canvas = tk.Canvas(parent, width=W, height=H, bg=GLASS, highlightthickness=1,
                                highlightbackground=LILAC)
        self.canvas.pack(side="left", padx=(24, 16), pady=8)
        self.side = tk.Frame(parent, bg=GLASS, width=270)
        self.side.pack(side="left", fill="y", pady=8)
        tk.Label(self.side, text=self.goal, font=UI_BOLD, fg=INK, bg=GLASS, wraplength=260,
                 justify="left", anchor="w").pack(fill="x", pady=(0, 12))
        self.status = tk.Label(self.side, font=UI, fg=INK, bg=GLASS, wraplength=260,
                               justify="left", anchor="nw")
        self.build()
        self.status.pack(fill="both", expand=True, pady=(12, 0))
        self.hint_label = tk.Label(self.side, font=SMALL, fg=VIOLET, bg=GLASS, wraplength=260,
                                   justify="left", anchor="w")

    def show_hint(self):
        if self.hint and not self.hint_label["text"]:
            self.hint_label.config(text="Hint: " + self.hint)
            self.hint_label.pack(fill="x", side="bottom", pady=(8, 0))

    def build(self):
        pass

    def tick(self):
        pass

    def key(self, keysym):
        pass

    def button(self, text, command):
        b = tk.Button(self.side, text=text, command=command, font=UI, fg=INK, bg=LILAC,
                      activebackground=VIOLET, activeforeground=GLASS, relief="flat",
                      padx=10, pady=6, anchor="w", takefocus=0, cursor="hand2")
        b.pack(fill="x", pady=3)
        return b

    def check(self, text, value=False):
        var = tk.BooleanVar(value=value)
        tk.Checkbutton(self.side, text=text, variable=var, font=UI, fg=INK, bg=GLASS,
                       activebackground=GLASS, selectcolor=LILAC, anchor="w",
                       takefocus=0).pack(fill="x", pady=2)
        return var

    def say(self, text):
        self.status.config(text=text)

    def win(self, stars, text=""):
        if not self.over:
            self.over = True
            self.say(text or "Done.")
            self.done(stars)

    def fail(self, text):
        self.over = True
        self.say(text + "\n\nPress Retry to try again.")
        self.show_hint()


class Spark(Level):
    title = "Spark"
    goal = "Fire exactly 5 spikes before the 500 ms window ends."
    intro = ("A neuron adds up the charge that flows onto its membrane. When the voltage reaches "
             "threshold it fires a spike, drops below its resting level and is silent for a moment. "
             "Charge also leaks away, so input that arrives slowly never adds up.\n\n"
             "Each click (or Space) sends a 10 ms pulse of current into this model neuron. "
             "Time runs 20 times slower than real so you can watch it.")
    debrief = ("You used temporal summation: pulses that arrive close together add up before the "
               "leak drains them away. Too many in a row and the neuron keeps firing. This is the "
               "leaky integrate-and-fire model, the workhorse of spiking simulations. Real neurons "
               "add ion-channel detail (Hodgkin-Huxley), but threshold, leak and reset are the core.")
    kb = "simulation/spiking-neural-networks.md"
    hint = "One click stays below threshold. Two quick clicks fire one spike, so send 5 pairs spread out."
    timed = True
    WINDOW = 500  # ms of model time

    def build(self):
        self.neuron, self.t, self.pulses, self.clicks, self.spikes = sim.LIF(), 0, [], 0, 0
        self.points = [(0, sim.V_REST)]
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
        self.say("Waiting for your first click.")

    def x(self, t):
        return 60 + t * (W - 110) / self.WINDOW

    def y(self, v):
        return H - 50 - (v + 80) * (H - 100) / 45

    def click(self):
        if not self.over:
            self.pulses.append(10)
            self.clicks += 1

    def key(self, keysym):
        if keysym == "space":
            self.click()

    def tick(self):
        if self.over or not self.clicks:
            return
        current = 2.0 * len(self.pulses)
        self.pulses = [p - 1 for p in self.pulses if p > 1]
        self.t += 1
        if self.neuron.step(current, 1.0):
            self.spikes += 1
            self.points.append((self.t, -40))
            self.canvas.create_line(self.x(self.t), self.y(sim.V_TH), self.x(self.t), self.y(-40),
                                    fill=PINK, width=4)
        self.points.append((self.t, self.neuron.v))
        self.canvas.coords(self.line, *[c for t, v in self.points for c in (self.x(t), self.y(v))])
        self.say(f"Spikes  {self.spikes} of 5\nClicks  {self.clicks}\nTime  {self.t} ms")
        if self.spikes > 5:
            self.fail(f"{self.spikes} spikes. While the current stays high the neuron keeps firing, "
                      "so stop clicking once you are close.")
        elif self.t >= self.WINDOW:
            if self.spikes == 5:
                self.win(3 if self.clicks <= 10 else 2 if self.clicks <= 15 else 1,
                         f"5 spikes from {self.clicks} clicks.")
            else:
                self.fail(f"{self.spikes} spikes. Click in quick bursts: pulses close together "
                          "add up before the charge leaks away.")


class Wire(Level):
    title = "Wire together"
    goal = "Make synapse A stronger than 0.8 and synapse B weaker than 0.2."
    intro = ("Synapses change strength with use. In spike-timing-dependent plasticity (STDP), "
             "timing decides the direction. An input that fires just before the output neuron "
             "gets stronger; one that fires just after gets weaker. The window is about 20 ms.\n\n"
             "You are the experimenter. Press A or B to fire an input and Space to make the "
             "output neuron fire. Time runs 10 times slower than real.")
    debrief = ("Pre before post strengthens, because the input may have caused the spike. Post "
               "before pre weakens. Both inputs share one output neuron, so a badly timed output "
               "spike changes both synapses at once. STDP lets neurons learn causal order and pick "
               "up repeating patterns without a teacher (Markram et al. 1997; Bi and Poo 1998).")
    kb = "function/learning-and-plasticity.md"
    hint = "Repeat A, then Space, then B, all quickly, and wait a second between rounds so the traces fade."
    timed = True
    DT, SPAN = 2.0, 400.0  # model ms per tick, ms shown on the raster
    ROWS = {0: ("Input A", 90), 1: ("Input B", 170), 2: ("Output", 250)}

    def build(self):
        self.syn, self.t, self.events, self.presses = sim.STDP(2), 0.0, [], 0
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
        self.say("A 0.50   B 0.50\n\nFire an input, then the output a moment later.")

    @staticmethod
    def wy(w):
        return 360 - w * 300

    def key(self, keysym):
        k = {"a": 0, "b": 1, "space": 2}.get(keysym.lower())
        if k is not None:
            self.fire(k)

    def fire(self, who):
        if self.over:
            return
        before = self.syn.w.copy()
        self.syn.post() if who == 2 else self.syn.pre(who)
        self.events.append((self.t, who))
        self.presses += 1
        dw = self.syn.w - before
        changes = ", ".join(f"{n} {d:+.2f}" for n, d in zip("AB", dw) if abs(d) >= 0.005)
        a, b = self.syn.w
        msg = f"A {a:.2f}   B {b:.2f}\n\nLast spike: {changes or 'no change (nothing within ~20 ms)'}\nPresses {self.presses}"
        self.say(msg)
        if a > 0.8 and b < 0.2:
            self.win(3 if self.presses <= 14 else 2 if self.presses <= 24 else 1, msg)

    def tick(self):
        self.t += self.DT
        self.syn.decay(self.DT)
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


# Main jobs from anatomy/brain-structure-overview.md; lesion effects and their sources are in
# its "What lesions show" section. Each entry: position, job, role, deficit, evidence.
REGIONS = {
    "Prefrontal cortex": ((150, 140), "Hold a phone number in mind while you dial it",
                          "working memory, goals and cognitive control",
                          "It repeats a number back at once, but loses it after a few seconds' delay.",
                          "Funahashi, Bruce & Goldman-Rakic 1993 (monkeys)"),
    "Neocortex": ((380, 100), "Recognise a friend's face in a crowd",
                  "perception, language, reasoning and planning",
                  "It sees eyes, nose and mouth but cannot tell whose face it is. It knows friends by voice.",
                  "acquired prosopagnosia, Barton 2008"),
    "Basal ganglia": ((220, 200), "Pick the action that paid off before, until it becomes a habit",
                      "action selection and habits, learned from dopamine",
                      "It remembers every practice session, yet the habit never forms.",
                      "Parkinson's patients, Knowlton, Mangels & Squire 1996"),
    "Thalamus": ((400, 190), "Gate which sensory signals reach the cortex",
                 "relay and gating of signals into the cortex",
                 "Its eyes and skin still work, but touch from one side of the body no longer gets through.",
                 "thalamic strokes, Schmahmann 2003"),
    "Amygdala": ((240, 280), "Fear a dog that bit you once",
                 "emotional salience and fear learning",
                 "It walks straight up to the dog that bit it. It can tell you about the bite but shows no fear.",
                 "Bechara et al. 1995; patient S.M., Feinstein et al. 2011"),
    "Hippocampus": ((420, 260), "Remember where you parked this morning",
                    "fast episodic memory and spatial maps",
                    "It forgets where it parked within minutes. Childhood memories and old skills are intact.",
                    "patient H.M., Scoville & Milner 1957"),
    "Cerebellum": ((540, 320), "Time a hand movement to catch a ball",
                   "fine motor timing and error correction",
                   "It reaches too late and overshoots. Every movement is clumsy and badly timed.",
                   "cerebellar ataxia, Holmes 1917"),
    "Brainstem and hypothalamus": ((380, 380), "Keep you breathing and send dopamine to the whole brain",
                                   "vital functions, drives and the neuromodulators",
                                   "It stops breathing on its own, and the dopamine signal to the brain goes silent.",
                                   "textbook (Kandel et al. 2021)"),
}


class Lesion(Level):
    title = "Lesion lab"
    tag_note = ("The deficits come from classic patient and animal studies. Real lesions are rarely this "
                "clean, and every behaviour uses many regions at once.")
    goal = "Lesion each hidden region and name it from what breaks. At most 3 wrong names."
    intro = ("Much of what we know about brain regions comes from damage. When a stroke, an injury or "
             "surgery takes out one part, the behaviour that breaks shows what that part was doing.\n\n"
             "This brain does 8 jobs. Its regions are hidden. Click a region to lesion it and watch which "
             "job fails, then name the region. Clicking another region heals the first one.")
    debrief = ("Each lesion took out one kind of learner. Losing the hippocampus stops new episodes but "
               "spares old memories, because those have moved to the cortex. Losing the basal ganglia "
               "stops habits forming while the memory of practising survives: two memory systems, broken "
               "separately. A brain-like AI would need several kinds of learner, not one big network.")
    kb = "anatomy/brain-structure-overview.md"
    hint = "Match the broken job to a role: memory of places is the hippocampus, fear is the amygdala, timing is the cerebellum."

    def build(self):
        self.cut, self.named, self.mistakes = None, set(), 0
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
        for k, name in enumerate(np.random.default_rng().permutation(list(REGIONS))):
            self.names[name] = tk.Button(grid, text=name, command=lambda n=name: self.name(n), font=SMALL,
                                         fg=INK, bg=LILAC, activebackground=VIOLET, activeforeground=GLASS,
                                         relief="flat", takefocus=0, cursor="hand2", wraplength=125, pady=1)
            self.names[name].grid(row=k // 2, column=k % 2, sticky="nswe", padx=1, pady=1)
        grid.columnconfigure((0, 1), weight=1)
        self.show_jobs()
        self.say("Click a hidden region on the slide to lesion it.")

    def show_jobs(self):
        if self.cut is None:
            self.canvas.itemconfig(self.job, text="All 8 jobs work.", fill=INK)
        else:
            self.canvas.itemconfig(self.job, text=f"7 of 8 jobs work. Broken:\n✗ {REGIONS[self.cut][1]}", fill=PINK)

    def lesion(self, name):
        if self.over:
            return
        self.cut = name
        for n, box in self.boxes.items():
            self.canvas.itemconfig(box, fill=PINK if n == name else LILAC if n in self.named else GLASS)
        self.show_jobs()
        self.say(f"Lesioned.\n\n{REGIONS[name][3]}" + ("" if name in self.named else "\n\nWhich region is it?"))

    def name(self, guess):
        if self.over:
            return
        if self.cut is None or self.cut in self.named:
            return self.say("Lesion a region you have not named yet, then pick its name.")
        cut = self.cut
        if guess != cut:
            self.mistakes += 1
            msg = f"Not quite. {guess} does {REGIONS[guess][2]}.\nWrong names {self.mistakes} of 3"
            return self.fail(msg) if self.mistakes > 3 else self.say(msg)
        self.named.add(cut)
        self.canvas.itemconfig(self.labels[cut], text=cut)
        self.canvas.itemconfig(self.boxes[cut], fill=LILAC)
        self.names[cut].config(state="disabled", bg=GLASS)
        self.cut = None
        self.show_jobs()
        msg = f"Yes. {cut}: {REGIONS[cut][2]}.\nEvidence: {REGIONS[cut][4]}."
        if len(self.named) == len(REGIONS):
            return self.win(3 if self.mistakes == 0 else 2 if self.mistakes == 1 else 1, msg)
        self.say(msg)


class Dopamine(Level):
    title = "Be the dopamine"
    goal = "Make the dopamine burst move from the juice to the bell. Then withhold the juice and cause a dip."
    intro = ("Dopamine neurons do not signal reward itself. They signal reward prediction error: "
             "a burst when things are better than expected, nothing when they are as expected, "
             "a dip when they are worse.\n\nA temporal-difference (TD) learner computes the same "
             "signal, δ = r + γV(s′) − V(s). Each button runs one trial. "
             "The bars show the learner's dopamine at each moment.")
    debrief = ("Once the bell predicts the juice, the surprise, and the burst, moves to the bell. "
               "Missing juice is worse than predicted, so dopamine dips at the moment the juice was "
               "due. Juice with no bell is still a surprise. Real dopamine neurons do all three "
               "(Schultz, Dayan and Montague 1997), one of the strongest links between neuroscience and AI.")
    kb = "function/learning-and-plasticity.md"
    hint = "Run bell-and-juice trials until the bell bar is tall and the juice bar is gone, then ring with no juice."
    ZERO, SCALE, X0, STEP = 160, 100, 70, 52

    def build(self):
        self.V, self.trials, self.learned, self.surprise, self.history = sim.td_values(), 0, False, False, []
        self.button("Ring bell, give juice", lambda: self.trial(True, True))
        self.button("Ring bell, no juice", lambda: self.trial(True, False))
        self.button("Juice, no bell", lambda: self.trial(False, True))
        self.say("Run a trial to see the dopamine response.")
        self.draw(np.zeros(sim.T_JUICE + 3), None, None)

    def trial(self, bell, juice):
        if self.over:
            return
        self.trials += 1
        d = sim.td_trial(self.V, bell, juice)
        self.history.append((d[sim.T_BELL], d[sim.T_JUICE]))
        self.draw(d, bell, juice)
        db, dj = d[sim.T_BELL], d[sim.T_JUICE]
        msg = f"Trial {self.trials}\nDopamine at bell  {db:+.2f}\nDopamine at juice time  {dj:+.2f}"
        if bell and juice and db >= 0.8 and dj <= 0.2 and not self.learned:
            self.learned = True
            msg += "\n\nThe burst has moved to the bell. Now try a trial without juice."
        elif self.learned and not bell and juice:
            self.surprise = True
        if self.learned and bell and not juice and dj <= -0.5:
            stars = 1 + self.surprise + (self.trials <= 25)
            return self.win(stars, msg + "\n\nA dip: the predicted juice never came.")
        self.say(msg)

    def draw(self, d, bell, juice):
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


class Remember(Level):
    title = "Remember me"
    goal = "Store at least 3 memories and pass a recall test. Then keep storing until recall breaks."
    intro = ("The hippocampus can store a memory in one go and recall the whole thing from a "
             "fragment. A Hopfield network does the same. Storing a pattern strengthens the "
             "connections between neurons that are active together; recall lets the network settle "
             "into the nearest stored pattern.\n\nHere 64 neurons form an 8 × 8 grid. "
             "Click and drag to draw.")
    debrief = ("Recall settles into an attractor: the stored pattern closest to the cue. Capacity is "
               "limited. Random patterns start to interfere at about 0.14 × N, about 9 for 64 "
               "neurons, and similar patterns, like hand drawings, interfere sooner. Modern Hopfield "
               "networks raise capacity sharply and are mathematically close to attention.")
    kb = "function/memory-systems.md"
    hint = "Similar drawings blur together. Store random patterns, press Test after each one, and keep going."
    CELL, X0, Y0 = 40, 30, 40

    @staticmethod
    def sweep():
        rng, xs, ys = np.random.default_rng(0), list(range(1, 21)), []
        for n in xs:
            net = sim.Hopfield(64)
            for _ in range(n):
                net.store(rng.choice([-1.0, 1.0], 64))
            ys.append(float(np.mean(net.test())))
        return "Recall vs memories stored (random patterns)", "memories stored", "mean recall overlap", xs, ys

    def build(self):
        self.net, self.state = sim.Hopfield(64), -np.ones(64)
        self.passed = self.completed = False
        self.recall_steps, self.paint, self.results = 0, 1.0, []
        self.rng = np.random.default_rng()
        c = self.canvas
        self.cells = [c.create_rectangle(self.X0 + (i % 8) * self.CELL, self.Y0 + (i // 8) * self.CELL,
                                         self.X0 + (i % 8 + 1) * self.CELL, self.Y0 + (i // 8 + 1) * self.CELL,
                                         outline=LILAC) for i in range(64)]
        c.create_text(self.X0, 20, text="drawing / recall", anchor="w", font=SMALL, fill=MUTED)
        c.bind("<Button-1>", self.press)
        c.bind("<B1-Motion>", self.drag)
        self.button("Store drawing", self.store)
        self.button("Store a random pattern", self.store_random)
        self.button("Recall from drawing", self.recall)
        self.button("Test all memories", self.test)
        self.button("Clear drawing", lambda: self.show(-np.ones(64)))
        self.show(self.state)
        self.say("Draw a shape, then store it.")

    def cell_at(self, e):
        col, row = (e.x - self.X0) // self.CELL, (e.y - self.Y0) // self.CELL
        return row * 8 + col if 0 <= col < 8 and 0 <= row < 8 else None

    def press(self, e):
        i = self.cell_at(e)
        if i is not None and not self.recall_steps:
            self.paint = -self.state[i]
            self.drag(e)

    def drag(self, e):
        i = self.cell_at(e)
        if i is not None and not self.recall_steps:
            self.state[i] = self.paint
            self.canvas.itemconfig(self.cells[i], fill=VIOLET if self.paint > 0 else GLASS)

    def show(self, s):
        self.state = np.array(s, float)
        for item, v in zip(self.cells, self.state):
            self.canvas.itemconfig(item, fill=VIOLET if v > 0 else GLASS)

    def store(self):
        if (self.state < 0).all():
            return self.say("The drawing is empty. Draw something first.")
        self.net.store(self.state)
        self.results = []
        self.draw_memories()
        self.say(f"{len(self.net.patterns)} memories stored.")

    def store_random(self):
        self.show(self.rng.choice([-1.0, 1.0], 64))
        self.store()

    def recall(self):
        if not self.net.patterns:
            return self.say("Store a memory first, then draw part of it and recall.")
        self.recall_steps = 10
        self.say("Recalling...")

    def tick(self):
        if self.recall_steps and self.canvas.winfo_exists():
            self.recall_steps -= 1
            new = self.net.update(self.state)
            stable = (new == self.state).all()
            self.show(new)
            if stable or not self.recall_steps:
                self.recall_steps = 0
                best = max(float(p @ new) / 64 for p in self.net.patterns)
                self.completed = True
                self.say(f"Settled. Best match with a stored memory: {best:.0%}.")

    def test(self):
        if self.over:
            return
        n = len(self.net.patterns)
        if n < 3:
            return self.say(f"{n} stored. Store at least 3 memories first.")
        self.results = self.net.test()
        self.draw_memories()
        good = sum(r > 0.95 for r in self.results)
        msg = f"Each memory was corrupted by 10% and recalled.\n{good} of {n} came back intact."
        if good == n:
            self.passed = True
            msg += "\n\nAll recalled. Keep storing memories until recall breaks."
        elif self.passed:
            stars = 1 + self.completed + (n >= 9)
            return self.win(stars, msg + f"\n\nRecall broke at {n} memories.")
        self.say(msg)

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


class Sleep(Level):
    title = "Sleep on it"
    tag, tag_note = "HYPOTHESIS", ("Replay during sleep is observed in the hippocampus. That it is how "
                                   "the brain avoids forgetting is the leading theory, not settled.")
    goal = "Learn task B to 90% while keeping task A at 80% or above."
    intro = ("A network that learns new associations on the same synapses overwrites old ones. "
             "This is catastrophic forgetting. The brain seems to avoid it by replaying experience "
             "during sleep, mixing old memories in with the new.\n\nThis network already knows "
             "task A: 8 associations. Task B is 8 new ones that look a lot like them. Each day "
             "it practises task B.")
    debrief = ("Learning B alone pulled the shared weights away from A. Mixing A back in while "
               "learning B finds weights that serve both. This is the complementary learning systems "
               "idea: the hippocampus stores episodes fast and replays them, so the cortex can learn "
               "slowly without overwriting what it knows. In AI the same trick is experience replay.")
    kb = "function/memory-systems.md"
    hint = "Tick sleep replay before you learn task B."
    DAYS = 8

    def build(self):
        self.a, self.b = sim.make_tasks()
        self.net = sim.Associator()
        self.net.train(*self.a, 50)
        self.hist = [(self.net.accuracy(*self.a), self.net.accuracy(*self.b))]
        self.forgot = False
        self.replay = self.check("Sleep replay of task A")
        self.button("Learn task B for a day", self.day)
        self.draw()
        self.say(f"Day 0\nTask A {self.hist[0][0]:.0%}\nTask B {self.hist[0][1]:.0%}")

    def day(self):
        if self.over:
            return
        sim.sleep_day(self.net, self.a, self.b, self.replay.get())
        acc_a, acc_b = self.net.accuracy(*self.a), self.net.accuracy(*self.b)
        self.hist.append((acc_a, acc_b))
        self.forgot |= acc_a < 0.8
        self.draw()
        days = len(self.hist) - 1
        msg = f"Day {days}{' (with replay)' if self.replay.get() else ''}\nTask A {acc_a:.0%}\nTask B {acc_b:.0%}"
        if acc_a >= 0.8 and acc_b >= 0.9:
            return self.win(1 + self.forgot + (days <= 4), msg)
        if acc_a < 0.8:
            msg += "\n\nTask A is being forgotten."
        if days >= self.DAYS:
            return self.fail(msg + "\n\nOut of days.")
        self.say(msg)

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


class Predict(Level):
    title = "Guess what's next"
    tag, tag_note = "HYPOTHESIS", "Predictive processing is a leading theory of the cortex, not a settled fact."
    goal = "Keep the tracking error under 0.05 for 12 seconds in a row."
    intro = ("One theory says the brain does not wait for its senses. It predicts what comes next "
             "and corrects itself only by the prediction error.\n\nThe ring is your brain's belief "
             "about a moving dot. Your senses are noisy (the pink flicker), and behind the grey "
             "screen you see nothing. The slider sets how much each prediction error moves the belief.")
    debrief = ("Trust the senses too much and the belief jumps with every bit of noise. Trust them "
               "too little and it lags behind. In between, the belief glides through the screen on "
               "its own prediction. Predictive coding calls this weighting precision, and attention "
               "may be the brain turning precision up where it matters.")
    kb = "function/predictive-processing.md"
    hint = "Neither end of the slider works. Try about a fifth of the way along and leave it there."
    timed = True
    WINDOW = 600  # ticks = 12 s
    TRACK_Y = 140

    @staticmethod
    def sweep():
        xs = [0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0]
        return ("Tracking error vs trust in the senses", "gain (trust in the senses)", "mean error over 12 s",
                xs, [sim.tracking_error(g) for g in xs])

    def build(self):
        self.world = sim.DotWorld(seed=None)
        self.tr = sim.Tracker(0.03)
        self.errs = []
        tk.Label(self.side, text="Trust in your senses", font=UI, fg=INK, bg=GLASS, anchor="w").pack(fill="x")
        self.scale = tk.Scale(self.side, from_=1, to=100, orient="horizontal", showvalue=False,
                              command=self.set_gain, bg=GLASS, troughcolor=LILAC, highlightthickness=0,
                              activebackground=VIOLET, sliderrelief="flat", length=240)
        self.scale.set(3)
        self.scale.pack(fill="x")
        c = self.canvas
        lo, hi = sim.DotWorld.OCCLUDER
        c.create_line(self.x(0), self.TRACK_Y, self.x(1), self.TRACK_Y, fill=LILAC, width=2)
        self.obs = c.create_oval(0, 0, 0, 0, fill=PINK, outline="")
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

    def set_gain(self, value):
        g = int(value) / 100
        self.tr.a, self.tr.b = g, g * g / (2 - g)
        self.errs = []

    def tick(self):
        if self.over:
            return
        dt = TICK_MS / 1000
        obs = self.world.step(dt)
        pos = self.tr.step(obs, dt)
        self.errs = (self.errs + [abs(pos - self.world.x)])[-self.WINDOW:]
        c = self.canvas
        y = self.TRACK_Y
        if obs is None:
            c.coords(self.obs, 0, 0, 0, 0)
        else:
            c.coords(self.obs, self.x(obs) - 5, y - 5, self.x(obs) + 5, y + 5)
        c.coords(self.belief, self.x(pos) - 14, y - 14, self.x(pos) + 14, y + 14)
        if len(self.errs) > 1:
            k = 30   # smooth the plotted error over 0.6 s
            sm = np.convolve(self.errs, np.ones(k) / k, mode="valid") if len(self.errs) > k else self.errs[-1:] * 2
            step = (W - 70) / self.WINDOW
            c.coords(self.err_line, *[v for i, e in enumerate(sm) for v in (40 + i * step, self.ey(e))])
        mean = float(np.mean(self.errs))
        secs = len(self.errs) * TICK_MS / 1000
        self.say(f"Error  {mean:.3f}  (goal under 0.05)\nMeasured over {secs:.0f} of 12 s.\n\n"
                 "Moving the slider restarts the 12 s.")
        if len(self.errs) == self.WINDOW and mean < 0.05:
            self.win(3 if mean < 0.035 else 2 if mean < 0.042 else 1, f"Tracking error {mean:.3f} over 12 s.")


class TinyBrain(Level):
    title = "Tiny brain"
    tag, tag_note = "HYPOTHESIS", ("Three-factor rules are observed at real synapses; that they are "
                                   "how whole animals learn to forage is a model, not a measurement.")
    goal = "Get the creature to eat 10 times within 400 steps."
    intro = ("Time to put pieces together. This creature starts in the top-left corner; the food is "
             "in the bottom-right. It has synapses that link where it is to which way it moves.\n\n"
             "A synapse used recently gets a tag (the eligibility trace). Dopamine, the reward "
             "prediction error, turns tags into lasting changes. Choose which parts to switch on, "
             "then run it.")
    debrief = ("Without dopamine nothing is learned: the creature wanders at random. Without the "
               "trace, only the last move before food gets credit, and learning crawls back one step "
               "at a time. With both, one meal teaches the whole path. This three-factor rule "
               "(tag × dopamine) is how real synapses are thought to solve credit assignment over time.")
    kb = "guides/build-a-brain-like-learner.md"
    hint = "It needs both parts: dopamine to learn at all, and the trace to credit the whole path."
    timed = True
    BUDGET, CELL, X0, Y0, SPEED = 400, 64, 40, 30, 2

    def build(self):
        self.dopamine = self.check("Dopamine (learning signal)")
        self.trace = self.check("Eligibility trace (memory of recent moves)")
        self.button("Run", self.run)
        self.agent, self.deltas = None, []
        self.say("Pick the parts, then press Run. You can run as many times as you like.")
        self.draw()

    def run(self):
        if not self.over:
            self.agent = sim.Forager(dopamine=self.dopamine.get(), trace=self.trace.get())
            self.deltas = []

    def tick(self):
        f = self.agent
        if self.over or f is None:
            return
        for _ in range(self.SPEED):
            self.deltas.append(f.step())
            if f.eaten >= 10 or f.steps >= self.BUDGET:
                break
        self.draw()
        msg = f"Food  {f.eaten} of 10\nSteps  {f.steps} of {self.BUDGET}"
        if f.eaten >= 10:
            self.win(3 if f.steps <= 250 else 2 if f.steps <= 320 else 1, msg)
        elif f.steps >= self.BUDGET:
            self.say(msg + "\n\nOut of steps. Change the parts and run again.")
            self.agent = None
        else:
            self.say(msg)

    def draw(self):
        c = self.canvas
        c.delete("all")
        f, n = self.agent, 5
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


class Pattern(Level):
    title = "Find the pattern"
    tag, tag_note = "HYPOTHESIS", ("Hebbian plasticity and synaptic normalisation are observed at real "
                                   "synapses. Oja's rule is a mathematical model of the pair, not a measured rule.")
    goal = "Line the neuron's weights up with the main direction of its inputs, and keep their length near 1."
    intro = ("Hebb's rule: neurons that fire together wire together. A synapse grows each time its input "
             "and the neuron's output are active at once. Applied alone it has a flaw: strong synapses make "
             "the output bigger, which makes them grow faster still.\n\nThis neuron has two input synapses. "
             "Each dot is one input it sees, and the arrow is its weights. Feed it inputs, set the learning "
             "rate, and decide whether to switch on Oja's forgetting term.")
    debrief = ("Pure Hebb finds the right direction but its weights run away. Oja's term, −y²w, makes each "
               "synapse forget in proportion to the output, which holds the weight length at 1. What is left "
               "is the first principal component: the direction the inputs vary most along. A neuron learned "
               "PCA from local information only (Oja 1982). Stack many such neurons with a little "
               "competition and you get sparse coding, the leading model of how V1 cells learn edge detectors.")
    kb = "learning/brain-inspired-learning-algorithms.md"
    hint = "Pure Hebb always runs away. Switch on Oja's term and keep the learning rate low."
    timed = True
    CX, CY, DOT, ARROW, HOLD, LIMIT = 230, 220, 40, 120, 100, 4.0   # px per input unit, px per weight unit

    def build(self):
        self.rng = np.random.default_rng()
        self.w, self.samples, self.streak = np.array([0.4, -0.3]), 0, 0
        self.running = self.ran_away = False
        self.recent, self.note = [], ""
        self.decay = self.check("Oja's forgetting term (−y²w)")
        tk.Label(self.side, text="Learning rate", font=UI, fg=INK, bg=GLASS, anchor="w").pack(fill="x")
        self.rate = tk.Scale(self.side, from_=1, to=50, orient="horizontal", bg=GLASS, troughcolor=LILAC,
                             highlightthickness=0, activebackground=VIOLET, sliderrelief="flat", length=240,
                             font=SMALL, fg=MUTED)
        self.rate.set(10)
        self.rate.pack(fill="x")
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
        self.say("Press Feed to start.")

    def toggle(self):
        if not self.over:
            self.running = not self.running
            self.feed.config(text="Pause  (Space)" if self.running else "Feed inputs  (Space)")

    def key(self, keysym):
        if keysym == "space":
            self.toggle()

    def reset(self):
        if not self.over:
            self.w, self.streak = np.array([0.4, -0.3]), 0

    def learn(self, n):
        """Feed n inputs through the rule. Returns True once the win condition has held for HOLD inputs."""
        X = self.rng.multivariate_normal([0, 0], sim.OJA_COV, size=n)
        for x in X:
            self.w = sim.oja_step(self.w, x, self.rate.get() / 1000, self.decay.get())
            self.samples += 1
            if not np.isfinite(self.w).all() or np.linalg.norm(self.w) > self.LIMIT:
                self.ran_away = True
                self.reset()
                self.note = (f"\n\nRunaway at input {self.samples}: the weights grew without limit and were "
                             "reset. Strong synapses made the output bigger, which made them grow faster.")
                break
            good = sim.alignment(self.w) > 0.98 and abs(np.linalg.norm(self.w) - 1) < 0.1
            self.streak = self.streak + 1 if good else 0
        self.recent = (self.recent + list(X))[-200:]
        return self.streak >= self.HOLD

    def tick(self):
        if self.over or not self.running:
            return
        done = self.learn(2)
        self.draw()
        norm = np.linalg.norm(self.w)
        msg = (f"Direction match  {sim.alignment(self.w):.0%}  (goal 98%)\nWeight length  {norm:.2f}  "
               f"(goal 0.9 to 1.1)\nInputs  {self.samples}")
        if done:
            return self.win(1 + self.ran_away + (self.samples <= 300), msg)
        self.say(msg + self.note)

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


class Zoo(Level):
    title = "Neuron zoo"
    goal = "Make the Izhikevich neuron fire all four patterns: regular, bursting, chattering, fast."
    intro = ("Cortical neurons do not all fire alike. Pyramidal cells fire regularly and slow down, some "
             "fire a burst and then settle, some fire burst after burst, and inhibitory interneurons fire "
             "fast and steady.\n\nTwo model neurons get the same constant current. The top one is the "
             "level 1 neuron (leaky integrate-and-fire). The bottom one is Izhikevich's: two equations and "
             "four numbers. a is how fast a recovery current builds, c is the voltage it resets to after "
             "a spike, d is how much recovery each spike adds (b stays at 0.2). Set them and press Run.")
    debrief = ("Four numbers turned one equation into four cell types. The recovery variable u is the trick: "
               "a high reset c with a small kick d lets spikes come in bursts, a large d slows the cell "
               "down, a fast a lets it fire quickly without tiring. The leaky integrate-and-fire neuron has "
               "no recovery variable, so it can only fire faster or slower, never in bursts. This is why "
               "large simulations that care about firing patterns use Izhikevich neurons (Izhikevich 2003).")
    kb = "simulation/levels-of-brain-modeling.md"
    hint = "Keep a at 0.02: c -55 with d 4 bursts once, c -50 with d 2 chatters. Fast spiking needs a near 0.1."
    TOP, BOTTOM, LEFT = 130, 330, 40   # y of the two traces' resting lines, x of their start
    TARGETS = ("regular spiking", "intrinsically bursting", "chattering", "fast spiking")

    def build(self):
        self.found, self.runs = set(), 0
        self.sliders = {}
        for name, lo, hi, res, val in (("current", 0, 20, 1, 10), ("a", 0.01, 0.12, 0.01, 0.02),
                                       ("c (mV)", -70, -45, 1, -65), ("d", 0, 10, 1, 8)):
            tk.Label(self.side, text=name, font=UI, fg=INK, bg=GLASS, anchor="w").pack(fill="x")
            s = tk.Scale(self.side, from_=lo, to=hi, resolution=res, orient="horizontal", bg=GLASS,
                         troughcolor=LILAC, highlightthickness=0, activebackground=VIOLET, sliderrelief="flat",
                         length=240, font=SMALL, fg=MUTED)
            s.set(val)
            s.pack(fill="x")
            self.sliders[name] = s
        self.button("Run 300 ms  (Space)", self.run)
        self.say("Found  none yet\n\nSet a, c and d, then press Run.")

    def key(self, keysym):
        if keysym == "space":
            self.run()

    def set(self, current, a, c, d):
        for name, v in zip(self.sliders, (current, a, c, d)):
            self.sliders[name].set(v)

    def run(self):
        if self.over:
            return
        I, a, c, d = (s.get() for s in self.sliders.values())
        self.runs += 1
        lif, izh = sim.lif_run(I), sim.izhikevich(a, 0.2, c, d, I)
        lif_kind, izh_kind = sim.firing_pattern(lif[0]), sim.firing_pattern(izh[0])
        if izh_kind in self.TARGETS:
            self.found.add(izh_kind)
        self.draw(lif, lif_kind, izh, izh_kind)
        msg = (f"Izhikevich  {izh_kind}\nLIF  {lif_kind}\n\nFound  "
               + (", ".join(t for t in self.TARGETS if t in self.found) or "none yet")
               + f"\nRuns  {self.runs}")
        if len(self.found) == len(self.TARGETS):
            return self.win(1 + (self.runs <= 8) + (self.runs <= 5), msg)
        self.say(msg)

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


LEVELS = [Spark, Wire, Lesion, Dopamine, Remember, Sleep, Predict, TinyBrain, Pattern, Zoo]
