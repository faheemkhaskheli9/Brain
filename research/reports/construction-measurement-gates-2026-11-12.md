# Construction pilot — adversarial measurement audit (PR 1)

Status: **implementation under review; no experiment or scientific claim verified**.
Detailed preregistration and Gates A–C: [plan PR #176](https://github.com/faheemkhaskheli9/Brain/pull/176).
This change does not introduce a learned option or AGI capability.

## Protocols and controls

- Diagnostic construction benchmark: paired seeds 1–10, 64 generated training tasks, exactly **10,000 primitive training decisions** for each trained or learning-off arm; 30 eval tasks, five attempts/task. A partial last training episode is truncated with no validation call. Report this explicitly rather than treating 10,000 decisions as 10,000 episodes.
- Evaluation uses fully detached per-score Brain checkpoints and independent seed-specific RNG. Tests check repeated sampled/greedy scoring, score-order invariance, no source parameter/counter/RNG changes, exact decision caps and masked action legality.
- Agent arms: learner raw/masked (goal-blind history mask), goal-masked input, learning-off; comparator arms: per-step random raw/masked and **noninteractive** candidate-search random-valid. Do **not** compare the candidate generator's zero environment decisions directly with the agent's interactive decision cost.
- Every final attempt is checked by the same validity function; every arm records its verifier calls, actions, decisions, duplicate/empty actions, per-episode result and frozen seed. Goal masks do not use hidden success information.
- The strict novelty exclusion set includes every enumerated training solution. Six primitives admit at most 63 nonempty subsets; symmetry-equivalent picture classes reduce that ceiling further. Report `novelOpportunityRate` and `conditionalNovel`; the latter is null if no task has any unseen valid class. Neither counts as open-ended creativity.
- Fair novelty comparator uses the **same 8 verifier calls per task** on all five arms, while the graded arm receives eight additional *privileged numerical feedback* calls. Only that arm is an unequal-information upper bound.

## Commands to run when a writable checkout and compute are available

```bash
node game/world/test_construct.mjs
node game/world/test_construct_learner.mjs
node game/world/test_construct_transfer.mjs
node game/world/test_novelty_fair.mjs
node game/world/novelty_fair.mjs 1 2 3 4 5 6 7 8 9 10 --tasks 30 --budget 8 --out /tmp/brain-novelty-fair-10seed.json
node game/world/construct_learner.mjs 1 2 3 4 5 6 7 8 9 10 --train-steps 10000 --train-tasks 64 --eval-tasks 30 --repeats 5 --out /tmp/brain-construction-10seed.json
python research/result_schema.py --check /tmp/brain-novelty-fair-10seed.json /tmp/brain-construction-10seed.json
ruff check .
python build_index.py
python run_code_blocks.py
python research/check_claims.py
```

Keep the raw validated JSON and checksums, report all failed seeds and CI status. No full 10-seed or latency numbers have been observed from this PR.

## Adversarial review and remaining blockers

| Priority | Test / threat | Status |
|---|---|---|
| P0 | A frozen evaluation mutates the training RNG, hidden activation counters or policy state | Detached evaluation introduced; local runtime test **not run** |
| P0 | A random candidate generator avoids charged submit/step actions | Distinct per-step raw/masked controls introduced; still explicitly unequal pretraining |
| P0 | Training budget silently overshoots by finishing the last episode | Exact cap added to construction and transfer pilots |
| P0 | Novelty saturates a 63-subset universe | Opportunity count added; larger task still required |
| P0 | Positive scores are cherry-picked or have pseudoreplicated confidence intervals | Ten paired seeds must be run; seed, not trial, is the unit |
| P1 | Memorized action order is mistaken for reusable skill | **Open**: Gate B must implement stateful acquire/carry/place and counterfactual transition tests |
| P1 | Shallow tabular learning beats a claimed reusable option | **Open**: Gate B/C need equal-budget tabular comparator |
| P1 | Hidden curriculum leakage, adaptation advantage or retention loss | **Open**: pre-register transition holdouts; evaluate old skill before/after option learning |

**Stop rule:** Do not start a purported learned-option benefit claim until the full pilot is measured and its checks pass. If it fails to beat the strongest budget-matched, legal-action nonlearning baseline, diagnose failure and publish the negative result instead of moving success thresholds.
