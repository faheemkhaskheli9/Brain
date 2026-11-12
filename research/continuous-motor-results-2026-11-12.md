# Continuous toy-body context switching under delayed reward: ten-seed result

**Status:** Pre-registered primary *reward* gate passed; downstream **goal
completion did not improve**. This experiment studies a backprop-free sparse
software controller with two pre-trained 4-synapse microcircuits, not a
biological human brain, free-running multi-joint motor system, or learned
perception. The result must not be cited as evidence of general intelligence
or overall task success.

**Question:** Does a reward-guided context selector with a **3-action feedback
latency** outperform a preselected time-based policy switcher when a *single
physical body* continues through hidden motor reversals with unchanged joint
positions and velocities?

**Preregistration:** source SHA `4fe342e487eb9da213e2482e158fa3ae8c332be2`
contains [the frozen protocol](continuous-motor-pilot.md) and eight-arm
benchmark, committed **before** using the reserved seeds **601–610**. Exploratory
seeds 0–5 are not included. No thresholds or preselected comparisons were
changed after that commit. Raw [brain-result/1 file](results/continuous-motor-2026-11-12.json)
includes 80/80 completed seed/arm records, checkpoint SHA256 digests, timing,
full actual selected-policy and motor-action streams, public/true reward signs,
quantized physical position trajectories and goal values. No failed or
missing confirmatory runs.

## Method

- Two pre-trained policies: normal actuator A trained for **1,920** real
  actions; detached inverted-actuator B subsequently adapted for **640**
  actions, with its original A stored in a separate checkpoint. Two policies
  per arm, each with at most 4 learned micro-synapses and local backprop-free
  weight updates **only during pretraining**. No online learning of either
  checkpoint weight during frozen scoring.
- Eight frozen controllers all receive the same **seed-jittered hidden
  A→B→A→B motor sign schedule** (~608 physical actions, range by seed), the
  same independently generated visual target sequence, and the same
  deterministic **10%** public-reward sign noise. A privileged true-context
  oracle is clearly a *performance bound*, not a learner.
- The physical **body is created only once for each stream**.
  `SimpleJointBody` state, positions, velocities and integrator are *never
  reset* on target changes or context switches. The evaluator replaces only
  target/scoring metadata every **16 actions**. Hidden motor sign transitions
  are placed inside target windows and not supplied to the selector.
- A causal buffer delivers feedback only when the action-clock index is
  at least `action_time + delay`: **one action** (available before the next
  choice) vs **three actions**. Three final rewards remain pending and are
  reported, not retroactively delivered. The selector has no second
  simulator, body restart, counterfactual state or free probe action.
- Scoring uses **actual** ±1 improvement in absolute target error (primary),
  target contact at any time during a 16-action window (secondary), selected
  checkpoint match to hidden context (offline verifier only), latency,
  switching and storage/compute cost. This reward is external task shaping,
  *not a learned prediction error from raw sensory media*.

## Frozen held-out results (10 seeds)

| Arm | Actual progress reward / action | Offline context correctness | Target contacted / window | Mean policy switches |
|---|---:|---:|---:|---:|
| Online immediate (1 action) | +0.2889 | 0.8672 | 0.2399 | 9.6 |
| **Online delayed (3 actions)** | **+0.2368** | **0.8423** | **0.2266** | **10.3** |
| Delayed selector, *shuffled rewards* | −0.0914 | 0.5905 | 0.2502 | 6.1 |
| **Blind periodic, primary control** | **−0.0531** | 0.6088 | 0.2529 | 12.0 |
| Blind random | −0.2788 | 0.4621 | 0.1872 | 6.8 |
| Always latest checkpoint | −0.2068 | 0.5322 | 0.2132 | 0.0 |
| Always old checkpoint | −0.2130 | 0.4678 | 0.1396 | 0.0 |
| Privileged true-context oracle | +0.3986 | 1.0000 | 0.2056 | 3.0 |

All summaries average **seed means**, not 6,000+ correlated physical actions
as if they were independent participants. The logged context correctness is
*verification metadata*; the controller never receives the true hidden
motor sign. Goal contact is **any** hit during the goal window, not sustained
tracking or precise final-position control. This benchmark has *no* learned
raw image/audio/video/text representation.

### Preregistered decision

**Primary `online_delay3 − blind_periodic`:** **+0.28993** actual progress
reward/action, seed-paired 95% bootstrap CI **[+0.19981, +0.37557]**, exact
two-sided sign-flip **p = 0.001953125**. The fixed +0.10 gain, positive CI
lower bound, p≤0.05, complete 10-pair sample and zero-body-reset conditions
**all pass**.

**Mechanistic `online_delay3 − delay3_shuffled`:** **+0.32819**
reward/action, seed-paired CI **[+0.24597, +0.41543]**, exact sign-flip
**p = 0.001953125**. This independently preregistered reward-signal
ablation also **passes**. The results are evidence for use of the observed
reward information under tested conditions, not general learned context
inference or a biological mechanism.

### Crucial secondary weakness: reward ≠ reaching success

**Goal-hit difference against periodic: −0.0264** (−2.64 percentage points),
paired 95% CI **[−0.0737, +0.0183]**, exact sign-flip **p = 0.3125**. The
delayed controller touched the target in **22.66%** of target windows vs
**25.29%** for periodic. Although progress reward and context selection
were substantially better, **there is no demonstrated improvement in the
actual reach-the-target outcome**. The negative mean does not establish
that delayed selection damages goal success either—the interval spans 0.
A better policy can earn many small progress rewards without contacting a
target before the 16-step deadline. Even the *privileged oracle* contacts
only 20.56% of targets here. **Passing the reward criterion must not be
reported as better bodily competence.**

**Observed latency cost:** `online_delay3 − online_immediate` was **−0.05206**
reward/action, paired CI **[−0.10348, −0.01311]**, exploratory p = 0.015625.
This secondary timing contrast was not preregistered as a decision gate and
is not adjusted for multiple comparisons.

### Budget and execution cost

- Mean continuous stream: about **601.6 actions** per arm/seed after the
  same seed-jittered phase schedule. Both checkpoints use ~**15.6 KB**
  total serialized memory and evaluate about **2,400 sparse synaptic
  weighted products** per run, with differences reflecting selected activity.
- The 3-step controller has **3 rewards pending** and receives about 598.6
  public rewards by the final selection time, compared with 1 pending and
  about 600.6 received for the 1-step arm. All arms still *generate* the same
  full sequence of actual outcomes; controls ignoring feedback have zero
  consumed deliveries, not free supervision.
- **Zero extra probe actions and zero physical body resets** in every arm.
  Mean ~37 target changes per seed, which modify target/scoring metadata but
  not physical state.
- Candidate discovery/learning compute happens *before* this benchmark, in
  the shared checkpoint training; these records do not establish the
  efficiency of backprop-free sparse training versus dense NumPy or GPUs.
  Runtime depends on Python object overhead and is not an energy measure.

## Adversarial evidence checks

The independent [analysis auditor](analyze_continuous_motor.py) recomputes
**each** of 80 physical trajectories from the logged motor action, deterministic
motor inversion schedule and published `SimpleJointBody` equations. It
independently recomputes progress rewards from actual positions and targets,
validates deterministic public noise, replays reward-delay selection to
prevent future-feedback leakage, checks every checkpoint digest shared by
arms, rejects changed splits/targets, and recomputes the scores in
`brain-result/1`. [Adversarial tests](test_analyze_continuous_motor.py) inject
forged motor actions, position traces, rewards, selector decisions,
budgets and checkpoints and require errors. The auditor is a second software
implementation of the same published integrator, not independent hardware
measurement. Existing unit tests assert that the same body object and its
velocities survive every target transition.

**Remaining problems:**

1. **The representation/reward is engineered.** The correct sign of target
   error is directly encoded in the visual port, so the learner does not
   infer visual goals from raw pixels or learn a general representation.
2. **A/B regimes are known during training.** Two pretrained checkpoints
   are saved; no additional synaptic weights emerge when a third unknown
   regime appears. Neither unsupervised skill creation nor synaptic
   consolidation is demonstrated.
3. **Reward objective misalignment.** Real goal-hit success does not follow
   from improved signed progress reward; the reverse trend is a direct
   reason not to declare the controller competent.
4. **Task artificiality.** A single bounded joint, target changes every 16
   actions, instantaneous motor inversion and simple ±1 reward are not a
   natural continuous environment. No contact sensors, collisions,
   2D/3D arm geometry, obstacle avoidance or realistic control delays.
5. **A priori context A.** Evaluation starts with policy A selected; a
   different initial context or nonalternating unexpected regimes could
   change selection performance. Only two separable regimes are tested.
6. **Latency is only in reward observation**, not in motor command, video,
   time-varying acoustics or the embodied actuator. No third context is
   available for the selector to discover.
7. **Sparsity claim:** four stored edges per microcircuit and selective
   events do not demonstrate shorter runtime or fewer joules than a
   vectorized correctly wired dense policy at matched goal quality.
8. **Statistical scope:** ten paired seeds and one frozen design, not
   evidence across naturally occurring tasks or people. Uncorrected
   secondary tests are exploratory.

## Decision and next falsifier

**Retain the positive preregistered reward-selection result and the
non-improving goal-hit result together.** The next experiment should target
*actual goal completion*, not just how often the motor moves in the right
direction. Consider dense-vs-sparse and static-correct wiring controls,
require final-distance/steady-contact/effort penalties, new unseen target
families, and a context that neither saved checkpoint can solve. A
fresh preregistration and **new seeds** are required; seeds 601–610 must not
be used for reward tuning. Only after real goal-performance evidence should
we add more neuronal anatomical detail, memory mechanisms or natural
multimodal perception claims.

## Reproduce

```bash
python research/test_continuous_motor.py
python research/test_evaluate_continuous_motor.py
python research/test_analyze_continuous_motor.py
python research/evaluate_continuous_motor.py --seeds 601 602 603 604 605 606 607 608 609 610 --train-episodes 120 --adapt-episodes 40 --phase-steps 137 155 149 167 --noise 0.1 --commit 4fe342e487eb9da213e2482e158fa3ae8c332be2 --out /tmp/brain-continuous-confirm.json
python research/result_schema.py --check /tmp/brain-continuous-confirm.json
python research/analyze_continuous_motor.py /tmp/brain-continuous-confirm.json
```

Context inference under noisy motor feedback has neuroscience and theoretical
precedents (e.g., Cuevas Rivera & Kiebel, 2023, *The effects of probabilistic
context inference on motor adaptation*, [PubMed](https://pubmed.ncbi.nlm.nih.gov/37399219/)).
The experiment here is only an engineered analogy, not a reproduction of that
human motor-adaptation result.