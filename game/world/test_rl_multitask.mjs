// Fast deterministic, masked-action and no-task-ID smoke for shared conventional RL (#153).
import assert from "node:assert/strict";
import { STAGES } from "./brain.js";
import { Env } from "./env.mjs";
import { ActorCritic, HP } from "./rl.mjs";
import { trainShared } from "./rl_multitask.mjs";

const hp = { ...HP, HID: 8 };
const budgetPerSkill = 30, episodes = 2;
const originalAct = ActorCritic.prototype.act;
let actions = 0;
ActorCritic.prototype.act = function (obs, allowed, greedy) {
  assert.equal(arguments.length, 3, "an extra task ID reached the network");
  assert.equal(obs.length, new Env(0, "walk").obs.length);
  assert.ok(allowed.every(Number.isInteger) && allowed.length > 0);
  const decision = originalAct.call(this, obs, allowed, greedy);
  assert.ok(Number.isInteger(decision.k) && decision.k >= 0 && decision.k < allowed.length);
  actions++;
  return decision;
};
let a, b, blocked;
try {
  a = trainShared(3, { budgetPerSkill, episodes, hp });
  b = trainShared(3, { budgetPerSkill, episodes, hp });
  blocked = trainShared(3, { budgetPerSkill, episodes, hp, schedule: "blocked" });
} finally { ActorCritic.prototype.act = originalAct; }
assert.ok(actions > 0);
assert.equal(a.schedule, "interleaved");
assert.equal(a.parameters, b.parameters);
assert.equal(a.optimizerBytes, b.optimizerBytes);
assert.deepEqual(a.results, b.results, "same seed and schedule must reproduce frozen performance");
assert.deepEqual(a.trainSteps, b.trainSteps);
assert.ok(a.totalTrainSteps >= budgetPerSkill * STAGES.length);
assert.equal(blocked.schedule, "blocked");
for (const { key } of STAGES) {
  assert.ok(a.trainSteps[key] >= budgetPerSkill);
  assert.ok(blocked.trainSteps[key] >= budgetPerSkill);
  assert.ok(Number.isFinite(a.results[key].success));
  assert.ok(a.results[key].success >= 0 && a.results[key].success <= 1);
  assert.equal(a.results[key].trainSteps, a.trainSteps[key]);
}
assert.throws(() => trainShared(1, { budgetPerSkill: -1 }), /invalid/);
assert.throws(() => trainShared(1, { schedule: "hidden-label" }), /invalid/);
console.log("ok: shared actor-critic, deterministic scoring, action masking, budgets");
