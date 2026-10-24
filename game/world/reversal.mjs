// Surprise-based context (issue #65, item 1; benchmark #106): can the brain tell two contexts apart
// when they look the same? A brain learns walk, grasp and listen. Then blocks of episodes alternate
// listen and "listen, reversed" (REVERSE: the same scene, but each tone names the next colour).
// Both produce the same scene summary, so the scene alone puts them in one slot and the actor must
// relearn at every switch. With GAINS.surprise on, a slot that stays surprised hands over to a
// look-alike slot, or founds one, so a context seen before can be picked up again.
// Arms (#106) ablate surprise, rehearsal replay during the blocks, and free context slots (slots3:
// walk, grasp and listen fill all three, so the reversed rule finds none free). Every arm gets the
// same episode budgets.
// Run: node game/world/reversal.mjs [seeds, default 1-10] [--arms off,surprise,...] [--surprise X]
//        [--block N] [--blocks N] [--out FILE.json]
// --out writes the shared result file (#104): python research/result_schema.py FILE.json
import { pathToFileURL } from "node:url";
import { World, STAGES, GAINS, REVERSE } from "./brain.js";
import { resultRecord, run, writeResult } from "./result.mjs";

export const LIMIT = 20000, WINDOW = 20, LATE = 50;
// surprise: true uses the --surprise threshold; replay: rehearsal share during the blocks; slots: GAINS.slots.
export const ARMS = {
  off: { surprise: false, replay: 0 },
  surprise: { surprise: true, replay: 0 },
  "surprise+replay": { surprise: true, replay: 0.3 },
  "off+replay": { surprise: false, replay: 0.3 },
  "surprise+slots3": { surprise: true, replay: 0, slots: 3 },
};

// One run. Returns per block {key, ok (success rate), first (success over its first 50 episodes),
// adapt (episodes until the last WINDOW reach the stage's pass mark, null if never), switches (slot
// changes between consecutive episodes), late (those after episode LATE, when the context has not
// changed: false switches), slot (most used slot at episode end), share (of episodes there)},
// or {failed} if listen was not learned.
export function reversal(seed, { surprise = 0, block = 300, blocks = 8, replay = 0, slots = GAINS.slots } = {}) {
  const keep = { surprise: GAINS.surprise, replay: GAINS.replay, slots: GAINS.slots }, n0 = STAGES.length;
  GAINS.surprise = surprise; GAINS.slots = slots;
  try {
    const w = new World(seed), listen = STAGES.findIndex(s => s.key === "listen");
    for (let s = 0; s <= listen; s++) {
      const start = w.episode;
      while (w.stage === s && w.episode - start < LIMIT) w.step();
      if (w.stage === s) return { seed, surprise, failed: STAGES[s].key, episodes: w.episode };
    }
    const learnedAt = w.episode;
    STAGES.push({ ...REVERSE, pass: 2 });   // pass 2: a block never ends by passing
    w.windows.push([]);
    const pass = STAGES[listen].pass, mark = REVERSE.pass;   // listen and reverse share the pass mark 0.7
    STAGES[listen] = { ...STAGES[listen], pass: 2 };
    GAINS.replay = replay;   // replay rehearses walk and grasp; listen and reverse are the blocks themselves
    const out = [];
    try {
      for (let k = 0; k < blocks; k++) {
        const idx = k % 2 ? listen : n0;   // reversed first: listen was just learned
        w.stage = w.playing = idx; w.reset();   // at an episode boundary: drops a fresh, unplayed episode
        const res = [], ends = Array(GAINS.slots).fill(0);
        let adapt = null, switches = 0, late = 0, last = -1;
        while (res.length < block) {
          const playing = w.playing, slot = w.slot, r = w.step();
          if (!r.done || playing !== idx) continue;   // rehearsal episodes of other skills are not scored
          res.push(r.success ? 1 : 0); ends[slot]++;
          if (last >= 0 && slot !== last) { switches++; if (res.length > LATE) late++; }
          last = slot;
          if (adapt === null && res.length >= WINDOW && res.slice(-WINDOW).reduce((a, b) => a + b) / WINDOW >= mark) adapt = res.length;
        }
        const top = ends.indexOf(Math.max(...ends)), mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
        out.push({ key: STAGES[idx].key, n: res.length, ok: +mean(res).toFixed(3), first: +mean(res.slice(0, LATE)).toFixed(3), adapt, switches, late,
          slot: top, share: +(ends[top] / block).toFixed(3) });
      }
    } finally { STAGES[listen] = { ...STAGES[listen], pass }; }
    return { seed, surprise, learnedAt, blocks: out, slotsUsed: Array.from(w.brain.uses).filter(u => u > 0).length };
  } finally { STAGES.length = n0; Object.assign(GAINS, keep); }
}

// Per-run scores for the result file. Blocks alternate reverse, listen, reverse, ...: blocks 0 and 1
// meet each rule for the first time, blocks 2 on return to a rule seen before.
export function scores(r) {
  const mean = xs => xs.length ? +(xs.reduce((a, b) => a + b, 0) / xs.length).toFixed(3) : null, ret = r.blocks.slice(2);
  const ad = bs => mean(bs.map(b => b.adapt ?? b.n));   // a block that never reached the mark counts as its whole length
  return {
    acquisition: r.learnedAt,                                          // episodes to learn walk, grasp, listen
    ok: mean(r.blocks.map(b => b.ok)),
    returnFirst: mean(ret.map(b => b.first)),                          // success on first 50 episodes back in a known rule
    retention: mean(ret.filter(b => b.key === "listen").map(b => b.first)),   // listen, after reversed blocks
    adaptFirst: ad(r.blocks.slice(0, 1)), adaptReturn: ad(ret),        // episodes to the pass mark, censored at the block length
    adapted: mean(r.blocks.map(b => b.adapt !== null ? 1 : 0)),        // share of blocks that reached the mark
    falseSwitches: mean(r.blocks.map(b => b.late)),
    detected: mean(r.blocks.slice(1).map(b => b.switches > 0 ? 1 : 0)),   // a slot change in a block after a rule change
    slotsUsed: r.slotsUsed, blocks: r.blocks,
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2), take = name => { const i = args.indexOf(name); return i < 0 ? null : args.splice(i, 2)[1]; };
  const num = (name, dflt) => { const v = take(name); return v === null ? dflt : Number(v); };
  const out = take("--out"), arms = (take("--arms") ?? "off,surprise").split(",");
  const surprise = num("--surprise", 3), block = num("--block", 300), blocks = num("--blocks", 8);
  const seeds = args.length ? args.map(Number) : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  const bad = arms.find(a => !ARMS[a]) || (seeds.some(s => !Number.isInteger(s)) && `seeds ${args.join(" ")}`);
  if (bad) { console.error(`bad argument: ${bad}; arms: ${Object.keys(ARMS).join(", ")}`); process.exit(2); }
  const opts = a => ({ surprise: ARMS[a].surprise ? surprise : 0, replay: ARMS[a].replay, slots: ARMS[a].slots ?? GAINS.slots, block, blocks });
  const rows = Object.fromEntries(arms.map(a => [a, []]));
  for (const seed of seeds) for (const arm of arms) {
    const t0 = Date.now(), r = { arm, ...reversal(seed, opts(arm)), seconds: (Date.now() - t0) / 1000 };
    rows[arm].push(r);
    console.log(JSON.stringify(r));
  }
  const mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
  console.log(`\nblocks of ${block}, reversed first; per block: success over the block (first ${LATE} episodes) {episodes to adapt, false switches}`);
  for (const arm of arms) {
    const ok = rows[arm].filter(r => r.blocks);
    console.log(`${arm} (surprise ${opts(arm).surprise}, replay ${opts(arm).replay}, slots ${opts(arm).slots}), ${ok.length}/${rows[arm].length} learned listen: `
      + Array.from({ length: blocks }, (_, k) => `${ok[0] ? ok[0].blocks[k].key.slice(0, 3) : ""} ${mean(ok.map(r => r.blocks[k].ok)).toFixed(2)}`
        + ` (${mean(ok.map(r => r.blocks[k].first)).toFixed(2)}) {${ok.filter(r => r.blocks[k].adapt !== null).length}/${ok.length}, ${mean(ok.map(r => r.blocks[k].late)).toFixed(1)}}`).join(" | ")
      + `; slots used ${mean(ok.map(r => r.slotsUsed)).toFixed(1)}`);
  }
  if (out) {
    const runs = arms.flatMap(arm => rows[arm].map(r => run({
      arm, seed: r.seed, seconds: r.seconds, status: r.blocks ? "ok" : "timeout",
      reason: r.blocks ? null : `${r.failed} not learned within ${LIMIT} episodes`, scores: r.blocks ? scores(r) : { acquisition: r.episodes },
    })));
    writeResult(out, resultRecord({ experiment: "brain-world/reversal", baseline: arms[0], runs,
      metrics: { ok: "higher", returnFirst: "higher", adaptReturn: "lower", retention: "higher", adapted: "higher", falseSwitches: "lower", detected: "higher" },
      config: { arms: Object.fromEntries(arms.map(a => [a, opts(a)])), seeds, window: WINDOW, late: LATE, passMark: REVERSE.pass, gains: { ...GAINS } },
      budgets: { episodes_per_stage: LIMIT, episodes_per_block: block, blocks } }));
  }
}
