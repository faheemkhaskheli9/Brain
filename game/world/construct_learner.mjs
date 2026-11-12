// Research-only goal-conditioned construction policy baseline (#112).
// Reuses Brain World's backprop-free local actor-critic; no options or oracle solver.
// Supplied: six strokes, submit action, task-to-sensor encoding, validator and reward.
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import { Brain, N_IN, PEN, ACT_SETS } from "./brain.js";
import { assertDisjoint, generate, valid, solutions } from "./construct.mjs";
import { pictureClass } from "./novelty.mjs";
import { randomLegal, rng } from "./novelty_fair.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

export const SUBMIT = 4; // the existing grasp action is repurposed as submit
export const ALLOWED = Object.freeze([SUBMIT, ...ACT_SETS[2]]);
export const ARMS = Object.freeze(["learner", "learner-legal", "goal-masked",
  "learning-off", "random-raw", "random-valid"]);
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

// Goal-blind legality: excludes strokes already used, but cannot inspect the
// target's required cells, symmetry or any verifier result. Optional by design.
export const legalActions = (strokes, mask = false) =>
  mask ? ALLOWED.filter(a => a === SUBMIT || !strokes.includes(a - 5)) : ALLOWED;

export function playEpisode(brain, task, {
  learn = true, revealGoal = true, legalMask = false, evalSeed = null, greedy = false,
} = {}) {
  const prevLearn = brain.learning, prevGreedy = brain.greedy, prevRand = brain.rand;
  brain.learning = learn; brain.greedy = !learn && greedy;
  // A frozen trial must not advance the training policy's random stream.
  if (!learn && evalSeed !== null) brain.rand = rng(evalSeed);
  const strokes = [];
  let repeated = 0;
  try {
    for (let n = 0; n <= task.budget; n++) {
      const h = brain.encode(observation(task, strokes, revealGoal), 0);
      const allowed = legalActions(strokes, legalMask);
      const action = brain.act(h, allowed);
      if (!allowed.includes(action)) throw new Error("invalid construction action");
      if (action !== SUBMIT) {
        if (strokes.includes(action - 5)) repeated++;
        strokes.push(action - 5);
      }
      const done = action === SUBMIT || strokes.length >= task.budget;
      if (done) {
        const success = valid(task, strokes);
        brain.learn(success ? 1 : -0.2, null);
        return { success, strokes, decisions: n + 1, repeated };
      }
      brain.learn(-0.005, brain.encode(observation(task, strokes, revealGoal), 0));
    }
    throw new Error("construction failed to terminate within stroke budget");
  } finally {
    brain.learning = prevLearn; brain.greedy = prevGreedy; brain.rand = prevRand;
  }
}

// Include traces and learned sensory parameters, not just actor and critic.
export function weightDigest(brain) {
  const hash = createHash("sha256");
  for (const key of ["P", "v", "ev", "eP", "wIn", "bias", "gate", "proto", "uses"]) {
    const array = brain[key];
    if (array && ArrayBuffer.isView(array))
      hash.update(Buffer.from(array.buffer, array.byteOffset, array.byteLength));
  }
  return hash.digest("hex");
}
const hashSeed = s => {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619);
  return h >>> 0;
};
// Stable per-task trial streams make scoring independent of episode order and
// of earlier train-set evaluation, without learning from frozen examples.
export const trialSeed = (seed, task, repeat) =>
  hashSeed(`${seed}/${task.id ?? JSON.stringify(task)}/${repeat}`);

export function frozenScore(brain, tasks, repeats, {
  revealGoal = true, seen = new Set(), legalMask = false, seed = 0, greedy = false,
} = {}) {
  if (!Number.isInteger(repeats) || repeats < 1 || !tasks.length)
    throw new Error("positive evaluation workload required");
  const before = weightDigest(brain), observed = new Set(seen);
  const old = { h: brain.h, dopamine: brain.dopamine,
    nActive: brain.nActive, nEncode: brain.nEncode, pi: brain.pi?.slice() };
  let success = 0, novel = 0, decisions = 0, repeated = 0;
  try {
    for (const task of tasks) for (let i = 0; i < repeats; i++) {
      const episode = playEpisode(brain, task, { learn: false, revealGoal, legalMask,
        greedy, evalSeed: trialSeed(seed, task, i) });
      decisions += episode.decisions; repeated += episode.repeated;
      if (episode.success) {
        success++;
        const cls = pictureClass(episode.strokes);
        if (!observed.has(cls)) { observed.add(cls); novel++; }
      }
    }
  } finally {
    brain.h = old.h; brain.dopamine = old.dopamine;
    brain.nActive = old.nActive; brain.nEncode = old.nEncode;
    if (old.pi) brain.pi.set(old.pi);
  }
  if (weightDigest(brain) !== before) throw new Error("frozen evaluation changed learner state");
  return { success: success / (tasks.length * repeats), novel: novel / (tasks.length * repeats),
    repeatedPerEpisode: repeated / (tasks.length * repeats),
    decisions, episodes: tasks.length * repeats };
}

// Sequential random actor with exactly the learner's action/termination rules.
// Unlike random-valid, it may waste a decision submitting an empty drawing or
// repeat a stroke. Both baselines are retained, and are never called learned.
export function randomEpisode(task, R, legalMask = false) {
  const strokes = [];
  let repeated = 0;
  for (let n = 0; n <= task.budget; n++) {
    const allowed = legalActions(strokes, legalMask);
    const action = allowed[Math.floor(R() * allowed.length)];
    if (action !== SUBMIT) {
      if (strokes.includes(action - 5)) repeated++;
      strokes.push(action - 5);
    }
    if (action === SUBMIT || strokes.length >= task.budget)
      return { success: valid(task, strokes), strokes, decisions: n + 1, repeated };
  }
  throw new Error("random construction exceeded stroke budget");
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
  // Novelty excludes every solution of every train task, not a sampled memory subset.
  // This deliberately makes the tiny 63-drawing task a strict novelty test.
  const known = new Set(train.flatMap(task => solutions(task)).map(pictureClass)), rows = [];
  for (const arm of ARMS) {
    const started = Date.now();
    if (arm === "random-valid" || arm === "random-raw") {
      const R = rng(seed * 101 + 13);
      let wins = 0, novel = 0, repeated = 0, decisions = 0;
      const observed = new Set(known);
      for (const task of eval_) for (let i = 0; i < repeats; i++) {
        const ep = arm === "random-valid"
          ? { strokes: randomLegal(R, task.budget), decisions: 1, repeated: 0 }
          : randomEpisode(task, rng(trialSeed(seed, task, i)));
        const { strokes } = ep;
        repeated += ep.repeated; decisions += ep.decisions;
        if (valid(task, strokes)) {
          wins++;
          const cls = pictureClass(strokes);
          if (!observed.has(cls)) { observed.add(cls); novel++; }
        }
      }
      rows.push(run({ arm, seed, split: "eval", status: "ok", seconds: (Date.now() - started) / 1000,
        scores: { train: { success: null },
          heldout: { success: wins / (evalTasks * repeats), novel: novel / (evalTasks * repeats),
            repeatedPerEpisode: repeated / (evalTasks * repeats), decisions },
          trainSteps: 0, trainEpisodes: 0 } }));
      continue;
    }
    const brain = new Brain(rng(seed * 7919 + 41)), chooseTask = rng(seed * 1741 + 17);
    const revealGoal = arm !== "goal-masked", learn = arm !== "learning-off";
    const legalMask = arm === "learner-legal";
    let steps = 0, episodes = 0, correct = 0, repeated = 0;
    while (steps < trainSteps) {
      const task = train[Math.floor(chooseTask() * train.length)];
      const outcome = playEpisode(brain, task, { learn, revealGoal, legalMask });
      steps += outcome.decisions; repeated += outcome.repeated;
      episodes++; correct += outcome.success ? 1 : 0;
    }
    const familiar = frozenScore(brain, train.slice(0, Math.min(evalTasks, train.length)),
      repeats, { revealGoal, legalMask, seed });
    const heldout = frozenScore(brain, eval_, repeats,
      { revealGoal, legalMask, seed, seen: known });
    rows.push(run({ arm, seed, split: "eval", status: "ok", seconds: (Date.now() - started) / 1000,
      scores: { train: { success: familiar.success },
        heldout: { success: heldout.success, novel: heldout.novel,
          repeatedPerEpisode: heldout.repeatedPerEpisode, decisions: heldout.decisions },
        trainSteps: steps, trainEpisodes: episodes, trainingSuccess: correct / episodes,
        trainingRepeatedPerEpisode: repeated / episodes } }));
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
      evaluation: "per-task/repeat independent RNG, restored learner state, sampled policy",
      limitations: "Diagnostic pilot: no options, no reversal or adaptation, 63 nonempty stroke subsets; random-valid is an engineered legal-action control" },
    budgets: { trainDecisionBudget: trainSteps, evalEpisodesPerArm: evalTasks * repeats },
  }));
}
