// Brain World core: a creature that learns, from reward alone, to walk, grasp, listen, read and write.
// No DOM here, so node can run it headlessly (test_brain.mjs) and index.html can draw it in 3D.
//
// Brain: a fixed random sparse expansion of the senses (like cerebellar granule cells or the
// insect mushroom body) feeds an actor-critic. Dopamine is the TD error; eligibility traces tag
// recently used synapses; weights change only when trace x dopamine (a three-factor rule).
// No backprop, no hand-coded behaviour. See guides/build-a-brain-like-learner.md.

export function rng(seed) {   // mulberry32: seeded, so runs are repeatable. f.state can be saved and set.
  const f = () => {
    const a = f.state = (f.state + 0x6D2B79F5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), a | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  f.state = seed >>> 0;
  return f;
}

export const ARENA = 8, RAYS = 15, FOV = 1.4, FOVEA = 0.2, REACH = 1.0, OBJ_R = 0.4;
export const BODY = ["push left leg", "push right leg", "lift left leg", "lift right leg", "grasp"];
// Pen strokes on a 5x5 pad. Letters are pairs of strokes, and the fovea sees the same bitmaps,
// so the letters it reads and the letters it writes are the same shapes.
export const PEN = ["top bar", "bottom bar", "left bar", "middle bar", "/", "\\"];
const STROKE_CELLS = [
  [0, 1, 2, 3, 4].map(c => [0, c]), [0, 1, 2, 3, 4].map(c => [4, c]),
  [0, 1, 2, 3, 4].map(r => [r, 0]), [0, 1, 2, 3, 4].map(r => [r, 2]),
  [0, 1, 2, 3, 4].map(r => [r, 4 - r]), [0, 1, 2, 3, 4].map(r => [r, r]),
];
export const LETTERS = [["T", [0, 3]], ["L", [2, 1]], ["X", [4, 5]]];
export const COLORS = [[1, 0.15, 0.15], [0.15, 1, 0.25], [0.25, 0.35, 1]];
export const TONES_HZ = [262, 392, 587];   // C4, G4, D5: one per letter / colour

export function glyph(strokes) {
  const g = new Float32Array(25);
  for (const s of strokes) for (const [r, c] of STROKE_CELLS[s]) g[r * 5 + c] = 1;
  return g;
}

export const STAGES = [
  { key: "walk", name: "Learn to walk", pass: 0.8,
    about: "Two legs, each forward or back. Pushing a forward leg moves it; pushing a back leg does nothing. Reward: distance covered." },
  { key: "grasp", name: "Find food and grasp it", pass: 0.75,
    about: "One object is in the room, and it is food, but only if the arm grasps it within reach. Walking is now automatic." },
  { key: "listen", name: "Listen", pass: 0.7,
    about: "Three objects. A tone plays: low = red, middle = green, high = blue. Only the colour it names is food; grasping another hurts." },
  { key: "read", name: "Read", pass: 0.6,
    about: "All objects are white with a letter on them: T, L or X. The tone names the letter; the fovea must read it." },
  { key: "write", name: "Write", pass: 0.8,
    about: "At the board, a tone plays. Draw its letter with two pen strokes: the same shapes it learned to read." },
];

// Inputs: retina, legs, cochlea, fovea, pen pad, at-board flag, then the fovea memory.
const BOARD_IN = RAYS * 3 + 2 + 3 + 25 + 6, MEM0 = BOARD_IN + 1, N_IN = MEM0 + 25, FAN_IN = 8;
// Game gains: tuning knobs so each stage learns in minutes, not measurements. A wrong grasp must
// cost more than a whole episode of step costs, or grabbing anything beats searching.
export const GAINS = { gamma: 0.96, lambda: 0.85, lrV: 0.05, lrP: 0.05, stepCost: 0.005, wrongCost: 0.6,
  hidden: 1000, maxSteps: 150, replay: 0.3, gate: 0.5, memory: 0.9,
  // Hippocampus (see class Hippocampus): every sleepEvery training episodes, replay sleepSize stored
  // transitions offline (0 = no sleep). Off by default: replay 0.1 with sleepEvery 20 passes as many
  // seeds, but greedy write in perform mode drops from 1.00 to about 0.65 (README "Sleep").
  // sleepActor also replays the actor: much faster, but it forgets more.
  memCap: 2048, sleepEvery: 0, sleepSize: 200, sleepActor: false,
  // k-winners-take-all on the hidden units (issue #82): keep only the kwta strongest, 0 = off.
  kwta: 0,
  // Timeouts of grasp, listen and read (issue #54, Pardo et al. 2018): 0 = treat as the task's end,
  // 1 = the same but sense the cut-off state first (RNG control), 2 = bootstrap from that state.
  // 2 passed 10/10 seeds vs the control's 9 but kept read lower, so it stays off (README "Timeouts").
  timeoutBootstrap: 0,
  // Innate orienting reflex (issue #83): a fixed, never-learned bias on the leg-push logits that
  // turns toward the brighter side of the retina, gain orient (0 = off). See README "Innate prior".
  orient: 0,
  // Perform mode only: skills that take the most likely action instead of sampling. Walk and write
  // gain from it; grasp, listen and read are searches, and a fixed policy turns the same way from
  // the same view forever (the best memoryless policy can be stochastic: Singh, Jaakkola and
  // Jordan 1994). See README "Perform mode".
  performGreedy: ["walk", "write"],
  // Context slots (issue #60): the brain is never told the task. It keeps `slots` prototypes of
  // pooled scene summaries and picks the gate row whose prototype matches the scene so far on every
  // channel within `vigilance`, adaptive-resonance style (Carpenter and Grossberg 1987). A full
  // store reclaims a slot used fewer than `minUses` times before it merges two contexts.
  slots: 8, vigilance: 0.35, minUses: 20 };
export const SCENE = 5;   // scene-summary channels: luminance, chroma, sound, fovea letter, at the board
// The scene code each of the five v3 stages produces (walk, grasp, listen, read, write), for World.migrate.
const V3_CODES = [[0, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 1, 1, 0, 0], [1, 0, 1, 1, 0], [0, 0, 1, 0, 1]];
const N_ACT = BODY.length + PEN.length;
const BODY_ACTS = [0, 1, 2, 3, 4], HABIT_ACTS = [0, 1, 4], PEN_ACTS = PEN.map((_, k) => BODY.length + k);
export const ACT_SETS = [BODY_ACTS, HABIT_ACTS, PEN_ACTS];

export class Brain {
  constructor(rand) {
    this.rand = rand;
    const HIDDEN = this.hidden = GAINS.hidden;
    this.nH = N_IN + HIDDEN;
    // Sparse random wiring, fixed and never learned. Each hidden unit is driven by one local patch
    // of a sense (a two-ray window of the retina, part of the fovea, or the body: legs, pen pad),
    // and sound scales that drive up or down: gain modulation, as attention scales V4 responses and
    // eye position scales parietal ones. Gains are random, so which tone goes with which colour or
    // letter is left for learning to find. (An additive mix learned the tone task far too slowly.)
    const RET = RAYS * 3, LEGS = [RET, RET + 1], COCH = [RET + 2, RET + 3, RET + 4];
    const FOV0 = RET + 5, BODY_IN = [...LEGS, ...[0, 1, 2, 3, 4, 5, 6].map(k => FOV0 + 25 + k)];
    const FOVEA_IN = Array.from({ length: 25 }, (_, k) => FOV0 + k), MEM_IN = FOVEA_IN.map(i => i - FOV0 + MEM0);
    this.idx = new Int32Array(HIDDEN * FAN_IN);
    this.wIn = new Float32Array(HIDDEN * FAN_IN);
    this.bias = new Float32Array(HIDDEN);
    const pick = list => list[Math.floor(rand() * list.length)];
    for (let j = 0; j < HIDDEN; j++) {
      const u = rand(), s = Math.floor(rand() * (RAYS - 1)) * 3;
      const patch = u < 0.5 ? [0, 1, 2, 3, 4, 5].map(k => s + k)
        : u < 0.72 ? FOVEA_IN : u < 0.85 ? MEM_IN : BODY_IN;
      for (let k = 0; k < FAN_IN; k++) {
        this.idx[j * FAN_IN + k] = k < 3 ? COCH[k] : pick(patch);
        this.wIn[j * FAN_IN + k] = (k < 3 ? 1.5 : 1) * gauss(rand);
      }
      this.bias[j] = -0.3 + 0.2 * gauss(rand);
    }
    // Task-context gating (a hypothesis-level model of prefrontal top-down gating; Masse, Grant and
    // Freedman 2018): each context slot switches off a fixed random share of the hidden units, so
    // each context mostly trains its own units and interferes less with the others. The raw senses
    // stay shared. gate[c * HIDDEN + j] = 1 if unit j is on in slot c. Which slot is in play is
    // inferred from the scene (infer), never given.
    this.gate = new Uint8Array(GAINS.slots * HIDDEN);
    for (let i = 0; i < this.gate.length; i++) this.gate[i] = rand() >= GAINS.gate ? 1 : 0;
    this.proto = new Float32Array(GAINS.slots * SCENE);   // each slot's prototype scene summary
    this.uses = new Int32Array(GAINS.slots);               // episodes committed to it; 0 = free
    this.v = new Float32Array(this.nH);           // critic
    this.P = new Float32Array(N_ACT * this.nH);   // actor
    this.ev = new Float32Array(this.nH);
    this.eP = new Float32Array(N_ACT * this.nH);
    this.dopamine = 0; this.pi = new Float32Array(N_ACT);
    this.learning = true;   // false = perform mode: act and compute dopamine, change no weight
    this.greedy = false;    // argmax instead of sampling; only set with learning off
  }

  encode(x, slot) {
    const h = new Float32Array(this.nH), gate = slot * this.hidden;
    h.set(x);
    let on = 0;
    for (let j = 0; j < this.hidden; j++) {
      if (!this.gate[gate + j]) continue;
      let gain = 1, drive = this.bias[j];   // the first three inputs are the cochlea bands
      for (let k = 0; k < FAN_IN; k++) {
        const v = this.wIn[j * FAN_IN + k] * x[this.idx[j * FAN_IN + k]];
        if (k < 3) gain += v; else drive += v;
      }
      if (drive > 0 && gain > 0) { h[N_IN + j] = drive * gain; on++; }
    }
    if (GAINS.kwta && on > GAINS.kwta) {
      const hid = h.subarray(N_IN), cut = hid.filter(v => v > 0).sort()[on - GAINS.kwta];   // typed-array sort is numeric
      for (let j = 0; j < this.hidden; j++) if (hid[j] < cut) hid[j] = 0;
      on = GAINS.kwta;
    }
    this.nActive = (this.nActive || 0) + on; this.nEncode = (this.nEncode || 0) + 1;   // sweep.mjs reports the mean
    return h;
  }

  match(z) {   // best: nearest used slot within vigilance on every channel; free; rare: least used under minUses; near: nearest used
    const m = { best: -1, free: -1, rare: -1, near: -1 };
    let bd = Infinity, nd = Infinity;
    for (let c = 0; c < GAINS.slots; c++) {
      if (!this.uses[c]) { if (m.free < 0) m.free = c; continue; }
      let d = 0, far = 0;
      for (let k = 0; k < SCENE; k++) { const e = Math.abs(z[k] - this.proto[c * SCENE + k]); d += e; if (e > far) far = e; }
      if (far <= GAINS.vigilance && d < bd) { bd = d; m.best = c; }
      if (d < nd) { nd = d; m.near = c; }
      if (this.uses[c] < GAINS.minUses && (m.rare < 0 || this.uses[c] < this.uses[m.rare])) m.rare = c;
    }
    return m;
  }

  infer(z) {   // the slot for scene summary z; changes nothing
    const m = this.match(z);
    return m.best >= 0 ? m.best : m.free >= 0 ? m.free : m.near;
  }

  commit(z) {   // end of a training episode: z joins its slot's prototype or founds a new one
    if (!this.learning) return;
    const m = this.match(z);
    const c = m.best >= 0 ? m.best : m.free >= 0 ? m.free : m.rare >= 0 ? m.rare : m.near;
    if (c !== m.best && c === m.rare) this.uses[c] = 0;   // reclaim a rarely used slot
    for (let k = 0; k < SCENE; k++) {
      const i = c * SCENE + k;
      this.proto[i] = this.uses[c] ? this.proto[i] + 0.05 * (z[k] - this.proto[i]) : z[k];
    }
    this.uses[c]++;
  }

  value(h) { let s = 0; for (let i = 0; i < this.nH; i++) s += this.v[i] * h[i]; return s; }

  policy(h, allowed, pi) {   // softmax over the allowed actions, written into pi (others 0)
    pi.fill(0);
    const turn = GAINS.orient ? GAINS.orient * orient(h) : 0;   // push left leg = turn left
    let mx = -Infinity;
    for (const a of allowed) {
      let s = a === 0 ? turn : a === 1 ? -turn : 0; const row = a * this.nH;
      for (let i = 0; i < this.nH; i++) s += this.P[row + i] * h[i];
      pi[a] = s; if (s > mx) mx = s;
    }
    let z = 0;
    for (const a of allowed) { pi[a] = Math.exp(pi[a] - mx); z += pi[a]; }
    for (const a of allowed) pi[a] /= z;
    return pi;
  }

  act(h, allowed) {   // sample from the policy; also lays down eligibility traces
    const pi = this.policy(h, allowed, this.pi);
    let u = this.rand(), choice = allowed[allowed.length - 1];
    for (const a of allowed) { u -= pi[a]; if (u <= 0) { choice = a; break; } }
    if (this.greedy) for (const a of allowed) if (pi[a] > pi[choice]) choice = a;
    this.h = h;
    if (!this.learning) return choice;
    const d = GAINS.gamma * GAINS.lambda;
    for (let i = 0; i < this.nH; i++) this.ev[i] = d * this.ev[i] + h[i];
    for (let a = 0; a < N_ACT; a++) {
      const g = allowed.includes(a) ? (a === choice) - pi[a] : 0, row = a * this.nH;
      for (let i = 0; i < this.nH; i++) this.eP[row + i] = d * this.eP[row + i] + g * h[i];
    }
    return choice;
  }

  learn(r, hNext, end = !hNext) {   // hNext null = episode over; end with hNext = cut off by a time limit
    const delta = r + (hNext ? GAINS.gamma * this.value(hNext) : 0) - this.value(this.h);
    this.dopamine = delta;   // still computed in perform mode, so the panel shows surprise
    if (!this.learning) return;
    // Step size over a running mean of |h|^2, not the current |h|^2: the trace holds past states,
    // and a small current one would blow the step up (it made the critic diverge).
    let hh = 0; for (let i = 0; i < this.nH; i++) hh += this.h[i] * this.h[i];
    this.hh = this.hh ? 0.99 * this.hh + 0.01 * hh : hh;
    const norm = 1 + this.hh;
    const av = GAINS.lrV / norm, ap = GAINS.lrP / norm;
    for (let i = 0; i < this.nH; i++) this.v[i] += av * delta * this.ev[i];
    for (let i = 0; i < this.eP.length; i++) this.P[i] += ap * delta * this.eP[i];
    if (end) { this.ev.fill(0); this.eP.fill(0); }
  }

  // Sleep: replay n stored transitions offline. TD(0) on the critic; with GAINS.sleepActor also a
  // policy-gradient step on the actor, over the action set stored with the transition and weighted
  // by rho = min(1, pi_now / pi_then) (truncated importance weight, as in Retrace: Munos et al.
  // 2016), because the policy has changed since the step was lived. The live traces are untouched.
  sleep(mem, n, rand) {
    const norm = 1 + (this.hh || 0), av = GAINS.lrV / norm, ap = GAINS.lrP / norm;
    const pi = new Float32Array(N_ACT);
    for (let k = 0; k < n; k++) {
      const e = mem.sample(rand);
      if (e < 0) return;
      const h = this.encode(mem.sense(e), mem.slot[e]), nx = mem.next(e);
      const delta = mem.r[e] + (nx >= 0 ? GAINS.gamma * this.value(this.encode(mem.sense(nx), mem.slot[nx])) : 0) - this.value(h);
      for (let i = 0; i < this.nH; i++) this.v[i] += av * delta * h[i];
      if (!GAINS.sleepActor) continue;
      const allowed = ACT_SETS[mem.set[e]], a = mem.a[e];
      this.policy(h, allowed, pi);
      const g = ap * delta * (pi[a] < mem.mu[e] ? pi[a] / mem.mu[e] : 1);   // mu can underflow to 0
      for (const b of allowed) {
        const gb = g * ((b === a) - pi[b]), row = b * this.nH;
        for (let i = 0; i < this.nH; i++) this.P[row + i] += gb * h[i];
      }
    }
  }
}

// Hippocampus-like episodic store: every training step is written once, as it happens (one-shot),
// and sleep replays a sample of it offline to the slow actor-critic (complementary learning
// systems: McClelland, McNaughton and O'Reilly 1995; sleep replay: Wilson and McNaughton 1994).
// A ring buffer of the last CAP transitions. Senses are quantised to bytes (step 1/200).
// end: 0 = the episode went on, 1 = terminal, 2 = cut by the time limit (never replayed: its
// target is ambiguous, #54). A transition is replayed only if it is terminal or its true successor
// (same episode, already stored) is still in the buffer.
export class Hippocampus {
  constructor(cap = GAINS.memCap) {
    this.cap = cap; this.n = 0; this.head = 0; this.epId = 0;
    this.x = new Uint8ClampedArray(cap * N_IN);   // clamps to [-0.05, 1.225]; senses stay in [-0.025, 1.025]
    this.slot = new Uint8Array(cap); this.a = new Uint8Array(cap); this.set = new Uint8Array(cap);
    this.end = new Uint8Array(cap); this.r = new Float32Array(cap); this.mu = new Float32Array(cap);
    this.ep = new Int32Array(cap);
  }

  store(x, slot, a, set, r, mu, end) {
    const e = this.head, o = e * N_IN;
    for (let k = 0; k < N_IN; k++) this.x[o + k] = (x[k] + 0.05) * 200;   // Uint8ClampedArray rounds and clamps
    this.slot[e] = slot; this.a[e] = a; this.set[e] = set; this.r[e] = r; this.mu[e] = mu; this.end[e] = end;
    this.ep[e] = this.epId;
    this.head = (e + 1) % this.cap; this.n = Math.min(this.n + 1, this.cap);
  }

  sense(e) {
    const x = new Float32Array(N_IN), o = e * N_IN;
    for (let k = 0; k < N_IN; k++) x[k] = this.x[o + k] / 200 - 0.05;
    return x;
  }

  next(e) {   // index of the stored successor, or -1 (terminal, cut, or not stored)
    if (this.end[e] !== 0) return -1;
    const j = (e + 1) % this.cap;
    return j !== this.head && j < this.n && this.ep[j] === this.ep[e] ? j : -1;
  }

  sample(rand) {   // a uniformly drawn replayable transition, or -1
    for (let t = 0; t < 50 && this.n; t++) {
      const e = Math.floor(rand() * this.n);
      if (this.end[e] === 1 || this.next(e) >= 0) return e;
    }
    return -1;
  }

  // Saved as it was at `at` = {head, n, epId}, the start of the current episode: a loaded world
  // plays that episode again and stores its steps again.
  toJSON(at) {
    const KEYS = ["x", "slot", "a", "set", "end", "r", "mu", "ep"], o = { cap: this.cap, ...at };
    for (const k of KEYS) o[k] = toB64(this[k]);
    return o;
  }

  static fromJSON(o) {   // null if o is not a valid store of this brain's shape
    const m = new Hippocampus();
    if (!o || o.cap !== m.cap || ![o.head, o.n, o.epId].every(Number.isInteger) || o.n < 0 || o.n > m.cap
      || o.head < 0 || o.head >= m.cap || (o.n < m.cap && o.head !== o.n)) return null;
    for (const k of ["x", "slot", "a", "set", "end", "r", "mu", "ep"]) {
      let arr;
      try { arr = fromB64(o[k], m[k].constructor); } catch { return null; }
      if (arr.length !== m[k].length) return null;
      m[k] = arr;
    }
    for (let e = 0; e < o.n; e++)
      if (m.slot[e] >= GAINS.slots || m.set[e] >= ACT_SETS.length || !ACT_SETS[m.set[e]].includes(m.a[e]) || m.end[e] > 2
        || !Number.isFinite(m.r[e]) || !(m.mu[e] >= 0 && m.mu[e] <= 1)) return null;
    Object.assign(m, { head: o.head, n: o.n, epId: o.epId });
    return m;
  }
}

function toB64(a) {
  const u = new Uint8Array(a.buffer, a.byteOffset, a.byteLength);
  let s = "";
  for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode(...u.subarray(i, i + 8192));
  return btoa(s);
}
function fromB64(s, Type) {
  const bin = atob(s), u = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
  if (u.length % Type.BYTES_PER_ELEMENT) throw new Error("bad length");
  return new Type(u.buffer);
}

// Left minus right object salience on the retina (h starts with the senses). A wall reads at most
// 0.2 in every channel, so max(r, g, b) - 0.2 > 0 only for an object; rays past the middle look left.
export function orient(x) {
  let t = 0;
  for (let i = 0; i < RAYS; i++) {
    const s = Math.max(x[i * 3], x[i * 3 + 1], x[i * 3 + 2]) - 0.2;
    if (s > 0) t += Math.sign(i - (RAYS - 1) / 2) * s;
  }
  return t;
}

// One step's scene, thresholded to 0/1 per channel: something white (luminance), something coloured
// (chroma), a tone, a letter on the fovea, the board. Walls read 0.2 grey, so they set neither.
// ponytail: the thresholds were picked knowing the five scenes; a continuous z is the A/B to run.
export function scene(x) {
  let lum = 0, chr = 0;
  for (let i = 0; i < RAYS; i++) {
    const r = x[i * 3], g = x[i * 3 + 1], b = x[i * 3 + 2], lo = Math.min(r, g, b);
    lum = Math.max(lum, lo); chr = Math.max(chr, Math.max(r, g, b) - lo);
  }
  const C = RAYS * 3 + 2, F = RAYS * 3 + 5;
  return [lum > 0.3, chr > 0.1, Math.max(x[C], x[C + 1], x[C + 2]) > 0.5,
    x.subarray(F, F + 25).some(v => v > 0.1), x[BOARD_IN] > 0.5].map(Number);
}

function gauss(rand) { return Math.sqrt(-2 * Math.log(rand() + 1e-12)) * Math.cos(2 * Math.PI * rand()); }

export class World {
  constructor(seed = 1) {
    this.rand = rng(seed);
    this.brain = new Brain(this.rand);
    this.hippo = new Hippocampus();
    this.stage = 0; this.playing = 0; this.episode = 0; this.log = []; this.graduated = false;
    this.windows = STAGES.map(() => []);   // last 50 outcomes per stage
    this.events = [];   // for the UI: {type: "tone"|"grasp"|"stroke"|"stage"|"graduated", ...}
    this.task = -1; this.perf = { n: 0, ok: 0, scene: {} };   // perform mode: the locked skill (STAGES.length = any), and its score
    this.reset();
  }

  // The stage being trained is `stage`; the episode being played is `playing`, which is an earlier
  // stage on review episodes (see finish).
  get mode() { return STAGES[this.playing].key; }
  get window() { return this.windows[this.stage]; }

  reset() {
    // Free play (perform "any"): a random scene each episode; the brain must find its skill itself.
    if (this.task === STAGES.length) {
      this.playing = Math.floor(this.rand() * STAGES.length);
      this.brain.greedy = GAINS.performGreedy.includes(this.mode);
    }
    const R = this.rand, m = this.mode;
    this.board = m === "write";   // the world puts the creature at the board: a fact about the scene
    this.episodeRand = R.state;   // a saved brain restarts the episode it was saved in from here
    const H = this.hippo;
    this.memAt = { head: H.head, n: H.n, epId: H.epId++ };   // and its episodic store from here
    this.pos = [ARENA / 2 + (R() - 0.5) * 2, ARENA / 2 + (R() - 0.5) * 2];
    this.heading = R() * 2 * Math.PI;
    this.legs = [1, 1];   // 1 = forward (ready to push), 0 = back
    this.t = 0; this.dist = 0; this.held = -1; this.pad = []; this.ret = 0; this.memory = new Float32Array(25);
    this.z = new Float32Array(SCENE);   // the scene summary so far: running max of scene(x), see sense
    this.objects = [];
    // The grasp stage has one object of a random colour, so it teaches "approach and grasp", not
    // "red is food": a colour habit there made the listen stage perseverate on red.
    const count = m === "walk" || m === "write" ? 0 : m === "grasp" ? 1 : 3;
    const pick = Math.floor(R() * 3);
    while (this.objects.length < count) {
      const p = [0.8 + R() * (ARENA - 1.6), 0.8 + R() * (ARENA - 1.6)];
      if (Math.hypot(p[0] - this.pos[0], p[1] - this.pos[1]) < 2) continue;
      if (this.objects.some(o => Math.hypot(o.pos[0] - p[0], o.pos[1] - p[1]) < 1.6)) continue;
      const i = this.objects.length;
      this.objects.push({ pos: p, color: m === "read" ? [1, 1, 1] : COLORS[count === 1 ? pick : i], letter: m === "read" ? i : -1 });
    }
    this.target = m === "grasp" ? 0 : Math.floor(R() * 3);
    this.tone = m === "listen" || m === "read" || m === "write" ? this.target : -1;
    if (this.tone >= 0) this.events.push({ type: "tone", tone: this.tone });
    this.x = this.sense();
    this.h = this.brain.encode(this.x, this.slot = this.context());
  }

  // The context slot comes from what the senses have shown this episode, not from the task.
  context() { return this.brain.infer(this.z); }

  sense() {
    const x = new Float32Array(N_IN), R = this.rand;
    this.retina = new Float32Array(RAYS * 3); this.fovea = new Float32Array(25);
    if (!this.board) {
      for (let i = 0; i < RAYS; i++) {
        const a = this.heading + FOV * (i / (RAYS - 1) - 0.5), dx = Math.cos(a), dy = Math.sin(a);
        let best = this.wallDist(dx, dy), hit = null;
        for (const o of this.objects) {
          const t = rayCircle(this.pos, dx, dy, o.pos, OBJ_R);
          if (t !== null && t < best) { best = t; hit = o; }
        }
        const near = 1 / (1 + 0.35 * best), col = hit ? hit.color : [0.2, 0.2, 0.2];
        for (let c = 0; c < 3; c++) this.retina[i * 3 + c] = col[c] * near;
      }
      // Fovea: the sharp centre of the eye resolves the letter on the nearest object in a
      // narrow central cone; the coarse retina above cannot.
      let fd = Infinity; this.fixated = -1;
      this.objects.forEach((o, i) => {
        const dx = o.pos[0] - this.pos[0], dy = o.pos[1] - this.pos[1], d = Math.hypot(dx, dy);
        if (Math.abs(angleDiff(Math.atan2(dy, dx), this.heading)) < FOVEA + OBJ_R / d && d < fd) { fd = d; this.fixated = i; }
      });
      const o = this.objects[this.fixated];
      if (o && o.letter >= 0) {
        const g = glyph(LETTERS[o.letter][1]), near = 1 / (1 + 0.35 * fd);
        for (let k = 0; k < 25; k++) this.fovea[k] = g[k] * near;
      }
    }
    // Fovea memory: a decaying trace of the last letter seen, so it can still hold the letter a
    // few steps after the gaze has moved on (persistent activity, as in prefrontal working memory).
    // Each leg push turns 0.3 rad, wider than the fovea, so a letter is in view only for a step or
    // two. (A "look" saccade action was tried too: it made reading less reliable across seeds.)
    for (let k = 0; k < 25; k++) this.memory[k] = Math.max(GAINS.memory * this.memory[k], this.fovea[k]);
    x.set(this.retina, 0);
    x[RAYS * 3] = this.legs[0]; x[RAYS * 3 + 1] = this.legs[1];
    if (this.tone >= 0) x[RAYS * 3 + 2 + this.tone] = 1;                 // cochlea: one band per tone
    for (let k = 0; k < 3; k++) x[RAYS * 3 + 2 + k] += 0.05 * (R() - 0.5);
    x.set(this.fovea, RAYS * 3 + 5);
    for (const s of this.pad) x[RAYS * 3 + 30 + s] = 1;                  // what the pen has drawn
    x[BOARD_IN] = this.board ? 1 : 0;                                     // at the board or not
    x.set(this.memory, MEM0);
    const s = scene(x);
    for (let k = 0; k < SCENE; k++) if (s[k] > this.z[k]) this.z[k] = s[k];
    return x;
  }

  wallDist(dx, dy) {
    const tx = dx > 0 ? (ARENA - this.pos[0]) / dx : dx < 0 ? -this.pos[0] / dx : Infinity;
    const ty = dy > 0 ? (ARENA - this.pos[1]) / dy : dy < 0 ? -this.pos[1] / dy : Infinity;
    return Math.min(tx, ty);
  }

  step() {
    const b = this.brain, m = this.mode;
    // Once walking is learned the gait is automatic (a practised skill runs as a habit, as spinal
    // pattern generators and the cerebellum take over): a pushed leg swings forward by reflex,
    // and later stages only choose which leg to push, or to grasp. The habit comes from the
    // brain's development and the action set from the body's situation, not from the task (#61).
    const habit = this.stage > 0 || this.graduated;
    if (habit) this.legs = [1, 1];
    if (this.task >= 0) (this.perf.scene[m] ??= { n: 0, ok: 0, slots: Array(GAINS.slots).fill(0) }).slots[this.slot]++;
    const set = this.board ? 2 : habit ? 1 : 0;
    const a = b.act(this.h, ACT_SETS[set]), mu = b.pi[a];
    this.lastAction = a;
    let r = m === "walk" ? 0 : -GAINS.stepCost, done = false, success = false;
    if (m === "write") {
      this.pad.push(a - BODY.length);
      this.events.push({ type: "stroke", stroke: a - BODY.length });
      if (this.pad.length === 2) {
        const want = LETTERS[this.target][1];
        success = this.pad.every(s => want.includes(s)) && this.pad[0] !== this.pad[1];
        r = success ? 1 : 0; done = true;
      }
    } else if (a < 2) {   // push a leg: moves only if that leg was forward
      if (this.legs[a]) {
        this.legs[a] = 0;
        this.heading += a === 0 ? 0.3 : -0.3;
        const old = [...this.pos];
        this.pos[0] = clamp(this.pos[0] + 0.22 * Math.cos(this.heading), 0.3, ARENA - 0.3);
        this.pos[1] = clamp(this.pos[1] + 0.22 * Math.sin(this.heading), 0.3, ARENA - 0.3);
        for (const o of this.objects) {   // objects are solid
          const d = Math.hypot(this.pos[0] - o.pos[0], this.pos[1] - o.pos[1]);
          if (d < OBJ_R + 0.25) this.pos = old;
        }
        const moved = Math.hypot(this.pos[0] - old[0], this.pos[1] - old[1]);
        this.dist += moved;
        if (m === "walk") r += 2 * moved;
      }
    } else if (a < 4) {
      this.legs[a - 2] = 1;
    } else {   // grasp: whatever is in reach and roughly ahead
      let got = -1;
      this.objects.forEach((o, i) => {
        const dx = o.pos[0] - this.pos[0], dy = o.pos[1] - this.pos[1];
        const off = Math.abs(angleDiff(Math.atan2(dy, dx), this.heading));
        if (Math.hypot(dx, dy) < REACH + OBJ_R && off < 0.6) got = i;
      });
      this.events.push({ type: "grasp", object: got });
      if (got >= 0 && m !== "walk") {
        this.held = got; done = true; success = got === this.target;
        r = success ? 1 : -GAINS.wrongCost;
      }
    }
    this.t++;
    const limit = m === "walk" ? 60 : GAINS.maxSteps, terminal = done;
    if (!done && this.t >= limit) {
      done = true;
      if (m === "walk") success = this.dist / this.t > 0.08;
    }
    this.ret += r;
    if (this.task < 0) this.hippo.store(this.x, this.slot, a, set, r, mu, terminal ? 1 : done ? 2 : 0);   // perform mode stores nothing
    if (done && !terminal && m !== "walk" && GAINS.timeoutBootstrap) {
      const x = this.sense();
      b.learn(r, GAINS.timeoutBootstrap === 2 ? b.encode(x, this.context()) : null, true);
      this.finish(success);
    } else if (done) {
      b.learn(r, null);
      this.finish(success);
    } else {
      this.x = this.sense();
      this.h = b.encode(this.x, this.slot = this.context());
      b.learn(r, this.h);
    }
    return { action: a, reward: r, done, success };
  }

  finish(success) {
    if (this.task >= 0) {   // perform mode: score it, leave the curriculum alone
      const s = this.perf.scene[this.mode];
      this.perf.n++; this.perf.ok += success ? 1 : 0; s.n++; s.ok += success ? 1 : 0;
      this.reset();
      return;
    }
    this.brain.commit(this.z);
    this.episode++;
    const win = this.windows[this.playing];
    win.push(success ? 1 : 0);
    if (win.length > 50) win.shift();
    this.log.push({ stage: this.playing, success, steps: this.t, ret: this.ret });
    const rate = this.successRate();
    if (!this.graduated && this.playing === this.stage && win.length === 50 && rate >= STAGES[this.stage].pass) {
      this.passedRate = rate;
      if (this.stage < STAGES.length - 1) {
        this.events.push({ type: "stage", from: this.stage, episodes: this.episode, rate });
        this.stage++; this.windows[this.stage] = [];
      } else {
        this.graduated = true;
        this.events.push({ type: "graduated", episodes: this.episode });
      }
    }
    // Interleaved replay: learning a new skill with one network overwrites the old ones
    // (catastrophic forgetting; without this, grasp/listen/read fell to chance once it learned to
    // write). So some episodes rehearse an earlier skill, as hippocampal replay interleaves old
    // experience with new (complementary learning systems). Walking is not replayed: it is an
    // automatic habit by then, and replaying its distance reward fought against stopping to grasp.
    // After graduation it cycles grasp, listen, read and write.
    if (this.graduated) this.playing = this.playing % (STAGES.length - 1) + 1;
    else this.playing = this.stage > 1 && this.rand() < GAINS.replay ? 1 + Math.floor(this.rand() * (this.stage - 1)) : this.stage;
    // Sleep: offline replay from the episodic store, between episodes.
    if (GAINS.sleepEvery && this.episode % GAINS.sleepEvery === 0) this.brain.sleep(this.hippo, GAINS.sleepSize, this.rand);
    this.reset();
  }

  setStage(s) { this.stage = this.playing = s; this.windows[s] = []; this.reset(); }

  // Perform mode: use the brain with learning off, every episode on one skill, or on a random scene
  // with "any" (free play). No weight, window, log or stage changes, so a saved brain can be used or
  // checked without training it further. perf.scene[key] = {n, ok, slots: steps per context slot}.
  // perform(null) goes back to training on `stage`.
  perform(key, greedy = GAINS.performGreedy.includes(key)) {
    const b = this.brain;
    b.ev.fill(0); b.eP.fill(0);   // a half-done training episode's traces must not carry over
    if (key === null) {
      this.task = -1; b.learning = true; b.greedy = false; this.playing = this.stage;
    } else {
      const s = key === "any" ? STAGES.length : STAGES.findIndex(st => st.key === key);
      if (s < 0) throw new Error(`unknown skill "${key}"; valid: ${STAGES.map(st => st.key).join(", ")}, any`);
      this.task = s; if (s < STAGES.length) this.playing = s;
      b.learning = false; b.greedy = greedy; this.perf = { n: 0, ok: 0, scene: {} };
    }
    this.reset();
  }

  // Save and load: weights (including the fixed random wiring) plus curriculum progress. A loaded
  // world replays the current episode from its start, so it acts exactly as the saved one would
  // have from that point. JSON.stringify(world) calls toJSON.
  toJSON() {
    const b = this.brain, arr = a => Array.from(a);
    // A save made while performing resumes training on its own stage.
    return { version: 4, rand: this.episodeRand, stage: this.stage, playing: this.task >= 0 ? this.stage : this.playing, episode: this.episode,
      graduated: this.graduated, passedRate: this.passedRate, windows: this.windows,
      brain: { idx: arr(b.idx), wIn: arr(b.wIn), bias: arr(b.bias), gate: arr(b.gate), v: arr(b.v), P: arr(b.P), hh: b.hh,
        proto: arr(b.proto), uses: arr(b.uses) },
      hippo: this.hippo.toJSON(this.memAt) };
  }

  // Old saves keep loading as the brain grows (#63), in a fixed order: v3 to v4, more slots, more
  // stages. A step that cannot read its input leaves it unchanged, so fromJSON's checks reject it.
  // Never across an N_IN change: new senses make a new brain, not a migrated one.
  static migrate(o) {
    if (!o || !o.brain || !Array.isArray(o.brain.gate) || !Array.isArray(o.windows)) return o;
    o = { ...o, brain: { ...o.brain } };
    const b = o.brain, H = GAINS.hidden, spare = rng(0x5107);
    // upgradeV3: the told gate had one row per stage, in STAGES order. Each becomes a slot whose
    // prototype is the scene code that stage produces (measured), with enough uses to keep it.
    if (o.version === 3 && b.gate.length === V3_CODES.length * H) {
      Object.assign(b, { proto: V3_CODES.flat(), uses: V3_CODES.map(() => 50) });
      o.version = 4;
    }
    // growSlots: fewer slots than GAINS.slots gets fresh free rows appended; slot ids stay valid.
    const n = Array.isArray(b.uses) ? b.uses.length : 0;
    if (o.version === 4 && n < GAINS.slots && b.gate.length === n * H && Array.isArray(b.proto) && b.proto.length === n * SCENE) {
      const add = GAINS.slots - n;
      b.gate = b.gate.concat(Array.from({ length: add * H }, () => spare() >= GAINS.gate ? 1 : 0));
      b.proto = b.proto.concat(Array(add * SCENE).fill(0));
      b.uses = b.uses.concat(Array(add).fill(0));
    }
    // growStages: one empty window per new stage; a graduated brain resumes at the first new one.
    const s = o.windows.length;
    if (s < STAGES.length) {
      o.windows = o.windows.concat(Array.from({ length: STAGES.length - s }, () => []));
      if (o.graduated) Object.assign(o, { graduated: false, stage: s, playing: s });
    }
    return o;
  }

  static fromJSON(o) {   // o comes from a user's file: check its shape before trusting it
    o = World.migrate(o);   // first: ob below must point at the migrated brain
    const w = new World(1), b = w.brain, ob = o && o.brain;
    const KEYS = ["idx", "wIn", "bias", "gate", "v", "P", "proto", "uses"];
    const ok = o && o.version === 4 && ob && Array.isArray(o.windows) && o.windows.length === STAGES.length && o.windows.every(Array.isArray)
      && Number.isInteger(o.stage) && o.stage >= 0 && o.stage < STAGES.length
      && Number.isInteger(o.playing) && o.playing >= 0 && o.playing < STAGES.length
      && KEYS.every(k => Array.isArray(ob[k]) && ob[k].length === b[k].length && ob[k].every(Number.isFinite))
      && ob.idx.every(i => Number.isInteger(i) && i >= 0 && i < N_IN) && ob.gate.every(g => g === 0 || g === 1)
      && ob.proto.every(p => p >= 0 && p <= 1) && ob.uses.every(u => Number.isInteger(u) && u >= 0)
      && (ob.hh === undefined || Number.isFinite(ob.hh));
    // An older save without an episodic store loads with an empty one.
    const hippo = o && o.hippo === undefined ? new Hippocampus() : Hippocampus.fromJSON(o && o.hippo);
    if (!ok || !hippo) throw new Error("not a Brain World save, or saved by an older version or with a different brain size");
    w.hippo = hippo;
    for (const k of KEYS) b[k].set(ob[k]);
    b.hh = ob.hh;
    Object.assign(w, { stage: o.stage, playing: o.playing, episode: o.episode | 0, graduated: !!o.graduated,
      passedRate: o.passedRate, windows: o.windows.map(win => win.slice(-50).map(x => x ? 1 : 0)), events: [] });
    w.rand.state = o.rand >>> 0;
    w.reset();
    return w;
  }

  successRate(s = this.stage) {
    const w = this.windows[s];
    return w.length ? w.reduce((p, q) => p + q, 0) / w.length : 0;
  }
}

function rayCircle(p, dx, dy, c, r) {
  const fx = p[0] - c[0], fy = p[1] - c[1];
  const bq = fx * dx + fy * dy, cq = fx * fx + fy * fy - r * r, disc = bq * bq - cq;
  if (disc < 0) return null;
  const t = -bq - Math.sqrt(disc);
  return t > 0 ? t : null;
}
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const angleDiff = (a, b) => Math.atan2(Math.sin(a - b), Math.cos(a - b));
