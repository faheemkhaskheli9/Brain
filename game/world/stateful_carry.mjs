// Research-only dependent-action environment. Learners see observations, not simulator rules.
import { rng } from "./brain.js";
export const SIZE = 5, LIMIT = 48;
export const ACTIONS = Object.freeze(["north", "east", "south", "west", "pickup", "drop", "wait"]);
const DIRECTIONS = [[0, -1], [1, 0], [0, 1], [-1, 0]];
export const RULES = Object.freeze({ train: "normal", dev: "wet-drop", eval: "turn-drop" });
const cell = (x, y) => y * SIZE + x;
const xy = c => [c % SIZE, Math.floor(c / SIZE)];
const choose = (R, xs) => xs[Math.floor(R() * xs.length)];
function wallsFor(split, hole, variant) {
  const w = [];
  if (split === "train")
    for (let y = 0; y < SIZE; y++) if (y !== hole) w.push(cell(2, y));
  else if (split === "dev")
    for (let x = 0; x < SIZE; x++) if (x !== hole) w.push(cell(x, 2));
  else if (split === "eval") {
    for (let y = 0; y < SIZE; y++) if (y !== hole) w.push(cell(2, y));
    w.push(cell(variant % 2 ? 0 : 4, (hole + 2) % SIZE));
  } else throw Error("unknown task split");
  return [...new Set(w)].sort((a, b) => a - b);
}
function adjacent(p, walls) {
  const [x, y] = xy(p), w = new Set(walls);
  return DIRECTIONS.map(([dx, dy], a) => ({ x: x + dx, y: y + dy, a }))
    .filter(t => t.x >= 0 && t.x < SIZE && t.y >= 0 && t.y < SIZE && !w.has(cell(t.x, t.y)))
    .map(t => [cell(t.x, t.y), t.a]);
}
export function reachable(start, goal, walls) {
  if (start == null || goal == null || walls.includes(start) || walls.includes(goal)) return false;
  const seen = new Set([start]), queue = [start];
  for (let i = 0; i < queue.length; i++) {
    if (queue[i] === goal) return true;
    for (const [p] of adjacent(queue[i], walls)) if (!seen.has(p)) { seen.add(p); queue.push(p); }
  }
  return false;
}
export function signature(t) {
  return JSON.stringify([t.rule, t.walls, t.start, t.object, t.goal, t.wet, t.interruptionAt]);
}
export function generateTasks(seed, split, n) {
  if (!Number.isInteger(seed) || seed < 0 || !Number.isInteger(n) || n < 1 || !RULES[split])
    throw Error("invalid task generator arguments");
  const R = rng((seed * 7919 + { train: 11, dev: 43, eval: 97 }[split]) >>> 0);
  const tasks = [], unique = new Set();
  for (let attempt = 0; tasks.length < n && attempt < n * 500; attempt++) {
    const hole = Math.floor(R() * SIZE), walls = wallsFor(split, hole, Math.floor(R() * 4));
    const free = Array.from({ length: SIZE * SIZE }, (_, i) => i).filter(c => !walls.includes(c));
    const start = choose(R, free), object = choose(R, free.filter(c => c !== start));
    if (!reachable(start, object, walls)) continue;
    const impossible = (tasks.length + 1) % 8 === 0;
    const choices = impossible ? walls : free.filter(c => c !== start && c !== object &&
      reachable(start, c, walls) && reachable(object, c, walls));
    if (!choices.length) continue;
    const goal = choose(R, choices);
    const wet = choose(R, free.filter(c => c !== start && c !== object && c !== goal));
    const interruptionAt = R() < 0.4 ? 6 + Math.floor(R() * 10) : null;
    const t = { id: split + "-" + seed + "-" + tasks.length, start, object, goal, walls,
      wet, rule: RULES[split], interruptionAt };
    if (unique.has(signature(t))) continue;
    unique.add(signature(t)); tasks.push(t);
  }
  if (tasks.length !== n) throw Error("insufficient unique tasks: " + JSON.stringify({ seed, split, expected: n, actual: tasks.length }));
  return tasks;
}
export const feasible = t => reachable(t.start, t.object, t.walls) &&
  reachable(t.object, t.goal, t.walls);
// Only public geometry and current object-holding state control the action mask.
export function legalActions(obs) {
  const out = adjacent(obs.position, obs.walls).map(([, action]) => action);
  if (!obs.carrying && obs.position === obs.object) out.push(4);
  if (obs.carrying) out.push(5); // drop permitted anywhere, not just at the goal
  out.push(6);
  return out;
}
export class CarryWorld {
  constructor(task, seed = 0) {
    if (!task || !Object.values(RULES).includes(task.rule)) throw Error("invalid carry task");
    this.task = task; this.random = rng(seed >>> 0);
    this.position = task.start; this.object = task.object; this.carrying = false;
    this.previousMove = -1; this.lastEvent = "start";
    this.ticks = 0; this.done = false; this.success = false;
  }
  observe() {
    const t = this.task;
    return { position: this.position, object: this.object, goal: t.goal, walls: [...t.walls],
      wet: t.wet, carrying: this.carrying, previousMove: this.previousMove,
      lastEvent: this.lastEvent, remaining: LIMIT - this.ticks };
  }
  step(action) {
    if (this.done) throw Error("episode already finished");
    if (!Number.isInteger(action) || action < 0 || action >= ACTIONS.length)
      throw Error("invalid primitive action");
    const t = this.task;
    this.ticks++;
    let reward = -0.01, event = "wait";
    if (action < 4) {
      const next = adjacent(this.position, t.walls).find(([, a]) => a === action);
      if (!next) { reward -= 0.09; event = "blocked"; }
      else {
        this.position = next[0]; event = "moved";
        if (this.carrying && ((t.rule === "turn-drop" &&
            this.previousMove >= 0 && this.previousMove !== action) ||
            (t.rule === "wet-drop" && this.position === t.wet))) {
          this.carrying = false; this.object = this.position;
          reward -= 0.05; event = "forced_drop";
        }
        this.previousMove = action;
      }
    } else if (action === 4) {
      if (!this.carrying && this.position === this.object) {
        if (this.random() < 0.12) { reward -= 0.05; event = "pickup_failed"; }
        else { this.carrying = true; this.object = null; event = "picked_up"; }
      } else { reward -= 0.09; event = "invalid_pickup"; }
    } else if (action === 5) {
      if (!this.carrying) { reward -= 0.09; event = "invalid_drop"; }
      else {
        this.carrying = false; this.object = this.position;
        event = this.position === t.goal ? "placed" : "dropped";
        if (event === "placed") { this.success = true; this.done = true; reward += 1; }
      }
    }
    if (!this.done && this.carrying && this.ticks === t.interruptionAt) {
      this.carrying = false; this.object = this.position;
      reward -= 0.05; event = "interrupted_drop";
    }
    if (this.ticks >= LIMIT) { this.done = true; if (!this.success) event = "timeout"; }
    this.lastEvent = event;
    return { observation: this.observe(), reward, done: this.done,
      success: this.success, event, ticks: this.ticks };
  }
}
// Hand-written navigation control. It is not a learned skill or oracle success proof.
export function heuristicAction(obs) {
  if (obs.carrying && obs.position === obs.goal) return 5;
  if (!obs.carrying && obs.position === obs.object) return 4;
  const target = obs.carrying ? obs.goal : obs.object;
  if (!reachable(obs.position, target, obs.walls)) return 6;
  const seen = new Set([obs.position]), q = [[obs.position, null]];
  for (let i = 0; i < q.length; i++) {
    const [pos, first] = q[i];
    for (const [next, action] of adjacent(pos, obs.walls)) {
      if (seen.has(next)) continue;
      const a = first === null ? action : first;
      if (next === target) return a;
      seen.add(next); q.push([next, a]);
    }
  }
  return 6;
}
