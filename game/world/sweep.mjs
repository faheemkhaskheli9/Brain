// Compare ways of keeping old skills across seeds: live rehearsal of old tasks vs offline sleep
// replay from the episodic store (issue #64). Each arm x seed trains the full curriculum in its own
// process, as test_brain.mjs does, then scores the skills it kept over 4,000 graduated episodes,
// and saves and reloads it: each row carries the save's perform-mode scores and git commit.
// Run: node game/world/sweep.mjs [seeds, default 1-10] [--arms A,B,...] [--jobs N] > sweep.log
//      node game/world/sweep.mjs --from sweep.log    (summarise a saved run again, no training)
import { execSync, fork } from "node:child_process";
import { readFileSync } from "node:fs";
import { availableParallelism } from "node:os";
import { fileURLToPath } from "node:url";
import { World, STAGES, GAINS, COPY } from "./brain.js";

export const ARMS = {
  rehearse30: { replay: 0.3, sleepEvery: 0 },                           // the current design; the baseline
  "rehearse10+sleep": { replay: 0.1, sleepEvery: 20 },                  // sleep replays the critic only
  "rehearse0+sleep": { replay: 0, sleepEvery: 20 },
  "rehearse10+sleepActor": { replay: 0.1, sleepEvery: 20, sleepActor: true },
  "rehearse0+sleepActor": { replay: 0, sleepEvery: 20, sleepActor: true },
  // Issue #82: k-winners-take-all on the 1,000 hidden units, on top of the baseline.
  kwta20: { replay: 0.3, sleepEvery: 0, kwta: 20 },
  kwta35: { replay: 0.3, sleepEvery: 0, kwta: 35 },
  kwta50: { replay: 0.3, sleepEvery: 0, kwta: 50 },
  // Issue #54: at grasp/listen/read timeouts, sense and discard (RNG control) vs bootstrap from there.
  timeoutSense: { replay: 0.3, sleepEvery: 0, timeoutBootstrap: 1 },
  timeoutBootstrap: { replay: 0.3, sleepEvery: 0, timeoutBootstrap: 2 },
  // Issue #83, a 2x2 with rehearse30: innate orienting reflex x actor sleep replay (rehearsal kept at 30%).
  orient: { replay: 0.3, sleepEvery: 0, orient: 1 },
  sleepActor30: { replay: 0.3, sleepEvery: 20, sleepActor: true },
  "orient+sleepActor30": { replay: 0.3, sleepEvery: 20, sleepActor: true, orient: 1 },
  // Issue #56: synaptic intelligence (si) on top of rehearsal, then a sixth skill (copy) learned after
  // a save and load. copy: true runs phase B (see sixth). The number after "si" is GAINS.si.
  copy: { replay: 0.3, sleepEvery: 0, copy: true },
  // Pilot, seeds 1-2: si 1e-3 failed listen on one seed, 1e-2 to 10 on both (a * Omega is about 1,
  // so si is the pull per step). The run uses 1e-4.
  "copy+si": { replay: 0.3, sleepEvery: 0, si: 1e-4, copy: true },
  copy15: { replay: 0.15, sleepEvery: 0, copy: true },
  "copy15+si": { replay: 0.15, sleepEvery: 0, si: 1e-4, copy: true },
  // Issue #38: torque-driven jointed legs (World.limbs) instead of discrete leg states.
  joints: { replay: 0.3, sleepEvery: 0, joints: true },
};
const FACTORIAL = ["rehearse30", "orient", "sleepActor30", "orient+sleepActor30"];   // none, prior, rule, both
const LIMIT = 20000, KEEP = { grasp: 0.7, listen: 0.5, read: 0.4, write: 0.5 };   // as in test_brain.mjs

function trial(arm, seed) {
  const { copy, ...gains } = ARMS[arm];
  Object.assign(GAINS, gains);
  const w = new World(seed), episodes = [], t0 = Date.now(), b = w.brain, commit = b.commit.bind(b), store = { reclaims: 0, merges: 0 };
  // A commit with no matching and no free slot reclaims a rarely used one, or else merges into the nearest.
  b.commit = (z, slot) => { const m = b.match(z); if (b.learning && m.best < 0 && m.free < 0) store[m.rare >= 0 ? "reclaims" : "merges"]++; commit(z, slot); };
  for (let s = 0; s < STAGES.length; s++) {
    const start = w.episode;
    while (w.stage === s && !w.graduated && w.episode - start < LIMIT) w.step();
    episodes.push(w.episode - start);
    if (!(w.stage > s || w.graduated)) return { arm, seed, passed: false, failed: STAGES[s].key, episodes };
  }
  const ok = {}, n = {}, steps = {}, eps = {}, start = w.episode, hist = () => Array(GAINS.slots).fill(0);
  while (w.episode - start < 4000) {
    const k = STAGES[w.playing].key, slot = w.slot, r = w.step();
    (steps[k] ??= hist())[slot]++;
    if (r.done) { ok[k] = (ok[k] || 0) + r.success; n[k] = (n[k] || 0) + 1; (eps[k] ??= hist())[slot]++; }
  }
  const kept = Object.fromEntries(Object.keys(KEEP).map(k => [k, +(ok[k] / n[k]).toFixed(3)]));
  const active = +(w.brain.nActive / w.brain.nEncode).toFixed(1);   // mean hidden units on per step
  // Context slots (#60): per skill its most used slot, with the share of episodes (label purity)
  // and of steps on it; and every slot's use count at the end.
  const share = (h, c) => +(h[c] / h.reduce((a, b) => a + b, 0)).toFixed(3);
  const slots = Object.fromEntries(Object.keys(KEEP).map(k => {
    const c = eps[k].indexOf(Math.max(...eps[k]));
    return [k, { slot: c, episodes: share(eps[k], c), steps: share(steps[k], c) }];
  }));
  // Each graduated brain goes through a real save and load (#55); its perform-mode scores are the
  // ones the save's model card records.
  try { w.meta.commit = execSync("git rev-parse --short HEAD", { stdio: ["ignore", "pipe", "ignore"] }).toString().trim(); } catch {}
  const json = w.save(), card = World.fromJSON(JSON.parse(json)).meta;
  return { arm, seed, passed: true, episodes, total: episodes.reduce((a, b) => a + b), kept, perform: card.saves[0].scores, commit: card.commit,
    active, slots, uses: Array.from(w.brain.uses), ...store, ...(copy && { copy: sixth(json) }), seconds: (Date.now() - t0) / 1000 };
}

// Issue #56, phase B: load the graduated save into six-stage code (growStages resumes it at copy),
// score the old skills in perform mode, learn copy for up to LIMIT episodes, and score them again.
function sixth(json) {
  STAGES.push(COPY);
  const w = World.fromJSON(JSON.parse(json)), before = w.scores(300), usesBefore = Array.from(w.brain.uses), start = w.episode;
  const ends = Array(GAINS.slots).fill(0);   // the slot each copy episode ended in
  while (!w.graduated && w.episode - start < LIMIT) {
    const k = STAGES[w.playing].key, slot = w.slot;
    if (w.step().done && k === "copy") ends[slot]++;
  }
  const c = ends.indexOf(Math.max(...ends));
  return { learned: w.graduated, episodes: w.episode - start, before, after: w.scores(300), slot: c,
    share: +(ends[c] / ends.reduce((a, b) => a + b)).toFixed(3), founded: usesBefore[c] === 0, slotsUsed: w.brain.uses.filter(u => u > 0).length };
}

// Phase B per arm: copy learned, its episodes, own slot, and how much the old skills fell (perform
// mode, before minus after copy). Paired against the first copy arm on the mean drop.
function copySummary(results, arms) {
  const mean = xs => xs.length ? xs.reduce((a, b) => a + b) / xs.length : NaN, OLD = Object.keys(KEEP);
  const drop = r => mean(OLD.map(k => r.copy.before[k] - r.copy.after[k]));
  const cs = arms.filter(a => results.some(r => r.arm === a && r.copy));
  if (!cs.length) return;
  const base = Object.fromEntries(results.filter(r => r.arm === cs[0] && r.copy).map(r => [r.seed, r]));
  console.log(`\nphase B (copy after load): ${OLD.join("/")} before -> after, perform mode, 300 episodes each`);
  for (const arm of cs) {
    const rs = results.filter(r => r.arm === arm && r.copy), ok = rs.filter(r => r.copy.learned);
    let line = `${arm.padEnd(24)}copy ${ok.length}/${rs.length} in ${mean(ok.map(r => r.copy.episodes)).toFixed(0)} eps, own slot ${rs.filter(r => r.copy.founded).length}/${rs.length}`
      + ` (share ${mean(rs.map(r => r.copy.share)).toFixed(2)}), slots used ${mean(rs.map(r => r.copy.slotsUsed)).toFixed(1)}  `
      + OLD.map(k => `${mean(rs.map(r => r.copy.before[k])).toFixed(2)}->${mean(rs.map(r => r.copy.after[k])).toFixed(2)}`).join(" ")
      + `  drop ${mean(rs.map(drop)).toFixed(3)}`;
    const pairs = rs.filter(r => base[r.seed]);
    if (arm !== cs[0] && pairs.length) {
      const d = pairs.map(r => drop(r) - drop(base[r.seed]));
      line += `  vs ${cs[0]} ${mean(d) > 0 ? "+" : ""}${mean(d).toFixed(3)} (p ${signFlip(d).toFixed(3)}, n ${pairs.length})`;
    }
    console.log(line);
  }
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
      + Object.keys(KEEP).map(k => mean(ok.map(r => r.kept[k])).toFixed(2).padStart(6)).join(" ")
      + `  active ${mean(ok.map(r => r.active)).toFixed(0)}`;
    const pf = ok.filter(r => r.perform);
    if (pf.length) line += `  perform ${STAGES.map(s => mean(pf.map(r => r.perform[s.key])).toFixed(2)).join("/")}`;
    const pairs = ok.filter(r => base[r.seed]);
    if (arm !== arms[0] && pairs.length) {
      const dt = pairs.map(r => r.total - base[r.seed].total), dw = pairs.map(r => r.episodes[4] - base[r.seed].episodes[4]);
      line += `   all ${mean(dt) > 0 ? "+" : ""}${mean(dt).toFixed(0)} (p ${signFlip(dt).toFixed(3)}), write ${mean(dw) > 0 ? "+" : ""}${mean(dw).toFixed(0)} (p ${signFlip(dw).toFixed(3)}), n ${pairs.length}`;
    }
    console.log(line);
    const sl = ok.filter(r => r.slots);
    if (sl.length) console.log(" ".repeat(24) + "slots: " + Object.keys(KEEP).map(k =>
      `${k} episodes ${mean(sl.map(r => r.slots[k].episodes)).toFixed(3)} steps ${mean(sl.map(r => r.slots[k].steps)).toFixed(2)}`).join(", ")
      + `, distinct ${sl.filter(r => new Set(Object.values(r.slots).map(s => s.slot)).size === 4).length}/${sl.length}`);
    // Per seed (#63): the slots in use with their use counts, each skill's step share, reclaims and merges.
    for (const r of sl) console.log(" ".repeat(26) + `seed ${String(r.seed).padStart(2)}: uses ${r.uses.map((u, c) => u && `${c}:${u}`).filter(Boolean).join(" ")}`
      + ` | steps ${Object.keys(KEEP).map(k => `${k} ${r.slots[k].steps.toFixed(2)}`).join(" ")}`
      + (r.reclaims === undefined ? "" : ` | reclaims ${r.reclaims}, merges ${r.merges}`));
  }
  if (FACTORIAL.every(a => arms.includes(a))) factorial(results);
  copySummary(results, arms);
}

// Issue #83: main effects and interaction on episodes per stage, over seeds that passed in all four
// cells. Negative = fewer episodes. 95% t interval (needs n >= 2) and the exact sign-flip p.
function factorial(results) {
  const T95 = [NaN, 12.71, 4.30, 3.18, 2.78, 2.57, 2.45, 2.36, 2.31, 2.26, 2.23, 2.20, 2.18, 2.16, 2.14, 2.13];   // by df
  const cell = a => Object.fromEntries(results.filter(r => r.arm === a && r.passed).map(r => [r.seed, r]));
  const [n0, p, r, pr] = FACTORIAL.map(cell), seeds = Object.keys(n0).filter(s => p[s] && r[s] && pr[s]);
  console.log(`\n2x2 (prior = orient, rule = sleepActor30), seeds passed in all four: ${seeds.length}`);
  if (seeds.length < 2) return;
  const cols = [...STAGES.map((st, i) => [st.key, x => x.episodes[i]]), ["all", x => x.total]];
  const effects = {
    prior: (s, f) => (f(p[s]) - f(n0[s]) + f(pr[s]) - f(r[s])) / 2,
    rule: (s, f) => (f(r[s]) - f(n0[s]) + f(pr[s]) - f(p[s])) / 2,
    interaction: (s, f) => f(pr[s]) - f(r[s]) - (f(p[s]) - f(n0[s])),
  };
  for (const [name, eff] of Object.entries(effects)) {
    console.log(name.padEnd(12) + cols.map(([k, f]) => {
      const d = seeds.map(s => eff(s, f)), n = d.length, m = d.reduce((a, b) => a + b) / n;
      // ponytail: normal 1.96 past df 15 (t is 2.04-2.12 up to df 30, so intervals run a little narrow there)
      const ci = (T95[n - 1] ?? 1.96) * Math.sqrt(d.reduce((a, x) => a + (x - m) ** 2, 0) / (n - 1) / n);
      return `${k} ${m.toFixed(0)} [${(m - ci).toFixed(0)}, ${(m + ci).toFixed(0)}] p ${signFlip(d).toFixed(3)}`;
    }).join(" | "));
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
