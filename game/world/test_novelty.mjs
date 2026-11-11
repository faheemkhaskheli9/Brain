// Validity-gated novelty (#111): exploits score zero, arms are deterministic and budget-matched.
// Run: node game/world/test_novelty.mjs
import assert from "node:assert/strict";
import { generate, solutions } from "./construct.mjs";
import { ARMS, compare, library, penalty, pictureClass, score } from "./novelty.mjs";

const task = { id: "t", kind: "connect", axis: null, budget: 3, points: [[0, 0]] };
const good = solutions(task);
assert.ok(good.length >= 2);

// Exploits: noise, repeats, reordering, empty, over budget and unknown strokes earn nothing.
const junk = [[], [9], [-1], [1.5], ["0"], null, [0, 0], [0, 0, 0, 0], [0, 1, 2, 3], [4, 4]];
assert.equal(score(task, junk).novel, 0);
assert.equal(score(task, junk).valid, 0);
// A reordered or repeated copy of a valid drawing is one drawing, and a known one is not new.
const d = good[0];
assert.equal(score(task, [d, [...d].reverse(), d]).valid, 3);   // all three are valid, only one is a new picture
assert.equal(score(task, [d, [...d].reverse(), d]).novel, 1);
assert.equal(score(task, [d], [d]).novel, 0);
// A pad-mirrored copy of a known picture is the same picture.
assert.equal(pictureClass([0]), pictureClass([1]));        // top bar and bottom bar: a ud flip apart
assert.equal(pictureClass([4]), pictureClass([5]));        // / and \ : an lr mirror apart
assert.notEqual(pictureClass([0]), pictureClass([2]));
assert.equal(pictureClass([]), null);
assert.equal(score({ ...task, points: [] }, [[0], [1]], [[0]]).novel, 0);

// The penalty is zero exactly when the validator accepts.
for (const t of generate(5, "eval", 25).tasks) for (let m = 1; m < 64; m++) {
  const s = [0, 1, 2, 3, 4, 5].filter(i => m >> i & 1);
  assert.equal(penalty(t, s) === 0, solutions(t).some(x => x.join() === s.join()));
}

// Arms: deterministic, and every arm gets exactly `budget` validator calls per task.
const a = compare(3, { tasks: 10, budget: 8 }), b = compare(3, { tasks: 10, budget: 8 });
assert.deepEqual(a.rows.map(r => r.scores), b.rows.map(r => r.scores));
for (const r of a.rows) assert.equal(r.scores.validatorCalls, 8, r.arm);
assert.ok(library(3).length > 0);
assert.deepEqual(Object.keys(ARMS), ["random", "retrieval", "search"]);
// Retrieval only replays the library, so it never earns novelty.
assert.equal(a.rows.find(r => r.arm === "retrieval").scores.novel, 0);
console.log("novelty: ok");
