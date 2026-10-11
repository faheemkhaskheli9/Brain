// Headless check: from reward alone the creature learns every stage within a bounded number of
// episodes, and with replay it still does all of them afterwards (no catastrophic forgetting).
// Run: node game/world/test_brain.mjs [seed ...]   (default seed 1; about 20 s per seed)
import assert from "node:assert/strict";
import { World, STAGES } from "./brain.js";

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
  const ok = {}, n = {};
  const start = w.episode;
  while (w.episode - start < 4000) {
    const k = STAGES[w.playing].key, r = w.step();
    if (r.done) { ok[k] = (ok[k] || 0) + r.success; n[k] = (n[k] || 0) + 1; }
  }
  console.log("  Kept after graduation:", Object.keys(KEEP).map(k => `${k} ${(ok[k] / n[k]).toFixed(2)}`).join(", "));
  for (const k in KEEP) assert.ok(ok[k] / n[k] >= KEEP[k], `seed ${seed}: ${k} forgotten: ${(ok[k] / n[k]).toFixed(2)} < ${KEEP[k]}`);

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
  w.perform(null);
  const after = JSON.parse(JSON.stringify(w)), was = JSON.parse(before);
  for (const k of ["P", "v", "hh"]) assert.deepEqual(after.brain[k], was.brain[k], `seed ${seed}: perform changed ${k}`);
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
console.log("ok");
