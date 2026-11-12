import assert from "node:assert/strict";
import { generate } from "./stateful_construct.mjs";
import { ARMS, EXIT, PROVENANCE, createModel, episode,
  legalActions, modelBytes, modelDigest, scoreTasks, selectOption,
  runSeed } from "./stateful_options.mjs";

assert.equal(EXIT, 6);
assert.ok(PROVENANCE.options.includes("carrying"));
assert.equal(ARMS.length, 7);
assert.equal(legalActions("flat").includes(EXIT), false);
assert.equal(legalActions("options").includes(EXIT), true);
assert.equal(legalActions("options-no-terminate").includes(EXIT), false);
const state = { carrying: false }, next = { carrying: true };
assert.equal(selectOption("options", state, () => 0.2), 0);
assert.equal(selectOption("options", next, () => 0.2), 1);
assert.equal(selectOption("options-no-gate", next, () => 0.2), 0);
assert.equal(selectOption("options-no-gate", state, () => 0.9), 1);
const tasks = generate(3, "eval", 3);
const model = createModel(3, "options");
assert.equal(model.brains.length, 2);
assert.ok(modelBytes(model) > modelBytes(createModel(3, "flat")));
const digest = modelDigest(model), randBefore = model.brains.map(b => b.rand);
const snapshot = model.brains.map(b => [b.nEncode, b.nActive]);
const scores = scoreTasks(model, tasks, 2, 7);
assert.ok(scores.success >= 0 && scores.success <= 1);
assert.equal(scores.episodes, 6);
assert.equal(modelDigest(model), digest);
for (let i = 0; i < model.brains.length; i++) {
  assert.equal(model.brains[i].rand, randBefore[i]);
  assert.deepEqual([model.brains[i].nEncode, model.brains[i].nActive], snapshot[i]);
}
assert.deepEqual(scores, scoreTasks(model, [...tasks].reverse(), 2, 7),
  "frozen scores must not depend on task order");
const before = modelDigest(model);
assert.equal(episode(model, tasks[0], { learn: false, seed: 4 }).decisions > 0, true);
assert.equal(modelDigest(model), before);
for (const arm of ARMS) {
  const instance = createModel(3, arm);
  const sample = scoreTasks(instance, tasks, 1, 17);
  assert.ok(sample.success >= 0 && sample.success <= 1);
  if (arm === "oracle") assert.equal(sample.success, 1);
}
const rows = runSeed(1, { trainSteps: 10, trainTasks: 3, evalTasks: 3, repeats: 1 });
assert.deepEqual(rows.map(x => x.arm), ARMS);
for (const row of rows) {
  assert.equal(row.status, "ok");
  assert.ok(row.scores.heldout.success >= 0 && row.scores.heldout.success <= 1);
  if (row.arm !== "random" && row.arm !== "oracle")
    assert.ok(row.scores.training.decisions >= 10);
}
console.log("stateful options: ok");
