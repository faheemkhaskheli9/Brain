# M0c bidirectional structural transfer stress protocol (2026-11-17)

**Status:** implementation and ten-seed evaluation workflow created, results **not yet observed** at authoring. This is an exploratory falsification study on an engineered 5×5 simulator, **not** AGI or a human-brain model. Existing issues [#110](https://github.com/faheemkhaskheli9/Brain/issues/110), [#112](https://github.com/faheemkhaskheli9/Brain/issues/112), [#153](https://github.com/faheemkhaskheli9/Brain/issues/153) and [#154](https://github.com/faheemkhaskheli9/Brain/issues/154) remain the backlog. The exact parent inspected was main [2f714b714d80574c4d66697f55bfbf3c3d61d250](https://github.com/faheemkhaskheli9/Brain/commit/2f714b714d80574c4d66697f55bfbf3c3d61d250) (2026-11-17).

## Confirmed source gap and falsifier

The earlier [M0c matched-controls implementation](m0c-stateful-construction-controls-2026-11-17.md) compared six policies within the same \`stateful_construct.mjs\` environment, but its train/dev/heldout split used only four goal pairs and four obstacle templates with fixed \`start=[2,0]\`. More seed IDs did not establish genuinely unseen geometry. The prior [ten-seed options result](stateful-options-exact-negative-2026-11-12.md) recorded **zero** held-out success for all non-oracle arms at its configured budgets; that is a negative finding for its toy setup, not proof that local learning cannot work.

**Hypothesis H-M0c2 (falsifiable):** under fixed per-arm physical-decision budgets, a public-observation learning policy improves actual *delivered items* compared with uniform random on at least one of the new stress directions. Failure means inspect observability, reward sparsity and history representation before adding a larger brain. A high-performing authored pathfinder or target-relative tabular learner does not prove unsupplied skill discovery by Brain.

## Implementation and immutable controls

- [\`stateful_structural.mjs\`](../game/world/stateful_structural.mjs) adds two **independently sampled authored** stress families: **scattered** (2–6 randomized obstacles and non-overlapping randomized start/item/goal, distance floor) and **barrier** (a 4-cell divider with a random open gate, optional distractors and an enforced opposite-side goal). Both use existing six-action transitions, reward, public sensor dimensions and dynamics. Stress tasks use explicit \`start\`; legacy defaults stay unchanged.
- **scattered → barrier**: train and development on different unique scattered configurations; score heldout on barrier configurations. **barrier → scattered** reverses the direction. These are **two topology-family tests**, not independently proven real-world transfer. No hidden extra mechanics or new task-solving action is supplied to the learner.
- Unique physical \`start, item, goal, sorted walls, horizon, dynamics-v1\` fingerprints exclude arbitrary task ID, random seed and split label. Reject full-structure cross-split repeats **and within-split duplicates**, preserve independently seeded generation and ordered manifest hashes. Fail closed if unique feasible samples cannot be found within the candidate budget.
- The generator may call privileged BFS feasibility **offline only**, before policies run. Every attempted BFS is counted as \`offlineGeneratorOracleQueries\` and each rejection is recorded. No policy can query BFS, and \`oracleQueries\` for each evaluated arm must remain **0**. A feasibility oracle is **not** a legitimate performance control for learned agents.
- For structural stress only, the Brain evaluator substitutes the *public task's physical fingerprint* for \`task.id\` in its evaluation RNG seed. Arbitrary IDs therefore cannot steer the sampling stream. Frozen learner copies and exact training caps are unchanged.
- All six arms use the same observations/actions/transitions/rewards. Relative coordinates and maze planning remain **engineered priors**; neural Brain weights are updated by local three-factor reward modulation, not backpropagation. Failed moves, bad placements and other legal attempts consume one physical environment transition; there are no free option exits in these six arms.
- \`research/analyze_m0c_controls.py\` fails integrity checks on missing seeds/failed runs, repeated records, uncharged environment actions, wrong budgets, oracle access, or structural duplicates. It reports ten-seed paired bootstrap 95% CIs (10,000 resamples; RNG seed 20261117) and **development-selected** strongest non-flat comparator, without tuning on heldout results. This is descriptive, not a sealed statistical promotion.

## Precommitted evaluation and reproducibility

Run from repository root (or via [M0c evidence GitHub Actions](../.github/workflows/m0c-evidence.yml), retaining each raw \`brain-result/1\` file and its paired analysis):

\`\`\`bash
node game/world/test_stateful_structural.mjs
python research/test_analyze_m0c_controls.py
node game/world/stateful_construct_controls.mjs 1 2 3 4 5 6 7 8 9 10 --protocol legacy --train-steps 10000 --train-tasks 32 --dev-tasks 16 --eval-tasks 16 --repeats 2 --out /tmp/m0c-legacy.json
node game/world/stateful_construct_controls.mjs 1 2 3 4 5 6 7 8 9 10 --protocol scattered-to-barrier --train-steps 2500 --train-tasks 32 --dev-tasks 16 --eval-tasks 16 --repeats 2 --out /tmp/m0c-scattered-to-barrier.json
node game/world/stateful_construct_controls.mjs 1 2 3 4 5 6 7 8 9 10 --protocol barrier-to-scattered --train-steps 2500 --train-tasks 32 --dev-tasks 16 --eval-tasks 16 --repeats 2 --out /tmp/m0c-barrier-to-scattered.json
python research/result_schema.py --check /tmp/m0c-legacy.json
python research/analyze_m0c_controls.py /tmp/m0c-legacy.json
\`\`\`

**Precommitted:** seeds 1–10; four trainable arms each use exactly 10,000 primitive/environment decisions on legacy and exactly 2,500 on each stress direction. Random and heuristic have **zero training**, making them useful non-learning controls rather than equal-training-cost claims. Each seed uses 32 training tasks, 16 dev tasks, 16 heldout tasks and two frozen repeats (32 heldout episodes/seed). The **primary outcome** is physical delivery completion, with failed actions and environment steps audited. Report per-arm actual decision consumption, parameter footprint estimates, offline feasibility cost, unique structures, all statuses, across-seed uncertainty and the development-selected comparator.

**Control and stopping rule:** if learned arms fail to beat random in these pilots, maintain **HOLD** on advanced architecture; prioritize a fixed-geometry learnability calibration, per-step reward/credit diagnostics and stronger public-history controls. If exploratory success appears, repeat on **20 sealed seeds across at least two novel, predeclared generator families** with the v1.1 gate (heldout delivery margin ≥0.10 over strongest non-oracle dev-selected baseline, paired CI lower >0, old-skill retention lower >−0.05, exact cost accounting). **Do not apply that promotion gate to these authored experiments.**

## Adversarial limitations

1. Stress family identity differs between development and evaluation, so selecting parameters using heldout scores would contaminate the result; only dev controls may guide subsequent architecture work. The same two authored families and a fixed 5×5 action/reward design limit scope.
2. Feasibility filtering changes the task distribution. Every rejected infeasible candidate and BFS call is recorded; future work should include infeasible cases to measure calibration, not just completion.
3. Tabular-Q has an engineered relative-state arm and a larger/different storage representation than Brain. Parameter count, memory allocation, wall time, unsuccessful episodes and exploration costs must not be conflated.
4. A positive *heuristic* or *tabular-relative* result is evidence that public sensors plus engineered priors can solve these tasks; it is **not evidence that Brain learned planning, hierarchy or spatial coordinates**.
5. A negative learner result on sparse terminal rewards is not an impossibility theorem for local learning. Early transitions may need an additional public memory state or reward/credit intervention, evaluated separately.
6. The frozen score of source tasks is post-training only, **not pre/post old-task retention**. No continual-learning benefit is claimed without a before/after intervention.
7. Ten seeds and deterministic bootstrap intervals are exploratory; no multiple-comparison correction or out-of-distribution real-world claim has been established. CI verifies reproducibility and integrity, not significance.

**Research context:** the options framework of Sutton, Precup & Singh (1999), [DOI:10.1016/S0004-3702(99)00052-1](https://doi.org/10.1016/S0004-3702(99)00052-1), motivates evaluation of hierarchical policy control but cannot establish this system's efficacy. All simulator implementation and baseline facts above are code-observed at the cited parent and proposed changes, not findings from a biological experiment.
