// Deterministic structural transfer stress test: exact geometry, independent
// generator families, offline oracle cost and public-policy action accounting.
import assert from "node:assert/strict";
import { START, generate, initial, observe, oracle, transition } from "./stateful_construct.mjs";
import { PROTOCOLS, createStructuralBenchmark, generateStructural,
  physicalFingerprint } from "./stateful_structural.mjs";
import { runSeed, PublicMazeHeuristic, buildManifest, rollout } from "./stateful_construct_controls.mjs";

const old = generate(1, "train", 1)[0];
assert.deepEqual(initial(old).agent, START, "legacy task remains unchanged");
assert.deepEqual(initial({ ...old, start: [4, 2] }).agent, [4, 2]);
assert.throws(() => initial({ ...old, start: old.walls[0] }), /wall/);
const moved = { ...old, start: [4, 2], id: "different-seed-and-split" };
assert.notEqual(physicalFingerprint(old), physicalFingerprint(moved));
assert.equal(physicalFingerprint(moved), physicalFingerprint({ ...moved,
  id: "secret-eval", walls: [...moved.walls].reverse() }));

const easy = { id: "easy-stress", start: [3, 1], item: [3, 1], goal: [4, 1],
  walls: [[1, 1]], maxSteps: 12 };
assert.deepEqual(initial(easy).agent, [3, 1]);
assert.equal(observe(easy, initial(easy))[1 * 5 + 3], 1);
assert.deepEqual(oracle(easy), [4, 1, 5]);
assert.equal(rollout(easy, new PublicMazeHeuristic()).success, true);

const seen = new Set(), g = generateStructural(2, "train", "scattered", 7, seen);
assert.equal(g.tasks.length, 7);
assert.equal(g.audit.feasible, 7);
assert.equal(g.audit.oracleQueries, g.audit.feasible + g.audit.infeasibleRejected);
assert.equal(g.audit.attempted, 7 + g.audit.duplicateRejected +
  g.audit.invalidRejected + g.audit.infeasibleRejected);
assert.equal(seen.size, 7);
assert.deepEqual(generateStructural(2, "train", "scattered", 7).tasks, g.tasks,
  "same seed and family must give exact task fixtures");
assert.throws(() => generateStructural(1, "wrong", "barrier"), /invalid/);
assert.throws(() => generateStructural(1, "train", "legacy"), /invalid/);
assert.throws(() => generateStructural(1, "eval", "barrier", 0), /invalid/);

for (const protocol of PROTOCOLS.filter(x => x !== "legacy")) {
  for (const seed of [1, 2, 3]) {
    const size = { train: 7, dev: 5, heldout: 5 };
    const a = createStructuralBenchmark(seed, protocol, size);
    const b = createStructuralBenchmark(seed, protocol, size);
    assert.deepEqual(a, b, "seeds must fix all training/evaluation candidates");
    const manifest = buildManifest(a.train, a.dev, a.heldout);
    for (const [split, n] of Object.entries(size)) {
      assert.equal(manifest.counts[split].tasks, n);
      assert.equal(manifest.counts[split].uniqueStructures, n,
        "no duplicate structure masquerades as independent evidence");
      assert.equal(manifest.counts[split].duplicates, 0);
      for (const t of a[split]) {
        assert.ok(t.start && t.start.length === 2);
        assert.ok(oracle(t), "feasibility certified before training");
        const first = initial(t), obs = observe(t, first);
        assert.equal(obs.length > 80, true);
        const act = new PublicMazeHeuristic().act(obs);
        assert.ok(act >= 0 && act < 6, "public heuristic same primitives as Brain");
        assert.equal(transition(t, first, act).state.steps, 1);
      }
    }
    assert.notEqual(a.audit.sourceFamily, a.audit.heldoutFamily);
    assert.ok(a.audit.totalOfflineOracleQueries >= 17);
    // This cheap test guarantees integration with the six-arm runner, not transfer.
    if (seed === 1) {
      const rows = runSeed(seed, { trainSteps: 23, trainTasks: 7,
        devTasks: 5, evalTasks: 5, repeats: 1, protocol });
      assert.deepEqual(rows.manifest, manifest);
      assert.equal(rows.generatorAudit.totalOfflineOracleQueries,
        a.audit.totalOfflineOracleQueries);
      assert.equal(rows.rows.length, 6);
      for (const row of rows.rows) {
        assert.equal(row.status, "ok", row.reason);
        assert.equal(row.split, "structural-" + protocol);
        assert.equal(row.scores.heldout.episodes, 5);
        assert.equal(row.scores.heldout.envSteps, row.scores.heldout.decisions);
        assert.equal(row.scores.oracleQueries, 0);
        if (row.arm === "flat" || row.arm === "flat-goal-masked" ||
            row.arm.startsWith("tabular-")) {
          assert.equal(row.scores.trainDecisions, 23);
          assert.equal(row.scores.trainEnvSteps, 23);
        }
      }
    }
  }
}
assert.throws(() => createStructuralBenchmark(1, "legacy",
  { train: 3, dev: 3, heldout: 3 }), /independent/);
console.log("two independent structural transfer generator families: OK");
