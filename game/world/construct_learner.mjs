// Research-only goal-conditioned construction policy baseline (#112).
// Reuses Brain World's backprop-free local actor-critic; no options or oracle solver.
// Supplied: six strokes, submit action, task-to-sensor encoding, validator and reward.
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import { Brain, N_IN, PEN, ACT_SETS, rng as evaluationRng } from "./brain.js";
import { assertDisjoint, generate, valid, solutions } from "./construct.mjs";
import { pictureClass } from "./novelty.mjs";
import { randomLegal, rng } from "./novelty_fair.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

export const SUBMIT = 4; // the existing grasp action is repurposed as submit
export const ALLOWED = Object.freeze([SUBMIT, ...ACT_SETS[2]]);
export const ARMS = Object.freeze(["learner", "learner-masked", "goal-masked", "learning-off", "random-step-raw", "random-step-masked", "random-valid"]);
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


/** Syntactic history-only mask. It never consults the target or validator. */
export function legalActions(strokes, maskHistory = false) {
  return maskHistory ? [SUBMIT, ...ACT_SETS[2].filter(a => !strokes.includes(a - 5))] : ALLOWED;
}

export function playEpisode(brain, task, { learn = true, revealGoal = true,
  maskHistory = false, greedy = false, maxDecisions = task.budget } = {}) {
  if (!Number.isInteger(maxDecisions) || maxDecisions < 1)
    throw new Error("positive decision budget required");
  const prevLearn = brain.learning, prevGreedy = brain.greedy;
  brain.learning = learn; brain.greedy = greedy;
  const strokes = [], actions = [];
  let duplicateActions = 0;
  try {
    for (let n = 0; n < Math.min(task.budget, maxDecisions); n++) {
      const h = brain.encode(observation(task, strokes, revealGoal), 0);
      const allowed = legalActions(strokes, maskHistory), action = brain.act(h, allowed);
      if (!allowed.includes(action)) throw new Error("invalid construction action");
      actions.push(action);
      if (action !== SUBMIT) {
        if (strokes.includes(action - 5)) duplicateActions++;
        strokes.push(action - 5);
      }
      // The final partial training episode is censored, never a lucky early submission.
      const truncated = action !== SUBMIT && n + 1 === maxDecisions && n + 1 < task.budget;
      if (action === SUBMIT || strokes.length >= task.budget || truncated) {
        const success = !truncated && valid(task, strokes);
        brain.learn(success ? 1 : -0.2, null);
        return { success, strokes, actions, decisions: n + 1, duplicateActions,
          emptySubmit: action === SUBMIT && !strokes.length, validatorCalls: truncated ? 0 : 1,
          truncated };
      }
      brain.learn(-0.005, brain.encode(observation(task, strokes, revealGoal), 0));
    }
    throw new Error("construction failed to terminate within stroke budget");
  } finally {
    brain.learning = prevLearn; brain.greedy = prevGreedy;
  }
}

/** A random policy that interacts with the same submit and per-step protocol. */
export function randomEpisode(R, task, { maskHistory = false } = {}) {
  const strokes = [], actions = [];
  let duplicateActions = 0;
  for (let n = 0; n < task.budget; n++) {
    const allowed = legalActions(strokes, maskHistory);
    const action = allowed[Math.floor(R() * allowed.length)];
    actions.push(action);
    if (action !== SUBMIT) {
      if (strokes.includes(action - 5)) duplicateActions++;
      strokes.push(action - 5);
    }
    if (action === SUBMIT || strokes.length >= task.budget) return {
      success: valid(task, strokes), strokes, actions, decisions: n + 1,
      duplicateActions, emptySubmit: action === SUBMIT && !strokes.length,
      validatorCalls: 1, truncated: false,
    };
  }
  throw new Error("stepwise random episode did not terminate");
}

export function weightDigest(brain) {
  // Cover all observable typed-array state, not just actor and critic weights.
  const hash = createHash("sha256");
  for (const key of ["P", "v", "ev", "eP", "wIn", "bias", "gate", "proto", "uses",
    "fast", "slow"]) {
    const a = brain[key];
    if (a && ArrayBuffer.isView(a))
      hash.update(Buffer.from(a.buffer, a.byteOffset, a.byteLength));
  }
  return hash.digest("hex");
}

/** Evaluation copies every mutable field, including traces, policy and metrics, not only weights. */
export function evaluationCopy(brain, seed = 1) {
  if (!Number.isInteger(seed)) throw new Error("evaluation seed must be integer");
  const detached = Object.create(Object.getPrototypeOf(brain));
  for (const [k, v] of Object.entries(brain)) {
    if (k !== "rand") detached[k] = typeof v === "function" ? v : structuredClone(v);
  }
  detached.rand = evaluationRng(seed);
  return detached;
}

function summarize(tasks, repeats, seen, next) {
  if (!Number.isInteger(repeats) || repeats < 1 || !tasks.length)
    throw new Error("positive evaluation workload required");
  const observed = new Set(seen), possible = tasks.map(t =>
    solutions(t).some(s => !seen.has(pictureClass(s))));
  let wins = 0, novel = 0, conditionalNovel = 0, decisions = 0, calls = 0,
    duplicates = 0, empty = 0;
  const audit = [];
  for (let t = 0; t < tasks.length; t++) for (let r = 0; r < repeats; r++) {
    const x = next(tasks[t], r);
    decisions += x.decisions; calls += x.validatorCalls || 0;
    duplicates += x.duplicateActions || 0; empty += x.emptySubmit ? 1 : 0;
    let newPicture = false;
    if (x.success) {
      wins++;
      const cls = pictureClass(x.strokes);
      if (!observed.has(cls)) {
        observed.add(cls); novel++; newPicture = true;
        if (possible[t]) conditionalNovel++;
      }
    }
    audit.push({ task: tasks[t].id, repeat: r, actions: x.actions, success: x.success,
      novel: newPicture, decisions: x.decisions, duplicateActions: x.duplicateActions || 0,
      emptySubmit: !!x.emptySubmit, truncated: !!x.truncated });
  }
  const episodes = tasks.length * repeats, eligible = possible.filter(Boolean).length * repeats;
  return { success: wins / episodes, novel: novel / episodes,
    conditionalNovel: eligible ? conditionalNovel / eligible : null,
    novelOpportunityRate: eligible / episodes, decisions, episodes, validatorCalls: calls,
    duplicateActionRate: decisions ? duplicates / decisions : 0, emptySubmitRate: empty / episodes,
    audit };
}

// Independent evaluation stream per task and repeat. Preserves actions when
// task order changes and prevents one frozen trial contaminating another.
export function trialSeed(seed, task, repeat) {
  if (!Number.isInteger(seed) || !Number.isInteger(repeat) || repeat < 0)
    throw new Error("evaluation seed and repeat must be valid integers");
  const key = `${seed}/${JSON.stringify(task)}/${repeat}`;
  let h = 2166136261;
  for (let i = 0; i < key.length; i++) h = Math.imul(h ^ key.charCodeAt(i), 16777619);
  return h >>> 0;
}

export function frozenScore(brain, tasks, repeats, {
  revealGoal = true, seen = new Set(), evalSeed = 1, greedy = false, maskHistory = false,
} = {}) {
  const sourceDigest = weightDigest(brain);
  const result = summarize(tasks, repeats, seen, (task, repeat) =>
    playEpisode(evaluationCopy(brain, trialSeed(evalSeed, task, repeat)), task,
      { learn: false, revealGoal, greedy, maskHistory }));
  if (weightDigest(brain) !== sourceDigest)
    throw new Error("source checkpoint was mutated during frozen evaluation");
  return result;
}

export function randomStepScore(tasks, repeats, { seen = new Set(), evalSeed = 1,
  maskHistory = false } = {}) {
  return summarize(tasks, repeats, seen, (task, repeat) =>
    randomEpisode(rng(trialSeed(evalSeed, task, repeat)), task, { maskHistory }));
}

/** Separate candidate-search upper bound: NOT a stepwise agent. */
export function randomCandidateScore(tasks, repeats, { seen = new Set(), evalSeed = 1 } = {}) {
  return summarize(tasks, repeats, seen, (task, repeat) => {
    const strokes = randomLegal(rng(trialSeed(evalSeed, task, repeat)), task.budget);
    return { success: valid(task, strokes), strokes, actions: [], decisions: 0,
      duplicateActions: 0, emptySubmit: false, validatorCalls: 1, truncated: false };
  });
}

export function runSeed(seed, { trainSteps = 10000, trainTasks = 64, evalTasks = 30, repeats = 5 } = {}) {
  if (![seed, trainSteps, trainTasks, evalTasks, repeats].every(Number.isInteger) || seed < 0 ||
      trainSteps < 1 || trainTasks < 1 || evalTasks < 1 || repeats < 1)
    throw new Error("invalid experiment configuration");
  assertDisjoint();
  const train = generate(seed, "train", trainTasks).tasks, eval_ = generate(seed, "eval", evalTasks).tasks;
  if (train.length !== trainTasks || eval_.length !== evalTasks) throw new Error("incomplete task generation");
  const known = new Set(train.flatMap(task => solutions(task)).map(pictureClass)), rows = [];
  const evalSeed = seed * 65537 + 97;
  for (const arm of ARMS) {
    const started = Date.now(), isRandom = arm.startsWith("random-step");
    const maskHistory = arm === "learner-masked" || arm === "random-step-masked";
    if (isRandom || arm === "random-valid") {
      const heldout = isRandom
        ? randomStepScore(eval_, repeats, { seen: known, evalSeed, maskHistory })
        : randomCandidateScore(eval_, repeats, { seen: known, evalSeed });
      rows.push(run({ arm, seed, split: "eval", status: "ok", seconds: (Date.now() - started) / 1000,
        scores: { train: { success: null }, heldout, trainSteps: 0, trainEpisodes: 0,
          trainingSuccess: null, trainTruncated: 0, heldoutGreedySuccess: null } }));
      continue;
    }
    const brain = new Brain(rng(seed * 7919 + 41)), chooseTask = rng(seed * 1741 + 17);
    const revealGoal = arm !== "goal-masked", learn = arm !== "learning-off";
    let steps = 0, episodes = 0, correct = 0, truncated = 0;
    while (steps < trainSteps) {
      const task = train[Math.floor(chooseTask() * train.length)];
      const x = playEpisode(brain, task, { learn, revealGoal, maskHistory,
        maxDecisions: trainSteps - steps });
      steps += x.decisions; episodes++; correct += x.success ? 1 : 0;
      truncated += x.truncated ? 1 : 0;
    }
    if (steps !== trainSteps) throw new Error("training overshot decision budget");
    const familiar = frozenScore(brain, train.slice(0, Math.min(evalTasks, train.length)),
      repeats, { revealGoal, maskHistory, evalSeed: evalSeed + 1 });
    const heldout = frozenScore(brain, eval_, repeats,
      { revealGoal, maskHistory, seen: known, evalSeed });
    const greedyHeldout = frozenScore(brain, eval_, repeats,
      { revealGoal, maskHistory, seen: known, evalSeed, greedy: true });
    rows.push(run({ arm, seed, split: "eval", status: "ok", seconds: (Date.now() - started) / 1000,
      scores: { train: { success: familiar.success }, heldout, trainSteps: steps,
        trainEpisodes: episodes, trainingSuccess: correct / episodes, trainTruncated: truncated,
        heldoutGreedySuccess: greedyHeldout.success } }));
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
    metrics: { "heldout.success": "higher", "heldout.novel": "higher", "heldout.conditionalNovel": "higher",
      "heldout.duplicateActionRate": "lower", heldoutGreedySuccess: "higher",
      "train.success": "higher", trainSteps: "lower" },
    config: { seeds, trainTasks, evalTasks, repeats, arms: ARMS, provenance: PROVENANCE,
      split: "fixed disjoint train/eval constraint families; fully detached frozen evaluation",
      protocol: "diagnostic only: trained arms use exact primitive decisions; random-valid generates whole candidates, not stepwise actions",
      limitations: "Pilot baseline only: no learned options, no reversal or adaptation, no held-out task training" },
    budgets: { trainDecisionBudget: trainSteps, evalEpisodesPerArm: evalTasks * repeats,
      candidateQueriesPerEpisode: 1, stepwiseMaxActionsPerEpisode: "task.budget" },
  }));
}
