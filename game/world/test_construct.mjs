// Construction tasks (#110): determinism, validity, many solutions, held-out splits, impossible
// constraints, degenerate drawings, flip equivariance. Run: node game/world/test_construct.mjs
import assert from "node:assert/strict";
import { SPLITS, PROVENANCE, assertDisjoint, comboKey, generate, solutions, valid, violation, distinct, feasible, flipTask, flipDrawing } from "./construct.mjs";

assertDisjoint();
assert.ok(PROVENANCE.primitives.startsWith("supplied") && PROVENANCE.learned.startsWith("nothing"));

// Deterministic: same (seed, split) -> same tasks; another seed differs.
const a = generate(3, "train", 40), b = generate(3, "train", 40);
assert.deepEqual(a, b);
assert.notDeepEqual(a.tasks, generate(4, "train", 40).tasks);

// Held-out combinations: every eval task is in an eval combination and never a train one.
for (const split of ["train", "eval"]) {
  const { tasks } = generate(1, split, 60);
  assert.equal(tasks.length, 60);
  for (const t of tasks) {
    assert.ok(SPLITS[split].includes(comboKey(t)), `${t.id} left ${split}`);
    assert.ok(!Object.entries(SPLITS).some(([n, k]) => n !== split && k.includes(comboKey(t))));
    assert.ok(feasible(t), `${t.id} has no solution`);
  }
}

// Multiple solutions are valid; the validator agrees with the enumerator on every subset.
let multi = 0;
for (const t of generate(2, "train", 60).tasks.concat(generate(2, "eval", 60).tasks)) {
  const sols = solutions(t);
  for (const s of sols) assert.equal(violation(t, s), null);
  if (sols.length >= 2) { multi++; assert.ok(distinct(t, sols.slice(0, 2))); }
  assert.ok(!distinct(t, [sols[0], [...sols[0]].reverse()]), "a reordering is not a new drawing");
}
assert.ok(multi > 0, "some tasks have more than one solution");

// Impossible constraints are detected, not repaired.
const none = { id: "x", kind: "combine", axis: "lr", budget: 1, points: [[0, 0], [4, 0]] };   // left bar is not lr-symmetric
assert.equal(solutions(none).length, 0);
assert.equal(feasible({ id: "y", kind: "connect", axis: null, budget: 1, points: [[0, 0], [4, 4], [0, 4], [4, 0]] }), false);

// Degenerate drawings fail with a reason.
const t = { id: "t", kind: "symmetry", axis: "lr", budget: 2, points: [] };
assert.equal(violation(t, []), "empty drawing");
assert.equal(violation(t, [0, 0]), "repeated stroke");
assert.equal(violation(t, [0, 1, 3]), "over the stroke budget");
assert.equal(violation(t, [9]), "unknown stroke");
assert.equal(violation(t, "TT"), "not a list of strokes");
assert.match(violation(t, [2]), /not lr-symmetric/);
assert.equal(valid(t, [0, 3]), true);

// Flip equivariance: flipping task and drawing together never changes validity.
for (const tk of generate(5, "train", 40).tasks.concat(generate(5, "eval", 40).tasks))
  for (let m = 1; m < 64; m++) {
    const s = [0, 1, 2, 3, 4, 5].filter(i => m >> i & 1);
    assert.equal(valid(flipTask(tk), flipDrawing(s)), valid(tk, s), `${tk.id} ${s}`);
  }
console.log(`construct: ok (${multi} multi-solution tasks of 120)`);
