---
title: Brain rhythms and oscillations
category: function
tags: [oscillations, rhythms, eeg, theta, gamma, alpha, sharp-wave-ripples, phase-precession, binding, interneurons]
use_cases:
  - what are brain waves and where do they come from
  - what is theta phase precession
  - does gamma synchrony bind features together
  - make a spiking network oscillate in the gamma band
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1126/science.1099745
  - https://doi.org/10.1146/annurev-neuro-062111-150444
  - https://doi.org/10.1002/hipo.450030307
  - https://doi.org/10.1038/nature08002
---

# Brain rhythms and oscillations

## Summary
Groups of neurons fire in rhythm, and the summed currents show up as waves in the
EEG and in local field potentials. The rhythms come from circuit loops, mostly
between excitatory cells and inhibitory interneurons, and their speed is set by
synaptic and membrane time constants. Some uses are established, like **theta
phase precession** packing a path into each theta cycle and **sharp-wave ripples**
carrying replay. Bigger claims, like gamma synchrony **binding** features or
routing communication between areas, are **hypotheses**.

## How it works

### The bands (established)
Bands are named by frequency. Edges vary between papers; these are the usual ones
for human EEG (Buzsáki & Draguhn 2004):

| Band | Range (Hz) | Where and when |
|---|---|---|
| Delta and slow oscillation | < 1-4 | Deep non-REM sleep, cortex-wide ([[sleep-and-memory-consolidation]]) |
| Theta | 4-8 (6-10 in rodent hippocampus) | Hippocampus during movement and REM sleep |
| Alpha | 8-12 | Occipital cortex, eyes closed; the first EEG rhythm recorded (Berger 1929) |
| Beta | 13-30 | Motor cortex, holding still; drops before a movement |
| Gamma | 30-80+ | Many areas, during active processing |
| Sharp-wave ripples | about 150-250 | Hippocampus, quiet rest and slow-wave sleep (Buzsáki 2015) |

The bands fall roughly on a log scale, and slower rhythms involve larger networks
(Buzsáki & Draguhn 2004).

### Where rhythms come from (established)
- **Gamma from E-I loops.** Pyramidal cells excite fast-spiking interneurons, which
  inhibit the pyramidal cells back. The cells can fire again only once GABA-A
  inhibition decays, so the decay time (several ms) sets a period in the gamma
  range (Buzsáki & Wang 2012). Optogenetically driving parvalbumin interneurons
  in mouse cortex was enough to produce gamma (Cardin et al. 2009). The code
  below builds this loop.
- **Theta from pacemakers and loops.** Hippocampal theta needs the medial septum;
  lesioning it removes theta. Local interneurons and intrinsic currents shape it.
- **Alpha and spindles involve the thalamus**, through loops between thalamic
  relay cells, the thalamic reticular nucleus and cortex.
- **Ripples** come from a burst of CA3 input onto CA1, with fast interneuron
  inhibition pacing the 150-250 Hz cycles (Buzsáki 2015).

### Theta phase precession (established)
As a rat runs through a place field, the place cell fires at an earlier phase of
each successive theta cycle (O'Keefe & Recce 1993). So within one theta cycle,
cells fire in the order of the places just behind, at and ahead of the animal: a
compressed sweep along the path, about ten times faster than the run. That
compression puts the cells' spikes within a few tens of ms of each other, the
window where STDP can link them ([[learning-and-plasticity]]). See
[[spatial-navigation]] for place cells.

### Gamma and binding (hypothesis)
- In cat visual cortex, cells responding to the same moving bar fired in sync at
  about 40 Hz, and cells responding to two separate bars did not (Gray et al. 1989).
- The **binding-by-synchrony** hypothesis (Singer & Gray 1995) proposes that
  synchrony marks which features belong to one object. It is contested: gamma
  frequency shifts with stimulus contrast, and differs between nearby sites,
  which makes it a poor shared clock (Ray & Maunsell 2010).
- **Communication through coherence** (Fries 2015) proposes that two areas pass
  information best when their gamma is phase-aligned, so attention could route
  signals by aligning rhythms. Also a hypothesis.
- **Theta-gamma code** (Lisman & Jensen 2013): several gamma cycles nest in each
  theta cycle, each holding one item, which could explain a working-memory limit
  of a handful of items. A hypothesis.

### Side effect or mechanism? (open)
A rhythm can be a by-product of a circuit that works for other reasons. The
strongest causal evidence is for ripples, where cutting them short impairs
memory (Girardeau et al. 2009). For gamma, causal tests are harder, because
removing the rhythm usually means changing the interneurons that also do other
work.

## Relevance to building brain-like AI
| Brain | AI component |
|---|---|
| E-I loop sets gamma | Inhibition as normalisation; a rhythm is a free by-product of a balanced recurrent net |
| Theta phase precession | A sequence compressed into one cycle, so a local rule can learn its order |
| Ripples carry replay | An offline replay phase ([[sleep-and-memory-consolidation]]) |
| Theta-gamma nesting (hypothesis) | Slot-based working memory with a small, fixed number of slots |
| Synchrony for binding (hypothesis) | Phase or complex-valued units that tag which features go together |

Most deep networks have no time dimension inside a step, so they have no room for
rhythm. [[spiking-neural-networks]] do, and an E-I spiking net will oscillate
unless tuned not to.

## Code: an E-I loop rings at gamma

Leaky integrate-and-fire excitatory cells drive inhibitory cells, which inhibit
them back (pyramidal-interneuron gamma). The population rate's spectrum has a
sharp peak in the gamma band. Remove the inhibition and the same cells, with the
same noisy drive, fire without a shared rhythm. Weights and drive are tuned for
the demo, not measured.

```python
import numpy as np

nE, nI, dt, T = 400, 100, 0.1, 1000.0          # cells, time step (ms), duration (ms)
tau_m, tau_ampa, tau_gaba = 10.0, 2.0, 8.0      # membrane and synaptic decay times (ms)

def run(inhibition, seed=0):
    rng = np.random.default_rng(seed)
    vE, vI = rng.uniform(0, 1, nE), rng.uniform(0, 1, nI)  # leaky integrate-and-fire, threshold 1
    sE = sI = 0.0                               # population synaptic traces
    rate = np.zeros(int(T / dt))
    for t in range(len(rate)):
        gI = sI if inhibition else 0.0
        vE += dt / tau_m * (-vE + 1.5 + rng.normal(0, 0.5, nE) - 12 * gI)  # noisy drive minus inhibition
        vI += dt / tau_m * (-vI + 6 * sE - 3 * gI)                         # I cells fire only when E cells do
        fE, fI = vE >= 1, vI >= 1
        vE[fE] = 0; vI[fI] = 0
        sE += -dt / tau_ampa * sE + fE.mean()
        sI += -dt / tau_gaba * sI + fI.mean()
        rate[t] = fE.mean()
    return rate[int(200 / dt):]                 # drop the first 200 ms

def spectrum_peak(rate):
    p = np.abs(np.fft.rfft(rate - rate.mean())) ** 2
    f = np.fft.rfftfreq(len(rate), dt / 1000)
    p, f = p[f > 5], f[f > 5]
    return f[p.argmax()], p.max() / p.mean()    # peak frequency (Hz), how sharp the peak is

f_on, sharp_on = spectrum_peak(run(inhibition=True))
f_off, sharp_off = spectrum_peak(run(inhibition=False))
print(f"E-I loop       peak {f_on:5.1f} Hz, sharpness {sharp_on:5.0f}")
print(f"no inhibition  peak {f_off:5.1f} Hz, sharpness {sharp_off:5.0f}")
assert 30 <= f_on <= 100                        # the loop rings in the gamma band
assert sharp_on > 4 * sharp_off                 # and inhibition is what synchronises it
```

## Open questions
- Which rhythms do computational work and which are by-products of balanced circuits.
- Whether gamma synchrony binds features or routes signals, or neither.
- How theta sequences are generated: from the input, or from the network itself.
- Why the bands sit where they do, and how stable their edges are across people and species.

## Related
- [[neural-coding-and-computation]] - phase and timing as part of the neural code.
- [[spatial-navigation]] - place cells, whose firing precesses against theta.
- [[sleep-and-memory-consolidation]] - slow oscillations, spindles and ripples during sleep.
- [[spiking-neural-networks]] - simulate the E-I loops that make rhythms.
- [[measuring-the-brain-and-open-datasets]] - EEG and LFP, where rhythms are recorded.

## References
- Buzsáki & Draguhn (2004) "Neuronal oscillations in cortical networks", *Science* 304:1926. doi:10.1126/science.1099745
- Buzsáki & Wang (2012) "Mechanisms of gamma oscillations", *Annu Rev Neurosci* 35:203. doi:10.1146/annurev-neuro-062111-150444
- Cardin et al. (2009) "Driving fast-spiking cells induces gamma rhythm and controls sensory responses", *Nature* 459:663. doi:10.1038/nature08002
- O'Keefe & Recce (1993) "Phase relationship between hippocampal place units and the EEG theta rhythm", *Hippocampus* 3:317. doi:10.1002/hipo.450030307
- Gray, König, Engel & Singer (1989) "Oscillatory responses in cat visual cortex exhibit inter-columnar synchronization which reflects global stimulus properties", *Nature* 338:334. doi:10.1038/338334a0
- Singer & Gray (1995) "Visual feature integration and the temporal correlation hypothesis", *Annu Rev Neurosci* 18:555. doi:10.1146/annurev.ne.18.030195.003011
- Ray & Maunsell (2010) "Differences in gamma frequencies across visual cortex restrict their possible use in computation", *Neuron* 67:885. doi:10.1016/j.neuron.2010.08.004
- Fries (2015) "Rhythms for cognition: communication through coherence", *Neuron* 88:220. doi:10.1016/j.neuron.2015.09.034
- Lisman & Jensen (2013) "The theta-gamma neural code", *Neuron* 77:1002. doi:10.1016/j.neuron.2013.03.007
- Buzsáki (2015) "Hippocampal sharp wave-ripple: a cognitive biomarker for episodic memory and planning", *Hippocampus* 25:1073. doi:10.1002/hipo.22488
- Girardeau, Benchenane, Wiener, Buzsáki & Zugaro (2009) "Selective suppression of hippocampal ripples impairs spatial memory", *Nat Neurosci* 12:1222. doi:10.1038/nn.2384
- Berger (1929) "Über das Elektrenkephalogramm des Menschen", *Archiv für Psychiatrie und Nervenkrankheiten* 87:527. doi:10.1007/BF01797193
