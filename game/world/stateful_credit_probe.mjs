// M0c frozen sensor/action/TD-credit audit (#112/#153); independent of Brain World's curriculum.
// All learned arms preserve the existing backprop-free Brain class, same six primitives,
// transitions and reward. Single-task ablations diagnose mechanisms; NOT heldout transfer.
import { pathToFileURL } from "node:url";
// Brain remains a separately imported class through the existing stateful model adapter.
import { ALLOWED, initial, observe, transition } from "./stateful_construct.mjs";
import { TASK, PROBES } from "./stateful_calibration.mjs";
import { cloneForEvaluation, createModel, modelBytes } from "./stateful_options.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

export const ARMS = Object.freeze([
  "native-three", "native-two", "mask-goal", "zero-feedback",
  "trace-one-step", "no-bootstrap",
]);
export const TASK_TWO = Object.freeze({ ...TASK, id: "two-step-pick-drop",
  goal: [2, 0] });
const mix = (a, b) => (Math.imul(a >>> 0, 1664525) + b + 1013904223) >>> 0;
const localTask = arm => arm === "native-two" ? TASK_TWO : TASK;
const mean = (s, n) => n ? s / n : 0;
function sense(task, state, arm) {
  const x = observe(task, state);
  if (arm === "mask-goal") {
    x.fill(0, 50, 75);
    x[81] = 0;
  }
  return x;
}
function actorEntropy(pi) {
  // Brain.policy stores probabilities in Float32Array: equal 1/6 values sum
  // slightly ABOVE 1 in float32. Renormalize for descriptive entropy only,
  // without changing the action sampler or silently admitting invalid logits.
  let sum = 0;
  for (const a of ALLOWED) {
    if (!Number.isFinite(pi[a]) || pi[a] < 0) throw new Error("invalid actor probabilities");
    sum += pi[a];
  }
  if (!Number.isFinite(sum) || Math.abs(sum - 1) > 1e-4)
    throw new Error("invalid actor probability normalization");
  let e = 0;
  for (const a of ALLOWED) {
    const p = pi[a] / sum;
    if (p > 0) e -= p * Math.log(p);
  }
  return Math.min(1, Math.max(0, e / Math.log(ALLOWED.length)));
}
export function rollout(model, arm, task, { learn = false,
  cap = task.maxSteps } = {}) {
  if (!ARMS.includes(arm) || !Number.isSafeInteger(cap) ||
      cap < 1 || cap > task.maxSteps)
    throw new Error("invalid credit probe episode");
  const brain = model.brains[0], wasLearning = brain.learning;
  const wasGreedy = brain.greedy;
  brain.learning = learn;
  brain.greedy = false;
  const counters = { success: false, decisions: 0, envSteps: 0, invalid: 0,
    pickups: 0, blocked: 0, misplaced: 0, rewardSum: 0,
    tdAbsSum: 0, tdUpdates: 0, entropySum: 0, entropyDecisions: 0,
    tracePMax: 0, truncated: false };
  let state = initial(task);
  try {
    for (let k = 0; k < cap; k++) {
      const x = sense(task, state, arm);
      if (learn && arm === "trace-one-step") {
        // Ablate PREVIOUS-step eligibility only; act still writes the current
        // state's exact policy-gradient trace. No change to Brain source/GAINS.
        brain.ev.fill(0);
        brain.eP.fill(0);
      }
      const action = brain.act(brain.encode(x, 0), ALLOWED);
      const entropy = actorEntropy(brain.pi);
      if (!Number.isFinite(entropy) || entropy < -1e-8 || entropy > 1 + 1e-8)
        throw new Error("invalid action probability distribution");
      counters.entropySum += entropy; counters.entropyDecisions++;
      if (learn) {
        let peak = 0;
        for (const v of brain.eP) peak = Math.max(peak, Math.abs(v));
        counters.tracePMax = Math.max(counters.tracePMax, peak);
      }
      const result = transition(task, state, action);
      counters.decisions++; counters.envSteps++;
      counters.rewardSum += result.reward;
      counters.invalid += Number(result.invalid);
      counters.pickups += Number(result.reason === "picked-up");
      counters.blocked += Number(result.reason === "blocked");
      counters.misplaced += Number(result.reason === "misplaced");
      if (learn) {
        const reward = arm === "zero-feedback" ? 0 : result.reward;
        const next = result.done ? null : brain.encode(
          sense(task, result.state, arm), 0);
        const end = result.done || k === cap - 1;
        // Intentionally distinguish cutting off the next-state TD value from
        // cutting the eligibility trace: null and end are independent arguments.
        brain.learn(reward, arm === "no-bootstrap" ? null : next, end);
        if (!Number.isFinite(brain.dopamine))
          throw new Error("nonfinite TD error");
        counters.tdAbsSum += Math.abs(brain.dopamine);
        counters.tdUpdates++;
      }
      state = result.state;
      if (result.done) {
        counters.success = result.success;
        break;
      }
    }
    counters.truncated = !state.done && cap < task.maxSteps;
    counters.entropy = mean(counters.entropySum, counters.entropyDecisions);
    counters.meanAbsTD = mean(counters.tdAbsSum, counters.tdUpdates);
    return counters;
  } finally {
    brain.learning = wasLearning;
    brain.greedy = wasGreedy;
  }
}
function policyFor(brain, obs) {
  return Array.from(brain.policy(brain.encode(obs, 0), ALLOWED,
    new Float32Array(brain.pi.length))).slice(0, ALLOWED.length);
}
const l1 = (x, y) => x.reduce((s, v, i) => s + Math.abs(v - y[i]), 0);

// Counterfactual probes modify only PUBLIC observations and never update weights.
// All goals are fully visible in original x[50:75]; this does not establish the
// learner *uses* them causally when the fixed training task never varies.
export function sensoryAudit(model, arm, seed) {
  const brain = cloneForEvaluation(model, seed).brains[0];
  const here = initial(TASK), alternate = { ...TASK,
    goal: [1, 0], id: "counterfactual-target" };
  const raw = observe(TASK, here), other = observe(alternate, here);
  const carry = transition(TASK, here, 4).state;
  const post = observe(TASK, carry), postOther = observe(alternate, carry);
  const p = policyFor(brain, arm === "mask-goal" ? sense(TASK, here, arm) : raw);
  const q = policyFor(brain, arm === "mask-goal" ? sense(alternate, here, arm) : other);
  const cp = policyFor(brain, arm === "mask-goal" ? sense(TASK, carry, arm) : post);
  const cq = policyFor(brain, arm === "mask-goal" ? sense(alternate, carry, arm) : postOther);
  const actor = i => ALLOWED.reduce((s, a) =>
    s + Math.abs(brain.P[a * brain.nH + i]), 0);
  const region = (from, until) => Array.from({ length: until - from },
    (_, j) => actor(j + from)).reduce((a, b) => a + b, 0);
  if (brain.nIn < raw.length || raw.length < 84)
    throw new Error("public construction fields inaccessible to direct actor");
  return { rawInputWidth: raw.length, directActorInputWidth: brain.nIn,
    goalCounterfactualL1: l1(p, q),
    carryingGoalCounterfactualL1: l1(cp, cq),
    agentActorL1: region(0, 25), itemActorL1: region(25, 50),
    goalActorL1: region(50, 75), carryingActorL1: actor(75),
    collisionActorL1: region(76, 80),
    directGoalMasked: arm === "mask-goal" };
}
function scored(model, arm, tasks, repeats, seed, salt) {
  const summary = { success: 0, deliveries: 0, pickups: 0, invalid: 0,
    decisions: 0, envSteps: 0, episodes: tasks.length * repeats,
    entropy: 0, failed: 0 };
  let entropySum = 0, entropyN = 0;
  for (let i = 0; i < tasks.length; i++) for (let j = 0; j < repeats; j++) {
    const copy = cloneForEvaluation(model, mix(seed, salt + i * 103 + j * 53));
    const x = rollout(copy, arm, tasks[i], { learn: false });
    summary.deliveries += Number(x.success);
    summary.pickups += x.pickups; summary.invalid += x.invalid;
    summary.decisions += x.decisions; summary.envSteps += x.envSteps;
    entropySum += x.entropySum; entropyN += x.entropyDecisions;
  }
  summary.failed = summary.episodes - summary.deliveries;
  summary.success = summary.deliveries / summary.episodes;
  summary.entropy = mean(entropySum, entropyN);
  return summary;
}
export function runSeed(seed, { checkpoints = [0, 250, 1000, 4000],
  repeats = 12 } = {}) {
  if (!Number.isSafeInteger(seed) || seed < 0 || !Array.isArray(checkpoints) ||
      checkpoints.length < 2 || checkpoints[0] !== 0 ||
      checkpoints.some((x, i) => !Number.isSafeInteger(x) || x < 0 ||
        (i > 0 && x <= checkpoints[i - 1])) ||
      !Number.isSafeInteger(repeats) || repeats < 1)
    throw new Error("invalid credit probe configuration");
  return ARMS.map(arm => {
    const start = Date.now();
    try {
      const model = createModel(mix(seed, 119), "flat");
      let decisions = 0, steps = 0, episodes = 0, pickups = 0, deliveries = 0;
      let invalid = 0, tdAbsSum = 0, tdUpdates = 0, tracePMax = 0;
      const curve = [];
      for (const target of checkpoints) {
        while (decisions < target) {
          const remaining = target - decisions;
          const x = rollout(model, arm, localTask(arm), { learn: true,
            cap: Math.min(localTask(arm).maxSteps, remaining) });
          if (x.decisions < 1 || x.decisions > remaining ||
              x.decisions !== x.envSteps || x.tdUpdates !== x.decisions)
            throw new Error("training action/feedback count mismatch");
          decisions += x.decisions; steps += x.envSteps; episodes++;
          pickups += x.pickups; deliveries += Number(x.success);
          invalid += x.invalid;
          tdAbsSum += x.tdAbsSum; tdUpdates += x.tdUpdates;
          tracePMax = Math.max(tracePMax, x.tracePMax);
        }
        curve.push({ decisions: target,
          calibration: scored(model, arm, [localTask(arm)], repeats, seed, 101),
          diagnosticVariants: scored(model, arm, PROBES, repeats, seed, 107),
          sensory: sensoryAudit(model, arm, mix(seed, target + 109)) });
      }
      return run({ arm, seed, split: "same-geometry-credit-diagnostic-not-transfer",
        status: "ok", seconds: (Date.now() - start) / 1000,
        scores: { curve, trainDecisions: decisions, trainEnvSteps: steps,
          trainEpisodes: episodes, trainPickups: pickups,
          trainDeliveries: deliveries, trainInvalid: invalid,
          trainMeanAbsTD: mean(tdAbsSum, tdUpdates), tracePMax,
          learningUpdates: tdUpdates, modelBytes: modelBytes(model),
          onlineOracleQueries: 0 } });
    } catch (e) {
      return run({ arm, seed, split: "same-geometry-credit-diagnostic-not-transfer",
        status: "error", reason: String(e?.message ?? e), seconds: (Date.now() - start) / 1000,
        scores: {} });
    }
  });
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  function option(name, fallback) {
    const at = args.indexOf(name);
    return at < 0 ? fallback : args.splice(at, 2)[1];
  }
  const checkpoints = option("--checkpoints", "0,250,1000,4000").split(",").map(Number);
  const repeats = Number(option("--repeats", "12"));
  const out = option("--out", null);
  const seeds = args.length ? args.map(Number) : [1, 2, 3];
  if (!out || !seeds.length || new Set(seeds).size !== seeds.length ||
      seeds.some(s => !Number.isSafeInteger(s) || s < 0))
    throw new Error("provide --out FILE, optional --checkpoints, --repeats, and seed(s)");
  const runs = seeds.flatMap(seed => runSeed(seed, { checkpoints, repeats }));
  writeResult(out, resultRecord({
    experiment: "brain-world/m0c-causal-sensory-td-audit",
    baseline: "native-three", runs,
    config: { arms: ARMS, seeds, checkpoints, repeats, taskThree: TASK,
      taskTwo: TASK_TWO, diagnosticVariants: PROBES, observer: "public sensors only",
      ablations: "no-goal, zero-reward, one-step eligibility, no-critic-bootstrap" },
    budgets: { physicalDecisionsPerArm: checkpoints.at(-1),
      policyOracleQueriesPerArm: 0, frozenScoring: true,
      note: "same fixed task; two-step arm has simpler objective, not fair geometry transfer" },
    metrics: { trainDeliveries: "higher", trainInvalid: "lower",
      trainEnvSteps: "lower" },
  }));
  for (const arm of ARMS) {
    const group = runs.filter(r => r.arm === arm && r.status === "ok");
    console.log(arm, group.length, "seeds; mean final delivery",
      mean(group.reduce((s, r) => s + r.scores.curve.at(-1).calibration.success, 0),
        group.length).toFixed(3));
  }
  if (runs.some(r => r.status !== "ok")) process.exitCode = 1;
}
