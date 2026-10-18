---
title: Glossary
category: guides
tags: [glossary, definitions, terms]
use_cases:
  - what does this neuroscience or neuro-AI term mean
status: stable
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
| Astrocyte | Star-shaped glial cell that regulates synapses, blood flow and transmitter recycling | [[glia-and-energy-budget]] |
| Attractor | A stable activity pattern a recurrent network settles into | [[neural-coding-and-computation]] |
| Backpropagation | Computing exact error gradients backwards through a network | [[brain-vs-deep-learning]] |
| Basal ganglia (Go / NoGo) | Subcortical loop that selects actions; in the Go/NoGo model the direct (Go) pathway learns from dopamine rises and the indirect (NoGo) one from dips | [[action-selection-and-motor-control]] |
| Binding (in hyperdimensional computing) | Combining a role vector and a filler vector into one vector that can later be unbound | [[hyperdimensional-computing]] |
| Brain-computer interface (BCI) | A system that decodes recorded neural activity into commands such as cursor movement or speech | [[brain-computer-interfaces]] |
| Brain-Score | Benchmark suite that scores models by how well they predict neural and behavioural data | [[evaluating-brain-models]] |
| Canonical microcircuit | Hypothesis that one layered cortical circuit repeats across areas and computes something general | [[cortical-layers-and-columns]] |
| Catastrophic forgetting | A network losing old skills when trained on new data | [[memory-systems]] |
| CLS (Complementary Learning Systems) | Theory: fast hippocampus + slow cortex + replay | [[memory-systems]] |
| Cognitive architecture | A fixed, general design for a whole mind (ACT-R, Soar, Spaun) into which task knowledge is loaded | [[cognitive-architectures]] |
| Connectome | Complete map of neurons and synapses | [[whole-brain-emulation-projects]] |
| Consolidation | Stabilising memories over time (synaptic) and moving them to cortex (systems) | [[memory-systems]] |
| Cortical column | Vertical group of neurons through the cortical layers that share response properties | [[cortical-layers-and-columns]] |
| Credit assignment | Working out which synapse caused an outcome | [[brain-vs-deep-learning]] |
| Critical period | A developmental window in which a circuit is unusually plastic and experience shapes it lastingly | [[brain-development-and-critical-periods]] |
| Dale's principle | A neuron releases the same transmitters at all its synapses, so it is either excitatory or inhibitory | [[neurons-and-synapses]] |
| Dendrite | Input branch of a neuron; can compute nonlinearly (dendritic spikes) | [[neurons-and-synapses]], [[dendritic-computation]] |
| Dopamine RPE | Dopamine neurons signal reward prediction error, like the TD error | [[learning-and-plasticity]] |
| Drift-diffusion model | Decision model that accumulates noisy evidence to a bound; explains the speed-accuracy trade-off | [[decision-making]] |
| Echo-state network | Reservoir computing with a fixed random recurrent network; only the linear readout is trained | [[reservoir-computing]] |
| Eligibility trace | A decaying synaptic tag that a later reward can turn into learning | [[learning-and-plasticity]] |
| EWC | Elastic Weight Consolidation: penalise changing important weights | [[brain-inspired-learning-algorithms]] |
| False-belief task | Test of theory of mind: predict what someone will do when they believe something that is no longer true | [[social-cognition-and-theory-of-mind]] |
| FlyHash | Similarity-search hash modelled on the fly olfactory circuit: sparse random expansion, then winner-take-all | [[other-sensory-systems]] |
| Free-energy principle | Friston's theory that organisms minimise a bound on surprise | [[predictive-processing]] |
| Global workspace theory | Hypothesis that conscious content is information broadcast widely across the cortex | [[theories-of-consciousness]] |
| Grid cell | Entorhinal neuron that fires at the vertices of a hexagonal lattice across an environment | [[spatial-navigation]] |
| Hebbian learning | Strengthen a synapse when pre and post are active together | [[learning-and-plasticity]] |
| Hodgkin-Huxley model | 4-ODE biophysical model of the spike | [[levels-of-brain-modeling]] |
| Homeostatic plasticity | Rules that keep firing rates in a stable range | [[learning-and-plasticity]] |
| Hopfield network | Recurrent network that stores patterns as attractors | [[memory-systems]] |
| Hyperdimensional computing (VSA) | Computing with very long random vectors combined by binding, bundling and permutation | [[hyperdimensional-computing]] |
| Integrated information theory (IIT) | Hypothesis that consciousness is integrated information (Φ) in a system's causal structure | [[theories-of-consciousness]] |
| Interoception | Sensing the body's internal state (heartbeat, breathing, gut); the insula is a key cortical area | [[emotion-amygdala-and-interoception]] |
| LIF neuron | Leaky integrate-and-fire: the simplest common spiking model | [[spiking-neural-networks]] |
| LTP / LTD | Long-term potentiation / depression of synapses | [[learning-and-plasticity]] |
| Mirror neuron | Neuron that fires both when an animal acts and when it watches the same act; what it explains is contested | [[social-cognition-and-theory-of-mind]] |
| Mixed selectivity | A neuron responding to combinations of task variables rather than to one; common in prefrontal cortex | [[prefrontal-cortex-and-abstraction]] |
| Neural manifold | The low-dimensional surface that a population's joint activity stays close to | [[population-dynamics-and-neural-manifolds]] |
| Neuromodulator | Broadcast chemical (dopamine, ACh, NE, 5-HT) that changes how circuits learn | [[neuromodulators]] |
| Neuromorphic | Hardware that mimics neural organisation: spikes, local memory | [[neuromorphic-hardware]] |
| Path integration | Tracking one's own position by adding up self-motion, with no landmarks | [[spatial-navigation]] |
| Pattern separation / completion | Making similar inputs distinct / recalling a whole from a part | [[memory-systems]] |
| Phase precession | A place cell firing at earlier phases of the theta rhythm as the animal crosses its field | [[brain-rhythms-and-oscillations]] |
| Place cell | Hippocampal neuron that fires when the animal is in one location (its place field) | [[spatial-navigation]] |
| Precision (predictive processing) | The estimated reliability of a prediction error, which sets how much it changes beliefs | [[predictive-processing]] |
| Predictive coding | Higher areas predict lower ones; only errors propagate up | [[predictive-processing]] |
| Replay | Reactivating past experience, during sleep and quiet waking rest | [[memory-systems]] |
| Reservoir computing | Using a fixed random dynamical system as a feature expansion and training only a readout | [[reservoir-computing]] |
| Ring attractor | Recurrent network whose stable states form a ring, so it can hold an angle such as head direction | [[population-dynamics-and-neural-manifolds]] |
| RSA (representational similarity analysis) | Comparing a model and a brain by the similarity structure of their responses to the same stimuli | [[evaluating-brain-models]] |
| Sharp-wave ripple | Brief fast hippocampal oscillation during rest and sleep that carries compressed replay | [[sleep-and-memory-consolidation]] |
| SHY (synaptic homeostasis hypothesis) | Hypothesis that sleep scales synapses back down after waking potentiation | [[sleep-and-memory-consolidation]] |
| Sparse coding | Representing input with few active neurons | [[neural-coding-and-computation]] |
| Spiking neural network (SNN) | Network of neurons that communicate with discrete spikes in time | [[spiking-neural-networks]] |
| STDP | Spike-timing-dependent plasticity: pre-before-post strengthens, post-before-pre weakens | [[spiking-neural-networks]] |
| Surrogate gradient | Smooth stand-in derivative that lets backprop train spiking nets | [[spiking-neural-networks]] |
| Theory of mind | Attributing beliefs, desires and intentions to others to predict what they will do | [[social-cognition-and-theory-of-mind]] |
| Three-factor rule | Δw = Hebbian term × neuromodulator signal | [[brain-inspired-learning-algorithms]] |
| Time cell | Hippocampal neuron that fires at one moment within a delay, as place cells do at one location | [[timing-and-sequence-learning]] |
| Tonotopy | Orderly mapping of sound frequency along the cochlea and auditory cortex | [[other-sensory-systems]] |
| Whole-brain emulation | Scanning and simulating a specific brain in full detail | [[whole-brain-emulation-projects]] |
| Working memory | Holding and manipulating a few items over seconds; limited in capacity | [[attention-and-working-memory]] |

## Related
- [[start-here]] - reading paths through the KB.
