---
title: Glossary
category: guides
tags: [glossary, definitions, terms]
use_cases:
  - what does this neuroscience or neuro-AI term mean
status: draft
last_verified: 2026-10-11
sources:
  - https://neuronaldynamics.epfl.ch/
---

# Glossary

## Summary
Short definitions of the terms used across this KB, each pointing to the file that explains it.

| Term | Meaning | More |
|---|---|---|
| Action potential (spike) | All-or-nothing ~1 ms voltage pulse a neuron sends down its axon | [[neurons-and-synapses]] |
| Active inference | Acting to make sensory input match predictions; part of the free-energy principle | [[predictive-processing]] |
| AMPA / NMDA receptors | Glutamate receptors; NMDA needs both glutamate and depolarisation, so it detects coincidence | [[neurons-and-synapses]] |
| Attractor | A stable activity pattern a recurrent network settles into | [[neural-coding-and-computation]] |
| Backpropagation | Computing exact error gradients backwards through a network | [[brain-vs-deep-learning]] |
| Catastrophic forgetting | A network losing old skills when trained on new data | [[memory-systems]] |
| CLS (Complementary Learning Systems) | Theory: fast hippocampus + slow cortex + replay | [[memory-systems]] |
| Connectome | Complete map of neurons and synapses | [[whole-brain-emulation-projects]] |
| Consolidation | Stabilising memories over time (synaptic) and moving them to cortex (systems) | [[memory-systems]] |
| Credit assignment | Working out which synapse caused an outcome | [[brain-vs-deep-learning]] |
| Dale's principle | A neuron releases the same transmitters at all its synapses, so it is either excitatory or inhibitory | [[neurons-and-synapses]] |
| Dendrite | Input branch of a neuron; can compute nonlinearly | [[neurons-and-synapses]] |
| Dopamine RPE | Dopamine neurons signal reward prediction error, like the TD error | [[learning-and-plasticity]] |
| Eligibility trace | A decaying synaptic tag that a later reward can turn into learning | [[learning-and-plasticity]] |
| EWC | Elastic Weight Consolidation: penalise changing important weights | [[brain-inspired-learning-algorithms]] |
| Free-energy principle | Friston's theory that organisms minimise a bound on surprise | [[predictive-processing]] |
| Hebbian learning | Strengthen a synapse when pre and post are active together | [[learning-and-plasticity]] |
| Hodgkin-Huxley model | 4-ODE biophysical model of the spike | [[levels-of-brain-modeling]] |
| Homeostatic plasticity | Rules that keep firing rates in a stable range | [[learning-and-plasticity]] |
| Hopfield network | Recurrent network that stores patterns as attractors | [[memory-systems]] |
| LIF neuron | Leaky integrate-and-fire: the simplest common spiking model | [[spiking-neural-networks]] |
| LTP / LTD | Long-term potentiation / depression of synapses | [[learning-and-plasticity]] |
| Neuromodulator | Broadcast chemical (dopamine, ACh, NE, 5-HT) that changes how circuits learn | [[learning-and-plasticity]] |
| Neuromorphic | Hardware that mimics neural organisation: spikes, local memory | [[neuromorphic-hardware]] |
| Pattern separation / completion | Making similar inputs distinct / recalling a whole from a part | [[memory-systems]] |
| Predictive coding | Higher areas predict lower ones; only errors propagate up | [[predictive-processing]] |
| Replay | Reactivating past experience, mostly during sleep | [[memory-systems]] |
| Sparse coding | Representing input with few active neurons | [[neural-coding-and-computation]] |
| STDP | Spike-timing-dependent plasticity: pre-before-post strengthens, post-before-pre weakens | [[spiking-neural-networks]] |
| Surrogate gradient | Smooth stand-in derivative that lets backprop train spiking nets | [[spiking-neural-networks]] |
| Three-factor rule | Δw = Hebbian term × neuromodulator signal | [[brain-inspired-learning-algorithms]] |
| Whole-brain emulation | Scanning and simulating a specific brain in full detail | [[whole-brain-emulation-projects]] |

## Related
- [[start-here]] - reading paths through the KB.
