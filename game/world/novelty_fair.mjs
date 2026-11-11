// Matched-query novelty baseline (#111). Historical novelty.mjs is not a fair
// information-budget comparison: it uses malformed random candidates and free graded search.
import { pathToFileURL } from "node:url";
import { PEN } from "./brain.js";
import { generate, violation } from "./construct.mjs";
import { library, penalty, pictureClass } from "./novelty.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

export const ARMS = ["random-valid", "retrieval", "mutate-blind", "search-binary", "search-graded"];
export const FEEDBACK = Object.freeze({
  "random-valid": "binary (unused)",
  retrieval: "binary (unused)",
  "mutate-blind": "binary (unused)",
  "search-binary": "binary validity only",
  "search-graded": "binary validity plus privileged numerical penalty",
});
export function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
const pick = (R, xs) => xs[Math.floor(R() * xs.length)];
const sorted = xs => [...xs].sort((a, b) => a - b);

// Sample syntactically legal, unique strokes within the budget. The goal itself
// is not consulted; validity still has to be discovered through a charged query.
export function randomLegal(R, budget) {
  if (!Number.isInteger(budget) || budget < 1) throw new Error("positive stroke budget required");
  const pool = PEN.map((_, i) => i), n = 1 + Math.floor(R() * Math.min(budget, pool.length));
  for (let i = 0; i < n; i++) {
    const j = i + Math.floor(R() * (pool.length - i));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return sorted(pool.slice(0, n));
}
// Goal-blind edit from a prior drawing, with the same syntactic constraints.
export function mutate(R, parent, budget) {
  if (!Array.isArray(parent)) throw new Error("expected parent drawing");
  const set = new Set(parent.filter(i => Number.isInteger(i) && i >= 0 && i < PEN.length));
  const max = Math.min(budget, PEN.length);
  if (!Number.isInteger(max) || max < 1) throw new Error("positive stroke budget required");
  while (set.size > max) set.delete(pick(R, [...set]));
  const k = Math.floor(R() * PEN.length);
  if (set.has(k)) {
    if (set.size > 1) set.delete(k);
    else {
      set.delete(k);
      set.add((k + 1 + Math.floor(R() * (PEN.length - 1))) % PEN.length);
    }
  } else {
    if (set.size >= max) set.delete(pick(R, [...set]));
    set.add(k);
  }
  return sorted(set);
}

// Validator and optional grader are called only here, once per attempted candidate.
// Binary search sees only passed; the privileged upper bound also sees distance.
export function runTask(task, budget, R, known, arm, {
  validator = violation, grader = penalty,
} = {}) {
  if (!ARMS.includes(arm)) throw new Error("unknown novelty arm " + arm);
  if (!Number.isInteger(budget) || budget < 1) throw new Error("positive query budget required");
  if (!Array.isArray(known) || !known.length) throw new Error("training library is empty");
  const seen = new Set(known.map(pictureClass)), rejected = {}, trace = [];
  let checked = 0, gradedCalls = 0, valid = 0, novel = 0;
  const graded = arm === "search-graded";
  function ask(candidate) {
    if (checked >= budget) throw new Error("validator budget exceeded");
    checked++;
    const why = validator(task, candidate);
    if (why !== null && typeof why !== "string") throw new Error("invalid verifier result");
    const passed = why === null;
    let distance = null;
    if (graded) {
      gradedCalls++;
      distance = grader(task, candidate);
      if (!Number.isFinite(distance) || (distance === 0) !== passed)
        throw new Error("graded feedback disagrees with verifier");
    }
    let newPicture = false;
    if (passed) {
      valid++;
      const cls = pictureClass(candidate);
      if (!seen.has(cls)) { seen.add(cls); novel++; newPicture = true; }
      else rejected["duplicate picture or known"] = (rejected["duplicate picture or known"] || 0) + 1;
    } else {
      rejected[why] = (rejected[why] || 0) + 1;
    }
    trace.push({ candidate: [...candidate], passed, novel: newPicture, reason: why,
      ...(graded ? { distance } : {}) });
    return graded ? { passed, distance } : { passed };
  }
  // All methods see an oracle-built training library, not a learned creature memory.
  // A known drawing whose length exceeds the public budget is not a legal
  // retrieval candidate. Apply this *goal-agnostic* syntactic filter to every
  // library-seeded arm without looking at the task's points or symmetry.
  const order = known.filter(d => d.length <= task.budget);
  if (!order.length) throw new Error("no budget-compatible library drawings");
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(R() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  let parent = pick(R, order), best = Infinity;
  for (let i = 0; i < budget; i++) {
    const candidate = arm === "random-valid" ? randomLegal(R, task.budget)
      : arm === "retrieval" ? [...order[i % order.length]]
        : arm === "mutate-blind" ? mutate(R, pick(R, order), task.budget)
          : mutate(R, parent, task.budget);
    const feedback = ask(candidate);
    if (arm === "search-binary" && feedback.passed) parent = candidate;
    if (graded && feedback.distance <= best) { parent = candidate; best = feedback.distance; }
    if ((arm === "search-binary" || graded) && R() < 0.1) {
      parent = pick(R, order);
      best = Infinity;
    }
  }
  if (checked !== budget || gradedCalls !== (graded ? budget : 0))
    throw new Error("feedback budget mismatch");
  return { valid, novel, validatorCalls: checked, gradedCalls, rejected, trace };
}

const stringHash = s => {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619);
  return h >>> 0;
};
export function compareFair(seed, { tasks = 30, budget = 8, arms = ARMS } = {}) {
  if (!Number.isInteger(seed) || seed < 0 || !Number.isInteger(tasks) || tasks < 1 ||
      !Number.isInteger(budget) || budget < 1 || !Array.isArray(arms) || !arms.length ||
      arms.some(a => !ARMS.includes(a)) || new Set(arms).size !== arms.length)
    throw new Error("invalid experiment configuration");
  const known = library(seed), tasksEval = generate(seed, "eval", tasks).tasks;
  if (tasksEval.length !== tasks) throw new Error("incomplete evaluation task generation");
  const rows = [], audit = [];
  for (const arm of arms) {
    const R = rng((seed * 7919) ^ stringHash(arm)), start = Date.now();
    const sum = { valid: 0, novel: 0, validatorCalls: 0, gradedCalls: 0 };
    for (const task of tasksEval) {
      const trial = runTask(task, budget, R, known, arm);
      for (const k of Object.keys(sum)) sum[k] += trial[k];
      audit.push({ seed, arm, task: task.id, checked: trial.validatorCalls,
        gradedFeedback: trial.gradedCalls, valid: trial.valid, novel: trial.novel,
        rejected: trial.rejected, candidates: trial.trace });
    }
    rows.push(run({ arm, seed, split: "eval", status: "ok", seconds: (Date.now() - start) / 1000,
      scores: Object.fromEntries(Object.entries(sum).map(([k, v]) => [k, v / tasks])) }));
  }
  return { rows, audit, libraryClasses: new Set(known.map(pictureClass)).size };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2), opt = (flag, def) => {
    const i = args.indexOf(flag);
    return i < 0 ? def : args.splice(i, 2)[1];
  };
  const tasks = Number(opt("--tasks", "30")), budget = Number(opt("--budget", "8"));
  const out = opt("--out", null), seeds = args.length ? args.map(Number)
    : Array.from({ length: 10 }, (_, i) => i + 1);
  if (seeds.some(s => !Number.isInteger(s) || s < 0) || new Set(seeds).size !== seeds.length)
    throw new Error("seeds must be distinct nonnegative integers");
  const runs = [], audit = [];
  for (const seed of seeds) {
    const result = compareFair(seed, { tasks, budget });
    runs.push(...result.rows); audit.push(...result.audit);
  }
  for (const arm of ARMS) {
    const rows = runs.filter(r => r.arm === arm);
    const avg = k => rows.reduce((s, r) => s + r.scores[k], 0) / rows.length;
    console.log(arm.padEnd(15), "valid", avg("valid").toFixed(3),
      "novel", avg("novel").toFixed(3), "validator", avg("validatorCalls"),
      "graded", avg("gradedCalls"));
  }
  if (out) writeResult(out, resultRecord({
    experiment: "brain-world/novelty-fair", baseline: "random-valid", runs,
    metrics: { valid: "higher", novel: "higher", validatorCalls: "lower", gradedCalls: "lower" },
    config: { seeds, tasks, split: "eval", arms: ARMS, feedback: FEEDBACK,
      limitations: "Engineered search and oracle-built library, no trained creature; six-stroke space has only 63 nonempty combinations.",
      audit }, budgets: { validatorCallsPerTask: budget,
      privilegedGradedCallsPerTask: "0 for binary arms, budget for search-graded" },
  }));
}
