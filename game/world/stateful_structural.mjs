// Independent M0c structural task families for the same stateful pickup/carry/place world.
// Generator-only oracle calls certify feasibility before any policy receives a task;
// no learned arm or public heuristic can import this generator's privileged path.
import { rng } from "./brain.js";
import { SIDE, START, oracle, validateTask } from "./stateful_construct.mjs";

export const PROTOCOLS = Object.freeze(["legacy", "scattered-to-barrier", "barrier-to-scattered"]);
export const STRESS_FAMILIES = Object.freeze(["scattered", "barrier"]);
const SPLIT = Object.freeze({ train: 1, dev: 2, eval: 3 });
const cellId = p => p[1] * SIDE + p[0];
const cells = () => Array.from({ length: SIDE * SIDE }, (_, c) => [c % SIDE, Math.floor(c / SIDE)]);
const randomIndex = (R, n) => Math.floor(R() * n);
const choice = (R, list) => list[randomIndex(R, list.length)];
const same = (a, b) => a[0] === b[0] && a[1] === b[1];
const distance = (a, b) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);

// Canonical PHYSICAL identity: never put task ID, seed or split in this key.
// The simulator's start is explicit on stress tasks and remains START for legacy.
export function physicalFingerprint(task) {
  validateTask(task);
  const walls = task.walls.map(cellId).sort((a, b) => a - b);
  return JSON.stringify([task.start ?? START, task.item, task.goal, walls,
    task.maxSteps, "stateful-construct-dynamics-v1"]);
}

function draw(R, pool) {
  if (!pool.length) throw new Error("candidate pool depleted");
  return pool.splice(randomIndex(R, pool.length), 1)[0];
}

function candidate(R, family, split, seed, index) {
  let walls = [], start, item, goal;
  if (family === "scattered") {
    const pool = cells(), count = 2 + randomIndex(R, 5);
    for (let j = 0; j < count; j++) walls.push(draw(R, pool));
    start = draw(R, pool); item = draw(R, pool); goal = draw(R, pool);
    // Avoid easy all-adjacent cases while retaining diverse layouts and affordances.
    if (distance(start, item) + distance(item, goal) < 5) return null;
  } else {
    const axis = randomIndex(R, 2), position = 1 + randomIndex(R, SIDE - 2);
    const gap = randomIndex(R, SIDE);
    for (let j = 0; j < SIDE; j++) if (j !== gap)
      walls.push(axis === 0 ? [position, j] : [j, position]);
    const blocked = new Set(walls.map(cellId));
    const other = cells().filter(p => !blocked.has(cellId(p)));
    // Place distractors outside the traversable gap and keep at least two
    // cells available for item+start on one side.
    for (let j = 0, count = randomIndex(R, 3); j < count; j++)
      walls.push(draw(R, other));
    const free = cells().filter(p => !walls.some(w => same(w, p)));
    const fromHigh = R() < 0.5;
    const before = free.filter(p => fromHigh ? p[axis] > position : p[axis] < position);
    const after = free.filter(p => fromHigh ? p[axis] < position : p[axis] > position);
    if (before.length < 2 || after.length < 1) return null;
    start = draw(R, before); item = draw(R, before);
    goal = choice(R, after);
  }
  return { id: family + "-" + split + "-" + seed + "-" + index,
    start, item, goal, walls, maxSteps: 40 };
}

// seen is shared across the named splits of one independent benchmark generation.
// A structural collision is rejected rather than relabelled as "held out".
// Returned oracleQueries is OFFLINE generator cost; each learned arm spends zero.
export function generateStructural(seed, split, family, n = 24, seen = new Set()) {
  if (!Number.isSafeInteger(seed) || seed < 0 || !Object.hasOwn(SPLIT, split) ||
      !STRESS_FAMILIES.includes(family) || !Number.isSafeInteger(n) || n < 1 ||
      !(seen instanceof Set))
    throw new Error("invalid structural task generation request");
  const R = rng((Math.imul(seed + 1, 88661) ^ (SPLIT[split] * 593) ^
    (family === "scattered" ? 0x4bad : 0x8a1d)) >>> 0);
  const tasks = [], stats = { family, split, attempted: 0, duplicateRejected: 0,
    invalidRejected: 0, infeasibleRejected: 0, oracleQueries: 0, feasible: 0,
    maxMinimalPath: 0, minMinimalPath: null };
  while (tasks.length < n) {
    if (++stats.attempted > n * 200)
      throw new Error("structural generator exhausted unique feasible candidates");
    const task = candidate(R, family, split, seed, tasks.length);
    if (!task) { stats.invalidRejected++; continue; }
    const id = physicalFingerprint(task);
    if (seen.has(id)) { stats.duplicateRejected++; continue; }
    // Feasibility is evaluated BEFORE policy training on a separate generator path.
    stats.oracleQueries++;
    const path = oracle(task);
    if (!path || path.length > task.maxSteps) { stats.infeasibleRejected++; continue; }
    stats.feasible++; stats.maxMinimalPath = Math.max(stats.maxMinimalPath, path.length);
    stats.minMinimalPath = Math.min(stats.minMinimalPath ?? path.length, path.length);
    seen.add(id);
    tasks.push(task);
  }
  return { tasks, audit: stats };
}

export function createStructuralBenchmark(seed, protocol, sizes) {
  if (!PROTOCOLS.includes(protocol) || protocol === "legacy")
    throw new Error("choose an independent structural stress protocol");
  const [source, target] = protocol === "scattered-to-barrier" ?
    ["scattered", "barrier"] : ["barrier", "scattered"];
  const seen = new Set();
  const train = generateStructural(seed, "train", source, sizes.train, seen);
  const dev = generateStructural(seed, "dev", source, sizes.dev, seen);
  const heldout = generateStructural(seed, "eval", target, sizes.heldout, seen);
  return { train: train.tasks, dev: dev.tasks, heldout: heldout.tasks,
    audit: { protocol, sourceFamily: source, heldoutFamily: target,
      train: train.audit, dev: dev.audit, heldout: heldout.audit,
      totalOfflineOracleQueries: train.audit.oracleQueries + dev.audit.oracleQueries +
        heldout.audit.oracleQueries } };
}
