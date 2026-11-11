// Candidate recombination and validity-gated novelty (issue #111) on the #110 construction tasks.
// No creature is trained here: these are engineered arms that set the bar a learned one must beat.
//
// Novelty is only awarded to a candidate that passes the task validator, is a new picture (up to
// the pad's lr / ud / rot symmetry) and is not already in the library of prior solutions.
// Invalid candidates, repeated strokes, reorderings, mirrored copies and noise all score zero.
//
// Arms, each allowed the same number of validator calls (`budget`):
//   random     random stroke lists (repeats and out-of-range strokes possible)
//   retrieval  prior solutions from training tasks, replayed unchanged
//   search     engineered: hill-climbs from retrieved drawings by adding / removing / swapping one
//              stroke, ranked by a graded penalty (the validator alone only says pass or fail)
// Run: node game/world/novelty.mjs [seeds, default 1-10] [--tasks N] [--budget N] [--out FILE.json]
import { PEN, glyph } from "./brain.js";
import { generate, solutions, violation, valid } from "./construct.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

const MAP = [(r, c) => [r, c], (r, c) => [r, 4 - c], (r, c) => [4 - r, c], (r, c) => [4 - r, 4 - c]];

// The picture a stroke set draws, identical for pad-symmetric copies. Invalid input has none.
export function pictureClass(strokes) {
  if (!Array.isArray(strokes) || !strokes.length || strokes.some(s => !Number.isInteger(s) || s < 0 || s >= PEN.length)) return null;
  const g = glyph([...new Set(strokes)]), cells = [];
  for (let i = 0; i < 25; i++) if (g[i]) cells.push([Math.floor(i / 5), i % 5]);
  return MAP.map(f => cells.map(([r, c]) => f(r, c)[0] * 5 + f(r, c)[1]).sort((a, b) => a - b).join()).sort()[0];
}

// Graded penalty (0 = valid): missed cells + asymmetric cells + strokes over budget + repeats.
export function penalty(task, strokes) {
  if (!Array.isArray(strokes) || !strokes.length || strokes.some(s => !Number.isInteger(s) || s < 0 || s >= PEN.length)) return 99;
  let p = strokes.length - new Set(strokes).size + Math.max(0, strokes.length - task.budget);
  const g = glyph([...new Set(strokes)]);
  for (const [r, c] of task.points) if (!g[r * 5 + c]) p++;
  if (task.axis) {
    const f = MAP[{ lr: 1, ud: 2, rot: 3 }[task.axis]];
    for (let i = 0; i < 25; i++) if (g[i]) { const [r, c] = f(Math.floor(i / 5), i % 5); if (!g[r * 5 + c]) p++; }
  }
  return p;
}

// Score candidates in order. Each is checked once (one validator call), then gated.
export function score(task, candidates, known = []) {
  const seen = new Set(known.map(pictureClass)), rejected = {};
  let validN = 0, novel = 0;
  for (const c of candidates) {
    const why = violation(task, c);
    if (why) { const k = why.replace(/ -?\d+,-?\d+/, ""); rejected[k] = (rejected[k] || 0) + 1; continue; }
    validN++;
    const cls = pictureClass(c);
    if (seen.has(cls)) { rejected["duplicate picture or known"] = (rejected["duplicate picture or known"] || 0) + 1; continue; }
    seen.add(cls); novel++;
  }
  return { valid: validN, novel, rejected, checked: candidates.length };
}

function rng(seed) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}
const pick = (R, xs) => xs[Math.floor(R() * xs.length)];

export const ARMS = {
  random(task, budget, R) {
    return Array.from({ length: budget }, () => Array.from({ length: 1 + Math.floor(R() * 4) }, () => Math.floor(R() * (PEN.length + 1))));
  },
  retrieval(task, budget, R, library) {
    const order = library.map(d => [R(), d]).sort((a, b) => a[0] - b[0]).map(x => x[1]);
    return order.slice(0, budget);
  },
  search(task, budget, R, library) {
    const out = [];
    let cur = pick(R, library), best = penalty(task, cur);
    while (out.length < budget) {
      const s = new Set(cur), k = Math.floor(R() * PEN.length);
      if (R() < 0.3 && s.size > 0) { const j = Math.floor(R() * PEN.length); s.has(j) ? s.delete(j) : s.add(j); }   // swap-ish second toggle
      s.has(k) ? s.delete(k) : s.add(k);
      const cand = [...s].sort((a, b) => a - b);
      out.push(cand);
      const p = penalty(task, cand);
      if (p <= best) { cur = cand; best = p; }
      else if (R() < 0.15) { cur = pick(R, library); best = penalty(task, cur); }   // restart
      if (!cur.length) { cur = pick(R, library); best = penalty(task, cur); }
    }
    return out;
  },
};

// Prior solutions the library holds: every valid drawing of `n` training tasks.
export function library(seed, n = 12) {
  const lib = new Map();
  for (const t of generate(seed, "train", n).tasks) for (const s of solutions(t)) lib.set(s.join(), s);
  return [...lib.values()];
}

export function compare(seed, { tasks = 30, budget = 8 } = {}) {
  const lib = library(seed), { tasks: eval_ } = generate(seed, "eval", tasks), rows = [], log = [];
  for (const arm of Object.keys(ARMS)) {
    const R = rng(seed * 31 + arm.length), t0 = Date.now(), tot = { valid: 0, novel: 0, checked: 0 }, rej = {};
    for (const task of eval_) {
      const cands = ARMS[arm](task, budget, R, lib), r = score(task, cands, lib);
      tot.valid += r.valid; tot.novel += r.novel; tot.checked += r.checked;
      for (const [k, v] of Object.entries(r.rejected)) rej[k] = (rej[k] || 0) + v;
    }
    const n = eval_.length;
    log.push({ seed, arm, budget, tasks: n, validatorCalls: tot.checked, rejected: rej });
    rows.push(run({ arm, seed, split: "eval", status: "ok", seconds: (Date.now() - t0) / 1000,
      scores: { valid: tot.valid / n, novel: tot.novel / n, validatorCalls: tot.checked / n } }));
  }
  return { rows, log, libraryClasses: new Set(lib.map(pictureClass)).size };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const arg = (f, d) => { const i = process.argv.indexOf(f); return i < 0 ? d : process.argv[i + 1]; };
  const seeds = Array.from({ length: 10 }, (_, i) => i + 1), tasks = Number(arg("--tasks", 30)), budget = Number(arg("--budget", 8)), out = arg("--out", null);
  const runs = [], logs = [];
  for (const seed of seeds) { const r = compare(seed, { tasks, budget }); runs.push(...r.rows); logs.push(...r.log); }
  const mean = (arm, k) => runs.filter(r => r.arm === arm).reduce((a, r) => a + r.scores[k], 0) / seeds.length;
  for (const arm of Object.keys(ARMS)) console.log(arm.padEnd(10), "valid", mean(arm, "valid").toFixed(2), "novel", mean(arm, "novel").toFixed(2), "per task at", budget, "validator calls");
  if (out) writeResult(out, resultRecord({ experiment: "brain-world/novelty", baseline: "random", runs,
    metrics: { valid: "higher", novel: "higher", validatorCalls: "lower" },
    config: { seeds, tasks, split: "eval", arms: Object.keys(ARMS), engineered: "search (penalty, mutation) and the validator are engineered; no creature involved", candidateLog: logs },
    budgets: { validatorCallsPerTask: budget } }));
}
