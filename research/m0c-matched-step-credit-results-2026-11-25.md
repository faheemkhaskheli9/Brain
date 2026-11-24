# M0c matched-step, one-drop credit protocol: results (2026-11-25)

**Status: exploratory. 20 evaluation seeds, local container run. Advancement remains HOLD M1–M8, and claims.tsv is unchanged.**

This note executes the [preregistration](m0c-matched-step-credit-protocol-2026-11-25.md) without amendment.

**Provenance (code-observed).**
- Command: `node game/world/matched_step_credit_protocol.mjs --out OUT`, Node 22, Linux.
- Run at commit `88dc3c9` (the preregistration commit) on a clean tree.
- Raw data: [brain-result/1](results/m0c-matched-step-20seed-2026-11-25.json). Analysis: [analysis](results/m0c-matched-step-analysis-2026-11-25.json).
- Rows: 140 selection and 160 eval. 24 selection rows and 3 eval rows diverged (nonfinite TD error); they are kept and score 0.
- Every `ok` training row applied η to within 1e-9 relative, and the analyzer gate passed.
- Every goal-masked row stayed at or below 1/k, with at most one goal delivered per repeat.

## Step-size selection (dev goals and seeds only)

Mean dev success by matched per-weight step η:

| Arm | 0.001 | 0.002 | 0.004 | 0.008 | 0.016 | 0.032 | 0.064 |
|---|---:|---:|---:|---:|---:|---:|---:|
| native (selects) | 2.8% | 16.7% | **43.3%** | 38.9% | 0† | 0† | 0† |
| mask-goal | 3.3% | 12.2% | 25.6% | 25.6% | 0† | 0† | 0† |
| trace-one-step | 3.9% | 3.9% | 28.3% | 43.9% | **49.4%** | 19.4% | 0† |
| no-hidden | 1.1% | 1.7% | 1.7% | 3.3% | 10.0% | 34.4% | **54.4%** |

† Mostly diverged rows, which score 0.

The selected η is 0.004 and the second-best is 0.008. Both were recomputed by the analyzer.

The per-arm optima differ: trace-one-step peaks at 0.016, and no-hidden peaks at 0.064, the top of the grid, so its true optimum may lie higher.

## Frozen evaluation (20 seeds)

The goal-blind ceiling is 1/3 on trained goals and 1/2 on heldout goals.

| Arm | Trained η 0.004 | Trained η 0.008 | Heldout η 0.004 | Heldout η 0.008 | Carrying goal L1 (η 0.004) |
|---|---:|---:|---:|---:|---:|
| native | **67.2%** | 50.8% | 8.8% | 5.2% | 0.50 |
| mask-goal | 28.6% | 31.0% | 0.0% | 0.0% | 0 |
| trace-one-step | 54.7% | 61.0% | 10.8% | 11.9% | 0.34 |
| no-hidden | 3.9% | 6.0% | 4.2% | 6.9% | 0.02 |

At η 0.004, native's trained-goal success is 44–97% on every seed.

At η 0.008, native scores 0 on 6 seeds:
- 2 diverged.
- 4 collapsed without diverging.

## Preregistered contrasts (trained goals, exact paired sign-flip, Holm over 6)

| Contrast | η | Mean diff | 95% bootstrap CI | Holm p |
|---|---:|---:|---|---:|
| goal-use (native − mask-goal) | 0.004 | +38.6 pp | [+31.8, +45.7] | 1.1e-5 |
| eligibility (native − trace-one-step) | 0.004 | +12.5 pp | [+5.8, +19.9] | 0.0024 |
| hidden-layer (native − no-hidden) | 0.004 | +63.3 pp | [+56.8, +70.3] | 1.1e-5 |
| goal-use | 0.008 | +19.9 pp | [+4.6, +34.3] | 0.050 |
| eligibility | 0.008 | −10.1 pp | [−30.8, +9.7] | 0.36 |
| hidden-layer | 0.008 | +44.9 pp | [+28.7, +60.4] | 0.0006 |

## Falsifier outcomes

1. **Goal-conditional learning at the selected step: supported in this family.**
   - Goal-use passes Holm.
   - Native trained success exceeds the provable goal-blind ceiling by +33.9 pp, CI [+27.5, +40.6].
   - No goal-blind policy, memorised or not, can reach 67%. This reverses the Round 28 "goal-insensitive memorisation" reading for the one-drop family only.
2. **Heldout goal use: the preregistered criterion passes, but generalisation fails.**
   - Native − mask-goal on heldout goals is +8.8 pp, CI [+5.4, +12.1], so the criterion passes.
   - Goal-masked scores 0% on heldout goals because its single memorised route ends on a trained goal.
   - Native's 8.8% is far below the 1/2 that a goal-blind policy could reach: native − 1/2 is −41.3 pp, CI [−44.6, −37.9].
   - The learner does not transfer to untrained goal positions.
3. **Mechanisms.**
   - The hidden layer is **supported under the matched per-weight step**: it is Holm-significant with the same sign at both η.
   - Eligibility is **step-size dependent**: it helps at 0.004 and is not significant at 0.008.

## Adversarial corrections

- **The hidden-layer result depends on the matching rule.** At a matched per-weight step, no-hidden barely learns. But tuned to its own dev optimum (η 0.064, grid edge), no-hidden reaches 54.4% dev success, above native's best of 43.3%.
  - The supported claim is narrow: "at the same per-weight step, the hidden layer helps".
  - "Brain needs its hidden layer" is not supported.
  - The preregistration flagged this limit (per-weight vs function-space step).
- **The trace-one-step advantage in Round 28 was largely a step-size effect.** With the step matched, eligibility helps at η 0.004. Trace-one-step's own optimum (0.016) is 4× native's. The λ = 0.85 trace effectively enlarges the step, so it destabilises sooner.
- **Native is fragile above its dev-best step.** At η 0.008, 6 of 20 seeds score 0, and at η ≥ 0.016 most dev runs diverge. The usable step window is narrow.
- **One-drop changes the task.** A misplaced drop is now terminal, so these numbers do not compare directly with Round 28.

## Next falsification test

1. Compare arms each at its own frozen dev-best step, with the grid extended above 0.064. Alternatively, match the function-space step (|h|²-normalised). Repeat the hidden-layer and λ contrasts.
2. Heldout transfer fails at the 1/2 ceiling. Train on more goal positions and hold out a few interior ones, then retest against the goal-blind ceiling.
3. Then move to independently generated heldout families (#112/#153/#154).
