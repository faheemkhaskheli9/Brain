// Cheap scientific-validity smoke test for the stage-dependent gait/action confound.
import assert from "node:assert/strict";
import { World, ACT_SETS } from "./brain.js";
import { evaluateCheckpoint } from "./scaffold_eval.mjs";

const legacy = new World(7), control = new World(7, "rays", "unscaffolded");
assert.equal(legacy.actionSetIndex(), 0);
assert.equal(control.actionSetIndex(), 0);
assert.equal(legacy.bodyScaffoldActive(), false);
assert.equal(control.bodyScaffoldActive(), false);
legacy.setStage(1);
control.setStage(1);
assert.equal(legacy.bodyScaffoldActive(), true);
assert.equal(legacy.actionSetIndex(), 1);
assert.equal(control.bodyScaffoldActive(), false);
assert.equal(control.actionSetIndex(), 0);
assert.ok(ACT_SETS[0].length > ACT_SETS[1].length);
legacy.perform("write");
control.perform("write");
assert.equal(legacy.actionSetIndex(), 2);
assert.equal(control.actionSetIndex(), 2);  // pen/board scaffold is explicitly not removed
assert.throws(() => new World(1, "rays", "invalid"), /unknown scaffold/);

const persisted = control.toJSON();
assert.equal(persisted.scaffold, "unscaffolded");
assert.equal(World.fromJSON(persisted).scaffold, "unscaffolded");
const oldSave = { ...persisted };
delete oldSave.scaffold;
assert.equal(World.fromJSON(oldSave).scaffold, "curriculum");

// Same initial world and scene draws; only the developmental action restriction changes.
// This is a synthetic untrained fixture, NOT an experimental success result.
const checkpoint = new World(3).toJSON();
const a = evaluateCheckpoint(checkpoint, "curriculum", 11, 1, ["grasp", "write"]);
const b = evaluateCheckpoint(checkpoint, "unscaffolded", 11, 1, ["grasp", "write"]);
assert.equal(a.sceneHash, b.sceneHash, "paired evaluation used different scenes");
assert.equal(a.scores.write, b.scores.write, "pen/board task should be unaffected by body scaffold");
for (const r of [a, b]) {
  assert.ok(r.scores.grasp >= 0 && r.scores.grasp <= 1);
  assert.ok(r.decisions > 0);
  assert.equal(r.episodes, 2);
}
console.log("stage-scaffold diagnostic: OK (no AGI claim)");
