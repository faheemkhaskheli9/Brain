// Audits the candidate-level oracle budget and the separation of privileged feedback.
import assert from "node:assert/strict";
import { generate, violation } from "./construct.mjs";
import { library, penalty, score } from "./novelty.mjs";
import { ARMS, compareFair, mutate, randomLegal, rng, runTask } from "./novelty_fair.mjs";
const known = library(3), task = generate(3, "eval", 1).tasks[0];
assert.ok(known.length > 0);
assert.deepEqual(ARMS, ["random-valid", "retrieval", "mutate-blind", "search-binary", "search-graded"]);
assert.throws(() => runTask(task, 0, rng(1), known, "random-valid"), /budget/);
assert.throws(() => runTask(task, 2, rng(1), [], "retrieval"), /empty/);
assert.throws(() => runTask(task, 2, rng(1), known, "unknown"), /unknown/);
for (let i = 0, R = rng(17); i < 200; i++) {
  const candidates = [randomLegal(R, task.budget), mutate(R, known[i % known.length], task.budget)];
  for (const c of candidates) {
    assert.ok(c.length >= 1 && c.length <= task.budget);
    assert.equal(new Set(c).size, c.length);
    assert.ok(c.every(n => Number.isInteger(n) && n >= 0 && n < 6));
  }
}
for (const arm of ARMS) {
  let checks = 0, grades = 0;
  const res = runTask(task, 8, rng(1), known, arm, {
    validator(t, c) { checks++; return violation(t, c); },
    grader(t, c) { grades++; return penalty(t, c); },
  });
  assert.equal(checks, 8, arm);
  assert.equal(grades, arm === "search-graded" ? 8 : 0, arm);
  assert.equal(res.validatorCalls, 8);
  assert.equal(res.gradedCalls, grades);
  assert.equal(res.trace.length, 8);
  const expected = score(task, res.trace.map(x => x.candidate), known);
  assert.equal(res.valid, expected.valid);
  assert.equal(res.novel, expected.novel);
  assert.deepEqual(res, runTask(task, 8, rng(1), known, arm));
}
assert.doesNotThrow(() => runTask(task, 4, rng(42), known, "search-binary", {
  grader() { throw new Error("privileged access"); },
}));
assert.throws(() => runTask(task, 4, rng(42), known, "search-graded", {
  validator() { return "injected failure"; }, grader() { return 0; },
}), /disagrees/);
const a = compareFair(3, { tasks: 10, budget: 8 }), b = compareFair(3, { tasks: 10, budget: 8 });
assert.deepEqual(a.rows.map(x => x.scores), b.rows.map(x => x.scores));
assert.deepEqual(a.audit, b.audit);
assert.equal(a.rows.length, ARMS.length);
assert.equal(a.audit.length, ARMS.length * 10);
for (const r of a.rows) {
  assert.equal(r.scores.validatorCalls, 8);
  assert.equal(r.scores.gradedCalls, r.arm === "search-graded" ? 8 : 0);
}
assert.equal(a.rows.find(r => r.arm === "retrieval").scores.novel, 0);
console.log("fair novelty: ok");
