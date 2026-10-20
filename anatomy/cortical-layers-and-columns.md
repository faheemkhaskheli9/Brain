---
title: Cortical layers, columns and the canonical microcircuit
category: anatomy
tags: [neocortex, cortical-layers, lamina, layer-4, layer-5, layer-6, cortical-column, minicolumn, canonical-microcircuit, feedforward, feedback, recurrent-amplification, it-pt-ct]
use_cases:
  - what do the six layers of the neocortex do
  - what is a cortical column and is it a real computational unit
  - what is the canonical cortical microcircuit
  - which layers carry feedforward and which carry feedback signals
  - how could a few thalamic inputs drive the cortex (recurrent amplification)
status: draft
last_verified: 2026-10-17
sources:
  - https://doi.org/10.1146/annurev.neuro.27.070203.144152
  - https://doi.org/10.1038/nn.3917
  - https://doi.org/10.1093/cercor/1.1.1
  - https://doi.org/10.1098/rstb.2005.1623
  - https://doi.org/10.1016/j.neuron.2012.10.038
---

# Cortical layers, columns and the canonical microcircuit

## Summary
The neocortex is a folded sheet, a few millimetres thick, built from six layers
([[brain-structure-overview]]). Each layer has its own inputs, cell types and output
targets, and the same layered pattern repeats, with variations, across areas. That
repetition led to the idea of a **canonical microcircuit**: one circuit, copied many
times, that computes something general (Douglas, Martin & Whitteridge 1989). The layers
and their wiring are **established**. What the circuit computes, and whether columns are
real computational units, are **open**.

## How it works

### The six layers (established)
| Layer | Main contents | Main inputs | Main outputs |
|---|---|---|---|
| 1 | Few cell bodies; apical dendrite tufts of deeper pyramidal cells, axons | Feedback from higher areas, matrix thalamus | (none of its own to speak of) |
| 2/3 | Pyramidal cells with local and cortico-cortical axons | Layer 4, other cortical areas | Other cortical areas (feedforward), layer 5 |
| 4 | Spiny stellate and pyramidal cells (the "granular" layer) | Core thalamus, e.g. LGN in V1; feedforward input from lower areas | Layers 2/3 |
| 5 | Large pyramidal cells | Layers 2/3, thalamus, other areas | Subcortical targets: striatum, thalamus, brainstem, spinal cord |
| 6 | Pyramidal cells with corticothalamic axons | Other layers, thalamus | Thalamus (feedback that shapes its relay) |

Primary motor cortex has almost no layer 4 ("agranular" cortex), so the table is a
template, not a law. Projection neurons fall into three genetically and anatomically
distinct classes: intratelencephalic (IT) cells in layers 2-6 project to cortex and
striatum, pyramidal-tract (PT) cells in layer 5B project out to brainstem and spinal
cord, and corticothalamic (CT) cells in layer 6 project to thalamus (Harris & Shepherd 2015).
About a fifth of cortical neurons are inhibitory interneurons (PV, SST, VIP), found in
every layer ([[neurons-and-synapses]]).

### The canonical microcircuit
Douglas, Martin & Whitteridge (1989) modelled cat visual cortex with a few populations
(superficial and deep pyramidal cells, inhibitory cells) and proposed that the same
circuit repeats everywhere. The textbook feedforward route is thalamus → layer 4 →
layers 2/3 → layer 5 → layer 6 → back to thalamus and layer 4, though deep layers also
get direct thalamic input and the real wiring is denser than this chain (Douglas & Martin 2004).

**Recurrent amplification (established anatomy, model-level account).** Thalamic
synapses are a small minority of the excitatory synapses on layer 4 cells; most come
from other cortical neurons. Douglas & Martin argued that weak thalamic input is
amplified by recurrent excitation between nearby pyramidal cells and held in check by
inhibition (Douglas et al. 1995). The code below shows the arithmetic of that idea.

### Feedforward and feedback by layer
Between areas, **feedforward** connections mostly start in superficial layers and
end in layer 4; **feedback** connections mostly start in deep layers and end outside
layer 4, in layers 1 and 6. Felleman & Van Essen (1991) used these laminar patterns to
rank 32 visual areas of the macaque into a hierarchy. Layer 1 feedback lands on the
apical tufts of pyramidal cells, where it can change how the cell responds to its basal
input ([[dendritic-computation]]).

### Columns
- **Established.** Neurons in a vertical track through the cortex share response
  properties: the same body location and touch submodality in somatosensory cortex
  (Mountcastle 1957), and orientation and ocular-dominance columns in cat and monkey V1
  (Hubel & Wiesel 1962).
- **Not universal.** Rodent V1 has well-tuned orientation-selective cells but no
  orientation columns; preferences are mixed "salt and pepper" (Ohki et al. 2005).
  Ocular-dominance columns vary even between individuals of one monkey species.
- **Contested.** Whether the column is a basic computational module has been doubted
  since Horton & Adams (2005) called it "a structure without a function". Mountcastle
  (1997) proposed narrower **minicolumns** as the repeating unit; that is a hypothesis.

## Relevance to building brain-like AI
- Predictive coding gives the layers jobs: superficial cells send prediction errors
  forward, deep cells send predictions back (Bastos et al. 2012). This mapping is a
  **hypothesis** that fits the laminar anatomy above; see [[predictive-processing]].
- The split between basal (feedforward) and apical (layer 1 feedback) input is what
  dendritic credit-assignment models use to keep the two signals apart
  ([[brain-vs-deep-learning]]).
- If one circuit really repeats everywhere, a brain-like system could use one module
  type many times. The Thousand Brains theory pushes this furthest and is a hypothesis
  ([[cognitive-architectures]]).
- Recurrent amplification is a cheap way to turn weak, sparse input into a strong,
  stable response, but it needs fast inhibition to stay stable, as balanced
  excitation-inhibition networks do ([[neural-coding-and-computation]]).

## Code (optional)
Recurrent amplification in one excitatory population with linear-threshold units:
with recurrent weight `w < 1` the steady state is `input / (1 - w)`.

```python
import numpy as np

def steady_rate(drive, w, steps=2000, dt=0.1, tau=1.0):
    """Rectified-linear population: tau dr/dt = -r + [drive + w r]+."""
    r = 0.0
    for _ in range(steps):
        r += dt / tau * (-r + max(drive + w * r, 0.0))
    return r

drive = 0.1                                   # weak thalamic input
for w in (0.0, 0.5, 0.8, 0.9):
    r = steady_rate(drive, w)
    print(f"recurrent weight {w:.1f}: rate {r:.2f}, gain {r / drive:4.1f}x")
    assert np.isclose(r, drive / (1 - w), rtol=1e-3)
# At w >= 1 the excitatory loop alone runs away: inhibition has to hold it.
assert steady_rate(drive, 1.05, steps=400) > 10 * steady_rate(drive, 0.9, steps=400)
```

## Open questions
- What, if anything, the canonical microcircuit computes in common across areas
  (predictive coding is the leading hypothesis, not a settled fact).
- Whether columns or minicolumns are computational units, given that some mammals see
  well without orientation columns.
- What layer 1 feedback does to perception and learning in behaving animals.
- How much the circuit differs between areas (agranular motor cortex, prefrontal
  cortex) and whether one model can cover them all.

## Related
- [[brain-structure-overview]] - the cortex among the brain's other subsystems.
- [[neurons-and-synapses]] - the pyramidal cells and interneurons in each layer.
- [[dendritic-computation]] - apical tufts in layer 1 and how feedback changes firing.
- [[predictive-processing]] - the layer-by-layer predictive-coding hypothesis.
- [[sensory-systems-and-vision]] - V1 columns and the visual hierarchy.
- [[cognitive-architectures]] - the Thousand Brains theory of cortical columns.

## References
- Douglas, Martin & Whitteridge (1989) "A canonical microcircuit for neocortex", *Neural Comput* 1:480. doi:10.1162/neco.1989.1.4.480
- Douglas, Koch, Mahowald, Martin & Suarez (1995) "Recurrent excitation in neocortical circuits", *Science* 269:981. doi:10.1126/science.7638624
- Douglas & Martin (2004) "Neuronal circuits of the neocortex", *Annu Rev Neurosci* 27:419. doi:10.1146/annurev.neuro.27.070203.144152
- Harris & Shepherd (2015) "The neocortical circuit: themes and variations", *Nat Neurosci* 18:170. doi:10.1038/nn.3917
- Felleman & Van Essen (1991) "Distributed hierarchical processing in the primate cerebral cortex", *Cereb Cortex* 1:1. doi:10.1093/cercor/1.1.1
- Mountcastle (1957) "Modality and topographic properties of single neurons of cat's somatic sensory cortex", *J Neurophysiol* 20:408. doi:10.1152/jn.1957.20.4.408
- Mountcastle (1997) "The columnar organization of the neocortex", *Brain* 120:701. doi:10.1093/brain/120.4.701
- Hubel & Wiesel (1962) "Receptive fields, binocular interaction and functional architecture in the cat's visual cortex", *J Physiol* 160:106. doi:10.1113/jphysiol.1962.sp006837
- Ohki, Chung, Ch'ng, Kara & Reid (2005) "Functional imaging with cellular resolution reveals precise micro-architecture in visual cortex", *Nature* 433:597. doi:10.1038/nature03274
- Horton & Adams (2005) "The cortical column: a structure without a function", *Phil Trans R Soc B* 360:837. doi:10.1098/rstb.2005.1623
- Bastos et al. (2012) "Canonical microcircuits for predictive coding", *Neuron* 76:695. doi:10.1016/j.neuron.2012.10.038
