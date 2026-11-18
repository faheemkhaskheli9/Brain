// M0c deterministic smoke and adversarial observation/interaction invariants.
import assert from "node:assert/strict";
import { observe, initial } from "./stateful_construct.mjs";
import { ARMS, PublicTabular, PublicMazeHeuristic, buildManifest, structureKey,
  publicStateKey, rollout, runSeed } from "./stateful_construct_controls.mjs";

const nearby = { id: "calibration", item: [2, 0], goal: [4, 0],
  walls: [[3, 0]], maxSteps: 20 };
const alteredId = { ...nearby, id: "eval-secret", split: "eval" };
assert.equal(structureKey(nearby), structureKey(alteredId),
  "split name and task ID must never become a structural feature");
const reordered = { ...nearby, walls: [[1, 2], [3, 0]] };
assert.equal(structureKey(reordered),
  structureKey({ ...reordered, walls: [[3, 0], [1, 2]] }));
assert.notEqual(structureKey(nearby), structureKey(reordered));
assert.throws(() => buildManifest([nearby], [alteredId], [reordered]), /overlap/);

const observation = observe(nearby, initial(nearby));
assert.equal(publicStateKey(observation),
  publicStateKey(observe(alteredId, initial(alteredId))));
assert.equal(new PublicMazeHeuristic().act(observation), 4,
  "pickup comes from public item-contact, not a scripted answer");
const solved = rollout(nearby, new PublicMazeHeuristic());
assert.equal(solved.success, true, "publicly discovered wall navigation should solve an easy fixture");
assert.equal(solved.decisions, solved.envSteps);
assert.ok(solved.decisions <= nearby.maxSteps);
const censored = rollout(nearby, new PublicMazeHeuristic(), { cap: 1 });
assert.equal(censored.decisions, 1);
assert.equal(censored.success, false);
assert.equal(censored.reason, "budget-censored");
assert.throws(() => rollout(nearby, { act: () => 6 }), /outside shared set/);

const qa = new PublicTabular(101), qb = new PublicTabular(101);
const selections = Array.from({ length: 60 }, () => qa.act(observation));
assert.deepEqual(selections, Array.from({ length: 60 }, () => qb.act(observation)));
assert.ok(new Set(selections).size >= 2, "untrained Q must not prefer first action");
assert.ok(selections.every(a => a >= 0 && a < 6));
assert.equal(qa.table.row(publicStateKey(observation)).length, 6);
const fresh = new PublicTabular(31);
const after = observe(nearby, { ...initial(nearby), agent: [2, 1], steps: 1 });
fresh.update(observation, 2, 1, after, false);
const detached = fresh.clone(89);
const frozenBefore = JSON.stringify([...fresh.table.values]);
detached.table.row(publicStateKey(observation))[2] += 5;
assert.equal(JSON.stringify([...fresh.table.values]), frozenBefore,
  "frozen scoring must deep-copy Q rows");
assert.ok(fresh.states > 0 && fresh.bytesEstimate > 0);
assert.notEqual(publicStateKey(observation, true), publicStateKey(after, true));

const cfg = { trainSteps: 17, trainTasks: 4, devTasks: 3, evalTasks: 3, repeats: 1 };
const a = runSeed(2, cfg), b = runSeed(2, cfg);
assert.deepEqual(a.manifest, b.manifest);
assert.deepEqual(a.rows.map(x => x.arm), ARMS);
assert.deepEqual(a.rows.map(x => x.scores), b.rows.map(x => x.scores),
  "all metrics must be deterministic under fixed seed/structural split");
for (const entry of a.rows) {
  assert.equal(entry.status, "ok", entry.reason);
  const s = entry.scores;
  for (const x of ["source", "development", "heldout"]) {
    assert.ok(s[x].success >= 0 && s[x].success <= 1);
    assert.equal(s[x].exits, 0);
    assert.equal(s[x].envSteps, s[x].decisions);
    assert.equal(s[x].episodes, (x === "source" ? Math.min(cfg.trainTasks, cfg.evalTasks) : 
      x === "development" ? cfg.devTasks : cfg.evalTasks) * cfg.repeats);
  }
  assert.equal(s.oracleQueries, 0);
  if (["flat", "flat-goal-masked", "tabular-absolute", "tabular-relative"].includes(entry.arm)) {
    assert.equal(s.trainDecisions, cfg.trainSteps, "no budget overshoot");
    assert.equal(s.trainEnvSteps, cfg.trainSteps, "every primitive action changes physical state");
  } else {
    assert.equal(s.trainDecisions, 0);
    assert.equal(s.trainEnvSteps, 0);
  }
}
assert.ok(a.manifest.counts.train.uniqueStructures <= 16);
assert.ok(a.manifest.counts.dev.uniqueStructures <= 16);
assert.ok(a.manifest.counts.heldout.uniqueStructures <= 16);
console.log("same-environment construction controls: OK (not scientific transfer)");
