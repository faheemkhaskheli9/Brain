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
import { World, STAGES, GAINS, COPY, NEW, rng } from "./brain.js";

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
  // Issue #65: after graduation, blocks of listen and reversed listen, surprise off vs on (see reversal).
  reversal: { replay: 0.3, sleepEvery: 0, reversal: true },
  // Issue #37: after graduation, three new letters made of known strokes, against the same brain untrained (see transfer).
  transfer: { replay: 0.3, sleepEvery: 0, transfer: true },
  // Issue #65 item 3: a forward model (fm = its learning rate) whose squared error is a curiosity bonus.
  // The pilot's error was 0.017-0.043 per step on seed 1, so 0.05 pays under the 0.005 step cost on
  // average and 0.25 about twice it. reversalFm: curiosity 0, then the reversal blocks also run with the
  // forward model's error as the surprise signal (see reversal).
  curiosity05: { replay: 0.3, sleepEvery: 0, fm: 0.1, curiosity: 0.05 },
  curiosity25: { replay: 0.3, sleepEvery: 0, fm: 0.1, curiosity: 0.25 },
  reversalFm: { replay: 0.3, sleepEvery: 0, fm: 0.1, reversal: true },
  // Issue #94: the 15 x 5 ray grid retina instead of 15 rays.
  grid: { replay: 0.3, sleepEvery: 0, retina: "grid" },
  // Issue #65 item 4: features learned by competing hidden units (Krotov and Hopfield 2019) in a critical period
  // of `develop` free-play steps before the curriculum, then fixed: half the visual units (hebb), all of them
  // (hebbAll), half that keep learning all through training (hebbOnline), and half on the grid retina.
  // The pilot (seeds 1-2, feature statistics only) picked hebb 0.1 and 20,000 steps (README "Learned features").
  hebb: { replay: 0.3, sleepEvery: 0, hebb: 0.1, develop: 20000 },
  hebbAll: { replay: 0.3, sleepEvery: 0, hebb: 0.1, hebbShare: 1, develop: 20000 },
  hebbOnline: { replay: 0.3, sleepEvery: 0, hebb: 0.1, hebbOnline: true, develop: 20000 },
  "grid+hebb": { replay: 0.3, sleepEvery: 0, retina: "grid", hebb: 0.1, develop: 20000 },
};
const FACTORIAL = ["rehearse30", "orient", "sleepActor30", "orient+sleepActor30"];   // none, prior, rule, both
const LIMIT = 20000, KEEP = { grasp: 0.7, listen: 0.5, read: 0.4, write: 0.5 };   // as in test_brain.mjs

function trial(arm, seed) {
  const { copy, reversal: rev, transfer: tr, develop, ...gains } = ARMS[arm];
  Object.assign(GAINS, gains);
  const w = new World(seed), episodes = [], t0 = Date.now(), b = w.brain, commit = b.commit.bind(b), store = { reclaims: 0, merges: 0 };
  const birth = Float32Array.from(b.wIn);   // #65 item 4: how far the learned features end up from the random ones
  if (develop) w.develop(develop);
  // A commit with no matching and no free slot reclaims a rarely used one, or else merges into the nearest.
  b.commit = z => { const m = b.match(z); if (b.learning && m.best < 0 && m.free < 0) store[m.rare >= 0 ? "reclaims" : "merges"]++; commit(z); };
  // Per stage: the mean step-size multiplier 1 / (1 + mean |h|^2) over its training steps (#37 found it
  // confounds speed comparisons), and the forward model's mean squared error per step (#65 item 3).
  const scale = [], fmErr = [];
  for (let s = 0; s < STAGES.length; s++) {
    const start = w.episode, f0 = [b.fmSum || 0, b.fmN || 0];
    let sc = 0, n = 0;
    while (w.stage === s && !w.graduated && w.episode - start < LIMIT) { w.step(); sc += 1 / (1 + (b.hh || 0)); n++; }
    episodes.push(w.episode - start); scale.push(+(sc / n).toPrecision(4));
    if (b.fm) fmErr.push(+((b.fmSum - f0[0]) / (b.fmN - f0[1])).toPrecision(4));
    if (!(w.stage > s || w.graduated)) return { arm, seed, passed: false, failed: STAGES[s].key, episodes, scale };
  }
  // Its first letters (#37): episodes of the write stage itself, rehearsal not counted (nothing rehearses write before graduation).
  const writeOwn = w.log.filter(e => e.stage === STAGES.length - 1).length;
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
    active, scale, ...(b.fm && { fmErr }), ...(b.pools && { features: features(b, birth) }), slots, uses: Array.from(w.brain.uses), ...store, ...(copy && { copy: sixth(json) }), ...(rev && { reversal: reversal(json) }),
    ...(tr && { transfer: { writeOwn, ...transfer(json, seed) } }), seconds: (Date.now() - t0) / 1000 };
}

// Issue #65 item 4: the learning units, how many moved from their random birth weights, and the mean cosine
// between their drive weights at birth and at graduation.
function features(b, birth) {
  const units = b.pools.flat(), drive = (w, j) => Array.from(w.subarray(j * 8 + 3, j * 8 + 8));
  const cos = units.map(j => { const a = drive(birth, j), c = drive(b.wIn, j); return a.reduce((s, x, k) => s + x * c[k], 0) / Math.hypot(...a) / Math.hypot(...c); });
  return { units: units.length, changed: cos.filter(x => x < 0.999).length, cos: +(cos.reduce((s, x) => s + x, 0) / cos.length).toFixed(3) };
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

// Issue #65, phase C: from the graduated save, BLOCKS blocks of BLOCK listen episodes that alternate
// the normal and the reversed tone rule (same scene, so the scene cannot pick the slot), with no
// rehearsal and no stage passes. Run from the same save with surprise off and on (TD error), and, when
// the save has a forward model, "fm": surprise from its error (item 3). Per block: success in its first
// and last 50 episodes, the slot the last episode ended in, switches so far, and each episode's summed
// squared TD error and forward-model error (what the detector sees), averaged over the first and last 50.
const BLOCK = 1000, BLOCKS = 6, SURPRISE = 3;
function reversal(json) {
  const out = {}, listen = STAGES.findIndex(s => s.key === "listen");
  for (const [name, surprise, surpriseFm] of [["off", 0, false], ["on", SURPRISE, false], ...(GAINS.fm ? [["fm", SURPRISE, true]] : [])]) {
    Object.assign(GAINS, { replay: 0, surprise, surpriseFm });
    STAGES[listen].pass = Infinity;   // blocks are fixed length: listen never passes
    const w = World.fromJSON(JSON.parse(json)), b = w.brain, commit = b.commit.bind(b), err = [];
    b.commit = z => { err.push([b.epErr, b.fmEp]); commit(z); };
    w.graduated = false; w.setStage(listen);
    out[name] = [];
    for (let k = 0; k < BLOCKS; k++) {
      w.reversed = k % 2 === 1; w.reset();
      const wins = [], e0 = err.length;
      while (wins.length < BLOCK) { const r = w.step(); if (r.done) wins.push(r.success ? 1 : 0); }
      const rate = xs => +(xs.reduce((a, b) => a + b, 0) / xs.length).toFixed(3);
      const avg = (xs, j) => +(xs.reduce((a, x) => a + x[j], 0) / xs.length).toPrecision(4), f = err.slice(e0, e0 + 50), l = err.slice(-50);
      out[name].push({ first: rate(wins.slice(0, 50)), last: rate(wins.slice(-50)), slot: w.slot, switches: b.switches || 0,
        td: [avg(f, 0), avg(l, 0)], fmErr: [avg(f, 1), avg(l, 1)] });
    }
    out[name + "Switches"] = w.brain.switches || 0;
  }
  return out;
}

// Phase C per arm: mean first-50 and last-50 success per block, off vs on, and on minus off on the
// first 50 of the return blocks (2 onwards: a rule it has met before), paired by seed.
function reversalSummary(results) {
  // One summary per arm: reversal and reversalFm train different brains and record different modes.
  for (const arm of new Set(results.filter(r => r.reversal).map(r => r.arm))) reversalArm(results.filter(r => r.reversal && r.arm === arm), arm);
}

function reversalArm(rs, arm) {
  const mean = xs => xs.reduce((a, b) => a + b) / xs.length;
  console.log(`\nphase C, ${arm} (reversal blocks of ${BLOCK}, normal/reversed alternating, surprise ${SURPRISE}): first50/last50 per block, n ${rs.length}`);
  const names = ["off", "on", "fm"].filter(n => rs.every(r => r.reversal[n]));
  for (const name of names) {
    const blocks = rs[0].reversal[name], per = rs[0].reversal[name][0].switches !== undefined;   // older logs lack switches per block
    console.log(`  surprise ${name.padEnd(4)}` + blocks.map((_, k) =>
      `${k % 2 ? "R" : "N"} ${mean(rs.map(r => r.reversal[name][k].first)).toFixed(2)}/${mean(rs.map(r => r.reversal[name][k].last)).toFixed(2)}`).join("  ")
      + `  switches ${mean(rs.map(r => r.reversal[name + "Switches"])).toFixed(1)}`
      + (per ? ` (per block ${blocks.map((_, k) => mean(rs.map(r => r.reversal[name][k].switches - (k ? r.reversal[name][k - 1].switches : 0))).toFixed(1)).join(" ")})` : ""));
  }
  for (const name of names.slice(1)) {
    const d = rs.map(r => mean(r.reversal[name].slice(2).map((b, k) => b.first - r.reversal.off[k + 2].first)));
    console.log(`  ${name} - off, first 50 of blocks 3-${BLOCKS}: ${mean(d) > 0 ? "+" : ""}${mean(d).toFixed(3)} (p ${signFlip(d).toFixed(3)}, n ${d.length})`);
  }
  // Item 3: does a rule change show in the signal? Surprise off, each episode's summed squared error: first
  // 50 of a block minus last 50 of the block before, at the reversals (N to R) and at the returns (R to N).
  for (const [j, label] of [["td", "TD error"], ["fmErr", "forward-model error"]]) {
    if (!rs.every(r => r.reversal.off[0][j] && r.reversal.off[0][j][1] > 0)) continue;
    const off = r => r.reversal.off, jump = (r, ks) => mean(ks.map(k => off(r)[k][j][0] - off(r)[k - 1][j][1]));
    const ks = { "N to R": [1, 3, 5].filter(k => k < BLOCKS), "R to N": [2, 4].filter(k => k < BLOCKS) };
    console.log(`  ${label} per episode, surprise off, first50/last50: ` + off(rs[0]).map((_, k) =>
      `${k % 2 ? "R" : "N"} ${mean(rs.map(r => off(r)[k][j][0])).toPrecision(3)}/${mean(rs.map(r => off(r)[k][j][1])).toPrecision(3)}`).join("  "));
    console.log("    jump at block start (first 50 minus the block before's last 50): " + Object.entries(ks).map(([why, k]) => {
      const d = rs.map(r => jump(r, k));
      return `${why} ${mean(d) > 0 ? "+" : ""}${mean(d).toPrecision(3)} (p ${signFlip(d).toFixed(3)})`;
    }).join(", "));
  }
}

// Issue #37, phase T. Train w on its current stage until it passes or has played LIMIT episodes of that
// stage. own counts that stage's own episodes, not rehearsal, so brains with and without old skills compare.
function learnStage(w) {
  const s = w.stage;
  let own = 0;
  while (w.stage === s && !w.graduated && own < LIMIT) { const k = w.playing; if (w.step().done && k === s) own++; }
  return { learned: w.stage > s || w.graduated, own };
}

// From the graduated save, NEW as a sixth stage, 2 x 2: learned weights kept or zeroed (P and v set to 0,
// the control that cannot reuse what it learned) x rehearsal on (GAINS.replay) or off. All four share the
// wiring, gate rows, slots and random stream, so only what it learned and the rehearsal differ. Rehearsal
// matters on its own: the step size lr / (1 + mean |h|^2) then follows the room scenes, whose |h|^2 is
// smaller than the board's, so board updates take larger steps. Also the same seed untrained (new World,
// another gate row, rehearsal off), and COPY (T, L, X) then NEW: the same task on the letters it knows,
// then on new ones. zero = sampled perform-mode success before any training on that stage, 300 episodes.
function transfer(json, seed) {
  const replay = GAINS.replay, out = {}, load = () => World.fromJSON(JSON.parse(json));
  const zero = (w, key) => { const c = World.fromJSON(JSON.parse(JSON.stringify(w))); c.perform(key, false); while (c.perf.n < 300) c.step(); return +(c.perf.ok / c.perf.n).toFixed(3); };
  const quiet = w => { GAINS.replay = 0; const r = learnStage(w); GAINS.replay = replay; return r; };
  const zeroed = w => { w.brain.P.fill(0); w.brain.v.fill(0); return w; };
  STAGES.push(NEW);
  const g = load(), fresh = new World(seed);
  fresh.setStage(STAGES.length - 1);
  Object.assign(out, { zeroNew: zero(g, "new"), gradNew: learnStage(g), zeroedNew: learnStage(zeroed(load())),
    gradNew0: quiet(load()), zeroedNew0: quiet(zeroed(load())), freshNew: quiet(fresh) });
  STAGES.pop(); STAGES.push(COPY, NEW);
  const c = load();
  Object.assign(out, { zeroCopy: zero(c, "copy"), gradCopy: learnStage(c) });
  if (out.gradCopy.learned) Object.assign(out, { zeroNewAfterCopy: zero(c, "new"), copyThenNew: learnStage(c) });
  STAGES.splice(-2);
  return out;
}

// Phase T per seed and overall: episodes of each stage itself, mean and median over the seeds that learned
// it, and paired differences over the seeds that learned both (positive = the second is faster): mean,
// 95% bootstrap interval of the mean, exact sign-flip p.
function transferSummary(results) {
  const rs = results.filter(r => r.transfer).map(r => ({ seed: r.seed, ...r.transfer }));
  if (!rs.length) return;
  const mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
  const median = xs => { const s = [...xs].sort((a, b) => a - b), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
  const own = (r, k) => k === "writeOwn" ? r.writeOwn : r[k] && r[k].learned ? r[k].own : null;
  const ROWS = { writeOwn: "write T, L, X by tone (its first letters)", gradNew: "new letters: graduated", zeroedNew: "new letters: weights zeroed",
    gradNew0: "new letters: graduated, no rehearsal", zeroedNew0: "new letters: zeroed, no rehearsal", freshNew: "new letters: untrained, no rehearsal",
    gradCopy: "copy T, L, X: graduated", copyThenNew: "new letters after copy T, L, X" };
  console.log(`\nphase T (new letters Γ ⊥ 7, #37): episodes of the stage itself, n ${rs.length}; a seed that missed either stage of a pair drops out of it`);
  for (const r of rs) console.log(`  seed ${String(r.seed).padStart(2)}: ${Object.keys(ROWS).map(k => `${k} ${own(r, k) ?? "-"}`).join(", ")}`
    + `; zero-shot new ${r.zeroNew}, copy ${r.zeroCopy}, new after copy ${r.zeroNewAfterCopy ?? "-"}`);
  for (const [k, name] of Object.entries(ROWS)) {
    const xs = rs.map(r => own(r, k)).filter(x => x !== null);
    console.log(`  ${name.padEnd(44)}learned ${xs.length}/${rs.length}  mean ${mean(xs).toFixed(0)}  median ${median(xs).toFixed(0)}`);
  }
  const z = k => mean(rs.filter(r => r[k] !== undefined).map(r => r[k])).toFixed(3);
  console.log(`  zero-shot (sampled; uniform strokes score 1/18 = 0.056): new ${z("zeroNew")}, copy ${z("zeroCopy")}, new after copy ${z("zeroNewAfterCopy")}`);
  for (const [a, b, why] of [["zeroedNew", "gradNew", "what it learned, with rehearsal"], ["zeroedNew0", "gradNew0", "what it learned, no rehearsal"],
    ["gradNew0", "gradNew", "rehearsal, graduated"], ["zeroedNew0", "zeroedNew", "rehearsal, zeroed"],
    ["freshNew", "gradNew", "untrained vs graduated (the plan before the run)"], ["writeOwn", "gradNew", "new letters vs its first letters"],
    ["gradCopy", "copyThenNew", "same task, new letters after old vs old"], ["gradNew", "copyThenNew", "copying old letters first"],
    ["gradNew", "gradCopy", "letters it knows vs new ones, same brain"]]) {
    const d = rs.filter(r => own(r, a) !== null && own(r, b) !== null).map(r => own(r, a) - own(r, b));
    if (d.length < 2) continue;
    const [lo, hi] = bootCI(d);
    console.log(`  ${`${a} - ${b}`.padEnd(24)}${mean(d) > 0 ? "+" : ""}${mean(d).toFixed(0)} [${lo.toFixed(0)}, ${hi.toFixed(0)}] p ${signFlip(d).toFixed(3)}, n ${d.length}  (${why})`);
  }
}

// Percentile bootstrap 95% interval of the mean, 10,000 resamples, seeded so a rerun prints the same.
function bootCI(d) {
  const r = rng(37), m = Array.from({ length: 10000 }, () => d.reduce(s => s + d[Math.floor(r() * d.length)], 0) / d.length).sort((a, b) => a - b);
  return [m[250], m[9749]];
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
    const ft = ok.filter(r => r.features);
    if (ft.length) line += `  features moved ${mean(ft.map(r => r.features.changed)).toFixed(0)}/${mean(ft.map(r => r.features.units)).toFixed(0)}, cos to birth ${mean(ft.map(r => r.features.cos)).toFixed(2)}`;
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
  reversalSummary(results);
  transferSummary(results);
  stageSummary(results, arms);
}

// Issue #65 item 3: per stage, paired against the first arm over the seeds both passed: episodes, the kept
// scores, and the step-size multiplier 1 / (1 + mean |h|^2) (as arm / first arm). Then the forward model's
// mean squared error per step, per stage. Rows from before #65 item 3 have no scale and are skipped.
function stageSummary(results, arms) {
  const mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length, sg = x => (x > 0 ? "+" : "");
  const base = Object.fromEntries(results.filter(r => r.arm === arms[0] && r.passed && r.scale).map(r => [r.seed, r]));
  const lines = [];
  for (const arm of arms.slice(1)) {
    const rs = results.filter(r => r.arm === arm && r.passed && r.scale && base[r.seed]);
    if (rs.length < 2) continue;
    const B = r => base[r.seed], pair = f => { const d = rs.map(r => f(r) - f(B(r))); return `${sg(mean(d))}${mean(d).toFixed(Math.abs(mean(d)) < 1 ? 3 : 0)} (p ${signFlip(d).toFixed(3)})`; };
    lines.push(`${arm.padEnd(24)}n ${rs.length}  episodes ${STAGES.map((s, i) => `${s.key} ${pair(r => r.episodes[i])}`).join(", ")}, all ${pair(r => r.total)}`);
    lines.push(" ".repeat(24) + `kept ${Object.keys(KEEP).map(k => `${k} ${pair(r => r.kept[k])}`).join(", ")}`);
    lines.push(" ".repeat(24) + `step scale x ${STAGES.map((s, i) => `${s.key} ${(mean(rs.map(r => r.scale[i])) / mean(rs.map(r => B(r).scale[i]))).toFixed(3)}`).join(", ")}`
      + ` (p ${STAGES.map((s, i) => signFlip(rs.map(r => r.scale[i] - B(r).scale[i])).toFixed(3)).join("/")})`);
  }
  if (lines.length) console.log(`\nper stage vs ${arms[0]} (paired, seeds both passed; step scale = 1 / (1 + mean |h|^2), arm / ${arms[0]})\n` + lines.join("\n"));
  for (const arm of arms) {
    const rs = results.filter(r => r.arm === arm && r.passed && r.fmErr);
    if (rs.length) console.log(`${arm.padEnd(24)}forward-model error per step: ${STAGES.map((s, i) => `${s.key} ${mean(rs.map(r => r.fmErr[i])).toFixed(4)}`).join(", ")}, n ${rs.length}`);
  }
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
