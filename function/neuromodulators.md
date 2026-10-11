---
title: Neuromodulators beyond dopamine (ACh, NE, 5-HT)
category: function
tags: [neuromodulation, acetylcholine, noradrenaline, norepinephrine, serotonin, dopamine, meta-learning, locus-coeruleus, raphe, basal-forebrain, uncertainty, exploration]
use_cases:
  - what do acetylcholine, noradrenaline and serotonin do in learning
  - how could neuromodulators map onto reinforcement learning hyperparameters
  - add global modulatory signals to a brain-inspired learning system
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1016/S0893-6080(02)00044-8
  - https://doi.org/10.1016/j.neuron.2005.04.026
  - https://doi.org/10.1146/annurev.neuro.28.061604.135709
  - https://doi.org/10.1016/j.neuron.2007.08.013
---

# Neuromodulators beyond dopamine (ACh, NE, 5-HT)

## Summary
Four small groups of neurons in the brainstem and basal forebrain send long, widely
branching axons across most of the brain and release **dopamine (DA)**,
**acetylcholine (ACh)**, **noradrenaline (NE, norepinephrine)** and **serotonin
(5-HT)**. They do not carry detailed information; they change *how* the circuits they
reach process and learn. Dopamine as a reward prediction error is the best-supported
link to AI ([[learning-and-plasticity]]). For the other three the anatomy and
receptors are textbook facts, while their computational roles are still hypotheses.
The best-known one is Doya's (2002): they set the **meta-parameters** of learning.

## How it works

### Established: sources, receptors, effects
| Modulator | Main source nuclei | Receptor families | Established effects |
|---|---|---|---|
| Dopamine | Ventral tegmental area, substantia nigra pars compacta | D1-like (D1, D5), D2-like (D2-D4); all G-protein-coupled | Phasic bursts track reward prediction error (Schultz et al. 1997); gates corticostriatal plasticity |
| Acetylcholine | Basal forebrain (nucleus basalis, medial septum); brainstem pedunculopontine and laterodorsal tegmental nuclei | Nicotinic (ionotropic) and muscarinic M1-M5 (G-protein-coupled) | Enhances responses to sensory input relative to recurrent cortical input; supports encoding of new memories (Hasselmo 2006) |
| Noradrenaline | Locus coeruleus (LC), a small pontine nucleus | α1, α2, β adrenergic; all G-protein-coupled | Arousal and vigilance; LC fires phasically to salient or unexpected events (Sara 2009; Aston-Jones & Cohen 2005) |
| Serotonin | Raphe nuclei (dorsal and median raphe) | Seven families 5-HT1 to 5-HT7, 14 subtypes in mammals; only 5-HT3 is a ligand-gated ion channel (Hannon & Hoyer 2008) | Mood, sleep-wake, impulse control; implicated in aversive processing and waiting for reward (Cools, Nakamura & Daw 2011) |

Because most of these receptors are G-protein-coupled, their effects are slow
(hundreds of ms to minutes) and change a neuron's excitability and plasticity
rather than driving spikes directly.

**Effects on plasticity (established).** Neuromodulators can decide *whether* and
*which way* a synapse changes. In visual cortex slices, Seol et al. (2007) showed
that activating β-adrenergic receptors (the NE pathway) enabled spike-timing LTP and
muscarinic (ACh) receptors enabled spike-timing LTD, and with both active the same
pairing protocol produced either sign depending on timing. This is the biological
basis of the three-factor rules in [[spiking-neural-networks]] and
[[learning-and-plasticity]] (Frémaux & Gerstner 2016).

### Hypothesis: neuromodulators as meta-parameters (Doya 2002)
Doya proposed that each modulator sets one hyperparameter of reinforcement learning:

| Modulator | Meta-parameter | RL role |
|---|---|---|
| Dopamine | TD error `δ` | the teaching signal itself |
| Serotonin | discount factor `γ` | how far into the future rewards count |
| Noradrenaline | inverse temperature `β` | exploration vs exploitation in `P(a) ∝ exp(β·Q(a))` |
| Acetylcholine | learning rate `α` | how fast memory is updated |

Evidence is mixed and the mapping is a **hypothesis**:
- *Serotonin and patience:* optogenetically activating dorsal raphe serotonin
  neurons made mice wait longer for delayed rewards (Miyazaki et al. 2014),
  consistent with a larger `γ`. Serotonin's role in aversive prediction does not fit
  a single discount parameter (Cools et al. 2011).
- *Noradrenaline and exploration:* adaptive gain theory (Aston-Jones & Cohen 2005)
  proposes phasic LC firing supports exploiting the current task and high tonic LC
  firing supports disengaging and exploring.
- *ACh and NE as uncertainty signals:* Yu & Dayan (2005) proposed an alternative split:
  ACh reports **expected uncertainty** (known unreliability of cues), NE reports
  **unexpected uncertainty** (the world has changed). Both lead to faster learning
  from new data, so ACh and NE both push the learning rate, not only ACh.

## Relevance to building brain-like AI
- The idea that a few **global scalars** retune a whole network is cheap to
  implement and matches what modern agents do by hand: schedule learning rates,
  anneal exploration, choose a horizon. A brain-like system would set them online
  from its own surprise and uncertainty.
- A practical recipe from Yu & Dayan: track prediction error, and raise the learning
  rate when errors are larger than the model's own noise estimate (the world
  changed), lower it when they match it.
- Three-factor rules with *several* modulators (one per sign or per timescale) are
  a natural extension of dopamine-only eligibility-trace learning.

## Code
Doya's mapping in a toy agent: `γ` decides whether to wait for a bigger reward,
`β` how often it explores, and `α` how fast it adapts after the reward switches arms.

```python
import numpy as np

rng = np.random.default_rng(0)

def softmax(q, beta):
    p = np.exp(beta * (q - q.max()))
    return p / p.sum()

# 5-HT ~ gamma: reward 1 now, or reward 3 after a 5-step wait
def waits(gamma):
    return 3 * gamma**5 > 1

# NE ~ beta: probability of picking the worse of two arms (values 1.0 and 0.5)
def explore_rate(beta):
    return softmax(np.array([1.0, 0.5]), beta)[1]

# ACh ~ alpha: trials until the agent prefers arm 1 after reward moves there from arm 0
def trials_to_switch(alpha, beta=5.0):
    q = np.array([1.0, 0.0])
    for t in range(1, 500):
        a = rng.choice(2, p=softmax(q, beta))
        q[a] += alpha * ((1.0 if a == 1 else 0.0) - q[a])
        if q[1] > q[0]:
            return t
    return 500

print("waits for bigger reward, gamma 0.9 / 0.7:", waits(0.9), waits(0.7))
print(f"explore rate, beta 1 / 10: {explore_rate(1):.2f} / {explore_rate(10):.3f}")
fast = np.mean([trials_to_switch(0.5) for _ in range(50)])
slow = np.mean([trials_to_switch(0.05) for _ in range(50)])
print(f"trials to adapt, alpha 0.5 / 0.05: {fast:.1f} / {slow:.1f}")
assert waits(0.9) and not waits(0.7)
assert explore_rate(1) > 0.3 > 0.01 > explore_rate(10)
assert fast < slow
```

## Open questions
- Whether serotonin has one computational role or several (patience, aversive
  prediction, behavioural inhibition) mixed by different raphe subpopulations.
- How far tonic vs phasic firing of the same nucleus carries different signals.
- Whether modulators are as global as "broadcast" suggests; projections and receptor
  distributions are target-specific, so the same release can have different effects
  in different areas.

## Related
- [[learning-and-plasticity]] - dopamine as TD error and three-factor rules.
- [[spiking-neural-networks]] - neuromodulated STDP in code.
- [[brain-structure-overview]] - where the source nuclei sit.
- [[brain-inspired-learning-algorithms]] - learning rules a modulator would gate.

## References
- Doya (2002) "Metalearning and neuromodulation", *Neural Networks* 15:495. doi:10.1016/S0893-6080(02)00044-8
- Schultz, Dayan & Montague (1997) "A neural substrate of prediction and reward", *Science* 275:1593. doi:10.1126/science.275.5306.1593
- Hasselmo (2006) "The role of acetylcholine in learning and memory", *Curr Opin Neurobiol* 16:710. doi:10.1016/j.conb.2006.09.002
- Sara (2009) "The locus coeruleus and noradrenergic modulation of cognition", *Nat Rev Neurosci* 10:211. doi:10.1038/nrn2573
- Aston-Jones & Cohen (2005) "An integrative theory of locus coeruleus-norepinephrine function: adaptive gain and optimal performance", *Annu Rev Neurosci* 28:403. doi:10.1146/annurev.neuro.28.061604.135709
- Hannon & Hoyer (2008) "Molecular biology of 5-HT receptors", *Behav Brain Res* 195:198. doi:10.1016/j.bbr.2008.03.020
- Cools, Nakamura & Daw (2011) "Serotonin and dopamine: unifying affective, activational, and decision functions", *Neuropsychopharmacology* 36:98. doi:10.1038/npp.2010.121
- Miyazaki et al. (2014) "Optogenetic activation of dorsal raphe serotonin neurons enhances patience for future rewards", *Curr Biol* 24:2033. doi:10.1016/j.cub.2014.07.041
- Yu & Dayan (2005) "Uncertainty, neuromodulation, and attention", *Neuron* 46:681. doi:10.1016/j.neuron.2005.04.026
- Seol et al. (2007) "Neuromodulators control the polarity of spike-timing-dependent synaptic plasticity", *Neuron* 55:919. doi:10.1016/j.neuron.2007.08.013
- Frémaux & Gerstner (2016) "Neuromodulated spike-timing-dependent plasticity, and theory of three-factor learning rules", *Front Neural Circuits* 9:85. doi:10.3389/fncir.2015.00085
