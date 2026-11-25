// Exploratory M0c transfer fixtures. This module owns task generation and evaluation;
// policies only receive the public observation and a goal-independent episode seed.
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import { rng } from "./brain.js";
import { ALLOWED, SIDE, initial, observe, oracle, transition } from "./stateful_construct.mjs";
import { buildManifest, PublicMazeHeuristic } from "./stateful_construct_controls.mjs";
import { drawStructuralCandidate, physicalFingerprint } from "./stateful_structural.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

const AREA = SIDE * SIDE, GOAL = 2 * AREA, AT_GOAL = 81;
const GRID = Array.from({ length: AREA }, (_, i) => [i % SIDE, Math.floor(i / SIDE)]);
const cell = ([x, y]) => y * SIDE + x;
const DIRECTIONS = [[-1, 0], [1, 0], [0, -1], [0, 1]];
const SPLITS = Object.freeze({ train: "open", dev: "open", scattered: "scattered", barrier: "barrier" });
const mix = (seed, salt) => (Math.imul(seed, 1664525) + salt + 1013904223) >>> 0;
const pick = (R, list) => list[Math.floor(R() * list.length)];
const layoutKey = ({ start, item, walls }) =>
  JSON.stringify([cell(start), cell(item), walls.map(cell).sort((a, b) => a - b)]);
const digest = value => createHash("sha256").update(value).digest("hex");

// Keep the original simulator's reward and timeout semantics. The first drop
// while carrying is terminal even when the original transition says "timeout".
export function oneDrop(task, state, action) {
  const result = transition(task, state, action);
  if (action !== 5 || !state.carrying || result.done) return result;
  return { ...result, done: true, state: { ...result.state, done: true } };
}

// BFS over the offline map. For each cell retain ALL first directions along
// shortest routes, so ties cannot accidentally make two goals look exclusive.
function shortestFromItem({ item, walls }) {
  const blocked = new Set(walls.map(cell)), origin = cell(item);
  const paths = new Map([[origin, { distance: 0, first: 0 }]]), queue = [origin];
  for (const id of queue) {
    const [x, y] = GRID[id], route = paths.get(id);
    DIRECTIONS.forEach(([dx, dy], action) => {
      const nx = x + dx, ny = y + dy, next = cell([nx, ny]);
      if (nx < 0 || nx >= SIDE || ny < 0 || ny >= SIDE || blocked.has(next)) return;
      const distance = route.distance + 1, first = route.distance ? route.first : 1 << action;
      if (!paths.has(next)) {
        paths.set(next, { distance, first });
        queue.push(next);
      } else if (paths.get(next).distance === distance) {
        paths.get(next).first |= first;
      }
    });
  }
  return paths;
}

function pairedTasks(layout, R) {
  const paths = shortestFromItem(layout), start = paths.get(cell(layout.start));
  if (!start?.distance) return null;
  const choices = [];
  // Keep the structural generator's sampled goal, including the opposite-side
  // goal on barrier layouts. Pair it with a different equally distant goal.
  const targets = layout.goal ? [cell(layout.goal)] : GRID.map(cell);
  for (const a of targets) {
    const left = paths.get(a);
    if (!left || left.distance < 2 || a === cell(layout.start)) continue;
    for (const [b, right] of paths) {
      if ((!layout.goal && b <= a) || b === cell(layout.start) ||
          right.distance !== left.distance || (left.first & right.first)) continue;
      choices.push([a, b]);
    }
  }
  if (!choices.length) return null;
  const ids = pick(R, choices);
  if (R() < 0.5) ids.reverse();
  const maxSteps = start.distance + paths.get(ids[0]).distance + 2;
  return ids.map((id, i) => ({ ...layout, id: layout.id + "-" + i, goal: [...GRID[id]], maxSteps }));
}

export function buildGoalPairSuite(seed, count = 6) {
  if (!Number.isSafeInteger(seed) || seed < 0 || !Number.isSafeInteger(count) || count < 1)
    throw new Error("invalid goal-pair seed or group count");
  const seen = new Set(), splits = {}, generation = {};
  for (const [index, [split, family]] of Object.entries(SPLITS).entries()) {
    const R = rng(mix(seed, 6007 + index * 977)), groups = [];
    const audit = { candidates: 0, oracleQueries: 0 };
    while (groups.length < count) {
      if (++audit.candidates > count * 500) throw new Error("goal-pair generator exhausted " + split);
      const id = split + "-" + seed + "-" + groups.length;
      const layout = family === "open" ?
        { id, start: [...pick(R, GRID)], item: [...pick(R, GRID)], walls: [] } :
        drawStructuralCandidate(R, family, "eval", seed, groups.length);
      if (!layout) continue;
      const key = layoutKey(layout);
      if (seen.has(key)) continue;
      // Layout membership is global across seeds. Restrict scattered walls to
      // fewer than a divider so the two held-out topology classes cannot overlap.
      if (family === "open" && (parseInt(digest(key)[0], 16) < 8) !== (split === "train")) continue;
      if (family === "scattered" && layout.walls.length >= SIDE - 1) continue;
      const tasks = pairedTasks(layout, R);
      if (!tasks) continue;
      for (const task of tasks) {
        audit.oracleQueries++;
        if (oracle(task)?.length !== task.maxSteps)
          throw new Error("goal-pair shortest path disagrees with simulator");
      }
      seen.add(key);
      groups.push(tasks);
    }
    splits[split] = groups;
    generation[split] = audit;
  }
  const manifest = buildManifest(splits.train.flat(), splits.dev.flat(),
    [...splits.scattered.flat(), ...splits.barrier.flat()]);
  const familyHashes = Object.fromEntries(Object.entries(splits).map(([split, groups]) =>
    [split, digest(JSON.stringify(groups.map(pair => pair.map(physicalFingerprint))))]));
  return { splits, manifest: { hashes: manifest.hashes, counts: manifest.counts, familyHashes, generation } };
}

function activeCell(obs, offset) {
  const id = obs.subarray(offset, offset + AREA).indexOf(1);
  if (id < 0) throw new Error("missing public position for relative goal");
  return GRID[id];
}

export function goalObservation(obs, mode) {
  if (mode === "absolute") return obs;
  const x = obs.slice();
  x.fill(0, GOAL, GOAL + AREA);
  if (mode === "blind") {
    x[AT_GOAL] = 0;
  } else if (mode === "relative") {
    // One signed one-hot per axis in the original goal block. Preserve the
    // agent, item, local collision and handling inputs for a one-factor comparison.
    const [ax, ay] = activeCell(obs, 0), [gx, gy] = activeCell(obs, GOAL);
    x[GOAL + gx - ax + SIDE - 1] = 1;
    x[GOAL + 2 * SIDE - 1 + gy - ay + SIDE - 1] = 1;
  } else {
    throw new Error("unknown goal observation mode");
  }
  return x;
}

// One policy per episode, seeded identically within the counterfactual pair.
// Observation is the only episode input. No rewards or IDs are given to the policy.
export function scoreGoalPairs(groups, makePolicy, { mode = "absolute", seed, repeats }) {
  if (!groups.length || !Number.isSafeInteger(seed) || seed < 0 ||
      !Number.isSafeInteger(repeats) || repeats < 1) throw new Error("invalid goal-pair scoring request");
  let deliveries = 0, episodes = 0, decisions = 0, maxGoalsPerRepeat = 0;
  for (const [i, tasks] of groups.entries()) {
    if (tasks.length !== 2 || layoutKey(tasks[0]) !== layoutKey(tasks[1]) ||
        tasks[0].maxSteps !== tasks[1].maxSteps || cell(tasks[0].goal) === cell(tasks[1].goal))
      throw new Error("invalid counterfactual goal pair");
    for (let repeat = 0; repeat < repeats; repeat++) {
      const evaluationSeed = mix(mix(seed, i), repeat);
      let wins = 0, blindActions;
      for (const task of tasks) {
        const policy = makePolicy(evaluationSeed);
        const actions = [];
        let state = initial(task);
        while (!state.done) {
          const action = policy.act(goalObservation(observe(task, state), mode));
          const result = oneDrop(task, state, action);
          actions.push(action);
          wins += Number(result.success);
          state = result.state;
        }
        if (mode === "blind") {
          if (blindActions && blindActions.join(",") !== actions.join(","))
            throw new Error("goal-blind trajectories differ within paired episode");
          blindActions = actions;
        }
        decisions += actions.length;
        episodes++;
      }
      if (mode === "blind" && wins > 1) throw new Error("goal-blind ceiling violated");
      deliveries += wins;
      maxGoalsPerRepeat = Math.max(maxGoalsPerRepeat, wins);
    }
  }
  return { success: deliveries / episodes, deliveries, episodes, decisions,
    maxGoalsPerRepeat, goalBlindCeiling: 0.5 };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [output, ...values] = process.argv.slice(2);
  const seeds = values.map(Number), count = 6, repeats = 3;
  if (!output || !seeds.length || new Set(seeds).size !== seeds.length ||
      seeds.some(seed => !Number.isSafeInteger(seed) || seed < 0))
    throw new Error("usage: node game/world/stateful_goal_pairs.mjs OUTPUT SEED [SEED ...]");
  const manifests = {}, runs = [];
  const policies = {
    "public-maze-heuristic": ["absolute", () => new PublicMazeHeuristic()],
    "goal-blind-random": ["blind", seed => {
      const R = rng(seed);
      return { act: () => pick(R, ALLOWED) };
    }],
  };
  for (const seed of seeds) {
    let suite, generationError;
    try {
      suite = buildGoalPairSuite(seed, count);
      manifests[seed] = suite.manifest;
    } catch (error) {
      generationError = error;
    }
    for (const split of Object.keys(SPLITS)) {
      for (const [arm, [mode, factory]] of Object.entries(policies)) {
        const start = performance.now();
        try {
          if (generationError) throw generationError;
          const scores = scoreGoalPairs(suite.splits[split], factory, { mode, seed, repeats });
          runs.push(run({ arm, seed, split, status: "ok", scores,
            seconds: (performance.now() - start) / 1000 }));
        } catch (error) {
          runs.push(run({ arm, seed, split, status: "error", reason: String(error),
            seconds: (performance.now() - start) / 1000 }));
        }
      }
    }
  }
  writeResult(output, resultRecord({
    experiment: "brain-world/m0c-goal-pair-fixture-audit",
    config: { seeds, count, repeats, families: SPLITS, manifests, dynamics: "one-drop-v1" },
    budgets: { trainDecisionsPerArm: 0, onlineOracleQueries: 0, repeats },
    baseline: "goal-blind-random", metrics: { success: "higher" }, runs,
  }));
  if (runs.some(row => row.status !== "ok")) process.exitCode = 1;
}
