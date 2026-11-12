import assert from "node:assert/strict";
import { Brain, N_IN, rng } from "./brain.js";
import { generateTasks, legalActions } from "./stateful_carry.mjs";
import { ARMS, encode, stateKey, episode, copyBrain, TabularQ, runSeed } from "./stateful_baselines.mjs";

const task = generateTasks(5, "train", 1)[0];
const worldObs = { position: task.start, object: task.object, goal: task.goal,
  walls: task.walls, wet: task.wet, carrying: false, previousMove: -1,
  lastEvent: "start", remaining: 48 };
const x = encode(worldObs), blind = encode(worldObs, false);
assert.equal(x.length, N_IN);
assert.notDeepEqual([...x], [...blind]);
assert.notEqual(stateKey(worldObs), stateKey({ ...worldObs, position: task.object }));

const brain = new Brain(rng(3)), copy = copyBrain(brain, 29), before = brain.P[0];
copy.P[0] += 1;
assert.equal(brain.P[0], before);
assert.notEqual(copy.rand, brain.rand);
const q = new TabularQ(3), actions = legalActions(worldObs);
const chosen = q.act(worldObs, actions);
q.update(worldObs, chosen, 1, { ...worldObs, position: task.object }, true);
const qcopy = q.copy(9);
qcopy.row(stateKey(worldObs))[chosen] += 1;
assert.notEqual(q.row(stateKey(worldObs))[chosen], qcopy.row(stateKey(worldObs))[chosen]);

const stopped = episode(task, 11, (o, a) => a[a.length - 1], () => {}, 1);
assert.equal(stopped.decisions, 1);
assert.equal(stopped.censored, true);
const bad = episode(task, 11, () => 4, () => {}, 3);
assert.equal(bad.decisions, 3);
assert.ok(bad.invalid >= 0);

const cfg = { trainSteps: 17, trainTasks: 3, evalTasks: 3, repeats: 1 };
const one = runSeed(2, cfg), two = runSeed(2, cfg);
assert.equal(one.splitHash, two.splitHash);
assert.deepEqual(one.rows.map(r => r.arm), ARMS);
assert.deepEqual(one.rows.map(r => r.scores), two.rows.map(r => r.scores));
for (const row of one.rows) {
  assert.equal(row.status, "ok", row.reason);
  const s = row.scores;
  assert.ok(s.heldout.success >= 0 && s.heldout.success <= 1);
  assert.equal(s.heldout.impossibleWins, 0);
  assert.equal(s.heldout.episodes, cfg.evalTasks * cfg.repeats);
  assert.ok(s.heldout.decisions >= s.heldout.episodes);
  assert.ok(s.heldout.invalidActionRate >= 0 && s.heldout.invalidActionRate <= 1);
  assert.equal(s.trainDecisions, row.arm.startsWith("flat-") || row.arm === "tabular-q"
    ? cfg.trainSteps : 0);
}
console.log("stateful carry baselines: ok");
