---
title: Glia and the brain's energy budget
category: anatomy
tags: [glia, astrocytes, oligodendrocytes, microglia, myelin, energy, atp, sparse-coding, metabolism]
use_cases:
  - what do glial cells do besides support neurons
  - how much energy does the brain use and what does it spend it on
  - why does the energy budget force sparse, event-driven coding
  - do astrocytes or myelin take part in learning
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1097/00004647-200110000-00001
  - https://doi.org/10.1038/jcbfm.2012.35
  - https://doi.org/10.1016/j.neuron.2012.08.019
  - https://doi.org/10.1002/cne.24040
  - https://doi.org/10.1162/neco.1996.8.3.531
---

# Glia and the brain's energy budget

## Summary
Roughly half the cells in the human brain are not neurons. Astrocytes,
oligodendrocytes and microglia keep synapses working, speed up axons and prune
connections, and some of them change with learning. All of it runs on a fixed
power supply of about 20 W, and most of that energy goes on signalling: spikes and,
above all, synaptic transmission. A spike is expensive enough that the brain can
only afford a few active neurons at a time, which is the strongest argument for
sparse, event-driven codes in brain-like hardware.

## How it works

### How many glia (established)
- The often-quoted "ten glia per neuron" is a myth. Counts by the isotropic
  fractionator put the human brain at about 86 billion neurons and a similar number
  of non-neuronal cells, close to 1:1 overall (Azevedo et al. 2009; review by
  von Bartheld, Bahney & Herculano-Houzel 2016). The ratio varies by region: the
  cerebellum is neuron-dense, the cortex has more glia than neurons.

### What each kind of glia does
| Cell | Established role | Role in learning |
|---|---|---|
| **Astrocytes** | Take up glutamate and K+ released at synapses, recycle transmitter, couple neural activity to blood flow, store glycogen | Wrap synapses into a "tripartite synapse" and can release transmitters themselves (Araque et al. 1999). Activating hippocampal astrocytes in mice improved memory (Adamsky et al. 2018). How much they compute in normal behaviour is debated. |
| **Oligodendrocytes** | Make myelin in the CNS, so spikes jump between nodes and travel faster, at lower energy cost | Myelination is adaptive: neural activity increases new oligodendrocytes and myelin (Gibson et al. 2014), and mice that cannot make new oligodendrocytes fail to learn a new motor skill (McKenzie et al. 2014). Changing conduction delay is a learning knob that ANNs do not have. |
| **Microglia** | Immune cells of the brain; clear debris | Prune synapses during development, tagged by complement proteins, with less active synapses removed preferentially (Schafer et al. 2012). See [[brain-development-and-critical-periods]]. |

### The energy budget (established, numbers are estimates)
- The brain is about 2% of body mass and uses about 20% of the body's resting
  oxygen (Raichle & Gusnard 2002), roughly 20 W ([[brain-structure-overview]]).
- **Where it goes.** A bottom-up budget for rodent cortex (Attwell & Laughlin 2001)
  put about half of signalling energy on action potentials and a third on
  postsynaptic currents, the rest on resting potentials and transmitter recycling.
  Measurements later showed action potentials waste less charge than assumed
  (Alle, Roth & Geiger 2009), and updated budgets make **synaptic transmission
  the largest single cost** (Howarth, Gleeson & Attwell 2012; Harris, Jolivet &
  Attwell 2012). Most of the ATP is spent by the Na+/K+ pump restoring ion
  gradients.
- **The budget caps activity.** Given the cost per spike, the brain's power can
  support only a low mean firing rate. Lennie (2003) estimated that only about 1%
  of cortical neurons can be substantially active at once.
- **Supply.** Neurons get energy through blood flow that rises locally with
  activity (the basis of the fMRI BOLD signal, see
  [[measuring-the-brain-and-open-datasets]]). The **astrocyte-neuron lactate
  shuttle**, in which astrocytes turn glucose into lactate for neurons (Pellerin &
  Magistretti 1994), is a **hypothesis** that is still contested.

### Why energy argues for sparse codes
If a spike costs much more than staying silent, a neuron that fires half the time
carries the most bits per time step but not the most bits per unit of energy. Levy
& Baxter (1996) showed that the energy-optimal firing probability is low and falls
as the relative cost of a spike rises. Sparse coding in sensory cortex fits this
(see [[neural-coding-and-computation]]).

## Relevance to building brain-like AI
| Brain | AI / hardware component |
|---|---|
| Spikes and synapses dominate the bill | Count energy per event, not per FLOP; data movement is the GPU analogue |
| Energy-optimal low firing rates | Activation sparsity, top-k, event-driven updates ([[neuromorphic-hardware]]) |
| Adaptive myelin | Learnable delays in spiking networks |
| Microglial pruning | Prune weak weights after an overgrown start |
| Astrocytes as a slow, wide modulator (hypothesis) | A slow gating state over many synapses at once |

## Code: bits per unit energy favour sparse firing

A binary neuron fires with probability p in each time bin. Its information is the
entropy H(p) bits. Staying alive costs 1 unit per bin, a spike costs r more
(Levy & Baxter 1996). The bits-per-energy optimum moves to sparse firing as r
grows. The values of r are illustrative.

```python
import numpy as np

p = np.linspace(0.001, 0.5, 5000)                 # firing probability per bin
H = -(p * np.log2(p) + (1 - p) * np.log2(1 - p))  # bits per bin

best = {}
for r in (1, 10, 100):                            # cost of a spike relative to resting cost
    eff = H / (1 + r * p)                         # bits per unit energy
    best[r] = p[eff.argmax()]
    print(f"spike cost {r:3d}x rest: best firing probability {best[r]:.3f}, "
          f"{eff.max():.3f} bits/energy (vs {eff[-1]:.3f} at p=0.5)")

assert H.argmax() == len(p) - 1                   # bits alone peak at p = 0.5
assert best[1] > best[10] > best[100]             # pricier spikes, sparser optimum
assert best[100] < 0.05
```

## Open questions
- How much astrocytes compute in the awake, behaving brain, and on what timescale.
- How often adult learning relies on new myelin, and how fast it changes.
- The real energy-supply route from blood to neurons (the lactate-shuttle debate).
- How close the brain's codes are to the energy optimum, region by region.

## Related
- [[neurons-and-synapses]] - the neurons and synapses this energy is spent on.
- [[neural-coding-and-computation]] - sparse codes and why the brain is efficient.
- [[neuromorphic-hardware]] - chips that copy event-driven, low-activity computing.
- [[sleep-and-memory-consolidation]] - sleep, synaptic downscaling and its energy savings.
- [[brain-structure-overview]] - cell counts and the 20 W figure.

## References
- Azevedo et al. (2009) "Equal numbers of neuronal and nonneuronal cells make the human brain an isometrically scaled-up primate brain", *J Comp Neurol* 513:532. doi:10.1002/cne.21974
- von Bartheld, Bahney & Herculano-Houzel (2016) "The search for true numbers of neurons and glial cells in the human brain: a review of 150 years of cell counting", *J Comp Neurol* 524:3865. doi:10.1002/cne.24040
- Araque, Parpura, Sanzgiri & Haydon (1999) "Tripartite synapses: glia, the unacknowledged partner", *Trends Neurosci* 22:208. doi:10.1016/S0166-2236(98)01349-6
- Adamsky et al. (2018) "Astrocytic activation generates de novo neuronal potentiation and memory enhancement", *Cell* 174:59. doi:10.1016/j.cell.2018.05.002
- Gibson et al. (2014) "Neuronal activity promotes oligodendrogenesis and adaptive myelination in the mammalian brain", *Science* 344:1252304. doi:10.1126/science.1252304
- McKenzie et al. (2014) "Motor skill learning requires active central myelination", *Science* 346:318. doi:10.1126/science.1254960
- Schafer et al. (2012) "Microglia sculpt postnatal neural circuits in an activity and complement-dependent manner", *Neuron* 74:691. doi:10.1016/j.neuron.2012.03.026
- Raichle & Gusnard (2002) "Appraising the brain's energy budget", *PNAS* 99:10237. doi:10.1073/pnas.172399499
- Attwell & Laughlin (2001) "An energy budget for signaling in the grey matter of the brain", *J Cereb Blood Flow Metab* 21:1133. doi:10.1097/00004647-200110000-00001
- Alle, Roth & Geiger (2009) "Energy-efficient action potentials in hippocampal mossy fibers", *Science* 325:1405. doi:10.1126/science.1174331
- Howarth, Gleeson & Attwell (2012) "Updated energy budgets for neural computation in the neocortex and cerebellum", *J Cereb Blood Flow Metab* 32:1222. doi:10.1038/jcbfm.2012.35
- Harris, Jolivet & Attwell (2012) "Synaptic energy use and supply", *Neuron* 75:762. doi:10.1016/j.neuron.2012.08.019
- Lennie (2003) "The cost of cortical computation", *Curr Biol* 13:493. doi:10.1016/S0960-9822(03)00135-0
- Pellerin & Magistretti (1994) "Glutamate uptake into astrocytes stimulates aerobic glycolysis", *PNAS* 91:10625. doi:10.1073/pnas.91.22.10625
- Levy & Baxter (1996) "Energy efficient neural codes", *Neural Comput* 8:531. doi:10.1162/neco.1996.8.3.531
