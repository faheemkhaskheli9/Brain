---
title: Connectomes and whole-brain emulation projects
category: simulation
tags: [connectome, whole-brain-emulation, flywire, microns, h01, openworm, blue-brain, human-brain-project, ebrains, digital-twin]
use_cases:
  - what is the state of the art in simulating real brains
  - which connectomes exist and how big are they
  - how close are we to whole human brain emulation
status: stable
last_verified: 2026-10-11
sources:
  - https://www.nih.gov/news-events/nih-research-matters/complete-wiring-map-adult-fruit-fly-brain
  - https://www.microns-explorer.org/cortical-mm3
  - https://doi.org/10.1126/science.adk4858
  - https://bbp.epfl.ch/
  - https://doi.org/10.1016/j.cell.2015.09.029
  - https://ora.ox.ac.uk/objects/uuid:a6880196-34c7-47a0-80f1-74d32ab98788
---

# Connectomes and whole-brain emulation projects

## Summary
**Whole-brain emulation (WBE)** means scanning a brain at synapse resolution and
simulating it closely enough to reproduce its behaviour. The path has three steps:
(1) map the **connectome** (every neuron and synapse), (2) infer each element's
dynamics and learning rules, (3) simulate it and check the behaviour matches.
As of 2026 step 1 is complete for a worm, a fly larva and an adult fruit fly, and
for small cubes of mouse and human cortex. Steps 2-3 have partial successes in the
fly. A human brain is about 600,000 times more neurons than a fly and is far
beyond current capability.

## How it works

### Connectome milestones
| Year | Organism / tissue | Size | Notes |
|---|---|---|---|
| 1986 | *C. elegans* worm | 302 neurons, ~7,000 synapses | White et al., hand-traced from electron microscopy (EM) |
| 2023 | *Drosophila* larva | ~3,000 neurons | Winding et al., *Science* |
| 2024 | Adult fruit fly brain (**FlyWire**) | 139,255 neurons, 50+ million synapses | Dorkenwald et al., *Nature*; EM + AI segmentation + crowd proofreading |
| 2024 | Human cortex, 1 mm³ (**H01**) | ~57,000 cells, ~150 million synapses, 1.4 PB of images | Shapson-Coe et al., *Science*; from surgical tissue |
| 2025 | Mouse visual cortex, 1 mm³ (**MICrONS**) | ~200,000 cells (~120,000 neurons), ~523 million synapses | *Nature*, April 2025; ~75,000 neurons' activity also recorded *before* imaging |

The human brain is roughly 1.2 million mm³. At the H01 rate (1.4 PB per mm³),
imaging alone would be on the order of an exabyte-plus of data.

### Simulation projects
| Project | Goal | Status |
|---|---|---|
| **OpenWorm** | Simulate *C. elegans* body + 302-neuron nervous system | Ongoing open-source effort. Even with the full connectome, worm behaviour is not fully reproduced, because neuromodulation and synapse signs/weights matter |
| **Fly brain models** | Connectome-constrained models | Shiu et al. (2024): LIF model of the whole fly brain predicted feeding and grooming circuits, later confirmed experimentally. Lappalainen et al. (2024): connectome-constrained deep network predicted fly visual neuron responses |
| **MICrONS digital twin** | Deep network trained on recorded activity to predict mouse visual cortex responses | Part of the 2025 package; predicts responses to new stimuli |
| **Blue Brain Project** (EPFL, 2005-2024) | Biophysically detailed simulation of rodent cortex | Markram et al. (2015) reconstructed a ~31,000-neuron rat neocortical microcircuit. Project ended in December 2024; tools continue in open platforms |
| **Human Brain Project → EBRAINS** (EU, 2013-2023) | Brain research infrastructure: atlases, simulators (NEST, NEURON, The Virtual Brain), neuromorphic access | HBP ended in 2023; EBRAINS continues as the research infrastructure |
| **Allen Institute / BRAIN Initiative** | Cell-type atlases, mouse and human brain cell census | Cell-type atlases of the whole mouse brain published 2023 |

### What a connectome does *not* give you
- **Synapse weights and signs** (only partly inferable from EM).
- **Neuromodulators and gap junctions** (hard to see in EM).
- **Learning rules**, and how they differ by cell type.
- **Body and environment.** A brain needs a sensorimotor loop to behave.
- **Moment-to-moment state** (which synapses are potentiated right now). That is
  the "memory content", and is what an emulation of a *specific person* would need.

## Relevance to building brain-like AI
- Two different goals often get mixed up:
  1. **Emulate a specific brain** (WBE). Needs the connectome and the state. Far off for humans.
  2. **Build a machine that learns like a brain.** Needs the *principles*
     (architecture, learning rules, memory systems), not one brain's wiring.
     Achievable in steps today. See [[build-a-brain-like-learner]].
- The fly results show that **wiring + simple neurons already predicts a lot of
  function**. Connectome-constrained architectures are a promising source of
  inductive bias for AI.
- "Digital twin" models (trained to predict recorded neural activity) are a
  practical middle ground between pure AI and full emulation.

## Open questions
- What scan resolution and which molecular data are sufficient for emulation.
- Whether it is possible to verify that an emulation is "the same" mind; this is
  a philosophical problem as much as a technical one.
- Ethics of simulating systems that may have experiences.

## Related
- [[levels-of-brain-modeling]] - the compute required at each level.
- [[neuromorphic-hardware]] - hardware for large simulations.
- [[brain-structure-overview]] - what a human connectome would have to cover.
- [[neuroethics]] - the moral status of an emulation, and precautionary positions.

## References
- Dorkenwald et al. (2024) "Neuronal wiring diagram of an adult brain", *Nature* 634:124. NIH summary: https://www.nih.gov/news-events/nih-research-matters/complete-wiring-map-adult-fruit-fly-brain
- MICrONS Consortium (2025) "Functional connectomics spanning multiple areas of mouse visual cortex", *Nature* 640:435. https://www.microns-explorer.org/cortical-mm3
- Shapson-Coe et al. (2024) "A petavoxel fragment of human cerebral cortex reconstructed at nanoscale resolution", *Science* 384:eadk4858. doi:10.1126/science.adk4858
- Shiu et al. (2024) "A Drosophila computational brain model reveals sensorimotor processing", *Nature* 634:210.
- Lappalainen et al. (2024) "Connectome-constrained networks predict neural activity across the fly visual system", *Nature* 634:1132.
- Markram et al. (2015) "Reconstruction and Simulation of Neocortical Microcircuitry", *Cell* 163:456. doi:10.1016/j.cell.2015.09.029
- White, Southgate, Thomson & Brenner (1986), *Phil Trans R Soc B* 314:1.
- Winding et al. (2023) "The connectome of an insect brain", *Science* 379:eadd9330.
- Blue Brain Project: https://bbp.epfl.ch/
- Sandberg & Bostrom (2008) "Whole Brain Emulation: A Roadmap", FHI Technical Report #2008-3.
