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
last_verified: 2026-10-12
sources:
  - https://doi.org/10.1146/annurev.neuro.28.061604.135703
  - https://doi.org/10.1016/S0896-6273(03)00149-1
  - https://doi.org/10.1038/35005094
  - https://doi.org/10.1038/18686
  - https://doi.org/10.48550/arxiv.1810.11393
  - https://doi.org/10.1038/s41467-025-56297-9
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
needs more cells for, at the cost of more state per cell. Fewer cells is not the
same as fewer parameters, though, as the next test shows.

**Point vs dendritic neurons at equal parameters (#85, a computational result about
network design, not evidence about cortex).** Dendritic ANNs already match or beat
dense MLPs on image tasks with far fewer parameters (Chavlis & Poirazi 2025), and
single dendritic-tree neurons solve MNIST-scale tasks (Jones & Kording, arXiv
2009.01269). Those comparisons are against a *one*-hidden-layer dense net, though,
and a dendritic layer is a structured-sparse two-stage net, so the gain could be
depth. [`research/dendritic_neurons.py`](../research/dendritic_neurons.py) (method
pre-registered on #85) adds a dense **two**-hidden-layer control. Each arm is sized
to the same parameter budget: point-1 (one dense tanh layer), point-2 (two), and
dend (each neuron splits a random partition of all inputs over k tanh branches,
learnable branch-to-soma weights, tanh soma). Multiply-adds are reported, not
matched; dend uses 3-20% fewer. Trained by backprop (BP) and by feedback alignment
(FA), learning rate tuned on separate seeds, 10 evaluation seeds:

| Task (budget, k) | Rule | point-1 | point-2 | dend | dend - point-1 (p) |
|---|---|---|---|---|---|
| 8-bit parity, train acc (80, 2) | BP | 0.50 | 0.50 | 0.51 | +0.01 (0.47) |
| | FA | 0.75 | 0.64 | 0.50 | -0.24 (0.006) |
| Feature conjunction, test acc (400, 4) | BP | 0.972 | 0.976 | 0.978 | +0.006 (0.25) |
| | FA | 0.955 | 0.940 | 0.924 | -0.031 (0.021) |
| 8x8 digits, test acc (2000, 4) | BP | 0.967 | 0.964 | 0.960 | -0.007 (0.016) |
| | FA | 0.966 | 0.948 | 0.946 | -0.020 (0.002) |

- **No gain from dendrites at equal parameters.** With backprop, dend was level
  with both point nets on the conjunction task and 0.7 points worse than point-1 on
  digits. It never beat point-2 significantly (best +0.002, p = 0.56), so there was
  no "dendrite over depth" effect to separate out either.
- **Under a local rule, dendrites hurt.** With FA, dend was below point-1 on all three
  tasks. Only the digits gap (p = 0.002) survives a Bonferroni correction over the 12
  comparisons. Against point-2 the gaps were smaller, and significant only on parity
  (-0.14, p = 0.047). One extra layer of random feedback seems to cost FA more than
  the branch structure buys.
- **Parity was at chance for backprop in every arm.** This is not a code error: the
  same code solves 2- to 6-bit parity at 100%. Parity's label is uncorrelated with
  every subset of fewer than all 8 bits, so plain gradient descent gets no signal at
  small width (a known failure case, Shalev-Shwartz, Shamir & Shammah 2017).
  Deviation from the pre-registration: the first run used -1/+1 bits, and the result
  was then re-run with 0/1 bits (logged on #85). Backprop was at chance in both;
  FA reached 0.94 / 0.86 / 0.52 with -1/+1 bits.
- **Caveats.** Each branch here takes a *random* subset of inputs. Chavlis & Poirazi's
  gains come from restricted, local receptive fields, a spatial prior that this test
  leaves out on purpose. Other limits: small budgets, one k per task, tanh branches
  (monotonic, unlike the XOR-capable human branches of Gidon et al. 2020).

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
  With random branch inputs, none paid off at equal parameters (#85, above). Still
  open: whether local receptive fields per branch are what makes dendritic ANNs
  efficient, tested against a dense net with the same locality.

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
- Chavlis & Poirazi (2025) "Dendrites endow artificial neural networks with accurate, robust and parameter-efficient learning", *Nat Commun*. doi:10.1038/s41467-025-56297-9
- Jones & Kording (2020) "Can single neurons solve MNIST? The computational power of biological dendritic trees", arXiv:2009.01269
- Shalev-Shwartz, Shamir & Shammah (2017) "Failures of gradient-based deep learning", ICML. arXiv:1703.07950
- Hawkins & Ahmad (2016) "Why neurons have thousands of synapses, a theory of sequence memory in neocortex", *Front Neural Circuits* 10:23. doi:10.3389/fncir.2016.00023
