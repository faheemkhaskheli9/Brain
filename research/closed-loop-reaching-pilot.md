# Sparse local learner controlling a toy joint: preregistered reaching pilot

Date: 2026-11-12  
Status: **implemented and evaluated**. This preregistration was committed before the frozen confirmatory seed run. [Measured 10-seed findings](closed-loop-reaching-results-2026-11-12.md) reject the preregistered superiority criterion and show substantial forgetting under motor reversal.

## What is new

`closed_loop_reach.py` connects the existing **backprop-free** `SparsePlasticPolicy` to the pre-existing `SensorimotorLoop` and `SimpleJointBody` without modifying Brain World's learner or the 78-region macroscopic structural graph:

```
engineered public visual target delta -> L_lgn / L_v1 SensoryPacket ---┐
L_hip position and velocity --------> L_s1 SensoryPacket -------------+-> signed 24-channel adapter
                                                                      -> 4-edge plastic input-to-action policy
                                                                      -> action 0/1, L hip drive -1/+1
                                                                      -> MotorDecoder -> SimpleJointBody (dt=0.1)
                                                                      -> next proprioception + verified post-action progress reward
                                                                      -> local eligibility updates and optional bounded synapse growth/pruning
```

Visual channel 0 contains **signed distance to a target**, not a real camera image. Channels 1–2 are independent, non-predictive distracting visual cues; channels 3–6 are joint positions/velocities. The other 17 inputs are zero. The learner never reads an oracle action, simulator hidden goal label, validation result, or other side information. However, the signed target-relative feature and `+1` progress / `-1` non-progress reward are **engineered strong priors**. This is a software controller, **not** neuron-scale cortical physiology or learned multimodal semantics.

The four initial synapses `(1,0), (1,1), (2,0), (2,1)` deliberately lack access to the goal-delta input (`feature 0`). The evidence-driven learner must discover a useful missing edge. The privileged topology has `(0,0), (0,1), (1,0), (1,1)` and serves as a **handwired upper bound**, not an independently learned anatomy.

### Training

`SparsePlasticPolicy` samples one of two actions from its existing sparse synapses. The actual joint receives that action through the existing bounded `MotorDecoder`. The environment observes the **resulting** hip position and returns `+1` only if target distance decreased; otherwise `-1`. The policy uses eligibility traces and a reward baseline to change weights; its bounded candidate cache proposes a missing connection when recent errors remain high. Max 4 stored edges, max 2 outgoing edges per active source, no trained dense input×action matrix, no macro-graph rewiring.

Delayed feedback arm batches **two physical actions** before one feedback event. Its candidate-growth schedule is normalized to feedback events, not physical actions; it receives **half as many reward values** as immediate-feedback arms, so it is not information-matched. It tests whether useful behavior remains possible with deferred feedback, not whether delayed learning is superior at matched label cost.

`run_episodes()` always uses 16 physical actions per episode, even after reaching the target. A goal counts as reached if the L hip is within absolute distance 0.07 of the target **at any step**. We also report final error, wrong-direction actions, number of new/pruned edges, weighted-product counts and training-candidate evaluations. This `ever hit` metric is weaker than a sustained hold or a learned stopping action.

### Fresh disjoint trial families

`reach_trials()` generates deterministic target values and two independent distractors. Train target distances are in [0.19, 0.36], development [0.29, 0.43], frozen evaluation [0.37, 0.52]. Each split/seed/episode ID is disjoint and independently seeded. Targets differ in *magnitude*, not action semantics or object identity; do not call this compositional generalization.

## Prespecified confirmatory experiment (freeze before evaluation)

**Selection and preregistration:** Initial troubleshooting/hyperparameter selection used exploratory seeds 0–5 and development splits only. **Reserved seeds 301–310** and their unseen held-out evaluation tasks must not be used for tuning this implementation. Record full results, including negative and failed runs; do not discard or rerun unfavorable seeds to choose winners.

| Setting | Fixed value |
|---|---|
| Reserved seeds | 301–310, 10 independent runs per arm |
| Per-arm training | 120 episodes × 16 actions = **1,920** physical actions |
| Training reward calls | Immediate: 1,920; delayed arm: **960** |
| Frozen source evaluation | 80 unseen train-distribution episodes, 1,280 physical actions |
| Frozen shifted-goal evaluation | 80 unseen eval-distribution episodes, 1,280 physical actions |
| Motion reversal baseline evaluation | 80 eval-distribution episodes; motor sign inverted without feedback updates |
| Development reversal adaptation | 40 dev-distribution episodes, 640 body actions, in a copy of the pretrained checkpoint |
| Frozen reversed/old retention after adaptation | 80 reversed eval and 80 ordinary source episodes |
| Maximum synaptic budget | 4; fanout 2; candidate cache ≤64 |
| Comparison arms | Evidence-guided growth; random growth; fixed missing-cue topology; frozen weights; privileged handwired topology; evidence growth with 2-step delayed reward |
| Growth and stabilization | `grow_every=80`, `warmup=80`, `min_prune_age=1000` reward calls, `min_error_rate=0.15`; delay2 uses 40, 40, 500 to scale to equal **physical actions** |

**Primary metric:** fixed-checkpoint `heldoutSuccess`, per seed, evidence growth minus random growth with identical decision/reward budgets. Preregistered success: paired mean ≥+0.10, paired-seed bootstrap 95% interval lower bound >0, two-sided exact sign-flip p≤0.05; all 10 seeds present and no hidden labels. This criterion may fail, and a failure must remain a result. Secondaries: shift-vs-source accuracy, new/pruned connections, candidate compute, final target error, two-step delayed feedback, and ability to adapt to inverted motor dynamics without destroying old skill. For reversal, compare `reversedAfter - reversedBefore`, and report `sourceRetentionDelta = sourceAfterReversal - sourceSuccess`; no preregistered claim of reversal success.

**Adversarial checks:** 1) the controlled task is intentionally unfair to a fixed missing-cue architecture; 2) random growth can find the same cue by chance; 3) privileged topology can match growth without rewiring; 4) signed target-relative pixels are *not* visual perception; 5) rewards encode target progress and are externally designed; 6) a 4-edge controller does not simulate recurrent neurons, spiking cells, dendritic growth, or human neuromodulation; 7) batch-2 feedback has fewer teaching signals; 8) this tests a single body joint; 9) successful touching is not sustained control; 10) sparse dictionary routing does not prove lower CPU/GPU time than dense vectors.

## Reproduce

```bash
python research/test_closed_loop_reach.py
python research/test_learn_reach.py
python research/learn_reach.py --seeds 1 2 --train-episodes 4 --eval-episodes 3 --reverse-episodes 2 --out /tmp/reach-smoke.json
python research/result_schema.py --check /tmp/reach-smoke.json
```

Full confirmatory run **only after this preregistration commit is present**:

```bash
python research/learn_reach.py --seeds 301 302 303 304 305 306 307 308 309 310 --train-episodes 120 --eval-episodes 80 --reverse-episodes 40 --commit THE_FROZEN_SOURCE_SHA --out /tmp/closed-loop-reaching-confirm.json
python research/result_schema.py --check /tmp/closed-loop-reaching-confirm.json
```

The `brain-result/1` JSON will preserve per-seed/per-arm scores, cost, topology and checkpoint hashes; the final report will include all 60 rows, including failed runs. An experiment can be correct even if no advantage or retention is demonstrated.

## Relationship to existing work

Reuses `research/structural_plasticity.py` from the earlier [simple structural repair result](sparse-plasticity-results-2026-11-12.md), [research/sparse-brain-next-implementation-plan.md](sparse-brain-next-implementation-plan.md), and existing issues #65 / #112 / #114 / #120 / #136. This phase is a *minimal opt-in bridge* and should not be mistaken for a complete physical brain or a new architecture for Brain World. Next controlled work should preserve richer sensory feature vectors across a microcircuit population and test genuinely delayed/uncertain sensory cues, memory, and new motor tasks.