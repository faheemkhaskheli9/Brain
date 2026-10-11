---
title: Neurons, synapses and glia
category: anatomy
tags: [neuron, synapse, action-potential, dendrite, axon, neurotransmitter, glia, spike]
use_cases:
  - how does a single neuron work
  - what is an action potential and how is it modeled
  - how is a biological neuron different from an artificial neuron
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1113/jphysiol.1952.sp004764
  - https://doi.org/10.1016/j.neuron.2021.07.002
---

# Neurons, synapses and glia

## Summary
A neuron collects input on its **dendrites**, integrates it in the **soma**, and,
if its membrane voltage crosses a threshold (about -55 mV from a resting -70 mV),
fires an all-or-nothing **action potential** (a spike, ~1 ms) down its **axon**.
At **synapses** the spike releases neurotransmitter onto the next neuron. Each
synapse has a strength that changes with experience, and that change is the main
physical basis of learning. A biological neuron is far richer than the weighted
sum plus nonlinearity used in artificial networks.

## How it works

### The action potential
1. At rest, ion pumps keep the inside about 70 mV negative relative to outside
   (high K+ inside, high Na+ outside).
2. Excitatory input depolarises the membrane. At threshold, voltage-gated **Na+**
   channels open, Na+ rushes in, and the voltage spikes to about +40 mV.
3. Na+ channels inactivate and **K+** channels open, so the voltage falls back,
   briefly undershooting (the refractory period, which caps firing at a few hundred Hz).
4. The spike regenerates along the axon. Myelin (made by glia) makes it jump
   between nodes, at up to ~100 m/s.

Hodgkin and Huxley (1952) captured this in four differential equations, which
is still the gold-standard biophysical neuron model ([[levels-of-brain-modeling]]).

### Synapses
- **Chemical synapse.** A spike → Ca2+ influx → vesicles release transmitter →
  receptors on the next cell open → a small voltage change (a PSP).
  Release is **probabilistic**: a single synapse often fails to transmit.
- **Excitatory** synapses mostly use glutamate (AMPA and NMDA receptors).
  **Inhibitory** ones mostly use GABA. A neuron generally releases the same
  transmitters at all its outputs (Dale's principle), so it is excitatory or
  inhibitory, never both. In cortex ~80% of neurons are excitatory and ~20% inhibitory.
- **NMDA receptors** open only when the cell is already depolarised *and*
  glutamate is present. That makes them a molecular coincidence detector, the
  basis of Hebbian learning ([[learning-and-plasticity]]).
- **Electrical synapses** (gap junctions) couple cells directly and synchronise them.
- A cortical pyramidal neuron receives on the order of **10,000** synapses.

### Dendrites compute
Dendrites are not passive wires. Active dendritic branches produce local NMDA and
Ca2+ spikes, so one pyramidal neuron behaves like a **two-layer network**.
Beniaguev et al. (2021) needed a 5-to-8-layer deep network to mimic one
cortical neuron's input-output behaviour at millisecond precision.

### Neuron types (cortex)
- **Pyramidal cells**: excitatory, long-range projections. Their apical dendrite
  reaches layer 1, where top-down feedback arrives.
- **Interneurons**: inhibitory, local. Main types are PV (fast, controls timing
  and gain), SST (gates dendritic input) and VIP (inhibits other interneurons,
  i.e. disinhibition).

### Glia
- **Astrocytes**: regulate synapses and blood flow, recycle transmitter; may take
  part in plasticity.
- **Oligodendrocytes**: make myelin. Myelination itself changes with learning.
- **Microglia**: immune cells that prune synapses during development.

## Biological vs artificial neuron
| Feature | Biological | Artificial (ANN) |
|---|---|---|
| Signal | Discrete spikes in time | Continuous real numbers |
| Computation | Nonlinear dendrites, ion-channel dynamics | Weighted sum then activation |
| Time | Intrinsic, with ms dynamics | None (except RNNs) |
| Sign | Fixed per neuron (Dale's principle) | Any weight can be + or - |
| Reliability | Noisy, probabilistic release | Deterministic |
| Learning | Local rules plus neuromodulators | Global backprop |
| Energy | Spends energy mainly when it spikes | Every unit computes every step |

## Relevance to building brain-like AI
- Spikes plus sparse activity make computation event-driven, which is where
  neuromorphic energy savings come from. See [[spiking-neural-networks]].
- Dendritic compartments give a natural place to separate feedforward evidence
  (basal dendrites) from top-down predictions (apical dendrites). Several
  biologically plausible backprop schemes rely on this ([[brain-vs-deep-learning]]).
- Dale's principle and noisy synapses are often dropped in models. Whether they
  matter for learning is an open question.

## Related
- [[brain-structure-overview]] - where these cells sit.
- [[learning-and-plasticity]] - how synapses change.
- [[spiking-neural-networks]] - simulating neurons in code.
- [[dendritic-computation]] - NMDA spikes and the neuron as a two-layer network.

## References
- Hodgkin & Huxley (1952), *J Physiol* 117:500-544. doi:10.1113/jphysiol.1952.sp004764
- Beniaguev, Segev & London (2021) "Single cortical neurons as deep artificial neural networks", *Neuron*. doi:10.1016/j.neuron.2021.07.002
- Kandel et al., *Principles of Neural Science* (6th ed.).
