// Score a saved brain with learning off: the success rate per skill, and the context slot it used
// most. Skill "any" is free play: a random scene per episode, episodes x 5 in all. Never writes the save.
// Run: node game/world/perform.mjs <save.json | --seed N> [skill ... | any] [--episodes N] [--greedy walk,write]
// --seed N trains seed N to graduation in memory instead of loading a file (about 20 s).
// --greedy lists the skills that take the argmax action (default GAINS.performGreedy; "" = none).
import { readFileSync } from "node:fs";
import { World, STAGES, GAINS } from "./brain.js";

const args = process.argv.slice(2), opt = (name, dflt) => {
  const i = args.indexOf(name);
  return i < 0 ? dflt : args.splice(i, 2)[1];
};
const episodes = Number(opt("--episodes", 500)), seed = opt("--seed", null);
const greedy = opt("--greedy", GAINS.performGreedy.join(",")).split(",").filter(Boolean);
let save;
if (seed !== null) {
  const w = new World(Number(seed));
  while (!w.graduated && w.episode < 100000) w.step();   // test_brain.mjs allows 20,000 per stage
  if (!w.graduated) { console.error(`seed ${seed} did not graduate in 100,000 episodes`); process.exit(1); }
  save = JSON.parse(JSON.stringify(w));
} else {
  if (!args.length) { console.error("usage: node perform.mjs <save.json | --seed N> [skill ...] [--episodes N] [--greedy walk,write]"); process.exit(2); }
  save = JSON.parse(readFileSync(args.shift(), "utf8"));
}
GAINS.performGreedy = greedy;   // "any" picks greedy per scene from this list
for (const key of args.length ? args : STAGES.map(s => s.key)) {
  const w = World.fromJSON(save);
  w.perform(key);
  while (w.perf.n < (key === "any" ? episodes * STAGES.length : episodes)) w.step();
  if (key === "any") console.log(`any: a random scene per episode, ${w.perf.n} episodes, ${(w.perf.ok / w.perf.n).toFixed(2)} overall`);
  for (const k of STAGES.map(st => st.key).filter(k => w.perf.scene[k])) {
    const s = w.perf.scene[k];
    const top = s.slots.indexOf(Math.max(...s.slots)), share = s.slots[top] / s.slots.reduce((a, b) => a + b);
    console.log(`${(key === "any" ? "  " : "") + k.padEnd(6)} ${(s.ok / s.n).toFixed(2)} (slot ${top} on ${(100 * share).toFixed(0)}% of steps)${greedy.includes(k) ? "  (greedy)" : ""}`);
  }
}
