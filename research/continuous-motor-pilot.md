**Post-evaluation record (2026-11-12):** The held-out 601–610 evaluation has
been completed and published as [continuous-motor-results-2026-11-12.md](continuous-motor-results-2026-11-12.md).
The predeclared *reward* primary and shuffled-signal criteria passed,
but **goal-hit success did not improve**. All original controls, budgets and
acceptance thresholds below were committed as `4fe342e487eb9da213e2482e158fa3ae8c332be2`
before the held-out run. This post-run note does not revise them.

# Continuous-body motor control and causal reward-latency experiment

Date: 2026-11-12. Status: **preregistered pilot, not yet a result**.
Related roadmap: #65, #94, #112, #114, #120, #136; follows the negative
context-memory primary gate and the positive reward-only context-switch toy pilot.
This experimental design must be committed **before** running reserved seeds.

## Exact gap and falsifiable hypothesis

Prior online work (`research/online-context-results-2026-11-12.md`) preserved
selector state but **constructed a new physical body every 16 actions**.
That made motor-state resets a potential confound and could exaggerate the
quality of reward-based context detection. The old experiment delivered
reward before the immediately next action and did not test latency.

**Question:** Can two separately pretrained *backprop-free* sparse action
policies be switched using delayed public reward while one physical simulated
body continues without resets through hidden motor-rule changes?

**Hypothesis:** At **three-action outcome latency**, the online reward
selector improves actual progress reward/action over a preselected
**blind-periodic** switcher on new frozen seeds at matched physical-action
budgets. Preregistered quantitative gate: mean paired improvement **≥+0.10**
reward/action; paired bootstrap 95% interval lower bound **>0**; exact
two-sided sign-flip **p≤0.05**; 10/10 paired seeds present; every arm has
zero body resets and equal actions. If one condition fails, record a **negative
or inconclusive** outcome and do not promote this hypothesis.

**Independent feedback ablation:** require improvement over `delay3_shuffled`
(sham binary feedback with identical latency), by at least **+0.10**, positive
paired 95% bootstrap lower bound, and sign-flip p≤0.05. This is a secondary
mechanistic control; report independently even if primary passes. **Delay
cost:** report `online_delay3` minus `online_immediate`, with paired interval
and no guaranteed success threshold.

## What actually continues without resetting

One `ContinuousReachBody` and **one `SensorimotorLoop` with the same
SimpleJointBody instance** persist for the full stream. At each 16-action
goal boundary, the simulator updates only the goal and score counters; joint
positions and velocities remain unchanged. Hidden actuator sign changes at
seed-jittered positions **inside those goal windows**. The controller is
never told whether a target changed or whether the motor sign flipped.
It observes the existing *engineered* signed visual target delta and S1
proprioception; it does not learn to process images or natural movement.

The source controller and inverted-motor controller are learned independently
*before* this stream with **experimenter-known** motor regimes. Their
synaptic weights are frozen at scoring. This evaluates **online policy
retrieval**, not unsupervised acquisition of a third context or biological
synaptogenesis during the stream. Background natural target transitions are
not simulator resets. There are no counterfactual probes, duplicated body
states, oracle training actions, or extra control decisions.

### Strict event timing

For action `t`: deliver any **previously queued** public reward whose
due index is at most `t`; select one checkpoint; generate its action from
currently observed sensory channels; actuate the real body; compute the
post-action signed progress reward; apply 10% predetermined reward-sign
corruption; queue the public outcome for delivery at `t + delay`.

`online_immediate`: delay=1 (previous action's reward available before the
next choice), not same-step future knowledge. `online_delay3`: delay=3.
No reward is received before its due action index. The final 1 or 3 outcomes
remain pending, are counted, and are **not** silently delivered after stream
termination. Every policy sees the same target schedule and motor dynamics.

## Predeclared protocol (frozen before confirmatory seeds)

| Parameter | Fixed configuration |
|---|---|
| Confirmatory seeds | **601 through 610**, all reported |
| Exploratory tuning seeds (excluded) | 0–5 only |
| Existing learner | `SparsePlasticPolicy`, 24 signed inputs, 2 actions, max **4** active micro-synapses |
| Learned checkpoints | A: 120 train episodes × 16 actions = **1,920**; B: inverted actuator adaptation on detached A for 40 episodes × 16 actions = **640** |
| Context stream | Alternating original/inverted/original/inverted, phase base (137, 155, 149, 167), seed jitter ±8; first three transitions forced off 16-action target boundaries |
| Physical goal handling | New 16-action target every goal window; **same body, same velocities**, no position reset |
| Target family | `reach_trials('eval', seed+175000, ceil(total/16))`, distinct from training and dev IDs |
| Public reward | ±1 based on change in absolute target error, **10%** exogenous sign corruption, same precomputed noise sequence across arms |
| Online selector | Existing `OnlineConfig(window=8, low_mean=-0.75, min_dwell=16, max_switches=32)`; **no tuning on held-out** |
| Blind periodic/random | 48-action switching blocks, as in previous exploratory baseline; no new tuning |
| Total per arm | Sum of phase lengths ≈ **608** real body actions and generated rewards; **zero** counterfactual probes |
| Trial result | Full `brain-result/1` per seed/arm with success or error, stream topology/hash, checkpoint digest, feedback availability and per-action trace |

**Arms (8):** `online_immediate`, **`online_delay3`**,
`delay3_shuffled`, **`blind_periodic`** (preselected primary comparator),
`blind_random`, `latest`, `oldest`, `privileged_oracle` (hidden motor
regime known, upper bound only). The same two frozen checkpoints are reused
per seed for all 8 arms; baseline memory storage is equal. The periodic
switcher makes the same style of interventions without looking at reward.
The shuffled feedback controller receives irrelevant but causal *actual
observations* from seeded sham signal with the same three-action delivery.

### Audit fields and cost

Report: mean true progress reward per action (primary), goal-hit fraction,
selected-policy context correctness (verifier only), return-phase accuracy,
latency to correct policy, number of false switches, *real* actions,
`generatedRewards`, actual `deliveredRewards`, `pendingRewards`,
`targetChanges`, `bodyResets`, `extraProbeActions`, total sparse synaptic
products and candidate-checkpoint storage. Per action retain binary
selected-controller ID, **actual motor action**, true/public reward sign,
and a 16-bit signed quantized physical position trace with explicit scale.
Store phase lengths and target sequence for full reconstruction.
Checkpoint digests must never change during frozen evaluation.

### Adversarial review and failure criteria

- **Biology:** simulated software joint and stored policies are not brain
  tissue, mammalian cortex, dendritic spines or learned human movement.
- **Construct validity:** reaching success at some time during the target
  window is NOT sustained control; track true reward separately.
- **Selection bias:** two pre-trained regimes and an initial A-context are
  provided; no third unfamiliar regime or autonomous consolidation.
- **Reward shortcut:** target-relative signed visual error and ±1 progress
  reward are engineered; compare shuffled feedback and blind periodic.
- **Confounds:** targets change but physical state must not; flag any joint
  teleportation and any off-schedule context disclosures.
- **Fairness:** frozen checkpoint training is identical across arms; all
  streams spend the same physical actions. Delayed feedback has fewer
  delivered rewards **by stream end** (report instead of hiding).
- **Optimization:** sparse synapse count does not by itself imply faster or
  cheaper runtime; record wall time separately, no GPU/power claim.
- **Statistical discipline:** no retuning on reserved seeds 601–610, no
  excluding runs that hurt results, no resubmitting an unfavorable split to
  manufacture a positive gate. Positive values without a paired CI/p-value
  are insufficient to claim a repeatable gain.

## Reproduce (from repository root)

```bash
python research/test_continuous_motor.py
python research/test_evaluate_continuous_motor.py
python research/evaluate_continuous_motor.py --seeds 0 1 --train-episodes 8 --adapt-episodes 5 --phase-steps 33 41 47 39 --out /tmp/brain-continuous-smoke.json
python research/result_schema.py --check /tmp/brain-continuous-smoke.json
```

Confirmatory run **only after this protocol is committed** and fixed at a
specific SHA, with all 10 reserved seeds (no subset selection):

```bash
python research/evaluate_continuous_motor.py --seeds 601 602 603 604 605 606 607 608 609 610 --train-episodes 120 --adapt-episodes 40 --phase-steps 137 155 149 167 --noise 0.1 --commit FROZEN_COMMIT_SHA --out /tmp/brain-continuous-confirm.json
python research/result_schema.py --check /tmp/brain-continuous-confirm.json
```

Do not use held-out results to tune the hypothesis. Publish every arm/seed,
including errors, and record success or failure of each gate.