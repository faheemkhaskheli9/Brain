## Stateful transfer and backprop-free option pilot (#112)

The original six-stroke construction benchmark tests **unordered** drawings (only 63
nonempty combinations); it is not evidence of temporal skill composition. The new,
separate `game/world/stateful_construct.mjs` environment requires
**acquire → carry → place**. It includes a local obstacle sensor, illegal action
penalties, recoverable wrong placement and held-out **object-to-goal pairs**. The
learner sees only agent/object/goal positions, carrying/contact flags and local
walls. A BFS oracle verifies feasibility but is never shown to the learner.

```bash
node game/world/test_stateful_construct.mjs
node game/world/test_stateful_options.mjs
node game/world/stateful_options.mjs 1 2 3 --train-steps 2000 --adapt-steps 2000 --train-tasks 32 --eval-tasks 16 --repeats 2 --out /tmp/stateful-options-pilot.json
python research/result_schema.py --check /tmp/stateful-options-pilot.json
```

The option pilot reuses the existing **backprop-free Brain local three-factor
actor/critic**, with flat, goal-masked, two-option, shuffled-gating, exit-disabled,
untrained random and **privileged BFS oracle** arms. Each option has a learned
action distribution and a voluntary **exit** action. The selector (before/after
carrying) is **engineered and observes the carrying flag**; the options and their
termination boundaries are not discovered autonomously. Option exits count as
decisions and are reported separately from environment transitions. Pretraining uses only train goal-pairs and adaptation uses **development** goal-pairs,
never frozen test goals. Source-skill performance is scored before/after adaptation
to expose forgetting; zero-shot and post-adaptation test scores are separate.
Frozen evaluation uses distinct RNG streams and cannot update actor weights.

**Research status:** This is an unconfirmed engineering pilot, not a reported
transfer gain or proof of human-like skill learning. The full 10-seed,
development-only tuned, matched-cost experiment and the preregistered +0.10
criterion in `research/adversarial-implementation-plan.md` are still required.
A learned goal-dependent option manager, changed dynamics, failure-case memory,
generalization beyond the supplied goal grammar and baseline compute fairness
remain future work.
