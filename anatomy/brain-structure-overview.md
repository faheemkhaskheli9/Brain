---
title: Brain structure overview
category: anatomy
tags: [anatomy, cortex, hippocampus, thalamus, basal-ganglia, cerebellum, brainstem, neocortex]
use_cases:
  - what are the main parts of the human brain and what does each do
  - which brain regions should a brain-inspired AI architecture copy
  - how many neurons and synapses does the human brain have
status: stable
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
| Power | ~20 W is the usual figure; Herculano-Houzel estimates ~516 kcal/day (~25 W), about 25% of the body's energy use | Herculano-Houzel 2012 |
| Cortical thickness | 2-4 mm, folded; 6 layers | textbook |

The rows can be checked against each other. The derived numbers below are
arithmetic on the table, not new measurements.

```python
neurons, cortex, cerebellum = 86e9, 16e9, 69e9   # Azevedo et al. 2009
synapses = (1e14, 1e15)                          # order-of-magnitude range
watts = 20                                       # usual figure; Herculano-Houzel 2012 gives ~25 W

assert cortex + cerebellum <= neurons            # the rest: brainstem, thalamus, basal ganglia...
share = cerebellum / neurons
assert 0.75 < share < 0.85, share                # "about 80% of all neurons"
per_neuron = [s / neurons for s in synapses]     # ~1,200 to ~12,000 synapses per neuron
assert per_neuron[0] < 1e4 < per_neuron[1]       # brackets ~10,000 per pyramidal cell
print(f"cerebellum {share:.0%} of neurons; outside cortex and cerebellum {(neurons - cortex - cerebellum) / 1e9:.0f} billion")
print(f"synapses per neuron {per_neuron[0]:,.0f} to {per_neuron[1]:,.0f}")
print(f"power per neuron {watts / neurons * 1e9:.2f} nW")
```

The 10^14 to 10^15 range brackets the ~10,000 synapses of one pyramidal cell
([[neurons-and-synapses]]), and the 20 W works out to about a quarter of a nanowatt
per neuron.

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

### What lesions show
Much of the table above was first learned from damage: lose one region and the
behaviour that breaks shows what it was doing. These are **established** classic
cases. Real lesions are rarely confined to one region.

| Region lost | What breaks | What survives | Source |
|---|---|---|---|
| Hippocampus (both sides) | Forming new episodic memories | Older memories, skills, intelligence | Patient H.M., Scoville & Milner 1957 |
| Basal ganglia (Parkinson's disease) | Gradual habit learning from feedback | Memory of the training episodes | Knowlton, Mangels & Squire 1996 |
| Amygdala | Conditioned fear | Knowing the facts of what happened | Bechara et al. 1995; patient S.M., Feinstein et al. 2011 |
| Dorsolateral prefrontal cortex | Holding a location in mind over a delay | Responding when no delay is needed | Funahashi, Bruce & Goldman-Rakic 1993 (monkeys) |
| Occipitotemporal cortex (face areas) | Recognising faces (prosopagnosia) | Recognising people by voice | Barton 2008 |
| Cerebellum | Smooth, well-timed movement (ataxia) | Strength and sensation | Holmes 1917 |
| Thalamus | Sensation from the opposite side of the body | The sense organs themselves | Schmahmann 2003 |
| Brainstem | Breathing, arousal; it holds the dopamine nuclei | - | Kandel et al. 2021 |

The hippocampus and basal ganglia rows form a **double dissociation**: each
lesion spares what the other one breaks. That is the classic evidence for
separate memory systems ([[memory-systems]]). Brain Lab level 3 is built on this table.

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
- [[cortical-layers-and-columns]] - the six layers of the neocortex, columns and the canonical microcircuit.
- [[memory-systems]] - hippocampus and cortex in detail.
- [[learning-and-plasticity]] - the learning rules each region uses.
- [[levels-of-brain-modeling]] - at what level of detail to simulate these regions.
- [[action-selection-and-motor-control]] - basal ganglia, cerebellum and motor cortex in detail.
- [[attention-and-working-memory]] - prefrontal cortex and thalamus in attention and working memory.
- [[glia-and-energy-budget]] - the glial half of the cell count, and what the 20 W is spent on.
- [Brain Lab](../game/README.md) - level 3, *Lesion lab*: name each region from what breaks when it is lesioned.

## References
- Azevedo et al. (2009) "Equal numbers of neuronal and nonneuronal cells make the human brain an isometrically scaled-up primate brain", *J Comp Neurol*. doi:10.1002/cne.21974
- Herculano-Houzel (2012) "The remarkable, yet not extraordinary, human brain as a scaled-up primate brain and its associated cost", *PNAS*. doi:10.1073/pnas.1201895109
- Kandel et al., *Principles of Neural Science* (6th ed., 2021), the standard textbook.
- Scoville & Milner (1957) "Loss of recent memory after bilateral hippocampal lesions", *J Neurol Neurosurg Psychiatry* 20:11. doi:10.1136/jnnp.20.1.11
- Knowlton, Mangels & Squire (1996) "A neostriatal habit learning system in humans", *Science* 273:1399. doi:10.1126/science.273.5280.1399
- Bechara et al. (1995) "Double dissociation of conditioning and declarative knowledge relative to the amygdala and hippocampus in humans", *Science* 269:1115. doi:10.1126/science.7652558
- Feinstein et al. (2011) "The human amygdala and the induction and experience of fear", *Curr Biol* 21:34. doi:10.1016/j.cub.2010.11.042
- Funahashi, Bruce & Goldman-Rakic (1993) "Dorsolateral prefrontal lesions and oculomotor delayed-response performance", *J Neurosci* 13:1479. doi:10.1523/JNEUROSCI.13-04-01479.1993
- Barton (2008) "Structure and function in acquired prosopagnosia: lessons from a series of 10 patients with brain damage", *J Neuropsychol* 2:197. doi:10.1348/174866407x214172
- Holmes (1917) "The symptoms of acute cerebellar injuries due to gunshot injuries", *Brain* 40:461. doi:10.1093/brain/40.4.461
- Schmahmann (2003) "Vascular syndromes of the thalamus", *Stroke* 34:2264. doi:10.1161/01.STR.0000087786.38997.9E
