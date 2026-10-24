// Difficult fixed-room navigation (issue #108). A frozen suite of hard rooms: three objects (coloured
// balls for listen, lettered cubes for read), the target in a corner and at least one distractor
// near the straight line from the room's centre, where the creature starts, to the target. The
// suite is drawn once from fixed seeds and pinned by its hash (test_navigation.mjs), so it cannot
// drift while arms are compared. Two disjoint splits: "tune" (seeds 1000-1019) is the only one any
// change may be tuned on; "eval" (2000-2019) is unseen layouts, reported separately.
// Each arm trains the five-stage curriculum on the ordinary random rooms (same budget per arm), then
// plays every suite room with learning off (teach mode, World.teach(lesson, false)), as listen and
// as read, with each of the three tones. Per episode: success, wrong grasp, timeout, collisions
// (a push that moved less than half its stride: a wall or an object in the way) and a loop (the
// heading turned through a full circle or more, net).
// Arms: default; timeoutBootstrap (GAINS.timeoutBootstrap 2, #54); orient (GAINS.orient 1, #83).
// Run: node game/world/navigation.mjs [seeds, default 1-5] [--arms a,b] [--episodes N] [--out FILE.json]
// --out writes the shared result file (#104): python research/result_schema.py FILE.json
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import { World, STAGES, GAINS, ARENA, OBJ_R, rng } from "./brain.js";
import { resultRecord, run, writeResult } from "./result.mjs";

export const LIMIT = 20000;   // training episodes per stage, as in test_brain.mjs
export const SPLIT_SEEDS = { tune: range(1000, 20), eval: range(2000, 20) };
export const ARMS = { default: {}, timeoutBootstrap: { timeoutBootstrap: 2 }, orient: { orient: 1 } };
function range(a, n) { return Array.from({ length: n }, (_, i) => a + i); }

// One hard room from a suite seed: three object positions, target index 0 (its colour or letter is
// set per episode by the tone, so each room is played with every tone).
export function room(seed) {
  const R = rng(seed), c = ARENA / 2, corner = 1.2;
  for (;;) {
    const sx = R() < 0.5 ? 1 : -1, sy = R() < 0.5 ? 1 : -1;
    const t = [c + sx * (c - 0.6 - R() * (corner - 0.6)), c + sy * (c - 0.6 - R() * (corner - 0.6))];
    const pos = [t];
    for (let k = 0; pos.length < 3 && k < 200; k++) {
      const p = [0.8 + R() * (ARENA - 1.6), 0.8 + R() * (ARENA - 1.6)];
      if (Math.hypot(p[0] - c, p[1] - c) < 2 || pos.some(o => Math.hypot(o[0] - p[0], o[1] - p[1]) < 1.6)) continue;
      pos.push(p);
    }
    if (pos.length === 3 && pos.slice(1).some(p => lineDist(p, [c, c], t) < 1.5)) return pos.map(p => p.map(v => +v.toFixed(3)));
  }
}
function lineDist(p, a, b) {   // distance from p to the segment a-b
  const dx = b[0] - a[0], dy = b[1] - a[1], u = Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)));
  return Math.hypot(p[0] - a[0] - u * dx, p[1] - a[1] - u * dy);
}
export const suite = split => SPLIT_SEEDS[split].map(s => ({ seed: s, pos: room(s) }));
export const suiteHash = () => createHash("sha256").update(JSON.stringify([suite("tune"), suite("eval")])).digest("hex").slice(0, 16);

// Play one lesson for `episodes` episodes with learning off; collect the navigation measures.
function play(w, lesson, episodes) {
  w.teach(lesson, false);
  const out = { n: 0, ok: 0, wrong: 0, timeout: 0, collisions: 0, loops: 0, steps: 0 };
  let turn = 0;
  const advance = w.advance.bind(w);
  w.advance = (t, d) => { turn += t; const moved = advance(t, d); if (moved < d / 2) out.collisions++; return moved; };
  try {
    while (out.n < episodes) {
      const { done, success, reward } = w.step();
      out.steps++;
      if (!done) continue;
      out.n++; out.ok += success; out.loops += Math.abs(turn) >= 2 * Math.PI;
      if (!success) reward <= -GAINS.wrongCost ? out.wrong++ : out.timeout++;   // a wrong grasp's reward is -wrongCost
      turn = 0;
    }
  } finally { delete w.advance; }
  return out;
}

// Train the curriculum under the arm's GAINS, then score both suites. episodes: per room, mode and tone.
export function navigation(seed, arm, episodes = 5) {
  const keep = { ...GAINS }, t0 = Date.now();
  Object.assign(GAINS, ARMS[arm]);
  try {
    const w = new World(seed);
    for (let s = 0; s < STAGES.length; s++) {
      const start = w.episode;
      while (w.stage === s && !w.graduated && w.episode - start < LIMIT) w.step();
      if (!(w.stage > s || w.graduated)) return { seed, arm, failed: STAGES[s].key, trained: w.episode, seconds: (Date.now() - t0) / 1000 };
    }
    const res = { seed, arm, trained: w.episode, rooms: {} };
    for (const split of Object.keys(SPLIT_SEEDS)) {
      const tot = { n: 0, ok: 0, wrong: 0, timeout: 0, collisions: 0, loops: 0, steps: 0 };
      res.rooms[split] = [];
      for (const r of suite(split)) {
        let ok = 0, n = 0;
        for (const kind of ["color", "letter"]) for (let tone = 0; tone < 3; tone++) {
          // object 0 (the corner) carries the toned colour or letter, the others the remaining two
          const ids = [tone, (tone + 1) % 3, (tone + 2) % 3];
          const o = play(w, { objects: r.pos.map((pos, i) => ({ pos, [kind]: ids[i] })), tone }, episodes);
          for (const k in tot) tot[k] += o[k];
          ok += o.ok; n += o.n;
        }
        res.rooms[split].push({ seed: r.seed, success: ok / n });
      }
      res[split] = { success: tot.ok / tot.n, wrong: tot.wrong / tot.n, timeout: tot.timeout / tot.n,
        loops: tot.loops / tot.n, collisions: tot.collisions / tot.steps, steps: tot.steps / tot.n };
    }
    res.seconds = (Date.now() - t0) / 1000;
    return res;
  } finally { Object.assign(GAINS, keep); }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i < 0 ? d : args.splice(i, 2)[1]; };
  const out = opt("--out", null), arms = opt("--arms", Object.keys(ARMS).join(",")).split(","), episodes = +opt("--episodes", 5);
  for (const a of arms) if (!ARMS[a]) throw new Error(`unknown arm ${a}; valid: ${Object.keys(ARMS).join(", ")}`);
  const seeds = args.length ? args.map(Number) : [1, 2, 3, 4, 5], rows = [], f = x => x.toFixed(2);
  for (const seed of seeds) for (const arm of arms) {
    const r = navigation(seed, arm, episodes);
    rows.push(r);
    console.log(`seed ${seed} ${arm.padEnd(16)} ` + (r.failed ? `${r.failed} not learned` : Object.keys(SPLIT_SEEDS).map(s =>
      `${s}: success ${f(r[s].success)} wrong ${f(r[s].wrong)} timeout ${f(r[s].timeout)} loops ${f(r[s].loops)} collisions/step ${f(r[s].collisions)}`).join("; "))
      + `  (${r.seconds.toFixed(0)} s)`);
  }
  if (out) {
    const runs = rows.flatMap(r => Object.keys(SPLIT_SEEDS).map(split => r.failed
      ? run({ arm: r.arm, seed: r.seed, split, seconds: r.seconds, status: "failed", reason: `${r.failed} not learned within ${LIMIT} episodes`, scores: { trained: r.trained } })
      : run({ arm: r.arm, seed: r.seed, split, seconds: r.seconds, status: "ok",
        scores: { ...r[split], trained: r.trained, failingRooms: r.rooms[split].filter(x => x.success === 0).map(x => x.seed) } })));
    writeResult(out, resultRecord({ experiment: "brain-world/navigation", baseline: "default", runs,
      metrics: { success: "higher", wrong: "lower", timeout: "lower", loops: "lower", collisions: "lower", steps: "lower" },
      config: { seeds, arms: Object.fromEntries(arms.map(a => [a, ARMS[a]])), suite: { seeds: SPLIT_SEEDS, hash: suiteHash(),
        rule: "target in a corner (within 1.2 of both walls), a distractor within 1.5 of the centre-target line; listen and read, every tone" },
        gains: { ...GAINS } },
      budgets: { episodes_per_stage: LIMIT, episodes_per_room_mode_tone: episodes } }));
  }
}
