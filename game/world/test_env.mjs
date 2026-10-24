// The common environment interface (#118) gives baselines what the creature gets and nothing more.
// Run: node game/world/test_env.mjs   (a few seconds)
import assert from "node:assert/strict";
import { World, ACT_SETS } from "./brain.js";
import { Env } from "./env.mjs";
import { POLICIES, evaluate } from "./baselines.mjs";
import { trainAndScore } from "./rl.mjs";

// Observations are the creature's senses: same length as World.sense(), no extra fields.
const w = new World(1), env = new Env(1, "grasp");
assert.equal(env.obs.length, w.sense().length);
assert.ok(env.obs instanceof Float32Array);
// Action constraints: the graduated creature's habit set off the board, the pen at the board.
assert.deepEqual(env.allowed, ACT_SETS[1]);
assert.deepEqual(new Env(1, "write").allowed, ACT_SETS[2]);
assert.throws(() => env.step(2), /not allowed/);   // lifting a leg is the reflex's job once graduated
// Episodes end by the World's own rules, and the time limit holds.
const e = new Env(2, "listen");
let steps = 0, r;
do { r = e.step(1); steps++; } while (!r.done);   // always push right: never grasps, so it times out
assert.equal(steps, 150);
assert.equal(r.success, false);
// Deterministic per seed, and the references sit where they should: random near chance, the
// heuristic grasps the lone object every time and picks the nearest of three on listen (about 1/3).
assert.deepEqual(evaluate(POLICIES.random, 1, "grasp", 50), evaluate(POLICIES.random, 1, "grasp", 50));
assert.ok(evaluate(POLICIES.heuristic, 1, "grasp", 100).success > 0.9);
const l = evaluate(POLICIES.heuristic, 1, "listen", 300).success;
assert.ok(l > 0.2 && l < 0.5, `heuristic listen ${l}`);
// The backprop actor-critic learns through the same interface: write (one step per stroke) within
// 30,000 steps, and scoring leaves its weights alone (trainAndScore throws if they change).
const rl = trainAndScore(1, "write", { budget: 30000, episodes: 100 });
assert.ok(rl.success > 0.9, `actor-critic write ${rl.success}`);
assert.ok(rl.trainSteps >= 30000 && rl.trainSteps < 30200);
console.log("env interface: ok");
