// Fast live checkpoint behavior gate (#154). No pretraining in CI.
// The historical v3 fixture predates inferred context slots. This detects
// drift in its migrated behavior, not improved transfer or human intelligence.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { World } from "./brain.js";
import { assertDisjoint, frozen, SPLITS } from "./heldout.mjs";

const bytes = readFileSync(new URL("./fixtures/v3-seed1.json", import.meta.url));
const blobHash = createHash("sha1").update("blob " + bytes.length + "\0").update(bytes).digest("hex");
assert.equal(blobHash, "37f865440eb4ed6daafda0ac1553b52121caa011",
  "trained fixture changed: review and rebaseline its behavioral contract");
const checkpoint = JSON.parse(bytes.toString("utf8"));
const restore = () => World.fromJSON(JSON.parse(JSON.stringify(checkpoint)));
assertDisjoint();
assert.deepEqual(SPLITS, { train: [0, 1], dev: [2], eval: [3] });

// Previously measured on this same fixture by test_brain.mjs: 80/100 read.
// This is not a competence threshold for freshly trained brains.
const w = restore();
const savedBrain = JSON.stringify(w.toJSON().brain);
const read = frozen(w, "read", 100, null);
assert.equal(read, 0.8, "migrated checkpoint read score drifted: " + read);
assert.equal(JSON.stringify(w.toJSON().brain), savedBrain,
  "frozen evaluation changed checkpoint parameters");
assert.equal(frozen(restore(), "read", 100, null), read,
  "same checkpoint should reproduce the same frozen score");

// Train/eval layout rooms remain disjoint even for a historical checkpoint.
// Report these scores but do not train, optimize or set thresholds on eval.
const train = frozen(restore(), "read", 20, "train");
const evalScore = frozen(restore(), "read", 20, "eval");
for (const score of [train, evalScore]) {
  assert.ok(Number.isFinite(score) && score >= 0 && score <= 1);
}

// Save/load must preserve a learned brain's action stream.
const original = restore(), loaded = World.fromJSON(JSON.parse(JSON.stringify(original)));
for (let i = 0; i < 250; i++) {
  assert.deepEqual(loaded.step(), original.step(), "save/load diverged at step " + i);
}

// Show that the frozen evaluator rejects weight updates on evaluation data.
const contaminated = restore(), perform = contaminated.perform.bind(contaminated);
contaminated.perform = (...args) => {
  perform(...args);
  contaminated.brain.learning = true; // deliberately violate test-only scoring
};
assert.throws(() => frozen(contaminated, "read", 50, null), /changed the brain/,
  "frozen evaluator failed to detect learning on held-out data");

const broken = JSON.parse(JSON.stringify(checkpoint));
broken.brain.gate = broken.brain.gate.slice(1);
assert.throws(() => World.fromJSON(broken), /not a Brain World save/,
  "invalid saved gate shape should be rejected");
console.log(JSON.stringify({ checkpoint: "v3-seed1", read, train, eval: evalScore,
  frozen: true, saveLoadSteps: 250, detectedMutation: true }));
