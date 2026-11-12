# Reward-modulated structural-plasticity pilot: 10-seed result (2026-11-12)

**Scope:** controlled *toy* 24-feature, two-action association; this is not evidence of human-neuron-level structural plasticity, language understanding or learned body control. The initial topology was deliberately **missing the only predictive cue**, so fixed-topology accuracy near chance is an expected handicap. No new edges were created in the 78-region macroscopic anatomical graph.

## Preregistered protocol and provenance

- Source: `research/structural_plasticity.py`, `sparse_brain_tasks.py`, `learn_sparse_brain.py`; source revision **`a2ce54102a23489ae8b0956f384f3d2472d21ab6`**, before confirmatory run and without tuning on reserved seeds.
- Prior exploratory development seeds **0–9**, not included in confirmation. The protocol was frozen in [`sparse-plasticity-pilot.md`](sparse-plasticity-pilot.md) before running seeds **101–110**.
- Each learned arm received **1,000** training episodes/actions, each with one binary verifier reward (`+1` correct, `-1` wrong). All arms were evaluated frozen on **400** unseen, cue-amplitude-shifted test instances per seed. A separate **400-trial** train-distribution evaluation was performed.
- All six arms ran the same observations, rewards availability, evaluation inputs and 4-edge synapse budget. Random rewiring shares the edge-turnover schedule but samples a random candidate and sign, not reward-based candidate ranking. Shuffled-feedback arm sees unrelated reward labels. The handwired initial-topology arm has privileged information about which feature predicts the target.
- `brain-result/1`: [`results/structural-plasticity-2026-11-12.json`](results/structural-plasticity-2026-11-12.json) contains **all 60 arm × seed runs**, scores, time, growth/pruning counts, operation counts, topology and SHA-256 checkpoint fingerprints. Every run status was `ok`.

Reproduce from repository root:

```bash
python research/learn_sparse_brain.py --seeds 101 102 103 104 105 106 107 108 109 110 --train-steps 1000 --eval-trials 400 --commit a2ce54102a23489ae8b0956f384f3d2472d21ab6 --out /tmp/sparse-plasticity.json
python research/result_schema.py --check /tmp/sparse-plasticity.json
```

## Frozen held-out outcomes

| Arm | Held-out success | Mean new / pruned synapses | Early / final 100 training successes | Mean weighted products (train+eval) | Mean candidate evaluations |
|---|---:|---:|---:|---:|---:|
| **Evidence-guided new connections** | **1.000** | 2.1 / 2.1 | 0.517 / 0.993 | 7,200 | 43,958 |
| Random connection turnover | 0.648 | 10.6 / 10.6 | 0.490 / 0.610 | 7,199 | 41,947 |
| Fixed topology, local weight updates | 0.513 | 0 / 0 | 0.497 / 0.493 | 7,200 | 0 |
| Frozen initial topology | 0.498 | 0 / 0 | 0.503 / 0.499 | 7,200 | 0 |
| Reward shuffled before learning | 0.503 | 12.0 / 12.0 | 0.502 / 0.501 | 7,200 | 42,429 |
| **Privileged topology (correct cue initially wired)** | **1.000** | 0 / 0 | 0.836 / 0.994 | 7,200 | 0 |

These are mean per-seed fractions, not performance on real-world perception. At inference, at most **four** synaptic weights exist among **48** possible input-output pairs (8.33% connectivity density). Candidate scoring is training-only, but **can examine up to 64 cached candidate pairs**, making learning more expensive than a fixed-topology policy. At this scale NumPy or a dense vectorized baseline may be faster on wall-clock despite fewer stored trained weights.

### Predeclared primary comparison

**Evidence-guided minus random growth:** +0.35225 absolute held-out success, paired seed-bootstrap 95% interval **[+0.202, +0.49025]**; exact two-sided paired sign-flip **p=0.015625**, n=10. The result clears the proposed +0.10 absolute improvement, positive paired lower CI and p≤0.05 criterion on this toy setup.

Additional comparisons, interpreted cautiously:

- Versus fixed trained topology: +0.48725, 95% CI [+0.47275, +0.50075], p=0.001953.
- Versus frozen initial weights: +0.50250, 95% CI [+0.48625, +0.51700], p=0.001953.
- Versus shuffled reward: +0.49725, 95% CI [+0.48050, +0.51875], p=0.001953.
- Versus privileged topology: **0.000** improvement. Correct a priori connectivity learns equally well here, and needs no regrowth.

Paired CIs were obtained by resampling seed-level differences 5,000 times with seed 112. Sign-flip comparisons are descriptive across secondary arms; no multiple-comparison adjustment is claimed.

## Adversarial review

1. **Initial architecture is biased by construction.** Fixed topology lacks the predictive feature, while growth discovers it. This is direct evidence that rewiring can repair a *missing-edge defect*, not evidence that rewiring is generally better than a well-wired network. Privileged topology achieves identical accuracy without new synapses.
2. **Simplistic task:** the one-step binary cue rule is linearly separable; the input's informative feature index never changes. Moving from amplitude 1.0 to 0.5 is a small distribution shift, not true compositional transfer or unseen skill learning. The mechanism has not been evaluated on natural images, sounds, text or bodily movement.
3. **Growth and local learning are not biologically validated.** The score-function eligibility times reward prediction error is an engineered algorithm, the action softmax is designed, synapses use signed effective weights rather than identified excitatory/inhibitory cell types, and the task reward is a perfect verifier.
4. **Compute:** the evidence arm averaged ~43,958 potential-candidate evaluations per run, versus 7,200 existing-edge weighted operations. Its CPU time and energy advantage are **not established**. The model uses dict/cache operations, not synapse-local physical processes.
5. **No long-range anatomical reconnection:** new synapses are limited to a small toy input-to-action microcircuit; the human-inspired 78-region anatomy stays fixed. Dendritic geometry, growth constraints, axonal projections and real connectomic evidence remain absent.
6. **Verification boundary:** only frozen scoring was demonstrated. Delayed reward is unit-tested but not shown to improve delayed control tasks. Memory, catastrophic forgetting, repeated-error diagnosis and embodied closed-loop control are future hypotheses.

## Decision and next experimental gate

**Accept this as positive synthetic evidence of targeted structural repair under a fixed four-edge budget, not a general neuroscience or AGI result.** Maintain 24-input task as a regression fixture. Next, test variable cue identity, reversal and delayed reward; add a separate sparse local neuronal population and compare to same-capacity static/recurrent models. Use **fresh, precommitted holdout seeds/tasks** for those new hypotheses; do not tune and then re-label seeds 101–110 as confirmatory again.

Relevant hypotheses: **H149** (structural synapse turnover; open) and **H088** (pruning). Existing roadmap issues: #65, #112, #120, #136. No changes to their hypothesis-status values are warranted solely by toy success.