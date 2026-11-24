// M0c own-step and wide-goal transfer protocol (#112/#153), follow-up to Round 29 of the review ledger.
// Part A (own step): every arm selects its OWN matched per-weight step on dev goals and seeds, from
//   a grid extended above Round 29's 0.064 edge, then is evaluated frozen at that step (20 seeds).
//   Tests whether the hidden-layer and eligibility effects survive when no arm is held at
//   another arm's step.
// Part B (wide transfer): one-drop family with 19 trained goal positions and 5 never-trained
//   interior heldout goals. With common random numbers a goal-blind policy succeeds on <= 1/5 of
//   heldout episodes, so heldout success above 1/5 needs goal information on untrained goals.
// Brain source and its backprop-free rule are unchanged; steps are set via matchedLearn().
import { pathToFileURL } from "node:url";
import { GAINS } from "./brain.js";
import { resultRecord, writeResult } from "./result.mjs";
import { DEV_SEEDS, GOALS, assertGoalSplits, makeModel } from "./stateful_credit_protocol.mjs";
import { ARMS, ETAS, EVAL_SEEDS, attempt, evalArm, label, score, select, train } from
  "./matched_step_credit_protocol.mjs";

export { ARMS, DEV_SEEDS, EVAL_SEEDS };
export const OWN_ETAS = Object.freeze([...ETAS, 0.128, 0.256, 0.512]);
export const WIDE_ARMS = Object.freeze(["native", "mask-goal", "flag-only"]);
const key = p => p.join(",");
const START = "2,0";
export const WIDE_HELDOUT = Object.freeze([[1, 1], [3, 1], [2, 2], [1, 3], [3, 3]]);
export const WIDE = Object.freeze({
  train: Object.freeze(Array.from({ length: 25 }, (_, i) => [i % 5, Math.floor(i / 5)])
    .filter(p => key(p) !== START && !WIDE_HELDOUT.some(h => key(h) === key(p)))),
  heldout: WIDE_HELDOUT,
});
export function assertWide() {
  const all = [...WIDE.train, ...WIDE.heldout].map(key);
  if (WIDE.train.length !== 19 || new Set(all).size !== 24 || all.includes(START) ||
      WIDE.heldout.some(([x, y]) => x < 1 || x > 3 || y < 1 || y > 3))
    throw new Error("wide goal split invalid");
}
const mean = a => a.length ? a.reduce((s, v) => s + v, 0) / a.length : 0;

// Part A. select() already returns each arm's own dev-best eta (ties -> smaller).
export function ownStep({ seeds = EVAL_SEEDS, devSeeds = DEV_SEEDS, etas = OWN_ETAS,
  budget = 8000, repeats = 12 } = {}) {
  const sel = select({ seeds: devSeeds, etas, budget, repeats });
  for (const r of sel.rows) r.split = "own-selection";
  const evals = ARMS.flatMap(arm => seeds.map(seed =>
    evalArm(seed, arm, sel.perArmBest[arm], { budget, repeats, split: "own-eval" })));
  return { rows: [...sel.rows, ...evals], curves: sel.curves, ownEta: sel.perArmBest };
}

// Part B selection: native only, dev seeds only, trained and scored on WIDE.train goals.
// Heldout goals are never touched before evaluation. Ties -> smaller eta.
export function wideSelect({ seeds = DEV_SEEDS, etas = ETAS, budget = 64000, repeats = 12 } = {}) {
  const rows = [];
  for (const eta of etas) for (const seed of seeds)
    rows.push(attempt({ arm: label("native", eta), seed, split: "wide-selection" }, () => {
      const model = makeModel(seed, "native");
      const training = train(model, "native", "train", seed, budget, eta, WIDE);
      const dev = score(model, "native", "train", repeats, seed, WIDE);
      return { eta, baseArm: "native", training, dev, primary: dev };
    }));
  const curve = etas.map(eta => ({ eta, devSuccess: mean(rows.filter(r =>
    r.arm === label("native", eta)).map(r => r.status === "ok" ? r.scores.dev.success : 0)) }));
  const selected = curve.reduce((b, s) => s.devSuccess > b.devSuccess + 1e-12 ? s : b).eta;
  return { rows, curve, selected };
}

export function wideTransfer({ seeds = EVAL_SEEDS, devSeeds = DEV_SEEDS, etas = ETAS,
  budget = 64000, repeats = 12 } = {}) {
  const sel = wideSelect({ seeds: devSeeds, etas, budget, repeats });
  const evals = WIDE_ARMS.flatMap(arm => seeds.map(seed =>
    evalArm(seed, arm, sel.selected, { budget, repeats, goals: WIDE, split: "wide-eval" })));
  return { rows: [...sel.rows, ...evals], curve: sel.curve, selected: sel.selected };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  const option = (name, fallback) => {
    const at = args.indexOf(name);
    return at < 0 ? fallback : args.splice(at, 2)[1];
  };
  const num = s => s.split(",").map(Number);
  const budget = Number(option("--budget", "8000"));
  const wideBudget = Number(option("--wide-budget", "64000"));
  const repeats = Number(option("--repeats", "12"));
  const devSeeds = num(option("--dev-seeds", DEV_SEEDS.join(",")));
  const etas = num(option("--etas", OWN_ETAS.join(",")));
  const wideEtas = num(option("--wide-etas", ETAS.join(",")));
  const out = option("--out", null);
  const seeds = args.length ? args.map(Number) : [...EVAL_SEEDS];
  const ints = [budget, wideBudget, repeats];
  if (!out || ints.some(n => !Number.isSafeInteger(n) || n < 1) ||
      new Set(seeds).size !== seeds.length || [etas, wideEtas].some(g => g.length < 1 ||
        g.some(e => !(e > 0)) || new Set(g).size !== g.length) ||
      seeds.some(s => !Number.isSafeInteger(s) || s < 0 || devSeeds.includes(s)))
    throw new Error("usage: --out FILE [--budget N] [--wide-budget N] [--repeats R] " +
      "[--dev-seeds a,b] [--etas a,b] [--wide-etas a,b] eval-seed ...");
  assertGoalSplits(); assertWide();
  const own = ownStep({ seeds, devSeeds, etas, budget, repeats });
  const wide = wideTransfer({ seeds, devSeeds, etas: wideEtas, budget: wideBudget, repeats });
  writeResult(out, resultRecord({
    experiment: "brain-world/m0c-own-step-transfer-protocol",
    baseline: label("native", own.ownEta.native), runs: [...own.rows, ...wide.rows],
    config: { family: "one-drop", arms: ARMS, wideArms: WIDE_ARMS, goals: GOALS, wideGoals: WIDE,
      devSeeds, seeds, repeats,
      own: { etaGrid: etas, budget, curves: own.curves, ownEta: own.ownEta,
        rule: "each arm: max mean own dev success on dev goals/seeds; divergence = 0; " +
          "ties -> smaller eta" },
      wide: { etaGrid: wideEtas, budget: wideBudget, curve: wide.curve, selected: wide.selected,
        rule: "native: max mean dev-seed success on WIDE.train goals; heldout untouched; " +
          "ties -> smaller eta; all wide arms at that eta" },
      stepRule: "lrP = lrV = eta * (1 + next running |h|^2) before every learn()",
      baseGains: { lrP: GAINS.lrP, lrV: GAINS.lrV } },
    budgets: { trainDecisionsPerArm: { own: budget, wide: wideBudget },
      policyOracleQueriesPerArm: 0, frozenScoring: true,
      note: "single 5x5 one-drop family, item at start; wide heldout goals are interior cells" },
    metrics: { "primary.success": "higher" },
  }));
  console.log("own eta", JSON.stringify(own.ownEta), "wide eta", wide.selected);
  for (const [split, arms] of [["own-eval", ARMS], ["wide-eval", WIDE_ARMS]]) for (const arm of arms) {
    const g = [...own.rows, ...wide.rows].filter(r => r.split === split && r.arm.startsWith(`${arm}@`));
    const ok = g.filter(r => r.status === "ok");
    console.log(split, arm.padEnd(15), "ok", ok.length, "/", g.length,
      "train", mean(ok.map(r => r.scores.after.train.success)).toFixed(3),
      "heldout", mean(ok.map(r => r.scores.after.heldout.success)).toFixed(3));
  }
}
