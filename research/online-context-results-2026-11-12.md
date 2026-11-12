# Online policy context detection — frozen 10-seed evaluation (2026-11-12)

**Question:** Can stored sparse motor policies be selected from **actual, noisy,
post-action reward alone**, without a signaled context boundary or additional
counterfactual simulator probe actions? This tests a toy *policy retrieval*
mechanism, not de novo learning, biological synaptic consolidation or AGI.

**Precommitted implementation and protocol:**
`667b6a7230dc4546957c7e313b72c2071da0b083`, documented at
[online-context-pilot.md](online-context-pilot.md) **before** any reserved
seed was evaluated. Development/tuning seeds 0–5 are excluded. Reserved
confirmatory seeds **501–510** each include all seven predeclared arms;
**70/70** records have `status=ok`. Machine-readable evidence is the
[brain-result/1 file](results/online-context-2026-11-12.json).

## Evaluation setup

All controllers for one seed use exactly the **same** two pretrained sparse
microcircuits (A trained on normal hip response for 1,920 actions; B adapted
from A for inverted response using 640 additional actions). The result is
entirely a **frozen selection** evaluation; synaptic weights are unchanged
through the stream. The body has signed target-relative *engineered*
visual input and proprioception, and a designed binary progress reward.

The A→B→A→B motor-response phases have nominal lengths 137, 155, 149 and
167 actions, with independent ±8-step jitter per seed. Phase changes
occur in the **middle of a reaching episode**. No transition indicator goes
to the learned-policy selector. Each new target starts a normal 16-action
reaching episode; **no controller is allowed to perform a separate body
reset, cloned counterfactual rollout, or diagnostic action outside the
single realized stream**. Every arm pays an actual action and reward
observation for every stream step (about 608 steps/arm/seed). The public
reward is independently sign-flipped on ~10% of steps, fixed per seed.

The reward selector uses a fixed trailing eight-reward mean ≤ −0.75,
a minimum 16-action residence, and a cap of 32 switches. These settings,
including the 48-action intervals for blind controls, were chosen only
on exploratory seeds 0–5 and frozen in the prior commit. The oracle
receives the environment's hidden regime label as a **privileged ceiling**.

## Measured results (10 paired seeds)

| Arm | Public context selection accuracy | Actual reward/action | Goal-hit rate | Return-context selection | Avg. switches |
|---|---:|---:|---:|---:|---:|
| **Online reward switch** | **0.8377** | **+0.1972** | **0.5813** | **0.8855** | 10.6 |
| Online, shuffled reward input | 0.5085 | −0.2093 | 0.3794 | 0.3878 | 7.7 |
| Blind periodic switching | 0.5982 | −0.1354 | 0.4538 | 0.6148 | 12.1 |
| Blind random switching | 0.4152 | −0.3683 | 0.3328 | 0.4465 | 5.6 |
| Always latest B | 0.5317 | −0.2612 | 0.3529 | 0.0000 | 0.0 |
| Always original A | 0.4683 | −0.2726 | 0.4189 | 1.0000 | 0.0 |
| Privileged context oracle | 1.0000 | +0.2926 | 0.6749 | 1.0000 | 3.0 |

The context-selection column is computed *offline* from simulator labels;
**the detector never sees those labels**. `goalHitRate` is the fraction of
natural target episodes that touched the target at least once, not a
measure of stable motor control. Reward/action is the public task's
**uncorrupted physical progress reward**, averaged over actual actions.

### Preregistered decision rule

Primary, 
`online_reward − blind_random` for **actual reward/action**:
**+0.56550** with seed-paired 95% percentile bootstrap interval
**[+0.43462, +0.70693]** and exact two-sided sign-flip **p=0.001953125**
(10 paired seeds; every seed's difference positive). It clears the
precommitted ≥+0.15 mean, lower 95% CI >0 and p≤0.05 thresholds.

All required additional checks also pass in this exact setup:
`goalHitRate` improves by **+0.24844** versus blind random (95% CI
[+0.16946,+0.33741]); online selection accuracy is **0.8377** (>0.5),
return-context accuracy **0.8855** (≥0.6), mean switches **10.6** (<33),
and the two saved checkpoint fingerprints are unchanged after scoring.
**The predefined advancement gate therefore passes in this synthetic
stream.** This does not establish a universal advantage for reward-triggered
switching or demonstrate learning new neural representations.

Useful checks outside the primary comparison, reported descriptively:

| Paired comparison (online − control) | Actual reward/action delta | Paired 95% CI | Exact p |
|---|---:|---|---:|
| Blind periodic (similar switching frequency) | +0.33267 | [+0.23577, +0.42668] | 0.001953 |
| Shuffled reward signal | +0.40651 | [+0.25750, +0.57492] | 0.001953 |
| Always latest checkpoint | +0.45840 | [+0.34961, +0.56007] | 0.001953 |

Comparisons above are **additional exploratory contrasts**, not a
multiple-comparison-adjusted family of preregistered tests. The 10 paired
seeds, not the 6,000 individual steps, are statistical units. The primary
blind-random control happened to select the wrong saved policy more often
than chance on these seeds. The periodic baseline offers a stronger check
and the observed improvement is also positive against it, but that does
not eliminate model/schedule selection bias.

## Auditable raw actions and reward accounting

The `brain-result/1` JSON records metrics and checkpoint digest for each
of 70 runs, with **every step's chosen checkpoint and actual/noisy reward**.
For repository size it uses lossless `bitstring/1` notation: the `policySlot`
field has one `0` or `1` per action, while `actualReward` and `publicReward`
use corresponding `+`/`-` characters for exactly +1/−1. `phaseLengths`
identify the four true physical regimes **only in the analysis record**;
`switchDelays` are computed using these labels afterward. This shrinks
readable evidence from ~1.95 MB to ~0.2 MB without dropping any recorded
selection or reward. Individual **motor-command choices** were not stored,
so the source code and seed are required to reconstruct commands; the
file is not a complete actuator-command audit. Do not claim otherwise.

## Reproduce

```bash
python research/evaluate_online_context.py --seeds 501 502 503 504 505 506 507 508 509 510 --train-episodes 120 --adapt-episodes 40 --phase-steps 137 155 149 167 --noise 0.1 --commit 667b6a7230dc4546957c7e313b72c2071da0b083 --out /tmp/online-context-full.json
python research/result_schema.py --check /tmp/online-context-full.json
```

The runner intentionally emits expanded per-step trace arrays for local
inspection. The committed `brain-result/1` evidence encodes those exact
arrays as lossless sign/slot strings, leaving all scores unchanged.

## Adversarial limitations and next falsifiers

1. **B is supplied by an experimenter:** no controller can train a new
   context online; the system chooses only between two pretrained sparse
   checkpoints. Human brain memory or autonomous latent causes are not
   represented.
2. **Designed reward strongly reveals the policy failure.** Noise is only
   10%; long delays, partial feedback, mixed/overlapping regimes, many
   regimes or a novel unseen context may fail. This is simpler than natural
   embodied control.
3. **Reward and task features are engineered.** V1's target delta is a
   hand-selected numeric signal rather than learned pixels; the body is
   a single synthetic hip joint, not a physical robot or biological brain.
4. **Natural episode resets remain.** No *counterfactual* per-policy resets
   occur in the online stream, but every 16 actions a new target and fresh
   simulator body are constructed. Future work should evaluate a truly
   continuous body with position-preserving target transitions.
5. **Switch chattering:** an ideal oracle switches only three times, while
   online reward switches 10.6 on average. False alarms cost actual
   movements; the controller is not optimal and does not perform explicit
   context inference under a probabilistic world model.
6. **Baseline weakness and dependence:** blind random was unlucky (41.5%
   context-selection accuracy), and a static oracle picks perfectly. Seeds
   and phase distributions are narrow, and there is no third held-out task
   family. The already reported test seeds must not become development data.
7. **No efficiency claim:** two saved checkpoints cost about twice one,
   plus sparse inference and reward processing. Even though there are
   zero *extra* probe interactions, policy mistakes cost physical steps;
   no wall-time, GPU power or energy comparison was made.

**Next:** benchmark truly continuous motor state with unannounced target
changes, delayed/noisy rewards, and a third unknown context; compare against
Bayesian change-point and context-replay baselines under the same memory and
physical-action budgets. Separately progress feature-preserving sparse
neuronal representations before multimodal understanding claims.