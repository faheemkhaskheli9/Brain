// Compare ways of keeping old skills across seeds: live rehearsal of old tasks vs offline sleep
// replay from the episodic store (issue #64). Each arm x seed trains the full curriculum in its own
// process, as test_brain.mjs does, then scores the skills it kept over 4,000 graduated episodes.
// Run: node game/world/sweep.mjs [seeds, default 1-10] [--arms A,B,...] [--jobs N] > sweep.log
//      node game/world/sweep.mjs --from sweep.log    (summarise a saved run again, no training)
import { fork } from "node:child_process";
import { readFileSync } from "node:fs";
import { availableParallelism } from "node:os";
import { fileURLToPath } from "node:url";
import { World, STAGES, GAINS } from "./brain.js";

export const ARMS = {
  rehearse30: { replay: 0.3, sleepEvery: 0 },                           // the current design; the baseline
  "rehearse10+sleep": { replay: 0.1, sleepEvery: 20 },                  // sleep replays the critic only
  "rehearse0+sleep": { replay: 0, sleepEvery: 20 },
  "rehearse10+sleepActor": { replay: 0.1, sleepEvery: 20, sleepActor: true },
  "rehearse0+sleepActor": { replay: 0, sleepEvery: 20, sleepActor: true },
};
const LIMIT = 20000, KEEP = { grasp: 0.7, listen: 0.5, read: 0.4, write: 0.5 };   // as in test_brain.mjs

function trial(arm, seed) {
  Object.assign(GAINS, ARMS[arm]);
  const w = new World(seed), episodes = [], t0 = Date.now();
  for (let s = 0; s < STAGES.length; s++) {
    const start = w.episode;
    while (w.stage === s && !w.graduated && w.episode - start < LIMIT) w.step();
    episodes.push(w.episode - start);
    if (!(w.stage > s || w.graduated)) return { arm, seed, passed: false, failed: STAGES[s].key, episodes };
  }
  const ok = {}, n = {}, start = w.episode;
  while (w.episode - start < 4000) {
    const k = STAGES[w.playing].key, r = w.step();
    if (r.done) { ok[k] = (ok[k] || 0) + r.success; n[k] = (n[k] || 0) + 1; }
  }
  const kept = Object.fromEntries(Object.keys(KEEP).map(k => [k, +(ok[k] / n[k]).toFixed(3)]));
  return { arm, seed, passed: true, episodes, total: episodes.reduce((a, b) => a + b), kept, seconds: (Date.now() - t0) / 1000 };
}

// Exact paired sign-flip test: two-sided p for the mean per-seed difference (2^n flips, n <= ~16).
function signFlip(diffs) {
  const n = diffs.length, obs = Math.abs(diffs.reduce((a, b) => a + b, 0));
  let hits = 0;
  for (let m = 0; m < 1 << n; m++) {
    let s = 0;
    for (let i = 0; i < n; i++) s += m >> i & 1 ? -diffs[i] : diffs[i];
    if (Math.abs(s) >= obs - 1e-9) hits++;
  }
  return hits / (1 << n);
}

function summarise(results, arms) {
  const mean = xs => xs.length ? xs.reduce((a, b) => a + b) / xs.length : NaN, f = (x, w) => x.toFixed(0).padStart(w);
  const base = Object.fromEntries(results.filter(r => r.arm === arms[0] && r.passed).map(r => [r.seed, r]));
  console.log(`\n${"arm".padEnd(24)}passed  kept>=bars  write eps  all eps  ${Object.keys(KEEP).map(k => k.padStart(6)).join(" ")}   vs ${arms[0]} (paired, seeds both passed)`);
  for (const arm of arms) {
    const rs = results.filter(r => r.arm === arm), ok = rs.filter(r => r.passed);
    const bars = ok.filter(r => Object.entries(KEEP).every(([k, v]) => r.kept[k] >= v)).length;
    let line = `${arm.padEnd(24)}${`${ok.length}/${rs.length}`.padStart(6)}  ${`${bars}/${rs.length}`.padStart(9)}  ${f(mean(ok.map(r => r.episodes[4])), 9)}  ${f(mean(ok.map(r => r.total)), 7)}  `
      + Object.keys(KEEP).map(k => mean(ok.map(r => r.kept[k])).toFixed(2).padStart(6)).join(" ");
    const pairs = ok.filter(r => base[r.seed]);
    if (arm !== arms[0] && pairs.length) {
      const dt = pairs.map(r => r.total - base[r.seed].total), dw = pairs.map(r => r.episodes[4] - base[r.seed].episodes[4]);
      line += `   all ${mean(dt) > 0 ? "+" : ""}${mean(dt).toFixed(0)} (p ${signFlip(dt).toFixed(3)}), write ${mean(dw) > 0 ? "+" : ""}${mean(dw).toFixed(0)} (p ${signFlip(dw).toFixed(3)}), n ${pairs.length}`;
    }
    console.log(line);
  }
}

if (process.send) {   // child: run one trial and report it
  process.on("message", ({ arm, seed }) => { process.send(trial(arm, seed)); process.exit(0); });
} else {
  const args = process.argv.slice(2), opt = (name, dflt) => {
    const i = args.indexOf(name);
    return i < 0 ? dflt : args.splice(i, 2)[1];
  };
  const from = opt("--from", null);
  const arms = opt("--arms", Object.keys(ARMS).join(",")).split(",");
  const nJobs = Number(opt("--jobs", Math.max(1, availableParallelism() - 2)));   // each job needs ~100 MB
  const seeds = args.length ? args.map(Number) : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  const bad = arms.find(a => !ARMS[a]) || (!(Number.isInteger(nJobs) && nJobs > 0) && `--jobs ${nJobs}`)
    || (seeds.some(s => !Number.isInteger(s)) && `seeds ${args.join(" ")}`);
  if (bad) { console.error(`bad argument: ${bad}; arms: ${Object.keys(ARMS).join(", ")}`); process.exit(2); }
  if (from) {
    const results = readFileSync(from, "utf8").split("\n").filter(l => l.startsWith("{")).map(l => JSON.parse(l));
    summarise(results, arms.filter(a => results.some(r => r.arm === a)));
  } else {
    const jobs = arms.flatMap(arm => seeds.map(seed => ({ arm, seed }))), results = [];
    const runOne = job => new Promise(done => {
      const child = fork(fileURLToPath(import.meta.url));
      let got = false;
      child.on("message", r => { got = true; results.push(r); console.log(JSON.stringify(r)); });
      child.on("exit", code => {   // a crashed run counts as a failure, never drops out of the count
        if (!got) { const r = { ...job, passed: false, error: `exit ${code}` }; results.push(r); console.log(JSON.stringify(r)); }
        done();
      });
      child.send(job);
    });
    await Promise.all(Array.from({ length: nJobs }, async () => { while (jobs.length) await runOne(jobs.shift()); }));
    summarise(results, arms);
    if (results.some(r => r.error)) process.exit(1);
  }
}
