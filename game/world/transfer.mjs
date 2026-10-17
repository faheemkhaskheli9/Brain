// Learning to learn (issue #37): are new letters made of known strokes learned faster by a brain that
// has already learned to copy T, L and X than by a naive one? Per seed, two brains from the same seed:
//   experienced: learn COPY (T, L, X), then NEW_LETTERS (Γ, ⊥, 7);
//   naive:       learn NEW_LETTERS from scratch.
// Both at the board only, no rehearsal (GAINS.replay = 0), so the only difference is what it learned first.
// Run: node game/world/transfer.mjs [seeds, default 1-10]
import { pathToFileURL } from "node:url";
import { World, STAGES, GAINS, COPY, NEW_LETTERS } from "./brain.js";

export const LIMIT = 20000;   // episodes per stage, as in test_brain.mjs

// Per stage from `first` on: episodes to pass it (null = not within LIMIT) and the success rate over its
// first 100 episodes (the head start). STAGES and GAINS are restored.
function learn(seed, first, stages) {
  const n0 = STAGES.length, replay = GAINS.replay;
  STAGES.push(...stages);
  GAINS.replay = 0;
  try {
    const w = new World(seed), out = [];
    w.setStage(n0 + first);
    for (let s = n0 + first; s < STAGES.length; s++) {
      const start = w.episode;
      while (w.stage === s && !w.graduated && w.episode - start < LIMIT) w.step();
      const early = w.log.slice(start, start + 100).reduce((a, e) => a + e.success, 0) / 100;
      out.push({ episodes: w.stage > s || w.graduated ? w.episode - start : null, early });
      if (out.at(-1).episodes === null) break;
    }
    return out;
  } finally { STAGES.length = n0; GAINS.replay = replay; }
}

export function transfer(seed) {
  const [copy, after] = learn(seed, 0, [COPY, NEW_LETTERS]), [naive] = learn(seed, 0, [NEW_LETTERS]);
  return { seed, copy: copy.episodes, after: after ? after.episodes : null, naive: naive.episodes,
    early: { copy: copy.early, after: after ? after.early : null, naive: naive.early } };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const seeds = process.argv.length > 2 ? process.argv.slice(2).map(Number) : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  const rows = [];
  for (const seed of seeds) {
    const r = transfer(seed);
    rows.push(r);
    const e = k => r.early[k] === null ? "-" : r.early[k].toFixed(2);
    console.log(`seed ${String(seed).padStart(2)}: copy T/L/X ${r.copy ?? "not learned"}, then new letters ${r.after ?? "not learned"}; naive new letters ${r.naive ?? "not learned"}`
      + `   (first 100 episodes: ${e("copy")} / ${e("after")} / ${e("naive")})`);
  }
  const ok = rows.filter(r => r.after !== null && r.naive !== null), mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
  if (ok.length) {
    const d = ok.map(r => r.after - r.naive);
    console.log(`mean over ${ok.length} seeds: first letters ${mean(rows.filter(r => r.copy !== null).map(r => r.copy)).toFixed(0)}, new letters after them ${mean(ok.map(r => r.after)).toFixed(0)}, naive ${mean(ok.map(r => r.naive)).toFixed(0)};`
      + ` experienced faster on ${d.filter(x => x < 0).length}/${ok.length}, paired sign-flip p ${signFlip(d).toFixed(3)};`
      + ` first-100 success after ${mean(ok.map(r => r.early.after)).toFixed(2)} vs naive ${mean(ok.map(r => r.early.naive)).toFixed(2)}`);
  }
}

// Exact paired sign-flip test, as in sweep.mjs: two-sided p for the mean difference.
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
