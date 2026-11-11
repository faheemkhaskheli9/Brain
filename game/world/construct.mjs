// Compositional construction tasks (issue #110): draw with the pen strokes under constraints
// instead of copying one letter. Deterministic generation, explicit validators, held-out
// constraint combinations. This file is the task suite only: no creature is trained here.
//
// A drawing is a set of pen strokes (indices into PEN). A task asks for a drawing that
//   covers   every listed pad cell,
//   symmetry is unchanged under an axis ("lr" mirror, "ud" flip, "rot" 180 degrees; null: none),
//   budget   uses at most `budget` strokes (and at least one, with no repeats).
// Kinds: connect (covers + budget), symmetry (symmetry + budget), combine (all three).
// Many drawings satisfy one task; solutions() lists them all and distinct() asks for several.
//
import { PEN, glyph } from "./brain.js";

// Who supplies what (kept apart so results can be labelled):
export const PROVENANCE = {
  primitives: "supplied: the six pen strokes and the 5x5 pad (brain.js PEN, glyph)",
  generator: "engineered: seeded, uses the constraint grammar above",
  validator: "engineered: checks cells, symmetry, budget and degenerate drawings",
  solver: "engineered oracle: enumerates solutions for ground truth; never shown to the creature",
  learned: "nothing here: a creature that scores on these tasks has to learn the composition itself",
};
export const AXES = [null, "lr", "ud", "rot"];
const MAP = {
  lr: (r, c) => [r, 4 - c],
  ud: (r, c) => [4 - r, c],
  rot: (r, c) => [4 - r, 4 - c],
};
const cellsOf = strokes => {
  const g = glyph(strokes), out = new Set();
  for (let i = 0; i < 25; i++) if (g[i]) out.add(i);
  return out;
};
const key = (r, c) => r * 5 + c;

// Held-out combinations: a split is a set of "kind:axis:budget" keys, disjoint by construction.
// train teaches covers and single-axis symmetry; eval pairs them in ways never seen:
//   rot symmetry at all, and covers+symmetry (combine) at the budgets and axes listed.
export const SPLITS = {
  train: ["connect:null:2", "connect:null:3", "symmetry:lr:2", "symmetry:ud:2", "symmetry:lr:3", "combine:lr:2"],
  eval: ["symmetry:rot:2", "symmetry:rot:3", "combine:ud:3", "combine:rot:3", "connect:null:4"],
};
export const comboKey = t => `${t.kind}:${t.axis}:${t.budget}`;
export function assertDisjoint() {
  const all = Object.values(SPLITS).flat();
  if (new Set(all).size !== all.length) throw new Error("construction splits overlap");
  for (const [name, keys] of Object.entries(SPLITS)) if (!keys.length) throw new Error(`split ${name} is empty`);
}

// Why a drawing is not valid for a task, or null when it is.
export function violation(task, strokes) {
  if (!Array.isArray(strokes)) return "not a list of strokes";
  if (strokes.some(s => !Number.isInteger(s) || s < 0 || s >= PEN.length)) return "unknown stroke";
  if (strokes.length === 0) return "empty drawing";
  if (new Set(strokes).size !== strokes.length) return "repeated stroke";
  if (strokes.length > task.budget) return "over the stroke budget";
  const cells = cellsOf(strokes);
  for (const [r, c] of task.points) if (!cells.has(key(r, c))) return `misses cell ${r},${c}`;
  if (task.axis) {
    for (const i of cells) {
      const [r, c] = MAP[task.axis](Math.floor(i / 5), i % 5);
      if (!cells.has(key(r, c))) return `not ${task.axis}-symmetric`;
    }
  }
  return null;
}
export const valid = (task, strokes) => violation(task, strokes) === null;

// Every valid drawing (stroke sets, ascending), by enumeration of the 2^6 - 1 non-empty sets.
export function solutions(task) {
  const out = [];
  for (let m = 1; m < 1 << PEN.length; m++) {
    const s = PEN.map((_, i) => i).filter(i => m >> i & 1);
    if (valid(task, s)) out.push(s);
  }
  return out;
}
export const feasible = task => solutions(task).length > 0;

// `n` distinct valid drawings (as sets: order and repeats do not make a drawing new), or false.
export function distinct(task, drawings, n = 2) {
  const seen = new Set();
  for (const d of drawings) {
    if (!valid(task, d)) return false;
    seen.add([...d].sort((a, b) => a - b).join());
  }
  return seen.size >= n;
}

// mulberry32: the generator's only randomness, so a (seed, split) always gives the same tasks.
function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

// `n` feasible tasks of `split` ("train" | "eval"), seeded. Points are cells of a hidden valid
// drawing, so every task is solvable by construction; ones that turn out to have no solution
// (a budget that is too small) are dropped, never repaired, and counted in `tried`.
export function generate(seed, split, n) {
  assertDisjoint();
  const rand = rng(seed * 7919 + (split === "eval" ? 1 : 0)), keys = SPLITS[split], tasks = [];
  let tried = 0;
  while (tasks.length < n && tried < n * 200) {
    tried++;
    const [kind, axisName, b] = keys[Math.floor(rand() * keys.length)].split(":");
    const axis = axisName === "null" ? null : axisName, budget = Number(b);
    let points = [];
    if (kind !== "symmetry") {
      const k = 1 + Math.floor(rand() * 3), pool = [...Array(25).keys()];
      for (let j = 0; j < k; j++) points.push(pool.splice(Math.floor(rand() * pool.length), 1)[0]);
      points = points.sort((x, y) => x - y).map(i => [Math.floor(i / 5), i % 5]);
    }
    const task = { id: `${split}-${seed}-${tasks.length}`, kind, axis, budget, points };
    if (feasible(task)) tasks.push(task);
  }
  return { tasks, tried };
}

// Transformation: a vertical flip permutes the six strokes (top<->bottom, / <-> \\, the rest stay),
// so a task, a drawing and its answer can all be flipped and validity must not change.
export const FLIP_UD = [1, 0, 2, 3, 5, 4];
export const flipTask = task => ({ ...task, points: task.points.map(([r, c]) => [4 - r, c]) });   // lr, ud, rot are all closed under it
export const flipDrawing = strokes => strokes.map(s => FLIP_UD[s]);
