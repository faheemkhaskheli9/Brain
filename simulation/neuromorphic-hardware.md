---
title: Neuromorphic hardware
category: simulation
tags: [neuromorphic, loihi, hala-point, spinnaker, truenorth, brainscales, northpole, in-memory-computing, memristor, energy]
use_cases:
  - which chips run spiking neural networks efficiently
  - can hardware match the brain's energy efficiency
  - deploy a brain-like model on neuromorphic hardware
status: draft
last_verified: 2026-10-11
sources:
  - https://newsroom.intel.com/artificial-intelligence/intel-builds-worlds-largest-neuromorphic-system-to
  - https://doi.org/10.1126/science.1254642
  - https://doi.org/10.1109/JPROC.2014.2304638
---

# Neuromorphic hardware

## Summary
Neuromorphic chips copy the brain's physical organisation, not just its
algorithms. Memory sits next to compute, neurons communicate with asynchronous
spike events, and nothing runs when nothing spikes. That attacks the von Neumann
bottleneck (moving weights between memory and processor), which costs GPUs most
of their energy. They are research platforms today, strongest on sparse,
event-driven, low-power workloads, not general-purpose replacements for GPUs.

## How it works

### Design principles
- **Event-driven (asynchronous)**: compute only when a spike arrives.
- **Co-located memory and compute**: synaptic weights live in local SRAM or
  analog devices beside each neuron core.
- **Massive parallelism, low precision**: many small cores, few-bit weights.
- **On-chip learning**: some chips implement local plasticity rules (STDP,
  three-factor) in hardware.

### Major systems
| System | Who | Approach | Notable facts |
|---|---|---|---|
| **Loihi 2 / Hala Point** | Intel | Digital, asynchronous, programmable neuron models, on-chip learning | Hala Point (2024): 1,152 Loihi 2 chips, up to 1.15 billion neurons and 128 billion synapses, max 2,600 W; deployed at Sandia National Labs (Intel's own figures) |
| **SpiNNaker / SpiNNaker2** | Univ. of Manchester; TU Dresden | Many ARM cores exchanging spike packets | Designed for real-time brain simulation; the original machine has about a million ARM cores |
| **TrueNorth** | IBM (2014) | Digital, fixed LIF neurons, no on-chip learning | 1 million neurons, 256 million synapses per chip, ~70 mW (Merolla et al. 2014) |
| **NorthPole** | IBM (2023) | Not spiking; near-memory digital inference | Brain-*inspired* memory/compute co-location for standard ANNs |
| **BrainScaleS** | Heidelberg | Analog circuits on wafer-scale silicon | Runs physics-based neuron models much faster than biological real time |
| **DYNAP-SE / Speck** | SynSense / INI Zürich | Mixed-signal, ultra-low-power | Edge sensing with event cameras |
| **Memristor / in-memory crossbars** | Many labs | Analog resistive devices store weights and do multiply-accumulate in place | Promising density; device variability is the hard problem |

### Event-based sensors
Event cameras (dynamic vision sensors) and silicon cochleas output spikes when
something changes, like the retina. Paired with neuromorphic chips they give very
low latency and power for robotics and edge vision.

## Relevance to building brain-like AI
- To get the brain's **energy** advantage, you need sparse spiking algorithms
  *and* this kind of hardware. Neither alone is enough.
- On-chip local learning (STDP, three-factor rules) enables **continual,
  on-device learning** with no backward pass, the most brain-like operating mode.
- Practical path: prototype in snnTorch or Brian2, then port to Lava (for Loihi)
  or the vendor SDK. See [[spiking-neural-networks]].

## Gotchas
- Vendor efficiency figures are usually measured on workloads chosen to suit the
  chip. Compare against an optimised GPU or edge-NPU baseline on *your* task.
- Tooling is immature next to PyTorch/CUDA, and access to many systems is through
  research programs (e.g. Intel's Neuromorphic Research Community).
- Product and access details change quickly. Check vendor pages before deciding.

## Related
- [[neural-coding-and-computation]] - why sparse events save energy.
- [[spiking-neural-networks]] - the models these chips run.
- [[whole-brain-emulation-projects]] - large-scale simulations that use them.

## References
- Intel (2024) "Intel Builds World's Largest Neuromorphic System to Enable More Sustainable AI", Intel Newsroom.
- Merolla et al. (2014) "A million spiking-neuron integrated circuit with a scalable communication network and interface", *Science* 345:668. doi:10.1126/science.1254642
- Furber et al. (2014) "The SpiNNaker Project", *Proc IEEE* 102:652. doi:10.1109/JPROC.2014.2304638
- Davies et al. (2018) "Loihi: A Neuromorphic Manycore Processor with On-Chip Learning", *IEEE Micro* 38:82.
- Schuman et al. (2022) "Opportunities for neuromorphic computing algorithms and applications", *Nature Computational Science* 2:10.
