// M0c matched-step, one-drop credit protocol (#112/#153), follow-up to Round 28 of the review ledger.
// 1. Matched effective step: every arm updates with the SAME per-weight step eta on every
//    decision, independent of hidden width. Brain's learn() divides lrP/lrV by 1 + running |h|^2;
//    the protocol sets lrP = lrV = eta * (1 + next running |h|^2) just before each learn() call,
//    so the step learn() applies is exactly eta. Brain source and its backprop-free rule are unchanged.
// 2. eta is selected on development goals and seeds (native arm), then frozen; ablations are
//    reported at the selected eta and the second-best one. 20 evaluation seeds, 3 contrasts.
// 3. One-drop family: dropping the item off the goal ends the episode. Scoring uses common random
//    numbers across goals, so any goal-blind policy delivers on at most one goal per repeat and its
//    success is at most 1/k exactly (k goals). One memorised route cannot exceed 1/k.
import { pathToFileURL } from "node:url";
import { GAINS, rng } from "./brain.js";
import { ALLOWED, initial, transition } from "./stateful_construct.mjs";
import { cloneForEvaluation, modelBytes } from "./stateful_options.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";
import { DEV_SEEDS, GOALS, assertGoalSplits, makeModel, sense, taskFor } from
  "./stateful_credit_protocol.mjs";

export { DEV_SEEDS, GOALS };
export const ARMS = Object.freeze(["native", "mask-goal", "trace-one-step", "no-hidden"]);
export const ETAS = Object.freeze([0.001, 0.002, 0.004, 0.008, 0.016, 0.032, 0.064]);
export const EVAL_SEEDS = Object.freeze(Array.from({ length: 20 }, (_, i) => i + 1));
const key = p => p.join(",");
const mix = (a, b) => (Math.imul(a >>> 0, 1664525) + b + 1013904223) >>> 0;
const mean = a => a.length ? a.reduce((s, v) => s + v, 0) / a.length : 0;

// One-drop rule: a misplaced drop is terminal (its -0.2 reward is kept).
export function step(task, state, action) {
  const r = transition(task, state, action);
  if (r.reason !== "misplaced") return r;
  return { ...r, done: true, state: { ...r.state, done: true } };
}

// The running |h|^2 that learn() is about to compute, replicated term for term.
function nextRunningHH(brain) {
  let hh = 0;
  for (let i = 0; i < brain.nH; i++) hh += brain.h[i] * brain.h[i];
  return brain.hh ? 0.99 * brain.hh + 0.01 * hh : hh;
}
export function matchedLearn(brain, eta, reward, next, end) {
  if (!(eta > 0) || !Number.isFinite(eta)) throw new Error("invalid matched step");
  const saved = [GAINS.lrP, GAINS.lrV], norm = 1 + nextRunningHH(brain);
  GAINS.lrP = eta * norm; GAINS.lrV = eta * norm;
  try {
    brain.learn(reward, next, end);
    return GAINS.lrP / (1 + brain.hh);   // the actor step learn() applied
  } finally { [GAINS.lrP, GAINS.lrV] = saved; }
}

// flag-only (used by the Round 30 transfer protocol): goal plane zeroed, at-goal flag kept.
export const SENSE_ARMS = Object.freeze([...ARMS, "flag-only"]);
function senseFor(task, state, arm) {
  if (arm !== "flag-only") return sense(task, state, arm);
  const y = sense(task, state, "native");
  y.fill(0, 50, 75);
  return y;
}

export function rollout(model, arm, task, { learn = false, eta = null, cap = task.maxSteps,
  rewards = null } = {}) {
  if (!SENSE_ARMS.includes(arm) || !Number.isSafeInteger(cap) || cap < 1 || cap > task.maxSteps)
    throw new Error("invalid protocol episode");
  const brain = model.brains[0], was = [brain.learning, brain.greedy];
  brain.learning = learn; brain.greedy = false;
  const out = { success: false, decisions: 0, misplaced: 0, tdAbsSum: 0, stepSum: 0,
    stepMaxDev: 0 };
  let state = initial(task);
  try {
    for (let k = 0; k < cap; k++) {
      if (learn && arm === "trace-one-step") { brain.ev.fill(0); brain.eP.fill(0); }
      const action = brain.act(brain.encode(senseFor(task, state, arm), 0), ALLOWED);
      const result = step(task, state, action);
      out.decisions++;
      out.misplaced += Number(result.reason === "misplaced");
      if (learn) {
        rewards?.push(result.reward);
        const next = result.done ? null : brain.encode(senseFor(task, result.state, arm), 0);
        const applied = matchedLearn(brain, eta, result.reward, next, result.done || k === cap - 1);
        if (!Number.isFinite(brain.dopamine)) throw new Error("nonfinite TD error");
        out.tdAbsSum += Math.abs(brain.dopamine);
        out.stepSum += applied;
        out.stepMaxDev = Math.max(out.stepMaxDev, Math.abs(applied - eta) / eta);
      }
      state = result.state;
      if (result.done) { out.success = result.success; break; }
    }
    return out;
  } finally { [brain.learning, brain.greedy] = was; }
}

// Frozen scoring with common random numbers: repeat r uses the same evaluation seed for every
// goal, so a goal-blind policy follows one trajectory per repeat and succeeds on <= 1 goal.
export function score(model, arm, split, repeats, seed, goals = GOALS) {
  const perGoal = {}, perRepeat = new Array(repeats).fill(0);
  let wins = 0, misplaced = 0, n = 0;
  for (const goal of goals[split]) {
    let w = 0;
    for (let r = 0; r < repeats; r++) {
      const x = rollout(cloneForEvaluation(model, mix(seed, 1009 + r * 17)), arm,
        taskFor(goal, split));
      w += Number(x.success); perRepeat[r] += Number(x.success); misplaced += x.misplaced; n++;
    }
    perGoal[key(goal)] = w / repeats; wins += w;
  }
  return { success: wins / n, episodes: n, deliveries: wins, misplaced, perGoal,
    goalBlindCeiling: 1 / goals[split].length, maxGoalsPerRepeat: Math.max(...perRepeat) };
}

function policyAt(brain, task, state, arm) {
  return Array.from(brain.policy(brain.encode(senseFor(task, state, arm), 0), ALLOWED,
    new Float32Array(brain.pi.length))).slice(0, ALLOWED.length);
}
const l1 = (p, q) => p.reduce((s, v, i) => s + Math.abs(v - q[i]), 0);
export function goalSensitivity(model, arm, seed, goals = GOALS) {
  const brain = cloneForEvaluation(model, seed).brains[0];
  const tasks = goals.train.map(g => taskFor(g, "train"));
  const pairs = fn => {
    const p = tasks.map(fn), d = [];
    for (let i = 0; i < p.length; i++) for (let j = i + 1; j < p.length; j++) d.push(l1(p[i], p[j]));
    return mean(d);
  };
  return { startL1: pairs(t => policyAt(brain, t, initial(t), arm)),
    carryingL1: pairs(t => policyAt(brain, t, step(t, initial(t), 4).state, arm)) };
}

// Goal order comes from a seed-only RNG: every arm and eta sees the same goal sequence.
export function train(model, arm, split, seed, budget, eta, goals = GOALS) {
  const R = rng(mix(seed, 307)), rewards = [];
  let decisions = 0, episodes = 0, deliveries = 0, td = 0, stepSum = 0, stepMaxDev = 0;
  while (decisions < budget) {
    const goal = goals[split][Math.floor(R() * goals[split].length)];
    const x = rollout(model, arm, taskFor(goal, split), { learn: true, eta, rewards,
      cap: Math.min(12, budget - decisions) });
    decisions += x.decisions; episodes++; deliveries += Number(x.success);
    td += x.tdAbsSum; stepSum += x.stepSum; stepMaxDev = Math.max(stepMaxDev, x.stepMaxDev);
  }
  if (decisions !== budget || rewards.length !== budget) throw new Error("decision budget mismatch");
  return { decisions, episodes, deliveries, meanAbsTD: td / budget, meanActorStep: stepSum / budget,
    maxStepRelDev: stepMaxDev, eta };
}

export function attempt(fields, fn) {
  const start = Date.now();
  try {
    const scores = fn();
    return run({ ...fields, status: "ok", seconds: (Date.now() - start) / 1000, scores });
  } catch (e) {
    return run({ ...fields, status: "error", reason: String(e?.message ?? e),
      seconds: (Date.now() - start) / 1000, scores: {} });
  }
}
export const label = (arm, eta) => `${arm}@eta${eta}`;

// Dev selection. Every arm is run for a descriptive per-arm curve; only native rows choose eta.
// Rule (preregistered): highest mean native dev success; divergence = 0; ties -> smaller eta.
// Ablations run at the selected eta and the second-best eta (same rule, selected one excluded).
export function select({ seeds = DEV_SEEDS, etas = ETAS, budget = 8000, repeats = 12 } = {}) {
  const rows = [];
  for (const arm of ARMS) for (const eta of etas) for (const seed of seeds)
    rows.push(attempt({ arm: label(arm, eta), seed, split: "dev-selection" }, () => {
      const model = makeModel(seed, arm);
      const training = train(model, arm, "dev", seed, budget, eta);
      const dev = score(model, arm, "dev", repeats, seed);
      return { eta, baseArm: arm, training, dev, primary: dev };
    }));
  const curve = arm => etas.map(eta => {
    const g = rows.filter(r => r.arm === label(arm, eta));
    return { eta, devSuccess: mean(g.map(r => r.status === "ok" ? r.scores.dev.success : 0)),
      errors: g.filter(r => r.status !== "ok").length };
  });
  const pick = list => list.reduce((b, s) => s.devSuccess > b.devSuccess + 1e-12 ? s : b);
  const curves = Object.fromEntries(ARMS.map(a => [a, curve(a)]));
  const selected = pick(curves.native).eta;
  const second = pick(curves.native.filter(s => s.eta !== selected)).eta;
  const perArmBest = Object.fromEntries(ARMS.map(a => [a, pick(curves[a]).eta]));
  return { rows, curves, selected, second, evalEtas: [selected, second], perArmBest };
}

export function evalArm(seed, arm, eta, { budget = 8000, repeats = 12, goals = GOALS,
  split = "eval" } = {}) {
  if (!Number.isSafeInteger(seed) || seed < 0 || DEV_SEEDS.includes(seed))
    throw new Error("evaluation seeds must be disjoint from development seeds");
  return attempt({ arm: label(arm, eta), seed, split }, () => {
    const model = makeModel(seed, arm === "flag-only" ? "native" : arm);
    const both = () => ({ train: score(model, arm, "train", repeats, seed, goals),
      heldout: score(model, arm, "heldout", repeats, seed, goals) });
    const before = both();
    const training = train(model, arm, "train", seed, budget, eta, goals);
    const after = both();
    return { eta, baseArm: arm, before, training, after, primary: after.train,
      goalSensitivity: goalSensitivity(model, arm, mix(seed, 401), goals),
      modelBytes: modelBytes(model), onlineOracleQueries: 0 };
  });
}
export const runSeed = (seed, eta, opts = {}) => ARMS.map(arm => evalArm(seed, arm, eta, opts));

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  const option = (name, fallback) => {
    const at = args.indexOf(name);
    return at < 0 ? fallback : args.splice(at, 2)[1];
  };
  const budget = Number(option("--budget", "8000")), repeats = Number(option("--repeats", "12"));
  const devSeeds = option("--dev-seeds", DEV_SEEDS.join(",")).split(",").map(Number);
  const etas = option("--etas", ETAS.join(",")).split(",").map(Number);
  const out = option("--out", null);
  const seeds = args.length ? args.map(Number) : [...EVAL_SEEDS];
  if (!out || !Number.isSafeInteger(budget) || budget < 1 || !Number.isSafeInteger(repeats) ||
      repeats < 1 || new Set(seeds).size !== seeds.length || etas.length < 2 ||
      etas.some(e => !(e > 0)) || new Set(etas).size !== etas.length ||
      seeds.some(s => !Number.isSafeInteger(s) || s < 0 || devSeeds.includes(s)))
    throw new Error("usage: --out FILE [--budget N] [--repeats R] [--dev-seeds a,b] " +
      "[--etas a,b,...] eval-seed ...");
  assertGoalSplits();
  const selection = select({ seeds: devSeeds, etas, budget, repeats });
  const runs = [...selection.rows, ...selection.evalEtas.flatMap(eta => seeds.flatMap(seed =>
    runSeed(seed, eta, { budget, repeats })))];
  writeResult(out, resultRecord({
    experiment: "brain-world/m0c-matched-step-credit-protocol",
    baseline: label("native", selection.selected), runs,
    config: { arms: ARMS, goals: GOALS, devSeeds, seeds, etaGrid: etas,
      selection: { curves: selection.curves, selected: selection.selected,
        second: selection.second, perArmBest: selection.perArmBest,
        rule: "max mean native dev success on dev goals/seeds only; ties -> smaller eta; " +
          "eval at the selected and the second-best eta" },
      evalEtas: selection.evalEtas, budget, repeats, family: "one-drop",
      stepRule: "lrP = lrV = eta * (1 + next running |h|^2) before every learn()",
      baseGains: { lrP: GAINS.lrP, lrV: GAINS.lrV } },
    budgets: { trainDecisionsPerArm: budget, policyOracleQueriesPerArm: 0, frozenScoring: true,
      note: "single 5x5 one-drop family, item at start; heldout goals untrained, same geometry" },
    // primary = dev score on selection rows, trained-goal score on eval rows.
    metrics: { "primary.success": "higher" },
  }));
  console.log("selected eta", selection.selected, "second", selection.second,
    "per-arm best", JSON.stringify(selection.perArmBest));
  for (const eta of selection.evalEtas) for (const arm of ARMS) {
    const g = runs.filter(r => r.arm === label(arm, eta) && r.split === "eval");
    const ok = g.filter(r => r.status === "ok");
    console.log(label(arm, eta).padEnd(24), "ok", ok.length, "/", g.length,
      "train", mean(ok.map(r => r.scores.after.train.success)).toFixed(3),
      "heldout", mean(ok.map(r => r.scores.after.heldout.success)).toFixed(3));
  }
}
