// Shared-network conventional policy-gradient baseline (partial issue #153).
// Every skill uses ONE actor-critic, with no task ID or hidden-world labels as input.
// This is a backprop baseline, not a modification of Brain World's backprop-free brain.
//
// Match the existing per-skill actor-critic: same env.mjs observations, actions,
// rewards, model, optimizer, and episode budgets. Only parameter sharing and
// the experimenter's training order change. Full held-out/reversal evaluation
// is tracked separately in #153; results here are in-distribution only.
//
// node game/world/rl_multitask.mjs 1 2 --budget 125000 --episodes 300 \
//      --schedule interleaved --creature --match-creature --out result.json
import { pathToFileURL } from "node:url";
import { STAGES, GAINS, World } from "./brain.js";
import { Env } from "./env.mjs";
import { ActorCritic, HP, trainAndScore } from "./rl.mjs";
import { evaluate, POLICIES } from "./baselines.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

const LIMIT = 20000;
export const SCHEDULES = ["interleaved", "blocked"];

function episode(env, net) {
  const steps = [];
  let done = false;
  while (!done) {
    // The learner receives only observation and allowed actions, never key,
    // reward rule, target label, slot, World, or another task ID.
    const x = Float64Array.from(env.obs), allowed = Array.from(env.allowed);
    const { k, f } = net.act(x, allowed, false);
    if (!allowed.includes(allowed[k])) throw new Error("invalid action index");
    const result = env.step(allowed[k]);
    steps.push({ x, allowed, k, f, r: result.reward });
    done = result.done;
  }
  net.learn(steps);
}

// One policy and value function for all five tasks. The training schedule is an
// experimental condition, not a task-label feature forwarded to the policy.
export function trainShared(seed, {
  budgetPerSkill = HP.BUDGET, episodes = 300, hp = HP, schedule = "interleaved",
} = {}) {
  if (!Number.isInteger(budgetPerSkill) || budgetPerSkill < 1 ||
      !Number.isInteger(episodes) || episodes < 1 || !SCHEDULES.includes(schedule)) {
    throw new Error("invalid multi-task budget, eval count, or schedule");
  }
  const envs = STAGES.map(s => new Env(seed, s.key));
  const net = new ActorCritic(envs[0].obs.length, seed * 7919 + 1, hp);
  if (schedule === "blocked") {
    for (const env of envs) while (env.steps < budgetPerSkill) episode(env, net);
  } else {
    while (envs.some(env => env.steps < budgetPerSkill)) {
      for (const env of envs) if (env.steps < budgetPerSkill) episode(env, net);
    }
  }
  const trainSteps = Object.fromEntries(STAGES.map((s, i) => [s.key, envs[i].steps]));
  const trainSuccess = Object.fromEntries(STAGES.map((s, i) => [
    s.key, envs[i].successes / envs[i].episodes,
  ]));
  const weights = Float64Array.from(net.theta);
  const results = {};
  for (const { key } of STAGES) {
    const test = new Env(seed + 100000, key), greedy = GAINS.performGreedy.includes(key);
    while (test.episodes < episodes) {
      const allowed = test.allowed, { k } = net.act(test.obs, allowed, greedy);
      test.step(allowed[k]);
    }
    results[key] = { success: test.successes / test.episodes,
      evalSteps: test.steps, trainSteps: trainSteps[key],
      trainSuccess: trainSuccess[key] };
  }
  if (weights.some((w, i) => w !== net.theta[i])) throw new Error("shared network changed during frozen evaluation");
  return { results, parameters: net.theta.length,
    optimizerBytes: net.theta.byteLength + net.m.byteLength + net.v.byteLength + net.grad.byteLength,
    trainSteps, totalTrainSteps: Object.values(trainSteps).reduce((a, b) => a + b, 0),
    schedule };
}

// Optional creature arm, trained on its original curriculum, *not* by backprop.
// Its steps determine the other arm's per-skill budgets when --match-creature
// is requested. Each policy's actual steps remain visible (episodes may overshoot).
export function trainCreature(seed, episodes) {
  const world = new World(seed);
  for (let s = 0; s < STAGES.length; s++) {
    const start = world.episode;
    while (world.stage === s && !world.graduated && world.episode - start < LIMIT) world.step();
    if (!(world.stage > s || world.graduated)) {
      return { failed: STAGES[s].key,
        trainSteps: world.log.reduce((total, e) => total + e.steps, 0) };
    }
  }
  const trainSteps = world.log.reduce((total, e) => total + e.steps, 0);
  const test = World.fromJSON(JSON.parse(JSON.stringify(world))), scores = {};
  for (const { key } of STAGES) {
    test.perform(key);
    let steps = 0;
    while (test.perf.n < episodes) { test.step(); steps++; }
    scores[key] = { success: test.perf.ok / test.perf.n, evalSteps: steps, trainSteps };
  }
  return { results: scores, trainSteps };
}

export function compare(seed, {
  budgetPerSkill = HP.BUDGET, episodes = 300, hp = HP,
  schedule = "interleaved", withCreature = false, matchCreature = false,
  withControls = true,
} = {}) {
  if (matchCreature && !withCreature) throw new Error("matching creature budget requires --creature");
  const rows = [], costs = {};
  const creatureT0 = Date.now();
  const creature = withCreature ? trainCreature(seed, episodes) : null;
  if (creature) costs.creature = { wallSecondsIncludingEval: (Date.now() - creatureT0) / 1000,
    trainSteps: creature.trainSteps };
  if (matchCreature && creature.failed) throw new Error("creature failed: cannot match training budget");
  const budget = matchCreature ? Math.ceil(creature.trainSteps / STAGES.length) : budgetPerSkill;
  const t0 = Date.now();
  const shared = trainShared(seed, { budgetPerSkill: budget, episodes, hp, schedule });
  const sharedSeconds = (Date.now() - t0) / 1000;
  costs.shared = { totalTrainSteps: shared.totalTrainSteps,
    parameters: shared.parameters, optimizerBytes: shared.optimizerBytes,
    wallSecondsIncludingEval: sharedSeconds };
  for (const { key } of STAGES) {
    rows.push(run({ arm: "shared-" + schedule, seed, split: key, status: "ok",
      seconds: sharedSeconds / STAGES.length,
      scores: { ...shared.results[key], parameters: shared.parameters,
        optimizerBytes: shared.optimizerBytes, totalTrainSteps: shared.totalTrainSteps } }));
  }
  const netExample = new ActorCritic(new Env(seed, STAGES[0].key).obs.length, seed, hp);
  const singleParams = netExample.theta.length;
  for (const { key } of STAGES) {
    const started = Date.now(), individual = trainAndScore(seed, key, { budget, episodes, hp });
    rows.push(run({ arm: "separate", seed, split: key, status: "ok",
      seconds: (Date.now() - started) / 1000,
      scores: { ...individual, parameters: singleParams * STAGES.length,
        optimizerBytes: (netExample.theta.byteLength + netExample.m.byteLength +
          netExample.v.byteLength + netExample.grad.byteLength) * STAGES.length,
        totalTrainSteps: null } }));
  }
  if (withControls) {
    for (const [arm, policy] of Object.entries(POLICIES)) {
      for (const { key } of STAGES) {
        const started = Date.now(), score = evaluate(policy, seed + 100000, key, episodes);
        rows.push(run({ arm, seed, split: key, status: "ok", seconds: (Date.now() - started) / 1000,
          scores: { success: score.success, trainSteps: 0, evalSteps: score.steps,
            parameters: 0, optimizerBytes: 0, totalTrainSteps: 0 } }));
      }
    }
  }
  if (creature) {
    for (const { key } of STAGES) {
      rows.push(run({ arm: "creature", seed, split: key,
        status: creature.failed ? "timeout" : "ok",
        reason: creature.failed ? creature.failed + " not learned within " + LIMIT + " episodes" : null,
        scores: creature.failed ? { trainSteps: creature.trainSteps } :
          { ...creature.results[key], parameters: null, optimizerBytes: null,
            totalTrainSteps: creature.trainSteps } }));
    }
  }
  return { rows, costs, budgetPerSkill: budget, creatureTrainSteps: creature?.trainSteps ?? null };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  const take = name => { const i = args.indexOf(name); return i < 0 ? null : args.splice(i, 2)[1]; };
  const out = take("--out"), budget = Number(take("--budget") ?? HP.BUDGET);
  const episodes = Number(take("--episodes") ?? 300), schedule = take("--schedule") ?? "interleaved";
  const withCreature = args.includes("--creature"), matchCreature = args.includes("--match-creature");
  const noControls = args.includes("--no-controls");
  for (const flag of ["--creature", "--match-creature", "--no-controls"]) {
    const pos = args.indexOf(flag);
    if (pos >= 0) args.splice(pos, 1);
  }
  const seeds = args.length ? args.map(Number) : [1, 2, 3, 4, 5];
  if (seeds.some(s => !Number.isInteger(s) || s < 0) ||
      !Number.isInteger(budget) || budget < 1 ||
      !Number.isInteger(episodes) || episodes < 1 || !SCHEDULES.includes(schedule)) {
    throw new Error("bad seeds, --budget, --episodes or --schedule");
  }
  const runs = [], budgets = {};
  for (const seed of seeds) {
    const result = compare(seed, { budgetPerSkill: budget, episodes, schedule,
      withCreature, matchCreature, withControls: !noControls });
    runs.push(...result.rows);
    budgets[seed] = result.budgetPerSkill;
    console.log("seed " + seed + " shared total steps " + result.costs.shared.totalTrainSteps +
      " / parameter count " + result.costs.shared.parameters +
      " / separate networks " + STAGES.length);
  }
  if (out) {
    writeResult(out, resultRecord({ experiment: "brain-world/rl-multitask",
      baseline: "separate", runs,
      metrics: { success: "higher", trainSteps: "lower",
        evalSteps: "lower", parameters: "lower" },
      config: { seeds, schedule, architecture: "one 64-hidden-unit tanh actor-critic with Adam",
        taskInput: "observation plus legal-action mask only; no task ID",
        separateNetworks: STAGES.length, hidden: HP.HID, lr: HP.LR, entropy: HP.ENT,
        evalSeeds: "seed+100000", greedy: GAINS.performGreedy,
        constraints: "no fixed held-out/reversal splits in this initial comparison" },
      budgets: { requestedTrainStepsPerSkill: budget, effectivePerSeed: budgets,
        evalEpisodesPerSkill: episodes, matchCreature } }));
  }
}
