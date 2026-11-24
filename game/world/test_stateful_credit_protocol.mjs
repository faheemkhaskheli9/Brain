import assert from "node:assert/strict";
import { GAINS, N_IN } from "./brain.js";
import { initial, observe, oracle } from "./stateful_construct.mjs";
import { modelDigest } from "./stateful_options.mjs";
import { ARMS, DEV_SEEDS, GOALS, LAYOUTS, assertGoalSplits, fanInAudit, layout, makeModel,
  rollout, runSeed, score, select, sense, taskFor, train, withScale } from "./stateful_credit_protocol.mjs";

assertGoalSplits();
for (const split of Object.keys(GOALS)) for (const g of GOALS[split]) {
  const path = oracle(taskFor(g, split));
  assert.ok(path && path.length >= 3 && path.length <= 4, "every goal is a short feasible delivery");
}
assert.throws(() => runSeed(DEV_SEEDS[0], 1, { budget: 5, repeats: 1 }), /disjoint/);

// Layouts: distinct targets inside Brain's input; aligned never touches legs or gain inputs.
for (const [name, map] of Object.entries(LAYOUTS)) {
  assert.equal(map.length, 84, name);
  assert.equal(new Set(map).size, 84, name);
  assert.ok(map.every(i => i >= 0 && i < N_IN), name);
}
assert.ok(LAYOUTS.aligned.every(i => i < 47 || i > 49), "aligned keeps gain inputs zero");
assert.equal(LAYOUTS.aligned.filter((v, i) => v !== LAYOUTS.native[i]).length, 3, "one-variable change");
const t0 = taskFor(GOALS.train[0], "train"), x0 = observe(t0, initial(t0));
assert.deepEqual(Array.from(layout(x0, "native")), Array.from(x0), "native layout is identity");
const brain = makeModel(3, "native").brains[0];
assert.equal(fanInAudit(brain, "native").gainIndicesUsed, 3, "native item cells drive gains");
assert.equal(fanInAudit(brain, "aligned").gainInputsLive, 0);
assert.ok(fanInAudit(brain, "aligned").driveInputsLive >= fanInAudit(brain, "native").driveInputsLive);

// Goal mask: different goals give identical sensed input; unmasked arms differ.
const [ga, gb] = GOALS.train.map(g => taskFor(g, "train"));
assert.deepEqual(Array.from(sense(ga, initial(ga), "mask-goal")),
  Array.from(sense(gb, initial(gb), "mask-goal")));
for (const arm of ["native", "aligned"])
  assert.notDeepEqual(Array.from(sense(ga, initial(ga), arm)), Array.from(sense(gb, initial(gb), arm)));

// Scaling is applied inside and restored after, even when the body throws.
const lr = [GAINS.lrP, GAINS.lrV];
withScale(4, () => assert.deepEqual([GAINS.lrP, GAINS.lrV], [lr[0] * 4, lr[1] * 4]));
assert.throws(() => withScale(2, () => { throw new Error("boom"); }), /boom/);
assert.deepEqual([GAINS.lrP, GAINS.lrV], lr);

// no-hidden: only the direct input trunk remains.
const flat = makeModel(5, "no-hidden").brains[0];
const h = flat.encode(sense(ga, initial(ga), "no-hidden"), 0);
assert.ok(h.subarray(flat.nIn).every(v => v === 0));

// Yoked reward: own rewards are ignored, the tape drives a nonzero TD error.
const yoked = makeModel(7, "yoked-reward");
const tape = new Array(12).fill(1);
const y = rollout(yoked, "yoked-reward", ga, { learn: true, tape });
assert.ok(y.tdAbsSum > 0);
assert.equal(y.rewardSum, y.decisions, "yoked arm learns from the tape, not the world");
assert.throws(() => rollout(makeModel(7, "yoked-reward"), "yoked-reward", ga, { learn: true }),
  /tape/);

// Exact training budget; frozen scoring never changes the learner.
const m = makeModel(9, "native");
const t = train(m, "native", "train", 9, 37);
assert.equal(t.decisions, 37);
assert.equal(t.rewards.length, 37);
const digest = modelDigest(m);
const s = score(m, "native", "heldout", 2, 9);
assert.equal(s.episodes, GOALS.heldout.length * 2);
assert.equal(modelDigest(m), digest, "frozen scoring mutated the learner");

// Selection ties resolve to the smaller scale; rows are dev-only.
const sel = select({ seeds: [101], scales: [1, 2], budget: 3, repeats: 1 });
assert.ok(sel.rows.every(r => r.split === "dev-selection"));
if (sel.byScale[0].devSuccess === sel.byScale[1].devSuccess) assert.equal(sel.selected, 1);

// Every arm runs end to end and reports a primary score.
const rows = runSeed(1, 1, { budget: 20, repeats: 1 });
assert.deepEqual(rows.map(r => r.arm), ARMS.map(a => `${a}@x1`));
for (const r of rows) {
  assert.equal(r.status, "ok", r.reason);
  assert.equal(r.scores.training.decisions, 20);
  assert.equal(r.scores.onlineOracleQueries, 0);
  assert.equal(r.scores.primary, r.scores.after.train);
}
const mg = rows.find(r => r.arm === "mask-goal@x1").scores.goalSensitivity;
assert.equal(mg.startL1, 0); assert.equal(mg.carryingL1, 0);
console.log("stateful credit protocol tests passed");
