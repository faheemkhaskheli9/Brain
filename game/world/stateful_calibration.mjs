// M0c controlled learnability/credit diagnostic (#112/#153).
// Same public sensors, six actions, simulator rewards and task for every arm.
// This diagnostic deliberately repeats ONE physical training task. Not transfer.
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import { rng } from "./brain.js";
import { ALLOWED, initial, observe, transition } from "./stateful_construct.mjs";
import { PublicTabular, publicStateKey } from "./stateful_construct_controls.mjs";
import { cloneForEvaluation, createModel, modelDigest, modelBytes } from "./stateful_options.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

export const ARMS = Object.freeze(["flat-brain", "q-absolute", "q-relative",
  "q-relative-explore50", "q-relative-potential", "q-relative-no-reward",
  "uniform-random"]);
const TRAINED = new Set(ARMS.filter(a => a !== "uniform-random"));
const RELATIVE = new Set(["q-relative", "q-relative-explore50",
  "q-relative-potential", "q-relative-no-reward"]);
const EPS = Object.freeze({ "q-absolute": 0.2, "q-relative": 0.2,
  "q-relative-explore50": 0.5, "q-relative-potential": 0.2,
  "q-relative-no-reward": 0.2 });
const mix = (a, b) => (Math.imul(a >>> 0, 1664525) + b + 1013904223) >>> 0;
const pick = (R, choices) => choices[Math.floor(R() * choices.length)];
export const TASK = Object.freeze({ id: "fixed-train", start: [2, 0],
  item: [2, 0], goal: [3, 0], walls: [], maxSteps: 12 });
// These are deliberately labelled nearby DIAGNOSTIC probes, not heldout splits.
export const PROBES = Object.freeze([
  Object.freeze({ id: "left-one-cell", start: [2, 0], item: [2, 0],
    goal: [1, 0], walls: [], maxSteps: 12 }),
  Object.freeze({ id: "move-then-pickup", start: [2, 0], item: [3, 0],
    goal: [4, 0], walls: [], maxSteps: 12 }),
]);
const cell = (x, base) => {
  for (let i = 0; i < 25; i++) if (x[base + i] > 0.5) return [i % 5, Math.floor(i / 5)];
  throw new Error("missing visible cell in public input");
};
const manhattan = (a, b) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);

// Potential is explicitly SUPPLIED coordinate/goal expertise. It is only
// applied to training feedback, never to environment transitions or scores.
export function publicPotential(x) {
  const agent = cell(x, 0), carrying = x[75] > 0.5;
  const target = cell(x, carrying ? 50 : 25);
  return -0.12 * manhattan(agent, target) + (carrying ? 0.25 : 0);
}
export function feedback(arm, obs, reward, after, terminal) {
  if (arm === "q-relative-no-reward") return 0;
  if (arm !== "q-relative-potential") return reward;
  return reward + 0.95 * (terminal ? 0 : publicPotential(after)) -
    publicPotential(obs);
}

export function makeAgent(arm, seed) {
  if (!ARMS.includes(arm) || !Number.isSafeInteger(seed) || seed < 0)
    throw new Error("invalid diagnostic agent");
  if (arm === "flat-brain") return createModel(seed, "flat");
  if (arm === "uniform-random") return null;
  return new PublicTabular(seed, RELATIVE.has(arm));
}
function chooseAction(agent, arm, obs, learn, R) {
  if (arm === "uniform-random") return pick(R, ALLOWED);
  if (arm === "flat-brain") {
    const b = agent.brains[0];
    return b.act(b.encode(obs, 0), ALLOWED);
  }
  const row = agent.table.row(publicStateKey(obs, RELATIVE.has(arm)));
  const random = agent.table.random;
  if (learn && random() < EPS[arm]) return pick(random, ALLOWED);
  const value = Math.max(...row);
  const ties = ALLOWED.filter(a => Math.abs(row[a] - value) < 1e-9);
  return pick(random, ties);
}
function stats() {
  return { success: false, decisions: 0, envSteps: 0, pickups: 0,
    blocked: 0, failedPickups: 0, emptyDrops: 0, misplaced: 0, invalid: 0,
    rewardSum: 0, feedbackSum: 0, truncated: false };
}

// An invalid primitive is an actual environment step, not a free rejection.
// A training-budget truncation bootstraps next value and clears Brain traces,
// unlike a true terminal which has no next-state bootstrap.
export function episode(agent, arm, task, { learn = false, cap = task.maxSteps,
  seed = 1 } = {}) {
  if (!ARMS.includes(arm) || !Number.isSafeInteger(seed) || seed < 0 ||
      !Number.isSafeInteger(cap) || cap < 1 || cap > task.maxSteps)
    throw new Error("invalid episode configuration");
  const outcome = stats(), R = rng(seed);
  let state = initial(task), oldLearning = null, b;
  if (arm === "flat-brain") {
    b = agent.brains[0];
    oldLearning = b.learning; b.learning = learn;
    b.greedy = false;
  }
  try {
    for (let i = 0; i < cap; i++) {
      const obs = observe(task, state);
      const action = chooseAction(agent, arm, obs, learn, R);
      if (!ALLOWED.includes(action)) throw new Error("illegal primitive action");
      const res = transition(task, state, action);
      const next = res.done ? null : observe(task, res.state);
      const signal = feedback(arm, obs, res.reward, next, res.done);
      outcome.decisions++; outcome.envSteps++; outcome.rewardSum += res.reward;
      outcome.feedbackSum += signal;
      outcome.invalid += Number(res.invalid);
      if (res.reason === "picked-up") outcome.pickups++;
      if (res.reason === "blocked") outcome.blocked++;
      if (res.reason === "failed-pickup") outcome.failedPickups++;
      if (res.reason === "empty-drop") outcome.emptyDrops++;
      if (res.reason === "misplaced") outcome.misplaced++;
      if (learn && arm !== "uniform-random") {
        if (b) {
          const hNext = next ? b.encode(next, 0) : null;
          b.learn(signal, hNext, res.done || i === cap - 1);
        } else {
          agent.update(obs, action, signal, next, res.done);
        }
      }
      state = res.state;
      if (res.done) {
        outcome.success = res.success;
        break;
      }
    }
    outcome.truncated = !state.done && cap < task.maxSteps;
    return outcome;
  } finally {
    if (b) b.learning = oldLearning;
  }
}
function freshForScoring(agent, arm, seed) {
  if (arm === "flat-brain") return cloneForEvaluation(agent, seed);
  return arm === "uniform-random" ? null : agent.clone(seed);
}
function evaluation(seed, arm, agent, tasks, repeats, salt) {
  const before = arm === "flat-brain" ? modelDigest(agent) :
    arm === "uniform-random" ? null :
      createHash("sha256").update(JSON.stringify([...agent.table.values])).digest("hex");
  const total = { success: 0, pickups: 0, invalid: 0, decisions: 0, envSteps: 0,
    episodes: tasks.length * repeats, failed: 0 };
  for (const [taskIndex, task] of tasks.entries()) {
    for (let rep = 0; rep < repeats; rep++) {
      // No action RNG uses the task ID; all arms share evaluation seed inputs.
      const s = mix(seed, Math.imul(taskIndex + 1, 931) + rep * 127 + salt);
      const copy = freshForScoring(agent, arm, s);
      const run = episode(copy, arm, task, { learn: false, seed: s });
      total.success += Number(run.success);
      total.pickups += run.pickups; total.invalid += run.invalid;
      total.decisions += run.decisions; total.envSteps += run.envSteps;
      total.failed += Number(!run.success);
    }
  }
  const after = arm === "flat-brain" ? modelDigest(agent) :
    arm === "uniform-random" ? null :
      createHash("sha256").update(JSON.stringify([...agent.table.values])).digest("hex");
  if (before !== after) throw new Error("frozen evaluation changed training model");
  total.deliveries = total.success;
  total.success /= total.episodes;
  return total;
}
export function runSeed(seed, { checkpoints = [0, 250, 1000, 4000],
  repeats = 12 } = {}) {
  if (!Number.isSafeInteger(seed) || seed < 0 ||
      !Array.isArray(checkpoints) || checkpoints.length < 2 ||
      checkpoints[0] !== 0 ||
      checkpoints.some((v, i) => !Number.isSafeInteger(v) || v < 0 ||
        (i > 0 && v <= checkpoints[i - 1])) ||
      !Number.isSafeInteger(repeats) || repeats < 1)
    throw new Error("invalid diagnostic config");
  const rows = [];
  for (const arm of ARMS) {
    const started = Date.now();
    try {
      const model = makeAgent(arm, mix(seed, 119));
      const checkpointsOut = [];
      const trained = TRAINED.has(arm);
      let spent = 0, environmentSteps = 0, trainingEpisodes = 0;
      const training = { pickups: 0, invalid: 0, failedPickups: 0,
        misplaced: 0, blocked: 0, successes: 0, truncatedEpisodes: 0,
        environmentRewardSum: 0, learningFeedbackSum: 0 };
      for (const target of checkpoints) {
        if (trained) while (spent < target) {
          const remaining = target - spent;
          const result = episode(model, arm, TASK, { learn: true,
            cap: Math.min(TASK.maxSteps, remaining),
            seed: mix(seed, trainingEpisodes + 691) });
          if (!result.decisions || result.decisions > remaining ||
              result.envSteps !== result.decisions)
            throw new Error("training decision/environment budget violated");
          spent += result.decisions; environmentSteps += result.envSteps;
          trainingEpisodes++; training.pickups += result.pickups;
          training.invalid += result.invalid;
          training.failedPickups += result.failedPickups;
          training.misplaced += result.misplaced;
          training.blocked += result.blocked;
          training.environmentRewardSum += result.rewardSum;
          training.learningFeedbackSum += result.feedbackSum;
          training.successes += Number(result.success);
          training.truncatedEpisodes += Number(result.truncated);
        }
        checkpointsOut.push({
          decisions: target,
          calibration: evaluation(seed, arm, model, [TASK], repeats, 19),
          diagnosticVariants: evaluation(seed, arm, model, PROBES, repeats, 31),
        });
      }
      rows.push(run({ arm, seed, split: "same-task-calibration-not-transfer",
        status: "ok", seconds: (Date.now() - started) / 1000,
        scores: {
          before: checkpointsOut[0],
          after: checkpointsOut.at(-1),
          curve: checkpointsOut,
          trainDecisions: spent, trainEnvSteps: environmentSteps,
          trainingEpisodes, training, oracleQueries: 0,
          tableStates: arm.startsWith("q-") ? model.states : 0,
          modelBytesEstimate: arm === "flat-brain" ? modelBytes(model) :
            arm.startsWith("q-") ? model.bytesEstimate : 0,
        } }));
    } catch (error) {
      rows.push(run({ arm, seed, split: "same-task-calibration-not-transfer",
        status: "error", reason: String(error?.message || error),
        seconds: (Date.now() - started) / 1000, scores: {} }));
    }
  }
  return rows;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const argv = process.argv.slice(2);
  const option = (name, fallback) => {
    const index = argv.indexOf(name);
    return index < 0 ? fallback : argv.splice(index, 2)[1];
  };
  const checkpoints = option("--checkpoints", "0,250,1000,4000")
    .split(",").map(Number);
  const repeats = Number(option("--repeats", "12"));
  const out = option("--out", null);
  const seeds = argv.length ? argv.map(Number) : [1, 2, 3];
  if (!out || seeds.some(x => !Number.isSafeInteger(x) || x < 0) ||
      new Set(seeds).size !== seeds.length)
    throw new Error("usage: node game/world/stateful_calibration.mjs 1 2 --checkpoints 0,250,1000,4000 --repeats 12 --out PATH");
  const rows = seeds.flatMap(seed => runSeed(seed, { checkpoints, repeats }));
  const result = resultRecord({
    experiment: "brain-world/m0c-fixed-geometry-calibration",
    baseline: "q-relative", runs: rows,
    config: { seeds, checkpoints, repeats, arms: ARMS,
      trainingTask: TASK, diagnosticVariants: PROBES,
      model: "Brain is backprop-free; Q uses authored tabular state keys",
      reward: "native except optional goal-relative potential or zero-feedback controls",
      constraint: "same fixed training geometry; deliberately NOT an independent holdout" },
    budgets: { exactPrimitiveDecisionsPerTrainedArm: checkpoints.at(-1),
      physicalTransitionsCharged: true, oracleCallsPerArm: 0,
      evaluationEpisodesPerStage: repeats * (1 + PROBES.length) },
    metrics: { "after.calibration.success": "higher",
      "after.diagnosticVariants.success": "higher",
      "before.calibration.success": "higher",
      trainDecisions: "lower", trainingEpisodes: "lower" },
  });
  writeResult(out, result);
  for (const arm of ARMS) {
    const valid = rows.filter(r => r.arm === arm && r.status === "ok");
    const avg = valid.length ? valid.reduce((s, r) =>
      s + r.scores.after.calibration.success, 0) / valid.length : NaN;
    console.log(arm.padEnd(24), "fixed-task delivery", avg.toFixed(3),
      "seeds", valid.length);
  }
  if (rows.some(row => row.status !== "ok")) process.exitCode = 1;
}
