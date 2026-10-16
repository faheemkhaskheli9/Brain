---
title: Neural coding and computation
category: function
tags: [neural-code, rate-code, spike-timing, population-code, sparse-coding, oscillations, energy-efficiency, attractor, decoding, allen-neuropixels]
use_cases:
  - how does the brain represent information with spikes
  - why is the brain so energy efficient compared to GPUs
  - what computational primitives does the brain use
  - does spike timing carry information beyond spike counts in mouse visual areas
status: stable
last_verified: 2026-10-16
sources:
  - https://doi.org/10.1038/381607a0
  - https://doi.org/10.1073/pnas.79.8.2554
  - https://doi.org/10.1016/S0960-9822(03)00135-0
  - https://doi.org/10.1038/s41586-020-03171-x
  - https://doi.org/10.1016/S0896-6273(01)00251-3
---

# Neural coding and computation

## Summary
Neurons communicate with spikes, so information has to live in **which** neurons
fire, **how often**, and **when**. The brain combines several codes at once:
firing rates, precise spike timing, and patterns across large populations. It
keeps activity **sparse**: perhaps 1% or fewer of cortical neurons are strongly
active at any moment (Lennie 2003). That sparsity is a large part of why it runs on ~20 W.
Measured here on open mouse data: in every visual area spike timing finer than 50 ms carries some
stimulus information, but with 20 neurons a linear decoder gains most from 50 ms bins;
millisecond bins beat the plain count only in LGN (firmly for gratings, weakly for scenes), and
first-spike latency never helps (table below).

## How it works

### Codes
| Code | Idea | Evidence / example |
|---|---|---|
| **Rate code** | Information is in spikes per second | Muscle force; classic V1 tuning curves |
| **Temporal code** | Information is in exact spike times or first-spike latency | Auditory localisation (µs precision); fast visual recognition (one spike per neuron per stage) |
| **Population code** | A stimulus is a pattern across many broadly tuned neurons, decoded by a weighted vote | Motor-cortex reaching direction (population vector) |
| **Sparse code** | Few active neurons per stimulus, each fairly selective | Olshausen & Field (1996): sparse coding of natural images gives V1-like edge filters |
| **Phase code** | Spike timing relative to an ongoing oscillation | Hippocampal place cells fire at earlier theta phases as an animal moves through a field (phase precession) |

How much timing adds is measured case by case (established). In rat barrel cortex, precise
spike timing raised the information about whisker location by 44% over the spike count alone,
mostly through the first spike (Panzeri et al. 2001). In cat LGN many spikes are timed to better
than 1 ms, and temporal patterns added between -9.4% and +24.9% of the information in the
response (Reinagel & Reid 2000). Retinal ganglion cells encode a flashed image in the relative
latencies of their first spikes (Gollisch & Meister 2008). The useful time scale depends on how
fast the stimulus changes (Butts et al. 2007), and one response can carry different features at
different time scales (Panzeri et al. 2010).

### Timing versus count across mouse visual areas (measured here, issue #86)
**Step 0, literature (checked 2026-10-16).** No published per-area table of timing gain over
counts on the Allen Visual Coding Neuropixels data was found, so this is a new analysis, not a
replication. Closest: Sotomayor-Gómez, Battaglia & Vinck (2023, bioRxiv preprint, not peer
reviewed) compared population spike-count vectors with relative spike-timing sequences
(SpikeShip) in six visual areas during natural movies; the sequences carried substantially more
information, especially for large populations. That work used movies, timing between neurons
rather than time after stimulus onset, and (as far as its abstract shows) no matched unit counts
or LGN. Siegle et al. (2021) showed that response latency, receptive-field size, phase-locking
to drifting gratings and response decay time scale all rise with the anatomical hierarchy, but
did not compare timing and count codes for stimulus identity.

**Method (pre-registered before the full run; the `--quick` smoke run only checked the pipeline).**
- Data: Allen Brain Observatory Visual Coding Neuropixels (Siegle et al. 2021), the 10
  `brain_observatory_1.1` sessions with the most of the 7 areas below holding at least 20 units.
  Units must be labelled `good` and pass the Siegle et al. (2021) filters: ISI violations < 0.5,
  amplitude cutoff < 0.1, presence ratio > 0.95. Area = the structure of the unit's peak channel.
- Areas: LGN (LGd), V1 (VISp), LM (VISl), RL (VISrl), AL (VISal), PM (VISpm), AM (VISam).
- Stimuli: 118 natural scenes (250 ms each, no gap, about 50 repeats; blank frames dropped) and
  drifting gratings (8 directions x 5 temporal frequencies = 40 classes, 15 repeats; blanks dropped).
- Window: 0-250 ms after onset, for both stimulus sets.
- Codes of the same spikes: (a) count in the window; counts in 50 ms bins (coarse time course);
  (b) counts in 10 ms bins (primary) and 5 ms bins; (c) first-spike latency (250 ms if no spike);
  and count plus latency together.
- Decoder: the same for every code, shrinkage LDA (scikit-learn `LinearDiscriminantAnalysis`,
  `lsqr` solver, Ledoit-Wolf shrinkage set by the data, so no hand-tuned penalty favours one
  code), 5-fold stratified cross-validation.
- Matched units: in each session and area, 20 units drawn at random (areas with fewer are skipped
  for that session), 5 draws, accuracies averaged over draws.
- Timing gain = accuracy(code) - accuracy(count), per session. Report the mean over sessions and a
  95% CI from 10,000 bootstrap resamples of sessions. A gain whose CI excludes 0 counts as real.
- Planned reading: if the 10 ms gain is positive but no larger than the 50 ms gain, the extra
  information is the slow time course of the response (onset versus sustained), not millisecond
  timing. Natural scenes follow each other with no gap, so early bins also hold the tail of the
  previous image's response; the 50 ms code controls for that.
- Pipeline check (not a hypothesis test): the population PSTH half-rise time per area should put
  LGN and V1 first, as in Siegle et al. (2021).
- Added after the smoke run, **not pre-registered**: in the smoke run (1 session, 8 units) the
  10 and 5 ms codes often scored *below* the count, which mixes two things: timing information and
  the cost of fitting 25-50 times more weights from the same trials. So one more code, `jit50`,
  moves every spike to a random time inside its own 50 ms bin and then counts 10 ms bins. It has
  the dimension of the 10 ms code and the same 50 ms counts, but no timing finer than 50 ms.
  Fine timing = accuracy(10 ms) - accuracy(`jit50`), at equal dimension.
- Added after review, **not pre-registered**: a correction for multiple comparisons. The primary
  family is the 10 ms gain in 7 areas x 2 stimulus sets = 14 contrasts. Each gets a Bonferroni
  percentile CI at alpha = 0.05/14, from the same 10,000 session resamples as its uncorrected CI.
  Bonferroni was chosen over a max-statistic bootstrap because it holds under any dependence
  between the 14 contrasts (they share sessions and mice) and needs no joint-resampling or
  studentising model; the price is that it is conservative. A primary gain counts as real only if
  its corrected CI excludes 0. All other gains (50 and 5 ms bins, latency, count plus latency,
  fine timing) are exploratory and uncorrected.

**Results (measured here, 2026-10-16).** 10 sessions, 20 units per area, 5 draws, run with
`python research/timing_vs_count.py --jobs 10`. Count = decoding accuracy (%) from spike counts.
Every other column is a gain over the count in percentage points, with an **uncorrected** 95%
bootstrap CI over sessions. The column "10 ms, family-wise CI" is the Bonferroni-corrected CI of
the primary gain. Chance is 0.85% for scenes and 2.5% for gratings. Runtime: the first run streams about
1.4 GB in total (10-30 minutes per session on the shared link used here); the analysis took
6,596 s with 10 parallel jobs on a busy 20-core machine; a rerun from the cache prints the tables
in seconds. `--quick` (one session, 8 units, 1 draw) took 67 s on cached data.

Natural scenes (118 classes):

| Area | Sessions | Count | 50 ms bins | 10 ms bins (primary) | 10 ms, family-wise CI | 5 ms bins | Latency | Count + latency | Fine timing (10 ms - `jit50`) |
|---|---|---|---|---|---|---|---|---|---|
| LGN | 8 | 13.0 | +5.4 [3.3, 7.4] | +2.2 [0.7, 3.7] | [0.1, 4.4] | -2.0 [-2.7, -1.3] | -10.2 [-15.3, -5.9] | -0.6 [-1.1, -0.1] | +3.3 [2.0, 4.7] |
| V1 | 10 | 16.8 | +5.1 [3.6, 6.8] | -4.0 [-4.9, -3.2] | [-5.3, -2.7] | -9.0 [-10.3, -7.6] | -12.6 [-15.0, -10.4] | -0.3 [-0.6, -0.1] | +2.8 [2.1, 3.5] |
| LM | 8 | 17.4 | +4.8 [3.4, 6.3] | -4.6 [-5.7, -3.6] | [-6.1, -3.2] | -9.6 [-12.0, -7.0] | -13.8 [-18.0, -9.5] | -0.7 [-1.0, -0.4] | +3.1 [1.8, 4.6] |
| RL | 9 | 7.4 | +2.8 [1.9, 3.8] | -1.6 [-2.2, -1.1] | [-2.5, -0.9] | -4.0 [-5.0, -2.9] | -5.2 [-6.5, -3.8] | -0.4 [-0.6, -0.3] | +1.4 [1.0, 1.9] |
| AL | 8 | 13.7 | +5.0 [3.4, 6.7] | -2.2 [-3.2, -1.3] | [-3.6, -0.8] | -6.6 [-8.4, -5.1] | -10.5 [-13.7, -7.8] | -0.5 [-0.9, -0.2] | +2.9 [2.0, 3.9] |
| PM | 7 | 11.3 | +3.7 [2.2, 5.2] | -3.7 [-5.8, -2.0] | [-7.0, -1.6] | -7.0 [-10.7, -4.1] | -8.8 [-13.0, -5.2] | -0.7 [-1.1, -0.4] | +1.9 [1.2, 2.6] |
| AM | 10 | 10.0 | +3.5 [2.6, 4.6] | -2.9 [-3.4, -2.5] | [-3.7, -2.3] | -5.8 [-7.2, -4.6] | -7.7 [-9.9, -5.8] | -0.5 [-0.7, -0.3] | +1.5 [1.1, 1.9] |

Drifting gratings (40 classes):

| Area | Sessions | Count | 50 ms bins | 10 ms bins (primary) | 10 ms, family-wise CI | 5 ms bins | Latency | Count + latency | Fine timing (10 ms - `jit50`) |
|---|---|---|---|---|---|---|---|---|---|
| LGN | 8 | 16.0 | +17.6 [11.3, 23.8] | +13.9 [8.4, 19.2] | [5.9, 21.5] | +7.5 [3.3, 11.6] | -11.2 [-16.4, -7.0] | -1.4 [-2.5, -0.3] | +11.5 [7.8, 14.7] |
| V1 | 10 | 16.8 | +4.7 [2.9, 6.9] | -0.1 [-1.9, 1.8] | [-2.6, 2.9] | -3.9 [-5.4, -2.5] | -10.3 [-12.1, -8.7] | -0.6 [-0.9, -0.3] | +4.6 [3.4, 6.3] |
| LM | 8 | 15.7 | +3.3 [2.0, 4.6] | -1.3 [-2.5, -0.1] | [-3.0, 0.4] | -5.0 [-6.5, -3.3] | -9.6 [-12.2, -6.6] | -0.9 [-1.7, -0.3] | +3.5 [1.8, 5.2] |
| RL | 9 | 12.3 | +3.0 [2.2, 4.0] | -1.4 [-2.4, -0.2] | [-2.8, 0.4] | -3.4 [-4.7, -2.0] | -7.3 [-10.1, -5.4] | -0.8 [-1.1, -0.5] | +2.2 [1.5, 3.0] |
| AL | 8 | 16.1 | +3.4 [2.5, 4.7] | -1.9 [-2.8, -0.8] | [-3.2, -0.3] | -5.6 [-6.9, -4.3] | -10.0 [-11.5, -8.5] | -1.6 [-2.3, -1.0] | +3.1 [2.7, 3.5] |
| PM | 7 | 13.7 | +2.4 [1.6, 3.1] | -1.8 [-2.6, -1.0] | [-2.8, -0.6] | -5.0 [-6.4, -3.5] | -8.0 [-10.0, -6.1] | -1.0 [-1.7, -0.3] | +2.4 [1.9, 3.0] |
| AM | 10 | 12.3 | +2.6 [1.5, 3.6] | -1.8 [-2.8, -0.6] | [-3.2, -0.1] | -3.4 [-4.6, -2.2] | -7.5 [-9.3, -5.8] | -0.7 [-1.1, -0.3] | +1.8 [0.7, 3.1] |

What the tables say (measured here; one dataset, one decoder):
- **Pre-registered answer, with the family-wise correction.** 10 ms bins beat the count only in
  LGN. For gratings that holds firmly (+13.9 points, corrected CI [5.9, 21.5]). For scenes it holds
  only barely (+2.2, corrected CI [0.1, 4.4]): one of the 8 sessions was negative, and a t-based
  Bonferroni interval, [-1.2, 5.7], includes 0, so treat the LGN scene gain as weak. In the
  cortex, 10 ms bins were worse than the count for scenes in all six areas (-1.6 to -4.6; every
  corrected CI below 0). For gratings they were worse in AL, PM and AM (-1.8 to -1.9; corrected CIs
  below 0, AM only just), and in V1, LM and RL no difference was detected (corrected CIs include 0;
  LM and RL excluded 0 before correction).
- The rest is exploratory and uncorrected (several dozen more contrasts). 5 ms bins were worse
  than 10 ms bins everywhere, and worse than the count everywhere except LGN gratings (+7.5).
- **Latency (exploratory).** First-spike latency alone decoded far worse than the count in every
  area (-5 to -14 points), and adding it to the count never helped (-0.3 to -1.6). For a linear
  readout here, latency is a weaker copy of the count, unlike the whisker result of Panzeri et al.
  (2001).
- **The slow time course carries information (exploratory).** 50 ms bins beat the count in every area for both
  stimulus sets (cortex +2.4 to +5.1, LGN +5.4 and +17.6). The 10 ms gain was below the 50 ms gain
  in all 14 rows, so by the pre-registered reading the usable extra information is the slow time
  course of the response (onset versus sustained), not millisecond timing.
- **But finer timing is there (added control, exploratory).** At equal dimension, real 10 ms bins beat the
  jittered ones in every area: +1.4 to +4.6 points in cortex, +3.3 (scenes) and +11.5 (gratings)
  in LGN. So spikes carry stimulus information finer than 50 ms, but a linear decoder trained on
  40 (scenes) or 12 (gratings) trials per class loses more to the extra weights than it gains.
  Relative to the count accuracy, fine timing was about 25% (scenes) and 72% (gratings) in LGN,
  15-21% and 15-27% in cortex, smallest in AM for both. For gratings it falls from LGN to V1 to
  the higher areas, in line with the fall of phase-locking to drifting gratings along the
  hierarchy (Siegle et al. 2021). That the LGN grating gain is mostly phase-locking to the
  grating's temporal frequency is a likely reading, not tested here.
- **Pipeline check.** Population PSTH half-rise after grating onset (median over sessions): LGN
  37 ms, V1 47, LM 50, RL 52, AL 53, AM 57, PM 60, so LGN and V1 lead as expected. The baseline is
  the mean PSTH over the first 20 ms after onset (2 ms bins, 10 ms smoothing), taken as activity
  before the visual response arrives; it is not the grey period itself, because the cache keeps
  no spikes before onset. Gratings follow 1 s of grey, so those 20 ms still reflect grey-screen
  activity; a response that began inside 20 ms would inflate the baseline and delay the half-rise.
  The first version of this check used natural scenes and put V1 at 93 ms: scenes follow each other
  with no grey gap, so the first 20 ms hold the previous image's response. The check was moved to
  gratings.

Limits (open):
- This measures what a linear decoder can learn from this many trials, not the total information
  in timing. A better-regularised or nonlinear decoder, or a bias-corrected information estimate,
  may find more. The high-dimensional codes depend on regularisation details: in spot checks on
  one session, an LDA with one pooled Ledoit-Wolf covariance moved 10 ms and 5 ms accuracies by
  up to 3.3 points either way relative to the scikit-learn version used here.
- 20 units per area and 7-10 sessions per area. A percentile bootstrap over so few sessions tends
  to give CIs that are too narrow, corrected ones included; the LGN scene gain does not survive a
  t-based Bonferroni interval. The corrected bounds come from 10,000 resamples; 100,000 moved them
  by at most 0.4 points.
- The family-wise correction covers only the 14 primary contrasts. The 50 and 5 ms, latency,
  count-plus-latency and fine-timing gains are exploratory and uncorrected.
- One 250 ms window. Gratings at 1-2 Hz complete less than one cycle in it, and natural scenes
  carry the previous image's tail into it. One jitter width (50 ms) only; 10-25 ms jitter would
  place the time scale more precisely.
- Area = the structure label of the unit's peak channel. Sessions were picked for area coverage,
  not at random.

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
- For reading out mouse visual cortex with a linear decoder, 50 ms bins beat both a single count
  and finer bins at 20 units (measured here, above). A model compared against these data should
  match the slow time course of responses before it is asked to match millisecond timing.

## Open questions
- How much information is carried by spike timing versus rate, in each area. Partly answered for
  mouse visual areas and a linear decoder (above): finer-than-50 ms timing carries information in
  every area, most in LGN, but at 20 units and these trial counts a decoder gains most from 50 ms
  bins (10 ms bins beat the count only in LGN, firmly only for gratings), and first-spike latency
  adds nothing to the count. Still open: the total information in
  timing (beyond what a linear decoder can learn), larger populations, other brain areas, and
  whether downstream neurons read the fine timing at all.
- Whether oscillations are causal for computation or a side effect of E-I circuits.

## Related
- [[neurons-and-synapses]] - where spikes come from.
- [[predictive-processing]] - a theory of what cortical computation is *for*.
- [[spiking-neural-networks]] - simulate these codes.
- [[efficient-brain-like-learning]] - put sparse, event-driven updates into a learner, with measurements.
- [[brain-rhythms-and-oscillations]] - spike timing against theta and gamma rhythms.
- [[dendritic-computation]] - single neurons compute more than a weighted sum.
- [[measuring-the-brain-and-open-datasets]] - the Allen Neuropixels data behind the timing-versus-count table.
- [Brain World](../game/world/) - a 3D creature whose tone-hearing neurons use gain modulation: sound scales their visual drive.

## References
- Olshausen & Field (1996) "Emergence of simple-cell receptive field properties by learning a sparse code for natural images", *Nature* 381:607. doi:10.1038/381607a0
- Hopfield (1982) "Neural networks and physical systems with emergent collective computational abilities", *PNAS* 79:2554. doi:10.1073/pnas.79.8.2554
- Lennie (2003) "The cost of cortical computation", *Current Biology* 13:493. doi:10.1016/S0960-9822(03)00135-0
- Carandini & Heeger (2012) "Normalization as a canonical neural computation", *Nat Rev Neurosci* 13:51.
- Dayan & Abbott, *Theoretical Neuroscience* (MIT Press, 2001), chapters 1-4.
- Panzeri, Petersen, Schultz, Lebedev & Diamond (2001) "The role of spike timing in the coding of stimulus location in rat somatosensory cortex", *Neuron* 29:769. doi:10.1016/S0896-6273(01)00251-3
- Reinagel & Reid (2000) "Temporal coding of visual information in the thalamus", *J Neurosci* 20:5392. doi:10.1523/JNEUROSCI.20-14-05392.2000
- Gollisch & Meister (2008) "Rapid neural coding in the retina with relative spike latencies", *Science* 319:1108. doi:10.1126/science.1149639
- Butts et al. (2007) "Temporal precision in the neural code and the timescales of natural vision", *Nature* 449:92. doi:10.1038/nature06105
- Panzeri, Brunel, Logothetis & Kayser (2010) "Sensory neural codes using multiplexed temporal scales", *Trends Neurosci* 33:111. doi:10.1016/j.tins.2009.12.001
- Siegle et al. (2021) "Survey of spiking in the mouse visual system reveals functional hierarchy", *Nature* 592:86. doi:10.1038/s41586-020-03171-x
- Sotomayor-Gómez, Battaglia & Vinck (2023) "Temporal spiking sequences in visual cortex carry unique information about natural movies", bioRxiv preprint. doi:10.1101/2023.06.27.546669
- Allen Brain Observatory, Visual Coding - Neuropixels data (NWB files): https://allen-brain-observatory.s3.us-west-2.amazonaws.com/visual-coding-neuropixels/ecephys-cache/manifest.json
