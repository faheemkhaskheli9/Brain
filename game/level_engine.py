"""The eleven Brain Lab levels without a UI: state, rules, win conditions and scoring.

levels.py draws each one on a tkinter canvas; test_levels.py plays them headlessly. Nothing here
imports tkinter. Every level runs its model from sim.py.
"""
import numpy as np

import sim

TICK_MS = 20   # one tick of a timed level, in wall-clock ms


class Level:
    title = goal = intro = debrief = kb = hint = ""
    tag, tag_note = "ESTABLISHED", ""
    timed = False   # runs on its own clock, so the shell offers pause and step

    @staticmethod
    def sweep():
        """Optional debrief chart: (title, x label, y label, xs, ys) from the level's model."""
        return None

    def __init__(self, seed=None):
        self.rng = np.random.default_rng(seed)
        self.over, self.stars, self.message, self.hint_text = False, None, "", ""
        self.setup()

    def setup(self):
        pass

    def tick(self):
        pass

    def key(self, keysym):
        pass

    def say(self, text):
        self.message = text

    def show_hint(self):
        if self.hint:
            self.hint_text = "Hint: " + self.hint

    def win(self, stars, text=""):
        if not self.over:
            self.over, self.stars = True, stars
            self.say(text or "Done.")

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

    def setup(self):
        self.neuron, self.t, self.pulses, self.clicks, self.spikes = sim.LIF(), 0, [], 0, 0
        self.points, self.spike_times = [(0, sim.V_REST)], []
        self.say("Waiting for your first click.")

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
            self.spike_times.append(self.t)
            self.points.append((self.t, -40))
        self.points.append((self.t, self.neuron.v))
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

    def setup(self):
        self.syn, self.t, self.events, self.presses = sim.STDP(2), 0.0, [], 0
        self.say("A 0.50   B 0.50\n\nFire an input, then the output a moment later.")

    def key(self, keysym):
        k = {"a": 0, "b": 1, "space": 2}.get(keysym.lower())
        if k is not None:
            self.fire(k)

    def fire(self, who):
        """who: 0 input A, 1 input B, 2 the output neuron."""
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


REGIONS = sim.REGIONS  # level 3's table lives in sim.py so the web version shares it


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

    def setup(self):
        self.cut, self.named, self.mistakes = None, set(), 0
        self.say("Click a hidden region on the slide to lesion it.")

    def jobs(self):
        """The job panel's text and whether a job is broken."""
        if self.cut is None:
            return "All 8 jobs work.", False
        return f"7 of 8 jobs work. Broken:\n✗ {REGIONS[self.cut][1]}", True

    def lesion(self, name):
        if self.over:
            return
        self.cut = name
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
        self.cut = None
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

    def setup(self):
        self.V, self.trials, self.learned, self.surprise, self.history = sim.td_values(), 0, False, False, []
        self.last = (np.zeros(sim.T_JUICE + 3), None, None)   # the latest trial: (TD error per step, bell, juice)
        self.say("Run a trial to see the dopamine response.")

    def trial(self, bell, juice):
        if self.over:
            return
        self.trials += 1
        d = sim.td_trial(self.V, bell, juice)
        self.history.append((d[sim.T_BELL], d[sim.T_JUICE]))
        self.last = (d, bell, juice)
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

    @staticmethod
    def sweep():
        rng, xs, ys = np.random.default_rng(0), list(range(1, 21)), []
        for n in xs:
            net = sim.Hopfield(64)
            for _ in range(n):
                net.store(rng.choice([-1.0, 1.0], 64))
            ys.append(float(np.mean(net.test())))
        return "Recall vs memories stored (random patterns)", "memories stored", "mean recall overlap", xs, ys

    def setup(self):
        self.net, self.state = sim.Hopfield(64), -np.ones(64)
        self.passed = self.completed = False
        self.recall_steps, self.paint, self.results = 0, 1.0, []
        self.say("Draw a shape, then store it.")

    def press(self, i):
        """Start a stroke on cell i: it flips, and the rest of the stroke paints the same value."""
        if not self.recall_steps:
            self.paint = -self.state[i]
            self.drag(i)

    def drag(self, i):
        if not self.recall_steps:
            self.state[i] = self.paint

    def show(self, s):
        self.state = np.array(s, float)

    def store(self):
        if (self.state < 0).all():
            return self.say("The drawing is empty. Draw something first.")
        self.net.store(self.state)
        self.results = []
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
        if self.recall_steps:
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
        good = sum(r > 0.95 for r in self.results)
        msg = f"Each memory was corrupted by 10% and recalled.\n{good} of {n} came back intact."
        if good == n:
            self.passed = True
            msg += "\n\nAll recalled. Keep storing memories until recall breaks."
        elif self.passed:
            stars = 1 + self.completed + (n >= 9)
            return self.win(stars, msg + f"\n\nRecall broke at {n} memories.")
        self.say(msg)


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

    def setup(self):
        self.a, self.b = sim.make_tasks()
        self.net = sim.Associator()
        self.net.train(*self.a, 50)
        self.hist = [(self.net.accuracy(*self.a), self.net.accuracy(*self.b))]
        self.forgot = self.replay = False
        self.say(f"Day 0\nTask A {self.hist[0][0]:.0%}\nTask B {self.hist[0][1]:.0%}")

    def day(self):
        if self.over:
            return
        sim.sleep_day(self.net, self.a, self.b, self.replay)
        acc_a, acc_b = self.net.accuracy(*self.a), self.net.accuracy(*self.b)
        self.hist.append((acc_a, acc_b))
        self.forgot |= acc_a < 0.8
        days = len(self.hist) - 1
        msg = f"Day {days}{' (with replay)' if self.replay else ''}\nTask A {acc_a:.0%}\nTask B {acc_b:.0%}"
        if acc_a >= 0.8 and acc_b >= 0.9:
            return self.win(1 + self.forgot + (days <= 4), msg)
        if acc_a < 0.8:
            msg += "\n\nTask A is being forgotten."
        if days >= self.DAYS:
            return self.fail(msg + "\n\nOut of days.")
        self.say(msg)


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

    @staticmethod
    def sweep():
        xs = [0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0]
        return ("Tracking error vs trust in the senses", "gain (trust in the senses)", "mean error over 12 s",
                xs, [sim.tracking_error(g) for g in xs])

    def setup(self):
        self.world = sim.DotWorld(seed=self.rng.integers(2**32))
        self.tr = sim.Tracker(0.03)
        self.errs, self.obs, self.pos = [], None, self.tr.pos

    def set_gain(self, percent):
        g = int(percent) / 100
        self.tr.a, self.tr.b = g, g * g / (2 - g)
        self.errs = []

    def tick(self):
        if self.over:
            return
        dt = TICK_MS / 1000
        self.obs = self.world.step(dt)
        self.pos = self.tr.step(self.obs, dt)
        self.errs = (self.errs + [abs(self.pos - self.world.x)])[-self.WINDOW:]
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
    BUDGET, SPEED = 400, 2

    def setup(self):
        self.dopamine = self.trace = False
        self.agent, self.deltas = None, []
        self.say("Pick the parts, then press Run. You can run as many times as you like.")

    def run(self, seed=None):
        if not self.over:
            self.agent = sim.Forager(dopamine=self.dopamine, trace=self.trace, seed=seed)
            self.deltas = []

    def tick(self):
        f = self.agent
        if self.over or f is None:
            return
        for _ in range(self.SPEED):
            self.deltas.append(f.step())
            if f.eaten >= 10 or f.steps >= self.BUDGET:
                break
        msg = f"Food  {f.eaten} of 10\nSteps  {f.steps} of {self.BUDGET}"
        if f.eaten >= 10:
            self.win(3 if f.steps <= 250 else 2 if f.steps <= 320 else 1, msg)
        elif f.steps >= self.BUDGET:
            self.say(msg + "\n\nOut of steps. Change the parts and run again.")
            self.agent = None
        else:
            self.say(msg)


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
    HOLD, LIMIT = 100, 4.0

    def setup(self):
        self.w, self.samples, self.streak = np.array([0.4, -0.3]), 0, 0
        self.running = self.ran_away = self.decay = False
        self.rate = 0.01
        self.recent, self.note = [], ""
        self.say("Press Feed to start.")

    def toggle(self):
        if not self.over:
            self.running = not self.running

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
            self.w = sim.oja_step(self.w, x, self.rate, self.decay)
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
        norm = np.linalg.norm(self.w)
        msg = (f"Direction match  {sim.alignment(self.w):.0%}  (goal 98%)\nWeight length  {norm:.2f}  "
               f"(goal 0.9 to 1.1)\nInputs  {self.samples}")
        if done:
            return self.win(1 + self.ran_away + (self.samples <= 300), msg)
        self.say(msg + self.note)


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
    TARGETS = ("regular spiking", "intrinsically bursting", "chattering", "fast spiking")
    # name, low, high, resolution, start value of each slider
    PARAMS = (("current", 0, 20, 1, 10), ("a", 0.01, 0.12, 0.01, 0.02),
              ("c (mV)", -70, -45, 1, -65), ("d", 0, 10, 1, 8))

    def setup(self):
        self.found, self.runs, self.last = set(), 0, None
        self.params = {name: val for name, *_, val in self.PARAMS}
        self.say("Found  none yet\n\nSet a, c and d, then press Run.")

    def key(self, keysym):
        if keysym == "space":
            self.run()

    def set(self, current, a, c, d):
        self.params = dict(zip(self.params, (current, a, c, d)))

    def run(self):
        if self.over:
            return
        I, a, c, d = self.params.values()
        self.runs += 1
        lif, izh = sim.lif_run(I), sim.izhikevich(a, 0.2, c, d, I)
        lif_kind, izh_kind = sim.firing_pattern(lif[0]), sim.firing_pattern(izh[0])
        if izh_kind in self.TARGETS:
            self.found.add(izh_kind)
        self.last = (lif, lif_kind, izh, izh_kind)
        msg = (f"Izhikevich  {izh_kind}\nLIF  {lif_kind}\n\nFound  "
               + (", ".join(t for t in self.TARGETS if t in self.found) or "none yet")
               + f"\nRuns  {self.runs}")
        if len(self.found) == len(self.TARGETS):
            return self.win(1 + (self.runs <= 8) + (self.runs <= 5), msg)
        self.say(msg)


class Home(Level):
    title = "Find your way home"
    tag, tag_note = "HYPOTHESIS", ("Place, grid and head-direction cells are measured. That grid cells do the "
                                   "brain's path integration is the leading theory, not settled.")
    goal = "Find the hidden food, then head home in one straight line and land on the nest."
    intro = ("Your brain keeps a map. Place cells in the hippocampus fire at one spot each; grid cells next "
             "door fire on a hexagonal lattice that tiles the whole room, like graph paper. By adding up its "
             "own steps (path integration) an animal knows where it is even in the dark, and can run "
             "straight home along a path it never took.\n\nArrow keys move the creature (pink). The ring "
             "is where it thinks it is. Each step is sensed with a little noise. The circles around the "
             "three posts are landmark place fields.")
    debrief = ("Adding up noisy steps drifts: the error grows the farther you walk, like the chart below. "
               "A landmark you recognise snaps the estimate back, which is why place fields anchor to visible "
               "cues. The straight run home was a shortcut you never walked: the home vector came from the "
               "map, not from memory of the route. Desert ants do this with no landmarks over tens of metres "
               "(Müller and Wehner 1988), and an AI agent trained to path-integrate grew grid-like units "
               "on its own (Banino et al. 2018).")
    kb = "function/spatial-navigation.md"
    hint = "After you find the food, walk through a post's circle so your estimate resets, then press H at once."
    STEP, FOUND_R, HOME_R, FAR = 0.03, 0.06, 0.08, 0.4   # FAR: H only works this far from the nest
    FOOD_SPOTS = ((0.9, 0.55), (0.55, 0.92), (0.92, 0.92), (0.6, 0.55))

    @staticmethod
    def sweep():
        xs = [10, 25, 50, 100, 150, 200]
        return ("Miss distance vs steps walked, no landmarks", "steps walked", "median miss (arena widths)",
                xs, [float(np.median([sim.homing_error(n, seed) for seed in range(40)])) for n in xs])

    def setup(self):
        self.nav = sim.Navigator(seed=self.rng.integers(2**32))
        self.food = np.array(self.FOOD_SPOTS[self.rng.integers(len(self.FOOD_SPOTS))])
        self.found = self.fixed = False
        self.landmarks = True
        self.trail = [tuple(sim.NEST)]
        self.run_home = None   # (start, end) of the straight run home, once taken
        self.say("Use the arrow keys to search for food.")

    def key(self, keysym):
        d = {"Left": (-1, 0), "Right": (1, 0), "Up": (0, 1), "Down": (0, -1)}.get(keysym)
        if d:
            self.move(*d)
        elif keysym.lower() == "h":
            self.go_home()

    def move(self, dx, dy):
        if self.over:
            return
        self.nav.landmarks = self.landmarks
        drift = self.nav.error()
        reset = self.nav.move(dx * self.STEP, dy * self.STEP)
        self.fixed |= reset and self.found and drift > 0.05   # a landmark fixed real drift on the way home
        self.trail.append(tuple(self.nav.true))
        if not self.found and np.linalg.norm(self.nav.true - self.food) < self.FOUND_R:
            self.found = True
        msg = "Food found. Now press H to run straight home." if self.found else "Searching for food."
        msg += (f"\n\nEstimate is off by {self.nav.error():.2f}\nWalked {self.nav.travelled:.1f} arena widths"
                f"\nGrid cell firing at your estimate  {sim.grid_rate(self.nav.est):.0%}")
        if reset:
            msg += "\n\nA landmark's place cells reset your position."
        self.say(msg)

    def go_home(self):
        if self.over:
            return
        if not self.found:
            return self.say("Find the food first, then head home.")
        start, drift = self.nav.true.copy(), self.nav.error()
        straight = float(np.linalg.norm(start - sim.NEST))
        if straight < self.FAR:
            return self.say("You can nearly see the nest from here. Head home from farther out, "
                            "where only your map knows the way.")
        miss = self.nav.home()
        self.run_home = (start, self.nav.true.copy())
        msg = f"Missed the nest by {miss:.2f}. Your estimate was off by {drift:.2f} when you set out."
        if miss >= self.HOME_R:
            return self.fail(msg)
        shortcut = self.nav.travelled >= 3 * straight
        self.win(1 + shortcut + self.fixed,
                 f"Home. Your route out was {self.nav.travelled:.1f} arena widths; the way back was {straight:.2f}.")


LEVELS = [Spark, Wire, Lesion, Dopamine, Remember, Sleep, Predict, TinyBrain, Pattern, Zoo, Home]
