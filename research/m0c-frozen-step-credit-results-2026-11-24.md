# M0c frozen-step credit protocol: results (2026-11-24)

**Status: exploratory. 10 evaluation seeds, local container run. Advancement remains HOLD M1–M8, and claims.tsv is unchanged.**

This note executes the [preregistration](m0c-frozen-step-credit-protocol-2026-11-24.md), including its appended Amendment 1, which follows up the [Round 27 review](m0c-credit-step-size-review-2026-11-23.md).

**Provenance (code-observed).**

- Command: `node game/world/stateful_credit_protocol.mjs --out OUT 1 2 3 4 5 6 7 8 9 10`, Node 22, Linux.
- The run used the working tree on top of `dcd307d`. That tree was committed unchanged in the PR that adds this note; the raw `commit` field reads `dcd307d`.
- Raw data: [brain-result/1](results/m0c-frozen-step-protocol-10seed-2026-11-24.json). Analysis: [analysis](results/m0c-frozen-step-protocol-analysis-2026-11-24.json).
- All 160 rows are `ok`: 20 selection rows and 140 eval rows. No run diverged.

## Run 1 failure, preserved

The first full run used a yoked-reward arm whose tape came from the same seed's native learner. That arm reproduced native exactly in all 20 seed × scale rows: same initialisation and same RNG means the same actions, so the tape reward equals the learner's own reward.

The raw output is kept as [run 1](results/m0c-frozen-step-run1-degenerate-yoke-2026-11-24.json). The current analyzer rejects it. Amendment 1 switches the tape to a donor learner with a different initialisation. Every other arm reproduced exactly in run 2.

## Step-size selection (development goals and seeds only)

Mean development success by step scale:

| ×1 | ×2 | ×4 | ×8 |
|---:|---:|---:|---:|
| 3.3% | 1.7% | 6.7% | **19.4%** |

×8 was selected by the preregistered rule. The analyzer recomputed the choice from the raw rows. The grid tops out at ×8, so a larger optimum is possible but was not tested.

## Frozen evaluation

Trained goals are [1,1], [4,0] and [2,1]. Heldout goals are [1,0] and [3,0] and were never trained. Each score is the mean over 10 seeds of 12 frozen trials per goal.

| Arm | Trained goals ×1 | ×8 | Heldout goals ×1 | ×8 | Effective actor step ×8 |
|---|---:|---:|---:|---:|---:|
| native | 3.3% | 40.0% | 2.1% | 12.1% | 0.0081 |
| aligned (gain cells moved) | 3.1% | 40.0% | 2.1% | 11.3% | 0.0084 |
| mask-goal | 3.3% | 31.7% | 1.7% | 1.3% | 0.0104 |
| yoked-reward (donor tape) | 3.3% | 2.5% | 3.7% | 4.2% | 0.0078 |
| trace-one-step | 1.9% | 66.7% | 1.3% | 22.5% | 0.0087 |
| no-bootstrap | 1.9% | 2.5% | 2.5% | 5.8% | 0.0074 |
| no-hidden | 3.9% | 72.5% | 3.7% | 10.0% | **0.0738** |

At ×8, native is bimodal across seeds. Four seeds stay at 0–6% and six reach 31–92%.

## Preregistered contrasts (trained goals, exact paired sign-flip, Holm over 12)

| Contrast at ×8 | Mean diff | 95% bootstrap CI | Holm p |
|---|---:|---|---:|
| goal-use (native − mask-goal) | +8.3 pp | [−13.3, +32.2] | 1.00 |
| reward-contingency (native − yoked) | +37.5 pp | [+14.4, +59.7] | 0.26 |
| eligibility (native − trace-one-step) | −26.7 pp | [−53.3, −0.8] | 0.90 |
| bootstrap (native − no-bootstrap) | +37.5 pp | [+16.7, +58.3] | 0.26 |
| gain-layout (aligned − native) | −0.0 pp | [−3.1, +2.2] | 1.00 |
| hidden-layer (native − no-hidden) | −32.5 pp | [−51.7, −14.4] | 0.19 |

At ×1, every contrast is within ±1.4 pp with Holm p = 1.00, because nothing learns at the inherited step size.

**No contrast survives Holm correction at either scale.** With 10 seeds and 12 tests, Holm significance needs every seed to share the sign of the effect. This design is underpowered for effects of this size.

## Falsifier outcomes

1. **Goal-conditional learning at the frozen step size: not supported.** Native beats goal-masked by only 8.3 pp on trained goals, and the CI includes 0. Goal-masked reaches 31.7%, close to the one-third a single memorised goal would give. The goal-insensitive-memorisation reading from 2026-11-23 stands.
2. **Heldout goal use above goal-blind: supported descriptively.** Native − mask-goal on heldout goals is +10.8 pp, CI [+3.3, +19.2]. The absolute level is low (12.1%). Native's carrying-state goal L1 is 0.32, against 0 for masked. This is one geometry and not Holm-tested (the preregistration made it a CI-only criterion).
3. **No mechanism claim is justified.** Each of the reward-contingency, bootstrap, eligibility and hidden-layer contrasts is nonzero by bootstrap CI only at ×8, and none passes Holm at either scale.

## Findings and corrections

- **Inherited step size: no learning at all.** At ×1, every arm sits at the ~3% untrained level on varying goals. The ×1 ablation rankings in the 2026-11-18 audit therefore describe a learner that barely moves.
- **Eligibility traces hurt at ×8 (bootstrap CI only).** Trace-one-step 66.7% beats native 40.0%, which agrees with the Round 27 ×16 reversal. The λ = 0.85 trace spreads credit across goal-specific paths.
- **Removing the hidden layer helps, but this is confounded.** `no-hidden` reaches 72.5%, yet its running |h|² normaliser is ~9× smaller, so its effective step (0.074) is ~9× native's. Layer and step size are not separable here. The next test needs a normaliser that is independent of hidden width, or matched effective steps.
- **Gain-input contamination is harmless on this family.** Aligned equals native to within 1 pp, as predicted: the item only reaches row 4 after a misplaced drop.
- **The yoked control now works.** The donor tape matched the learner's own rewards on 12–37% of steps, mostly the shared step cost. Yoked does not learn (2.5% at ×8), so reward contingency matters descriptively.

## Next falsification test

1. Make the step size independent of hidden width: normalise by input count or use a matched effective step. Then repeat the hidden-layer and λ contrasts.
2. Use 20 or more evaluation seeds, or fewer preregistered contrasts, to reach adequate power.
3. Test whether goal use survives a training family where one memorised route cannot exceed 1/k, for example by blocking routes between goals.
4. Then move to independently generated heldout families (#112/#153/#154).
