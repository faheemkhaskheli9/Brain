// Score a saved brain with learning off: the success rate per skill. Never writes the save.
// Run: node game/world/perform.mjs <save.json | --seed N> [skill ...] [--episodes N] [--greedy walk,write]
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
for (const key of args.length ? args : STAGES.map(s => s.key)) {
  const w = World.fromJSON(save);
  w.perform(key, greedy.includes(key));
  while (w.perf.n < episodes) w.step();
  console.log(`${key.padEnd(6)} ${(w.perf.ok / w.perf.n).toFixed(2)}${greedy.includes(key) ? "  (greedy)" : ""}`);
}
