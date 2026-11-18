import assert from "node:assert/strict";
import { ARMS, makeStream, replay, runSeed } from "./stateful_credit_replay.mjs";

assert.equal(ARMS.length, 7);
const stream = makeStream(3, 9);
assert.deepEqual(stream, makeStream(3, 9),
  "data collection must be deterministic and independent of training arms");
assert.notEqual(stream.hash, makeStream(4, 9).hash,
  "seed should change public-transition data");
assert.equal(stream.episodes, 9);
assert.ok(stream.scripted > 0 && stream.scripted < stream.episodes);
assert.ok(stream.completions >= 1,
  "supplied demonstrations must produce a positive reward-bearing stream");
assert.ok(stream.invalid >= 0);
assert.ok(stream.steps.length > 9 && stream.steps.length <= 9 * 12);
assert.equal(stream.steps.filter(r => r.end).length, 9);
for (const step of stream.steps) {
  assert.equal(step.before.length, step.after.length);
  assert.ok(step.before.length >= 84);
  assert.ok([0, 1, 2, 3, 4, 5].includes(step.action));
  assert.ok(Number.isFinite(step.reward));
  assert.ok(step.terminal ? step.end : true);
}
const rows = runSeed(3, { episodes: 9 });
const again = runSeed(3, { episodes: 9 });
assert.deepEqual(rows.map(x => x.scores), again.map(x => x.scores),
  "same log and same initialized network must give identical TD updates");
assert.deepEqual(rows.map(x => x.arm), ARMS);
for (const row of rows) {
  assert.equal(row.status, "ok", row.reason);
  const scores = row.scores;
  assert.equal(scores.streamHash, stream.hash,
    "different learning rules must NOT collect different data");
  assert.equal(scores.replayDecisions, stream.steps.length);
  assert.equal(scores.recordedEnvironmentSteps, stream.steps.length);
  assert.equal(scores.replayEnvironmentSteps, 0);
  assert.equal(scores.policyEnvironmentInteractions, 0);
  assert.equal(scores.policyOracleQueries, 0);
  assert.equal(scores.recordedEpisodes, 9);
  assert.equal(scores.recordedSuccesses, stream.completions);
  assert.equal(scores.originalRewardSum, stream.rewardSum);
  assert.ok(scores.modelBytes > 0);
  assert.ok(scores.actorDeltaL1 >= 0);
  assert.ok(scores.criticDeltaL1 >= 0);
  assert.ok(Number.isFinite(scores.meanAbsTD));
  assert.ok(scores.probeChangeL1 >= 0);
  assert.deepEqual(scores.beforeProbe, rows[0].scores.beforeProbe,
    "arms must start from exactly the same actor");
}
const byArm = Object.fromEntries(rows.map(x => [x.arm, x.scores]));
assert.ok(byArm.native.actorDeltaL1 > 0);
assert.ok(byArm.native.criticDeltaL1 > 0);
assert.equal(byArm["actor-frozen"].actorDeltaL1, 0);
assert.ok(byArm["actor-frozen"].criticDeltaL1 > 0);
assert.equal(byArm["critic-frozen"].criticDeltaL1, 0);
assert.ok(byArm["critic-frozen"].actorDeltaL1 > 0);
assert.equal(byArm["zero-feedback"].actorDeltaL1, 0);
assert.equal(byArm["zero-feedback"].criticDeltaL1, 0);
assert.equal(byArm["zero-feedback"].meanAbsTD, 0);
assert.equal(byArm["zero-feedback"].probeChangeL1, 0);
assert.notEqual(byArm.native.criticDeltaL1, byArm["no-bootstrap"].criticDeltaL1,
  "next-state bootstrap must affect the critic on identical transitions");
assert.notEqual(byArm.native.actorDeltaL1, byArm["trace-one-step"].actorDeltaL1,
  "eligibility memory must affect the actor on identical transitions");
assert.ok(Math.abs(byArm["reward-shifted"].appliedRewardSum -
  byArm.native.appliedRewardSum) < 1e-8,
  "reward-shift control preserves reward mass while disturbing assignment");
assert.notEqual(byArm["reward-shifted"].actorDeltaL1,
  byArm.native.actorDeltaL1,
  "shifting outcomes should cause a different update without new observations");

assert.throws(() => makeStream(-1), /invalid/);
assert.throws(() => makeStream(1, 0), /invalid/);
assert.throws(() => replay(1, "unknown", stream), /invalid/);
assert.throws(() => runSeed(1, { episodes: 0 }), /invalid/);
console.log("M0d matched public-transition credit replay: OK");
