# Structural micro-synapse plasticity: first backprop-free learning pilot

**Status:** implementation, preregistered protocol, and completed 10-seed frozen evaluation. [Detailed measured results](sparse-plasticity-results-2026-11-12.md). The protocol below was committed before the confirmatory run. **Scope:** a separate 24-input/2-action microcircuit policy. Not human connectome reconstruction, not integrated with the 78-region anatomical network or with Brain World, and not learned image/audio/text recognition. Brain World's backprop-free learner is unchanged.

## Question and falsifiable hypothesis

Can a sparse, reward-modulated policy learn an initially missing *useful* input-to-action connection without ever allocating dense weight matrices? Does evidence-guided connection turnover improve sample efficiency relative to the same edge budget with fixed topology or randomly rewired topology?

This is a deliberately biased synthetic test: **the initial four synapses connect only irrelevant cues** (input 1 and 2); the only predictive cue is input 0. A fixed-topology agent cannot learn that cue, regardless of training. An **oracle-informed topology** with the predictive cue connected at initialization is included as a separate, privileged positive-control comparator.

A biological analogy is experience-related formation and elimination of synapses (e.g. dendritic spines), but the exact growth rule here is **engineered**. It neither models dendritic spine biochemistry nor reproduces biological wiring rates. It cannot grow long-range anatomical pathways in `structural_connectome.py`.

## Architecture and learning

- **Sparse policy:** 24 continuous input features; 2 selectable output actions; a maximum of four explicitly stored synapses, at most two outgoing connections per input. No all-to-all matrix, and no parameters for absent edges.
- **Forward activity:** only `abs(input)>0.01` presynaptic features contribute through existing edges. Action probabilities come from a two-way softmax over local weighted inputs.
- **Three-factor learning:** each eligible existing synapse gets a local tag `e_ij <- lambda*e_ij + pre_i*(selected_j - probability_j)`. On external feedback `r` the weight changes `delta_w = 0.06*(r - running_reward_baseline)*e_ij`, clipped to +/-4. This is a stochastic-policy score-function term; it does **not** backpropagate through hidden layers or imply biological validity.
- **Potential new connections:** bounded cache (`max_candidates=64`) tracks reward-modulated eligibility for *observed active but currently absent* input-output pairs. Lazy decay discounts old scores. No full matrix is maintained.
- **Need gate:** every 80 feedback episodes (after warmup), grow one strongest candidate only if its absolute score >=0.75 and at least 12% of the latest <=80 feedbacks were failures. No growth when the observed error rate is already low.
- **Fixed resource cap:** if four edges are occupied, remove the smallest-magnitude mature synapse (age >=50 feedback episodes) before adding the new one; respect presynaptic fanout of two. The new synapse's small initial sign follows reward evidence. Random-growth control ignores that ranking and chooses a random eligible candidate/sign.
- **Persistence:** `export_state()` / `from_state()` use JSON-compatible validated sparse synapses, candidate scores and RNG state; a save must occur between trials, not with pending feedback.

## Preregistered external evaluation (freeze before running)

- **Experiment:** `brain/sparse-microcircuit-structural-plasticity`, using `brain-result/1` with every arm/seed, including any failures.
- **Development already used for algorithm design:** seeds 0–9; 1000 training episodes, 400 held-out per seed. This is **exploratory, not confirmatory**. Do not quote its performance as an independent evaluation.
- **Untouched confirmation:** seeds **101–110**, exactly 1000 training interactions per arm, 400 frozen held-out evaluation trials per arm and seed (with a separate 400-trial train-distribution control). One immediate binary verifier reward per training interaction, `+1` for correct action and `-1` for incorrect; labels are NOT given to the policy. Evaluation uses deterministic greedy decisions and must not update weights or RNG.
- **Data:** 24 public numeric features: input 0 is the signed cue; inputs 1–23 are independent distractors/noise. Train cue magnitude 1.0, dev 0.7, held-out evaluation 0.5. Different deterministic RNG namespaces and trial keys keep splits disjoint. The observation is a visible feature vector, not an image, cochlear stream or brain-derived signal.
- **Arms, same trial budget and edge budget:** evidence-guided growth (primary), random candidate growth, no-growth trained weights, frozen initial weights, shuffled verifier feedback with evidence growth, and privileged predictive fixed topology (upper bound with architecture knowledge). The *last* arm is not an information-matched baseline and must not be used to claim topology-discovery advantage.
- **Primary metric:** mean frozen held-out correct-action rate per seed; signed paired difference of evidence growth versus random growth, fixed, frozen, and shuffled feedback with a seed-bootstrap 95% interval and exact paired sign-flip p.
- **Secondary:** early versus final 100 training choices, train-distribution control, number of new/pruned synapses, final density, synaptic multiplication counts, candidate-evaluation counts, evictions, elapsed CPU wall time, checkpoint hash and training/reward/query budgets.
- **Proposed success gate:** evidence growth improves held-out accuracy by >=+0.10 absolute versus the strongest **nonprivileged** matched control, the paired bootstrap lower bound is >0, and paired p <=0.05; all ten seeds must be valid, no leaks/budget violations. Otherwise report negative/inconclusive. Do not tune parameters on seeds 101–110 if the gate fails.
- **Data retention:** write seed-wise `brain-result/1` JSON including failed runs and errors; update a separate outcome report and claims register only for reviewed positive assertions. Learning accuracy on this toy task is **not** evidence of brain realism, animal learning, emergent language, autonomy or AGI.

## Commands

```bash
PYTHONPATH=research python -m unittest research/test_sparse_brain_tasks.py research/test_structural_plasticity.py research/test_learn_sparse_brain.py -v
python research/learn_sparse_brain.py --seeds 101 102 103 104 105 106 107 108 109 110 --train-steps 1000 --eval-trials 400 --out /tmp/sparse-plasticity.json
python research/result_schema.py --check /tmp/sparse-plasticity.json
```

## Adversarial limits

1. **Biased graph:** because its initial edges omit the predictive input, the fixed-topology arm is deliberately disadvantaged. Only the equally budgeted *random rewiring* arm tests whether the proposed growth ranking helps more than generic rewiring. Privileged topology is a separate engineering upper bound.
2. **Too easy:** this binary association does not require temporal memory, compositional transfer, model-based planning, morphology or language. Success cannot establish learning how a human learns.
3. **Reward design:** externally supplied +/-1 correctness is much cleaner than a real body's sparse/delayed reward. The policy uses an engineered action softmax and score-function eligibility, not experimentally measured dopamine dynamics.
4. **Not always optimized:** scanning up to 64 candidate scores and Python dictionaries may be slower than a dense NumPy kernel on small problems. Count operations and benchmark wall time; avoid energy claims.
5. **False wiring:** learned micro-connections are constrained within the toy policy. Growing arbitrary new anatomical region-to-region projections would not be justified by the sources.
6. **Sign constraints:** signed effective synapses violate Dale's law if interpreted as excitatory/inhibitory axons. Interpret this model as functional weights, not identified neuronal cell types.
7. **One-step feedback and serial evaluation:** the pilot uses immediate reward. Delayed eligibility is unit-tested but not a demonstrated delayed-reward advantage.
8. **Generalization:** evaluation amplitude differs, but the relevant cue feature has the same identity and rule; test new sensor encoders, shifting input meaning, and held-out task families in subsequent experiments.

## Source grounding

- Holtmaat & Svoboda (2009), *Experience-dependent structural synaptic plasticity in the mammalian brain*, Nat Rev Neurosci 10:647–658: https://doi.org/10.1038/nrn2699 (structural turnover as biological phenomenon, not our algorithm).
- Gerstner, Lehmann, Liakoni, Corneil & Brea (2018), *Eligibility Traces and Plasticity on Behavioral Time Scales*, Front Neural Circuits 12:53: https://doi.org/10.3389/fncir.2018.00053 (three-factor credit assignment motivation).
- Evci et al. (2020), *Rigging the Lottery*, ICML: https://proceedings.mlr.press/v119/evci20a.html (strong gradient-based sparse-training comparison; our rule does **not** use its gradients).
- Xu et al. (2009), *Rapid formation and selective stabilization of synapses for enduring motor memories*, Nature 462:915–919: https://doi.org/10.1038/nature08389 (motor skill related spine dynamics; not simulated here).

## Next gate, after results

Replace scalar task input with small sparse within-region neuronal populations, test altered cues/temporal delay, and connect a learned output policy to the existing bounded toy-body interface. Preserve the existing macro graph and Brain World behavior. Reuse hypotheses H149/H088, #65 and #112 rather than create a parallel learning backlog.