# Construction and novelty: ten-seed diagnostic and adversarial review

**Date:** 2026-11-12. **Status:** executed diagnostic, **not** a confirmed creative-composition result.
**Source:** [GitHub Actions run 43152025176](https://github.com/faheemkhaskheli9/Brain/actions/runs/43152025176),
commit `e212ebf`, Node 22 and Python 3.12; both jobs completed and schema checks passed.

This diagnostic tests Gates A/B of [the existing implementation plan](../adversarial-implementation-plan.md). The backprop-free creature is independent of an LLM; engineered generators, rewards, oracle enumeration and action interfaces must never be described as learned.

## Frozen protocol and artifacts

- Seeds **1–10**, paired by seed. Unit of statistical replication: **seed**, not 30 evaluation tasks or five attempts nested within each seed. No posttest tuning.
- Fair novelty: **30 evaluation tasks per seed × 8 validator calls**, five arms; the graded arm additionally gets **8 privileged penalty-score calls per task**.
- Construction: **64 training tasks per seed**, **exactly 10,000 primitive training decisions** per trained arm, **30 evaluation tasks × 5 attempts** per seed. Evaluation uses detached checkpoints with independent RNG. History masks consult only already selected strokes.
- GitHub artifact `construction-novelty-fair-10seed`: `novelty-fair-10seed.json`, SHA-256 `ac21e69159654b143ca52db0d78d82a4d142eb7fb8cc2405bdb4e865a085fe7d`.
- GitHub artifact `construct-learner-10seed`: `construct-learner-10seed.json`, SHA-256 `01430ee1066f4ead453c9f495233722baf1581e6514c3fe2404916fd6d6a40d2`.
- Raw candidate/action traces, all seeds, summary scores, wall time and failure statuses are retained in the artifacts linked from the Actions run.

## A. Matched-query fair novelty (mean counts per task)

| Arm | Valid | Novel | Validator calls | Additional privileged grader calls |
|---|---:|---:|---:|---:|
| Random-valid | 2.287 | 0.583 | 8 | 0 |
| Retrieval | 2.070 | 0.000 | 8 | 0 |
| Blind mutation | 1.963 | 0.523 | 8 | 0 |
| Binary search | 2.227 | 0.620 | 8 | 0 |
| Privileged graded search | 2.313 | 0.587 | 8 | 8 |

Across 10 paired seeds, binary-feedback search minus random-valid novelty averaged **+0.037/task**;
seed-resampled percentile bootstrap 95% interval **[-0.060,+0.160]** (20,000 resamples, fixed RNG);
exact paired sign-flip **p=0.709**. Graded-search difference was **+0.003/task**, 95% interval approximately **[-0.057,+0.063]**; privileged feedback does not establish an advantage. The strict novelty metric excludes *every enumerated training solution*, within a space of at most `2^6-1=63` nonempty stroke sets. Approximately **73%** of evaluated tasks had at least one unseen, valid drawing class. These ceilings make open-ended creativity claims invalid.

**Conclusion:** no significant or scientifically persuasive novelty advantage over matched legal random. The outcome is negative/inconclusive, not proof of composition.

## B. Ten-seed backprop-free construction learner

| Arm | Held-out success | Held-out novel per attempt | Training decisions |
|---|---:|---:|---:|
| Learner, raw actions, goal visible | 0.241 | 0.011 | 10,000 |
| Learner, history mask, goal visible | 0.517 | 0.021 | 10,000 |
| Learner, raw actions, **goal withheld** | 0.549 | 0.001 | 10,000 |
| Learning disabled, raw actions | 0.140 | 0.014 | 10,000 nonlearning interaction |
| Stepwise random, raw | 0.140 | 0.014 | 0 |
| Stepwise random, history mask | 0.218 | 0.026 | 0 |
| Candidate-generating random-valid | 0.279 | 0.023 | 0 (noninteractive candidate) |

The history-masked learner minus history-masked random scored **+0.299 absolute success**,
seed-cluster bootstrap 95% interval **[+0.205,+0.393]**,
exact paired sign-flip **p=0.00195**. This supports a learned *task-specific drawing policy* under the supplied representation.

**Critical adversarial finding:** the **goal-withheld, raw-action learner (0.549)** beat the comparable **goal-visible, raw-action learner (0.241)** by **0.308 absolute** (paired seed bootstrap 95% interval on goal-visible minus goal-withheld roughly **[-0.353,-0.262]**). Both use the same raw action protocol; different goal information is the tested factor. The task's validation/solution classes allow a policy to succeed without demonstrating meaningful goal conditioning. A direct goal-swap counterfactual and a history-masked no-goal arm are **not** in this preregistered run, so do not overinterpret the mechanism.

The history mask itself boosts *random* held-out success from **0.140 to 0.218**. Legal masking is a substantive intervention, not just a runtime optimization. Candidate random-valid is not decision-level comparable (it produces a complete candidate without submit/action cost) and remains a labeled search upper bound.

**Conclusion:** the learner has evidence of experience-dependent success against matched nonlearning controls, **not** of goal-conditioned composition, reusable options, novel creativity or AGI. No positive claim should be promoted to `research/claims.tsv`.

## Adversarial review: failures and required falsifiers

| Severity | Attack / confound | Decision |
|---|---|---|
| **P0** | Goal-withheld policy beats the goal-visible policy under the same raw-action rules | **Mechanism gate fails** for goal dependence; use counterfactual goal swaps and a new frozen benchmark family before any claim |
| **P0** | Six-stroke enumeration and symmetry yield a small novelty universe | Keep 63-subset task as a unit test only; do not claim open-ended creativity |
| **P0** | Stepwise random, masked random and full-candidate random have different action protocols | Label and compare within matched protocols only; preserve action/feedback audit |
| **P0** | One metric across repeated attempts falsely treats 1,500 episodes as independent | Paired seeds (n=10) are the only independent replicate units for this report |
| P1 | Syntactic history masking changes performance markedly | Train, test and compare masks symmetrically; test no-goal + mask in a **new exploratory** protocol |
| P1 | Novelty metric can be zero even when valid outputs are useful | Report validity, distinctness, opportunity ceiling and costs separately |
| P1 | Frozen random streams or train/eval order may leak | Keep detached checkpoint and reversal-order CI gates; preserve complete per-arm RNG and split seed |
| P1 | Unordered stroke sets can mimic temporal skill composition | Use separately implemented acquire/carry/place transitions, impossible goals, interruptions and held-out transition rules |
| P1 | State-based Q-learning or hand-coded observation-based routing could solve the dependent task | Compare tabular Q, flat Brain, heuristic, fixed script and options under matched primitive budgets |

## Gate disposition and next step

- **Gate A engineering checks:** implemented and passing; ten-seed diagnostics now archived. **Mechanism/novelty claims rejected**, despite positive learned-versus-random construction success.
- **Gate B infrastructure:** stateful carry environment and equal-budget flat/tabular controls implemented and CI-tested (PR #184, merge `5f6b4d`); the **full ten-seed dependent-task baseline experiment remains outstanding**.
- **Gate C learned options:** **not implemented/validated** because the preregistered preceding gates do not yet justify a confirmatory option mechanism. Do not retrofit test seeds or thresholds to produce a positive result.

**Next action:** run the Gate B baseline diagnostic with its predeclared 10 seeds, 40 train / 12 dev / 30 held-out tasks and 10,000 primitive train decisions per trained arm; select the strongest non-oracle comparator on development only. Only after that should a new goal-dependent option task be frozen and learned initiation/termination be tested as a distinct registered mechanism. Negative results must be retained.
