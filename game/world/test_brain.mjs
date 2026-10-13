// Headless check: from reward alone the creature learns every stage within a bounded number of
// episodes, and with replay it still does all of them afterwards (no catastrophic forgetting).
// Run: node game/world/test_brain.mjs [seed ...]   (default seed 1; about 40 s per seed)
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { World, Brain, STAGES, GAINS, ACT_SETS, rng, orient } from "./brain.js";

// One model, no task index (#60): nothing in the brain is sized or indexed by task, and the world
// hands encode an inferred slot, never the task it is playing.
assert.ok(!Brain.toString().includes("STAGES"), "Brain is indexed by task");
for (const [, arg] of World.toString().matchAll(/\.encode\(([^;]*)/g)) assert.ok(!/playing|mode|task|stage/.test(arg), `encode is told the task: ${arg}`);
assert.ok(!/playing|mode|task|stage|target|tone/.test(World.prototype.context.toString()), "context() reads the task");
assert.equal(new World(1).brain.gate.length, GAINS.slots * GAINS.hidden);
// The action set and the leg habit come from the body and development, not the task name (#61).
const stepSrc = World.prototype.step.toString();
for (const [, arg] of stepSrc.matchAll(/\.act\(([^;]*)/g)) assert.ok(!/\bm\b|mode|playing/.test(arg), `act is told the task: ${arg}`);
for (const [, rhs] of stepSrc.matchAll(/(?:const set|const habit|this\.legs) = ([^;]*)/g)) assert.ok(!/\bm\b|mode|playing|task/.test(rhs), `action set or habit reads the task: ${rhs}`);
assert.ok(!/mode|playing/.test(World.prototype.sense.toString()), "sense() reads the task");

const LIMIT = 20000;   // episodes per stage before we call it a failure
// After graduation, well above chance (grasping the nearest object scores about 0.33 on listen and
// read; random strokes write the right letter 1 time in 18). Lower than the pass marks: one
// network doing four jobs keeps some interference.
const KEEP = { grasp: 0.7, listen: 0.5, read: 0.4, write: 0.5 };

const seeds = process.argv.slice(2).map(Number);
for (const seed of seeds.length ? seeds : [1]) {
  console.log(`seed ${seed}`);
  const w = new World(seed);
  for (let s = 0; s < STAGES.length; s++) {
    const start = w.episode;
    while (w.stage === s && !w.graduated && w.episode - start < LIMIT) w.step();
    const passed = w.stage > s || w.graduated;
    console.log(`  ${STAGES[s].name}: ${passed ? "learned" : "NOT learned"} after ${w.episode - start} episodes`);
    assert.ok(passed, `seed ${seed}: ${STAGES[s].key} not learned within ${LIMIT} episodes`);
  }

  // Graduated: it now cycles grasp, listen, read and write (walking is an automatic habit by then).
  // Every live encode must get the slot infer just returned (the brain is never handed the task).
  const ok = {}, n = {}, steps = {}, eps = {};
  const start = w.episode, b = w.brain, infer = b.infer.bind(b), encode = b.encode.bind(b);
  let inferred;
  b.infer = z => (inferred = infer(z));
  b.encode = (x, slot) => { assert.equal(slot, inferred, `seed ${seed}: encode got a slot infer did not pick`); return encode(x, slot); };
  while (w.episode - start < 4000) {
    const k = STAGES[w.playing].key, slot = w.slot, r = w.step();
    (steps[k] ??= Array(GAINS.slots).fill(0))[slot]++;
    if (r.done) { ok[k] = (ok[k] || 0) + r.success; n[k] = (n[k] || 0) + 1; (eps[k] ??= Array(GAINS.slots).fill(0))[slot]++; }
  }
  delete b.infer; delete b.encode;
  console.log("  Kept after graduation:", Object.keys(KEEP).map(k => `${k} ${(ok[k] / n[k]).toFixed(2)}`).join(", "));
  for (const k in KEEP) assert.ok(ok[k] / n[k] >= KEEP[k], `seed ${seed}: ${k} forgotten: ${(ok[k] / n[k]).toFixed(2)} < ${KEEP[k]}`);
  // Each kept skill ends its episodes in its own slot (label share) and spends most steps there.
  const top = Object.fromEntries(Object.keys(KEEP).map(k => [k, eps[k].indexOf(Math.max(...eps[k]))]));
  const share = (h, c) => h[c] / h.reduce((p, q) => p + q, 0);
  console.log("  Context slots:", Object.keys(KEEP).map(k => `${k} slot ${top[k]} (episodes ${share(eps[k], top[k]).toFixed(2)}, steps ${share(steps[k], top[k]).toFixed(2)})`).join(", "));
  for (const k in KEEP) {
    assert.ok(share(eps[k], top[k]) >= 0.95, `seed ${seed}: ${k} episodes split across slots`);
    assert.ok(share(steps[k], top[k]) >= 0.7, `seed ${seed}: ${k} steps split across slots`);
  }
  assert.equal(new Set(Object.values(top)).size, Object.keys(KEEP).length, `seed ${seed}: two skills share a slot`);

  // Save and load: at an episode boundary, a reloaded brain acts exactly as the original does.
  while (!w.step().done);
  const copy = World.fromJSON(JSON.parse(JSON.stringify(w)));
  for (let i = 0; i < 2000; i++) {
    const a = w.step(), b = copy.step();
    assert.deepEqual(b, a, `seed ${seed}: loaded brain diverged at step ${i}`);
  }
  console.log("  Save and load: same actions for 2000 steps");

  // Perform mode: learning off, one skill per run. It still scores at the kept bar, and nothing
  // the brain or the curriculum holds changes.
  const before = JSON.stringify(w), rates = [];
  for (const k in KEEP) {
    w.perform(k);
    while (w.perf.n < 200) { assert.equal(w.mode, k); w.step(); }
    rates.push(`${k} ${(w.perf.ok / w.perf.n).toFixed(2)}`);
    assert.ok(w.perf.ok / w.perf.n >= KEEP[k], `seed ${seed}: perform ${k} ${w.perf.ok / w.perf.n} < ${KEEP[k]}`);
  }
  // Free play (#62): a random scene each episode, never told which. It must find each skill itself.
  w.perform("any");
  while (w.perf.n < 1000) w.step();
  const sc = w.perf.scene;
  console.log("  Free play (any scene):", Object.keys(KEEP).map(k => `${k} ${(sc[k].ok / sc[k].n).toFixed(2)}`).join(", "));
  for (const k in KEEP) assert.ok(sc[k].ok / sc[k].n >= KEEP[k], `seed ${seed}: free play ${k} ${(sc[k].ok / sc[k].n).toFixed(2)} < ${KEEP[k]}`);
  w.perform(null);
  const after = JSON.parse(JSON.stringify(w)), was = JSON.parse(before);
  for (const k of ["P", "v", "hh", "proto", "uses"]) assert.deepEqual(after.brain[k], was.brain[k], `seed ${seed}: perform changed ${k}`);
  assert.equal(after.stage, was.stage);
  console.log("  Perform (learning off):", rates.join(", "));
}

// Perform mid-training leaves the curriculum alone, and a save made while performing resumes training.
const t = new World(1);
t.setStage(3);
while (t.episode < 30) t.step();
const snap = JSON.stringify({ e: t.episode, w: t.windows, l: t.log.length, s: t.stage, P: Array.from(t.brain.P) });
t.perform("grasp");
while (t.perf.n < 60) t.step();
assert.equal(t.toJSON().playing, t.stage);
assert.equal(JSON.stringify({ e: t.episode, w: t.windows, l: t.log.length, s: t.stage, P: Array.from(t.brain.P) }), snap);
assert.throws(() => t.perform("fly"), /valid: walk, grasp/);
assert.throws(() => World.fromJSON({ version: 1 }), /not a Brain World save/);

// Migration (#63). fixtures/v3-seed1.json: seed 1 trained to graduation by the told-gate code
// before #60 (one gate row per task), saved without its episodic store.
const v3 = JSON.parse(readFileSync(new URL("fixtures/v3-seed1.json", import.meta.url), "utf8"));
const g3 = World.fromJSON(v3);
assert.equal(g3.brain.gate.length, GAINS.slots * GAINS.hidden);
g3.perform("read");
while (g3.perf.n < 100) g3.step();
const rs = g3.perf.scene.read.slots, rShare = rs[3] / rs.reduce((p, q) => p + q);
console.log(`  v3 save: read ${(g3.perf.ok / g3.perf.n).toFixed(2)}, ${(100 * rShare).toFixed(0)}% of its steps in slot 3`);
assert.ok(rShare > 0.5, `v3 save: read uses slot 3 on ${rShare.toFixed(2)} of steps`);
assert.throws(() => World.fromJSON({ ...v3, brain: { ...v3.brain, gate: v3.brain.gate.slice(1) } }), /not a Brain World save/);
// More slots: a save at 8 loads at 12 and performs exactly as before (the new rows start free).
const save8 = JSON.parse(JSON.stringify(World.fromJSON(v3)));
const kept = slots => {
  const SLOTS = GAINS.slots; GAINS.slots = slots;
  const w = World.fromJSON(save8), out = {};
  assert.equal(w.brain.uses.length, slots);
  for (const k in KEEP) { w.perform(k); while (w.perf.n < 50) w.step(); out[k] = w.perf.ok; }
  GAINS.slots = SLOTS;
  return out;
};
assert.deepEqual(kept(12), kept(8), "more slots changed what a saved brain does");
// More stages: a graduated save resumes at the first new one.
STAGES.push({ key: "copy", name: "Copy", pass: 0.8, about: "test only" });
for (const o of [v3, save8]) {
  const w = World.fromJSON(o);
  assert.deepEqual([w.windows.length, w.stage, w.graduated], [6, 5, false], `v${o.version} save in six-stage code`);
}
STAGES.pop();
console.log("  Migration: v3 loads, 8 slots load at 12 unchanged, a sixth stage resumes there");

// The model card (#55): birth facts survive load and re-save, and each save adds one scored row.
assert.equal(g3.meta.seed, null, "a save from before meta has an unknown seed");
const once = JSON.parse(World.fromJSON({ ...save8, meta: new World(7).meta }).save());
const twice = JSON.parse(World.fromJSON(once).save());
assert.deepEqual([twice.meta.seed, twice.meta.created, twice.meta.gains], [7, once.meta.created, once.meta.gains]);
assert.deepEqual([once.meta.saves.length, twice.meta.saves.length], [1, 2]);
const sc = twice.meta.saves[1].scores;
assert.deepEqual(Object.keys(sc), STAGES.map(s => s.key));
assert.ok(Object.values(sc).every(r => r >= 0 && r <= 1));
console.log(`  meta: seed and birth kept over two saves, scores ${JSON.stringify(sc)}`);

// Episodic store and sleep. A spy records, for every buffer slot, which episode (reset) and which
// store call wrote it: ground truth that does not rely on the store's own episode ids. Every
// replayable non-terminal draw must have its true successor next to it, and an action from its set.
const KEEP_GAINS = { ...GAINS };
Object.assign(GAINS, { memCap: 256, sleepEvery: 5, sleepActor: true });   // small, so it wraps fast
function spy(w) {
  const truth = [], s = { resets: 0, calls: 0 };
  const reset = w.reset.bind(w), store = w.hippo.store.bind(w.hippo);
  w.reset = () => { s.resets++; reset(); };
  w.hippo.store = (...args) => { truth[w.hippo.head] = [s.resets, s.calls++]; store(...args); };
  return { truth, s };
}
function checkReplay(w, truth, why) {
  const H = w.hippo, rand = rng(7);
  for (let k = 0; k < 10000; k++) {
    const e = H.sample(rand);
    assert.ok(e >= 0, `${why}: nothing replayable`);
    assert.ok(ACT_SETS[H.set[e]].includes(H.a[e]), `${why}: action outside its set`);
    assert.notEqual(H.end[e], 2, `${why}: replayed a time-limit cut`);
    if (H.end[e] === 1) continue;
    const j = H.next(e);
    assert.ok(j >= 0 && truth[j][0] === truth[e][0] && truth[j][1] === truth[e][1] + 1, `${why}: wrong successor`);
  }
}
const run = (w, n) => { for (let i = 0; i < n; i++) w.step(); };
const m = new World(2), { truth, s } = spy(m);
m.setStage(3);
run(m, 1500);
assert.equal(m.hippo.n, 256);
checkReplay(m, truth, "wrapped");
run(m, 7); m.perform("grasp");
const calls = s.calls; run(m, 300);
assert.equal(s.calls, calls, "perform mode stored transitions");
m.perform(null); run(m, 30);   // check before the junction between episodes is overwritten
checkReplay(m, truth, "perform on/off mid-episode");
run(m, 7); m.setStage(4); run(m, 5); m.setStage(2); run(m, 30);
checkReplay(m, truth, "setStage mid-episode");
const v0 = Array.from(m.brain.v);
m.brain.sleep(m.hippo, 50, rng(3));
assert.notDeepEqual(Array.from(m.brain.v), v0, "sleep changed no weight");

// Save 40 steps into an episode and load: the copy plays that episode again from its start, so the
// 40 steps already stored must not count twice. (Its weights include those 40 steps of learning,
// so it need not act exactly as before; boundary saves are checked step by step above.)
m.setStage(3);
let start;
do { start = { head: m.hippo.head, n: m.hippo.n }; while (m.t < 40 && !m.step().done); } while (m.t < 40);
const c = World.fromJSON(JSON.parse(JSON.stringify(m)));
assert.deepEqual({ head: c.hippo.head, n: c.hippo.n }, start, "store: the saved episode's steps were kept");
// A few steps in, the stale pre-save copies of these steps sit right at head, in the same episode:
// the newest step must not link to them (the j !== head guard).
for (let i = 0; i < 5; i++) c.step();
assert.equal(c.hippo.next((c.hippo.head + GAINS.memCap - 1) % GAINS.memCap), -1, "store: newest step linked to a stale one");
let len = 5;
while (!c.step().done) len++;
assert.equal(c.hippo.head, (start.head + len + 1) % GAINS.memCap, "store: duplicated steps after load");
// The step before the replayed episode belongs to the one setStage cut short: never its successor.
assert.equal(c.hippo.next((start.head + GAINS.memCap - 1) % GAINS.memCap), -1, "store: linked across episodes after load");
const old = JSON.parse(JSON.stringify(m));
delete old.hippo;
assert.equal(World.fromJSON(old).hippo.n, 0);   // a save from before the store loads with an empty one
old.hippo = { ...JSON.parse(JSON.stringify(m)).hippo, n: 9999 };
assert.throws(() => World.fromJSON(old), /not a Brain World save/);
Object.assign(GAINS, KEEP_GAINS);
console.log("  Episodic store: replay draws valid after wrap, perform, setStage and save/load");

// Orienting reflex (#83): an object on the left pushes the left leg (turn left), walls alone do nothing.
const o = new World(3);
o.setStage(1);
o.objects[0].pos = [o.pos[0] + 3 * Math.cos(o.heading + 0.4), o.pos[1] + 3 * Math.sin(o.heading + 0.4)];
const ox = o.sense();
assert.ok(orient(ox) > 0, "orient: object on the left must turn left");
o.objects = [];
assert.equal(orient(o.sense()), 0, "orient: walls must not drive the reflex");
console.log("  Orienting reflex: turns toward an object, ignores walls");
console.log("ok");
