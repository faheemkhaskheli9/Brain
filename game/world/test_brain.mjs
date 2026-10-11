// Headless check: from reward alone the creature learns every stage within a bounded number of
// episodes, and with replay it still does all of them afterwards (no catastrophic forgetting).
// Run: node game/world/test_brain.mjs [seed]   (seed 1 takes about 20 s)
import assert from "node:assert/strict";
import { World, STAGES } from "./brain.js";

const LIMIT = 20000;   // episodes per stage before we call it a failure
// After graduation, well above chance (grasping the nearest object scores about 0.33 on listen and
// read; random strokes write the right letter 1 time in 18). Lower than the pass marks: one
// network doing four jobs keeps some interference.
const KEEP = { grasp: 0.7, listen: 0.5, read: 0.4, write: 0.5 };

const w = new World(Number(process.argv[2] || 1));
for (let s = 0; s < STAGES.length; s++) {
  const start = w.episode;
  while (w.stage === s && !w.graduated && w.episode - start < LIMIT) w.step();
  const passed = w.stage > s || w.graduated;
  console.log(`${STAGES[s].name}: ${passed ? "learned" : "NOT learned"} after ${w.episode - start} episodes`);
  assert.ok(passed, `${STAGES[s].key} not learned within ${LIMIT} episodes`);
}

// Graduated: it now cycles grasp, listen, read and write (walking is an automatic habit by then).
const ok = {}, n = {};
const start = w.episode;
while (w.episode - start < 4000) {
  const k = STAGES[w.playing].key, r = w.step();
  if (r.done) { ok[k] = (ok[k] || 0) + r.success; n[k] = (n[k] || 0) + 1; }
}
console.log("Kept after graduation:", Object.keys(KEEP).map(k => `${k} ${(ok[k] / n[k]).toFixed(2)}`).join(", "));
for (const k in KEEP) assert.ok(ok[k] / n[k] >= KEEP[k], `${k} forgotten: ${(ok[k] / n[k]).toFixed(2)} < ${KEEP[k]}`);

// Save and load: at an episode boundary, a reloaded brain acts exactly as the original does.
while (!w.step().done);
const copy = World.fromJSON(JSON.parse(JSON.stringify(w)));
for (let i = 0; i < 2000; i++) {
  const a = w.step(), b = copy.step();
  assert.deepEqual(b, a, `loaded brain diverged at step ${i}`);
}
assert.throws(() => World.fromJSON({ version: 1 }), /not a Brain World save/);
console.log("Save and load: same actions for 2000 steps");
console.log("ok");
