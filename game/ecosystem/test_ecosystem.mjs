// Headless check that every species' brains learn from their own experience.
// 1. Alone (energy and age held, so nothing dies), learning on beats learning off: humans and foxes
//    eat more, and insects pick the colour that carries nectar this season.
// 2. In the shared world, grown foxes and humans, tested alone with learning off, eat more than
//    newborns with the same genome: what they gained is learned, not inherited.
// Run: node game/ecosystem/test_ecosystem.mjs [seed ...]   (default seeds 1 2 3; about a minute)
import assert from "node:assert/strict";
import { World, SPECIES, probe } from "./ecosystem.js";

const seeds = process.argv.slice(2).map(Number);
const SEEDS = seeds.length ? seeds : [1, 2, 3];
const mean = a => a.reduce((s, v) => s + v, 0) / a.length;

// Food per step in the second half of a solo run, and the insect's rich-colour share in the second
// half of each season.
function solo(sp, seed, learn, steps = 8000) {
  const pop = { insect: sp === "fox" ? 20 : 0, fox: 0, human: 0 }; pop[sp] = 1;
  const w = new World(seed, { learn, pop, births: false });
  let f0 = 0;
  for (let i = 0; i < steps; i++) {
    for (const c of w.creatures) if (c.sp === sp) { c.energy = 1.5; c.age = 0; }
    w.step();
    if (i === steps / 2 - 1) f0 = w.stats[sp].food;
  }
  const v = w.seasonVisits, rich = v.reduce((s, x) => s + x[0], 0), all = v.reduce((s, x) => s + x[0] + x[1], 0);
  return { food: (w.stats[sp].food - f0) / (steps / 2), rich: rich / Math.max(1, all) };
}

for (const sp of ["human", "fox"]) {
  const on = mean(SEEDS.map(s => solo(sp, s, true).food)), off = mean(SEEDS.map(s => solo(sp, s, false).food));
  console.log(`${sp} alone: food per 1000 steps ${(on * 1000).toFixed(1)} learning, ${(off * 1000).toFixed(1)} not`);
  assert.ok(on > 1.4 * off, `${sp} learning does not pay: ${on} vs ${off}`);
}
{
  const on = mean(SEEDS.map(s => solo("insect", s, true, 16000).rich)), off = mean(SEEDS.map(s => solo("insect", s, false, 16000).rich));
  console.log(`insect alone: share of flower visits on the rich colour ${on.toFixed(2)} learning, ${off.toFixed(2)} not`);
  assert.ok(on > 0.65, `insects do not learn the rich colour: ${on}`);
  assert.ok(off < 0.6, `insects prefer the rich colour without learning: ${off}`);
}

for (const sp of ["human", "fox"]) {
  const learned = [], born = [];
  for (const seed of SEEDS.slice(0, 2)) {
    const w = new World(seed);
    for (let i = 0; i < 6000; i++) w.step();
    for (const c of w.creatures) {
      assert.ok(Number.isFinite(c.energy) && c.brain.wP.every(Number.isFinite) && c.brain.wV.every(Number.isFinite), `non-finite state in ${c.sp} ${c.id}`);
    }
    for (const s in SPECIES) assert.ok(w.count(s) > 0, `${s} died out`);
    const old = w.creatures.filter(c => c.sp === sp).sort((a, b) => b.age - a.age).slice(0, 3);
    for (const c of old) { learned.push(probe(c, w).food); born.push(probe(c, w, { newborn: true }).food); }
  }
  console.log(`${sp} in the world: grown ${(mean(learned) * 1000).toFixed(1)}, newborn ${(mean(born) * 1000).toFixed(1)} food per 1000 steps`);
  assert.ok(mean(learned) > 1.2 * mean(born), `grown ${sp} are no better than newborns`);
}

// Same seed, same world.
const a = new World(5), b = new World(5);
for (let i = 0; i < 500; i++) { a.step(); b.step(); }
assert.deepEqual(a.creatures.map(c => [c.x, c.y, c.energy]), b.creatures.map(c => [c.x, c.y, c.energy]));
console.log("ok");
