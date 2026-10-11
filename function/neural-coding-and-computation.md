---
title: Neural coding and computation
category: function
tags: [neural-code, rate-code, spike-timing, population-code, sparse-coding, oscillations, energy-efficiency, attractor]
use_cases:
  - how does the brain represent information with spikes
  - why is the brain so energy efficient compared to GPUs
  - what computational primitives does the brain use
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1038/381607a0
  - https://doi.org/10.1073/pnas.79.8.2554
  - https://doi.org/10.1016/S0960-9822(03)00135-0
---

# Neural coding and computation

## Summary
Neurons communicate with spikes, so information has to live in **which** neurons
fire, **how often**, and **when**. The brain combines several codes at once:
firing rates, precise spike timing, and patterns across large populations. It
keeps activity **sparse**: only a few percent of cortical neurons are strongly
active at any moment. That sparsity is a large part of why it runs on ~20 W.

## How it works

### Codes
| Code | Idea | Evidence / example |
|---|---|---|
| **Rate code** | Information is in spikes per second | Muscle force; classic V1 tuning curves |
| **Temporal code** | Information is in exact spike times or first-spike latency | Auditory localisation (µs precision); fast visual recognition (one spike per neuron per stage) |
| **Population code** | A stimulus is a pattern across many broadly tuned neurons, decoded by a weighted vote | Motor-cortex reaching direction (population vector) |
| **Sparse code** | Few active neurons per stimulus, each fairly selective | Olshausen & Field (1996): sparse coding of natural images gives V1-like edge filters |
| **Phase code** | Spike timing relative to an ongoing oscillation | Hippocampal place cells fire at earlier theta phases as an animal moves through a field (phase precession) |

### Computational primitives (established)
- **Receptive fields and tuning.** Each neuron responds to a region and feature,
  e.g. an oriented edge (Hubel & Wiesel). This inspired CNNs.
- **Divisive normalisation.** A response is divided by pooled activity of
  neighbours (Carandini & Heeger). It acts like a softmax or layer norm and
  appears across many brain areas.
- **Excitation-inhibition balance.** Large excitatory and inhibitory inputs cancel,
  leaving the neuron near threshold, fast to respond and noisy.
- **Winner-take-all** through lateral inhibition.
- **Attractor dynamics.** Recurrent networks settle into stable states, used for
  memory and decisions. Hopfield (1982) is the classic model: see the
  Hopfield code in [[memory-systems]].
- **Gain modulation.** Attention and neuromodulators multiply responses, a
  biological "attention" mechanism.
- **Oscillations.** Theta (4-8 Hz), gamma (30-100 Hz) and sleep spindles
  coordinate *when* groups of neurons communicate and when they learn.

### Why it is energy-efficient
- **Sparse, event-driven activity.** Spikes are energetically expensive, so the
  brain uses few of them (Lennie 2003 estimated only ~1% of cortical neurons can
  be substantially active at once on the brain's energy budget).
- **Memory and compute in the same place.** Synapses store weights *and* do the
  multiply. GPUs spend most of their energy moving weights between memory and
  compute (the von Neumann bottleneck).
- **Analog, low-precision, noisy components**, slow (ms) but massively parallel.

## Relevance to building brain-like AI
- Sparse coding and normalisation are cheap, proven tricks: k-WTA layers, layer
  norm, mixture-of-experts routing (only a few experts active per token) all echo them.
- Spiking networks plus neuromorphic chips try to capture the energy advantage:
  [[spiking-neural-networks]], [[neuromorphic-hardware]].
- Temporal and phase codes are mostly unused in mainstream deep learning, which is
  an open research direction.

## Open questions
- How much information is carried by spike timing versus rate, in each area.
- Whether oscillations are causal for computation or a side effect of E-I circuits.

## Related
- [[neurons-and-synapses]] - where spikes come from.
- [[predictive-processing]] - a theory of what cortical computation is *for*.
- [[spiking-neural-networks]] - simulate these codes.

## References
- Olshausen & Field (1996) "Emergence of simple-cell receptive field properties by learning a sparse code for natural images", *Nature* 381:607. doi:10.1038/381607a0
- Hopfield (1982) "Neural networks and physical systems with emergent collective computational abilities", *PNAS* 79:2554. doi:10.1073/pnas.79.8.2554
- Lennie (2003) "The cost of cortical computation", *Current Biology* 13:493. doi:10.1016/S0960-9822(03)00135-0
- Carandini & Heeger (2012) "Normalization as a canonical neural computation", *Nat Rev Neurosci* 13:51.
- Dayan & Abbott, *Theoretical Neuroscience* (MIT Press, 2001), chapters 1-4.
