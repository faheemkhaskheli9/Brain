import assert from "node:assert/strict";
import { GAINS } from "./brain.js";
import { initial } from "./stateful_construct.mjs";
import { modelDigest } from "./stateful_options.mjs";
import { makeModel, taskFor } from "./stateful_credit_protocol.mjs";
import { ARMS, DEV_SEEDS, ETAS, GOALS, matchedLearn, rollout, runSeed, score, select, step, train }
  from "./matched_step_credit_protocol.mjs";

// One-drop rule: a misplaced drop ends the episode; delivery still succeeds.
const t = taskFor(GOALS.train[0], "train");          // goal [1,1], start/item [2,0]
let s = step(t, initial(t), 4).state;                // pick up
const miss = step(t, s, 5);                          // drop at [2,0], off the goal
assert.equal(miss.reason, "misplaced");
assert.ok(miss.done && miss.state.done && !miss.success);
s = step(t, step(t, s, 0).state, 3).state;           // west, south -> [1,1]
const hit = step(t, s, 5);
assert.ok(hit.success && hit.done);

// Matched step: learn() applies exactly eta, for every arm, whatever the hidden width.
const lr = [GAINS.lrP, GAINS.lrV];
for (const arm of ARMS) {
  const m = makeModel(11, arm);
  const x = train(m, arm, "train", 11, 60, 0.008);
  assert.ok(x.maxStepRelDev < 1e-9, `${arm} step is matched`);
  assert.ok(Math.abs(x.meanActorStep - 0.008) < 1e-12, arm);
  assert.deepEqual([GAINS.lrP, GAINS.lrV], lr, "gains restored");
}
assert.throws(() => matchedLearn(makeModel(1, "native").brains[0], 0, 0, null, true), /matched/);
assert.deepEqual([GAINS.lrP, GAINS.lrV], lr);

// Goal-blind ceiling: with common random numbers a goal-masked policy delivers on at most one goal
// per repeat, so its success never exceeds 1/k, trained or not.
for (const seed of [2, 3]) {
  const m = makeModel(seed, "mask-goal");
  train(m, "mask-goal", "train", seed, 400, 0.032);
  for (const split of ["train", "heldout"]) {
    const sc = score(m, "mask-goal", split, 20, seed);
    assert.ok(sc.maxGoalsPerRepeat <= 1, `${split} goal-blind repeat delivers once at most`);
    assert.ok(sc.success <= 1 / GOALS[split].length + 1e-12);
  }
}

// Frozen scoring does not change the learner.
const m = makeModel(9, "native");
train(m, "native", "train", 9, 37, 0.004);
const digest = modelDigest(m);
score(m, "native", "train", 2, 9);
assert.equal(modelDigest(m), digest);

// Selection: eta from native dev rows only; second-best excludes the selected eta; ties -> smaller.
const sel = select({ seeds: [DEV_SEEDS[0]], etas: [0.004, 0.016], budget: 24, repeats: 1 });
assert.equal(sel.rows.length, ARMS.length * 2);
assert.ok(sel.rows.every(r => r.split === "dev-selection" && r.status === "ok"));
assert.equal(new Set(sel.evalEtas).size, 2);
const n = sel.curves.native;
assert.equal(sel.selected, n[1].devSuccess > n[0].devSuccess + 1e-12 ? 0.016 : 0.004);
assert.ok(ETAS.includes(0.064) && ETAS.length === 7);

// End to end: every arm runs at one eta; dev seeds are rejected.
assert.throws(() => runSeed(DEV_SEEDS[0], 0.004, { budget: 5, repeats: 1 }), /disjoint/);
const rows = runSeed(1, 0.004, { budget: 30, repeats: 1 });
assert.deepEqual(rows.map(r => r.arm), ARMS.map(a => `${a}@eta0.004`));
assert.ok(rows.every(r => r.status === "ok" && r.scores.training.decisions === 30));
assert.ok(rows.every(r => r.seconds >= 0));
const mg = rows.find(r => r.arm.startsWith("mask-goal"));
assert.equal(mg.scores.goalSensitivity.carryingL1, 0);
assert.equal(rollout(makeModel(1, "native"), "native", t).decisions > 0, true);
console.log("matched-step credit protocol tests passed");
