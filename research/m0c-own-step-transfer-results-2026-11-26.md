# M0c own-step and wide-goal transfer protocol: results (2026-11-26)

**Status: exploratory. 20 evaluation seeds, local container run. Advancement remains HOLD M1–M8, and claims.tsv is unchanged.**

This note executes the [preregistration](m0c-own-step-transfer-protocol-2026-11-26.md) without amendment.

**Provenance (code-observed).**
- Command: `node game/world/own_step_transfer_protocol.mjs --out OUT`, Node 22, Linux, 25 min.
- Run at commit `5117332` (the preregistration commit) on a clean tree.
- Raw data: [brain-result/1](results/m0c-own-step-transfer-20seed-2026-11-26.json). Analysis: [analysis](results/m0c-own-step-transfer-analysis-2026-11-26.json).
- 82 own-step selection rows and 10 wide selection rows diverged; they are kept and score 0. No eval row diverged.
- Every `ok` training row applied its η to within 1e-9 relative, and every goal-masked row stayed at or below 1/k. The analyzer gates passed.

## Step selection (dev seeds only)

Mean dev success by matched per-weight step η:

| Arm | 0.004 | 0.008 | 0.016 | 0.032 | 0.064 | 0.128–0.512 |
|---|---:|---:|---:|---:|---:|---:|
| native | **43.3%** | 38.9% | 0† | 0† | 0† | 0† |
| mask-goal | **25.6%** | 25.6% | 0† | 0† | 0† | 0† |
| trace-one-step | 28.3% | 43.9% | **49.4%** | 19.4% | 0† | 0† |
| no-hidden | 1.7% | 3.3% | 10.0% | 34.4% | **54.4%** | 0† |
| wide native (19 goals) | **62.2%** | 32.5% | 0† | 0† | 0† | — |

† Diverged rows, which score 0.

Selected steps: native 0.004, mask-goal 0.004, trace-one-step 0.016, no-hidden 0.064, wide 0.004. No arm's optimum is at the extended grid edge (0.512), so no own-step contrast is inconclusive.

## Part A: each arm at its own step (3 trained goals)

| Arm (η) | Trained | Heldout |
|---|---:|---:|
| native (0.004) | 67.2% | 8.8% |
| mask-goal (0.004) | 28.6% | 0.0% |
| trace-one-step (0.016) | 66.2% | 12.1% |
| no-hidden (0.064) | **77.9%** | 6.9% |

Native and mask-goal rows are identical to Round 29, which used the same step and code.

## Part B: wide-goal transfer (19 trained goals, 5 interior heldout goals)

The goal-blind ceiling is 1/19 (5.3%) on trained goals and 1/5 (20%) on heldout goals.

| Arm (η 0.004) | Trained | Heldout |
|---|---:|---:|
| native | 63.3% | 21.4% |
| mask-goal | 4.7% | 0.2% |
| flag-only | 39.2% | 4.1% |

Native heldout success by goal: [2,2] 33%, [1,1] 23%, [3,1] 23%, [3,3] 17%, [1,3] 12%. Before training it was 0.7%.

## Preregistered tests (exact paired sign-flip, Holm over 5)

| # | Test | Mean diff | 95% bootstrap CI | Holm p |
|---|---|---:|---|---:|
| A1 | hidden-layer: native@0.004 − no-hidden@0.064 | **−10.7 pp** | [−17.9, −3.6] | 0.035 |
| A2 | eligibility: native@0.004 − trace-one-step@0.016 | +1.0 pp | [−8.7, +13.5] | 0.88 |
| A3 | goal-use: native − mask-goal | +38.6 pp | [+31.8, +45.7] | 9.5e-6 |
| B1 | native heldout − 1/5 | +1.4 pp | [−1.3, +4.1] | 0.73 |
| B2 | heldout goal-use: native − mask-goal | +21.2 pp | [+18.4, +23.9] | 9.5e-6 |

Descriptive:
- Native trained − 1/19: +58.1 pp, CI [+52.0, +63.7].
- Flag-only heldout − 1/5: −15.9 pp, CI [−18.3, −12.8].
- Native − flag-only heldout: +17.3 pp, CI [+13.8, +20.5].

## Falsifier outcomes

1. **Hidden layer: reversed.** With each arm at its own dev-selected step, no-hidden beats native by 10.7 pp on trained goals (Holm-significant). "The hidden layer helps" does not survive. Round 29's hidden-layer effect came from holding no-hidden at native's step.
2. **Eligibility: not supported.** At their own steps, native and trace-one-step do not differ.
3. **Goal use on trained goals: supported** in both families. Native exceeds the goal-blind ceiling by +33.9 pp (3 goals, Round 29) and +58.1 pp (19 goals).
4. **Heldout transfer: not supported.** Native reaches 21.4% on never-trained interior goals, which is not distinguishable from the 1/5 a goal-blind policy can reach. B2 passes only because the goal-blind arm falls far below its own ceiling.

## Adversarial corrections

- **Native is goal-sensitive on heldout goals, but this gains nothing over a goal-blind policy.** Its `maxGoalsPerRepeat` on heldout goals is 2–4, which a goal-blind policy cannot exceed past 1. So the heldout behaviour does depend on the goal input. But total success sits at the goal-blind ceiling. Untrained goal cells shift its routes without aiming them.
- **The at-goal flag alone does not transfer.** Flag-only reaches 39.2% on trained goals but 4.1% on heldout goals. That is below the 1/5 ceiling, so "wander until the flag fires, then drop" is not what was learned.
- **The no-hidden win is narrow.** It is one family, 8,000 decisions, a learning rate tuned per arm on 5 dev seeds, and a 3-goal train split. No-hidden's optimum (0.064) sits just below a diverging step (0.128), and native's (0.004) just below 0.008. Neither arm has a wide usable step window.
- **Selected steps diverge often.** 82 of 200 own-step selection rows diverged, all at steps above each arm's optimum.

## Next falsification test

1. Move to independently generated heldout families (#112/#153/#154). These have different geometry, start, item and walls, and each gets its own goal-blind ceiling.
2. Make goal coding relational (for example, an agent-relative goal offset) as a preregistered adapter arm. Test whether transfer to untrained cells then exceeds 1/k. This would separate "Brain cannot transfer" from "a one-hot goal plane cannot transfer".
3. Repeat the no-hidden versus native comparison with each arm at its own step on the wide family. Part B held all arms at native's step.
