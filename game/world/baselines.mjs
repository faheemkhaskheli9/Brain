// Baselines for Brain World (issue #118), through the common interface in env.mjs: the same
// observations, action sets, rewards and time limits the creature gets, nothing privileged.
//   random     uniform over the allowed actions
//   heuristic  hand-written, from the observation only: turn toward the salience centroid on the
//              retina, grasp when an object fills the centre rays, and at the board draw two
//              different random strokes. Engineered assistance: it knows that objects are what to
//              grasp and that a letter has two different strokes, but not which colour or letter a
//              tone names, so on listen, read and write it is the "nearest object" / chance reference.
//   creature   the backprop-free creature: trains the curriculum (as test_brain.mjs), then is scored
//              in perform mode like the baselines. --creature to include it (minutes per seed).
// Every arm is scored per skill over the same number of episodes, counting environment steps.
// Run: node game/world/baselines.mjs [seeds, default 1-5] [--episodes N] [--creature] [--out FILE.json]
import { World, STAGES, GAINS, RAYS } from "./brain.js";
import { Env } from "./env.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

const LIMIT = 20000;   // training episodes per stage for the creature, as in test_brain.mjs
// GRASP: centre-ray brightness meaning "in reach". Tuned on seeds 101-103 (0.65, 0.7, 0.75 x
// centroid band 1-3; 0.75 and band 1 grasped every single object), never on the reported seeds.
const CENTRE = (RAYS - 1) / 2, PEN0 = RAYS * 3 + 30, GRASP = 0.75;

export const POLICIES = {
  random: (obs, allowed, R) => allowed[Math.floor(R() * allowed.length)],
  heuristic(obs, allowed, R) {
    if (allowed.includes(4)) {   // the habit set: push left (turns left), push right, grasp
      let w = 0, m = 0, top = 0;   // salience above the walls' 0.2 grey, its centroid, the centre rays' peak
      for (let i = 0; i < RAYS; i++) { const s = Math.max(obs[i * 3], obs[i * 3 + 1], obs[i * 3 + 2]) - 0.2; if (s > 0) { w += s; m += s * i; } }
      for (let i = CENTRE - 1; i <= CENTRE + 1; i++) top = Math.max(top, obs[i * 3], obs[i * 3 + 1], obs[i * 3 + 2]);
      if (top > GRASP) return 4;   // an object fills the centre: in reach
      if (w === 0) return 0;       // nothing in view: keep turning left to search
      const off = m / w - CENTRE;
      if (Math.abs(off) <= 1) return R() < 0.5 ? 0 : 1;   // ahead: walk on, alternating legs on average
      return off > 0 ? 0 : 1;      // rays past the middle look left; a left push turns left
    }
    const drawn = allowed.filter(a => obs[PEN0 + a - allowed[0]] > 0.5);   // the pen set: strokes already on the pad
    const free = allowed.filter(a => !drawn.includes(a));
    return free[Math.floor(R() * free.length)];
  },
};

// A fixed policy on one skill: success rate and environment steps over `episodes` episodes.
export function evaluate(policy, seed, skill, episodes) {
  const env = new Env(seed, skill);
  while (env.episodes < episodes) env.step(policy(env.obs, env.allowed, env.rand));
  return { success: env.successes / env.episodes, steps: env.steps };
}

// The creature: train the curriculum, then score each skill in perform mode (the save's scores),
// counting the training and evaluation steps.
function creature(seed, episodes) {
  const w = new World(seed);
  for (let s = 0; s < STAGES.length; s++) {
    const start = w.episode;
    while (w.stage === s && !w.graduated && w.episode - start < LIMIT) w.step();
    if (!(w.stage > s || w.graduated)) return { failed: STAGES[s].key, trainSteps: w.log.reduce((a, e) => a + e.steps, 0) };
  }
  const trainSteps = w.log.reduce((a, e) => a + e.steps, 0), out = {};
  const c = World.fromJSON(JSON.parse(JSON.stringify(w)));
  for (const { key } of STAGES) {
    c.perform(key);
    let steps = 0;
    while (c.perf.n < episodes) { c.step(); steps++; }
    out[key] = { success: c.perf.ok / c.perf.n, steps };
  }
  return { trainSteps, episodes: w.episode, skills: out };
}

if (process.argv[1] && import.meta.url.endsWith(process.argv[1].split("/").pop())) {
  const args = process.argv.slice(2), take = name => { const i = args.indexOf(name); return i < 0 ? null : args.splice(i, 2)[1]; };
  const out = take("--out"), episodes = Number(take("--episodes") ?? 300), withCreature = args.includes("--creature");
  const seeds = args.filter(a => /^\d+$/.test(a)).map(Number);
  if (!seeds.length) seeds.push(1, 2, 3, 4, 5);
  const runs = [], table = {};
  for (const seed of seeds) {
    for (const [arm, policy] of Object.entries(POLICIES)) for (const { key } of STAGES) {
      const t0 = Date.now(), r = evaluate(policy, seed, key, episodes);
      runs.push(run({ arm, seed, split: key, status: "ok", seconds: (Date.now() - t0) / 1000,
        scores: { success: r.success, evalSteps: r.steps, trainSteps: 0 } }));
      (table[arm] ??= {})[key] = [...(table[arm][key] ?? []), r.success];
    }
    if (withCreature) {
      const t0 = Date.now(), r = creature(seed, episodes), seconds = (Date.now() - t0) / 1000;
      for (const { key } of STAGES) {
        runs.push(run({ arm: "creature", seed, split: key, seconds, status: r.skills ? "ok" : "timeout",
          reason: r.skills ? null : `${r.failed} not learned within ${LIMIT} episodes`,
          scores: r.skills ? { success: r.skills[key].success, evalSteps: r.skills[key].steps, trainSteps: r.trainSteps } : { trainSteps: r.trainSteps } }));
        if (r.skills) (table.creature ??= {})[key] = [...(table.creature?.[key] ?? []), r.skills[key].success];
      }
    }
    console.error(`seed ${seed} done`);
  }
  const mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
  console.log(`success over ${episodes} episodes per skill, mean over seeds ${seeds.join(" ")} (perform mode, gait reflex on)`);
  console.log("arm".padEnd(10) + STAGES.map(s => s.key.padStart(8)).join(""));
  for (const [arm, t] of Object.entries(table)) console.log(arm.padEnd(10) + STAGES.map(s => (t[s.key] ? mean(t[s.key]).toFixed(2) : "-").padStart(8)).join(""));
  if (out) writeResult(out, resultRecord({ experiment: "brain-world/baselines", baseline: "random", runs,
    metrics: { success: "higher" },
    config: { arms: [...Object.keys(POLICIES), ...(withCreature ? ["creature"] : [])], seeds, mode: "perform, graduated (gait reflex on)",
      greedy: GAINS.performGreedy },
    budgets: { eval_episodes_per_skill: episodes, train_episodes_per_stage: withCreature ? LIMIT : 0 } }));
}
