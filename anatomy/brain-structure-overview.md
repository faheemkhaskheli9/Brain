---
title: Brain structure overview
category: anatomy
tags: [anatomy, cortex, hippocampus, thalamus, basal-ganglia, cerebellum, brainstem, neocortex]
use_cases:
  - what are the main parts of the human brain and what does each do
  - which brain regions should a brain-inspired AI architecture copy
  - how many neurons and synapses does the human brain have
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1002/cne.21974
  - https://doi.org/10.1073/pnas.1201895109
---

# Brain structure overview

## Summary
The human brain weighs about 1.4 kg, contains roughly **86 billion neurons** and a
similar number of glial cells, and runs on about **20 watts**. It is not one uniform
network. It is a set of specialised subsystems (cortex, hippocampus, basal ganglia,
cerebellum, thalamus, brainstem) wired in loops. Each uses different circuitry and
different learning rules, which matters a lot when you try to copy it.

## How it works

### Key numbers
| Quantity | Value | Source |
|---|---|---|
| Neurons | ~86 billion | Azevedo et al. 2009 |
| Neurons in the cerebral cortex | ~16 billion | Azevedo 2009; Herculano-Houzel 2012 |
| Neurons in the cerebellum | ~69 billion (about 80% of all neurons) | Azevedo 2009 |
| Synapses | about 10^14 to 10^15 (an order-of-magnitude estimate) | textbook estimate |
| Power | ~20 W, about 20% of the body's resting energy use | Herculano-Houzel 2012 |
| Cortical thickness | 2-4 mm, folded; 6 layers | textbook |

### The major subsystems
| Region | Main job | Learning style | AI analogue |
|---|---|---|---|
| **Neocortex** | Perception, language, reasoning, planning. Repeating 6-layer "columns" | Slow, unsupervised and predictive, Hebbian plus neuromodulation | Deep hierarchical networks, transformers, predictive coding |
| **Hippocampus** (medial temporal lobe) | Fast episodic memory ("what happened where, when"), spatial maps (place and grid cells) | One-shot, rapid | Replay buffer, key-value memory, retrieval (RAG) |
| **Basal ganglia** (striatum etc.) | Action selection, habits | Reinforcement learning driven by dopamine | Actor-critic RL |
| **Cerebellum** | Fine motor timing, error correction, forward models | Supervised, driven by an error signal from climbing fibres | Supervised regression, forward models |
| **Thalamus** | Relay and gating of signals into the cortex; attention | - | Routing and gating, attention |
| **Amygdala** | Emotional salience, fear learning | Fast associative | Value and salience tagging |
| **Prefrontal cortex** | Working memory, goals, cognitive control | Gated by dopamine | Recurrent controller, context window |
| **Brainstem and hypothalamus** | Vital functions, arousal, drives; source of the neuromodulators | Mostly innate | Reward function, global "learning-rate" signals |

### Wiring principles
- **Hierarchy with feedback.** Visual cortex runs V1 → V2 → V4 → IT. Feedback
  connections are at least as numerous as feedforward ones.
- **Loops.** Cortex → basal ganglia → thalamus → cortex; cortex → cerebellum → thalamus → cortex.
- **Two hemispheres** joined by the corpus callosum. They are partly lateralised
  (in most people, language sits mostly on the left).
- **Small-world network.** Dense local wiring plus a few long-range hubs.
- **Neuromodulators broadcast globally.** Dopamine, serotonin, acetylcholine and
  noradrenaline come from small brainstem and basal-forebrain nuclei and project
  to the whole brain. They change *how* circuits learn, not *what* they encode.

## Relevance to building brain-like AI
- The brain is a **modular system of different learners**: unsupervised cortex,
  one-shot hippocampus, RL basal ganglia, supervised cerebellum. A single
  backprop-trained network is closer to "just cortex". See [[memory-systems]].
- The 20 W budget comes from sparse, event-driven spiking and from co-locating
  memory and compute. See [[neural-coding-and-computation]] and [[neuromorphic-hardware]].

## Open questions
- What exactly the canonical cortical microcircuit computes (predictive coding is
  the leading hypothesis, not a settled fact).
- How the subsystems coordinate to produce general intelligence.

## Related
- [[neurons-and-synapses]] - the components these regions are built from.
- [[memory-systems]] - hippocampus and cortex in detail.
- [[learning-and-plasticity]] - the learning rules each region uses.
- [[levels-of-brain-modeling]] - at what level of detail to simulate these regions.

## References
- Azevedo et al. (2009) "Equal numbers of neuronal and nonneuronal cells make the human brain an isometrically scaled-up primate brain", *J Comp Neurol*. doi:10.1002/cne.21974
- Herculano-Houzel (2012) "The remarkable, yet not extraordinary, human brain as a scaled-up primate brain and its associated cost", *PNAS*. doi:10.1073/pnas.1201895109
- Kandel et al., *Principles of Neural Science* (6th ed., 2021), the standard textbook.
