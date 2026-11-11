// Research-only goal-conditioned construction policy baseline (#112).
// Reuses Brain World's backprop-free local actor-critic; no options or oracle solver.
// Supplied: six strokes, submit action, task-to-sensor encoding, validator and reward.
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import { Brain, N_IN, PEN, ACT_SETS } from "./brain.js";
import { assertDisjoint, generate, valid } from "./construct.mjs";
import { library, pictureClass } from "./novelty.mjs";
import { randomLegal, rng } from "./novelty_fair.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

export const SUBMIT = 4; // the existing grasp action is repurposed as submit
export const ALLOWED = Object.freeze([SUBMIT, ...ACT_SETS[2]]);
export const ARMS = Object.freeze(["learner", "goal-masked", "learning-off", "random-valid"]);
export const PROVENANCE = Object.freeze({
  learner: "Brain local three-factor actor-critic; fixed random expansion; no backprop",
  supplied: "goal sensor map, six stroke primitives, submit, validator/reward and split grammar",
  missing: "learned options, episodic memory retrieval, world model, planning, open-ended creativity",
});

// Points -> fovea, symmetry axis -> cochlea, budget -> leg channels,
// already drawn strokes -> pen-pad sensors. No hidden solution or penalty.
export function observation(task, strokes, revealGoal = true) {
  const x = new Float32Array(N_IN);
  x[45] = task.budget / PEN.length;
  x[46] = (task.budget - strokes.length) / PEN.length;
  x[81] = 1;
  if (revealGoal) {
    const axis = { lr: 0, ud: 1, rot: 2 }[task.axis];
    if (axis !== undefined) x[47 + axis] = 1;
    for (const [r, c] of task.points) x[50 + r * 5 + c] = 1;
  }
  for (const s of strokes) x[75 + s] = 1;
  return x;
}

export function playEpisode(brain, task, { learn = true, revealGoal = true } = {}) {
  const prevLearn = brain.learning, prevGreedy = brain.greedy;
  brain.learning = learn; brain.greedy = false;
  const strokes = [];
  try {
    for (let n = 0; n <= task.budget; n++) {
      const h = brain.encode(observation(task, strokes, revealGoal), 0);
      const action = brain.act(h, ALLOWED);
      if (!ALLOWED.includes(action)) throw new Error("invalid construction action");
      if (action !== SUBMIT) strokes.push(action - 5);
      const done = action === SUBMIT || strokes.length >= task.budget;
      if (done) {
        const success = valid(task, strokes);
        brain.learn(success ? 1 : -0.2, null);
        return { success, strokes, decisions: n + 1 };
      }
      brain.learn(-0.005, brain.encode(observation(task, strokes, revealGoal), 0));
    }
    throw new Error("construction failed to terminate within stroke budget");
  } finally {
    brain.learning = prevLearn; brain.greedy = prevGreedy;
  }
}

export function weightDigest(brain) {
  return createHash("sha256").update(Buffer.from(brain.P.buffer))
    .update(Buffer.from(brain.v.buffer)).digest("hex");
}
export function frozenScore(brain, tasks, repeats, { revealGoal = true, seen = new Set() } = {}) {
  if (!Number.isInteger(repeats) || repeats < 1 || !tasks.length)
    throw new Error("positive evaluation workload required");
  const before = weightDigest(brain);
  let success = 0, novel = 0, decisions = 0;
  for (const task of tasks) for (let i = 0; i < repeats; i++) {
    const episode = playEpisode(brain, task, { learn: false, revealGoal });
    decisions += episode.decisions;
    if (episode.success) {
      success++;
      if (!seen.has(pictureClass(episode.strokes))) novel++;
    }
  }
  if (weightDigest(brain) !== before) throw new Error("frozen evaluation changed weights");
  return { success: success / (tasks.length * repeats), novel: novel / (tasks.length * repeats),
    decisions, episodes: tasks.length * repeats };
}

export function runSeed(seed, { trainSteps = 10000, trainTasks = 64, evalTasks = 30, repeats = 5 } = {}) {
  if (![seed, trainSteps, trainTasks, evalTasks, repeats].every(Number.isInteger) || seed < 0 ||
      trainSteps < 1 || trainTasks < 1 || evalTasks < 1 || repeats < 1)
    throw new Error("invalid experiment configuration");
  assertDisjoint();
  const train = generate(seed, "train", trainTasks).tasks;
  const eval_ = generate(seed, "eval", evalTasks).tasks;
  if (train.length !== trainTasks || eval_.length !== evalTasks)
    throw new Error("incomplete task generation");
  const known = new Set(library(seed).map(pictureClass)), rows = [];
  for (const arm of ARMS) {
    const started = Date.now();
    if (arm === "random-valid") {
      const R = rng(seed * 101 + 13);
      let wins = 0, novel = 0;
      for (const task of eval_) for (let i = 0; i < repeats; i++) {
        const strokes = randomLegal(R, task.budget);
        if (valid(task, strokes)) {
          wins++;
          if (!known.has(pictureClass(strokes))) novel++;
        }
      }
      rows.push(run({ arm, seed, split: "eval", status: "ok", seconds: (Date.now() - started) / 1000,
        scores: { train: { success: null },
          heldout: { success: wins / (evalTasks * repeats), novel: novel / (evalTasks * repeats) },
          trainSteps: 0, trainEpisodes: 0 } }));
      continue;
    }
    const brain = new Brain(rng(seed * 7919 + 41)), chooseTask = rng(seed * 1741 + 17);
    const revealGoal = arm !== "goal-masked", learn = arm !== "learning-off";
    let steps = 0, episodes = 0, correct = 0;
    while (steps < trainSteps) {
      const task = train[Math.floor(chooseTask() * train.length)];
      const outcome = playEpisode(brain, task, { learn, revealGoal });
      steps += outcome.decisions;
      episodes++; correct += outcome.success ? 1 : 0;
    }
    const familiar = frozenScore(brain, train.slice(0, Math.min(evalTasks, train.length)),
      repeats, { revealGoal });
    const heldout = frozenScore(brain, eval_, repeats, { revealGoal, seen: known });
    rows.push(run({ arm, seed, split: "eval", status: "ok", seconds: (Date.now() - started) / 1000,
      scores: { train: { success: familiar.success },
        heldout: { success: heldout.success, novel: heldout.novel },
        trainSteps: steps, trainEpisodes: episodes, trainingSuccess: correct / episodes } }));
  }
  return rows;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2), opt = (flag, def) => {
    const i = args.indexOf(flag);
    return i < 0 ? def : args.splice(i, 2)[1];
  };
  const trainSteps = Number(opt("--train-steps", "10000")),
    trainTasks = Number(opt("--train-tasks", "64")),
    evalTasks = Number(opt("--eval-tasks", "30")),
    repeats = Number(opt("--repeats", "5")), out = opt("--out", null);
  const seeds = args.length ? args.map(Number) : [1, 2, 3];
  if (!seeds.length || seeds.some(s => !Number.isInteger(s) || s < 0) ||
      new Set(seeds).size !== seeds.length) throw new Error("invalid seeds");
  const runs = seeds.flatMap(seed => runSeed(seed, { trainSteps, trainTasks, evalTasks, repeats }));
  for (const arm of ARMS) {
    const cohort = runs.filter(r => r.arm === arm);
    const avg = k => cohort.reduce((s, r) => s + r.scores.heldout[k], 0) / cohort.length;
    console.log(arm.padEnd(15), "held-out", avg("success").toFixed(3),
      "novel", avg("novel").toFixed(3));
  }
  if (out) writeResult(out, resultRecord({
    experiment: "brain-world/construction-learner", baseline: "learning-off", runs,
    metrics: { "heldout.success": "higher", "heldout.novel": "higher",
      "train.success": "higher", trainSteps: "lower" },
    config: { seeds, trainTasks, evalTasks, repeats, arms: ARMS, provenance: PROVENANCE,
      split: "fixed disjoint train/eval constraint families; evaluation frozen",
      limitations: "Pilot baseline only: no learned options, no reversal or adaptation, no held-out task training" },
    budgets: { trainDecisionBudget: trainSteps, evalEpisodesPerArm: evalTasks * repeats },
  }));
}
