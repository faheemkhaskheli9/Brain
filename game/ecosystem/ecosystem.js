// Brain Ecosystem core: insects, animals (foxes) and humans share one world, and every individual
// has its own brain that learns from its own experience. No DOM here, so node can run it headlessly
// (test_ecosystem.mjs) and index.html can draw it in 3D.
//
// Every brain is the same kind of learner as Brain World's (game/world/brain.js): a fixed random
// sparse expansion of the senses (insect mushroom body, cerebellar granule cells) feeds an
// actor-critic. Dopamine is the TD error; eligibility traces tag recently used synapses; weights
// change only where trace meets dopamine (a three-factor rule). No backprop.
//
// The species differ where the knowledge base says brains differ (function/innate-priors-and-
// infant-learning.md, anatomy/comparative-and-evolutionary-neuroscience.md):
//   insects: a small brain, strong inherited reflexes (a genome), short lives, no memory;
//   foxes:   a larger brain, a fading working memory of where prey was last seen;
//   humans:  the largest brain, weak reflexes, a place memory of where food was (hippocampus-like
//            map) and social learning: they tell each other where food grows (hypothesis-level).
// Learned weights are never inherited: a newborn starts with its parent's mutated genome only.
// Sizes, rates and costs below are game gains (tuning knobs), not measurements.

export function rng(seed) {   // mulberry32: seeded, so runs are repeatable
  const f = () => {
    const a = f.state = (f.state + 0x6D2B79F5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), a | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  f.state = seed >>> 0;
  return f;
}
function gauss(rand) { return Math.sqrt(-2 * Math.log(rand() + 1e-12)) * Math.cos(2 * Math.PI * rand()); }

export const SIZE = 50;   // the world is SIZE x SIZE, walled
// What a creature can sense. Empty flowers and bare bushes have no smell or colour, so are not sensed.
export const KINDS = ["red flower", "blue flower", "berry bush", "insect", "fox", "human", "wall"];
// Cues: the kinds, plus a remembered place (a fox's last prey seen, a human's best food spot), sensed
// like a thing in one sector at a strength that fades.
export const CUES = [...KINDS, "remembered food"];
const MEMCUE = KINDS.length;
export const SECTORS = 6;                 // senses split into six 60-degree sectors around the head
export const ACTIONS = ["forward", "turn left", "turn right"];   // every action moves (a rest action became a trap)
const NC = CUES.length, N_SENSE = SECTORS * NC, ENERGY = N_SENSE, BIAS = ENERGY + 1;
export const N_IN = BIAS + 1;             // cues per sector, energy, bias

export const SPECIES = {
  insect: { hidden: 60, k: 6, speed: 0.35, turn: 0.6, cost: 0.004, view: 6, lr: 0.2,
    maxAge: 3000, cap: 40, min: 12, start: 30, birthAge: 300,
    genome: [0.5, 0.5, 0, 0, -2, -0.5, -1, 0] },  // inherited pull (+) or push (-) toward each CUE
  fox: { hidden: 200, k: 20, speed: 0.5, turn: 0.5, cost: 0.006, view: 10, lr: 0.25,
    maxAge: 6000, cap: 8, min: 2, start: 5, birthAge: 800,
    genome: [0, 0, 0, 0.5, 0, 0, -1, 0.5] },
  human: { hidden: 400, k: 40, speed: 0.4, turn: 0.5, cost: 0.003, view: 12, lr: 0.25,
    maxAge: 10000, cap: 10, min: 3, start: 6, birthAge: 1500,
    genome: [0, 0, 0.2, 0, 0, 0, -1, 0.5] },
};
export const GAINS = { gamma: 0.95, lambda: 0.8, fanIn: 8, mutate: 0.1, rich: 0.5, poor: 0,
  berry: 0.6, prey: 0.8, scare: 0.03, flowerRegrow: 80, bushRegrow: 150, season: 4000,
  tell: 0.02, cueLr: 0.5, cueForget: 0.999, socialView: 10, grid: 8, maxEnergy: 3, birthEnergy: 1.8 };

// Innate reflex template: what each sector pulls toward. Thing ahead: go forward; on the left: turn
// left; on the right: turn right; behind: turn. A negative genome gain turns a pull into a push.
const TEMPLATE = [[1, 0, 0], [0, 1, 0], [0, 1, 0], [0, 0.5, 0.5], [0, 0, 1], [0, 0, 1]];

export class Brain {
  constructor(sp, rand, genome) {
    const p = SPECIES[sp], F = N_IN + p.hidden;
    this.sp = sp; this.nH = p.hidden; this.k = p.k; this.lr = p.lr; this.F = F;
    this.genome = Float32Array.from(genome);
    // Learned valence of each CUE, added to the inborn pull. Dopamine at contact with a thing (a meal,
    // an empty flower, a bite) moves the valence of that kind, as dopamine neurons change mushroom-body
    // output synapses for the odour present at reward (learning/brain-inspired-learning-algorithms.md).
    // One number per cue, so it learns in a few meals, it can reverse, and it fades.
    this.valence = new Float32Array(NC);
    // Fixed random expansion: each hidden unit sums fanIn random inputs. Never learns.
    this.idx = new Int32Array(p.hidden * GAINS.fanIn); this.w = new Float32Array(p.hidden * GAINS.fanIn);
    for (let i = 0; i < this.idx.length; i++) { this.idx[i] = Math.floor(rand() * N_IN); this.w[i] = gauss(rand); }
    this.wV = new Float32Array(F); this.wP = new Float32Array(ACTIONS.length * F);
    this.eV = new Float32Array(F); this.eP = new Float32Array(ACTIONS.length * F);
    this.f = new Float32Array(F); this.pre = new Float32Array(p.hidden);
    this.pi = new Float32Array(ACTIONS.length);
    this.prev = null;     // { v } of the last step, for the TD error
    this.dopamine = 0;
  }
  // Features: the raw senses plus a k-winners-take-all sparse code of the expansion.
  features(x, out = this.f) {
    out.fill(0); out.set(x);
    const H = this.nH, fan = GAINS.fanIn, pre = this.pre;
    for (let j = 0; j < H; j++) { let s = 0; for (let i = 0; i < fan; i++) s += this.w[j * fan + i] * x[this.idx[j * fan + i]]; pre[j] = s; }
    // Exactly k winners (ties broken by index), so a quiet scene does not switch every unit on.
    const thr = kth(pre, this.k, this.tmp || (this.tmp = new Float32Array(H)));
    let left = this.k;
    for (let j = 0; j < H; j++) if (pre[j] > thr) { out[N_IN + j] = 1; left--; }
    for (let j = 0; j < H && left > 0; j++) if (pre[j] === thr) { out[N_IN + j] = 1; left--; }
    return out;
  }
  clone() {   // a copy for testing, so the original keeps its traces
    const b = Object.assign(Object.create(Brain.prototype), this);
    for (const k of ["genome", "valence", "idx", "w", "wV", "wP", "eV", "eP", "f", "pre", "pi"]) b[k] = this[k].slice();
    b.prev = null; b.tmp = null; return b;
  }
  innate(x, a) {   // reflex: inborn (genome) plus learned (valence) pull per kind x sector template
    let s = 0;
    for (let sec = 0; sec < SECTORS; sec++) for (let k = 0; k < NC; k++) s += (this.genome[k] + this.valence[k]) * x[sec * NC + k] * TEMPLATE[sec][a];
    return 2 * s;
  }
  policy(x, f, out = this.pi) {
    const F = this.F; let m = -Infinity;
    for (let a = 0; a < ACTIONS.length; a++) {
      let s = this.innate(x, a);
      for (let i = 0; i < F; i++) if (f[i]) s += this.wP[a * F + i] * f[i];
      out[a] = Math.max(-20, Math.min(20, s)); m = Math.max(m, out[a]);
    }
    let z = 0; for (let a = 0; a < out.length; a++) z += (out[a] = Math.exp(out[a] - m));
    for (let a = 0; a < out.length; a++) out[a] /= z;
    return out;
  }
  value(f) { let s = 0; for (let i = 0; i < this.F; i++) if (f[i]) s += this.wV[i] * f[i]; return s; }
  norm(f) { let n = 0; for (let i = 0; i < this.F; i++) n += Math.abs(f[i]); return Math.max(1, n); }
  // One step: learn from the reward that followed the last action, then pick the next action.
  // touched: the KIND contacted last step (food, an empty flower, a bite), or -1.
  step(x, r, rand, learn = true, touched = -1) {
    const f = this.features(x), v = this.value(f), F = this.F;
    if (this.prev) {
      const delta = r + GAINS.gamma * v - this.prev.v;   // dopamine: reward prediction error
      this.dopamine = delta;
      if (learn) this.learn(delta, touched);
    }
    const pi = this.policy(x, f);
    let u = rand(), act = 0; while (act < pi.length - 1 && (u -= pi[act]) > 0) act++;
    const dec = GAINS.gamma * GAINS.lambda;   // eligibility traces decay, then tag what was just used
    for (let i = 0; i < F; i++) {
      this.eV[i] = dec * this.eV[i] + f[i];
      if (f[i]) for (let a = 0; a < pi.length; a++) this.eP[a * F + i] = dec * this.eP[a * F + i] + ((a === act) - pi[a]) * f[i];
      else for (let a = 0; a < pi.length; a++) this.eP[a * F + i] *= dec;
    }
    // Slow forgetting: the inborn pull comes back, so a soured food gets tried again.
    for (let k = 0; k < NC; k++) this.valence[k] *= GAINS.cueForget;
    this.prev = { v, n: this.norm(f) };
    return act;
  }
  learn(delta, touched) {   // the three-factor update: learning rate x dopamine x eligibility trace
    const a = this.lr * delta / this.prev.n, F = this.F;
    for (let i = 0; i < F; i++) this.wV[i] += a * this.eV[i];
    for (let i = 0; i < this.wP.length; i++) this.wP[i] += a * this.eP[i];
    // Valence moves only for the thing touched. Dips between contacts (prey that got away) would sour
    // the cue, and crediting every cue in view would make everything attractive.
    if (touched >= 0) this.valence[touched] = Math.max(-3, Math.min(3, this.valence[touched] + GAINS.cueLr * delta));
  }
  end(r, learn = true, touched = -1) {   // death: the last reward with no future
    if (!this.prev) return;
    const delta = r - this.prev.v; this.dopamine = delta;
    if (learn) this.learn(delta, touched);
    this.prev = null;
  }
}

let nextId = 1;
export class Creature {
  constructor(sp, x, y, rand, genome, gen = 0) {
    this.id = nextId++; this.sp = sp; this.x = x; this.y = y; this.h = rand() * 2 * Math.PI;
    this.energy = 1; this.age = 0; this.gen = gen; this.meals = 0; this.alive = true;
    this.brain = new Brain(sp, rand, genome);
    this.act = 0; this.reward = 0;
    this.dopa = new Float32Array(100); this.dopaAt = 0;   // ring buffer for the inspector
    this.touched = -1;
    this.mem = { x: 0, y: 0, s: 0 };                      // fox: last prey seen (world frame)
    this.map = sp === "human" ? new Float32Array(GAINS.grid * GAINS.grid) : null;   // human: food per cell
    this.ate = false;
  }
}

export class World {
  constructor(seed = 1, opts = {}) {
    this.seed = seed; this.rand = rng(seed); this.t = 0;
    this.learn = opts.learn ?? true; this.social = opts.social ?? true; this.memory = opts.memory ?? true;
    this.richColor = 0;   // which flower colour carries rich nectar this season
    this.plants = []; this.creatures = []; this.events = [];
    this.stats = {}; for (const sp in SPECIES) this.stats[sp] = { food: 0, steps: 0, rate: 0, births: 0, deaths: 0, eaten: 0, lastFood: 0 };
    this.visits = [0, 0];   // insect visits to the rich, poor colour in the current season's second half
    this.seasonVisits = []; this.flowerVisits = [0, 0];   // the same per past season, and over all time
    const R = this.rand;
    for (let i = 0; i < 70; i++) this.plants.push({ kind: i % 2, x: 2 + R() * (SIZE - 4), y: 2 + R() * (SIZE - 4), full: true, t: 0 });
    // Berry bushes grow in clumps, so remembering where they are pays.
    for (let c = 0; c < 5; c++) {
      const cx = 8 + R() * (SIZE - 16), cy = 8 + R() * (SIZE - 16);
      for (let i = 0; i < 6; i++) this.plants.push({ kind: 2, x: cx + gauss(R) * 2, y: cy + gauss(R) * 2, full: true, t: 0 });
    }
    // opts.pop = { insect: n, ... } overrides the starting and minimum counts (0 removes a species).
    this.pop = {}; for (const sp in SPECIES) this.pop[sp] = opts.pop?.[sp] ?? SPECIES[sp].start;
    this.min = {}; for (const sp in SPECIES) this.min[sp] = opts.pop ? this.pop[sp] : SPECIES[sp].min;
    this.births = opts.births ?? true;
    for (const sp in SPECIES) for (let i = 0; i < this.pop[sp]; i++) this.spawn(sp);
  }
  spawn(sp, parent = null) {
    const R = this.rand, p = SPECIES[sp];
    const genome = parent ? Array.from(parent.brain.genome, g => g + GAINS.mutate * gauss(R)) : p.genome;
    const x = parent ? parent.x + gauss(R) : 2 + R() * (SIZE - 4), y = parent ? parent.y + gauss(R) : 2 + R() * (SIZE - 4);
    const c = new Creature(sp, clamp(x), clamp(y), R, genome, parent ? parent.gen + 1 : 0);
    this.creatures.push(c); return c;
  }
  count(sp) { let n = 0; for (const c of this.creatures) if (c.sp === sp && c.alive) n++; return n; }
  sense(c, out) {
    out.fill(0);
    const view = SPECIES[c.sp].view, K = NC;
    const sector = rel => (Math.round(Math.atan2(Math.sin(rel), Math.cos(rel)) / (Math.PI / 3)) + SECTORS) % SECTORS;
    const see = (kind, ox, oy) => {
      const dx = ox - c.x, dy = oy - c.y, d = Math.hypot(dx, dy);
      if (d > view || d < 1e-6) return;
      const i = sector(Math.atan2(dy, dx) - c.h) * K + kind, s = 1 - d / view;
      if (s > out[i]) out[i] = s;
    };
    for (const p of this.plants) if (p.full) see(p.kind, p.x, p.y);
    for (const o of this.creatures) if (o !== c && o.alive) see(3 + ["insect", "fox", "human"].indexOf(o.sp), o.x, o.y);
    for (let sec = 0; sec < SECTORS; sec++) {   // walls: distance to the wall along each sector's centre
      const a = c.h + sec * Math.PI / 3, dx = Math.cos(a), dy = Math.sin(a);
      const d = Math.min(dx > 1e-6 ? (SIZE - c.x) / dx : dx < -1e-6 ? -c.x / dx : Infinity,
        dy > 1e-6 ? (SIZE - c.y) / dy : dy < -1e-6 ? -c.y / dy : Infinity);
      if (d < view) out[sec * K + 6] = 1 - d / view;
    }
    // The remembered place, sensed in its direction at its strength.
    let mx = 0, my = 0, ms = 0;
    if (this.memory && c.sp === "fox" && c.mem.s > 0.05) { mx = c.mem.x; my = c.mem.y; ms = c.mem.s; }
    if (this.memory && c.map) {
      const G = GAINS.grid, cell = SIZE / G; let best = 0.05, bi = -1;
      for (let i = 0; i < c.map.length; i++) if (c.map[i] > best) { best = c.map[i]; bi = i; }
      if (bi >= 0) { mx = (bi % G + 0.5) * cell; my = (Math.floor(bi / G) + 0.5) * cell; ms = Math.min(1, best); }
    }
    if (ms > 0 && Math.hypot(mx - c.x, my - c.y) > 1) out[sector(Math.atan2(my - c.y, mx - c.x) - c.h) * K + MEMCUE] = ms;
    out[ENERGY] = c.energy / GAINS.maxEnergy; out[BIAS] = 1;
    return out;
  }
  step() {
    const R = this.rand; this.t++; this.events.length = 0;
    if (this.t % GAINS.season === 0) {
      this.seasonVisits.push(this.visits.slice()); this.visits = [0, 0];
      this.richColor = 1 - this.richColor; this.events.push({ type: "season", rich: this.richColor });
    }
    for (const p of this.plants) if (!p.full && --p.t <= 0) p.full = true;
    const x = new Float32Array(N_IN);
    for (const c of this.creatures) {
      if (!c.alive) continue;
      const p = SPECIES[c.sp];
      this.sense(c, x);
      c.act = c.brain.step(x, c.reward, R, this.learn, c.touched);
      c.dopa[c.dopaAt++ % c.dopa.length] = c.brain.dopamine;
      c.reward = 0; c.ate = false; c.touched = -1;
      const e0 = c.energy;
      if (c.act === 1) c.h += p.turn; else if (c.act === 2) c.h -= p.turn;
      c.x = clamp(c.x + Math.cos(c.h) * p.speed); c.y = clamp(c.y + Math.sin(c.h) * p.speed);
      c.energy -= p.cost;
      this.eat(c);
      if (c.sp === "fox") {
        for (const o of this.creatures) if (o.alive && o.sp === "human" && Math.hypot(o.x - c.x, o.y - c.y) < 2.5) { c.energy -= GAINS.scare; c.touched = 5; }
        c.mem.s *= 0.95;
        for (const o of this.creatures) if (o.alive && o.sp === "insect" && Math.hypot(o.x - c.x, o.y - c.y) < p.view) { c.mem.x = o.x; c.mem.y = o.y; c.mem.s = 1; break; }
      }
      if (c.map) {   // place memory: a cell with no ripe bushes in sight slowly loses its value
        const i = cellOf(c.x, c.y);
        if (!c.ate && !x.some((v, j) => j < N_SENSE && j % NC === 2 && v > 0)) c.map[i] *= 0.97;
      }
      c.energy = Math.min(GAINS.maxEnergy, c.energy);
      c.reward = c.energy - e0;
      c.age++;
      const st = this.stats[c.sp]; st.steps++;
      if (c.energy <= 0) this.die(c, -1, "starved");
      else if (c.age > p.maxAge) this.die(c, 0, "old age");
    }
    // Social learning (hypothesis-level): humans near each other pass on where food grows, each
    // place the other knows better, as if told. It needs place memory to have something to tell.
    if (this.social && this.memory) {
      for (const d of this.creatures) if (d.alive && d.map) for (const o of this.creatures)
        if (o !== d && o.alive && o.map && Math.hypot(o.x - d.x, o.y - d.y) < GAINS.socialView)
          for (let i = 0; i < o.map.length; i++) if (d.map[i] > o.map[i] + 0.1) o.map[i] += GAINS.tell * (d.map[i] - o.map[i]);
    }
    // Births, then immigrants so no species dies out.
    for (const c of this.creatures.slice()) {
      const p = SPECIES[c.sp];
      if (this.births && c.alive && c.energy >= GAINS.birthEnergy && c.age >= p.birthAge && this.count(c.sp) < p.cap) {
        c.energy /= 2; const kid = this.spawn(c.sp, c); kid.energy = c.energy;
        this.stats[c.sp].births++; this.events.push({ type: "birth", id: kid.id, sp: c.sp });
      }
    }
    for (const sp in SPECIES) while (this.count(sp) < this.min[sp]) this.spawn(sp);
    this.creatures = this.creatures.filter(c => c.alive);
    for (const sp in SPECIES) { const st = this.stats[sp]; st.rate = 0.999 * st.rate + 0.001 * st.lastFood / Math.max(1, this.count(sp)); st.lastFood = 0; }
  }
  eat(c) {
    const st = this.stats[c.sp];
    const gain = (g, kind) => { c.touched = kind; if (!g) return; c.energy += g; c.meals++; c.ate = true; st.food += g; st.lastFood += g; };
    if (c.sp === "insect") {
      for (const p of this.plants) if (p.full && p.kind < 2 && Math.hypot(p.x - c.x, p.y - c.y) < 0.6) {
        p.full = false; p.t = GAINS.flowerRegrow;
        gain(p.kind === this.richColor ? GAINS.rich : GAINS.poor, p.kind);
        const j = p.kind === this.richColor ? 0 : 1; this.flowerVisits[j]++;
        if (this.t % GAINS.season >= GAINS.season / 2) this.visits[j]++;
        return;
      }
    } else if (c.sp === "human") {
      for (const p of this.plants) if (p.full && p.kind === 2 && Math.hypot(p.x - c.x, p.y - c.y) < 0.9) {
        p.full = false; p.t = GAINS.bushRegrow; gain(GAINS.berry, 2);
        const i = cellOf(p.x, p.y); c.map[i] += 0.5 * (1 - c.map[i]);
        return;
      }
    } else if (c.sp === "fox") {
      for (const o of this.creatures) if (o.alive && o.sp === "insect" && Math.hypot(o.x - c.x, o.y - c.y) < 0.7) {
        gain(GAINS.prey, 3); this.die(o, -1, "eaten", 4); this.stats.insect.eaten++; return;
      }
    }
  }
  die(c, r, why, touched = -1) {
    c.alive = false; c.brain.end(r, this.learn, touched); this.stats[c.sp].deaths++;
    this.events.push({ type: "death", id: c.id, sp: c.sp, why });
  }
}
// The k-th largest value of a (quickselect on a copy).
function kth(a, k, t) {
  t.set(a); let lo = 0, hi = t.length - 1; const want = k - 1;
  while (lo < hi) {
    const piv = t[(lo + hi) >> 1]; let i = lo, j = hi;
    while (i <= j) { while (t[i] > piv) i++; while (t[j] < piv) j--; if (i <= j) { const v = t[i]; t[i] = t[j]; t[j] = v; i++; j--; } }
    if (want <= j) hi = j; else if (want >= i) lo = i; else break;
  }
  return t[want];
}
function cellOf(x, y) { const G = GAINS.grid; return Math.min(G - 1, Math.floor(y / SIZE * G)) * G + Math.min(G - 1, Math.floor(x / SIZE * G)); }
function clamp(v) { return Math.max(0.5, Math.min(SIZE - 0.5, v)); }

// What has a creature learned? Put a copy alone in a fresh world with the same layout and season as
// its own world, learning off, and measure its food per step (and, for an insect, the share of its
// flower visits that hit the rich colour). With newborn = true, test a newborn with the same genome
// instead. Foxes get 20 naive insects to hunt. steps stays under a season, so the season holds.
export function probe(c, world, { newborn = false, steps = 3000 } = {}) {
  const sp = c.sp, pop = { insect: sp === "fox" ? 20 : 0, fox: 0, human: 0 }; pop[sp] = 1;
  const w = new World(world.seed, { learn: false, pop, births: false, social: false });
  w.richColor = world.richColor;
  const t = w.creatures.find(o => o.sp === sp);
  t.brain = newborn ? new Brain(sp, rng(c.id), c.brain.genome) : c.brain.clone();
  if (c.map && !newborn) t.map = c.map.slice();
  for (let i = 0; i < steps; i++) { t.energy = 1.5; t.age = 0; w.step(); }
  const [rich, poor] = w.flowerVisits;
  return { food: w.stats[sp].food / steps, rich: rich / Math.max(1, rich + poor) };
}
