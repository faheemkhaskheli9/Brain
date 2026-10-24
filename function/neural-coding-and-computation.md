---
title: Neural coding and computation
category: function
tags: [neural-code, rate-code, spike-timing, population-code, sparse-coding, oscillations, energy-efficiency, attractor]
use_cases:
  - how does the brain represent information with spikes
  - why is the brain so energy efficient compared to GPUs
  - what computational primitives does the brain use
status: stable
last_verified: 2026-10-24
sources:
  - https://doi.org/10.1038/381607a0
  - https://doi.org/10.1073/pnas.79.8.2554
  - https://doi.org/10.1016/S0960-9822(03)00135-0
  - https://doi.org/10.1038/s41586-020-03171-x
---

# Neural coding and computation

## Summary
Neurons communicate with spikes, so information has to live in **which** neurons
fire, **how often**, and **when**. The brain combines several codes at once:
firing rates, precise spike timing, and patterns across large populations. It
keeps activity **sparse**: perhaps 1% or fewer of cortical neurons are strongly
active at any moment (Lennie 2003). That sparsity is a large part of why it runs on ~20 W.

## How it works

### Codes
| Code | Idea | Evidence / example |
|---|---|---|
| **Rate code** | Information is in spikes per second | Muscle force; classic V1 tuning curves |
| **Temporal code** | Information is in exact spike times or first-spike latency | Auditory localisation (µs precision); fast visual recognition (one spike per neuron per stage) |
| **Population code** | A stimulus is a pattern across many broadly tuned neurons, decoded by a weighted vote | Motor-cortex reaching direction (population vector) |
| **Sparse code** | Few active neurons per stimulus, each fairly selective | Olshausen & Field (1996): sparse coding of natural images gives V1-like edge filters |
| **Phase code** | Spike timing relative to an ongoing oscillation | Hippocampal place cells fire at earlier theta phases as an animal moves through a field (phase precession) |

### Timing versus count across mouse visual areas (#86, measured here)
`research/spike_timing_areas.py` decodes which stimulus was shown from 20 simultaneously
recorded units per area in the 32 `brain_observatory_1.1` sessions of the Allen Visual
Coding Neuropixels dataset (Siegle et al. 2021): 118 natural scenes and 40 drifting-grating
classes (8 directions x 5 temporal frequencies), 0-250 ms after onset. Codes: spike
**count** per unit, counts in **10 ms** and **5 ms bins**, and first-spike **latency**.
Decoder: shrinkage LDA, 5-fold cross-validation, 5 random draws of 20 units per session;
95% CIs from 10,000 session bootstraps. Method and prediction were written in the script
before the real-data run; a synthetic check (latency-only vs rate-only areas) passes.

Timing gain = accuracy(10 ms bins) - accuracy(count), in percentage points:

| Area | Sessions | Scenes: count acc. | Scenes: gain [95% CI] | Gratings: count acc. | Gratings: gain [95% CI] |
|---|---|---|---|---|---|
| LGN | 16 | 15.3% | -1.1 [-1.8, -0.4] | 17.6% | **+19.3 [+13.6, +24.6]** |
| V1 | 30 | 20.1% | -3.4 [-4.3, -2.6] | 16.4% | -0.9 [-1.6, -0.2] |
| LM | 23 | 14.7% | -3.0 [-3.8, -2.3] | 15.2% | -2.4 [-3.3, -1.4] |
| RL | 26 | 9.4% | -1.8 [-2.1, -1.5] | 12.3% | -1.5 [-2.0, -0.9] |
| AL | 23 | 12.8% | -2.0 [-2.7, -1.4] | 14.1% | -2.6 [-3.0, -2.1] |
| PM | 19 | 13.3% | -2.9 [-3.5, -2.3] | 12.5% | -2.9 [-3.5, -2.3] |
| AM | 26 | 11.1% | -2.3 [-2.7, -1.9] | 11.3% | -2.2 [-2.7, -1.6] |

Chance: 0.8% (scenes), 2.5% (gratings). Per-session accuracies:
`research/data/allen_vcn_timing_2026-10-24.csv`.

- **Measured:** only LGN with drifting gratings gains from 10 ms timing, by a large margin
  (count 17.6% to bins 36.9%); 5 ms bins also gain there (+13.2). This fits LGN responses
  locking to the grating's temporal frequency, which a count cannot see.
- **Measured:** in every cortical area, and in LGN for natural scenes, the binned code
  decodes slightly *worse* than the count. First-spike latency alone is far worse than the
  count everywhere, and adding it to the count changes almost nothing (within 1 point).
- **Prediction partly failed:** timing helped in LGN but not in V1. The gain declines with
  hierarchy for gratings (Spearman rho -0.71, driven by LGN) but not for scenes (-0.07).
- **Limits:** this measures what a linear decoder learns from about 50 (scenes) or 15
  (gratings) repeats per class, not total information. Binned codes have 25-50 times more
  features than the count, so a negative gain means "not usable by this decoder", not
  "absent". No multiple-comparison correction; LP (extra area) is in the CSV, gain about 0.
  Numbers reported in the #86 issue comments from code never pushed (#128) are not these.

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
- **Oscillations.** Theta (4-8 Hz), gamma (30-100 Hz) and sleep spindles are
  established; that they coordinate *when* groups of neurons communicate and
  learn is a hypothesis (see Open questions).

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
- How much information is carried by spike timing versus rate, in each area. For a
  linear decoder on mouse visual areas, only LGN with gratings gains from 10 ms timing
  (measured above, #86); whether a non-linear decoder or more trials finds timing
  information in cortex stays open.
- Whether oscillations are causal for computation or a side effect of E-I circuits.

## Related
- [[neurons-and-synapses]] - where spikes come from.
- [[predictive-processing]] - a theory of what cortical computation is *for*.
- [[spiking-neural-networks]] - simulate these codes.
- [[efficient-brain-like-learning]] - put sparse, event-driven updates into a learner, with measurements.
- [[brain-rhythms-and-oscillations]] - spike timing against theta and gamma rhythms.
- [[dendritic-computation]] - single neurons compute more than a weighted sum.
- [[hyperdimensional-computing]] - distributed codes put to work as symbols: binding roles to fillers.
- [Brain World](../game/world/) - a 3D creature whose tone-hearing neurons use gain modulation: sound scales their visual drive.

## References
- Olshausen & Field (1996) "Emergence of simple-cell receptive field properties by learning a sparse code for natural images", *Nature* 381:607. doi:10.1038/381607a0
- Hopfield (1982) "Neural networks and physical systems with emergent collective computational abilities", *PNAS* 79:2554. doi:10.1073/pnas.79.8.2554
- Lennie (2003) "The cost of cortical computation", *Current Biology* 13:493. doi:10.1016/S0960-9822(03)00135-0
- Carandini & Heeger (2012) "Normalization as a canonical neural computation", *Nat Rev Neurosci* 13:51.
- Siegle et al. (2021) "Survey of spiking in the mouse visual system reveals functional hierarchy", *Nature* 592:86. doi:10.1038/s41586-020-03171-x
- Dayan & Abbott, *Theoretical Neuroscience* (MIT Press, 2001), chapters 1-4.
