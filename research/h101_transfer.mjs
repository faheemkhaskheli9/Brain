// H101, the main transfer experiment (research/learning-algorithm-hypotheses.md): with equal
// parameters, does a local rule plus replay transfer to new Brain World layouts as well as backprop?
//
// Layouts (chosen with the repo owner): the listen task, where a tone names which of three coloured
// objects is food. Training layouts use red, green and blue objects; new layouts use yellow, cyan and
// magenta. The structure is the same (the tone names an object: find it and grasp it); the surface,
// and so which retina channels light up and which tone goes with which look, is new.
//
// Arms, all on the same brain (same wiring and random stream per seed), the same training budget and
// no rehearsal of other stages:
//   local       the Brain World learner: fixed sparse expansion, readouts learn by trace x dopamine
//   local+sleep the same, plus offline replay from the hippocampal store (GAINS.sleepEvery)
//   backprop    the same network, but the expansion's weights and biases also learn, by the exact
//               gradient of the critic and of the policy, carried in eligibility traces (TD(lambda)
//               actor-critic with backprop into the hidden layer). Same parameters, all trained.
// Measure: episodes to pass the new layouts (70% of 50, the listen pass mark), after TRAIN episodes on
// the old ones, against a naive brain of the same arm. Savings = naive - trained.
//
// The backprop arm's hidden-layer step (HID_LR, relative to the readouts') was tuned on the OLD
// layouts only, seeds 1-2 with --quick: 0.03, 0.1, 0.3, 1, 3, 10 gave old-layout success 0.58, 0.61,
// 0.62, 0.67, 0.76, 0.76; 3 is the smaller of the tied best. The local arms use Brain World's own gains.
// Result (seeds 1-5): research/learning-algorithm-hypotheses.md, H101.
//
// H103 (issue #125) adds two arms: does a built-in structural prior close more of the gap than the
// better rule does? The prior is a colour-blind "where" pathway, after the magnocellular stream
// (Livingstone and Hubel 1988): a fixed share PRIOR of the retina-driven hidden units read each
// ray's max(r, g, b), which says how near an object is in that direction whatever its hue, instead
// of one colour channel. Same units, wiring and weights, so same parameters; only what half the
// retina units see changes. The share is not tuned. Which units are colour-blind comes from a
// separate random stream, so the brain's own stream is untouched.
//   local+prior     the local arm with the prior
//   backprop+prior  the backprop arm with the prior
//
// Run: node research/h101_transfer.mjs [seeds, default 1-5]   (--quick: 2 seeds, short budgets)
//      ARMS=backprop HID_LR=1 node research/h101_transfer.mjs 1 2 --quick   (one arm, another step)
//      OUT=rows.json ...   (also write the per-seed rows as JSON)
//      ARMS=local,local+prior,backprop,backprop+prior node research/h101_transfer.mjs 1 2 3 4 5 6 7 8 9 10   (H103)
// About 40 minutes for all arms and 5 seeds; the backprop arm is about 4x slower per episode.
import { World, Brain, GAINS, COLORS, STAGES, RAYS, rng } from "../game/world/brain.js";

const QUICK = process.argv.includes("--quick");
const SEEDS = process.argv.slice(2).filter(a => /^\d+$/.test(a)).map(Number);
const seeds = SEEDS.length ? SEEDS : QUICK ? [1, 2] : [1, 2, 3, 4, 5];
const TRAIN = QUICK ? 2500 : 4000;   // episodes on the old layouts, past the ~2000 listen needs from scratch
const CAP = QUICK ? 6000 : 10000;    // give up on the new layouts after this many
const LISTEN = STAGES.findIndex(s => s.key === "listen"), PASS = STAGES[LISTEN].pass;
const OLD = COLORS.map(c => [...c]), NEW = [[1, 1, 0.15], [0.15, 1, 1], [1, 0.15, 1]];   // yellow, cyan, magenta
GAINS.replay = 0;   // no rehearsal of earlier stages: listen only
STAGES[LISTEN].pass = 2;   // never let the curriculum move on; passing is judged here

// Backprop into the expansion. Hidden unit j: drive = bias + sum_k>=3 w x, gain = 1 + sum_k<3 w x,
// h = drive * gain when both are positive (Brain.encode). dh/dw = x * gain (drive inputs) or
// x * drive (gain inputs, the cochlea), dh/dbias = gain. Two traces per hidden weight, one for the
// critic's gradient and one for the policy's, decayed like the readout traces.
export class BackpropBrain extends Brain {
  static adopt(b, hidLr) {   // turn an existing Brain into one, keeping its wiring and weights
    Object.setPrototypeOf(b, BackpropBrain.prototype);
    const n = b.wIn.length;
    b.fan = n / b.hidden; b.nIn = b.nH - b.hidden; b.hidLr = hidLr;
    b.tV = new Float32Array(n); b.tP = new Float32Array(n); b.tVb = new Float32Array(b.hidden); b.tPb = new Float32Array(b.hidden);
    return b;
  }
  encode(x, slot) {
    const h = super.encode(x, slot);
    h.x = x;   // the input it came from, for the gradient
    return h;
  }
  act(h, allowed) {
    const choice = super.act(h, allowed);
    if (!this.learning) return choice;
    const d = GAINS.gamma * GAINS.lambda, x = h.x, F = this.fan, nH = this.nH;
    for (let j = 0; j < this.hidden; j++) {
      const hj = h[this.nIn + j];
      let gV = 0, gP = 0;
      if (hj > 0) {
        gV = this.v[this.nIn + j];
        for (const a of allowed) gP += ((a === choice) - this.pi[a]) * this.P[a * nH + this.nIn + j];
      }
      // Recompute drive and gain of an active unit (cheap: fan inputs).
      let drive = this.bias[j], gain = 1;
      if (hj > 0) for (let k = 0; k < F; k++) { const v = this.wIn[j * F + k] * x[this.idx[j * F + k]]; if (k < 3) gain += v; else drive += v; }
      this.tVb[j] = d * this.tVb[j] + (hj > 0 ? gV * gain : 0);
      this.tPb[j] = d * this.tPb[j] + (hj > 0 ? gP * gain : 0);
      for (let k = 0; k < F; k++) {
        const i = j * F + k, g = hj > 0 ? x[this.idx[i]] * (k < 3 ? drive : gain) : 0;
        this.tV[i] = d * this.tV[i] + gV * g;
        this.tP[i] = d * this.tP[i] + gP * g;
      }
    }
    return choice;
  }
  learn(r, hNext, end = !hNext) {
    super.learn(r, hNext, end);
    if (!this.learning) return;
    const delta = this.dopamine, norm = 1 + this.hh;
    const av = this.hidLr * GAINS.lrV / norm * delta, ap = this.hidLr * GAINS.lrP / norm * delta;
    for (let i = 0; i < this.wIn.length; i++) this.wIn[i] += av * this.tV[i] + ap * this.tP[i];
    for (let j = 0; j < this.hidden; j++) this.bias[j] += av * this.tVb[j] + ap * this.tPb[j];
    if (end) { this.tV.fill(0); this.tP.fill(0); this.tVb.fill(0); this.tPb.fill(0); }
  }
}

// H103's prior. A colour-blind unit's drive inputs point at extra inputs after the senses, one per
// ray, holding that ray's max(r, g, b). encode is Brain.encode reading the extended input; h.x is
// set too, so BackpropBrain's gradient sees the values these units actually read.
export function addPrior(b, share, seed) {
  const rand = rng(seed + 1e6), F = b.wIn.length / b.hidden, nIn = b.nH - b.hidden, RET = RAYS * 3;
  b.blind = 0;
  for (let j = 0; j < b.hidden; j++) {
    let retina = true;
    for (let k = 3; k < F; k++) if (b.idx[j * F + k] >= RET) retina = false;
    if (!retina || rand() >= share) continue;
    for (let k = 3; k < F; k++) b.idx[j * F + k] = nIn + Math.floor(b.idx[j * F + k] / 3);
    b.blind++;
  }
  b.encode = function (x, slot) {
    const xa = new Float32Array(nIn + RAYS);
    xa.set(x);
    for (let i = 0; i < RAYS; i++) xa[nIn + i] = Math.max(x[i * 3], x[i * 3 + 1], x[i * 3 + 2]);
    const h = new Float32Array(this.nH), gate = slot * this.hidden;
    h.set(x);
    for (let j = 0; j < this.hidden; j++) {
      if (!this.gate[gate + j]) continue;
      let gain = 1, drive = this.bias[j];
      for (let k = 0; k < F; k++) {
        const v = this.wIn[j * F + k] * xa[this.idx[j * F + k]];
        if (k < 3) gain += v; else drive += v;
      }
      if (drive > 0 && gain > 0) h[nIn + j] = drive * gain;
    }
    h.x = xa;
    return h;
  };
  return b;
}

const ARMS = {
  local: { sleep: 0, bp: 0 },
  "local+sleep": { sleep: 20, bp: 0 },
  backprop: { sleep: 0, bp: 1 },
  "local+prior": { sleep: 0, bp: 0, prior: 1 },
  "backprop+prior": { sleep: 0, bp: 1, prior: 1 },
};
const HID_LR = Number(process.env.HID_LR ?? 3);   // hidden-layer step relative to the readouts'
const PRIOR = Number(process.env.PRIOR ?? 0.5);   // share of retina-driven units made colour-blind

function make(seed, arm) {
  GAINS.sleepEvery = ARMS[arm].sleep; GAINS.sleepActor = ARMS[arm].sleep > 0;
  const w = new World(seed);
  if (ARMS[arm].bp) BackpropBrain.adopt(w.brain, HID_LR);
  if (ARMS[arm].prior) addPrior(w.brain, PRIOR, seed);
  w.setStage(LISTEN);
  return w;
}
const setColors = cs => cs.forEach((c, i) => { COLORS[i] = c; });
function run(w, n) { const e0 = w.episode; while (w.episode - e0 < n) w.step(); }
function rate(w, n = 50) { const l = w.log.slice(-n); return l.reduce((s, e) => s + e.success, 0) / Math.max(1, l.length); }
// Episodes until the last 50 on the current layouts reach PASS (null = not within CAP).
function toPass(w) {
  const e0 = w.episode;
  w.windows[LISTEN] = []; w.reset();
  while (w.episode - e0 < CAP) {
    w.step();
    const k = w.episode - e0;
    if (k >= 50 && w.log.length && rate(w) >= PASS) return k;
  }
  return null;
}

const rows = [];
const ONLY = process.env.ARMS ? process.env.ARMS.split(",").filter(a => a in ARMS) : Object.keys(ARMS);   // e.g. ARMS=backprop
for (const arm of ONLY) for (const seed of seeds) {
  const t0 = Date.now();
  setColors(OLD);
  const w = make(seed, arm);
  run(w, TRAIN);
  const oldRate = rate(w, 200);
  setColors(NEW);
  const firstNew = (() => { const before = w.log.length; run(w, 100); return w.log.slice(before).reduce((s, e) => s + e.success, 0) / 100; })();
  const trained = toPass(w);
  setColors(NEW);
  const naive = toPass(make(seed, arm));
  setColors(OLD);
  rows.push({ arm, seed, oldRate, firstNew, trained, naive });
  console.log(`${arm.padEnd(12)} seed ${seed}: old layouts ${oldRate.toFixed(2)} after ${TRAIN}, first 100 on new ${firstNew.toFixed(2)},`
    + ` new layouts passed in ${trained ?? ">" + CAP} (naive ${naive ?? ">" + CAP})  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
if (process.env.OUT) (await import("node:fs")).writeFileSync(process.env.OUT, JSON.stringify(rows));
const med = a => { const s = a.map(v => v ?? Infinity).sort((x, y) => x - y), n = s.length; return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2; };
console.log("\narm          old  first100  trained(median)  naive(median)  saved(median)");
for (const arm of ONLY) {
  const r = rows.filter(x => x.arm === arm), m = k => r.reduce((s, x) => s + x[k], 0) / r.length;
  const saved = r.map(x => x.trained === null || x.naive === null ? null : x.naive - x.trained);
  console.log(`${arm.padEnd(12)} ${m("oldRate").toFixed(2)} ${m("firstNew").toFixed(2).padStart(9)} ${String(med(r.map(x => x.trained))).padStart(16)}`
    + ` ${String(med(r.map(x => x.naive))).padStart(14)} ${String(med(saved.filter(v => v !== null))).padStart(14)}`);
}
