// Held-out generalization and transfer (issue #105). Splits are fixed here, before any run, and
// nothing is tuned on them. Three axes, each disjoint by construction and asserted:
//   layout  the quadrant of the room the target object stands in: train {0, 1} (y < 4), dev {2},
//           eval {3}. All training uses train rooms; grasp, listen and read are scored frozen on each.
//   tone    the tone-to-colour mapping: trained on listen (tone t names colour t), evaluated on
//           "listen, reversed" (tone t names colour t + 1), which differs on every tone.
//   glyph   the letters: copy is trained on T, L and X, evaluated on Γ, ⊥ and 7 (new stroke pairs
//           made of strokes the first three use).
// Per seed, two arms:
//   pretrained  learns the five-stage curriculum on train rooms (and copy, for the glyph axis), then
//               for each new task: frozen score (learning off: zero-shot transfer), then ADAPT
//               episodes of training on it with no rehearsal (bounded adaptation), then frozen scores
//               of the new task and of the skill it came from (forgetting = before - after).
//   scratch     a fresh brain of the same seed, ADAPT episodes on the new task, then a frozen score.
// Every frozen score checks that the brain, its episodic store and its curriculum did not change.
// Run: node game/world/heldout.mjs [seeds, default 1-10] [--adapt N] [--episodes N] [--out FILE.json]
// --out writes the shared result file (#104): python research/result_schema.py FILE.json
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import { World, STAGES, GAINS, ARENA, LETTERS, COPY, NEW_LETTERS, REVERSE } from "./brain.js";
import { resultRecord, run, writeResult } from "./result.mjs";

export const LIMIT = 20000;   // training episodes per stage, as in test_brain.mjs
export const QUADRANT = p => (p[0] >= ARENA / 2 ? 1 : 0) + (p[1] >= ARENA / 2 ? 2 : 0);
export const SPLITS = { train: [0, 1], dev: [2], eval: [3] };
export const TONE_MAP = { train: t => t, eval: t => (t + 1) % 3 };   // tone -> colour; REVERSE is the eval map
export const GLYPHS = { train: [0, 1, 2], eval: [3, 4, 5] };          // LETTERS indices: COPY and NEW_LETTERS
const inSplit = name => p => SPLITS[name].includes(QUADRANT(p));

// The splits are disjoint: no quadrant, tone mapping or stroke pair in two of them. Throws if not.
export function assertDisjoint() {
  const q = Object.values(SPLITS).flat();
  if (new Set(q).size !== q.length) throw new Error(`layout splits overlap: ${JSON.stringify(SPLITS)}`);
  for (let t = 0; t < 3; t++) if (TONE_MAP.train(t) === TONE_MAP.eval(t)) throw new Error(`tone ${t} maps alike in train and eval`);
  if (REVERSE.key !== "reverse") throw new Error("the tone eval split is REVERSE");
  const pair = i => [...LETTERS[i][1]].sort().join(), train = new Set(GLYPHS.train.map(pair));
  if (GLYPHS.eval.some(i => train.has(pair(i)))) throw new Error("an eval letter has a train letter's strokes");
}

// Everything learning may change: weights, slots, the episodic store and the curriculum.
function fingerprint(w) {
  const o = w.toJSON();
  return createHash("sha256").update(JSON.stringify([o.brain, o.windows, o.episode, w.log.length, w.hippo.n, w.hippo.head])).digest("hex");
}

// Success over `episodes` episodes of skill `key` with learning off, on rooms of `split` (null: any).
// Throws if the world learned anything or a room left the split.
export function frozen(w, key, episodes, split = "train") {
  const before = fingerprint(w), keep = w.roomFilter;
  w.roomFilter = split && inSplit(split);
  try {
    w.perform(key);
    let n = -1;
    while (w.perf.n < episodes) {
      if (w.perf.n !== n) {
        n = w.perf.n;
        if (w.roomFilter && w.objects.length && !w.roomFilter(w.objects[w.target].pos)) throw new Error(`a ${key} room left the ${split} split`);
      }
      w.step();
    }
    const score = w.perf.ok / w.perf.n;
    w.perform(null);
    if (fingerprint(w) !== before) throw new Error(`frozen ${key} changed the brain`);
    return score;
  } finally { w.roomFilter = keep; }
}

// Train stage index s until it passes (null if not within LIMIT) or, with pass 2, for exactly n episodes.
function train(w, s, n = LIMIT) {
  w.graduated = false; w.setStage(s);
  const start = w.episode;
  while ((w.stage === s && !w.graduated) && w.episode - start < n) w.step();
  return w.stage > s || w.graduated ? w.episode - start : null;
}

const clone = w => { const c = World.fromJSON(JSON.parse(JSON.stringify(w))); c.roomFilter = w.roomFilter; return c; };

// Run fn with extra stages appended (as `pass` 2 they never pass) and GAINS overrides; both restored.
function withStages(stages, gains, fn) {
  const n0 = STAGES.length, keep = Object.fromEntries(Object.keys(gains).map(k => [k, GAINS[k]]));
  STAGES.push(...stages); Object.assign(GAINS, gains);
  try { return fn(n0); } finally { STAGES.length = n0; Object.assign(GAINS, keep); }
}

// A new task learned for exactly `adapt` episodes, no rehearsal, by w (null: a fresh brain of
// `seed`). before/after: frozen scores on the task (for a fresh brain, before is chance); source, if given, is the skill it came from,
// scored frozen after adaptation (w is changed in place).
function adapt(w, seed, task, adaptN, episodes, source = null, sourceSplit = "train") {
  return withStages([{ ...task, pass: 2 }], { replay: 0 }, n0 => {
    const fresh = !w;
    if (fresh) { w = new World(seed); w.roomFilter = inSplit("train"); }
    w.windows.length = n0; w.windows.push([]);
    const before = frozen(w, task.key, episodes);
    train(w, n0, adaptN);
    const after = frozen(w, task.key, episodes);
    w.stage = w.playing = n0 - 1; w.graduated = true;   // back on the curriculum's last stage
    return { before, after, sourceAfter: source && frozen(w, source, episodes, sourceSplit) };
  });
}

export function heldout(seed, { adapt: adaptN = 2000, episodes = 300 } = {}) {
  assertDisjoint();
  const t0 = Date.now(), w = new World(seed);
  w.roomFilter = inSplit("train");
  let pretrain = 0;
  for (let s = 0; s < STAGES.length; s++) {
    const n = train(w, s);
    if (n === null) return { seed, failed: STAGES[s].key, pretrain: w.episode, seconds: (Date.now() - t0) / 1000 };
    pretrain += n;
  }
  w.stage = STAGES.length - 1; w.graduated = true;
  const layout = {};
  for (const key of ["grasp", "listen", "read"])
    layout[key] = Object.fromEntries(Object.keys(SPLITS).map(sp => [sp, frozen(w, key, episodes, sp)]));
  layout.write = { train: frozen(w, "write", episodes, null) };

  // Tone: listen -> reversed listen.
  const listenBefore = frozen(w, "listen", episodes);
  const tone = adapt(clone(w), seed, REVERSE, adaptN, episodes, "listen");
  const toneScratch = adapt(null, seed, REVERSE, adaptN, episodes);

  // Glyph: copy T, L, X -> copy new letters.
  let glyph = null, copyAt = null;
  const gw = clone(w);
  withStages([COPY], {}, n0 => {
    gw.windows.length = n0; gw.windows.push([]);
    copyAt = train(gw, n0);
    if (copyAt === null) return;
    const copyBefore = frozen(gw, "copy", episodes, null);
    const g = adapt(gw, seed, NEW_LETTERS, adaptN, episodes, "copy", null);
    glyph = { before: g.before, after: g.after, copyBefore, copyAfter: g.sourceAfter };
  });
  const glyphScratch = adapt(null, seed, NEW_LETTERS, adaptN, episodes);
  return { seed, pretrain, copyAt, layout, seconds: (Date.now() - t0) / 1000,
    tone: { before: tone.before, after: tone.after, scratch: toneScratch, sourceBefore: listenBefore, sourceAfter: tone.sourceAfter },
    glyph, glyphScratch };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i < 0 ? d : args.splice(i, 2)[1]; };
  const out = opt("--out", null), adaptN = +opt("--adapt", 2000), episodes = +opt("--episodes", 300);
  const seeds = args.length ? args.map(Number) : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  const rows = [], f = x => x === null || x === undefined ? "-" : x.toFixed(2);
  for (const seed of seeds) {
    const r = heldout(seed, { adapt: adaptN, episodes });
    rows.push(r);
    if (r.failed) { console.log(`seed ${seed}: ${r.failed} not learned`); continue; }
    const L = r.layout;
    console.log(`seed ${String(seed).padStart(2)}: layout train/dev/eval grasp ${f(L.grasp.train)}/${f(L.grasp.dev)}/${f(L.grasp.eval)}`
      + ` listen ${f(L.listen.train)}/${f(L.listen.dev)}/${f(L.listen.eval)} read ${f(L.read.train)}/${f(L.read.dev)}/${f(L.read.eval)};`
      + ` tone 0-shot ${f(r.tone.before)} adapted ${f(r.tone.after)} scratch ${f(r.tone.scratch.after)} listen ${f(r.tone.sourceBefore)}->${f(r.tone.sourceAfter)};`
      + ` glyph ${r.glyph ? `0-shot ${f(r.glyph.before)} adapted ${f(r.glyph.after)} copy ${f(r.glyph.copyBefore)}->${f(r.glyph.copyAfter)}` : "copy not learned"} scratch ${f(r.glyphScratch.after)}`
      + `  (${r.seconds.toFixed(0)} s)`);
  }
  if (out) {
    const runs = rows.flatMap(r => {
      if (r.failed) return [run({ arm: "pretrained", seed: r.seed, seconds: r.seconds, status: "failed",
        reason: `${r.failed} not learned within ${LIMIT} episodes`, scores: { pretrain: null } })];
      const L = r.layout, g = r.glyph;
      return [
        run({ arm: "pretrained", seed: r.seed, seconds: r.seconds, status: g ? "ok" : "timeout",
          reason: g ? null : `copy not learned within ${LIMIT} episodes`,
          scores: { pretrain: r.pretrain, copyPretrain: r.copyAt, layout: L,
            gap: Object.fromEntries(["grasp", "listen", "read"].map(k => [k, L[k].eval - L[k].train])),
            tone: { zeroShot: r.tone.before, adapted: r.tone.after, forgetting: r.tone.sourceBefore - r.tone.sourceAfter,
              listenBefore: r.tone.sourceBefore, listenAfter: r.tone.sourceAfter, episodes: r.pretrain + adaptN },
            glyph: g ? { zeroShot: g.before, adapted: g.after, forgetting: g.copyBefore - g.copyAfter,
              copyBefore: g.copyBefore, copyAfter: g.copyAfter, episodes: r.pretrain + r.copyAt + adaptN } : null } }),
        run({ arm: "scratch", seed: r.seed, seconds: null, status: "ok",
          scores: { gap: { grasp: null, listen: null, read: null },
            tone: { zeroShot: r.tone.scratch.before, adapted: r.tone.scratch.after, forgetting: null, episodes: adaptN },
            glyph: { zeroShot: r.glyphScratch.before, adapted: r.glyphScratch.after, forgetting: null, episodes: adaptN } } }),
      ];
    });
    writeResult(out, resultRecord({ experiment: "brain-world/heldout", baseline: "scratch", runs,
      metrics: { "tone.adapted": "higher", "glyph.adapted": "higher", "tone.zeroShot": "higher", "glyph.zeroShot": "higher",
        "tone.forgetting": "lower", "glyph.forgetting": "lower", "gap.grasp": "higher", "gap.listen": "higher", "gap.read": "higher" },
      config: { seeds, splits: { layout: SPLITS, quadrant: "x >= 4 adds 1, y >= 4 adds 2 (target object)",
        tone: { train: "listen: tone t -> colour t", eval: "reverse: tone t -> colour t+1" },
        glyph: { train: GLYPHS.train.map(i => LETTERS[i][0]), eval: GLYPHS.eval.map(i => LETTERS[i][0]) } },
        adaptation: "no rehearsal (replay 0), learning on, a fixed number of episodes", gains: { ...GAINS } },
      budgets: { episodes_per_stage: LIMIT, adapt_episodes: adaptN, eval_episodes: episodes } }));
  }
}
