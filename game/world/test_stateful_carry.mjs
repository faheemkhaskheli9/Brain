import assert from "node:assert/strict";
import { ACTIONS, CarryWorld, LIMIT, RULES, feasible, generateTasks, heuristicAction,
  legalActions, reachable, signature } from "./stateful_carry.mjs";

assert.equal(ACTIONS.length, 7);
assert.deepEqual(Object.keys(RULES), ["train", "dev", "eval"]);
for (const split of Object.keys(RULES)) {
  const a = generateTasks(7, split, 30), b = generateTasks(7, split, 30);
  assert.deepEqual(a, b);
  assert.equal(new Set(a.map(signature)).size, 30);
  assert.ok(a.some(t => !feasible(t)), "impossible goals must be represented");
  assert.ok(a.some(t => feasible(t)), "feasible goals must be represented");
  assert.ok(a.every(t => t.rule === RULES[split]));
  for (const t of a) {
    const world = new CarryWorld(t, 99), obs = world.observe();
    assert.ok(!Object.hasOwn(obs, "rule") && !Object.hasOwn(obs, "id"));
    assert.ok(!Object.hasOwn(obs, "feasible"));
    assert.deepEqual(world.observe(), obs);
    assert.ok(legalActions(obs).every(action => ACTIONS[action]));
    assert.ok(legalActions(obs).includes(6));
    assert.equal(legalActions(obs).includes(5), false);
    assert.ok(obs.walls.every(c => !legalActions(obs).some(a => a < 4 &&
      (a === 0 && c === obs.position - 5 ||
       a === 1 && c === obs.position + 1 && obs.position % 5 !== 4 ||
       a === 2 && c === obs.position + 5 ||
       a === 3 && c === obs.position - 1 && obs.position % 5 !== 0))));
  }
}
const train = new Set(generateTasks(7, "train", 30).map(t => t.rule));
const test = new Set(generateTasks(7, "eval", 30).map(t => t.rule));
assert.equal([...train].some(x => test.has(x)), false);

const base = { id: "manual", start: 0, object: 0, goal: 1,
  walls: [], wet: 1, rule: "normal", interruptionAt: null };
const world = new CarryWorld(base, 1);
assert.ok(legalActions(world.observe()).includes(4));
let pickup = world.step(4);
for (let tries = 0; pickup.event === "pickup_failed" && tries < 8; tries++) pickup = world.step(4);
assert.equal(pickup.event, "picked_up");
assert.equal(world.observe().object, null);
assert.equal(world.step(1).event, "moved");
assert.equal(world.step(5).event, "placed");
assert.equal(world.success, true);
assert.throws(() => world.step(6), /finished/);

const impossible = { ...base, goal: 2, walls: [2] };
assert.equal(feasible(impossible), false);
assert.equal(reachable(0, 2, [2]), false);
const blocked = new CarryWorld({ ...base, walls: [1], goal: 4 }, 1);
assert.ok(!legalActions(blocked.observe()).includes(1));
assert.equal(blocked.step(1).event, "blocked");
assert.equal(blocked.position, 0);

const turn = new CarryWorld({ ...base, goal: 6, rule: "turn-drop", wet: 4 }, 1);
let outcome = turn.step(4);
for (let i = 0; outcome.event === "pickup_failed" && i < 8; i++) outcome = turn.step(4);
assert.equal(outcome.event, "picked_up");
turn.step(1);
assert.equal(turn.step(2).event, "forced_drop");
assert.equal(turn.observe().object, 6);
assert.equal(turn.observe().carrying, false);

const wet = new CarryWorld({ ...base, rule: "wet-drop" }, 1);
outcome = wet.step(4);
for (let i = 0; outcome.event === "pickup_failed" && i < 8; i++) outcome = wet.step(4);
assert.equal(wet.step(1).event, "forced_drop");

const interrupted = new CarryWorld({ ...base, interruptionAt: 1 }, 1);
outcome = interrupted.step(4);
assert.equal(outcome.event, "interrupted_drop");
assert.equal(interrupted.observe().carrying, false);

const noOp = new CarryWorld({ ...base, goal: 6 }, 2);
for (let i = 0; i < LIMIT; i++) noOp.step(6);
assert.equal(noOp.done, true);
assert.equal(noOp.success, false);
assert.equal(noOp.ticks, LIMIT);

const observeA = new CarryWorld({ ...base, object: 4 }).observe();
const observeB = new CarryWorld({ ...base, object: 20 }).observe();
assert.notEqual(heuristicAction(observeA), heuristicAction(observeB));
assert.ok(legalActions(observeA).includes(6));
console.log("stateful carry environment: ok");
