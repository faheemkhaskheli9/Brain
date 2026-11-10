// Fast deterministic sampling and save/load checks for Brain World replay (#152).
import assert from "node:assert/strict";
import { GAINS, Hippocampus, World, rng } from "./brain.js";

const keep = { memCap: GAINS.memCap, sleepSampler: GAINS.sleepSampler,
  sleepEvery: GAINS.sleepEvery, sleepSize: GAINS.sleepSize };
GAINS.memCap = 4;
try {
  const x = new World(1).sense();
  const m = new Hippocampus();
  m.epId = 1;
  for (let i = 0; i < 4; i++) {
    m.store(x, 0, 0, 1, i + 1, 1, 1, i === 0);
  }
  assert.equal(m.n, 4);
  assert.deepEqual(Array.from(m.priority), [1, 2, 3, 4]);
  assert.deepEqual(Array.from(m.failed), [1, 0, 0, 0]);
  // Exact probabilities and inverse-probability weights, not only frequencies.
  let d = m.sampleWeighted(() => 0.05, "td", { alpha: 1, beta: 1 });
  assert.deepEqual([d.index, d.eligible], [0, 4]);
  assert.ok(Math.abs(d.probability - 0.1) < 1e-12);
  assert.equal(d.importance, 1);
  d = m.sampleWeighted(() => 0.95, "td", { alpha: 1, beta: 1 });
  assert.equal(d.index, 3);
  assert.ok(Math.abs(d.probability - 0.4) < 1e-12);
  assert.ok(Math.abs(d.importance - 0.25) < 1e-12);
  d = m.sampleWeighted(() => 0.04, "td-mix", { alpha: 1, mix: 0.2, beta: 1 });
  assert.equal(d.index, 0);
  assert.ok(Math.abs(d.probability - 0.13) < 1e-12);
  // A fixed permutation breaks the link between a transition and its error
  // without changing the priority histogram; save/load must reproduce it.
  const shuffled = m.sampleWeighted(() => 0.05, "td-shuffle", { alpha: 1 });
  assert.equal(shuffled.index, 0);
  assert.ok(Math.abs(shuffled.probability - 0.2) < 1e-12);
  assert.notEqual(shuffled.probability, m.sampleWeighted(() => 0.05, "td", { alpha: 1 }).probability);
  d = m.sampleWeighted(() => 0.25, "failure", { beta: 1 });
  assert.equal(d.index, 0);
  assert.ok(Math.abs(d.probability - 0.5) < 1e-12);
  d = m.sampleWeighted(() => 0.75, "failure", { beta: 1 });
  assert.notEqual(d.index, 0);
  assert.ok(Math.abs(d.probability - 1 / 6) < 1e-12);
  assert.ok(Math.abs(d.importance - 1) < 1e-12);
  const draws = [0, 0, 0, 0];
  const R = rng(5);
  for (let i = 0; i < 10000; i++) draws[m.sampleWeighted(R, "td", { alpha: 1 }).index]++;
  const observed = draws.map(n => n / 10000);
  for (let i = 0; i < 4; i++) {
    assert.ok(Math.abs(observed[i] - (i + 1) / 10) < 0.02,
      "biased sampler deviates from normalized probabilities at " + i);
  }

  // Ring wrap: newer transition overwrites the old TD score and failure flag.
  m.store(x, 0, 0, 1, 0, 1, 1, false);
  assert.equal(m.head, 1);
  assert.equal(m.priority[0], 0.0010000000474974513);
  assert.equal(m.failed[0], 0);
  m.store(x, 0, 0, 1, 0.5, 1, 2, false);
  assert.equal(m.head, 2);
  for (let i = 0; i < 1000; i++) {
    const got = m.sampleWeighted(R, "td-mix");
    assert.ok(got.index >= 0 && got.index !== 1, "sampled a timeout cut");
    assert.ok(m.end[got.index] === 1 || m.next(got.index) >= 0, "sampled an orphan");
  }
  const saved = m.toJSON({ head: m.head, n: m.n, epId: m.epId });
  const restored = Hippocampus.fromJSON(saved);
  assert.ok(restored);
  assert.deepEqual(Array.from(restored.priority), Array.from(m.priority));
  assert.deepEqual(Array.from(restored.failed), Array.from(m.failed));
  assert.deepEqual(m.sampleWeighted(rng(7), "failure"), restored.sampleWeighted(rng(7), "failure"));
  assert.deepEqual(m.sampleWeighted(rng(7), "td-shuffle"), restored.sampleWeighted(rng(7), "td-shuffle"));
  // Old checkpoint lacks priority/failure arrays; they are unknown, not guessed.
  const legacy = { ...saved }; delete legacy.priority; delete legacy.failed;
  const old = Hippocampus.fromJSON(legacy);
  assert.ok(old);
  assert.deepEqual(Array.from(old.priority), [1, 1, 1, 1]);
  assert.deepEqual(Array.from(old.failed), [0, 0, 0, 0]);
  assert.equal(Hippocampus.fromJSON({ ...saved, priority: saved.priority.slice(2) }), null);
  assert.equal(Hippocampus.fromJSON({ ...saved, failed: saved.failed.slice(2) }), null);
  assert.throws(() => m.sampleWeighted(R, "task-oracle"), /invalid/);
  assert.throws(() => m.sampleWeighted(R, "td", { beta: 2 }), /invalid/);

  // No eligible transitions: do not resurrect a timeout or orphan successor.
  const cuts = new Hippocampus();
  cuts.store(x, 0, 0, 1, 0, 1, 2, false);
  assert.equal(cuts.sampleWeighted(R, "failure").index, -1);

  // Integrated live learning + offline replay, without backprop or an oracle.
  GAINS.sleepSampler = "td-mix";
  GAINS.sleepEvery = 1; GAINS.sleepSize = 3;
  const w = new World(2);
  w.setStage(2);
  for (let step = 0; step < 500; step++) w.step();
  assert.ok(w.hippo.n > 0);
  assert.ok(Array.from(w.hippo.priority.slice(0, w.hippo.n)).every(q => q > 0 && Number.isFinite(q)));
  const snapshot = JSON.parse(JSON.stringify(w));
  const w2 = World.fromJSON(snapshot);
  assert.ok(w2.hippo.n > 0);
  assert.deepEqual(Array.from(w2.hippo.priority), Array.from(w.hippo.priority));
  assert.deepEqual(Array.from(w2.hippo.failed), Array.from(w.hippo.failed));
  w2.perform("listen");
  const frozen = JSON.stringify(w2.toJSON().brain);
  for (let step = 0; step < 100; step++) w2.step();
  assert.equal(JSON.stringify(w2.toJSON().brain), frozen, "frozen scoring learned from test data");
  console.log("ok: weighted replay, importance, failures, wrap, legacy saves, live integration");
} finally {
  Object.assign(GAINS, keep);
}
