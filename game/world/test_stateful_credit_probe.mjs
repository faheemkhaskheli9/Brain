import assert from "node:assert/strict";
import { createModel, cloneForEvaluation, modelDigest } from "./stateful_options.mjs";
import { ALLOWED, initial, observe, oracle } from "./stateful_construct.mjs";
import { TASK } from "./stateful_calibration.mjs";
import { ARMS, TASK_TWO, rollout, sensoryAudit, runSeed } from "./stateful_credit_probe.mjs";

assert.deepEqual(oracle(TASK_TWO), [4, 5], "two-step fixture must be physical pickup then drop");
assert.deepEqual(oracle(TASK), [4, 1, 5], "three-step fixture must be pickup, move, drop");
assert.equal(ARMS.length, 6);
const b = createModel(7, "flat");
const sensory = sensoryAudit(b, "native-three", 15);
assert.equal(sensory.rawInputWidth, observe(TASK, initial(TASK)).length);
assert.ok(sensory.directActorInputWidth >= sensory.rawInputWidth,
  "all public channels must reach actor via direct-input trunk");
assert.equal(sensory.goalCounterfactualL1, 0, "initial policy must be uniform");
assert.equal(sensory.carryingGoalCounterfactualL1, 0, "no acquired goal response before learning");
const m = sensoryAudit(b, "mask-goal", 15);
assert.equal(m.goalCounterfactualL1, 0);
assert.equal(m.carryingGoalCounterfactualL1, 0);
assert.equal(m.directGoalMasked, true);

// Policy-gradient and critic updates receive a real reward prediction error
// and clear eligibility only at an actual terminal/explicit budget boundary.
const actionModel = createModel(11, "flat");
const before = modelDigest(actionModel);
const result = rollout(actionModel, "native-three", TASK, { learn: true, cap: 1 });
assert.equal(result.decisions, 1);
assert.equal(result.envSteps, 1);
assert.equal(result.tdUpdates, 1);
assert.equal(result.truncated, true);
assert.ok(result.tracePMax > 0);
assert.ok(result.meanAbsTD > 0);
assert.notEqual(modelDigest(actionModel), before);
assert.ok(actionModel.brains[0].ev.every(v => v === 0),
  "decision cap must clear critic trace");
assert.ok(actionModel.brains[0].eP.every(v => v === 0),
  "decision cap must clear actor trace");

const untrained = createModel(11, "flat");
const original = modelDigest(untrained);
const frozen = cloneForEvaluation(untrained, 27);
rollout(frozen, "native-three", TASK, { learn: false });
assert.equal(modelDigest(untrained), original,
  "frozen rollout must not mutate original weights or stored traces");

const rewardless = createModel(13, "flat");
const beforeZero = Array.from(rewardless.brains[0].P);
rollout(rewardless, "zero-feedback", TASK, { learn: true, cap: 7 });
assert.deepEqual(Array.from(rewardless.brains[0].P), beforeZero,
  "zero reward and zero initial critic must not cause spurious actor updates");

// A controlled nonterminal next-value counterexample verifies that the no-
// bootstrap ablation is not accidentally identical to the native TD target.
const seed = createModel(19, "flat");
for (let i = 0; i < 25; i++) seed.brains[0].v[i] = 1;
const withBootstrap = cloneForEvaluation(seed, 41);
const withoutBootstrap = cloneForEvaluation(seed, 41);
rollout(withBootstrap, "native-three", TASK, { learn: true, cap: 1 });
rollout(withoutBootstrap, "no-bootstrap", TASK, { learn: true, cap: 1 });
assert.notEqual(modelDigest(withBootstrap), modelDigest(withoutBootstrap),
  "removing the next-state critic value must alter the TD update");

const conf = { checkpoints: [0, 5, 17], repeats: 2 };
const rows = runSeed(2, conf), repeat = runSeed(2, conf);
assert.deepEqual(rows.map(x => [x.arm, x.status, x.scores]),
  repeat.map(x => [x.arm, x.status, x.scores]), "deterministic replay");
assert.deepEqual(rows.map(x => x.arm), ARMS);
for (const row of rows) {
  assert.equal(row.status, "ok", row.reason);
  const s = row.scores;
  assert.equal(s.trainDecisions, 17);
  assert.equal(s.trainEnvSteps, 17);
  assert.equal(s.learningUpdates, 17);
  assert.equal(s.onlineOracleQueries, 0);
  assert.ok(s.modelBytes > 0);
  assert.deepEqual(s.curve.map(x => x.decisions), conf.checkpoints);
  for (const point of s.curve) {
    for (const metric of ["calibration", "diagnosticVariants"]) {
      const q = point[metric];
      assert.equal(q.decisions, q.envSteps);
      assert.equal(q.failed + q.deliveries, q.episodes);
      assert.equal(q.success, q.deliveries / q.episodes);
      assert.ok(q.entropy >= 0 && q.entropy <= 1);
    }
  }
  if (row.arm === "mask-goal") {
    assert.equal(s.curve.at(-1).sensory.goalCounterfactualL1, 0);
    assert.equal(s.curve.at(-1).sensory.carryingGoalCounterfactualL1, 0);
  }
  if (row.arm === "zero-feedback") {
    assert.equal(s.trainMeanAbsTD, 0);
    assert.equal(s.curve.at(-1).sensory.goalActorL1, 0);
  }
}
assert.throws(() => runSeed(1, { checkpoints: [0, 0], repeats: 2 }), /invalid/);
assert.throws(() => rollout(b, "native-three", TASK, { cap: 0 }), /invalid/);
assert.throws(() => rollout(b, "invalid-arm", TASK), /invalid/);
console.log("M0c causal sensory and TD trace audit: OK");
