// Backprop-free, stateful option-learning experiment (#112).
// Reuses Brain's three-factor actor/critic, not an LLM or backprop network.
// Option initiation and carrying-based switching are ENGINEERED; intra-option
// action/voluntary-exit policies are LEARNED. Do not call this learned planning.
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import { Brain, rng } from "./brain.js";
import { ALLOWED, generate, initial, observe, oracle, transition } from "./stateful_construct.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

export const EXIT = 6; // existing pen action repurposed as voluntary option termination
export const ARMS = Object.freeze(["flat", "flat-goal-masked", "options",
  "options-no-gate", "options-no-terminate", "random", "oracle"]);
export const PROVENANCE = Object.freeze({
  learning: "Brain World local three-factor actor/critic (no backprop); weights learned online",
  supplied: "5x5 grid, six primitive actions, reward, goal sensor, contact sensors, split grammar",
  options: "two separate policy modules; initiation/switch keyed to observable carrying flag",
  learned: "each module's primitive-action policy and option-exit action probabilities",
  upperBound: "BFS oracle uses simulator transitions only to score feasibility; not accessible to policies",
  missing: "learned option discovery/initiation, recurrent memory, robust transfer, planning",
});
const isOptions = arm => arm.startsWith("options");
const isLearned = arm => arm !== "random" && arm !== "oracle";
const mix = (a, b) => (Math.imul(a >>> 0, 1664525) + b + 1013904223) >>> 0;
const evalSeed = (seed, task, repeat) => {
  let h = mix(seed, repeat);
  for (const c of task.id) h = Math.imul(h ^ c.charCodeAt(0), 16777619) >>> 0;
  return h >>> 0;
};

export function createModel(seed, arm) {
  if (!ARMS.includes(arm) || !Number.isInteger(seed) || seed < 0)
    throw new Error("invalid model");
  return { arm, brains: isLearned(arm) ?
    Array.from({ length: isOptions(arm) ? 2 : 1 },
      (_, i) => new Brain(rng(mix(seed, i * 17 + 13)))) : [] };
}
const arrays = b => ["P", "v", "wIn", "bias", "gate", "ev", "eP", "proto", "uses"]
  .map(k => b[k]).filter(v => v && ArrayBuffer.isView(v));
export function modelDigest(model) {
  const hash = createHash("sha256");
  for (const b of model.brains) for (const v of arrays(b))
    hash.update(Buffer.from(v.buffer, v.byteOffset, v.byteLength));
  return hash.digest("hex");
}
export const modelBytes = model => model.brains.reduce((n, b) =>
  n + arrays(b).reduce((m, v) => m + v.byteLength, 0), 0);

// Engineered option selector sees only the public carrying observation.
// This is not claimed as a learned manager; shuffled selector is a control.
export function selectOption(arm, state, R) {
  if (!isOptions(arm)) return 0;
  return arm === "options-no-gate" ? Math.floor(R() * 2) : Number(state.carrying);
}
export const legalActions = arm =>
  isOptions(arm) && arm !== "options-no-terminate" ? [...ALLOWED, EXIT] : ALLOWED;

function sensed(task, state, arm) {
  const x = observe(task, state);
  if (arm === "flat-goal-masked") {
    x.fill(0, 50, 75); x[81] = 0;
  }
  return x;
}

// Primitive-decision budget includes the option's exit action; environment steps
// and voluntary exits are separately reported. Wrong drops can be recovered by pickup.
export function episode(model, task, { learn = true, seed = 0, greedy = false } = {}) {
  const R = rng(mix(seed, 991)), optionActions = legalActions(model.arm);
  const old = model.brains.map(b => ({ learning: b.learning, greedy: b.greedy }));
  for (const b of model.brains) { b.learning = learn; b.greedy = !learn && greedy; }
  let state = initial(task), successes = 0, decisions = 0, exits = 0, envSteps = 0;
  let option = selectOption(model.arm, state, R), reason = "decision-budget";
  const limit = task.maxSteps * 2;
  try {
    if (model.arm === "oracle") {
      const path = oracle(task);
      if (path) return { success: true, decisions: path.length, envSteps: path.length,
        invalid: 0, exits: 0, reason: "oracle" };
      return { success: false, decisions: 0, envSteps: 0,
        invalid: 0, exits: 0, reason: "infeasible" };
    }
    for (let n = 0; n < limit; n++) {
      decisions++;
      const b = model.brains[option];
      const h = b?.encode(sensed(task, state, model.arm), 0);
      const action = b ? b.act(h, optionActions)
        : ALLOWED[Math.floor(R() * ALLOWED.length)];
      if (!optionActions.includes(action)) throw new Error("illegal option action");
      if (action === EXIT) {
        exits++;
        b.learn(n === limit - 1 ? -0.2 : -0.04, null);
        option = selectOption(model.arm, state, R);
        continue;
      }
      const result = transition(task, state, action);
      state = result.state; envSteps++;
      reason = result.reason;
      if (result.success) successes++;
      const next = selectOption(model.arm, state, R);
      if (b) {
        const last = result.done || n === limit - 1 || next !== option;
        const reward = result.reward - (n === limit - 1 && !result.done ? 0.2 : 0);
        b.learn(reward, last ? null : b.encode(sensed(task, state, model.arm), 0));
      }
      if (result.done) break;
      option = next;
    }
    return { success: successes > 0, decisions, envSteps,
      invalid: state.invalid, exits, reason };
  } finally {
    for (let i = 0; i < old.length; i++) {
      model.brains[i].learning = old[i].learning;
      model.brains[i].greedy = old[i].greedy;
    }
  }
}

function frozenEpisode(model, task, seed) {
  const before = modelDigest(model);
  const saved = model.brains.map((b, i) => ({
    rand: b.rand, h: b.h, dopamine: b.dopamine, pi: b.pi.slice(),
    nActive: b.nActive, nEncode: b.nEncode, learning: b.learning, greedy: b.greedy,
  }));
  model.brains.forEach((b, i) => { b.rand = rng(mix(seed, i + 47)); });
  let result;
  try { result = episode(model, task, { learn: false, seed }); }
  finally {
    model.brains.forEach((b, i) => {
      const old = saved[i];
      b.rand = old.rand; b.h = old.h; b.dopamine = old.dopamine;
      b.pi.set(old.pi); b.nActive = old.nActive; b.nEncode = old.nEncode;
      b.learning = old.learning; b.greedy = old.greedy;
    });
  }
  if (before !== modelDigest(model))
    throw new Error("frozen stateful scoring changed the learner");
  return result;
}
export function scoreTasks(model, tasks, repeats = 2, seed = 0) {
  if (!Array.isArray(tasks) || !tasks.length || !Number.isInteger(repeats) || repeats < 1)
    throw new Error("invalid evaluation tasks");
  let wins = 0, invalid = 0, decisions = 0, envSteps = 0, exits = 0, timeouts = 0;
  for (const task of tasks) for (let i = 0; i < repeats; i++) {
    const result = frozenEpisode(model, task, evalSeed(seed, task, i));
    if (result.success) wins++;
    if (!result.success) timeouts++;
    invalid += result.invalid; decisions += result.decisions;
    envSteps += result.envSteps; exits += result.exits;
  }
  const episodes = tasks.length * repeats;
  return { success: wins / episodes, failed: timeouts, invalidPerEpisode: invalid / episodes,
    decisions, envSteps, exits, episodes };
}
// The adaptation phase uses DEVELOPMENT goal pairs only, never the frozen eval
// family. Budget is primitive + exit decisions, and is logged separately.
function trainPhase(model, tasks, seed, budget, salt) {
  const R = rng(mix(seed, salt));
  let decisions = 0, envSteps = 0, episodes = 0, wins = 0, invalid = 0;
  if (isLearned(model.arm)) while (decisions < budget) {
    const task = tasks[Math.floor(R() * tasks.length)];
    const trial = episode(model, task, { learn: true,
      seed: mix(seed, episodes + salt + 971) });
    decisions += trial.decisions; envSteps += trial.envSteps;
    episodes++; wins += Number(trial.success); invalid += trial.invalid;
  }
  return { decisions, envSteps, episodes, success: episodes ? wins / episodes : null, invalid };
}
export function runSeed(seed, { trainSteps = 2000, adaptSteps = 0, trainTasks = 32,
  evalTasks = 16, repeats = 2 } = {}) {
  if (![seed, trainSteps, adaptSteps, trainTasks, evalTasks, repeats].every(Number.isInteger) ||
    seed < 0 || trainSteps < 1 || adaptSteps < 0 ||
    trainTasks < 1 || evalTasks < 1 || repeats < 1)
    throw new Error("invalid experiment budget");
  const train = generate(seed, "train", trainTasks);
  const dev = generate(seed, "dev", trainTasks);
  const evalSet = generate(seed, "eval", evalTasks);
  const sourceTasks = train.slice(0, Math.min(evalTasks, train.length));
  const rows = [];
  for (const arm of ARMS) {
    const start = Date.now(), model = createModel(mix(seed, 31), arm);
    const training = trainPhase(model, train, seed, trainSteps, 617);
    const sourceBefore = scoreTasks(model, sourceTasks, repeats, seed);
    const zeroShot = scoreTasks(model, evalSet, repeats, seed);
    const adaptation = trainPhase(model, dev, seed, adaptSteps, 997);
    const sourceAfter = adaptSteps ? scoreTasks(model, sourceTasks, repeats, seed) : sourceBefore;
    const heldout = adaptSteps ? scoreTasks(model, evalSet, repeats, seed) : zeroShot;
    rows.push(run({ arm, seed, split: "eval", status: "ok",
      seconds: (Date.now() - start) / 1000,
      scores: { zeroShot, heldout, sourceBefore, sourceAfter,
        sourceRetentionDelta: sourceAfter.success - sourceBefore.success,
        training, adaptation, modelBytes: modelBytes(model) } }));
  }
  return rows;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2), opt = (flag, fallback) => {
    const i = args.indexOf(flag);
    return i === -1 ? fallback : args.splice(i, 2)[1];
  };
  const trainSteps = Number(opt("--train-steps", "2000")),
    adaptSteps = Number(opt("--adapt-steps", "0")),
    trainTasks = Number(opt("--train-tasks", "32")),
    evalTasks = Number(opt("--eval-tasks", "16")),
    repeats = Number(opt("--repeats", "2")), out = opt("--out", null);
  const seeds = args.length ? args.map(Number) : [1, 2, 3];
  if (!seeds.length || seeds.some(s => !Number.isInteger(s) || s < 0) ||
    new Set(seeds).size !== seeds.length) throw new Error("invalid seeds");
  const runs = seeds.flatMap(seed => runSeed(seed, { trainSteps, adaptSteps, trainTasks, evalTasks, repeats }));
  for (const arm of ARMS) {
    const group = runs.filter(r => r.arm === arm);
    const mean = group.reduce((s, r) => s + r.scores.heldout.success, 0) / group.length;
    console.log(arm.padEnd(21), "heldout", mean.toFixed(3));
  }
  if (out) writeResult(out, resultRecord({
    experiment: "brain-world/stateful-options-pilot", baseline: "flat", runs,
    metrics: { "zeroShot.success": "higher", "heldout.success": "higher",
      sourceRetentionDelta: "higher", "heldout.invalidPerEpisode": "lower", modelBytes: "lower" },
    budgets: { trainingDecisionsPerArm: trainSteps, adaptationDecisionsPerArm: adaptSteps,
      evalEpisodes: evalTasks * repeats,
      optionExitCountsAsDecision: true, trainingOvershoot: "episode boundary, logged per run" },
    config: { seeds, trainTasks, evalTasks, repeats, arms: ARMS, provenance: PROVENANCE,
      splits: "train pretraining, dev adaptation, frozen eval; disjoint goal-pair families",
      limitations: "Engineered option initiation and reward; no learned option discovery or statistically confirmed advantage" },
  }));
}
