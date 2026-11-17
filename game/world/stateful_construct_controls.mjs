// M0c same-environment public-observation baseline audit (#112/#153).
// No privileged oracle, hidden task ID, authored answer, model planning or backprop is used
// by the tabular/heuristic policies. The 5x5 task family is a REGRESSION pilot only.
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import { rng } from "./brain.js";
import { TabularQ } from "./stateful_baselines.mjs";
import { createModel, episode as brainEpisode, scoreTasks as brainScore,
  modelBytes as brainBytes } from "./stateful_options.mjs";
import { ALLOWED, SIDE, START, generate, initial, observe, transition,
  validateTask } from "./stateful_construct.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

export const ARMS = Object.freeze(["flat", "flat-goal-masked", "tabular-absolute",
  "tabular-relative", "uniform-random", "public-maze-heuristic"]);
const TRAINED = new Set(["flat", "flat-goal-masked", "tabular-absolute", "tabular-relative"]);
const pick = (random, options) => options[Math.floor(random() * options.length)];
const mix = (a, b) => (Math.imul(a >>> 0, 1664525) + b + 1013904223) >>> 0;
const digest = value => createHash("sha256").update(JSON.stringify(value)).digest("hex");
const coord = cell => [cell % SIDE, Math.floor(cell / SIDE)];
const inBounds = (x, y) => x >= 0 && y >= 0 && x < SIDE && y < SIDE;
const offsets = [[-1, 0], [1, 0], [0, -1], [0, 1]];
function hot(obs, start, n) {
  let found = -1;
  for (let i = 0; i < n; i++) if (obs[start + i] > 0.5) {
    if (found >= 0) throw new Error("ambiguous public observation one-hot");
    found = i;
  }
  return found;
}

// This key is derived ONLY from the same public Float32 observation that Brain sees.
// The relative arm explicitly adds an engineered spatial inductive bias; it is not
// evidence that the creature acquired that representation on its own.
export function publicStateKey(obs, relative = false) {
  const agent = hot(obs, 0, SIDE * SIDE), item = hot(obs, 25, SIDE * SIDE);
  const goal = hot(obs, 50, SIDE * SIDE), carrying = Number(obs[75] > 0.5);
  if (agent < 0 || goal < 0 || (!carrying && item < 0))
    throw new Error("missing public position, item or goal");
  const localWalls = [76, 77, 78, 79].map(i => Number(obs[i] > 0.5));
  const lastFailure = Number(obs[83] > 0.5);
  if (!relative) return JSON.stringify([agent, item, goal, carrying, localWalls, lastFailure]);
  const [ax, ay] = coord(agent), [tx, ty] = coord(carrying ? goal : item);
  return JSON.stringify([tx - ax, ty - ay, carrying, localWalls, lastFailure]);
}

// Reuse the existing tested TabularQ storage and random tie-breaking RNG, with
// six actions instead of the other simulator's seven. No hidden map lookup.
export class PublicTabular {
  constructor(seed, relative = false) {
    this.table = new TabularQ(seed, ALLOWED.length);
    this.relative = relative;
  }
  act(obs, learn = false) {
    const row = this.table.row(publicStateKey(obs, this.relative));
    const R = this.table.random;
    if (learn && R() < 0.2) return pick(R, ALLOWED);
    const highest = Math.max(...ALLOWED.map(a => row[a]));
    const ties = ALLOWED.filter(a => Math.abs(row[a] - highest) < 1e-9);
    return pick(R, ties);
  }
  update(obs, action, reward, after, terminal) {
    const values = this.table.row(publicStateKey(obs, this.relative));
    const future = terminal ? 0 :
      Math.max(...ALLOWED.map(a => this.table.row(publicStateKey(after, this.relative))[a]));
    values[action] += 0.2 * (reward + 0.95 * future - values[action]);
  }
  clone(seed) {
    const copy = new PublicTabular(seed, this.relative);
    copy.table = this.table.copy(seed);
    return copy;
  }
  get states() { return this.table.values.size; }
  get bytesEstimate() {
    // Lower-bound packed payload; does not claim JS Map/array runtime overhead.
    return [...this.table.values].reduce((sum, [key, row]) =>
      sum + Buffer.byteLength(key) + row.length * 8, 0);
  }
}

export class PublicMazeHeuristic {
  constructor() { this.discoveredWalls = new Set(); }
  act(obs) {
    const here = hot(obs, 0, SIDE * SIDE), item = hot(obs, 25, SIDE * SIDE);
    const goal = hot(obs, 50, SIDE * SIDE), carrying = obs[75] > 0.5;
    if (here < 0 || goal < 0 || (!carrying && item < 0))
      throw new Error("incomplete public scene");
    if (!carrying && here === item) return 4;
    if (carrying && here === goal) return 5;
    const [cx, cy] = coord(here);
    for (let a = 0; a < 4; a++) {
      const [dx, dy] = offsets[a], x = cx + dx, y = cy + dy;
      if (inBounds(x, y) && obs[76 + a] > 0.5) this.discoveredWalls.add(y * SIDE + x);
    }
    // Optimistic BFS over sensed walls ONLY. Unobserved cells are treated as
    // potentially open until approached: no access to task.walls or oracle().
    const target = carrying ? goal : item;
    const seen = new Set([here]), queue = [{ cell: here, first: -1 }];
    for (let p = 0; p < queue.length; p++) {
      const { cell, first } = queue[p];
      if (cell === target) return first;
      const [x, y] = coord(cell);
      for (let a = 0; a < 4; a++) {
        const [dx, dy] = offsets[a], nx = x + dx, ny = y + dy, next = ny * SIDE + nx;
        if (!inBounds(nx, ny) || seen.has(next) || this.discoveredWalls.has(next)) continue;
        seen.add(next); queue.push({ cell: next, first: first < 0 ? a : first });
      }
    }
    // An unreachable target is not a free learned solution.
    return [0, 1, 2, 3].find(a => obs[76 + a] < 0.5) ?? 0;
  }
}

export function structureKey(task) {
  validateTask(task);
  const walls = task.walls.map(([x, y]) => y * SIDE + x).sort((a, b) => a - b);
  return JSON.stringify([START, task.item, task.goal, walls, task.maxSteps, "legacy-dynamics-v1"]);
}

export function buildManifest(train, dev, heldout) {
  const parts = { train, dev, heldout }, indexed = {}, hashes = {}, counts = {};
  for (const [split, tasks] of Object.entries(parts)) {
    const identities = tasks.map(structureKey), unique = new Set(identities);
    indexed[split] = unique;
    hashes[split] = digest(identities);
    counts[split] = { tasks: tasks.length, uniqueStructures: unique.size,
      duplicates: tasks.length - unique.size };
  }
  for (const [x, left] of Object.entries(indexed))
    for (const [y, right] of Object.entries(indexed))
      if (x < y && [...left].some(f => right.has(f)))
        throw new Error("structural overlap across " + x + "/" + y);
  return { hashes, counts, generator: "legacy fixed START, corners, four wall maps",
    fingerprint: "start+item+goal+sorted-walls+horizon+dynamics; no ID/seed" };
}

function evaluationSeed(seed, task, repeat) {
  let s = mix(seed, repeat);
  // Task ID is deliberately excluded; the physical task structure sets RNG stream.
  for (const char of structureKey(task)) s = Math.imul(s ^ char.charCodeAt(0), 16777619) >>> 0;
  return s;
}

// Every policy gets precisely the same six primitive actions, transition,
// public observation and reward. Wrong/blocked actions are legal attempts that
// consume one policy decision AND one physical environment transition.
export function rollout(task, policy, { learn = false, cap = task.maxSteps } = {}) {
  if (!Number.isSafeInteger(cap) || cap < 1 || cap > task.maxSteps)
    throw new Error("invalid exact episode cap");
  let state = initial(task), decisions = 0, rewardSum = 0, success = false, reason = "capped";
  for (let i = 0; i < cap; i++) {
    const obs = observe(task, state), action = policy.act(obs, learn);
    if (!ALLOWED.includes(action)) throw new Error("policy attempted action outside shared set");
    const result = transition(task, state, action);
    decisions++; rewardSum += result.reward; state = result.state; reason = result.reason;
    if (learn && policy.update)
      policy.update(obs, action, result.reward,
        result.done ? null : observe(task, result.state), result.done);
    if (result.done) { success = result.success; break; }
  }
  return { success, decisions, envSteps: decisions, invalid: state.invalid,
    rewardSum, reason: !state.done && cap < task.maxSteps ? "budget-censored" : reason,
    truncated: !state.done && cap < task.maxSteps };
}

function scorePublic(model, arm, tasks, repeats, seed) {
  let successes = 0, invalid = 0, decisions = 0, rewardSum = 0, censored = 0;
  for (const task of tasks) for (let i = 0; i < repeats; i++) {
    const s = evaluationSeed(seed, task, i);
    // The random arm's RNG is seeded independently for each evaluation task.
    const R = rng(s);
    const policy = arm.startsWith("tabular") ? model.clone(s) :
      arm === "uniform-random" ? { act: () => pick(R, ALLOWED) } :
        new PublicMazeHeuristic();
    const outcome = rollout(task, policy);
    successes += Number(outcome.success);
    invalid += outcome.invalid;
    decisions += outcome.decisions;
    rewardSum += outcome.rewardSum;
    censored += Number(outcome.truncated);
  }
  const episodes = tasks.length * repeats;
  return { success: successes / episodes, failed: episodes - successes,
    invalidPerEpisode: invalid / episodes, decisions, envSteps: decisions,
    exits: 0, episodes, rewardPerEpisode: rewardSum / episodes, censored };
}

function trainedArm(arm) { return TRAINED.has(arm); }
export function runSeed(seed, options = {}) {
  const { trainSteps = 10000, trainTasks = 32, devTasks = 16, evalTasks = 16,
    repeats = 2 } = options;
  if (![seed, trainSteps, trainTasks, devTasks, evalTasks, repeats]
    .every(Number.isSafeInteger) || seed < 0 ||
      Math.min(trainSteps, trainTasks, devTasks, evalTasks, repeats) < 1)
    throw new Error("invalid control budgets/seed");
  const train = generate(seed, "train", trainTasks);
  const dev = generate(seed, "dev", devTasks);
  const heldout = generate(seed, "eval", evalTasks);
  const manifest = buildManifest(train, dev, heldout);
  const rows = [];
  for (const arm of ARMS) {
    const start = Date.now();
    try {
      const isBrain = arm === "flat" || arm === "flat-goal-masked";
      const model = isBrain ? createModel(mix(seed, 31), arm) :
        arm.startsWith("tabular") ?
          new PublicTabular(mix(seed, 31), arm === "tabular-relative") : null;
      const chooseTask = rng(mix(seed, 617));
      let trainDecisions = 0, trainEnvSteps = 0, trainEpisodes = 0, truncatedTrain = 0;
      if (trainedArm(arm)) while (trainDecisions < trainSteps) {
        const task = train[Math.floor(chooseTask() * train.length)];
        const remaining = trainSteps - trainDecisions;
        const trial = isBrain ? brainEpisode(model, task, { learn: true,
          seed: mix(seed, trainEpisodes + 1588), maxDecisions: remaining }) :
          rollout(task, model, { learn: true, cap: Math.min(task.maxSteps, remaining) });
        if (trial.decisions < 1 || trial.decisions > remaining)
          throw new Error("training budget overshot/stalled");
        trainDecisions += trial.decisions;
        trainEnvSteps += trial.envSteps;
        truncatedTrain += Number(trial.truncated);
        trainEpisodes++;
      }
      if (trainedArm(arm) && trainDecisions !== trainSteps)
        throw new Error("exact training budget violated");
      const score = (tasks, salt) => isBrain ?
        brainScore(model, tasks, repeats, mix(seed, salt)) :
        scorePublic(model, arm, tasks, repeats, mix(seed, salt));
      const source = score(train.slice(0, Math.min(train.length, evalTasks)), 101);
      const development = score(dev, 103);
      const evaluation = score(heldout, 107);
      const bytes = isBrain ? brainBytes(model) :
        model?.bytesEstimate ?? 0;
      rows.push(run({ arm, seed, split: "legacy-goal-pair-holdout", status: "ok",
        seconds: (Date.now() - start) / 1000,
        scores: { source, development, heldout: evaluation, trainDecisions,
          trainEnvSteps, trainEpisodes, truncatedTrain, modelBytesEstimate: bytes,
          tableStates: model?.states ?? 0, oracleQueries: 0 } }));
    } catch (e) {
      rows.push(run({ arm, seed, split: "legacy-goal-pair-holdout", status: "error",
        reason: String(e?.message || e), seconds: (Date.now() - start) / 1000, scores: {} }));
    }
  }
  return { rows, manifest };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const argv = process.argv.slice(2);
  const option = (name, fallback) => {
    const i = argv.indexOf(name); return i < 0 ? fallback : argv.splice(i, 2)[1];
  };
  const trainSteps = Number(option("--train-steps", "10000"));
  const trainTasks = Number(option("--train-tasks", "32"));
  const devTasks = Number(option("--dev-tasks", "16"));
  const evalTasks = Number(option("--eval-tasks", "16"));
  const repeats = Number(option("--repeats", "2"));
  const out = option("--out", null);
  const seeds = argv.length ? argv.map(Number) : [1, 2, 3];
  if (!out || !seeds.length || new Set(seeds).size !== seeds.length ||
      seeds.some(s => !Number.isSafeInteger(s) || s < 0))
    throw new Error("usage: node game/world/stateful_construct_controls.mjs --out RESULT.json [--train-steps N] [seed ...]");
  const cfg = { trainSteps, trainTasks, devTasks, evalTasks, repeats };
  const groups = seeds.map(seed => {
    try { return runSeed(seed, cfg); }
    catch (e) {
      return { manifest: null, rows: ARMS.map(arm => run({ arm, seed,
        split: "legacy-goal-pair-holdout", status: "error",
        reason: String(e?.message || e), scores: {} })) };
    }
  });
  const runs = groups.flatMap(g => g.rows);
  writeResult(out, resultRecord({
    experiment: "brain-world/stateful-construct-m0c-controls",
    baseline: "tabular-relative", runs,
    budgets: { exactPrimitiveDecisionsPerTrainedArm: trainSteps, oracleQueriesPerArm: 0,
      physicalTransitionsCharged: true, evaluationEpisodesPerSplit: evalTasks * repeats },
    metrics: { "heldout.success": "higher", "development.success": "higher",
      "source.success": "higher", "heldout.invalidPerEpisode": "lower",
      trainDecisions: "lower", modelBytesEstimate: "lower" },
    config: { ...cfg, seeds, arms: ARMS,
      manifests: Object.fromEntries(seeds.map((seed, i) => [seed, groups[i].manifest])),
      provenance: "all controls share stateful_construct.observe/transition and six public actions; heuristic uses only locally discovered walls; relative tabular has authored coordinate inductive bias; flat uses existing backprop-free Brain; no oracle during any learning/evaluation",
      limitations: "Legacy authored goal-pair and four-template geometry pilot; no novel structural families, no sealed transfer claim, no independently tuned stronger gradient RL, no AGI result" },
  }));
  for (const arm of ARMS) {
    const group = runs.filter(x => x.arm === arm && x.status === "ok");
    const mean = group.length ? group.reduce((s, x) => s + x.scores.heldout.success, 0) / group.length : NaN;
    console.log(arm.padEnd(22), "heldout success", mean.toFixed(3), "seeds", group.length);
  }
  if (runs.some(x => x.status !== "ok")) process.exitCode = 1;
}
