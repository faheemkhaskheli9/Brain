// Stateful, observable construction task (#110/#112), separate from Brain World's curriculum.
// Engineered world, actions, splits and verifier; no model, teacher, or learned solution here.
// An object must be found, picked up, transported around obstacles and dropped at the goal.
// Every primitive changes the next observation; invalid actions are recoverable.
// Goal-family pairs (not just input permutations) are disjoint across train/dev/eval.
import { N_IN, rng } from "./brain.js";

export const SIDE = 5, START = Object.freeze([2, 0]);
export const ACTIONS = Object.freeze(["west", "east", "north", "south", "pickup", "drop"]);
export const ALLOWED = Object.freeze(ACTIONS.map((_, i) => i));
export const CORNERS = Object.freeze([[0, 0], [4, 0], [0, 4], [4, 4]]);
export const FAMILIES = Object.freeze({
  train: [[0, 1], [1, 2], [2, 3], [3, 0]],
  dev: [[0, 2], [2, 0], [1, 3], [3, 1]],
  eval: [[0, 3], [3, 2], [2, 1], [1, 0]],
});
export const OBSTACLES = Object.freeze([
  [[2, 2]], [[1, 2], [3, 2]], [[2, 1], [2, 3]], [[1, 1], [3, 1], [2, 2]],
]);
const key = p => p.join(",");
const cell = p => p[1] * SIDE + p[0];
const at = (a, b) => a[0] === b[0] && a[1] === b[1];
const inside = p => p[0] >= 0 && p[0] < SIDE && p[1] >= 0 && p[1] < SIDE;
const offsets = [[-1, 0], [1, 0], [0, -1], [0, 1]];
const move = (p, a) => [p[0] + offsets[a][0], p[1] + offsets[a][1]];

export function assertSplits() {
  const keys = Object.values(FAMILIES).flat().map(pair => pair.join(">"));
  if (keys.length !== 12 || new Set(keys).size !== keys.length)
    throw new Error("overlapping stateful goal pairs");
  for (const pair of Object.values(FAMILIES).flat())
    if (pair[0] === pair[1] || pair.some(n => !Number.isInteger(n) || n < 0 || n >= CORNERS.length))
      throw new Error("invalid family");
}
export const pairKey = task => key(task.item) + ">" + key(task.goal);
export function generate(seed, split, n = 24) {
  assertSplits();
  if (!Number.isInteger(seed) || seed < 0 || !Number.isInteger(n) || n < 1 || !FAMILIES[split])
    throw new Error("invalid task generation request");
  const R = rng(seed * 7927 + { train: 1, dev: 2, eval: 3 }[split]);
  const pairs = FAMILIES[split], tasks = [];
  for (let i = 0; i < n; i++) {
    const [src, dest] = pairs[Math.floor(R() * pairs.length)];
    const walls = OBSTACLES[Math.floor(R() * OBSTACLES.length)];
    tasks.push({ id: `${split}-${seed}-${i}`, item: [...CORNERS[src]],
      goal: [...CORNERS[dest]], walls: walls.map(p => [...p]), maxSteps: 40 });
  }
  return tasks;
}
export function validateTask(task) {
  if (!task || !Array.isArray(task.item) || !Array.isArray(task.goal) ||
      !Array.isArray(task.walls) || !Number.isInteger(task.maxSteps) || task.maxSteps < 1)
    throw new Error("invalid task");
  const all = [task.item, task.goal, ...task.walls];
  if (all.some(p => !Array.isArray(p) || p.length !== 2 ||
      p.some(n => !Number.isInteger(n)) || !inside(p)))
    throw new Error("invalid grid coordinate");
  if (new Set(task.walls.map(key)).size !== task.walls.length ||
      task.walls.some(p => at(p, START)))
    throw new Error("invalid wall placement");
}
export function initial(task) {
  validateTask(task);
  return { agent: [...START], item: [...task.item], carrying: false,
    steps: 0, done: false, invalid: 0, lastFailure: false };
}
const blocked = (task, p) => !inside(p) || task.walls.some(w => at(w, p));
// No hidden task ID, transition rule, oracle path or answer enters the observation.
// Three 5x5 maps: agent, visible item, goal; local collision/handling sensors.
export function observe(task, state) {
  const x = new Float32Array(N_IN);
  x[cell(state.agent)] = 1;
  if (!state.carrying) x[25 + cell(state.item)] = 1;
  x[50 + cell(task.goal)] = 1;
  x[75] = state.carrying ? 1 : 0;
  for (let a = 0; a < 4; a++) x[76 + a] = blocked(task, move(state.agent, a)) ? 1 : 0;
  x[80] = !state.carrying && at(state.agent, state.item) ? 1 : 0;
  x[81] = at(state.agent, task.goal) ? 1 : 0;
  x[82] = state.steps / task.maxSteps;
  x[83] = state.lastFailure ? 1 : 0;
  return x;
}
export function transition(task, state, action) {
  if (state.done || !ALLOWED.includes(action)) throw new Error("invalid stateful action");
  const next = { ...state, agent: [...state.agent], item: [...state.item],
    steps: state.steps + 1, lastFailure: false };
  let reward = -0.01, reason = "step", success = false, invalid = false;
  if (action < 4) {
    const target = move(next.agent, action);
    if (blocked(task, target)) { invalid = true; reason = "blocked"; reward = -0.08; }
    else next.agent = target;
  } else if (action === 4) {
    if (!next.carrying && at(next.agent, next.item)) {
      next.carrying = true; reward = 0.15; reason = "picked-up";
    } else { invalid = true; reason = "failed-pickup"; reward = -0.12; }
  } else if (!next.carrying) {
    invalid = true; reason = "empty-drop"; reward = -0.12;
  } else if (at(next.agent, task.goal)) {
    next.carrying = false; next.item = [...next.agent];
    reward = 1; success = true; next.done = true; reason = "delivered";
  } else {
    next.carrying = false; next.item = [...next.agent];
    invalid = true; reward = -0.2; reason = "misplaced";
  }
  if (invalid) { next.invalid++; next.lastFailure = true; }
  if (!next.done && next.steps >= task.maxSteps) {
    next.done = true; reward -= 0.2; reason = "timeout";
  }
  return { state: next, reward, success, done: next.done, invalid, reason };
}

// Engineered breadth-first oracle for feasibility checks / an explicitly labelled ceiling.
// Never call from a learned policy or construct observations from its answer.
export function oracle(task) {
  const first = initial(task), queue = [{ state: first, path: [] }], seen = new Set();
  for (let p = 0; p < queue.length; p++) {
    const { state, path } = queue[p];
    const id = [key(state.agent), key(state.item), Number(state.carrying)].join("|");
    if (seen.has(id)) continue;
    seen.add(id);
    for (const action of ALLOWED) {
      const result = transition(task, state, action);
      if (result.success) return [...path, action];
      if (!result.done) queue.push({ state: result.state, path: [...path, action] });
    }
  }
  return null;
}
