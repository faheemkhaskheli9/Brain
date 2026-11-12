# Stateful option exact primitive-decision budget audit

Date: 2026-11-12. Status: correctness intervention awaiting CI verification. Related issues: [#112](https://github.com/faheemkhaskheli9/Brain/issues/112), [#153](https://github.com/faheemkhaskheli9/Brain/issues/153), [#154](https://github.com/faheemkhaskheli9/Brain/issues/154). Builds on frozen-scoring PR [#195](https://github.com/faheemkhaskheli9/Brain/pull/195), which itself builds on main commit `49e2c6f1`. Initial M0b code commit: `aab50b1d8ad159861f0aa5b47bae52dab86ca916`.

## Source-grounded problem

Previously, `trainPhase` in [stateful_options.mjs](../game/world/stateful_options.mjs) added the full length of a completed episode, even if its requested training budget had already been reached during that episode. Output metadata even specified episode-boundary overshoot. The reported requested budget was **not** an exact count of learner decisions. Also, EXIT consumes one policy decision but no environment step; a privileged BFS oracle reports a path without learning or stepping as a normal policy. Existing comparisons must not conflate these costs.

## Implementation hypothesis and decisions

1. Add an optional positive safe-integer `maxDecisions` to `episode`; default behavior and natural horizon remain unchanged. Include EXIT, movement, failed pickup/drop and other attempts in decisions; report environment steps separately.
2. Call `episode` with the *remaining* primitive-decision allowance. Reject zero-progress or over-budget results; report exactly how many final episodes were truncated.
3. Treat experiment-budget truncation differently from a genuine environment timeout: do not award an artificial failure penalty on budget cutoff. When the *same option* remains active, bootstrap the next-state value while ending the current eligibility trace. An option change still terminates the previous option's trace as before.
4. Forbid a capped privileged oracle call; oracle search is a feasibility ceiling, not a comparable online learner.
5. Preserve prior historical result artifacts; new runs must be labeled as post-cap results and compared at actually matched interaction budgets. No new held-out performance, intelligence or AGI result is claimed.

## Falsification and tests

In [test_stateful_options.mjs](../game/world/test_stateful_options.mjs), exercise exact caps 1, 39, 80, 81, 137 for flat/options/no-gate/random; invalid caps 0, negative, fractional, infinite and NaN; and the capped-oracle rejection. Check `decisions == envSteps + exits`, physical steps never exceed `maxSteps`, and all trained arms report exact 1, 17, 79, 81 and 137 **pretraining and adaptation** decisions. Repro: `node game/world/test_stateful_options.mjs` and `node game/world/stateful_options.mjs 1 --train-steps 17 --adapt-steps 13 --train-tasks 3 --eval-tasks 3 --repeats 1 --out /tmp/brain-budget.json`, then `python research/result_schema.py --check /tmp/brain-budget.json`.

**Verification at note creation:** no local checkout available, so source patch was committed and CI remains the independent executable check. Do not present source inspection as an executed test.

## Adversarial limitations and next priority

- Exact counts do not alone make a test statistically fair. Partial-episode cutoff position changes TD bootstrapping and can bias learning, so compare boundary policies on development tasks and report truncated-attempt fractions.
- Dormant option eligibility may persist across separate episodes. Audit resets before using retained options as evidence of continual learning.
- Current tiny generated goal families, weak conventional-RL baseline, uncharged BFS expansions, hidden compute, and missing full failure rows remain M0c/M0d gaps.
- M0a's clone-based scoring does not serialize opaque RNG closures; future exact checkpoint work needs restorable RNG state.
- No novel learned-option initiation, open-ended planning, cross-domain transfer, or AGI was demonstrated.

Scientific formalism: Sutton, Precup & Singh (1999), [DOI 10.1016/S0004-3702(99)00052-1](https://doi.org/10.1016/S0004-3702(99)00052-1) defines temporally abstract options; it does not establish the efficacy of this implementation. Reuse [brain-result/1](result_schema.py), [claims register](claims.tsv), and [continual guard](continual_guard.py), rather than introducing duplicate evidence infrastructure.

## Adversarial correction: confirmatory analyzer protocol (2026-11-12)

A follow-up source audit of [analyze_stateful_options.py](analyze_stateful_options.py) found it still accepted `limit <= decisions < limit + 81` (the historical whole-episode overshoot tolerance). An M0b run could therefore pass its scientific budget gate even when exceeding the exact cap. The evidence checker now **requires equality** for records explicitly declaring `trainingOvershoot: "none (exact cap)"`. Legacy/missing markers are still interpreted under the older bounded overshoot protocol for historical reproducibility, but are flagged `budget_protocol: "legacy-overshoot"` and can no longer receive the new confirmatory **pass** verdict, even if their effect-size statistics look favorable.

Synthetic tests distinguish the two modes and reject a one-decision overrun and unrecognized protocol. This is a *method-integrity repair*, not newly measured generalization. Historical raw files and the original negative conclusions remain unchanged. GitHub CI must verify the patch before it is reported as tested.

## Measured exact-budget outcome and permanent archive (2026-11-12)

The new 10-seed workflow has **passed as a workflow but failed its research advancement gate**: all non-oracle policies scored zero held-out completions, while the privileged BFS feasibility oracle scored 1.0. This is a hard negative learning result, not an implementation failure or a reason to relabel invalid-action reductions as skill learning. See [the complete source-grounded result report](stateful-options-exact-negative-2026-11-12.md) and the lossless [raw archive](results/stateful-options-exact-2026-11-12.tar.br), now preserved in Git. M0c should first establish learnability with nonprivileged public-observation controls; M1 remains on HOLD.
