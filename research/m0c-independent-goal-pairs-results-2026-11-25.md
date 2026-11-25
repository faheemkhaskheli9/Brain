# M0c independent goal-pair fixture audit results (2026-11-25)

**Exploratory engineering result.** Implements the
[registered fixture audit](m0c-independent-goal-pairs-protocol-2026-11-25.md) on
[a2970d5](https://github.com/faheemkhaskheli9/Brain/commit/a2970d557d19e33c4446591ac4c4924b7672fd2b).
Node 24.22.3, seeds 1–10, six goal pairs per split and three frozen repeats.
The [raw brain-result/1 file](results/m0c-independent-goal-pairs-audit-2026-11-25.json)
records split fingerprints, candidate counts, offline oracle calls and all 80 arm/split/seed rows.

| Layout split | Goal-aware public heuristic | Goal-blind uniform random |
| --- | ---: | ---: |
| Open train | 360/360 (100%) | 0/360 |
| Open dev | 360/360 (100%) | 0/360 |
| Scattered holdout | 315/360 (87.5%) | 0/360 |
| Barrier holdout | 324/360 (90.0%) | 0/360 |

All 480 goals passed offline oracle certification. The generator considered 109 open
train, 159 open dev, 459 scattered and 729 barrier layout candidates. No run row
errored. Every blinded random trajectory matched its paired rollout. Separate regression
tests used evaluator-only routes to attain the 50% ceiling, searched for overlapping
legal first carry moves using the simulator, and rejected a deliberately mismatched
blind trajectory.

Both holdout families cleared the heuristic fixture-review threshold. The heuristic
uses public coordinates and discovered walls. Its repeat outcomes are deterministic.
The 0% uniform-random score measures exploration difficulty under a tight deadline.
The 50% upper bound is the appropriate reference for whether blind goal selection
could account for a future learned policy's score. The pilot does not quantify how
well a public-information learner could approach that bound or explain individual
heuristic failures.

**Decision.** Keep these public fixtures for diagnostics. Tight deadlines and rejection
sampling favor layouts with feasible shortest routes and leave little room for obstacle
discovery. The relational adapter and its public input contract passed regression tests.
The learning effect of the adapter is unmeasured. Next falsifier is an equal-budget
absolute vs. relative vs. masked comparison with dev-only tuning, a public-history
baseline and independently sealed family manifests. M1–M8 remain HOLD.
