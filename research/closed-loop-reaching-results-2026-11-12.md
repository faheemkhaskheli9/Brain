# Closed-loop sparse motor control: 10-seed held-out result (2026-11-12)

**Status:** *precommitted, completed research experiment.* Positive simple motor learning was observed, but the **primary criterion for advantage over random structural growth FAILED**. Reversal adaptation caused severe loss of the original skill. This is a synthetic **single-joint task**, not a demonstrated human neural model or general intelligence.

## Reproduction and provenance

- The complete protocol, budgets, task splits, controls and decision rule were [preregistered](closed-loop-reaching-pilot.md) in source commit **`fccf2c6d0983a617365ba53f5230ffd10a2422d8`**, before the confirmatory run. Exploration used seeds 0–5; they were excluded from confirmation.
- Fresh fixed seeds: **301, 302, 303, 304, 305, 306, 307, 308, 309, 310**.
- All **60 runs** (`10 seeds × 6 arms`) completed with status `ok`; every arm saw 120 training episodes × 16 movements (**1,920 body actions**). Primary immediate-feedback arms had 1,920 reward calls; `evidence_delay2` had 960 (one reward after two actions).
- After training: **80 frozen source** and **80 frozen amplitude-shifted held-out** goal episodes per arm, no learning or RNG changes. A further 80 reversed-actuator episodes were scored frozen, then 40 **development** reversal-adaptation episodes trained in a *detached checkpoint copy*; reversed performance and old-goal retention were rescored frozen.
- Output: [all 60 `brain-result/1` rows](results/closed-loop-reaching-2026-11-12.json) with per-seed metrics, runtime, connection topology and SHA-256 checkpoint hashes.

Run from the repository root:

```bash
python research/learn_reach.py --seeds 301 302 303 304 305 306 307 308 309 310 --train-episodes 120 --eval-episodes 80 --reverse-episodes 40 --commit fccf2c6d0983a617365ba53f5230ffd10a2422d8 --out /tmp/reaching-reproduction.json
python research/result_schema.py --check /tmp/reaching-reproduction.json
```

## Frozen held-out reaching results

| Arm | Held-out goal hit rate | Source task hit rate | New synapses | Training-only candidate evaluations (mean) |
|---|---:|---:|---:|---:|
| **Evidence growth** | **0.930** | 0.899 | 4.0 | 10,526 |
| Random growth | 0.798 | 0.756 | 4.0 | 10,689 |
| Fixed initial edges (missing target cue) | 0.533 | 0.513 | 0 | 0 |
| Frozen initial weights | 0.498 | 0.485 | 0 | 0 |
| Privileged correctly wired static topology | **0.960** | **0.945** | 0 | 0 |
| Evidence growth, feedback delayed two actions | 0.904 | 0.861 | 4.0 | 10,464 |

A `goal hit` means the left hip came within a distance of 0.07 of the target *at any point* in the 16-step episode. The controller has no stop action. Final target error is separately recorded in the artifact. Success does **not** mean sustained control, robust grasping, vision understanding or transfer to new action primitives. Reward is an engineered local `+1` for reduced distance after movement and `−1` otherwise.

### Preregistered primary gate — **failed**

Evidence growth minus random growth: **+0.1325** absolute held-out accuracy. Paired 95% seed-bootstrap confidence interval **[−0.01875, +0.28375]**; exact two-sided seed sign-flip **p=0.1875** (`n=10`). The mean clears the +0.10 minimum, **but the interval includes zero and p>0.05**. Do not assert a reliable advantage from the 10-seed evaluation. Random growth reached 100% on several seeds; the two approaches had different failure patterns.

Secondary exploratory paired comparisons (not corrected for multiple tests): evidence vs incomplete fixed topology +0.3975 (95% CI +0.2875 to +0.4900, p=0.0039); vs frozen +0.4325 (CI +0.330 to +0.518, p=0.0020); vs privileged topology **−0.0300** (CI −0.120 to +0.030, p=1.0); vs delayed evidence +0.0263 (CI −0.130 to +0.1925, p=0.656). The incomplete fixed network is handicapped by design because it has no synapse from the informative feature. **Privilege-aware static wiring also learns effectively; connectivity growth is not inherently necessary.**

Training-phase success under stochastic exploration is not directly comparable to greedy frozen success. In the evidence arm, the first 20 exploratory episodes scored 0.405 and later episodes 0.503; these values alone do not demonstrate a monotonic learning curve.

## Motor reversal and forgetting

The motor command mapping was inverted in the environment. The policy was **not given an explicit reversal/context flag**. A detached checkpoint was adapted using 40 development episodes, then evaluated on fresh held-out reversed goals and retained source goals.

| Arm | Reversed hit before adaptation | Reversed hit after adaptation | Change in original source success |
|---|---:|---:|---:|
| **Evidence growth** | 0.000 | 0.579 | **−0.521** |
| Random growth | 0.158 | 0.666 | −0.434 |
| Fixed initial edges | 0.500 | 0.500 | −0.013 |
| Frozen initial weights | 0.491 | 0.491 | 0.000 |
| Privileged correctly wired topology | 0.000 | 0.344 | −0.326 |
| Delayed evidence growth | 0.000 | 0.544 | −0.465 |

Evidence reversal adaptation improved by +0.579 (paired 95% CI +0.494 to +0.696), but original-source retention declined **−0.521** (paired CI −0.670 to −0.364). The reversal mechanism therefore **does not meet the continual-learning goal**. The fixed/frozen arms retain around-chance source performance; their smaller retention change is not evidence of superior memory.

## Adversarial review and decision

1. **The environment supplies the useful representation.** Target-relative distance is injected into a software visual port; real images, audio and text are not processed by a trained sensory layer. S1 proprioception is real output from the toy integrator but lacks biomechanics or neural coding.
2. **Fixed-topology comparison is biased.** Its initial four edges intentionally exclude the informative target feature, whereas growth can discover it. A correct topology achieves 0.960 without growth. Compare against equal-capacity topologies *with accessible predictive inputs* before generalization claims.
3. **A motor action, not an inferred biological spike.** A two-action softmax drives one joint at ±1 using the existing MotorDecoder. No macro-graph edge formation, cortical internal neural population, dendritic STDP or naturally self-organized sensory-to-motor projections is demonstrated.
4. **Persistent memory fails.** Retraining on inverted motor physics causes catastrophic interference. The next test must reuse existing Brain World replay/context work and measure retention at equal feedback, bytes and steps rather than simply increasing synapses.
5. **Delay is information-unequal.** Two-step feedback uses half as many reward calls and a scaled growth schedule, so its 0.904 score is a functional existence result, not proof of delayed reward superiority.
6. **Efficiency is not proven.** Four stored weights are sparse, yet the evidence arm examines about 10.5k candidate links for training. The result contains CPU time and weighted-product counts, but no vectorized dense baseline or equal-task-accuracy energy measurement.
7. **Frozen evaluation is separated from adaptation.** The source checkpoint is fingerprinted, no held-out labels are used in training, and reversal adaptation occurs only in a detached copy. However, we have not proven absence of all possible simulator confounds.

**Decision:** Accept as a reproducible *working toy motor-learning integration* and a negative finding on both reliable evidence-vs-random advantage and old-skill retention. **Do not promote as an AGI, human-like synaptogenesis or general continual-learning result.** Next prioritize feature-preserving sparse neuronal populations and an opt-in context/replay mechanism, with fresh holdouts and less biased fixed-topology comparators. Reuse #65, #112, #114, #120, #136 and the existing `brain-result/1`/claims pipeline.