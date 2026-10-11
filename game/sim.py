"""Brain Lab models: numpy only, no UI imports.

Each section names the knowledge-base topic it comes from. Biological constants are
copied from those files. Constants marked "game gain" are tuning knobs chosen so a
level is playable; they are not biological measurements.
"""
import math

import numpy as np

# --- Leaky integrate-and-fire neuron (simulation/spiking-neural-networks.md) ---
TAU_M, V_REST, V_TH, V_RESET, R = 10.0, -70.0, -55.0, -75.0, 10.0  # ms, mV, mV, mV, MOhm
T_REF = 2.0  # ms, absolute refractory period (textbook ~1-2 ms; anatomy/neurons-and-synapses.md)


class LIF:
    def __init__(self, tau_m=TAU_M, r=R, v_th=V_TH, v_reset=V_RESET, t_ref=T_REF):
        self.v, self.ref = V_REST, 0.0
        self.tau_m, self.r, self.v_th, self.v_reset, self.t_ref = tau_m, r, v_th, v_reset, t_ref

    def step(self, current, dt):
        """Advance dt ms with input current (nA). Returns True if the neuron spiked."""
        if self.ref > 0:
            self.ref -= dt
            return False
        self.v += dt / self.tau_m * (-(self.v - V_REST) + self.r * current)
        if self.v >= self.v_th:
            self.v, self.ref = self.v_reset, self.t_ref
            return True
        return False


# --- STDP pair rule (function/learning-and-plasticity.md: ~20 ms window) ---
TAU_STDP = 20.0  # ms
A_STDP = 0.1     # game gain: a few well-timed pairings move a weight from 0.5 past 0.8


class STDP:
    """Synapses onto one postsynaptic neuron, nearest-spike traces."""

    def __init__(self, n, w0=0.5):
        self.w = np.full(n, w0)
        self.x_pre = np.zeros(n)
        self.x_post = 0.0

    def decay(self, dt):
        k = math.exp(-dt / TAU_STDP)
        self.x_pre *= k
        self.x_post *= k

    def pre(self, i):
        self.w[i] -= A_STDP * self.x_post   # pre after post -> depress
        self.x_pre[i] = 1.0
        np.clip(self.w, 0, 1, out=self.w)

    def post(self):
        self.w += A_STDP * self.x_pre       # pre before post -> potentiate
        self.x_post = 1.0
        np.clip(self.w, 0, 1, out=self.w)


# --- TD(0) dopamine model (function/learning-and-plasticity.md: d = r + gV(s') - V(s)) ---
T_BELL, T_JUICE, TD_ALPHA = 2, 8, 0.5  # time steps; game gain


def td_trial(V, bell, juice, alpha=TD_ALPHA, gamma=1.0, t_juice=T_JUICE):
    """Run one trial and update V in place.

    V[k] is the value k steps after the bell. Before the bell (or with no bell) the
    state predicts nothing and has value 0, and so does every state from T_JUICE on.
    The trial ends at T_JUICE, or later if t_juice (at most T_JUICE + 2) delays the juice.
    Returns the TD error per time step: the simulated dopamine signal.
    """
    def state(t):
        return t - T_BELL if bell and t >= T_BELL else None

    def value(s):
        return 0.0 if s is None or s >= len(V) else V[s]

    delta = np.zeros(T_JUICE + 3)
    for t in range(1, max(T_JUICE, t_juice) + 1):
        prev, now = state(t - 1), state(t)
        r = 1.0 if juice and t == t_juice else 0.0
        delta[t] = r + gamma * value(now) - value(prev)
        if prev is not None and prev < len(V):
            V[prev] += alpha * delta[t]
    return delta


def td_values():
    return np.zeros(T_JUICE - T_BELL)


# --- Hopfield network (function/memory-systems.md: capacity ~0.14 N) ---
class Hopfield:
    def __init__(self, n):
        self.n = n
        self.W = np.zeros((n, n))
        self.patterns = []

    def store(self, p):
        p = np.asarray(p, float)
        self.patterns.append(p)
        self.W += np.outer(p, p) / self.n   # Hebbian one-shot storage
        np.fill_diagonal(self.W, 0)

    def update(self, s):
        s = np.sign(self.W @ s)
        s[s == 0] = 1
        return s

    def recall(self, cue, steps=10):
        s = np.asarray(cue, float)
        for _ in range(steps):
            s = self.update(s)
        return s

    def test(self, flip_frac=0.1, seed=0):
        """Corrupt each stored pattern, recall it, return the overlaps (1.0 = perfect)."""
        rng = np.random.default_rng(seed)
        out = []
        for p in self.patterns:
            cue = p.copy()
            cue[rng.choice(self.n, int(flip_frac * self.n), replace=False)] *= -1
            out.append(float(self.recall(cue) @ p) / self.n)
        return out


# --- Continual learning with replay (function/memory-systems.md, learning/brain-inspired-learning-algorithms.md) ---
# A linear associator trained with the local delta rule. Tasks A and B share a common
# input component, so learning B overwrites A unless A is replayed (interleaved).
LMS_RATE = 0.2  # game gain


def make_tasks(seed=0, n_in=20, n_out=5, items=8, shared=1.0):
    rng = np.random.default_rng(seed)
    common = rng.normal(size=n_in)
    tasks = []
    for _ in range(2):
        X = shared * common + rng.normal(size=(items, n_in))
        X /= np.linalg.norm(X, axis=1, keepdims=True)
        tasks.append((X, rng.choice([-1.0, 1.0], size=(items, n_out))))
    return tasks


class Associator:
    def __init__(self, n_in=20, n_out=5):
        self.W = np.zeros((n_out, n_in))

    def train(self, X, Y, epochs=1, rate=LMS_RATE):
        for _ in range(epochs):
            for x, y in zip(X, Y):
                self.W += rate * np.outer(y - self.W @ x, x)  # error x presynaptic input

    def accuracy(self, X, Y):
        return float((np.sign(X @ self.W.T) == Y).mean())


def sleep_day(net, task_a, task_b, replay, epochs=10):
    """One day of learning task B; with replay, task A is interleaved (as in sleep replay)."""
    if replay:
        X = np.vstack([task_a[0], task_b[0]])
        Y = np.vstack([task_a[1], task_b[1]])
        order = np.random.default_rng(len(X)).permutation(len(X))
        net.train(X[order], Y[order], epochs)
    else:
        net.train(*task_b, epochs)


# --- Predictive tracking (function/predictive-processing.md) ---
# Belief = position and velocity. Each step predicts, then corrects by gain x prediction
# error. The gain is how much the observer trusts its senses (the "precision").
class Tracker:
    def __init__(self, gain):
        self.a = gain
        self.b = gain * gain / (2 - gain)   # matched velocity gain (critically damped alpha-beta)
        self.pos, self.vel = 0.5, 0.0

    def step(self, obs, dt):
        self.pos += self.vel * dt                 # prediction
        if obs is not None:
            err = obs - self.pos                  # prediction error
            self.pos += self.a * err
            self.vel += self.b * err / dt
        return self.pos


class DotWorld:
    """A dot bouncing between 0 and 1, hidden behind an occluder, seen with sensor noise."""
    SPEED, NOISE, OCCLUDER = 0.35, 0.05, (0.4, 0.6)

    def __init__(self, seed=0):
        self.x, self.v = 0.1, self.SPEED
        self.rng = np.random.default_rng(seed)

    def step(self, dt):
        self.x += self.v * dt
        if not 0 <= self.x <= 1:
            self.v = -self.v
            self.x = min(max(self.x, 0.0), 1.0)
        lo, hi = self.OCCLUDER
        if lo <= self.x <= hi:
            return None
        return self.x + self.rng.normal(0, self.NOISE)


def tracking_error(gain, seconds=12.0, dt=0.02, seed=0):
    world, tr = DotWorld(seed), Tracker(gain)
    errs = [abs(tr.step(world.step(dt), dt) - world.x) for _ in range(int(seconds / dt))]
    return float(np.mean(errs))


# --- Three-factor forager (guides/build-a-brain-like-learner.md, learning-and-plasticity.md) ---
# Actor-critic on a grid. Dopamine = TD error. The eligibility trace tags recently used
# synapses so a later dopamine burst can credit them.
MOVES = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right


class Forager:
    def __init__(self, size=5, dopamine=True, trace=True, seed=None):
        self.size, self.dopamine = size, dopamine
        self.lam = 0.9 if trace else 0.0
        self.gamma, self.alpha_v, self.alpha_pi = 0.95, 0.3, 2.0  # game gains
        n = size * size
        self.V = np.zeros(n)
        self.pi = np.zeros((n, 4))
        self.food = (size - 1, size - 1)
        self.rng = np.random.default_rng(seed)
        self.eaten = self.steps = 0
        self._respawn()

    def _respawn(self):
        self.pos = (0, 0)
        self.e_v = np.zeros_like(self.V)
        self.e_pi = np.zeros_like(self.pi)

    def _s(self, pos):
        return pos[1] * self.size + pos[0]

    def step(self):
        """Take one action. Returns the dopamine (TD error) of this step."""
        s = self._s(self.pos)
        p = np.exp(self.pi[s] - self.pi[s].max())
        p /= p.sum()
        a = self.rng.choice(4, p=p)
        dx, dy = MOVES[a]
        self.pos = (min(max(self.pos[0] + dx, 0), self.size - 1),
                    min(max(self.pos[1] + dy, 0), self.size - 1))
        self.steps += 1
        ate = self.pos == self.food
        r = 1.0 if ate else 0.0
        v_next = 0.0 if ate else self.V[self._s(self.pos)]
        delta = r + self.gamma * v_next - self.V[s]
        self.e_v *= self.gamma * self.lam
        self.e_pi *= self.gamma * self.lam
        self.e_v[s] += 1
        self.e_pi[s] += np.eye(4)[a] - p          # Hebbian tag: chosen action vs expected
        if self.dopamine:                          # the third factor gates every change
            self.V += self.alpha_v * delta * self.e_v
            self.pi += self.alpha_pi * delta * self.e_pi
        if ate:
            self.eaten += 1
            self._respawn()
        return delta if self.dopamine else 0.0


# --- Hebbian learning with Oja's rule (learning/brain-inspired-learning-algorithms.md, Oja 1982) ---
OJA_COV = np.array([[3.0, 1.0], [1.0, 1.0]])  # input covariance, as in the topic file


def oja_step(w, x, rate, decay=True):
    """One input. Hebb alone is y*x; Oja's decay term -y^2*w keeps |w| near 1."""
    y = w @ x
    return w + rate * y * (x - y * w if decay else x)


def alignment(w, C=OJA_COV):
    """|cos| between w and the input's first principal component (1.0 = found it)."""
    pc1 = np.linalg.eigh(C)[1][:, -1]
    return float(abs(w @ pc1) / max(np.linalg.norm(w), 1e-12))


# --- Izhikevich neuron (simulation/levels-of-brain-modeling.md, spiking-neural-networks.md) ---
# Izhikevich 2003, IEEE Trans Neural Networks 14:1569, Fig. 2: (a, b, c, d) per cortical cell type.
IZH_PRESETS = {
    "regular spiking": (0.02, 0.2, -65, 8),
    "intrinsically bursting": (0.02, 0.2, -55, 4),
    "chattering": (0.02, 0.2, -50, 2),
    "fast spiking": (0.1, 0.2, -65, 2),
}
ZOO_T, ZOO_DT = 300.0, 0.25   # ms
LIF_PER_IZH = 0.2             # game gain: nA of LIF current per Izhikevich current unit (10 -> 2 nA)


def izhikevich(a, b, c, d, current, T=ZOO_T, dt=ZOO_DT):
    """Constant current for T ms. Returns (spike times in ms, voltage trace in mV)."""
    v, u, spikes, trace = -65.0, b * -65.0, [], []
    for k in range(int(T / dt)):
        v += dt * (0.04 * v * v + 5 * v + 140 - u + current)
        u += dt * a * (b * v - u)
        if v >= 30:
            trace.append(30.0)
            v, u = c, u + d
            spikes.append(k * dt)
        else:
            trace.append(v)
    return spikes, np.array(trace)


def lif_run(current, T=ZOO_T, dt=ZOO_DT):
    """The level 1 LIF neuron under the same constant current, scaled to nA."""
    n, spikes, trace = LIF(), [], []
    for k in range(int(T / dt)):
        spiked = n.step(current * LIF_PER_IZH, dt)
        if spiked:
            spikes.append(k * dt)
        trace.append(30.0 if spiked else n.v)
    return spikes, np.array(trace)


def firing_pattern(spikes, T=ZOO_T):
    """Name a spike train's pattern from its interspike intervals.

    A burst is 3+ spikes whose intervals are under a quarter of the longest one.
    No bursts: fast spiking at 50 Hz or more, else regular spiking.
    """
    if len(spikes) < 3:
        return "too few spikes"
    isi = np.diff(spikes)
    short = isi < 0.25 * isi.max()
    runs = "".join("s" if s else "." for s in short).split(".")
    bursts = sum(len(r) >= 2 for r in runs)
    if bursts >= 2:
        return "chattering"
    if bursts == 1 and short[0] and short[1]:
        return "intrinsically bursting"
    if bursts:
        return "irregular"
    return "fast spiking" if len(spikes) / T * 1000 >= 50 else "regular spiking"


# --- Grid cells (function/spatial-navigation.md) ---
def grid_rate(pos, spacing=0.25):
    """A grid cell's firing (0..1) at pos: three plane waves 60° apart make a hexagonal lattice."""
    k = 4 * math.pi / (math.sqrt(3) * spacing)
    pos = np.asarray(pos, float)
    s = sum(math.cos(k * (pos[0] * math.cos(t) + pos[1] * math.sin(t))) for t in (0, math.pi / 3, 2 * math.pi / 3))
    return (s + 1.5) / 4.5


# --- Path integration with landmark correction (function/spatial-navigation.md) ---
NEST = (0.1, 0.1)
LANDMARKS = ((0.75, 0.3), (0.3, 0.75), (0.8, 0.85))
PLACE_R = 0.08     # game gain: radius of a landmark's place field, in arena units
NAV_NOISE = 0.35   # game gain: self-motion noise per step, as a fraction of the step length


class Navigator:
    """A forager that knows where it is only by adding up its own steps (path integration).

    The estimate drifts because every step is sensed with noise. With landmarks on, standing in a
    landmark's place field resets the estimate to the true position.
    """

    def __init__(self, landmarks=True, seed=None):
        self.landmarks = landmarks
        self.true, self.est = np.array(NEST), np.array(NEST)
        self.rng = np.random.default_rng(seed)
        self.travelled = 0.0

    def move(self, dx, dy):
        """Step by (dx, dy), stopped at the arena walls. Returns True if a landmark reset the estimate."""
        new = np.clip(self.true + (dx, dy), 0, 1)
        step = new - self.true
        self.true = new
        size = float(np.linalg.norm(step))
        self.travelled += size
        self.est = self.est + step + self.rng.normal(0, NAV_NOISE * size, 2)
        if self.landmarks and any(np.linalg.norm(self.true - L) < PLACE_R for L in LANDMARKS):
            self.est = self.true.copy()
            return True
        return False

    def error(self):
        return float(np.linalg.norm(self.est - self.true))

    def home(self):
        """Walk the home vector in one straight line, stopped by the walls. Returns the miss distance."""
        self.true = np.clip(self.true + (np.array(NEST) - self.est), 0, 1)
        self.est = np.array(NEST)
        return float(np.linalg.norm(self.true - NEST))


def homing_error(steps, seed=0, step=0.03):
    """Wander for steps with no landmarks, then head home. Returns the miss distance."""
    nav, rng, heading = Navigator(landmarks=False, seed=seed), np.random.default_rng(seed + 1000), 0.8
    for _ in range(steps):
        heading += rng.normal(0, 0.6)
        nav.move(step * math.cos(heading), step * math.sin(heading))
    return nav.home()
