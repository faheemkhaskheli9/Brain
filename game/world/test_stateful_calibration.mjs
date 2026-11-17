// The calibration is deliberately a SAME-TASK learning unit, not heldout transfer.
import assert from "node:assert/strict";
import { initial, observe, oracle, transition } from "./stateful_construct.mjs";
import { makeAgent, feedback, publicPotential, episode, runSeed, ARMS,
  TASK, PROBES } from "./stateful_calibration.mjs";
import { modelDigest } from "./stateful_options.mjs";

assert.deepEqual(oracle(TASK), [4, 1, 5],
  "calibration must genuinely require acquire, move, deliver");
for (const probe of PROBES) assert.ok(oracle(probe), "probe is reachable");
const state = initial(TASK);
const x = observe(TASK, state);
const picked = transition(TASK, state, 4);
const xp = observe(TASK, picked.state);
assert.ok(publicPotential(xp) > publicPotential(x));
assert.equal(feedback("q-relative-no-reward", x, 1, xp, false), 0);
assert.equal(feedback("q-relative", x, 1, xp, false), 1);
assert.notEqual(feedback("q-relative-potential", x, 1, xp, false), 1);
assert.equal(feedback("q-relative-potential", x, 1, null, true),
  1 - publicPotential(x),
  "terminal potential must be zero, never cross into next episode");
assert.deepEqual([...observe({ ...TASK, id: "secret-eval" }, initial(TASK))],
  [...x], "the ID cannot be an input feature");

const q = makeAgent("q-relative", 13);
const one = episode(q, "q-relative", TASK, { learn: true, cap: 1, seed: 37 });
assert.equal(one.decisions, 1);
assert.equal(one.envSteps, 1);
assert.equal(one.truncated, true);
assert.ok(one.pickups <= 1);
assert.equal(one.invalid, one.blocked + one.failedPickups + one.emptyDrops + one.misplaced);
const brain = makeAgent("flat-brain", 3);
const prior = modelDigest(brain);
const frozenResult = episode(brain, "flat-brain", TASK, { learn: false, seed: 5 });
assert.ok(frozenResult.decisions > 0);
assert.equal(prior, modelDigest(brain), "learning-off cannot update primary weights");
assert.throws(() => episode(brain, "flat-brain", TASK, { cap: 0 }), /invalid/);
assert.throws(() => makeAgent("unknown", 3), /invalid/);

const config = { checkpoints: [0, 7, 19], repeats: 3 };
const first = runSeed(1, config), again = runSeed(1, config);
assert.deepEqual(first.map(r => [r.arm, r.status, r.scores]),
  again.map(r => [r.arm, r.status, r.scores]),
  "fixed seeds should produce identical complete learning curves");
assert.deepEqual(first.map(r => r.arm), ARMS);
for (const r of first) {
  assert.equal(r.status, "ok", r.reason);
  const s = r.scores;
  assert.equal(s.oracleQueries, 0);
  assert.equal(s.curve.length, 3);
  assert.deepEqual(s.curve.map(x => x.decisions), config.checkpoints);
  for (const stage of s.curve) {
    for (const category of ["calibration", "diagnosticVariants"]) {
      const x = stage[category];
      assert.ok(x.success >= 0 && x.success <= 1);
      assert.equal(x.decisions, x.envSteps);
      assert.equal(x.success * x.episodes, x.deliveries);
      assert.equal(x.failed, x.episodes - x.deliveries);
    }
  }
  assert.equal(s.trainDecisions, r.arm === "uniform-random" ? 0 : 19);
  assert.equal(s.trainEnvSteps, s.trainDecisions);
  assert.ok(s.training.pickups >= 0);
  if (r.arm === "flat-brain" || r.arm.startsWith("q-"))
    assert.ok(s.modelBytesEstimate > 0, "learned parameter payload must be charged");
  assert.ok(Number.isFinite(s.training.environmentRewardSum));
  assert.ok(Number.isFinite(s.training.learningFeedbackSum));
  if (r.arm === "q-relative-no-reward") assert.ok(s.trainingEpisodes > 0);
}
const control = first.find(r => r.arm === "uniform-random");
assert.deepEqual(control.scores.before.calibration, control.scores.after.calibration,
  "random control has no training; checkpoints must reuse the same frozen evaluation");
assert.deepEqual(control.scores.before.diagnosticVariants,
  control.scores.after.diagnosticVariants);
console.log("M0c fixed-geometry calibration, feedback and accounting: OK");
