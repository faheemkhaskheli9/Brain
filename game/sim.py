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
    def __init__(self):
        self.v, self.ref = V_REST, 0.0

    def step(self, current, dt):
        """Advance dt ms with input current (nA). Returns True if the neuron spiked."""
        if self.ref > 0:
            self.ref -= dt
            return False
        self.v += dt / TAU_M * (-(self.v - V_REST) + R * current)
        if self.v >= V_TH:
            self.v, self.ref = V_RESET, T_REF
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
