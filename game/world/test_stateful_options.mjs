import assert from "node:assert/strict";
import { generate } from "./stateful_construct.mjs";
import { ARMS, EXIT, PROVENANCE, createModel, episode,
  legalActions, modelBytes, modelDigest, cloneForEvaluation, scoreTasks, selectOption,
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
const rows = runSeed(1, { trainSteps: 10, adaptSteps: 10,
  trainTasks: 3, evalTasks: 3, repeats: 1 });
assert.deepEqual(rows.map(x => x.arm), ARMS);
for (const row of rows) {
  assert.equal(row.status, "ok");
  assert.ok(row.scores.heldout.success >= 0 && row.scores.heldout.success <= 1);
  assert.ok(row.scores.zeroShot.success >= 0 && row.scores.zeroShot.success <= 1);
  assert.ok(row.scores.sourceRetentionDelta >= -1 && row.scores.sourceRetentionDelta <= 1);
  if (row.arm !== "random" && row.arm !== "oracle")
    assert.ok(row.scores.adaptation.decisions >= 10);
  if (row.arm !== "random" && row.arm !== "oracle")
    assert.ok(row.scores.training.decisions >= 10);
}
// Frozen scoring must not consume training RNG or mutate *any* Brain state,
// including synaptic importance, surprise traces and optional future fields.
const stateCopy = instance => instance.brains.map(b => Object.fromEntries(
  Reflect.ownKeys(b).filter(k => k !== "rand").map(k => [k, structuredClone(b[k])])));
const sourceTask = generate(29, "train", 1)[0];
for (const arm of ["flat", "options", "options-no-gate"]) {
  const learner = createModel(19, arm), control = createModel(19, arm);
  for (let i = 0; i < 3; i++)
    assert.deepEqual(episode(learner, sourceTask, { seed: 100 + i }),
      episode(control, sourceTask, { seed: 100 + i }),
      "identically seeded pretraining must agree");

  const frozenState = stateCopy(learner);
  const frozenDigest = modelDigest(learner);
  const trainingRng = learner.brains.map(b => b.rand);
  scoreTasks(learner, tasks, 2, 31);
  scoreTasks(learner, [...tasks].reverse(), 2, 31);
  assert.deepEqual(stateCopy(learner), frozenState, "scoring must not change actor state");
  assert.equal(modelDigest(learner), frozenDigest);
  for (let i = 0; i < learner.brains.length; i++)
    assert.strictEqual(learner.brains[i].rand, trainingRng[i]);

  const isolated = cloneForEvaluation(learner, 31);
  assert.notStrictEqual(isolated.brains[0], learner.brains[0]);
  assert.notStrictEqual(isolated.brains[0].P, learner.brains[0].P);
  assert.notStrictEqual(isolated.brains[0].syn.P.omega, learner.brains[0].syn.P.omega);
  isolated.brains[0].P[0] += 1;
  isolated.brains[0].syn.P.omega[0] += 1;
  isolated.brains[0].pi[0] += 1;
  episode(cloneForEvaluation(learner, 44), tasks[0],
    { learn: false, greedy: true, seed: 44 });
  const badTask = { ...tasks[0], walls: [[2, 0]] };
  assert.throws(() => scoreTasks(learner, [badTask]), /invalid wall placement/);
  assert.deepEqual(stateCopy(learner), frozenState,
    "evaluating an isolated actor, even on failure, must not mutate training");

  for (let i = 0; i < 5; i++) {
    const left = episode(learner, sourceTask, { seed: 300 + i });
    const right = episode(control, sourceTask, { seed: 300 + i });
    assert.deepEqual(left, right, "later training diverged after frozen evaluation");
    assert.deepEqual(stateCopy(learner), stateCopy(control),
      "complete actor state diverged after frozen evaluation");
  }
}
const unknownField = createModel(40, "flat");
unknownField.brains[0].uncloneable = () => 1;
assert.throws(() => cloneForEvaluation(unknownField, 42), /cannot clone brain field/,
  "future uncloneable state must fail closed instead of being aliased");

console.log("stateful options: ok");
