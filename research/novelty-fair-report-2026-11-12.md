# Fair novelty benchmark — 10-seed adversarial evidence (2026-11-12)

**Question:** Under legal action spaces and eight charged candidate-validity
queries per task, does engineered novelty search beat a legal random generator?

**Reproduction:** `node game/world/novelty_fair.mjs 1 2 3 4 5 6 7 8 9 10
--tasks 30 --budget 8 --out /tmp/novelty-fair.json`.
This uses 300 held-out task instances per arm, 10 seeds, all five arms,
and exactly eight validator calls per task. Only graded search additionally
sees eight numerical penalty responses per task; it is not an
information-matched baseline. A 63-candidate drawing universe and an
oracle-built training library constrain generalization.

The research run was validated against `brain-result/1` on
[GitHub Actions run 43129642597](https://github.com/faheemkhaskheli9/Brain/actions/runs/43129642597).
Complete per-candidate traces and verification outcomes are in that run's
`novelty-fair-10seed` artifact (90-day retention); a compact 50-run
`brain-result/1` summary is committed at
[`research/results/novelty-fair-2026-11-12.json`](results/novelty-fair-2026-11-12.json).
The summary intentionally excludes the 2.16 MB trace; it is **not** a
replacement for the raw audit.

## Measured outcomes

| Arm | Valid per task | Novel per task | Validator/task | Graded/task |
|---|---:|---:|---:|---:|
| legal random | 2.287 | 0.583 | 8 | 0 |
| retrieval | 2.070 | 0.000 | 8 | 0 |
| blind mutation | 1.963 | 0.523 | 8 | 0 |
| binary-feedback search | 2.227 | 0.620 | 8 | 0 |
| privileged graded search | 2.313 | 0.587 | 8 | 8 |

**Paired differences versus legal random**, where positive means more novel
valid drawings per held-out task. Each seed's 30 tasks are averaged before
pairing. The 95% percentile bootstrap resamples *10 seeds* 20,000 times
with a fixed analysis seed; exact two-sided sign-flip p enumerates 1,024
sign assignments (these are exploratory comparisons, not corrected for
all comparisons).

| Arm − legal random | Difference | 95% bootstrap CI | Exact p |
|---|---:|---|---:|
| blind mutation | −0.060 | [−0.143, +0.027] | 0.242 |
| binary search | +0.037 | [−0.060, +0.160] | 0.709 |
| privileged graded search | +0.003 | [−0.057, +0.060] | 1.000 |

Exploratory contrasts: binary versus blind mutation +0.097
(CI [−0.013, +0.187], p = 0.127); graded versus binary −0.033
(CI [−0.127, +0.033], p = 0.711).
The retrieval arm has zero novel solutions *by definition* because
retrieved pictures are from the excluded prior-solution library.

## Adversarial verdict

1. **Legacy unfair-baseline artifact invalidated as comparative evidence.**
   Legal random reaches 0.583 novel/task, not the historical malformed
   random arm's 0.27. Do not cite the old +0.22 as evidence.
2. **No reliable evidence of a better candidate generator.** Binary search's
   observed advantage is small and unstable across seeds; its CI spans
   both harm and benefit. Failing to reject zero is not proof of equivalence.
3. **The privileged upper bound also fails to improve novelty** in this
   tested small grammar. It paid an additional eight graded calls/task,
   so its information and compute costs are not equivalent.
4. **Tiny task universe and engineered priors are dominant limitations.**
   Only 63 nonempty stroke sets exist, and the library is oracle-built.
   These results say nothing about human-level creativity or learned
   long-horizon reasoning.
5. **Next falsifier:** benchmark the actual backprop-free creature on
   the stateful acquire/carry/place task and unseen goal pairs (#112).
   Include legal random, flat policy, engineered option gate, and a
   separately labeled oracle; require preregistered learning/retention
   gains across 10 seeds before asserting transfer.

**Interpretation:** This is a reproducible *negative/inconclusive*
comparison of engineered novelty methods at one fixed budget, not a
demonstration that search cannot help on other problems or budgets.
