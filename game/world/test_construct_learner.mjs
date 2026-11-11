import assert from "node:assert/strict";
import { Brain, N_IN, PEN } from "./brain.js";
import { assertDisjoint, generate } from "./construct.mjs";
import { observation, playEpisode, frozenScore, runSeed, weightDigest, ALLOWED, SUBMIT, ARMS } from "./construct_learner.mjs";
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
assert.equal(x[45], first.budget / PEN.length);
const brain = new Brain(rng(12));
const before = weightDigest(brain);
const frozen = playEpisode(brain, first, { learn: false });
assert.ok(frozen.decisions >= 1 && frozen.decisions <= first.budget);
assert.equal(weightDigest(brain), before);
const tasks = generate(1, "eval", 3).tasks;
const score = frozenScore(brain, tasks, 2);
assert.ok(score.success >= 0 && score.success <= 1);
assert.equal(weightDigest(brain), before);
const cheap = { trainSteps: 15, trainTasks: 3, evalTasks: 3, repeats: 2 };
const rows = runSeed(1, cheap);
assert.deepEqual(rows.map(r => r.arm), ARMS);
for (const row of rows) {
  assert.equal(row.status, "ok");
  assert.ok(row.scores.heldout.success >= 0 && row.scores.heldout.success <= 1);
  assert.ok(row.scores.heldout.novel >= 0 && row.scores.heldout.novel <= 1);
  if (row.arm !== "random-valid") assert.ok(row.scores.trainSteps >= cheap.trainSteps);
}
const cfg = { trainSteps: 20, trainTasks: 3, evalTasks: 3, repeats: 1 };
assert.deepEqual(runSeed(2, cfg).map(x => x.scores), runSeed(2, cfg).map(x => x.scores));
console.log("construction learner: ok");
