// Frozen, paired-scene intervention on Brain World's historical stage-dependent gait.
// Compare one trained checkpoint with and without the automatic gait/action-set scaffold.
// This is a *dependence diagnostic*, not proof that either arm can learn from scratch.
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { World } from "./brain.js";
import { resultRecord, run, writeResult } from "./result.mjs";

export const SCAFFOLDS = Object.freeze(["curriculum", "unscaffolded"]);
export const SKILLS = Object.freeze(["grasp", "listen", "read", "write"]);

function digest(brain) {
  const h = createHash("sha256");
  for (const arr of [brain.P, brain.v, brain.wIn, brain.bias, brain.gate, brain.proto]) {
    h.update(Buffer.from(arr.buffer, arr.byteOffset, arr.byteLength));
  }
  return h.digest("hex");
}

function sceneSeed(seed, skillIndex, episode) {
  return (Math.imul(seed, 0x9e3779b1) ^ Math.imul(skillIndex + 1, 0x85ebca6b)
    ^ Math.imul(episode + 1, 0xc2b2ae35)) >>> 0;
}

export function evaluateCheckpoint(checkpoint, scaffold, seed, episodes = 30, skills = SKILLS) {
  if (!SCAFFOLDS.includes(scaffold)) throw new Error("unknown scaffold arm");
  if (!Number.isSafeInteger(seed) || seed < 0 || !Number.isInteger(episodes) || episodes < 1
    || !skills.length || skills.some(k => !SKILLS.includes(k)) || new Set(skills).size !== skills.length)
    throw new Error("invalid paired-scene evaluation settings");
  const w = World.fromJSON(checkpoint);
  w.scaffold = scaffold;  // the sole intervention; same trained parameters in both arms
  const weights = digest(w.brain);
  const scenes = createHash("sha256");
  const scores = {};
  let decisions = 0;
  for (const skill of skills) {
    w.perform(skill); // disables learning; does not change the trained policy weights
    let wins = 0;
    const skillIndex = SKILLS.indexOf(skill);
    for (let i = 0; i < episodes; i++) {
      // Reset RNG BEFORE constructing each scene, independent of prior action counts.
      w.rand.state = sceneSeed(seed, skillIndex, i);
      w.reset();
      scenes.update(JSON.stringify([skill, i, w.pos, w.heading, w.objects, w.target,
        w.tone, w.shown, w.board]));
      let outcome;
      do {
        outcome = w.step();
        decisions++;
      } while (!outcome.done);
      wins += Number(outcome.success);
    }
    scores[skill] = wins / episodes;
  }
  if (digest(w.brain) !== weights) throw new Error("frozen evaluation modified policy weights");
  const mean = skills.reduce((sum, k) => sum + scores[k], 0) / skills.length;
  return { scores: { ...scores, mean }, decisions, episodes: skills.length * episodes,
    sceneHash: scenes.digest("hex") };
}

export function pairedSeed(checkpoint, seed, episodes = 30, skills = SKILLS) {
  const rows = [], hashes = {};
  for (const scaffold of SCAFFOLDS) {
    const start = Date.now();
    const score = evaluateCheckpoint(checkpoint, scaffold, seed, episodes, skills);
    hashes[scaffold] = score.sceneHash;
    rows.push(run({ arm: scaffold, seed, split: "frozen-paired-scenes", status: "ok",
      seconds: (Date.now() - start) / 1000, scores: { ...score.scores,
        decisions: score.decisions, episodes: score.episodes } }));
  }
  if (hashes.curriculum !== hashes.unscaffolded)
    throw new Error("paired arms were not evaluated on the same initial scenes");
  return { rows, sceneHash: hashes.curriculum };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  const option = (flag, fallback) => {
    const idx = args.indexOf(flag);
    return idx < 0 ? fallback : args.splice(idx, 2)[1];
  };
  const path = option("--checkpoint", null), out = option("--out", null);
  const episodes = Number(option("--episodes", "30"));
  const seeds = args.length ? args.map(Number) : [1, 2, 3];
  if (!path || !out || !seeds.length || seeds.some(s => !Number.isSafeInteger(s) || s < 0)
      || new Set(seeds).size !== seeds.length || !Number.isInteger(episodes) || episodes < 1)
    throw new Error("usage: node game/world/scaffold_eval.mjs --checkpoint SAVE.json --out RESULT.json --episodes 30 [seed ...]");
  const raw = readFileSync(path), checkpoint = JSON.parse(raw.toString("utf8"));
  const trained = World.fromJSON(checkpoint).graduated;
  if (!trained) throw new Error("checkpoint has not graduated: paired evaluation requires a trained creature");
  const comparisons = seeds.map(seed => pairedSeed(checkpoint, seed, episodes));
  const runs = comparisons.flatMap(c => c.rows);
  const config = { seeds, episodes, skills: SKILLS, arms: SCAFFOLDS,
    sceneHashes: Object.fromEntries(seeds.map((seed, i) => [seed, comparisons[i].sceneHash])),
    checkpointSha256: createHash("sha256").update(raw).digest("hex"),
    intervention: "post-training action/gait scaffold only; both arms keep the board/pen shortcut",
    caveat: "Frozen checkpoint dependency, not a from-scratch training comparison; all training costs must be reported separately" };
  writeResult(out, resultRecord({ experiment: "brain-world/scaffold-dependence",
    baseline: "curriculum", config, budgets: { evalEpisodesPerSkill: episodes,
      trainingDecisions: "unknown (supplied external checkpoint)" },
    metrics: Object.fromEntries([...SKILLS, "mean", "decisions"].map(k =>
      [k, k === "decisions" ? "lower" : "higher"])), runs }));
  console.log("scaffold dependence: frozen paired scenes; checkpoint trained =", trained);
  for (const arm of SCAFFOLDS) {
    const subset = runs.filter(r => r.arm === arm);
    const avg = subset.reduce((n, r) => n + r.scores.mean, 0) / subset.length;
    console.log(arm, "mean success", avg.toFixed(3), "seeds", subset.length);
  }
}
