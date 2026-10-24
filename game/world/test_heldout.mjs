// Held-out splits (#105): disjoint, enforced on every room, and frozen scoring learns nothing.
// Fast: no curriculum is trained. Run: node game/world/test_heldout.mjs
import assert from "node:assert/strict";
import { World } from "./brain.js";
import { assertDisjoint, frozen, QUADRANT, SPLITS } from "./heldout.mjs";

assertDisjoint();
for (const [name, quads] of Object.entries(SPLITS)) {
  const w = new World(7);
  w.roomFilter = p => quads.includes(QUADRANT(p));
  for (const s of [1, 2, 3]) {   // grasp, listen, read
    w.setStage(s);
    for (let k = 0; k < 200; k++) { assert.ok(quads.includes(QUADRANT(w.objects[w.target].pos)), `${name} room left its split`); w.reset(); }
  }
}
const w = new World(5);
w.setStage(2);
for (let k = 0; k < 3000; k++) w.step();   // some learning, then frozen scores must not change it
const before = JSON.stringify(w.toJSON().brain);
for (const sp of Object.keys(SPLITS)) frozen(w, "listen", 20, sp);
assert.equal(JSON.stringify(w.toJSON().brain), before);
w.brain.learning = true;   // and the check catches a brain that does learn: perform turns learning off, so force it
const perform = w.perform.bind(w);
w.perform = key => { perform(key); w.brain.learning = true; };
assert.throws(() => frozen(w, "listen", 50, "train"), /changed the brain/);
console.log("ok");
