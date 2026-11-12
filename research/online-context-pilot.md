# Online motor context detection without simulator probing

**Scope:** separate, backprop-free sparse microcircuit *research* prototype. The
existing 78-region anatomical graph, Brain World creature and natural media
adapters are unchanged. This is not biological hippocampal replay, neuronal
context discovery, or online training of new motor skills.

## Gap and hypothesis (#65, #114, #120, #136)

Previous [two-checkpoint memory experiments](context-memory-results-2026-11-12.md)
selected learned skills with 72 extra DEV simulator interactions and an
experimenter-provided *context-change boundary*. A selection that depends on
fresh counterfactual simulator resets is not a deployable change detector.

**Falsifiable hypothesis:** A causal rolling-negative-reward selector can pick
between two **already trained** sparse action policies on one realized
A→B→A→B motor stream, with *no switch signal and no additional probe actions*,
more successfully than a blind random switching controller under matched
action budgets. Both share exactly the same two checkpoint memories.

This is a software design hypothesis, not a biological mechanism established
in humans. Retrieving a saved policy is **not modifying its parameters**.

## Implementation contracts

- Policy A: existing local three-factor synaptic learner, 24 engineered
  visual/S1 features and 2 actions; 120 × 16 body training actions.
- Policy B: clone of A adapted with the *inverted actuator* for 40 × 16
  actions in separate DEV training. The experimenter labels training B;
  there is **no online skill formation** for unknown contexts.
- Both are stored in the existing capacity-two `SparseContextMemory` and
  restored frozen for evaluation. All arms see the **same** pretrained A/B
  per seed, the same phase schedule and reward-noise draws.
- At each stream step the selector sees only `select()`→ chosen policy,
  then `feedback(public_reward)` from the action *actually taken*.
  It never sees phase index, inversion flag, next phase boundary or rewards
  for the unchosen checkpoint. Evaluation never calls `memory.retrieve()`.
- A natural reaching task resets its body after every 16 actions so that
  different target positions can be presented. **That reset is not a probe**:
  exactly one body trajectory is realized per arm; selectors are not reset
  between tasks. Motor-rule changes occur **inside** normal episodes, not
  at those natural task reset points.
- Online reward is flipped with probability 0.10 at the observation boundary
  by a seeded independent noise stream; actual progress reward is kept
  separately for behavioral scoring. All arms pay one action and one reward
  observation per stream step. No free oracle labels or probe calls.
- Structural micro-synapse growth was used during *pretraining only*;
  streaming policy weights remain frozen and are checked against a digest.
  Candidate-link scoring compute and checkpoint bytes are not omitted from
  interpretation. No dense N×N synaptic matrix is allocated.

### Fixed selector and controls (exploratory tuning complete)

`OnlineRewardSelector` starts in checkpoint A. It keeps the last 8 **public**
rewards while one policy is active; when their mean is ≤ −0.75 after at least
16 actions since the last switch, it switches to the other checkpoint and
clears its history. At most 32 switches are permitted in a stream; no policy
training is enabled during evaluation. It is a simple reward-threshold rule,
**not inferred task goals**. All configuration was chosen by inspecting
**exploratory seeds 0–5 only**; those seeds must never enter the confirmatory
analysis.

Arms with the same trained memory and physical feedback/actions:

| Arm | Selector | Leakage or cost |
|---|---|---|
| `online_reward` | negative rolling observed reward | primary treatment, no privileged context |
| `online_shuffled_feedback` | same algorithm but independent random ±1 feedback | credit-information ablation |
| `blind_periodic` | alternate checkpoints every 48 actions | matched ~12 switches in DEV, ignores reward |
| `blind_random` | seeded random checkpoint per 48-action interval | **preselected primary baseline**, equal memory/actions |
| `latest` | always pretrained B | memory comparator, no switching |
| `oldest` | always pretrained A | memory comparator, no switching |
| `privileged_oracle` | sees hidden context flag | explicitly privileged upper bound, **not** a fair learner |

The periodic/random interval of 48 was selected using exploratory seeds 0–5.
Report actual switches rather than assuming matching numbers. The reward-
shuffled arm still gets the same **physical actions and real progress rewards**;
only its *selector input* loses credit information.

## Preregistered confirmatory protocol (freeze before run)

- **Reserved seeds:** 501–510, ten paired seeds. No selecting favorable runs,
  adjustments or reruns based on their performance.
- **Frozen task:** alternating old/new/old/new motor rules, nominal phase lengths
  137/155/149/167 actions. Each seed gets independent deterministic ±8 action
  jitter; ensure changes happen between natural task resets. **No switch
  signal** goes to the detector.
- **Training:** 1,920 actions for checkpoint A and 640 for B, identical for
  every arm within a seed; exact costs reported separately.
- **Evaluation:** ~608 actual body actions and equal observed feedback calls
  **per arm**. All seven arms and all ten seeds, including failures, in
  `brain-result/1` with per-action selected slots and public/actual rewards.
- **Primary behavior metric:** `rewardPerAction`, in [−1,+1]; compare
  `online_reward` − `blind_random` seed-paired difference. Advancement only
  if absolute mean ≥ **+0.15**, paired 95% bootstrap lower bound > 0,
  exact two-sided sign-flip **p ≤ 0.05**, and all 70 records are present.
- **Secondary safeguards:** goalHitRate not lower than `blind_random` by
  more than 0.05, contextAccuracy higher than chance 0.5, source-return
  context accuracy ≥ 0.6, fewer than 33 switches/stream, and frozen A/B
  checkpoints unchanged. The final claim needs both the primary and
  secondary criteria; report any failed gate. A privileged oracle is
  **excluded** from comparative inference.
- **Statistics:** 10 *paired independent seeds*, not thousands of correlated
  stream steps as independent statistical units. Record seed-resolved
  paired differences, percentile bootstrap 95% CI and exact two-sided
  sign-flip p. Confidence intervals describe this toy simulator only.
- **Measurement:** reward, goal touches, context selections (offline label
  used only for scoring), time to first correct selection after change,
  false switches, memory bytes, synaptic products, feedback calls, and
  the full action/reward trajectory, including counterexamples.

## Adversarial review and failure criteria

1. **Checkpoint oracle during pretraining.** The experimenter trains B on
   inverted motor dynamics. The method cannot discover an unseen third
   context, infer causality or learn a new skill during streaming.
2. **Engineered reward.** Progress is almost immediately observable and
   signed target error is supplied directly. Unreliable sparse natural
   feedback may defeat the rule.
3. **Noise and oscillation.** Reaching the target can produce alternate
   ±1 progress rewards; false switches and source skill loss are possible.
   The fixed window and threshold may overfit this body's dynamics.
4. **No cost-free inference.** Every mistaken action causes movement and
   consumes task budget, even though no extra *counterfactual* probes are
   used. Both saved policies consume memory; stream policy inference counts.
5. **Trajectory confound.** Different selected policies create different
   physical states, so observed rewards are not matched counterfactual
   outcomes. Shared seeds/noise and matched budgets do not make the
   trajectories identical. Report realized outcomes, not causal effect
   claims stronger than the randomized-arm comparison permits.
6. **Biological analogy.** The rolling threshold and checkpoint selection
   are engineered, not experimentally measured neuronal operations.
   Do not claim new cortex-like representations, synaptic consolidation,
   general AGI, energy reductions or human brain fidelity.
7. **Phase schedule simplicity.** Four binary context segments are easy;
   phase lengths are jittered only slightly, and the selector starts with
   the correct context. Future tests need more contexts, distractors,
   nonlinear targets, changes without a saved matching checkpoint, and
   auditory/visual representations rather than engineered deltas.

## Reproduce

```bash
python research/test_online_context.py
python research/test_evaluate_online_context.py
python research/evaluate_online_context.py --seeds 0 1 --train-episodes 8 --adapt-episodes 5 --phase-steps 33 41 47 39 --out /tmp/online-context-smoke.json
python research/result_schema.py --check /tmp/online-context-smoke.json
```

**Run the confirmatory 501–510 seeds only after this source and protocol are
committed to GitHub.** Record the exact source commit in the result file:

```bash
python research/evaluate_online_context.py --seeds 501 502 503 504 505 506 507 508 509 510 --train-episodes 120 --adapt-episodes 40 --phase-steps 137 155 149 167 --noise 0.1 --commit SOURCE_SHA --out /tmp/online-context-confirm.json
python research/result_schema.py --check /tmp/online-context-confirm.json
```

The evidence file will be linked from this protocol **after** evaluation.