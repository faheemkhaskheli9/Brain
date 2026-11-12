// Matched primitive-decision stateful-carry diagnostic (#112). No learned options and no AGI claim.
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import { Brain, N_IN, rng } from "./brain.js";
import { CarryWorld, LIMIT, generateTasks, legalActions, heuristicAction, feasible, signature } from "./stateful_carry.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

export const ARMS = Object.freeze(["flat-brain", "flat-no-goal", "tabular-q", "random-legal", "fixed-script", "hand-coded-heuristic"]);
const TRAINED = new Set(["flat-brain", "flat-no-goal", "tabular-q"]);
const SCRIPT = [4, 1, 1, 2, 2, 5, 6];
const randPick = (R, allowed) => allowed[Math.floor(R() * allowed.length)];

export function encode(obs, revealGoal = true) {
  const x = new Float32Array(N_IN);
  for (const wall of obs.walls) x[wall] = -1;
  if (obs.wet != null) x[obs.wet] = 0.5;
  x[45] = Number(obs.carrying); x[46] = obs.remaining / LIMIT;
  x[47] = Number(obs.lastEvent === "pickup_failed");
  x[48] = Number(obs.lastEvent.includes("drop"));
  x[49] = (obs.previousMove + 1) / 5;
  x[50 + obs.position] = 1;
  if (obs.object != null) {
    x[50 + obs.object] += 0.5;
    x[82 + obs.object] = 0.25;
  }
  if (revealGoal) x[82 + obs.goal] += 1;
  return x;
}

// Public-observation-only key. No hidden rule, task id, RNG or feasibility bit.
export function stateKey(o, revealGoal = true) {
  return JSON.stringify([o.position, o.object, revealGoal ? o.goal : null, o.walls,
    o.wet, o.carrying, o.previousMove, o.lastEvent, Math.floor(o.remaining / 8)]);
}
export class TabularQ {
  constructor(seed) { this.random = rng(seed); this.values = new Map(); }
  row(key) {
    if (!this.values.has(key)) this.values.set(key, Array(7).fill(0));
    return this.values.get(key);
  }
  act(obs, allowed, learn = false) {
    if (learn && this.random() < 0.2) return randPick(this.random, allowed);
    const row = this.row(stateKey(obs));
    let best = -Infinity, chosen = allowed[0];
    for (const a of allowed) if (row[a] > best) { best = row[a]; chosen = a; }
    return chosen;
  }
  update(obs, action, reward, nextObs, terminal) {
    const q = this.row(stateKey(obs));
    const future = terminal ? 0 : Math.max(...legalActions(nextObs).map(a => this.row(stateKey(nextObs))[a]));
    q[action] += 0.2 * (reward + 0.95 * future - q[action]);
  }
  copy(seed) {
    const q = new TabularQ(seed);
    q.values = new Map([...this.values].map(([k, v]) => [k, [...v]]));
    return q;
  }
}
export function copyBrain(brain, seed) {
  const out = Object.create(Object.getPrototypeOf(brain));
  for (const [key, val] of Object.entries(brain))
    if (key !== "rand") out[key] = typeof val === "function" ? val : structuredClone(val);
  out.rand = rng(seed);
  return out;
}

// Max steps counts actual primitive decisions; the last training episode is censored.
export function episode(task, seed, decide, observeStep = () => {}, cap = LIMIT) {
  if (!Number.isInteger(cap) || cap < 1 || cap > LIMIT) throw Error("invalid episode cap");
  const env = new CarryWorld(task, seed);
  let invalid = 0, forcedDrops = 0, recoveries = 0, pickupFailures = 0, everDropped = false;
  for (let step = 0; step < cap; step++) {
    const obs = env.observe(), allowed = legalActions(obs), action = decide(obs, allowed, step);
    if (!Number.isInteger(action) || action < 0 || action > 6) throw Error("illegal policy output");
    if (!allowed.includes(action)) invalid++;
    const result = env.step(action);
    if (result.event === "forced_drop" || result.event === "interrupted_drop") {
      forcedDrops++; everDropped = true;
    }
    if (result.event === "pickup_failed") pickupFailures++;
    if (result.event === "picked_up" && everDropped) { recoveries++; everDropped = false; }
    const censored = step + 1 === cap && !result.done;
    observeStep(obs, action, result, result.done || censored);
    if (result.done || censored) return { success: result.success, decisions: step + 1,
      censored, invalid, forcedDrops, recoveries, pickupFailures, timeout: !result.success };
  }
  throw Error("episode ended without report");
}

function agent(seed, arm) {
  if (arm === "tabular-q") return new TabularQ(seed);
  if (arm.startsWith("flat-")) return new Brain(rng(seed));
  return null;
}
function learnerEpisode(model, arm, task, envSeed, cap) {
  const isBrain = arm.startsWith("flat-"), goal = arm !== "flat-no-goal";
  if (isBrain) { model.learning = true; model.greedy = false; }
  return episode(task, envSeed,
    (obs, allowed) => isBrain ? model.act(model.encode(encode(obs, goal), 0), allowed)
      : model.act(obs, allowed, true),
    (obs, action, result, terminal) => {
      if (isBrain) model.learn(result.reward, terminal ? null :
        model.encode(encode(result.observation, goal), 0));
      else model.update(obs, action, result.reward, result.observation, terminal);
    }, cap);
}
function score(model, arm, tasks, repeats, seed, greedy = false) {
  const R = rng(seed ^ 0x33aacc), brain = arm.startsWith("flat-") ? copyBrain(model, seed) : null;
  const q = arm === "tabular-q" ? model.copy(seed) : null;
  if (brain) { brain.learning = false; brain.greedy = greedy; }
  let wins = 0, invalid = 0, decisions = 0, forcedDrops = 0, recoveries = 0,
    pickupFailures = 0, timeouts = 0, possible = 0, impossibleWins = 0;
  const audit = [];
  for (let t = 0; t < tasks.length; t++) for (let r = 0; r < repeats; r++) {
    const task = tasks[t], possibleGoal = feasible(task);
    const runSeed = (seed + t * 991 + r * 31) >>> 0;
    const x = episode(task, runSeed, (obs, allowed, step) => {
      if (brain) return brain.act(brain.encode(encode(obs, arm !== "flat-no-goal"), 0), allowed);
      if (q) return q.act(obs, allowed);
      if (arm === "random-legal") return randPick(R, allowed);
      if (arm === "fixed-script") return SCRIPT[step % SCRIPT.length];
      if (arm === "hand-coded-heuristic") return heuristicAction(obs);
      throw Error("unknown arm " + arm);
    });
    wins += Number(x.success); decisions += x.decisions; invalid += x.invalid;
    forcedDrops += x.forcedDrops; recoveries += x.recoveries;
    pickupFailures += x.pickupFailures; timeouts += Number(x.timeout);
    possible += Number(possibleGoal); impossibleWins += Number(!possibleGoal && x.success);
    audit.push({ task: task.id, repeat: r, possible: possibleGoal, ...x });
  }
  const n = tasks.length * repeats;
  return { success: wins / n, feasibleTaskRate: possible / n, invalidActionRate: invalid / decisions,
    forcedDrops, recoveries, pickupFailures, timeouts: timeouts / n, impossibleWins,
    decisions, episodes: n, audit };
}
export function runSeed(seed, { trainSteps = 10000, trainTasks = 40, devTasks = 12, evalTasks = 30,
  repeats = 2 } = {}) {
  if (![seed, trainSteps, trainTasks, devTasks, evalTasks, repeats].every(Number.isInteger) ||
      seed < 0 || Math.min(trainSteps, trainTasks, devTasks, evalTasks, repeats) < 1)
    throw Error("invalid experiment budget");
  const train = generateTasks(seed, "train", trainTasks),
    development = generateTasks(seed, "dev", devTasks),
    evaluation = generateTasks(seed, "eval", evalTasks), rows = [];
  const splitHash = createHash("sha256").update(JSON.stringify({
    train: train.map(signature), dev: development.map(signature), eval: evaluation.map(signature) })).digest("hex");
  for (const arm of ARMS) {
    const began = Date.now();
    try {
      const model = agent(seed * 7919 + 41, arm);
      let trained = 0, episodes = 0, interrupted = 0;
      if (TRAINED.has(arm)) {
        const R = rng(seed * 1741 + 17);
        while (trained < trainSteps) {
          const task = train[Math.floor(R() * train.length)];
          const x = learnerEpisode(model, arm, task, seed * 65537 + episodes,
            Math.min(LIMIT, trainSteps - trained));
          trained += x.decisions; episodes++; interrupted += Number(x.censored);
        }
        if (trained !== trainSteps) throw Error("overshot exact primitive decision budget");
      }
      const old = score(model, arm, train.slice(0, Math.min(evalTasks, train.length)),
        repeats, seed * 101 + 7);
      const dev = score(model, arm, development, repeats, seed * 103 + 17);
      const heldout = score(model, arm, evaluation, repeats, seed * 103 + 11);
      const greedy = arm.startsWith("flat-")
        ? score(model, arm, evaluation, repeats, seed * 103 + 11, true).success : null;
      rows.push(run({ arm, seed, split: "heldout-transition", status: "ok",
        seconds: (Date.now() - began) / 1000,
        scores: { heldout, development: dev, oldSuccess: old.success, greedySuccess: greedy,
          trainDecisions: trained, trainEpisodes: episodes, truncatedTrainEpisodes: interrupted } }));
    } catch (e) {
      rows.push(run({ arm, seed, split: "heldout-transition", status: "error",
        reason: String(e?.message || e), seconds: (Date.now() - began) / 1000, scores: {} }));
    }
  }
  return { rows, splitHash };
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2), opt = (flag, value) => {
    const i = args.indexOf(flag);
    return i < 0 ? value : args.splice(i, 2)[1];
  };
  const trainSteps = Number(opt("--train-steps", "10000"));
  const trainTasks = Number(opt("--train-tasks", "40"));
  const devTasks = Number(opt("--dev-tasks", "12"));
  const evalTasks = Number(opt("--eval-tasks", "30")), repeats = Number(opt("--repeats", "2"));
  const out = opt("--out", null), seeds = args.length ? args.map(Number) : [1, 2, 3];
  if (!seeds.length || seeds.some(s => !Number.isInteger(s) || s < 0) ||
      new Set(seeds).size !== seeds.length) throw Error("bad seeds");
  const groups = seeds.map(seed => runSeed(seed, { trainSteps, trainTasks, devTasks, evalTasks, repeats }));
  const runs = groups.flatMap(x => x.rows);
  if (out) writeResult(out, resultRecord({
    experiment: "brain-world/stateful-carry-diagnostic", baseline: "tabular-q", runs,
    metrics: { "development.success": "higher", "heldout.success": "higher", "heldout.invalidActionRate": "lower",
      "heldout.timeouts": "lower", oldSuccess: "higher", greedySuccess: "higher" },
    config: { seeds, trainTasks, devTasks, evalTasks, repeats, arms: ARMS,
      splitHashes: Object.fromEntries(seeds.map((seed, i) => [seed, groups[i].splitHash])),
      split: "disjoint geometry and held-out transition rules (normal versus turn-drop)",
      provenance: "engineered goal/rewards/primitives; tabular Q and backprop-free flat Brain trained; heuristic is hand-coded; no learned options",
      limitations: "diagnostic protocol: nonlearning arms have 0 training decisions; action masks use public state; hidden rule changes make evaluation deliberately difficult" },
    budgets: { primitiveTrainingDecisionsPerTrainedArm: trainSteps,
      devEpisodesPerArm: devTasks * repeats,
      evalEpisodesPerArm: evalTasks * repeats, episodeDecisionLimit: LIMIT },
  }));
  for (const arm of ARMS) {
    const ok = runs.filter(r => r.arm === arm && r.status === "ok");
    const mean = ok.length ? ok.reduce((a, r) => a + r.scores.heldout.success, 0) / ok.length : NaN;
    console.log(arm.padEnd(20), "success", mean.toFixed(3), "seeds", ok.length);
  }
  if (runs.some(r => r.status !== "ok")) process.exitCode = 1;
}
