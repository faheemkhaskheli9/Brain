---
title: Start here (entry point)
category: guides
tags: [entry-point, chooser, reading-order, overview]
use_cases:
  - I want to learn how the human brain works from the beginning
  - I want to build a brain-like AI and do not know which file to read
  - find the right file for a brain or neuro-AI question
status: draft
last_verified: 2026-10-11
sources:
  - https://neuronaldynamics.epfl.ch/
---

# Start here

## Summary
This KB answers three questions in order: what the brain is made of, how it
works, and how to build a computer that learns like it. Pick a path below, or
use the question table to jump to one file.

## Reading paths

**Path A: understand the brain (no code)**
1. [[brain-structure-overview]] - regions, numbers, wiring.
2. [[neurons-and-synapses]] - the components.
3. [[neural-coding-and-computation]] - how spikes carry information.
4. [[learning-and-plasticity]] - how synapses learn.
5. [[memory-systems]] - how memories form and consolidate.
6. [[predictive-processing]] - how perception works (leading theory).

**Path B: simulate the brain**
1. [[levels-of-brain-modeling]] - choose the level of detail.
2. [[spiking-neural-networks]] - code neurons, STDP, simulators.
3. [[neuromorphic-hardware]] - chips that run it efficiently.
4. [[whole-brain-emulation-projects]] - connectomes and real-brain simulations.

**Path C: make a computer learn like a brain**
1. [[brain-vs-deep-learning]] - the gap to close.
2. [[brain-inspired-learning-algorithms]] - runnable learning rules.
3. [[build-a-brain-like-learner]] - the staged project roadmap.

**Path D: learn by playing.** `python game/play.py` runs Brain Lab, eight levels
in which you operate the models from these files: a spiking neuron, STDP, dopamine,
Hopfield memory, sleep replay, predictive tracking and a three-factor forager. See
[game/README.md](../game/README.md).

## Question → file
| Question | File |
|---|---|
| How many neurons, what does the hippocampus do? | [[brain-structure-overview]] |
| What is an action potential? | [[neurons-and-synapses]] |
| Why is the brain so energy-efficient? | [[neural-coding-and-computation]] |
| What are Hebbian learning, STDP and dopamine RPE? | [[learning-and-plasticity]] |
| How does the brain avoid catastrophic forgetting? | [[memory-systems]] |
| What is predictive coding / the free-energy principle? | [[predictive-processing]] |
| Hodgkin-Huxley vs LIF? How much compute for a whole brain? | [[levels-of-brain-modeling]] |
| How do I simulate a spiking network in Python? | [[spiking-neural-networks]] |
| Loihi, SpiNNaker, TrueNorth? | [[neuromorphic-hardware]] |
| FlyWire, MICrONS, Blue Brain, can we upload a brain? | [[whole-brain-emulation-projects]] |
| Can the brain do backprop? | [[brain-vs-deep-learning]] |
| Code a learning rule without backprop | [[brain-inspired-learning-algorithms]] |
| Plan a brain-like AI project | [[build-a-brain-like-learner]] |
| What does a term mean? | [[glossary]] |

## Best general resources
- Kandel et al., *Principles of Neural Science*: the standard neuroscience textbook.
- Dayan & Abbott, *Theoretical Neuroscience*: the maths of neural coding and learning.
- Gerstner et al., *Neuronal Dynamics* (free online): neuron models and plasticity, with Python exercises.
- Neuromatch Academy (free online course with notebooks): computational neuroscience and NeuroAI.

## Related
- [[glossary]] - terms used across the KB.
- [[build-a-brain-like-learner]] - the practical goal of this KB.
