// M0d: same recorded PUBLIC transitions, different local learning updates.
// Diagnostic of credit assignment, not on-policy training or generalization.
// The logged action stream contains supplied demonstration segments. No oracle
// or task ID is used by the learner; replay is deliberately off-policy.
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import { rng } from "./brain.js";
import { ALLOWED, initial, observe, transition } from "./stateful_construct.mjs";
import { TASK, PROBES } from "./stateful_calibration.mjs";
import { cloneForEvaluation, createModel, modelBytes, modelDigest } from "./stateful_options.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

export const ARMS = Object.freeze([
  "native", "trace-one-step", "no-bootstrap", "actor-frozen",
  "critic-frozen", "reward-shifted", "zero-feedback",
]);
const TASKS = Object.freeze([TASK, ...PROBES]);
// Supplied, labelled behaviors ensure the stream includes both rewarded and
// failed transitions. These are NOT discovered by the Brain learner.
const DEMONSTRATIONS = Object.freeze([[4, 1, 5], [4, 0, 5], [1, 4, 1, 5]]);
const mix = (a, b) => (Math.imul(a >>> 0, 1664525) + b + 1013904223) >>> 0;
const l1 = (a, b) => a.reduce((sum, x, i) => sum + Math.abs(x - b[i]), 0);

export function makeStream(seed, episodes = 12) {
  if (!Number.isSafeInteger(seed) || seed < 0 ||
      !Number.isSafeInteger(episodes) || episodes < 1 || episodes > 1000)
    throw new Error("invalid matched-transition stream configuration");
  const R = rng(mix(seed, 1301)), steps = [];
  let completions = 0, scripted = 0, rewardSum = 0, invalid = 0;
  for (let episode = 0; episode < episodes; episode++) {
    const index = episode % TASKS.length, task = TASKS[index];
    const demo = episode % 2 === 0 ? DEMONSTRATIONS[index] : [];
    if (demo.length) scripted++;
    let state = initial(task);
    for (let k = 0; k < task.maxSteps; k++) {
      const action = k < demo.length ?
        demo[k] : ALLOWED[Math.floor(R() * ALLOWED.length)];
      const before = Array.from(observe(task, state));
      const outcome = transition(task, state, action);
      const end = outcome.done || k === task.maxSteps - 1;
      steps.push({
        episode, taskIndex: index, action, before,
        after: Array.from(observe(task, outcome.state)),
        reward: outcome.reward, terminal: outcome.done, end,
        success: outcome.success, invalid: Boolean(outcome.invalid),
      });
      rewardSum += outcome.reward;
      invalid += Number(outcome.invalid);
      state = outcome.state;
      if (outcome.done) {
        completions += Number(outcome.success);
        break;
      }
    }
  }
  const hash = createHash("sha256").update(JSON.stringify(steps)).digest("hex");
  return { steps, hash, episodes, scripted, completions, invalid, rewardSum };
}

function forcedAct(brain, input, action) {
  // Use Brain.act's own eligibility update, not a reimplementation.
  // Only replace its RNG draw with a point inside the recorded action's
  // probability interval. This forces the same action in EVERY arm.
  if (!ALLOWED.includes(action)) throw new Error("invalid logged action");
  const h = brain.encode(input, 0);
  const pi = brain.policy(h, ALLOWED, new Float32Array(brain.pi.length));
  let lower = 0, chosen = null;
  for (const a of ALLOWED) {
    if (!Number.isFinite(pi[a]) || pi[a] <= 0)
      throw new Error("invalid logged action probability");
    if (a === action) chosen = Math.min(1 - Number.EPSILON, lower + pi[a] / 2);
    lower += pi[a];
  }
  if (chosen === null || !Number.isFinite(chosen) || Math.abs(lower - 1) > 1e-4)
    throw new Error("invalid forced action distribution");
  const original = brain.rand;
  try {
    brain.rand = () => chosen;
    if (brain.act(h, ALLOWED) !== action)
      throw new Error("action replay diverged");
  } finally {
    brain.rand = original;
  }
}

function policyProbe(model, seed) {
  // Probe only cloned brains; encoder diagnostic counters must not contaminate
  // the training state or the later replay comparison.
  const clone = cloneForEvaluation(model, mix(seed, 907)), brain = clone.brains[0];
  const start = initial(TASK), carried = transition(TASK, start, 4).state;
  const left = PROBES[0];
  const probability = (task, state, action) => {
    const h = brain.encode(observe(task, state), 0);
    return brain.policy(h, ALLOWED, new Float32Array(brain.pi.length))[action];
  };
  return {
    pickupAtStart: probability(TASK, start, 4),
    moveRightAfterPickup: probability(TASK, carried, 1),
    moveLeftAfterPickup: probability(left, carried, 0),
  };
}

export function replay(seed, arm, stream) {
  if (!ARMS.includes(arm) || !stream?.steps?.length)
    throw new Error("invalid credit replay arm or stream");
  const model = createModel(mix(seed, 119), "flat");
  const brain = model.brains[0], beforeP = brain.P.slice(), beforeV = brain.v.slice();
  const beforeDigest = modelDigest(model), beforeProbe = policyProbe(model, seed);
  if (modelDigest(model) !== beforeDigest)
    throw new Error("frozen probe changed training state");
  // The native Brain.learn path still computes TD and trace decay. Freezing
  // one parameter group acts only at its existing update(w, ...) boundary.
  const originalUpdate = brain.update;
  if (arm === "actor-frozen" || arm === "critic-frozen") {
    brain.update = function (w, ...args) {
      if ((arm === "actor-frozen" && w === this.P) ||
          (arm === "critic-frozen" && w === this.v)) return;
      return originalUpdate.call(this, w, ...args);
    };
  }
  let absTD = 0, appliedRewardSum = 0, updates = 0;
  try {
    for (const [i, row] of stream.steps.entries()) {
      if (arm === "trace-one-step") {
        brain.ev.fill(0);
        brain.eP.fill(0);
      }
      forcedAct(brain, Float32Array.from(row.before), row.action);
      const shifted = stream.steps[(i + 7) % stream.steps.length].reward;
      const reward = arm === "zero-feedback" ? 0 :
        arm === "reward-shifted" ? shifted : row.reward;
      const next = row.terminal ? null : brain.encode(
        Float32Array.from(row.after), 0);
      brain.learn(reward, arm === "no-bootstrap" ? null : next, row.end);
      if (!Number.isFinite(brain.dopamine))
        throw new Error("nonfinite replay TD error");
      absTD += Math.abs(brain.dopamine);
      appliedRewardSum += reward;
      updates++;
      if (row.end && (!brain.ev.every(x => x === 0) ||
                      !brain.eP.every(x => x === 0)))
        throw new Error("eligibility not cleared at replay episode boundary");
    }
  } finally {
    brain.update = originalUpdate;
  }
  const digest = modelDigest(model), afterProbe = policyProbe(model, seed);
  if (modelDigest(model) !== digest)
    throw new Error("frozen replay probe changed training state");
  const probeChangeL1 = Object.keys(beforeProbe).reduce((s, key) =>
    s + Math.abs(afterProbe[key] - beforeProbe[key]), 0);
  return {
    streamHash: stream.hash,
    replayDecisions: updates, replayEnvironmentSteps: 0,
    recordedEnvironmentSteps: stream.steps.length,
    recordedEpisodes: stream.episodes, scriptedEpisodes: stream.scripted,
    recordedSuccesses: stream.completions, recordedInvalid: stream.invalid,
    originalRewardSum: stream.rewardSum, appliedRewardSum,
    actorDeltaL1: l1(brain.P, beforeP),
    criticDeltaL1: l1(brain.v, beforeV),
    meanAbsTD: absTD / updates, beforeProbe, afterProbe, probeChangeL1,
    modelBytes: modelBytes(model), policyOracleQueries: 0,
    policyEnvironmentInteractions: 0,
    replayProvenance: "forced action, fixed logged observations, offline TD; not on-policy",
  };
}

export function runSeed(seed, { episodes = 12 } = {}) {
  const stream = makeStream(seed, episodes);
  return ARMS.map(arm => {
    const started = Date.now();
    try {
      return run({ arm, seed, split: "logged-public-transitions-not-transfer",
        status: "ok", seconds: (Date.now() - started) / 1000,
        scores: replay(seed, arm, stream) });
    } catch (e) {
      return run({ arm, seed, split: "logged-public-transitions-not-transfer",
        status: "error", reason: String(e?.message ?? e),
        seconds: (Date.now() - started) / 1000, scores: {} });
    }
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  function option(flag, fallback) {
    const i = args.indexOf(flag);
    if (i < 0) return fallback;
    if (i === args.length - 1) throw new Error("missing " + flag + " value");
    return args.splice(i, 2)[1];
  }
  const out = option("--out", null);
  const episodes = Number(option("--episodes", "12"));
  const seeds = args.length ? args.map(Number) : [1, 2, 3];
  if (!out || seeds.length < 1 || new Set(seeds).size !== seeds.length ||
      seeds.some(s => !Number.isSafeInteger(s) || s < 0))
    throw new Error("provide --out FILE, --episodes N and unique seed(s)");
  const runs = seeds.flatMap(seed => runSeed(seed, { episodes }));
  writeResult(out, resultRecord({
    experiment: "brain-world/m0d-matched-public-transition-credit-replay",
    baseline: "native", runs,
    config: { arms: ARMS, seeds, episodes, tasks: TASKS,
      source: "alternating explicit demonstration and uniform random behavior",
      loggedFields: "public observations, selected action, post-action reward and terminal flags",
      noModelRollout: true },
    budgets: { loggedEpisodesPerSeed: episodes, replayPassesPerArm: 1,
      trainedEnvironmentInteractionsPerArm: 0, policyOracleQueriesPerArm: 0,
      comparison: "same recorded experiences; does not equal on-policy distribution" },
    metrics: {},
  }));
  for (const arm of ARMS) {
    const rows = runs.filter(x => x.arm === arm && x.status === "ok");
    const mean = rows.length ? rows.reduce((s, x) =>
      s + x.scores.probeChangeL1, 0) / rows.length : 0;
    console.log(arm, rows.length, "valid seeds; policy probe L1 change",
      mean.toFixed(5));
  }
  if (runs.some(r => r.status !== "ok")) process.exitCode = 1;
}
