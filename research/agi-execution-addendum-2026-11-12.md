# Brain AGI execution addendum: implemented integrity repairs and M0c handoff

Date: 2026-11-12. Status: research protocol, not demonstrated AGI. Preserve predecessor [v1.0](agi-execution-blueprint-2026-11-12.md), canonical [v1.1](agi-execution-blueprint-v1.1-2026-11-12.md), and [append-only adversarial ledger](agi-review-ledger.md). Follow existing issues [#120](https://github.com/faheemkhaskheli9/Brain/issues/120) (goals) and [#136](https://github.com/faheemkhaskheli9/Brain/issues/136) (priority).

## Current source-backed implementation status

| Package | Code and evidence | Scientific interpretation |
| --- | --- | --- |
| M0a frozen evaluation | [PR #195](https://github.com/faheemkhaskheli9/Brain/pull/195): `98544659` code/tests, `0be775b6` knowledge note. Full CI and separate 10-seed workflow passed. | Evaluation correctness; no new learned competence. |
| M0b exact budget | [PR #196](https://github.com/faheemkhaskheli9/Brain/pull/196): `aab50b1d` code/tests, `c44cd932` KB. Full CI and separate 10-seed workflow passed. Stacked on #195. | Exact counts are needed for fairness, not sufficient to establish improvement. |
| M0c fair new tasks / comparators | Not implemented by these PRs. | Highest-value next engineering change. |
| M0d evidence mutation gates | Existing `continual_guard.py` is partial; new attacks still open. | No independent proof of source/global-state or hidden answer immunity. |

No results or historical claims were overwritten; PRs were still **unmerged** at this review.

## Review finding: an exact cap can remain unfair

Cutting an episode at a fixed total decision count changes its endpoint and eligibility/critic update. Some algorithms make more or fewer steps per episode, so equal total decisions can still yield different end-state distributions. Before claiming an M0b performance gain, compare final-partial-episode bootstrap against a separately costed episode-boundary historical arm on development tasks. Measure truncated-attempt count, learning-curve AUC, goal success, retention, environment actions and wall time. A passing deterministic test is not a proof of advantage.

## Detailed M0c engineering sequence (one logical change per PR)

1. **Freeze legacy fixtures:** retain the current 5×5 `generate`, four item-goal pairs and four obstacle templates per split as a regression-only dataset; pin canonical structural fingerprints excluding IDs. Do not silently relabel old evidence.
2. **Define opt-in task schema:** implement `generateV2(seed, split, n, config)` with start, goal, item, obstacles, affordances, horizon, interruption schedule and environment dynamics metadata. Hide generator-only fields from `observe`. Validate occupancy, reachability, duplicate walls, solvability and deterministic seeds.
3. **Partition by structural family:** define train/dev/held-out/stress families with new starts, nonisomorphic obstacle maps, goals, dynamics and perceptual omissions. Detect duplicates and rotational/reflection equivalents *between* partitions, not only duplicate task IDs.
4. **Audit feasibility offline:** use BFS only during task-set design to stratify shortest-path length and identify impossible stress cases. Account for all oracle calls and expansions; never give its map, path, hidden rules or feasibility label to the learner.
5. **Implement public-observation controls:** same `observe`, legal *syntactic* actions and reward/termination rules for legal stepwise random, open-loop script, observation-only heuristic and tabular history-based SARSA/Q-learning. Do not grant a tabular agent hidden obstacles or actual generator IDs.
6. **Benchmark learned policies:** reuse flat backprop-free actor, supplied options, no-gate/no-termination, goal-masked, no-observation and a tuned shared gradient-based RL comparator. Label full-state BFS as privileged ceiling. Tune comparator hyperparameters on development only; account for all tuning and total pretraining + adaptation interactions.
7. **Build mutation gates:** reject hidden target in observed features, altered split fingerprint, repeated/equivalent test patterns, free oracle call, action-mask mismatch, model modification during scoring, dropped failure row and tampered checkpoint.
8. **Run diagnostic:** ten matched development seeds, exact primitive decisions, actual held-out goal success, per-family success, failures/timeouts, source retention, learning curve, memory, CPU/wall time, output in `brain-result/1`. Record negative results even if all learners fail. If no public-observation baseline exceeds legal random, repair observability, reward and horizon before adding more neural complexity.
9. **Run independent confirmation only after freezing:** use another task-family generator whose instances are not present in public training data and at least twenty new paired seeds; report cluster-by-family confidence intervals and old-skill non-inferiority, not seed-wise point improvement alone.
10. **Promotion decision:** require meaningful actual-task success improvement against the strongest development-selected *nonprivileged* comparator, noninferior retention, absence of leakage, fair compute accounting and independent replication. Otherwise HOLD/REJECT and preserve raw failures.

## Benchmark-source adversarial research (not Brain measurements)

[ARC Prize's 2026 ARC-AGI-3 competition](https://arcprize.org/competitions/2026/arc-agi-3) presents agents interacting with new environments to explore, infer goals and act. Its [testing policy](https://arcprize.org/policy) describes testing, score publication and information security. These are useful methodological inspirations for Brain's future open-ended evaluation, not validation of the current creature.

An independent [Epoch AI review dated October 30, 2026](https://epoch.ai/benchmarks/arc-agi-3/review) judged ARC-AGI-3 **Flawed**, identifying action-efficiency scoring ambiguity, harness/version inconsistency and evaluation bias. This is external methodological criticism based on public information, not a refutation of all interactive tests. Therefore never use a single ARC-AGI-3 score, or any benchmark's name, as a proof of AGI. Separately report task completion, action count, planning/tool costs, adaptation and learned-vs-engineered knowledge. Public GitHub test seeds are accessible to agents and cannot constitute truly sealed confirmation.

## Durable research policy

Every substantive task must append the review outcome and a dated, source-grounded KB note containing actual inspected code/commit, published sources, failed/null outcomes, exact executed tests, limitations and next falsification. Keep research reports, older plans and negative data in Git; do not fabricate paper evidence or retroactively rewrite confirmatory protocols. Backprop-free Brain World remains separate from gradient/LLM hybrid baselines.

## 2026-11-12 empirical update — M0b exact-budget learning FAILED

The [10-seed exact-budget result report](https://github.com/faheemkhaskheli9/Brain/blob/fix/options-exact-decision-budget-20261112/research/stateful-options-exact-negative-2026-11-12.md) and [archived raw data](https://github.com/faheemkhaskheli9/Brain/blob/fix/options-exact-decision-budget-20261112/research/results/stateful-options-exact-2026-11-12.tar.br) overturn any optimistic inference that passing code integrity tests demonstrates transferable options. The experiment ran 70 arm×seed rows and passed CI, **but all six non-oracle policies had 0% frozen held-out goal success** (privileged BFS feasibility ceiling 100%). The preregistered paired option-vs-flat success improvement was 0.000, CI [0.000,0.000], p=1.000; gate **FAIL**. The learned policies spent exactly 10,000 training plus 2,000 adaptation decisions per seed. The raw artifact is retained losslessly as a Git-tracked Brotli tar archive with the independent gate file and complete `brain-result/1` data, SHA-256 `eb2b6641702f499c50cfb3f114d0aeb39b5bc0ba3263a3780fc71a5c8da1c79f`.

**Changed implementation decision:** Stop promoting option hierarchy, planner or 'AGI architecture' claims. For M0c first test *learnability* with a public-observation tabular/history baseline and a transparent legal heuristic; report actual task completions and failures, not shaped reward or fewer invalid actions as a substitute. Only if an unprivileged baseline learns should the next study attempt independent structural-family transfer. This is a negative research result and must remain in the durable KB even if later experiments improve.
