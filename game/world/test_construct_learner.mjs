import assert from "node:assert/strict";
import { Brain, N_IN, PEN } from "./brain.js";
import { assertDisjoint, generate } from "./construct.mjs";
import { observation, playEpisode, frozenScore, runSeed, weightDigest, legalActions,
  randomEpisode, trialSeed, ALLOWED, SUBMIT, ARMS } from "./construct_learner.mjs";
import { rng } from "./novelty_fair.mjs";

assertDisjoint();
assert.equal(ALLOWED.length, 7);
assert.equal(legalActions([0], true).length, 6);
assert.ok(!legalActions([0], true).includes(5));
assert.ok(legalActions([0], true).includes(SUBMIT));
assert.equal(legalActions([0], false).length, 7);
assert.notEqual(trialSeed(1, { id: "one" }, 0), trialSeed(1, { id: "two" }, 0));
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
const repeatedStub = { learning: false, greedy: false, P: new Float32Array(1),
  v: new Float32Array(1), encode(x) { return x; },
  act(_h, allowed) { return allowed.includes(5) ? 5 : allowed.includes(6) ? 6 : SUBMIT; },
  learn() {} };
assert.equal(playEpisode(repeatedStub, first, { learn: false }).repeated, 1);
assert.equal(playEpisode(repeatedStub, first, { learn: false, legalMask: true }).repeated, 0);
assert.equal(randomEpisode(first, rng(8), true).repeated, 0);
const tasks = generate(1, "eval", 3).tasks;
const score = frozenScore(brain, tasks, 2);
assert.ok(score.success >= 0 && score.success <= 1);
assert.equal(weightDigest(brain), before);
// Frozen scoring preserves policy RNG, counters and the next training action.
const originalRand = brain.rand, count = brain.nEncode, active = brain.nActive;
const firstScore = frozenScore(brain, tasks, 2, { seed: 11 });
assert.deepEqual(firstScore, frozenScore(brain, [...tasks].reverse(), 2, { seed: 11 }));
assert.equal(brain.rand, originalRand);
assert.equal(brain.nEncode, count);
assert.equal(brain.nActive, active);
assert.equal(weightDigest(brain), before);
assert.equal(frozenScore(brain, tasks, 2, { seed: 11, legalMask: true }).repeatedPerEpisode, 0);
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
  if (!row.arm.startsWith("random-")) assert.ok(row.scores.trainSteps >= cheap.trainSteps);
  assert.ok(row.scores.heldout.repeatedPerEpisode >= 0);
  if (row.arm === "learner-legal") assert.equal(row.scores.heldout.repeatedPerEpisode, 0);
}
const cfg = { trainSteps: 20, trainTasks: 3, evalTasks: 3, repeats: 1 };
assert.deepEqual(runSeed(2, cfg).map(x => x.scores), runSeed(2, cfg).map(x => x.scores));
console.log("construction learner: ok");
