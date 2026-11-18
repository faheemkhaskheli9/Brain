import assert from "node:assert/strict";
import { N_IN } from "./brain.js";
import { SIDE, START, FAMILIES, ALLOWED, assertSplits, pairKey, generate,
  initial, observe, transition, oracle } from "./stateful_construct.mjs";

assert.equal(SIDE, 5);
assert.deepEqual(START, [2, 0]);
assert.equal(ALLOWED.length, 6);
assert.doesNotThrow(assertSplits);
const keys = {};
for (const split of Object.keys(FAMILIES)) {
  const a = generate(1, split, 24), b = generate(1, split, 24);
  assert.deepEqual(a, b);
  keys[split] = new Set(a.map(pairKey));
  assert.ok(a.every(t => oracle(t)?.length <= t.maxSteps), "all generated tasks feasible");
}
for (const one of Object.keys(keys)) for (const two of Object.keys(keys))
  if (one !== two) assert.ok([...keys[one]].every(k => !keys[two].has(k)));
const example = { id: "custom", item: [2, 0], goal: [3, 0], walls: [], maxSteps: 12 };
const first = initial(example);
assert.deepEqual(first.agent, [2, 0]);
let obs = observe(example, first);
assert.equal(obs.length, N_IN);
assert.equal(obs[2], 1); // agent at (2,0)
assert.equal(obs[25 + 2], 1); // object visible
assert.equal(obs[50 + 3], 1); // goal visible
assert.deepEqual([...obs], [...observe({ ...example, id: "different", split: "eval" }, first)]);
const invalid = transition(example, first, 5);
assert.equal(invalid.reason, "empty-drop");
assert.equal(invalid.state.invalid, 1);
assert.deepEqual(first, initial(example), "transition must not mutate its input");
const picked = transition(example, first, 4);
assert.equal(picked.reason, "picked-up");
assert.equal(picked.state.carrying, true);
assert.equal(observe(example, picked.state)[75], 1);
const moved = transition(example, picked.state, 1);
assert.deepEqual(moved.state.agent, [3, 0]);
const dropped = transition(example, moved.state, 5);
assert.equal(dropped.success, true);
assert.equal(dropped.reason, "delivered");
assert.equal(dropped.done, true);
assert.throws(() => transition(example, dropped.state, 5), /invalid/);
assert.deepEqual(oracle(example), [4, 1, 5]);
const failedDrop = transition(example, picked.state, 5);
assert.equal(failedDrop.reason, "misplaced");
assert.equal(failedDrop.state.carrying, false);
assert.equal(transition(example, failedDrop.state, 4).state.carrying, true,
  "failed placement must permit retry");
const wall = { ...example, walls: [[3, 0]] };
const blocked = transition(wall, picked.state, 1);
assert.deepEqual(blocked.state.agent, [2, 0]);
assert.equal(blocked.reason, "blocked");
const impossible = { ...example, walls: [[3, 0], [3, 1], [4, 0]], maxSteps: 8 };
assert.equal(oracle(impossible), null);
assert.throws(() => generate(1, "test", 1), /invalid/);
assert.throws(() => initial({ ...example, walls: [[2, 0]] }), /wall/);
console.log("stateful construction: ok");
