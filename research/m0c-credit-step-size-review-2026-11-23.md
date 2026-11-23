# Adversarial review of the M0c credit audit: step-size confound (2026-11-23)

**Status: exploratory, in-sample. Advancement remains HOLD M1–M8.** Reviews [the executed credit audit](m0c-sensory-credit-results-2026-11-18.md) (PR #206). Does not replace it or its raw results.

**Inspected source:** main `bcd3c87e561c8e9dbc59b178286b4b22edf604c7`; `game/world/brain.js` (`Brain` constructor, `encode`, `act`, `learn`), `game/world/stateful_credit_probe.mjs`, `game/world/stateful_construct.mjs::observe`, `research/analyze_m0c_credit_probe.py`, `research/results/m0c-credit-audit-10seed-2026-11-18.json`. Node 22, Linux container, local (not CI).

## 1. Reproduction (code-observed)

`node game/world/stateful_credit_probe.mjs --out OUT 1 2 3 4 5 6 7 8 9 10` reproduced every arm/seed `curve` of the archived file exactly (0 of 60 rows differ). The archived numbers are deterministic and correct as computed.

## 2. Confound: the effective learning rate is about 40–80× below nominal

`Brain.learn` divides `lrP`/`lrV` (0.05) by `1 + hh`, a running mean of |h|². On the construct observation, |raw input|² = 5 and |hidden|² ≈ 35–78 at the start state (seeds 1–3 of `createModel`), so the actor step is ≈ 0.0006–0.0012. The `GAINS` were tuned for Brain World's retina input, not this adapter. Scaling `lrP` and `lrV` together (`node game/world/stateful_credit_lr_sweep.mjs SCALE`, seeds 1–10, same 4,000 decisions, 12 frozen trials):

| Arm (mean final delivery) | ×1 (archived) | ×2 | ×4 | ×8 | ×16 |
|---|---:|---:|---:|---:|---:|
| native-three | 10.0% | 60.8% | 84.2% | **98.3%** | 0% (6/10 seeds diverged) |
| native-two | 97.5% | 100% | 99.2% | 100% | 18.3% |
| mask-goal | 9.2% | 50.8% | 95.0% | 69.2% | 0% (4/10 diverged) |
| trace-one-step | 0% | 7.5% | 28.3% | 50.0% | 60.0% |
| no-bootstrap | 2.5% | 2.5% | 2.5% | 0% | all 10 diverged |
| zero-feedback | 2.5% | 2.5% | 2.5% | 2.5% | 2.5% |

Divergences are `nonfinite TD error` rows, kept as errors, not dropped. Per-seed counts are printed by the script.

**Consequences for the 2026-11-18 interpretation:**

- The 10% vs 97.5% three/two-action gap and the Round 24 "Brain learning is bottlenecked vs tabular Q" reading are largely a **step-size artifact**. At ×8 the unchanged learning rule reaches 98.3% on the three-action task.
- The ablation ranking is **not robust to step size**: trace-one-step is worst at ×1 but beats native-three at ×16. "Eligibility/TD ablations reduce success" holds only at the inherited step size.
- At ×8 native-three has goal counterfactual L1 **0.0082** (×1: 0.0844) and mask-goal reaches 69–95%: success is goal-insensitive memorisation of one action sequence, as the protocol predicted for a constant-goal task.
- **zero-feedback is tautological**: with r = 0 and a zero critic, δ ≡ 0, so no weight changes. Its final score equals the untrained score seed for seed ([0,0,0,1,0,1,0,0,0,1]/12). It cannot test anything beyond "no update ⇒ no change".

## 3. Further findings

- **Input-layout mismatch (code-observed).** `observe` writes 84 construct channels into Brain's 107-wide input whose indices carry Brain World meanings. The multiplicative "cochlea" gain inputs (indices 47–49) fall on item-plane cells (2,4),(3,4),(4,4); the fovea patch (50–74) is exactly the goal plane; about 11% of hidden fan-in (≈550 of 5,000 draws) reads indices 84–106, which are always zero. Harmless on this fixed task (item never on row 4) but would gate hidden units by item position in any family that puts the item on the bottom row.
- **Statistics.** The analyzer reports only within-arm before/after CIs. Between-arm paired differences at ×1 (seed bootstrap, 10,000 draws): native-three − trace-one-step +10.0 pp [+4.2, +18.3]; − no-bootstrap +7.5 pp [+0.8, +16.7]; − mask-goal +0.8 pp [−5.0, +7.5]. Seed 8 contributes 5 of native-three's 12 successes; no multiple-comparison correction.
- The sweep is **in-sample tuning on the scored task**, two-factor (`lrP` and `lrV` together), with five grid points. It shows sensitivity, not a selected setting.

## 4. Decision and next falsification test

HOLD M1–M8. No claims.tsv change. Before any further credit/ablation conclusion on construct tasks:

1. Select the step size (or a normalisation that does not scale with hidden count) on **development** tasks only, then freeze it; report ablations across at least two step sizes.
2. Replace zero-feedback with a shuffled-reward control that keeps nonzero δ.
3. Fix or document the input mapping so gain and fan-in indices land on intended construct channels, or ablate the hidden layer.
4. Re-run the goal-varying / heldout-family test from the 2026-11-18 decision with the frozen step size.
