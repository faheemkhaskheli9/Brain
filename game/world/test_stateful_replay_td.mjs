import assert from "node:assert/strict";
import { createModel, modelDigest } from "./stateful_options.mjs";
import { ARMS, logStream, replay, runSeed } from "./stateful_replay_td.mjs";

const log = logStream(3, 40), again = logStream(3, 40);
assert.equal(log.length, 40);
assert.deepEqual(log.map(t => [t.action, t.reward, t.end]), again.map(t => [t.action, t.reward, t.end]), "log is deterministic");
assert.ok(log.at(-1).end, "stream ends at its budget");

// Same stream, same init: replaying the native rule twice gives identical weights; other rules differ.
const digest = arm => { const m = createModel(3 * 1664525 + 119 + 1013904223 >>> 0, "flat"); replay(m, arm, log); return modelDigest(m); };
assert.equal(digest("replay-native"), digest("replay-native"));
for (const arm of ARMS.slice(1)) assert.notEqual(digest(arm), digest("replay-native"), arm);

// Forced replay of the logged actions reproduces the logging learner's own weights exactly.
assert.equal(digest("replay-native"), modelDigest(log.model), "forced replay is faithful");

const rows = runSeed(2, { decisions: 30, repeats: 2 });
assert.deepEqual(rows.map(r => r.arm), ARMS);
for (const r of rows) {
  assert.equal(r.status, "ok", r.reason);
  assert.equal(r.scores.replayedTransitions, 30);
  assert.equal(r.scores.onlineOracleQueries, 0);
}
assert.equal(rows.find(r => r.arm === "replay-zero-feedback").scores.meanAbsTD, 0);
assert.throws(() => logStream(1, 0), /invalid/);
assert.throws(() => replay(createModel(1, "flat"), "nope", log), /invalid/);
console.log("identical-transition replay: ok");
