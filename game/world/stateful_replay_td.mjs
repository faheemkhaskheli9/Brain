// M0c identical-transition update-rule test (#112/#153). One logged stream of public transitions
// (from a native-three learner's own training) is replayed into fresh, identically initialised
// Brain learners that differ ONLY in the TD / eligibility rule, so state visitation cannot differ.
// Actions are forced to the logged ones; nothing about Brain or its GAINS changes.
// Diagnostic on one fixed task: NOT transfer. Run: node stateful_replay_td.mjs --out FILE seed...
import { pathToFileURL } from "node:url";
import { ALLOWED, initial, transition } from "./stateful_construct.mjs";
import { TASK, PROBES } from "./stateful_calibration.mjs";
import { cloneForEvaluation, createModel, modelBytes } from "./stateful_options.mjs";
import { rollout } from "./stateful_credit_probe.mjs";
import { observe } from "./stateful_construct.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

export const ARMS = Object.freeze(["replay-native", "replay-no-bootstrap",
  "replay-trace-one-step", "replay-zero-feedback", "replay-shuffled"]);
const mix = (a, b) => (Math.imul(a >>> 0, 1664525) + b + 1013904223) >>> 0;
const mean = (s, n) => n ? s / n : 0;

// Log the native learner's training: [obs, action, reward, nextObs|null, end] per decision.
export function logStream(seed, decisions) {
  if (!Number.isSafeInteger(decisions) || decisions < 1) throw new Error("invalid stream length");
  const model = createModel(mix(seed, 119), "flat"), brain = model.brains[0], log = [];
  brain.learning = true;
  let state = initial(TASK), k = 0;
  while (log.length < decisions) {
    const x = observe(TASK, state), h = brain.encode(x, 0), action = brain.act(h, ALLOWED);
    const r = transition(TASK, state, action), last = log.length === decisions - 1;
    const nextObs = r.done ? null : observe(TASK, r.state);
    log.push({ x, action, reward: r.reward, nextObs, end: r.done || last || ++k >= TASK.maxSteps });
    brain.learn(r.reward, nextObs ? brain.encode(nextObs, 0) : null, log.at(-1).end);
    if (log.at(-1).end) { state = initial(TASK); k = 0; } else state = r.state;
  }
  Object.defineProperty(log, "model", { value: model });   // the logging learner, for the fidelity check
  return log;
}

// Force `brain.act` to choose `action` by steering the sampler's uniform draw into its interval.
function forcedAct(brain, h, action) {
  const pi = brain.policy(h, ALLOWED, new Float32Array(brain.pi.length));
  let before = 0;
  for (const a of ALLOWED) { if (a === action) break; before += pi[a]; }
  const keep = brain.rand, wasGreedy = brain.greedy;
  brain.rand = () => before + pi[action] / 2; brain.greedy = false;
  try {
    const choice = brain.act(h, ALLOWED);
    if (choice !== action) throw new Error("forced action not taken");
  } finally { brain.rand = keep; brain.greedy = wasGreedy; }
}

export function replay(model, arm, log) {
  if (!ARMS.includes(arm)) throw new Error("invalid replay arm");
  const brain = model.brains[0];
  let order = log;
  if (arm === "replay-shuffled") {   // same transitions, order destroyed: breaks trace credit only
    let s = 0x9E3779B9; order = [...log];
    for (let i = order.length - 1; i > 0; i--) {
      s = mix(s, i); const j = s % (i + 1); [order[i], order[j]] = [order[j], order[i]];
    }
  }
  brain.learning = true; brain.greedy = false;
  let tdAbs = 0;
  for (const t of order) {
    if (arm === "replay-trace-one-step") { brain.ev.fill(0); brain.eP.fill(0); }
    const h = brain.encode(t.x, 0);
    forcedAct(brain, h, t.action);
    const reward = arm === "replay-zero-feedback" ? 0 : t.reward;
    const next = arm === "replay-no-bootstrap" || !t.nextObs ? null : brain.encode(t.nextObs, 0);
    brain.learn(reward, next, t.end);
    if (!Number.isFinite(brain.dopamine)) throw new Error("nonfinite TD error");
    tdAbs += Math.abs(brain.dopamine);
  }
  brain.learning = false;
  return { meanAbsTD: mean(tdAbs, order.length), updates: order.length };
}

function score(model, tasks, repeats, seed, salt) {
  let ok = 0, n = 0;
  for (let i = 0; i < tasks.length; i++) for (let j = 0; j < repeats; j++) {
    const copy = cloneForEvaluation(model, mix(seed, salt + i * 103 + j * 53));
    ok += Number(rollout(copy, "native-three", tasks[i], { learn: false }).success); n++;
  }
  return { success: ok / n, episodes: n };
}

export function runSeed(seed, { decisions = 4000, repeats = 12 } = {}) {
  if (!Number.isSafeInteger(seed) || seed < 0 || !Number.isSafeInteger(repeats) || repeats < 1)
    throw new Error("invalid replay configuration");
  const log = logStream(seed, decisions);
  const logged = { deliveries: log.filter(t => t.end && t.reward > 0 && !t.x.every(v => v === 0)).length };
  return ARMS.map(arm => {
    const start = Date.now();
    try {
      const model = createModel(mix(seed, 119), "flat");   // same init as the logging learner
      const stats = replay(model, arm, log), calibration = score(model, [TASK], repeats, seed, 101);
      return run({ arm, seed, split: "identical-transition-replay-not-transfer", status: "ok",
        seconds: (Date.now() - start) / 1000,
        scores: { calibration, deliverySuccess: calibration.success,
          diagnosticVariants: score(model, PROBES, repeats, seed, 107),
          replayedTransitions: stats.updates, meanAbsTD: stats.meanAbsTD,
          loggedRewardEnds: logged.deliveries, modelBytes: modelBytes(model),
          onlineOracleQueries: 0 } });
    } catch (e) {
      return run({ arm, seed, split: "identical-transition-replay-not-transfer", status: "error",
        reason: String(e?.message ?? e), seconds: (Date.now() - start) / 1000, scores: {} });
    }
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  const option = (name, fallback) => { const at = args.indexOf(name); return at < 0 ? fallback : args.splice(at, 2)[1]; };
  const decisions = Number(option("--decisions", "4000")), repeats = Number(option("--repeats", "12"));
  const out = option("--out", null), seeds = args.length ? args.map(Number) : [1, 2, 3];
  if (!out || new Set(seeds).size !== seeds.length || seeds.some(s => !Number.isSafeInteger(s) || s < 0))
    throw new Error("provide --out FILE, optional --decisions, --repeats, and seed(s)");
  const runs = seeds.flatMap(seed => runSeed(seed, { decisions, repeats }));
  writeResult(out, resultRecord({ experiment: "brain-world/m0c-identical-transition-replay",
    baseline: "replay-native", runs,
    config: { arms: ARMS, seeds, decisions, repeats, task: TASK, diagnosticVariants: PROBES,
      design: "one logged native-three stream per seed replayed with forced actions into identically initialised learners; only the update rule differs" },
    budgets: { replayedTransitionsPerArm: decisions, policyOracleQueriesPerArm: 0, frozenScoring: true },
    metrics: { deliverySuccess: "higher" } }));
  for (const arm of ARMS) {
    const g = runs.filter(r => r.arm === arm && r.status === "ok");
    console.log(arm.padEnd(22), g.length, "seeds; mean delivery",
      mean(g.reduce((s, r) => s + r.scores.calibration.success, 0), g.length).toFixed(3));
  }
  if (runs.some(r => r.status !== "ok")) process.exitCode = 1;
}
