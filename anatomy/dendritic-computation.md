---
title: Dendritic computation
category: anatomy
tags: [dendrites, nmda-spikes, bac-firing, two-layer-neuron, credit-assignment, plateau-potentials, apical-dendrite]
use_cases:
  - do single neurons compute more than a weighted sum
  - what is an NMDA spike or a dendritic plateau potential
  - how could dendrites carry error signals for credit assignment
  - model a neuron with nonlinear dendritic branches
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1146/annurev.neuro.28.061604.135703
  - https://doi.org/10.1016/S0896-6273(03)00149-1
  - https://doi.org/10.1038/35005094
  - https://doi.org/10.1038/18686
  - https://doi.org/10.48550/arxiv.1810.11393
---

# Dendritic computation

## Summary
The point neuron of deep learning sums its inputs and applies one nonlinearity.
Real dendrites are not passive wires: their branches fire their own local spikes,
so a single cortical neuron behaves more like a **two-layer network** (Poirazi et
al. 2003). Where on the tree an input lands, and which inputs arrive together on
the same branch, changes the output. The separate apical dendrite of pyramidal
cells may also carry a **teaching signal**, one of the leading **hypotheses** for
how the cortex solves credit assignment without backprop.

## How it works

### Active dendrites (established)
- Dendrites carry voltage-gated sodium, calcium and NMDA channels, so they can
  generate regenerative events of their own, not just pass current to the soma
  (London & Häusser 2005).
- **NMDA spikes.** When enough nearby synapses on one thin basal branch are active
  together, NMDA receptors open further and the branch produces a local spike of
  tens of ms (Schiller et al. 2000). Inputs clustered on one branch sum
  **supralinearly**; the same inputs scattered over branches sum roughly linearly
  (Losonczy & Magee 2006 in CA1 obliques).
- **BAC firing.** In layer 5 pyramidal cells, a back-propagating action potential
  that coincides with input to the distal apical tuft triggers a calcium spike
  and a burst of somatic spikes (Larkum et al. 1999). The cell thus detects
  coincidence between bottom-up input (near the soma) and top-down input (in the
  tuft, layer 1).
- **Plateau potentials** in CA1 dendrites can create a new place field in one
  trial, potentiating inputs that were active seconds before or after the plateau
  (Bittner et al. 2017, behavioural-timescale plasticity).
- In human layer 2/3 neurons, dendritic calcium spikes are strongest for
  intermediate input and weaker for strong input. That non-monotonic response lets
  one dendrite compute XOR, which a point neuron cannot (Gidon et al. 2020).

### A neuron as a network (established modelling result)
- A compartmental model of a CA1 pyramidal cell was predicted well by a two-layer
  network: each branch applies a sigmoid to its summed input, and the soma sums
  the branch outputs (Poirazi, Brannon & Mel 2003).
- A detailed layer 5 cortical neuron model, with NMDA synapses, needed a temporal
  convolutional network with 5 to 8 layers to mimic its spike output at
  millisecond resolution (Beniaguev, Segev & London 2021). Without NMDA, one hidden
  layer was enough. See [[neurons-and-synapses]].

### Dendrites and credit assignment (hypothesis)
Cortex has to learn deep representations without sending exact gradients backward
([[brain-vs-deep-learning]]). The pyramidal cell's two zones suggest a way:
- **Segregated dendrites** (Guerguiev, Lillicrap & Richards 2017): basal dendrites
  take feedforward input, the apical tuft takes feedback from higher areas, and the
  difference drives local learning.
- **Dendritic error** (Sacramento et al. 2018): apical dendrites compare top-down
  feedback with a local interneuron prediction. The mismatch is an error signal,
  and the resulting microcircuit approximates backprop.
- **Burst-dependent plasticity** (Payeur et al. 2021): apical input changes whether
  a cell sends single spikes or bursts. Single spikes carry the signal forward,
  burst rate carries the error back, and plasticity depends on bursts.
- **Dendrites as prediction** (Hawkins & Ahmad 2016): an NMDA spike on a distal
  branch depolarises the cell without firing it, putting it in a "predicted" state
  for the next input.

None of these is established as how cortex learns. Each matches parts of the
anatomy; the experimental tests are ongoing.

## Relevance to building brain-like AI
| Brain | AI component |
|---|---|
| Branch-level nonlinearity | A neuron as a small two-layer net; sparse "dendritic" gating units |
| Clustered vs scattered input | Where a weight sits matters, not only its size |
| Apical tuft for top-down input | A separate input channel for feedback or context, multiplicative with feedforward |
| Dendritic error signals (hypothesis) | Local learning rules that approximate backprop ([[brain-inspired-learning-algorithms]]) |
| Plateau potentials | One-shot learning with a seconds-long eligibility window |

A network of dendritic neurons can do with fewer cells what a point-neuron network
needs more cells for, at the cost of more state per cell.

## Code: clustered inputs fire a branch, scattered ones do not

A point neuron sums all synapses, so eight active synapses give the same output
wherever they land. A two-layer neuron (Poirazi et al. 2003) passes each branch's
sum through a sigmoid before the soma adds them. Eight synapses on one branch
cross the branch threshold; the same eight spread over eight branches do not.
The threshold and gain are illustrative, not fitted.

```python
import numpy as np

n_branch, per_branch = 10, 20                   # 10 dendritic branches, 20 synapses each
n_syn = n_branch * per_branch

def branch_nl(x):                               # NMDA-spike-like sigmoid: little output until
    return 1 / (1 + np.exp(-(x - 6) * 1.5))     # about 6 synapses on one branch are active together

def point_neuron(active):                       # one layer: the soma just sums every synapse
    return active.sum() / 10

def two_layer_neuron(active):                   # Poirazi et al. 2003: each branch is a hidden unit
    return branch_nl(active.reshape(n_branch, per_branch).sum(1)).sum()

def pattern(clustered, k=8):
    a = np.zeros(n_syn)
    a[np.arange(k) if clustered else np.arange(k) * per_branch] = 1  # all on branch 0, or one per branch
    return a

for name, neuron in (("point", point_neuron), ("two-layer", two_layer_neuron)):
    c, s = neuron(pattern(True)), neuron(pattern(False))
    print(f"{name:9s}  8 synapses clustered {c:.2f}   scattered {s:.2f}")

assert point_neuron(pattern(True)) == point_neuron(pattern(False))  # a point neuron cannot tell
assert two_layer_neuron(pattern(True)) > 5 * two_layer_neuron(pattern(False))  # dendrites can

# Feature binding: the cell should respond to A AND B on the same branch, not to A or B alone.
A, B = np.zeros(n_syn), np.zeros(n_syn)
A[0:4], B[4:8] = 1, 1                           # 4 synapses each, both on branch 0
r = {k: float(two_layer_neuron(v)) for k, v in (("A", A), ("B", B), ("A+B", A + B))}
print({k: round(v, 2) for k, v in r.items()})
assert r["A+B"] > 2 * (r["A"] + r["B"])         # supralinear: more than the sum of its parts
```

## Open questions
- How often cortical neurons use dendritic spikes during natural behaviour, not
  only in slices.
- Whether synapses carrying related features actually cluster on the same branch,
  and how plasticity puts them there.
- Which, if any, of the dendritic credit-assignment hypotheses the cortex uses.
- How much dendritic detail a useful AI model needs, given that it multiplies cost.

## Related
- [[neurons-and-synapses]] - the neuron parts; this file is about what the dendrites compute.
- [[brain-inspired-learning-algorithms]] - local learning rules that dendritic error signals could support.
- [[brain-vs-deep-learning]] - the credit-assignment problem dendrites may help solve.
- [[levels-of-brain-modeling]] - point neurons vs multi-compartment models.
- [[spatial-navigation]] - place fields created by dendritic plateau potentials.

## References
- London & Häusser (2005) "Dendritic computation", *Annu Rev Neurosci* 28:503. doi:10.1146/annurev.neuro.28.061604.135703
- Poirazi, Brannon & Mel (2003) "Pyramidal neuron as two-layer neural network", *Neuron* 37:989. doi:10.1016/S0896-6273(03)00149-1
- Schiller, Major, Koester & Schiller (2000) "NMDA spikes in basal dendrites of cortical pyramidal neurons", *Nature* 404:285. doi:10.1038/35005094
- Losonczy & Magee (2006) "Integrative properties of radial oblique dendrites in hippocampal CA1 pyramidal neurons", *Neuron* 50:291. doi:10.1016/j.neuron.2006.03.016
- Larkum, Zhu & Sakmann (1999) "A new cellular mechanism for coupling inputs arriving at different cortical layers", *Nature* 398:338. doi:10.1038/18686
- Bittner, Milstein, Grienberger, Romani & Magee (2017) "Behavioral time scale synaptic plasticity underlies CA1 place fields", *Science* 357:1033. doi:10.1126/science.aan3846
- Gidon et al. (2020) "Dendritic action potentials and computation in human layer 2/3 cortical neurons", *Science* 367:83. doi:10.1126/science.aax6239
- Beniaguev, Segev & London (2021) "Single cortical neurons as deep artificial neural networks", *Neuron* 109:2727. doi:10.1016/j.neuron.2021.07.002
- Guerguiev, Lillicrap & Richards (2017) "Towards deep learning with segregated dendrites", *eLife* 6:e22901. doi:10.7554/eLife.22901
- Sacramento, Costa, Bengio & Senn (2018) "Dendritic cortical microcircuits approximate the backpropagation algorithm", NeurIPS. doi:10.48550/arxiv.1810.11393
- Payeur, Guerguiev, Zenke, Richards & Naud (2021) "Burst-dependent synaptic plasticity can coordinate learning in hierarchical circuits", *Nat Neurosci* 24:1010. doi:10.1038/s41593-021-00857-x
- Hawkins & Ahmad (2016) "Why neurons have thousands of synapses, a theory of sequence memory in neocortex", *Front Neural Circuits* 10:23. doi:10.3389/fncir.2016.00023
