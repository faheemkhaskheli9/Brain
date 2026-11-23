// Adversarial step-size sweep for the M0c credit probe (#112/#153). Exploratory and
// IN-SAMPLE: scales GAINS.lrP/lrV on the same fixed task that is scored. Not a tuning result.
// Usage: node game/world/stateful_credit_lr_sweep.mjs SCALE [seed ...]   (default seeds 1-10)
import { GAINS } from "./brain.js";
import { runSeed } from "./stateful_credit_probe.mjs";

const [scaleArg, ...seedArgs] = process.argv.slice(2);
const scale = Number(scaleArg);
const seeds = seedArgs.length ? seedArgs.map(Number) : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
if (!(scale > 0) || seeds.some(s => !Number.isSafeInteger(s) || s < 0))
  throw new Error("usage: SCALE [seed ...]");
GAINS.lrP *= scale;
GAINS.lrV *= scale;
const out = {};
for (const seed of seeds) for (const r of runSeed(seed)) {
  const a = (out[r.arm] ??= { wins: [], errors: 0, variants: 0, goalL1: 0 });
  if (r.status !== "ok") { a.errors++; continue; }
  const p = r.scores.curve.at(-1);
  a.wins.push(p.calibration.deliveries);
  a.variants += p.diagnosticVariants.success;
  a.goalL1 += p.sensory.goalCounterfactualL1;
}
for (const [arm, a] of Object.entries(out)) {
  const n = a.wins.length, per = p => n ? (p / n).toFixed(4) : "n/a";
  const reps = n ? a.wins.reduce((s, v) => s + v, 0) / n : 0;
  console.log(JSON.stringify({ scale, arm, okSeeds: n, errors: a.errors,
    perSeedDeliveries: a.wins, meanDeliveriesPerSeed: reps,
    nearbyVariants: per(a.variants), goalL1: per(a.goalL1) }));
}
