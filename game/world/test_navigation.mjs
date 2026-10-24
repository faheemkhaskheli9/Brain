// The navigation suite (#108) is frozen, its splits are disjoint, every room is hard by its rule,
// and scoring it learns nothing. Fast: no curriculum is trained. Run: node game/world/test_navigation.mjs
import assert from "node:assert/strict";
import { World, ARENA } from "./brain.js";
import { SPLIT_SEEDS, suite, suiteHash, room } from "./navigation.mjs";

// Changing the suite changes every result measured on it: update this only with a new result file.
assert.equal(suiteHash(), "dea85e7930545dbf", "the frozen navigation suite changed");
const tune = new Set(SPLIT_SEEDS.tune);
assert.ok(SPLIT_SEEDS.eval.every(s => !tune.has(s)), "tune and eval share a seed");
const key = r => JSON.stringify(r.pos), seen = new Set(suite("tune").map(key));
assert.ok(suite("eval").every(r => !seen.has(key(r))), "tune and eval share a layout");
for (const r of [...suite("tune"), ...suite("eval")]) {
  const [t] = r.pos;
  assert.ok(t.every(v => v < 1.2 || v > ARENA - 1.2), `room ${r.seed}: target not in a corner`);
}
assert.deepEqual(room(1000), room(1000));
const w = new World(4);
w.setStage(2);
for (let k = 0; k < 2000; k++) w.step();
const before = JSON.stringify(w.toJSON().brain);
w.teach({ objects: suite("eval")[0].pos.map((pos, i) => ({ pos, color: i })), tone: 0 }, false);
for (let k = 0; k < 500; k++) w.step();
assert.equal(JSON.stringify(w.toJSON().brain), before, "teach with learning off changed the brain");
console.log("ok");
