---
title: Learning and synaptic plasticity
category: function
tags: [hebbian, stdp, ltp, ltd, dopamine, reward-prediction-error, neuromodulation, three-factor, homeostasis, plasticity]
use_cases:
  - how does the brain learn at the level of synapses
  - what learning rules could replace backpropagation in a brain-like system
  - how does dopamine relate to reinforcement learning
status: stable
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1523/JNEUROSCI.18-24-10464.1998
  - https://doi.org/10.1126/science.275.5306.1593
  - https://doi.org/10.1038/361031a0
  - https://doi.org/10.3389/fncir.2018.00053
---

# Learning and synaptic plasticity

## Summary
The brain learns mainly by changing synapse strengths, and it does so with
**local** rules: a synapse sees only its own pre- and postsynaptic activity, plus
a few **global broadcast signals** (neuromodulators such as dopamine). No error
gradient is sent backwards through the network the way backpropagation does it.
The core recipe is roughly *Hebbian coincidence × neuromodulator × homeostatic
stabilisation*, wrapped in sleep-driven replay and consolidation.

## How it works

### 1. Hebbian learning, LTP and LTD
"Cells that fire together wire together" (Carla Shatz's 1992 paraphrase of Hebb 1949). The molecular mechanism is
established:
- **LTP** (long-term potentiation): strong pre + post activity → NMDA receptors
  open → Ca2+ influx → more AMPA receptors inserted → a stronger synapse. First
  shown by Bliss & Lømo (1973); Bliss & Collingridge (1993) is the classic review.
- **LTD** (long-term depression): weak or uncorrelated activity → a weaker synapse.
- Pure Hebbian growth is unstable (weights explode). Models add normalisation:
  Oja's rule `Δw = η·y·(x − y·w)` makes a neuron learn the first principal
  component of its input ([[brain-inspired-learning-algorithms]]).

### 2. Spike-timing-dependent plasticity (STDP)
Timing matters (Markram et al. 1997; Bi & Poo 1998):
- pre spike **before** post (by up to ~20 ms) → potentiation, "pre caused post";
- pre **after** post → depression.

`Δw = A+ · exp(−Δt/τ+)` when `Δt = t_post − t_pre > 0`, and `−A− · exp(Δt/τ−)` when it is negative.
STDP learns causal sequences and makes neurons pick up repeating input patterns.
Code: [[spiking-neural-networks]].

### 3. Neuromodulation and three-factor rules
Hebbian coincidence alone cannot know whether an outcome was *good*. The brain
adds a third factor:
- **Dopamine = reward prediction error (RPE).** Dopamine neurons fire more for
  unexpected reward, do not change for predicted reward, and dip when a predicted
  reward is missing. This matches the TD error `δ = r + γV(s') − V(s)` of
  temporal-difference RL (Schultz, Dayan & Montague 1997), one of the strongest
  links between neuroscience and AI.
- **Eligibility traces.** A Hebbian coincidence leaves a decaying synaptic "tag".
  If dopamine arrives within ~1 s, the tag becomes a lasting change. This solves
  credit assignment over time:
  `Δw = η · eligibility(pre, post) · M(t)`, where M is the neuromodulator signal.
  See Gerstner et al. (2018) on "neoHebbian three-factor rules".
- **Acetylcholine**: signals uncertainty and novelty, raises plasticity and
  bottom-up attention. **Noradrenaline**: surprise, arousal, "reset" of network
  state. **Serotonin**: patience and time horizon, aversive prediction (less settled).
  Details and the meta-parameter hypothesis: [[neuromodulators]].

### 4. Homeostatic plasticity
Neurons keep their average firing rate in range by scaling all their synapses up
or down (synaptic scaling), adjusting intrinsic excitability, and through the
sliding threshold of the BCM rule. These rules stop Hebbian learning from running away.

### 5. Structural plasticity and development
Synapses and dendritic spines are created and pruned continuously. Childhood
overproduces synapses and then prunes them. New neurons are born in adulthood only in
limited regions; how much this happens in the adult human hippocampus is debated.

### 6. Systems-level learning
- **Fast hippocampal + slow cortical learning**, consolidated by replay during
  sleep: [[memory-systems]].
- **Predictive learning**: much cortical learning may be driven by prediction
  errors on sensory input, a kind of self-supervised learning ([[predictive-processing]]).
- **Critical periods**: some circuits (e.g. ocular dominance in V1) are plastic only
  early in life. Learning rates are themselves scheduled and regulated.

## What humans learn that current AI struggles with
| Ability | Brain mechanism (best current account) |
|---|---|
| One-shot learning of a new fact or episode | Hippocampal rapid binding |
| Learning continually without forgetting old skills | Complementary memory systems, replay, synaptic consolidation |
| Learning from few labels | Mostly self-supervised predictive learning plus strong innate priors |
| Learning from reward with delays | Dopamine TD error plus eligibility traces |
| Learning efficiently from limited energy and data | Sparse coding, active exploration, curiosity |

## Relevance to building brain-like AI
- Local rules (Hebbian, STDP, three-factor) scale well on neuromorphic hardware
  because no global backward pass is needed.
- On their own they have so far learned far worse than backprop on hard tasks.
  The open problem is **credit assignment**. Leading candidates are in [[brain-vs-deep-learning]].
- Dopamine-as-TD-error is directly usable: actor-critic RL is already
  brain-like at the systems level.

## Related
- [[neurons-and-synapses]] - NMDA receptors as coincidence detectors.
- [[spiking-neural-networks]] - STDP and three-factor rules in code.
- [[brain-inspired-learning-algorithms]] - Hebbian, Oja and predictive coding in code.
- [[memory-systems]] - consolidation and replay.
- [[neuromodulators]] - ACh, NE and serotonin beyond dopamine.
- [[brain-development-and-critical-periods]] - when plasticity is high, and what closes it.
- [Brain World](../game/world/) - TD dopamine and eligibility traces teaching a 3D creature five skills in a row.
- [Brain Lab](../game/README.md) - level 2, *Wire together* (STDP), and level 4, *Be the dopamine* (TD error moving to the cue).

## References
- Bi & Poo (1998) "Synaptic modifications in cultured hippocampal neurons", *J Neurosci* 18:10464. doi:10.1523/JNEUROSCI.18-24-10464.1998
- Schultz, Dayan & Montague (1997) "A neural substrate of prediction and reward", *Science* 275:1593. doi:10.1126/science.275.5306.1593
- Bliss & Collingridge (1993) "A synaptic model of memory: long-term potentiation in the hippocampus", *Nature* 361:31. doi:10.1038/361031a0
- Gerstner, Lehmann, Liakoni, Corneil & Brea (2018) "Eligibility traces and plasticity on behavioral time scales", *Front Neural Circuits* 12:53.
- Kuśmierz, Isomura & Toyoizumi (2017) "Learning with three factors", *Curr Opin Neurobiol* 46:170.
- Markram, Lübke, Frotscher & Sakmann (1997), *Science* 275:213.
- Turrigiano (2008) "The self-tuning neuron: synaptic scaling of excitatory synapses", *Cell* 135:422.
