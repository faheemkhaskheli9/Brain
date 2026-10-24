// A conventional deep-RL baseline for Brain World (issue #118): an actor-critic MLP trained by
// backprop through env.mjs, so it gets the creature's observations, action sets, rewards and time
// limits and nothing more. It is the comparator, not the creature: the creature stays backprop-free.
//   network   obs (107) -> HID tanh units -> a softmax over the allowed actions and a value
//   update    after every episode: Monte Carlo returns, advantage = return - value, policy gradient
//             with an entropy bonus plus a squared value loss, one Adam step (Mnih et al. 2016 is
//             the n-step form of the same estimator; Kingma and Ba 2015 for Adam)
//   budget    a fresh network per skill, BUDGET environment steps of training each, so its five
//             skills together use about as many steps as the creature's whole curriculum (median
//             637,000, README "Baselines"). A network per skill is easier than the creature's task:
//             the creature learns all five in one brain and is never told which one it is doing.
//   scoring   learning off, in perform mode like every other arm, taking the most likely action on
//             the skills where the creature does (GAINS.performGreedy) and sampling on the searches.
// LR and ENT were tuned on seeds 101-103 (README "Baselines"), never on the reported seeds.
// Run: node game/world/rl.mjs [seeds, default 1-5] [--budget STEPS] [--episodes N] [--out FILE.json]
import { STAGES, GAINS, BODY, PEN, rng } from "./brain.js";
import { Env } from "./env.mjs";
import { resultRecord, run, writeResult } from "./result.mjs";

export const HP = { HID: 64, LR: 3e-3, ENT: 0.03, GAMMA: 0.99, BUDGET: 125000 };
const N_ACT = BODY.length + PEN.length;

export class ActorCritic {
  constructor(nIn, seed, hp = HP) {
    const R = rng(seed), H = hp.HID, init = (n, s) => Float64Array.from({ length: n }, () => (R() * 2 - 1) * s);
    this.hp = hp; this.nIn = nIn;
    // parameters in one array, so Adam runs over a single buffer: W1 (H x nIn), b1, Wp (A x H), bp, Wv (H), bv
    this.sizes = [H * nIn, H, N_ACT * H, N_ACT, H, 1];
    this.theta = new Float64Array(this.sizes.reduce((a, b) => a + b));
    const off = []; this.sizes.reduce((o, n) => (off.push(o), o + n), 0);
    [this.oW1, this.ob1, this.oWp, this.obp, this.oWv, this.obv] = off;
    this.theta.set(init(H * nIn, 1 / Math.sqrt(nIn)), this.oW1);
    this.theta.set(init(N_ACT * H, 0.01), this.oWp);
    this.grad = new Float64Array(this.theta.length);
    this.m = new Float64Array(this.theta.length); this.v = new Float64Array(this.theta.length); this.t = 0;
    this.rand = R;
  }
  // Hidden activity, the allowed actions' probabilities and the value of one observation.
  forward(x, allowed) {
    const { HID: H } = this.hp, th = this.theta, h = new Float64Array(H);
    for (let j = 0; j < H; j++) {
      let s = th[this.ob1 + j];
      const row = this.oW1 + j * this.nIn;
      for (let i = 0; i < this.nIn; i++) s += th[row + i] * x[i];
      h[j] = Math.tanh(s);
    }
    const logits = allowed.map(a => { let s = th[this.obp + a]; for (let j = 0; j < H; j++) s += th[this.oWp + a * H + j] * h[j]; return s; });
    const top = Math.max(...logits), e = logits.map(l => Math.exp(l - top)), z = e.reduce((a, b) => a + b);
    let v = th[this.obv];
    for (let j = 0; j < H; j++) v += th[this.oWv + j] * h[j];
    return { h, p: e.map(q => q / z), v };
  }
  act(x, allowed, greedy) {
    const f = this.forward(x, allowed);
    let k = 0;
    if (greedy) { for (let i = 1; i < f.p.length; i++) if (f.p[i] > f.p[k]) k = i; }
    else { let u = this.rand(); while (k < f.p.length - 1 && (u -= f.p[k]) > 0) k++; }
    return { k, f };
  }
  // One Adam step on an episode: steps hold { x, allowed, k, f, r }.
  learn(steps) {
    const { HID: H, ENT, GAMMA, LR } = this.hp, th = this.theta, g = this.grad.fill(0);
    let G = 0;
    for (let t = steps.length - 1; t >= 0; t--) {
      const { x, allowed, k, f, r } = steps[t];
      G = r + GAMMA * G;
      const adv = G - f.v, n = steps.length;
      // d(loss)/d(logit_i) for loss = -log p_k * adv - ENT * entropy + 0.5 (G - v)^2, averaged over the episode
      const ent = -f.p.reduce((s, q) => s + q * Math.log(q + 1e-12), 0);
      const dl = f.p.map((q, i) => ((q - (i === k ? 1 : 0)) * adv + ENT * q * (Math.log(q + 1e-12) + ent)) / n);
      const dv = (f.v - G) / n, dh = new Float64Array(H);
      allowed.forEach((a, i) => {
        g[this.obp + a] += dl[i];
        for (let j = 0; j < H; j++) { g[this.oWp + a * H + j] += dl[i] * f.h[j]; dh[j] += dl[i] * th[this.oWp + a * H + j]; }
      });
      g[this.obv] += dv;
      for (let j = 0; j < H; j++) { g[this.oWv + j] += dv * f.h[j]; dh[j] += dv * th[this.oWv + j]; }
      for (let j = 0; j < H; j++) {
        const d = dh[j] * (1 - f.h[j] * f.h[j]);
        if (d === 0) continue;
        g[this.ob1 + j] += d;
        const row = this.oW1 + j * this.nIn;
        for (let i = 0; i < this.nIn; i++) g[row + i] += d * x[i];
      }
    }
    this.t++;
    const b1 = 0.9, b2 = 0.999, c1 = 1 - b1 ** this.t, c2 = 1 - b2 ** this.t;
    for (let i = 0; i < th.length; i++) {
      this.m[i] = b1 * this.m[i] + (1 - b1) * g[i];
      this.v[i] = b2 * this.v[i] + (1 - b2) * g[i] * g[i];
      th[i] -= LR * (this.m[i] / c1) / (Math.sqrt(this.v[i] / c2) + 1e-8);
    }
  }
}

// Train a fresh network on one skill for `budget` steps, then score it over `episodes` episodes
// with learning off. Training and evaluation run in separate environments seeded from `seed`.
export function trainAndScore(seed, skill, { budget = HP.BUDGET, episodes = 300, hp = HP } = {}) {
  const env = new Env(seed, skill), net = new ActorCritic(env.obs.length, seed * 7919 + 1, hp);
  let ep = [];
  while (env.steps < budget || ep.length) {   // finish the episode that is running at the budget
    const x = Float64Array.from(env.obs), allowed = env.allowed, { k, f } = net.act(x, allowed, false);
    const r = env.step(allowed[k]);
    ep.push({ x, allowed, k, f, r: r.reward });
    if (r.done) { net.learn(ep); ep = []; }
  }
  const trainSteps = env.steps, trainSuccess = env.successes / env.episodes;
  const test = new Env(seed + 100000, skill), greedy = GAINS.performGreedy.includes(skill);
  const theta = Float64Array.from(net.theta);
  while (test.episodes < episodes) test.step(test.allowed[net.act(test.obs, test.allowed, greedy).k]);
  if (theta.some((w, i) => w !== net.theta[i])) throw new Error("weights changed during scoring");
  return { success: test.successes / test.episodes, evalSteps: test.steps, trainSteps, trainSuccess };
}

if (process.argv[1] && import.meta.url.endsWith(process.argv[1].split("/").pop())) {
  const args = process.argv.slice(2), take = name => { const i = args.indexOf(name); return i < 0 ? null : args.splice(i, 2)[1]; };
  const out = take("--out"), episodes = Number(take("--episodes") ?? 300), budget = Number(take("--budget") ?? HP.BUDGET);
  const hp = { ...HP, BUDGET: budget, LR: Number(process.env.LR ?? HP.LR), ENT: Number(process.env.ENT ?? HP.ENT) };
  const seeds = args.filter(a => /^\d+$/.test(a)).map(Number);
  if (!seeds.length) seeds.push(1, 2, 3, 4, 5);
  const runs = [], table = {};
  for (const seed of seeds) {
    for (const { key } of STAGES) {
      const t0 = Date.now(), r = trainAndScore(seed, key, { budget, episodes, hp });
      runs.push(run({ arm: "actor-critic", seed, split: key, status: "ok", seconds: (Date.now() - t0) / 1000, scores: r }));
      (table[key] ??= []).push(r.success);
    }
    console.error(`seed ${seed}: ` + STAGES.map(s => `${s.key} ${table[s.key].at(-1).toFixed(2)}`).join(", "));
  }
  const mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
  console.log(`actor-critic (LR ${hp.LR}, ENT ${hp.ENT}, ${hp.HID} hidden), ${budget} training steps per skill, ` +
    `success over ${episodes} episodes, mean over seeds ${seeds.join(" ")}`);
  console.log(STAGES.map(s => s.key.padStart(8)).join("") + "\n" + STAGES.map(s => mean(table[s.key]).toFixed(2).padStart(8)).join(""));
  if (out) writeResult(out, resultRecord({ experiment: "brain-world/rl-baseline", baseline: "actor-critic", runs,
    metrics: { success: "higher" },
    config: { arms: ["actor-critic"], seeds, hidden: hp.HID, lr: hp.LR, entropy: hp.ENT, gamma: hp.GAMMA,
      mode: "perform, graduated (gait reflex on)", greedy: GAINS.performGreedy, network: "one per skill" },
    budgets: { train_steps_per_skill: budget, eval_episodes_per_skill: episodes } }));
}
