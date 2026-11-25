import assert from "node:assert/strict";
import { rng } from "./brain.js";
import { ALLOWED, initial, observe, oracle, transition } from "./stateful_construct.mjs";
import { PublicMazeHeuristic } from "./stateful_construct_controls.mjs";
import { buildGoalPairSuite, goalObservation, oneDrop, scoreGoalPairs } from "./stateful_goal_pairs.mjs";

const layoutKey = ({ start, item, walls }) =>
  JSON.stringify([start, item, [...walls].map(p => p.join(",")).sort()]);
const sets = Object.fromEntries(["train", "dev", "scattered", "barrier"].map(split => [split, new Set()]));
for (const seed of [1, 2, 3, 10, 101]) {
  const suite = buildGoalPairSuite(seed);
  assert.deepEqual(suite, buildGoalPairSuite(seed), "seed fixes the full manifest");
  for (const [split, groups] of Object.entries(suite.splits)) {
    assert.equal(groups.length, 6);
    assert.match(suite.manifest.familyHashes[split], /^[0-9a-f]{64}$/);
    assert.equal(suite.manifest.generation[split].oracleQueries, 12);
    for (const [a, b] of groups) {
      assert.equal(layoutKey(a), layoutKey(b));
      assert.equal(a.maxSteps, b.maxSteps);
      assert.notDeepEqual(a.start, a.item);
      assert.notDeepEqual(a.goal, b.goal);
      assert.equal(oracle(a).length, a.maxSteps);
      assert.equal(oracle(b).length, b.maxSteps);
      sets[split].add(layoutKey(a));
      if (split === "scattered") assert.ok(a.walls.length < 4);
      if (split === "barrier") assert.ok(a.walls.length >= 4);
    }
  }
}
for (const [split, layouts] of Object.entries(sets))
  for (const [other, otherLayouts] of Object.entries(sets))
    if (split < other) assert.ok([...layouts].every(key => !otherLayouts.has(key)));

const suite = buildGoalPairSuite(10, 2);
function canDeliver(task, state) {
  const queue = [state], visited = new Set();
  for (const s of queue) {
    if (s.done) continue;
    const key = [s.agent.join(","), s.steps].join(":");
    if (visited.has(key)) continue;
    visited.add(key);
    // The item is already carried. Search using the actual simulator.
    for (const action of [0, 1, 2, 3, 5]) {
      const result = oneDrop(task, s, action);
      if (result.success) return true;
      if (!result.done) queue.push(result.state);
    }
  }
  return false;
}

for (const groups of Object.values(suite.splits)) {
  for (const tasks of groups) {
    const allowed = tasks.map(task => {
      const path = oracle(task);
      let state = initial(task);
      for (const action of path) {
        state = transition(task, state, action).state;
        if (state.carrying) break;
      }
      return ALLOWED.slice(0, 4).filter(action =>
        canDeliver(task, oneDrop(task, state, action).state));
    });
    assert.ok(allowed[0].length && allowed[1].length);
    assert.ok(allowed[0].every(action => !allowed[1].includes(action)),
      "goals require disjoint first carry moves, including ties");
    const fixedPath = oracle(tasks[0]);
    const witness = scoreGoalPairs([tasks], () => {
      let i = 0;
      return { act: () => fixedPath[i++] };
    }, { mode: "blind", seed: 9, repeats: 2 });
    assert.equal(witness.success, 0.5, "one fixed route reaches exactly one goal");
    assert.equal(witness.maxGoalsPerRepeat, 1);
  }
}
const [a, b] = suite.splits.barrier[0];
assert.throws(() => scoreGoalPairs([[a, { ...b, maxSteps: b.maxSteps + 1 }]],
  () => new PublicMazeHeuristic(), { seed: 1, repeats: 1 }), /counterfactual/);
assert.throws(() => {
  let calls = 0;
  scoreGoalPairs([[a, b]], () => ({ act: () => calls++ % 2 }), {
    mode: "blind", seed: 1, repeats: 1 });
}, /trajectories differ/);
assert.throws(() => buildGoalPairSuite(-1), /invalid/);
const random = scoreGoalPairs(suite.splits.barrier, seed => {
  const R = rng(seed);
  return { act: () => ALLOWED[Math.floor(R() * ALLOWED.length)] };
}, { mode: "blind", seed: 7, repeats: 20 });
assert.ok(random.success <= 0.5);
assert.equal(random.episodes, 80);

const t = { start: [0, 0], item: [0, 0], goal: [1, 0], walls: [], maxSteps: 3 };
const carrying = transition(t, initial(t), 4).state;
const wrong = oneDrop(t, carrying, 5);
assert.equal(wrong.done, true);
assert.equal(wrong.state.done, true);
assert.equal(wrong.reward, -0.2);
assert.equal(transition(t, carrying, 5).done, false, "legacy world still permits retry");
assert.equal(oneDrop(t, initial(t), 5).done, false, "empty drop does not expend the item");
const moved = oneDrop(t, carrying, 1).state;
assert.equal(oneDrop(t, moved, 5).success, true, "final-step delivery is allowed");
assert.equal(oneDrop(t, oneDrop(t, carrying, 3).state, 5).done, true, "final-step wrong drop");

const sense = observe(t, initial(t));
const counterfactual = observe({ ...t, goal: [0, 0] }, initial(t));
assert.deepEqual(goalObservation(sense, "blind"), goalObservation(counterfactual, "blind"));
assert.equal(counterfactual[81], 1, "adapter preserves source observation");
const relative = goalObservation(sense, "relative");
assert.equal(relative[55], 1);
assert.equal(relative[63], 1);
assert.equal(relative.slice(50, 75).reduce((sum, value) => sum + value, 0), 2);
assert.deepEqual(relative.slice(0, 50), sense.slice(0, 50));
assert.deepEqual(relative.slice(75), sense.slice(75));
const shift = { ...t, start: [2, 2], item: [2, 2], goal: [3, 2] };
assert.deepEqual(goalObservation(observe(shift, initial(shift)), "relative").slice(50, 75),
  relative.slice(50, 75), "goal offsets survive translation");
assert.throws(() => goalObservation(sense, "other"), /unknown/);
console.log("goal-pair fixtures: disjoint layouts and first moves, frozen ceiling, relative sensing OK");
