// Surprise-based context (issue #65, item 1): can the brain tell two contexts apart when they look
// the same? A brain learns walk, grasp and listen. Then blocks of episodes alternate listen and
// "listen, reversed" (REVERSE: the same scene, but each tone names the next colour), with no
// rehearsal. Both produce the same scene summary, so the scene alone puts them in one slot and the
// actor must relearn at every switch. With GAINS.surprise on, a slot that stays surprised hands over
// to a look-alike slot, or founds one, so a context seen before can be picked up again.
// Run: node game/world/reversal.mjs [seeds, default 1-10] [--surprise X] [--block N] [--blocks N]
import { pathToFileURL } from "node:url";
import { World, STAGES, GAINS, REVERSE } from "./brain.js";

export const LIMIT = 20000;

// One run. Returns per block {key, ok (success rate), first (success over its first 50 episodes),
// slot (most used slot at episode end), share (of episodes there)}, or {failed} if listen was not learned.
export function reversal(seed, { surprise = 0, block = 300, blocks = 8 } = {}) {
  const keep = { surprise: GAINS.surprise, replay: GAINS.replay }, n0 = STAGES.length;
  GAINS.surprise = surprise;
  try {
    const w = new World(seed), listen = STAGES.findIndex(s => s.key === "listen");
    for (let s = 0; s <= listen; s++) {
      const start = w.episode;
      while (w.stage === s && w.episode - start < LIMIT) w.step();
      if (w.stage === s) return { seed, surprise, failed: STAGES[s].key };
    }
    STAGES.push({ ...REVERSE, pass: 2 });   // pass 2: a block never ends by passing
    w.windows.push([]);
    const pass = STAGES[listen].pass;
    STAGES[listen] = { ...STAGES[listen], pass: 2 };
    GAINS.replay = 0;
    const out = [];
    try {
      for (let k = 0; k < blocks; k++) {
        const idx = k % 2 ? listen : n0;   // reversed first: listen was just learned
        w.stage = w.playing = idx; w.reset();   // at an episode boundary: drops a fresh, unplayed episode
        const res = [], ends = Array(GAINS.slots).fill(0);
        while (res.length < block) {
          const slot = w.slot, r = w.step();
          if (r.done) { res.push(r.success ? 1 : 0); ends[slot]++; }
        }
        const top = ends.indexOf(Math.max(...ends)), mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
        out.push({ key: STAGES[idx].key, ok: +mean(res).toFixed(3), first: +mean(res.slice(0, 50)).toFixed(3), slot: top, share: +(ends[top] / block).toFixed(3) });
      }
    } finally { STAGES[listen] = { ...STAGES[listen], pass }; }
    return { seed, surprise, blocks: out, slotsUsed: Array.from(w.brain.uses).filter(u => u > 0).length };
  } finally { STAGES.length = n0; Object.assign(GAINS, keep); }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2), opt = (name, dflt) => { const i = args.indexOf(name); return i < 0 ? dflt : Number(args.splice(i, 2)[1]); };
  const surprise = opt("--surprise", 3), block = opt("--block", 300), blocks = opt("--blocks", 8);
  const seeds = args.length ? args.map(Number) : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  const rows = { off: [], on: [] };
  for (const seed of seeds) for (const [arm, x] of [["off", 0], ["on", surprise]]) {
    const r = reversal(seed, { surprise: x, block, blocks });
    rows[arm].push(r);
    console.log(JSON.stringify(r));
  }
  const mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
  console.log(`\nblocks of ${block}, reversed first; per block: success over the block (first 50 episodes) [slot share]`);
  for (const arm of ["off", "on"]) {
    const ok = rows[arm].filter(r => r.blocks);
    console.log(`surprise ${arm === "off" ? "off" : `x${surprise}`}, ${ok.length}/${rows[arm].length} learned listen: `
      + Array.from({ length: blocks }, (_, k) => `${ok[0] ? ok[0].blocks[k].key.slice(0, 3) : ""} ${mean(ok.map(r => r.blocks[k].ok)).toFixed(2)} (${mean(ok.map(r => r.blocks[k].first)).toFixed(2)})`).join(" | ")
      + `; slots used ${mean(ok.map(r => r.slotsUsed)).toFixed(1)}`);
  }
}
