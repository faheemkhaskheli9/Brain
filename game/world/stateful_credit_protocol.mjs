// M0c frozen-step-size credit protocol (#112/#153), follow-up to Round 27 of the review ledger.
// 1. Learning-rate scale is SELECTED on development goals and seeds only, then frozen.
// 2. Ablations are reported at two step sizes: inherited (x1) and the selected one.
// 3. zero-feedback is replaced by a yoked-reward control (native's reward tape, nonzero TD error).
// 4. An "aligned" adapter layout moves the 3 item cells off Brain's multiplicative gain inputs.
// 5. Training and scoring use VARYING goals; heldout goals are never trained.
// Brain source and its backprop-free rule are unchanged; GAINS.lrP/lrV are scaled per run and restored.
import { pathToFileURL } from "node:url";
import { GAINS, N_IN, rng } from "./brain.js";
import { ALLOWED, initial, observe, transition } from "./stateful_construct.mjs";
import { cloneForEvaluation, createModel, modelBytes } from "./stateful_options.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

export const ARMS = Object.freeze(["native", "aligned", "mask-goal", "yoked-reward",
  "trace-one-step", "no-bootstrap", "no-hidden"]);
export const GOALS = Object.freeze({
  dev: Object.freeze([[0, 0], [2, 2], [3, 1]]),
  train: Object.freeze([[1, 1], [4, 0], [2, 1]]),
  heldout: Object.freeze([[1, 0], [3, 0]]),
});
export const DEV_SEEDS = Object.freeze([101, 102, 103, 104, 105]);
export const SCALES = Object.freeze([1, 2, 4, 8]);
export const START = Object.freeze([2, 0]);
const key = p => p.join(",");
export function assertGoalSplits() {
  const all = Object.values(GOALS).flat().map(key);
  if (new Set(all).size !== all.length || all.includes(key(START)))
    throw new Error("goal splits overlap or include the start cell");
}
export const taskFor = (goal, split) => ({ id: `${split}-${key(goal)}`, start: [...START],
  item: [...START], goal: [...goal], walls: [], maxSteps: 12 });
const mix = (a, b) => (Math.imul(a >>> 0, 1664525) + b + 1013904223) >>> 0;
const mean = a => a.length ? a.reduce((s, v) => s + v, 0) / a.length : 0;

// Brain's fixed wiring (brain.js constructor, 15-ray retina): 0-44 retina windows, 45-46 legs,
// 47-49 multiplicative cochlea GAIN inputs, 50-74 fovea, 75-81 body, 82-106 memory patch.
// observe() fills 0-83 in construct order, so item cells (2..4,4) land on the gain inputs and
// 84-106 are always zero. "aligned" is the minimal one-variable fix: only those three item
// cells move to 84-86 (memory drive patch), so the gains stay zero (gain == 1).
const NATIVE = Array.from({ length: 84 }, (_, i) => i);
export const LAYOUTS = Object.freeze({
  native: Object.freeze(NATIVE),
  aligned: Object.freeze(NATIVE.map(i => i >= 47 && i <= 49 ? i + 37 : i)),
});
const GAIN_INPUTS = [47, 48, 49];
export function layout(x, name) {
  const map = LAYOUTS[name];
  if (!map) throw new Error("unknown layout");
  const y = new Float32Array(N_IN);
  for (let i = 0; i < map.length; i++) y[map[i]] = x[i];
  return y;
}
const layoutOf = arm => arm === "aligned" ? "aligned" : "native";
export function sense(task, state, arm) {
  const y = layout(observe(task, state), layoutOf(arm));
  if (arm === "mask-goal") { y.fill(0, 50, 75); y[81] = 0; }
  return y;
}
// Share of hidden fan-in that can ever be nonzero under a layout (code-observed wiring audit).
export function fanInAudit(brain, name) {
  const live = new Set(LAYOUTS[name]), gain = { live: 0, total: 0 }, drive = { live: 0, total: 0 };
  for (let j = 0; j < brain.hidden; j++) for (let k = 0; k < 8; k++) {
    const slot = k < 3 ? gain : drive;
    slot.total++;
    slot.live += Number(live.has(brain.idx[j * 8 + k]));
  }
  return { gainInputsLive: gain.live / gain.total, driveInputsLive: drive.live / drive.total,
    gainIndicesUsed: GAIN_INPUTS.filter(i => live.has(i)).length };
}

export function withScale(scale, fn) {
  if (!(scale > 0) || !Number.isFinite(scale)) throw new Error("invalid step scale");
  const saved = [GAINS.lrP, GAINS.lrV];
  GAINS.lrP = saved[0] * scale; GAINS.lrV = saved[1] * scale;
  try { return fn(); } finally { [GAINS.lrP, GAINS.lrV] = saved; }
}

export function makeModel(seed, arm) {
  const model = createModel(mix(seed, 211), "flat");
  if (arm === "no-hidden") for (const b of model.brains) b.gate.fill(0);
  return model;
}

// One episode. tape: yoked rewards indexed by global training decision; offset is its position.
export function rollout(model, arm, task, { learn = false, cap = task.maxSteps,
  tape = null, offset = 0, rewards = null } = {}) {
  if (!ARMS.includes(arm) || !Number.isSafeInteger(cap) || cap < 1 || cap > task.maxSteps)
    throw new Error("invalid protocol episode");
  if (learn && arm === "yoked-reward" && (!tape || offset + cap > tape.length))
    throw new Error("yoked reward tape missing or too short");
  const brain = model.brains[0], was = [brain.learning, brain.greedy];
  brain.learning = learn; brain.greedy = false;
  const out = { success: false, decisions: 0, misplaced: 0, invalid: 0,
    tdAbsSum: 0, stepSum: 0, rewardSum: 0 };
  let state = initial(task);
  try {
    for (let k = 0; k < cap; k++) {
      if (learn && arm === "trace-one-step") { brain.ev.fill(0); brain.eP.fill(0); }
      const action = brain.act(brain.encode(sense(task, state, arm), 0), ALLOWED);
      const result = transition(task, state, action);
      out.decisions++;
      out.invalid += Number(result.invalid);
      out.misplaced += Number(result.reason === "misplaced");
      if (learn) {
        rewards?.push(result.reward);
        const reward = arm === "yoked-reward" ? tape[offset + k] : result.reward;
        const next = result.done ? null : brain.encode(sense(task, result.state, arm), 0);
        brain.learn(reward, arm === "no-bootstrap" ? null : next, result.done || k === cap - 1);
        if (!Number.isFinite(brain.dopamine)) throw new Error("nonfinite TD error");
        out.tdAbsSum += Math.abs(brain.dopamine);
        out.stepSum += GAINS.lrP / (1 + brain.hh);
        out.rewardSum += reward;
      }
      state = result.state;
      if (result.done) { out.success = result.success; break; }
    }
    return out;
  } finally { [brain.learning, brain.greedy] = was; }
}

function policyAt(brain, task, state, arm) {
  return Array.from(brain.policy(brain.encode(sense(task, state, arm), 0), ALLOWED,
    new Float32Array(brain.pi.length))).slice(0, ALLOWED.length);
}
const l1 = (p, q) => p.reduce((s, v, i) => s + Math.abs(v - q[i]), 0);
// Mean pairwise policy L1 between trained goals, at the start and right after pickup.
export function goalSensitivity(model, arm, seed) {
  const brain = cloneForEvaluation(model, seed).brains[0];
  const tasks = GOALS.train.map(g => taskFor(g, "train"));
  const pairs = (fn) => {
    const p = tasks.map(fn), d = [];
    for (let i = 0; i < p.length; i++) for (let j = i + 1; j < p.length; j++) d.push(l1(p[i], p[j]));
    return mean(d);
  };
  return {
    startL1: pairs(t => policyAt(brain, t, initial(t), arm)),
    carryingL1: pairs(t => policyAt(brain, t, transition(t, initial(t), 4).state, arm)),
  };
}

export function score(model, arm, split, repeats, seed) {
  const perGoal = {};
  let wins = 0, misplaced = 0, n = 0;
  GOALS[split].forEach((goal, i) => {
    let w = 0;
    for (let r = 0; r < repeats; r++) {
      const x = rollout(cloneForEvaluation(model, mix(seed, 1009 + i * 131 + r * 17)), arm,
        taskFor(goal, split));
      w += Number(x.success); misplaced += x.misplaced; n++;
    }
    perGoal[key(goal)] = w / repeats; wins += w;
  });
  return { success: wins / n, episodes: n, deliveries: wins, misplaced, perGoal };
}

// Train on a goal split. The goal of each episode is drawn from a seed-only RNG, so every arm
// sees the same goal order for the same episode index.
export function train(model, arm, split, seed, budget, { tape = null } = {}) {
  const R = rng(mix(seed, 307)), rewards = [];
  let decisions = 0, episodes = 0, deliveries = 0, td = 0, step = 0;
  while (decisions < budget) {
    const goal = GOALS[split][Math.floor(R() * GOALS[split].length)];
    const x = rollout(model, arm, taskFor(goal, split), { learn: true, tape, offset: decisions,
      rewards, cap: Math.min(12, budget - decisions) });
    decisions += x.decisions; episodes++; deliveries += Number(x.success);
    td += x.tdAbsSum; step += x.stepSum;
  }
  if (decisions !== budget || rewards.length !== budget) throw new Error("decision budget mismatch");
  return { decisions, episodes, deliveries, meanAbsTD: td / budget, meanActorStep: step / budget,
    rewards };
}

function attempt(fields, fn) {
  const start = Date.now();
  try {
    return run({ ...fields, status: "ok", seconds: (Date.now() - start) / 1000, scores: fn() });
  } catch (e) {
    return run({ ...fields, status: "error", reason: String(e?.message ?? e),
      seconds: (Date.now() - start) / 1000, scores: {} });
  }
}

// Development-only selection: native arm, dev goals, dev seeds. Divergence counts as 0 success.
// Rule (preregistered): highest mean dev success; ties go to the smaller scale.
export function select({ seeds = DEV_SEEDS, scales = SCALES, budget = 8000, repeats = 12 } = {}) {
  const rows = [];
  for (const scale of scales) for (const seed of seeds)
    rows.push(attempt({ arm: `native@x${scale}`, seed, split: "dev-selection" }, () =>
      withScale(scale, () => {
        const model = makeModel(seed, "native");
        const t = train(model, "native", "dev", seed, budget);
        delete t.rewards;
        const dev = score(model, "native", "dev", repeats, seed);
        return { scale, training: t, dev, primary: dev };
      })));
  const byScale = scales.map(scale => {
    const group = rows.filter(r => r.arm === `native@x${scale}`);
    return { scale, devSuccess: mean(group.map(r => r.status === "ok" ? r.scores.dev.success : 0)),
      errors: group.filter(r => r.status !== "ok").length };
  });
  const pick = list => list.reduce((b, s) => s.devSuccess > b.devSuccess + 1e-12 ? s : b);
  const selected = pick(byScale).scale;
  // Always evaluate two step sizes: x1 and the selected one, or the best other one if x1 wins.
  const second = selected === 1 ? pick(byScale.filter(s => s.scale !== 1)).scale : selected;
  return { rows, byScale, selected, evalScales: [1, second] };
}

export function runSeed(seed, scale, { budget = 8000, repeats = 12 } = {}) {
  if (!Number.isSafeInteger(seed) || seed < 0 || DEV_SEEDS.includes(seed))
    throw new Error("evaluation seeds must be disjoint from development seeds");
  return withScale(scale, () => {
    let tape = null;
    return ARMS.map(arm => attempt({ arm: `${arm}@x${scale}`, seed, split: "eval" }, () => {
      if (arm === "yoked-reward" && !tape) throw new Error("native reward tape unavailable");
      const model = makeModel(seed, arm);
      const before = { train: score(model, arm, "train", repeats, seed),
        heldout: score(model, arm, "heldout", repeats, seed) };
      const t = train(model, arm, "train", seed, budget, { tape });
      if (arm === "native") tape = t.rewards;
      delete t.rewards;
      const after = { train: score(model, arm, "train", repeats, seed),
        heldout: score(model, arm, "heldout", repeats, seed) };
      return { scale, baseArm: arm, before, training: t, after, primary: after.train,
        goalSensitivity: goalSensitivity(model, arm, mix(seed, 401)),
        fanIn: fanInAudit(model.brains[0], layoutOf(arm)),
        modelBytes: modelBytes(model), onlineOracleQueries: 0 };
    }));
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  const option = (name, fallback) => {
    const at = args.indexOf(name);
    return at < 0 ? fallback : args.splice(at, 2)[1];
  };
  const budget = Number(option("--budget", "8000")), repeats = Number(option("--repeats", "12"));
  const devSeeds = option("--dev-seeds", DEV_SEEDS.join(",")).split(",").map(Number);
  const out = option("--out", null);
  const seeds = args.length ? args.map(Number) : [1, 2, 3];
  if (!out || !Number.isSafeInteger(budget) || budget < 1 || !Number.isSafeInteger(repeats) ||
      repeats < 1 || new Set(seeds).size !== seeds.length ||
      seeds.some(s => !Number.isSafeInteger(s) || s < 0 || devSeeds.includes(s)))
    throw new Error("usage: --out FILE [--budget N] [--repeats R] [--dev-seeds a,b] eval-seed ...");
  assertGoalSplits();
  const selection = select({ seeds: devSeeds, budget, repeats });
  const scales = selection.evalScales;
  const runs = [...selection.rows, ...scales.flatMap(s => seeds.flatMap(seed =>
    runSeed(seed, s, { budget, repeats })))];
  writeResult(out, resultRecord({
    experiment: "brain-world/m0c-frozen-step-credit-protocol",
    baseline: `native@x${selection.selected}`, runs,
    config: { arms: ARMS, goals: GOALS, devSeeds, seeds, scaleGrid: SCALES,
      selection: { byScale: selection.byScale, selected: selection.selected,
        rule: "max mean dev success, native arm, dev goals/seeds only; ties -> smaller scale; " +
          "eval at x1 and the selected scale (best other scale if x1 is selected)" },
      evalScales: scales, budget, repeats, layouts: LAYOUTS,
      baseGains: { lrP: GAINS.lrP, lrV: GAINS.lrV } },
    budgets: { trainDecisionsPerArm: budget, policyOracleQueriesPerArm: 0, frozenScoring: true,
      note: "single 5x5 family, item at start; heldout goals untrained but same geometry" },
    // primary = dev score on selection rows, trained-goal score on eval rows.
    metrics: { "primary.success": "higher" },
  }));
  console.log("selected scale", selection.selected, JSON.stringify(selection.byScale));
  for (const s of scales) for (const arm of ARMS) {
    const g = runs.filter(r => r.arm === `${arm}@x${s}` && r.split === "eval");
    const ok = g.filter(r => r.status === "ok");
    console.log(`${arm}@x${s}`.padEnd(22), "ok", ok.length, "/", g.length,
      "train", mean(ok.map(r => r.scores.after.train.success)).toFixed(3),
      "heldout", mean(ok.map(r => r.scores.after.heldout.success)).toFixed(3));
  }
}
