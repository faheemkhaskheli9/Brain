---
title: Levels of brain modeling
category: simulation
tags: [marr, hodgkin-huxley, lif, izhikevich, rate-model, compartmental, whole-brain-emulation, scale, compute]
use_cases:
  - at what level of detail should I simulate the brain
  - how much compute would a whole-brain simulation need
  - difference between Hodgkin-Huxley, LIF and rate neuron models
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1109/TNN.2003.820440
  - https://www.fhi.ox.ac.uk/brain-emulation-roadmap-report.pdf
  - https://doi.org/10.1113/jphysiol.1952.sp004764
---

# Levels of brain modeling

## Summary
"Simulating the brain" can mean anything from modelling individual ion channels
to training a deep network that only reproduces behaviour. The right level depends
on the goal. If you want a computer that **learns like a brain**, the useful level
is usually **algorithmic**: spiking or rate neurons with brain-like learning rules
and architecture. Molecular realism costs orders of magnitude more compute and is
not needed for that goal.

## How it works

### Marr's three levels (1982)
1. **Computational**: what problem is solved, and why (e.g. "infer the 3D scene
   from 2D images").
2. **Algorithmic / representational**: what representations and algorithm are used
   (e.g. predictive coding, sparse codes).
3. **Implementational**: how neurons and synapses physically do it.
Brain-inspired AI mostly borrows from levels 1-2. Neuroscience simulations focus on level 3.

### The ladder of detail
| Level | Model | What it captures | Cost per neuron | Used for |
|---|---|---|---|---|
| Molecular | Reaction-diffusion of ions, proteins | Synaptic biochemistry | Enormous | Drug and plasticity mechanisms |
| Multi-compartment | Hodgkin-Huxley channels on a reconstructed dendrite tree (100s-1000s of compartments) | Dendritic computation, exact spike shape | Very high | Blue Brain cortical microcircuit; NEURON simulator |
| Point HH neuron | 4 ODEs (V, m, h, n) | Real spike mechanism | High | Single-cell studies |
| **Izhikevich** | 2 ODEs + reset | 20+ firing patterns (bursting, chattering) at low cost | Low | Large realistic networks |
| **LIF / AdEx** | 1-2 ODEs + threshold reset | Integration, spikes, timing | Very low | Most large SNNs, neuromorphic chips |
| Rate model | Continuous firing rate, e.g. `τ dr/dt = −r + f(Wr + I)` | Average activity | Minimal | Systems-level models |
| ANN unit | `y = f(Wx)` with no time | Static input-output mapping | Minimal, GPU-friendly | Deep learning |
| Whole-brain / mean-field | One "neural mass" per brain region | Large-scale dynamics (EEG, fMRI) | Per region | The Virtual Brain, clinical modelling |

### The equations
- **Hodgkin-Huxley**: `C dV/dt = −g_Na m³h (V−E_Na) − g_K n⁴ (V−E_K) − g_L (V−E_L) + I`,
  with gating variables `m, h, n` following first-order kinetics.
- **Leaky integrate-and-fire (LIF)**: `τ_m dV/dt = −(V − V_rest) + R·I`; when
  `V ≥ V_th`, emit a spike and reset `V ← V_reset`.
- **Izhikevich (2003)**: `v' = 0.04v² + 5v + 140 − u + I`, `u' = a(bv − u)`; when
  `v ≥ 30 mV`: `v ← c`, `u ← u + d`. Four parameters `(a, b, c, d)` select the cell type.

Runnable LIF and Izhikevich code: [[spiking-neural-networks]].

### Scale and compute for a whole human brain
Rough orders of magnitude (Sandberg & Bostrom 2008 give the detailed analysis):
- ~86e9 neurons × ~10^4 synapses each ≈ ~10^15 synapses.
- Point-neuron simulation with ~1 ms steps and synaptic events at a ~1-10 Hz mean
  rate needs roughly 10^15-10^16 synaptic updates per second, before learning.
- Synapse state alone: 10^15 synapses × a few bytes ≈ petabytes of memory.
- Compartmental or molecular detail adds many orders of magnitude more.
- **The binding constraint is not compute but data.** We do not have the human
  connectome, the per-synapse parameters, or the full set of learning rules.
  The largest complete connectome is the adult fruit fly
  ([[whole-brain-emulation-projects]]).

## Relevance to building brain-like AI
- Pick the **lowest-cost level that still has the property you care about**.
  Want energy efficiency and timing → LIF spiking. Want learning principles →
  rate or ANN units with local rules. Want behaviour → standard deep learning.
- A connectome-constrained model can predict function even with simple neurons:
  a LIF model of the whole fly brain predicted feeding and grooming circuits
  (Shiu et al. 2024). Wiring carries much of the computation.

## Open questions
- Which biological details are *necessary* for intelligence and which are
  implementation noise (dendrites? glia? spike timing? neuromodulator diffusion?).
- Whether a human whole-brain emulation is feasible at all without molecular-scale
  data on every synapse.

## Related
- [[neurons-and-synapses]] - the biology behind HH.
- [[spiking-neural-networks]] - code for LIF and Izhikevich and the simulators.
- [[whole-brain-emulation-projects]] - who is simulating what.
- [[neuromorphic-hardware]] - chips built for the LIF level.

## References
- Marr (1982) *Vision*. W.H. Freeman.
- Hodgkin & Huxley (1952), *J Physiol* 117:500. doi:10.1113/jphysiol.1952.sp004764
- Izhikevich (2003) "Simple model of spiking neurons", *IEEE Trans Neural Networks* 14:1569. doi:10.1109/TNN.2003.820440
- Sandberg & Bostrom (2008) "Whole Brain Emulation: A Roadmap", Future of Humanity Institute, Technical Report #2008-3.
- Gerstner, Kistler, Naud & Paninski (2014) *Neuronal Dynamics*. Cambridge University Press. Free online: https://neuronaldynamics.epfl.ch/
- Shiu et al. (2024) "A Drosophila computational brain model reveals sensorimotor processing", *Nature* 634:210.
