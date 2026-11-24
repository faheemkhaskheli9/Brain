import assert from "node:assert/strict";
import { GOALS } from "./stateful_credit_protocol.mjs";
import { makeModel } from "./stateful_credit_protocol.mjs";
import { score, train } from "./matched_step_credit_protocol.mjs";
import { ARMS, OWN_ETAS, WIDE, WIDE_ARMS, assertWide, ownStep, wideSelect, wideTransfer }
  from "./own_step_transfer_protocol.mjs";

// Wide split: 19 trained cells, 5 interior heldout cells, start excluded, disjoint.
assertWide();
assert.equal(WIDE.train.length, 19);
assert.ok(OWN_ETAS.length === 10 && Math.max(...OWN_ETAS) === 0.512);

// Goal-blind ceiling holds on the wide split: <= 1 goal per repeat, success <= 1/k.
for (const seed of [2, 3]) {
  const m = makeModel(seed, "mask-goal");
  train(m, "mask-goal", "train", seed, 600, 0.008, WIDE);
  for (const split of ["train", "heldout"]) {
    const sc = score(m, "mask-goal", split, 12, seed, WIDE);
    assert.ok(sc.maxGoalsPerRepeat <= 1 && sc.success <= 1 / WIDE[split].length + 1e-12, split);
    assert.equal(sc.goalBlindCeiling, 1 / WIDE[split].length);
  }
}

// flag-only sees the at-goal flag but not the goal plane, and trains on the wide split.
const f = makeModel(4, "native");
const t = train(f, "flag-only", "train", 4, 50, 0.004, WIDE);
assert.ok(t.maxStepRelDev < 1e-9);
assert.deepEqual(Object.keys(score(f, "flag-only", "heldout", 1, 4, WIDE).perGoal).sort(),
  WIDE.heldout.map(p => p.join(",")).sort());

// Part A: each arm is evaluated at its own selected eta.
const a = ownStep({ seeds: [1], devSeeds: [101], etas: [0.004, 0.064], budget: 30, repeats: 1 });
const evals = a.rows.filter(r => r.split === "own-eval");
assert.equal(evals.length, ARMS.length);
for (const arm of ARMS) assert.ok(evals.some(r => r.arm === `${arm}@eta${a.ownEta[arm]}`), arm);
assert.equal(a.rows.filter(r => r.split === "own-selection").length, ARMS.length * 2);

// Part B: native-only selection on trained goals; heldout never scored during selection.
const s = wideSelect({ seeds: [101], etas: [0.004, 0.008], budget: 30, repeats: 1 });
assert.ok(s.rows.every(r => r.split === "wide-selection" && r.arm.startsWith("native@") &&
  Object.keys(r.scores.dev.perGoal).length === 19));
const b = wideTransfer({ seeds: [1], devSeeds: [101], etas: [0.004], budget: 30, repeats: 1 });
const w = b.rows.filter(r => r.split === "wide-eval");
assert.deepEqual(w.map(r => r.arm), WIDE_ARMS.map(arm => `${arm}@eta0.004`));
assert.ok(w.every(r => r.status === "ok" && r.scores.after.heldout.episodes === 5));
assert.equal(w.find(r => r.arm.startsWith("mask-goal")).scores.goalSensitivity.carryingL1, 0);
assert.equal(GOALS.train.length, 3, "Round 29 split unchanged");
console.log("own-step transfer protocol tests passed");
