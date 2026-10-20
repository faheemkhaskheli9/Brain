---
title: Neurons, synapses and glia
category: anatomy
tags: [neuron, synapse, action-potential, dendrite, axon, neurotransmitter, glia, spike]
use_cases:
  - how does a single neuron work
  - what is an action potential and how is it modeled
  - how is a biological neuron different from an artificial neuron
status: stable
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1113/jphysiol.1952.sp004764
  - https://doi.org/10.1016/j.neuron.2021.07.002
  - https://doi.org/10.7554/eLife.10778
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
   briefly undershooting rest (the afterhyperpolarisation). Until the Na+ channels
   recover, the cell cannot fire again or needs a stronger input (the refractory
   period), which caps firing at a few hundred Hz.
4. The spike regenerates along the axon. Myelin (made by glia) makes it jump
   between nodes, at up to ~100 m/s.

Hodgkin and Huxley (1952) captured this in four differential equations, which
is still the gold-standard biophysical neuron model ([[levels-of-brain-modeling]]).
The four variables are the voltage V and three gates: m (Na+ activation), h (Na+
inactivation) and n (K+ activation). The squid axon they modelled rests near -65 mV,
a little above the -70 mV typical of mammalian neurons.

```python
import numpy as np

# Hodgkin-Huxley (1952) squid axon, modern sign convention, rest near -65 mV.
# Units: mV, ms, uA/cm^2, mS/cm^2, uF/cm^2. Constants as in Dayan & Abbott (2001), ch. 5.
C, gNa, gK, gL = 1.0, 120.0, 36.0, 0.3
ENa, EK, EL = 50.0, -77.0, -54.4

def rates(V):
    an = 0.01 * (V + 55) / (1 - np.exp(-(V + 55) / 10)); bn = 0.125 * np.exp(-(V + 65) / 80)
    am = 0.1 * (V + 40) / (1 - np.exp(-(V + 40) / 10));  bm = 4.0 * np.exp(-(V + 65) / 18)
    ah = 0.07 * np.exp(-(V + 65) / 20);                   bh = 1 / (1 + np.exp(-(V + 35) / 10))
    return an, bn, am, bm, ah, bh

def run(I, T=100.0, dt=0.01):
    V = -65.0
    an, bn, am, bm, ah, bh = rates(V)
    n, m, h = an / (an + bn), am / (am + bm), ah / (ah + bh)   # start at rest
    trace = np.empty(int(T / dt))
    for k in range(trace.size):
        an, bn, am, bm, ah, bh = rates(V)
        INa, IK, IL = gNa * m**3 * h * (V - ENa), gK * n**4 * (V - EK), gL * (V - EL)
        V += dt * (I - INa - IK - IL) / C
        n += dt * (an * (1 - n) - bn * n)
        m += dt * (am * (1 - m) - bm * m)
        h += dt * (ah * (1 - h) - bh * h)
        trace[k] = V
    spikes = int(np.sum((trace[1:] >= 0) & (trace[:-1] < 0)))   # upward crossings of 0 mV
    return trace, spikes

for I in (1.0, 10.0, 20.0):
    v, s = run(I)
    print(f"I = {I:4.1f} uA/cm^2: {s:2d} spikes in 100 ms, peak {v.max():5.1f} mV, trough {v.min():5.1f} mV")

assert run(1.0)[1] == 0                      # below threshold: no spike
v, s10 = run(10.0)
assert s10 >= 5 and v.max() > 20 and v.min() < -70   # repetitive spikes, overshoot, undershoot
assert run(20.0)[1] > s10                    # more current, higher rate
```

At 10 uA/cm^2 it fires 7 spikes in 100 ms, each peaking near +40 mV and undershooting
to about -75 mV, below rest: steps 2 and 3 above, from the equations alone.

### Synapses
- **Chemical synapse.** A spike → Ca2+ influx → vesicles release transmitter →
  receptors on the next cell open → a small voltage change (a PSP).
  Release is **probabilistic**: a single synapse often fails to transmit.
- **Excitatory** synapses mostly use glutamate (AMPA and NMDA receptors).
  **Inhibitory** ones mostly use GABA. A neuron generally releases the same
  transmitters at all its outputs (Dale's principle), so it is excitatory or
  inhibitory, with rare exceptions that co-release glutamate and GABA. In cortex ~80% of neurons are excitatory and ~20% inhibitory.
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

## Open questions
- Whether the brain's "noise" is a cost or a feature. Single synapses often fail to
  transmit; one **hypothesis** is that this randomness acts like sampling or dropout and
  helps learning, but how much it matters in vivo is not settled.
- Whether Dale's principle and fixed excitatory/inhibitory identity matter for what a
  network can learn, or only constrain how it is built. Models usually drop them.
- What most cell types compute. Transcriptomic atlases split cortex into far more types
  than the classic pyramidal, PV, SST and VIP classes; the function of most is unknown.
- How much information one synapse stores. An electron-microscopy study of rat
  hippocampus estimated about 4.7 bits from how precisely paired spines match in size
  (Bartol et al. 2015); whether other synapses and regions are similar is open.

## Related
- [[brain-structure-overview]] - where these cells sit.
- [[learning-and-plasticity]] - how synapses change.
- [[spiking-neural-networks]] - simulating neurons in code.
- [[dendritic-computation]] - NMDA spikes and the neuron as a two-layer network.

## References
- Hodgkin & Huxley (1952), *J Physiol* 117:500-544. doi:10.1113/jphysiol.1952.sp004764
- Beniaguev, Segev & London (2021) "Single cortical neurons as deep artificial neural networks", *Neuron*. doi:10.1016/j.neuron.2021.07.002
- Kandel et al., *Principles of Neural Science* (6th ed.).
- Dayan & Abbott, *Theoretical Neuroscience* (MIT Press, 2001), chapter 5: the Hodgkin-Huxley constants used in the code.
- Bartol et al. (2015) "Nanoconnectomic upper bound on the variability of synaptic plasticity", *eLife* 4:e10778. doi:10.7554/eLife.10778
