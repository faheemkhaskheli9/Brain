import assert from "node:assert/strict";
import { Brain, N_IN, PEN } from "./brain.js";
import { assertDisjoint, generate } from "./construct.mjs";
import { observation, playEpisode, frozenScore, runSeed, weightDigest, ALLOWED, SUBMIT, ARMS, legalActions, evaluationCopy, randomEpisode, randomStepScore, randomCandidateScore } from "./construct_learner.mjs";
import { rng } from "./novelty_fair.mjs";

assertDisjoint();
assert.equal(ALLOWED.length, 7);
assert.ok(ALLOWED.includes(SUBMIT));
const first = { id: "a", kind: "connect", axis: null, budget: 2, points: [[0, 0]] };
const second = { ...first, points: [[4, 4]] };
const x = observation(first, []), y = observation(second, []);
assert.equal(x.length, N_IN);
assert.notDeepEqual([...x], [...y]);
assert.deepEqual([...observation(first, [], false)], [...observation(second, [], false)]);
assert.equal(x[50], 1);
assert.equal(x[81], 1);
assert.ok(Math.abs(x[45] - first.budget / PEN.length) < 1e-6);
const brain = new Brain(rng(12));
const before = weightDigest(brain);
const frozen = playEpisode(brain, first, { learn: false });
assert.ok(frozen.decisions >= 1 && frozen.decisions <= first.budget);
assert.equal(weightDigest(brain), before);
const tasks = generate(1, "eval", 3).tasks;
const score = frozenScore(brain, tasks, 2);
assert.ok(score.success >= 0 && score.success <= 1);
assert.equal(weightDigest(brain), before);
// Repeated copies of one valid drawing count as one novel picture, not three.
const stub = { learning: false, greedy: false, P: new Float32Array(1), v: new Float32Array(1),
  encode(x) { return x; }, act() { return 5; }, learn() {} };
const repeat = frozenScore(stub, [{ ...first, budget: 1 }], 3, { seen: new Set() });
assert.equal(repeat.success, 1);
assert.equal(repeat.novel, 1 / 3);
const cheap = { trainSteps: 15, trainTasks: 3, evalTasks: 3, repeats: 2 };
const rows = runSeed(1, cheap);
assert.deepEqual(rows.map(r => r.arm), ARMS);
for (const row of rows) {
  assert.equal(row.status, "ok");
  assert.ok(row.scores.heldout.success >= 0 && row.scores.heldout.success <= 1);
  assert.ok(row.scores.heldout.novel >= 0 && row.scores.heldout.novel <= 1);
  if (!row.arm.startsWith("random")) assert.equal(row.scores.trainSteps, cheap.trainSteps);
  if (row.arm.startsWith("random")) assert.equal(row.scores.trainSteps, 0);
  assert.equal(row.scores.heldout.validatorCalls, cheap.evalTasks * cheap.repeats);
}
const cfg = { trainSteps: 20, trainTasks: 3, evalTasks: 3, repeats: 1 };
assert.deepEqual(runSeed(2, cfg).map(x => x.scores), runSeed(2, cfg).map(x => x.scores));

// Mutate a detached eval copy and prove source arrays, counters, and RNG are untouched.
const detached = evaluationCopy(brain, 123);
assert.notEqual(detached, brain);
assert.notEqual(detached.P.buffer, brain.P.buffer);
const originalWeight = brain.P[0], originalActive = brain.nActive, originalRandom = brain.rand;
detached.P[0] += 1;
assert.equal(brain.P[0], originalWeight);
const left = frozenScore(brain, tasks, 2, { evalSeed: 77, greedy: true });
const right = frozenScore(brain, tasks, 2, { evalSeed: 77, greedy: true });
assert.deepEqual(left, right);
assert.equal(brain.nActive, originalActive);
assert.equal(brain.rand, originalRandom);
assert.equal(weightDigest(brain), before);
assert.deepEqual(legalActions([0], true), ALLOWED.filter(a => a !== 5));
assert.deepEqual(legalActions([0], false), ALLOWED);
assert.equal(randomStepScore(tasks, 2, { evalSeed: 19, maskHistory: true }).duplicateActionRate, 0);
assert.equal(randomCandidateScore(tasks, 2, { evalSeed: 19 }).decisions, 0);
const randomOut = randomEpisode(rng(42), { ...first, budget: 2 }, { maskHistory: true });
assert.ok(randomOut.decisions >= 1 && randomOut.decisions <= 2);
assert.equal(randomOut.validatorCalls, 1);
const interrupted = playEpisode(stub, first, { maxDecisions: 1 });
assert.equal(interrupted.truncated, true);
assert.equal(interrupted.validatorCalls, 0);
// Train-then-test, test-then-train and test-only use the exact same frozen checkpoint.
const trainScore = frozenScore(brain, generate(7, "train", 2).tasks, 2, { evalSeed: 18 });
const testA = frozenScore(brain, tasks, 2, { evalSeed: 17 });
const testB = frozenScore(brain, tasks, 2, { evalSeed: 17 });
const trainAgain = frozenScore(brain, generate(7, "train", 2).tasks, 2, { evalSeed: 18 });
assert.deepEqual(trainScore, trainAgain);
assert.deepEqual(testA, testB);
console.log("construction learner: ok");
