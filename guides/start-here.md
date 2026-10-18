---
title: Start here (entry point)
category: guides
tags: [entry-point, chooser, reading-order, overview]
use_cases:
  - I want to learn how the human brain works from the beginning
  - I want to build a brain-like AI and do not know which file to read
  - find the right file for a brain or neuro-AI question
status: stable
last_verified: 2026-10-11
sources:
  - https://neuronaldynamics.epfl.ch/
---

# Start here

## Summary
This KB answers three questions in order: what the brain is made of, how it
works, and how to build a computer that learns like it. Pick a path below, or
use the question table to jump to one file. For an ordered list by background
(ML engineer, neuroscience student, player of the games), see [[learning-paths]].
Theories of consciousness are all hypotheses and live in one file of their own:
[[theories-of-consciousness]].

## Reading paths

**Path A: understand the brain (no code)**
1. [[brain-structure-overview]] - regions, numbers, wiring.
2. [[neurons-and-synapses]] - the components.
3. [[cortical-layers-and-columns]] - how the cortex is layered and wired.
4. [[dendritic-computation]] - why one neuron is more like a small network.
5. [[glia-and-energy-budget]] - the other half of the cells, and where the 20 W goes.
6. [[neural-coding-and-computation]] - how spikes carry information.
7. [[brain-rhythms-and-oscillations]] - brain waves: where they come from and what they may do.
8. [[learning-and-plasticity]] - how synapses learn.
9. [[brain-development-and-critical-periods]] - wiring, pruning and windows of plasticity.
10. [[ageing-and-lifelong-plasticity]] - what changes with age, and how plasticity can return.
11. [[neuromodulators]] - ACh, NE and serotonin as learning dials.
12. [[emotion-amygdala-and-interoception]] - fear learning, value and the body's state.
13. [[memory-systems]] - how memories form and consolidate.
14. [[sleep-and-memory-consolidation]] - what sleep does to memory: replay and downscaling.
15. [[spatial-navigation]] - place cells, grid cells and the brain's map.
16. [[sensory-systems-and-vision]] - from retina to object recognition, and CNNs.
17. [[predictive-processing]] - how perception works (leading theory).

**Path B: simulate the brain**
1. [[levels-of-brain-modeling]] - choose the level of detail.
2. [[spiking-neural-networks]] - code neurons, STDP, simulators.
3. [[neuromorphic-hardware]] - chips that run it efficiently.
4. [[whole-brain-emulation-projects]] - connectomes and real-brain simulations.
5. [[evaluating-brain-models]] - test whether a model is actually brain-like.
6. [[measuring-the-brain-and-open-datasets]] - recording methods and the open data to test against.
7. [[neuroethics]] - moral status of simulations, organoids, and neural-data law.

**Path C: make a computer learn like a brain**
1. [[brain-vs-deep-learning]] - the gap to close.
2. [[brain-inspired-learning-algorithms]] - runnable learning rules.
3. [[build-a-brain-like-learner]] - the staged project roadmap.

**Path E: add something new.** [[open-questions-register]] ranks every open question
in this KB by whether a computer can answer it; [[research-with-ai]] is the workflow for
testing one with an AI assistant.

**Path D: learn by playing.** `python game/play.py` runs Brain Lab, eleven levels
in which you operate the models from these files: a spiking neuron, STDP, a lesion
lab, dopamine, Hopfield memory, sleep replay, predictive tracking, a three-factor
forager, Oja's rule, a neuron zoo and path integration with grid cells. See
[game/README.md](../game/README.md). The same levels run in a browser with nothing
to install: serve the repo root (`python -m http.server 8000`) and open
`http://localhost:8000/game/web/`.
[Brain World](../game/world/) puts those mechanisms together in one 3D creature that
learns to walk, grasp, listen, read and write from dopamine alone: run
`python -m http.server 8000` from the repo root, then open
`http://localhost:8000/game/world/`.

## Question → file
| Question | File |
|---|---|
| How many neurons, what does the hippocampus do? | [[brain-structure-overview]] |
| How do brains differ across species? Why are crows so clever with small brains? | [[comparative-and-evolutionary-neuroscience]] |
| What is an action potential? | [[neurons-and-synapses]] |
| What do the six cortical layers do? Are cortical columns real units? | [[cortical-layers-and-columns]] |
| Do dendrites compute? What is an NMDA spike? | [[dendritic-computation]] |
| What are theta and gamma waves? What is phase precession? | [[brain-rhythms-and-oscillations]] |
| What is a neural manifold, a ring attractor or a line attractor? | [[population-dynamics-and-neural-manifolds]] |
| How does the brain keep time without a clock? What are time cells? | [[timing-and-sequence-learning]] |
| Why is the brain so energy-efficient? | [[neural-coding-and-computation]] |
| What are Hebbian learning, STDP and dopamine RPE? | [[learning-and-plasticity]] |
| What is a critical period? Why do children learn languages more easily? | [[brain-development-and-critical-periods]] |
| What do babies know at birth? What is core knowledge? | [[innate-priors-and-infant-learning]] |
| How does the brain change with age? Why do networks lose plasticity? | [[ageing-and-lifelong-plasticity]] |
| What do glial cells do? What does the brain spend its energy on? | [[glia-and-energy-budget]] |
| How is fear learned? What does the amygdala or insula do? | [[emotion-amygdala-and-interoception]] |
| What is theory of mind? What do mirror neurons explain? | [[social-cognition-and-theory-of-mind]] |
| What do acetylcholine, noradrenaline and serotonin do? | [[neuromodulators]] |
| How does the brain avoid catastrophic forgetting? | [[memory-systems]] |
| What happens to memories during sleep? | [[sleep-and-memory-consolidation]] |
| How does working memory hold things, and what is attention? | [[attention-and-working-memory]] |
| What does the prefrontal cortex do? How are rules and task switches represented? | [[prefrontal-cortex-and-abstraction]] |
| How does the brain choose an action? What do the basal ganglia and cerebellum compute? | [[action-selection-and-motor-control]] |
| How does the brain decide under noise? What is the drift-diffusion model? | [[decision-making]] |
| How does one brain learn many tasks without a module per task? | [[one-brain-many-tasks]] |
| What are place cells and grid cells? How does an animal find its way home? | [[spatial-navigation]] |
| How does vision work? Why are CNNs compared to visual cortex? | [[sensory-systems-and-vision]] |
| How do hearing, touch, smell and pain work? What is FlyHash? | [[other-sensory-systems]] |
| What is predictive coding / the free-energy principle? | [[predictive-processing]] |
| What do Parkinson's, schizophrenia or depression reveal about the healthy brain? | [[brain-disorders-and-computational-psychiatry]] |
| Hodgkin-Huxley vs LIF? How much compute for a whole brain? | [[levels-of-brain-modeling]] |
| How do I simulate a spiking network in Python? | [[spiking-neural-networks]] |
| What is an echo-state network? Why train only the readout? | [[reservoir-computing]] |
| What are ACT-R, Soar, the NEF and Spaun? | [[cognitive-architectures]] |
| How do I measure whether my model is brain-like (RSA, Brain-Score)? | [[evaluating-brain-models]] |
| EEG vs fMRI vs Neuropixels? Where can I download real brain recordings? | [[measuring-the-brain-and-open-datasets]] |
| How does a brain-computer interface decode movement or speech? | [[brain-computer-interfaces]] |
| Loihi, SpiNNaker, TrueNorth? | [[neuromorphic-hardware]] |
| FlyWire, MICrONS, Blue Brain, can we upload a brain? | [[whole-brain-emulation-projects]] |
| Where is language in the brain? Do LLMs process language like brains? | [[language-and-llms]] |
| What is global workspace theory or IIT? Could an AI be conscious? | [[theories-of-consciousness]] |
| Is it ethical to simulate a brain? Which laws protect neural data? | [[neuroethics]] |
| Can the brain do backprop? | [[brain-vs-deep-learning]] |
| Code a learning rule without backprop | [[brain-inspired-learning-algorithms]] |
| Make a brain-like learner cheap: sparse, event-driven updates | [[efficient-brain-like-learning]] |
| Store a structured record in one vector (binding and bundling) | [[hyperdimensional-computing]] |
| Plan a brain-like AI project | [[build-a-brain-like-learner]] |
| Save a trained learner and load it so it acts the same | [[saving-and-reusing-a-trained-brain]] |
| What does a term mean? | [[glossary]] |
| Which paper is the evidence for a claim? | [[key-papers]] |
| Which open questions can I test myself? | [[open-questions-register]] |
| How do I use Claude to do research without fooling myself? | [[research-with-ai]] |

## Best general resources
- Kandel et al., *Principles of Neural Science*: the standard neuroscience textbook.
- Dayan & Abbott, *Theoretical Neuroscience*: the maths of neural coding and learning.
- Gerstner et al., *Neuronal Dynamics* (free online): neuron models and plasticity, with Python exercises.
- Neuromatch Academy (free online course with notebooks): computational neuroscience and NeuroAI.

## Related
- [[glossary]] - terms used across the KB.
- [[build-a-brain-like-learner]] - the practical goal of this KB.
- [[evaluating-brain-models]] - how to check the result against the brain.
