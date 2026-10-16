---
title: Dendritic computation
category: anatomy
tags: [dendrites, nmda-spikes, bac-firing, two-layer-neuron, credit-assignment, plateau-potentials, apical-dendrite, synaptic-clustering, microns]
use_cases:
  - do single neurons compute more than a weighted sum
  - what is an NMDA spike or a dendritic plateau potential
  - how could dendrites carry error signals for credit assignment
  - model a neuron with nonlinear dendritic branches
  - do inputs with similar tuning land on the same dendritic branch
status: draft
last_verified: 2026-10-16
sources:
  - https://doi.org/10.1146/annurev.neuro.28.061604.135703
  - https://doi.org/10.1016/S0896-6273(03)00149-1
  - https://doi.org/10.1038/35005094
  - https://doi.org/10.1038/18686
  - https://doi.org/10.48550/arxiv.1810.11393
  - https://doi.org/10.1038/s41467-025-56297-9
  - https://doi.org/10.1038/s41586-025-08840-3
  - https://doi.org/10.1038/nature23019
---

# Dendritic computation

## Summary
The point neuron of deep learning sums its inputs and applies one nonlinearity.
Real dendrites are not passive wires: their branches fire their own local spikes,
so a single cortical neuron behaves more like a **two-layer network** (Poirazi et
al. 2003). Where on the tree an input lands, and which inputs arrive together on
the same branch, changes the output. In mouse visual cortex, inputs from nearby parts
of visual space sit closer together on the dendrite than chance, while inputs with the
same orientation preference do not (spine imaging, and the MICrONS test below).
The separate apical dendrite of pyramidal cells may also carry a **teaching
signal**, one of the leading **hypotheses** for
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

### Do inputs with similar tuning land on the same branch?
Branch nonlinearities only matter for coding if related inputs share a branch. In vivo
spine imaging gives the established part. It measures the tuning of each spine's input,
but not which neuron that input comes from.
- **Mouse V1, orientation: not clustered.** In layer 2/3 cells, inputs with the same
  preferred orientation were spread over the whole tree, and neighbouring dendritic
  segments were tuned to different orientations (Jia et al. 2010).
- **Mouse V1, visual space: clustered at a fine scale.** Inputs that respond to similar
  features at the same place in the visual field were more likely to sit on neighbouring
  spines. Inputs from beyond the cell's receptive field sat more often on higher-order
  branches (Iacaruso, Gasler & Hofer 2017).
- **Ferret V1: clustered.** Co-tuned spines clustered on layer 2/3 dendrites. Cells with
  more clustering were more orientation selective, and branches with more co-tuned
  clusters had more local dendritic calcium events (Wilson et al. 2016). Spines less than
  10 µm apart shared similar spatial receptive fields, with no map across the whole tree
  (Scholl, Wilson & Fitzpatrick 2017).
- **Slices, layer 5.** Inputs from other layer 5 cells formed clusters of 4 to 14 synapses
  within 30 µm of basal dendrite (Gökçe, Bonhoeffer & Scheuss 2016).
- **How clusters form (partly established).** In mouse V1 before eye opening, inputs
  first appear in confined dendritic segments, and a synapse's co-activity with its
  neighbours goes with its stabilisation and potentiation (Leighton, Cheyne & Lohmann 2024). A
  plasticity model explains the species difference (orientation clusters in ferret,
  receptive-field clusters in mouse) by receptive-field size and cortical magnification.
  That is a model, not a measurement (Kirchner & Gjorgjieva 2021).

**What the MICrONS connectome showed, and what it did not.** The MICrONS cubic
millimetre of mouse visual cortex has the visual responses and the electron-microscopy
wiring of the same tissue (MICrONS Consortium 2025). In it, similarly tuned neurons
connect more often than neighbours whose axons and dendrites pass equally close, and
feature similarity, not receptive-field position, predicts synapses beyond that
proximity. Synapse size and synapse count also rise with signal correlation (Ding et al.
2025, Figs 2 and 3). Pairs joined by 4 or more synapses had a higher response correlation
(0.259 ± 0.042, n = 11 pairs) than pairs joined by one (0.118 ± 0.002, n = 5,350) (Celii et
al. 2025, Fig. 5i). A 2026 preprint found over 700,000 axon groups that repeatedly cluster
their synapses on dendritic branches of several pyramidal cells, more often than
proximity predicts, but it reports anatomy only, not the tuning of those axons (Sarup &
Boahen 2026, bioRxiv). None of the 2025 MICrONS papers (Consortium, Ding, Celii,
Schneider-Mizell, Wang) asks where on the postsynaptic dendrite co-tuned inputs land, and
a literature search on 2026-10-16 found no later paper that does. For identified
presynaptic neurons the question was open, so #87 tested it.

**MICrONS test (#87, this repo's analysis of public data, not peer reviewed).**
[`research/microns_clustering.py`](../research/microns_clustering.py) uses only public
files (materialization v1300, no login). Inputs are the 733 excitatory neurons that have
a proofread axon, a manual functional match and a well-fitted digital-twin unit (Ding et
al. 2025's thresholds). Their synapses were snapped to each target's dendrite skeleton.
22,620 excitatory targets had at least 3 distinct such inputs: 167,382 synapses, 984,396
pairs from two different input neurons. Tuning: feature similarity (cosine of the digital
twin's readout weights, Ding's best predictor of connections), receptive-field (RF) centre
distance in screen units (the screen spans 2), and orientation difference when both
inputs are tuned. Null A (from the issue): shuffle which input sits at which synapse
within each neuron, 1,000 times. Null B: shuffle only within the same primary dendrite,
which asks for clustering beyond which dendrite an input targets. One-sided p; 0.001 is
the floor. Primary test (pre-registered): feature similarity of pairs within 10 µm along
the dendrite, against null A.

| Pairs along the dendrite (n) | Feature similarity, observed / null A (p A, p B) | RF distance (p A, p B) | Orientation difference, deg (p A) |
|---|---|---|---|
| within 10 µm (7,625; 2,282 tuned) | 0.0488 / 0.0470 (0.018, 0.059) | 0.0848 / 0.0898 (≤ 0.001, ≤ 0.001) | 41.0 / 41.1 (0.39) |
| 10-20 µm (7,593) | 0.0472 / 0.0466 (0.31, 0.69) | 0.0853 / 0.0873 (≤ 0.001, 0.012) | 40.5 / 41.1 (0.16) |
| 20-50 µm (24,668) | 0.0482 / 0.0471 (0.043, 0.11) | 0.0852 / 0.0871 (≤ 0.001, ≤ 0.001) | 40.7 / 40.9 (0.35) |
| 50-100 µm (92,219) | 0.0481 / 0.0466 (≤ 0.001, 0.003) | 0.0864 / 0.0872 (≤ 0.001, ≤ 0.001) | 40.9 / 40.8 (0.66) |
| 100-200 µm (514,788) | 0.0461 / 0.0457 (≤ 0.001, ≤ 0.001) | 0.0879 / 0.0878 (0.92, 0.71) | 40.9 / 41.0 (0.16) |
| over 200 µm (337,503) | 0.0432 / 0.0444 (1.0, 1.0) | 0.0891 / 0.0887 (1.0, 1.0) | 40.4 / 40.3 (0.86) |
| same unbranched segment (33,545) | 0.0483 / 0.0472 (0.026, 0.16) | 0.0852 / 0.0879 (≤ 0.001, ≤ 0.001) | 40.9 / 40.8 (0.67) |

- **Receptive-field position: clustered.** Inputs within 10 µm of each other have RF
  centres 5.6% closer than the shuffled ones (3.5% closer than null B), and the gap
  shrinks with distance until it is gone past 100 µm. This held with at least 5 inputs
  per target (12,814 targets, p ≤ 0.001) and on the 1,412 targets with proofread dendrites
  (0.0784 vs 0.0809, p A = 0.004, p B = 0.005). It matches the mouse spine imaging above
  (Iacaruso, Gasler & Hofer 2017), now with identified presynaptic cells.
- **Orientation: not clustered,** at any distance or in any subset (within 10 µm,
  p = 0.39), as Jia et al. 2010 found in mouse.
- **What the inputs respond to: at most a tiny local excess.** The primary test passed
  (p = 0.018), but the effect is +0.0018 on a mean similarity of 0.045 (4%). It was not
  significant against null B (p = 0.059) or on proofread dendrites (p = 0.29); with 5 or
  more inputs it was p = 0.006 (null B 0.046). Pairs 50-200 µm apart are a little more
  similar and pairs over 200 µm apart (often on different dendrites) a little less, a
  coarse gradient rather than branch-level clusters.
- **Most of the RF clustering goes with where the input cells sit (exploratory, chosen
  after seeing the result).** The somata of inputs within 10 µm of each other are 174 µm
  apart against 203 µm when shuffled (p ≤ 0.001), and nearby cells have nearby RFs
  (retinotopy). Measured against the mean RF distance at each soma distance, the within-
  10 µm excess shrinks from 0.0050 to 0.0009 (p A = 0.007, p B = 0.038), was 0.0007 with 5
  or more inputs (p A = 0.029), and was absent on proofread dendrites (p = 0.68). So
  axons of neighbouring cells landing side by side explain about four fifths of the
  effect. Whether that is a wiring rule or the geometry of axons that grow together is
  not answered here (**open**).
- **Caveats.** The inputs are the cells whose axons proofreading projects chose to
  proofread, not a random sample. Tuning comes from a digital twin, not from the recorded
  responses. Most target dendrites are not proofread, and 0.7% of synapses (1,205 of
  168,892) lay more than 5 µm from the skeleton, on the soma or on a detached fragment and
  were dropped. A neuron gives many pairs, but the shuffles stay inside neurons, so the
  p-values allow for that. The tests across 12 pair classes and several tuning measures
  are not corrected; only the primary test was pre-registered. Deviations: the planned "at least 2 inputs" run was skipped, because
  with two single-synapse inputs a shuffle cannot change the pair. Where a cell matched
  several imaging units, the unit with the best model fit was used, not Ding's oracle
  score. Result table: `research/data/microns_clustering_v1300.csv`.

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
- Whether synapses carrying related features cluster on the same branch, and how
  plasticity puts them there. Partly answered for mouse visual cortex (#87, above):
  inputs with nearby receptive fields land closer together than chance, inputs with the
  same orientation do not, and feature similarity shows at most a 4% local excess. Still
  open: whether the RF clustering is a synapse-level rule or just axons of neighbouring
  cells running side by side (it mostly tracks soma distance); whether these clusters
  are big enough to fire branch spikes; and other areas, layers and inhibitory targets.
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
- Jia, Rochefort, Chen & Konnerth (2010) "Dendritic organization of sensory input to cortical neurons in vivo", *Nature* 464:1307. doi:10.1038/nature08947
- Wilson, Whitney, Scholl & Fitzpatrick (2016) "Orientation selectivity and the functional clustering of synaptic inputs in primary visual cortex", *Nat Neurosci* 19:1003. doi:10.1038/nn.4323
- Iacaruso, Gasler & Hofer (2017) "Synaptic organization of visual space in primary visual cortex", *Nature* 547:449. doi:10.1038/nature23019
- Scholl, Wilson & Fitzpatrick (2017) "Local order within global disorder: synaptic architecture of visual space", *Neuron* 96:1127. doi:10.1016/j.neuron.2017.10.017
- Gökçe, Bonhoeffer & Scheuss (2016) "Clusters of synaptic inputs on dendrites of layer 5 pyramidal cells in mouse visual cortex", *eLife* 5:e09222. doi:10.7554/eLife.09222
- Leighton, Cheyne & Lohmann (2024) "Clustered synapses develop in distinct dendritic domains in visual cortex before eye opening", *eLife* 12:RP93498. doi:10.7554/eLife.93498
- Kirchner & Gjorgjieva (2021) "Emergence of local and global synaptic organization on cortical dendrites", *Nat Commun* 12:4005. doi:10.1038/s41467-021-23557-3
- MICrONS Consortium (2025) "Functional connectomics spanning multiple areas of mouse visual cortex", *Nature* 640:435. doi:10.1038/s41586-025-08790-w
- Ding et al. (2025) "Functional connectomics reveals general wiring rule in mouse visual cortex", *Nature* 640:459. doi:10.1038/s41586-025-08840-3
- Celii et al. (2025) "NEURD offers automated proofreading and feature extraction for connectomics", *Nature* 640:487. doi:10.1038/s41586-025-08660-5
- Schneider-Mizell et al. (2025) "Inhibitory specificity from a connectomic census of mouse visual cortex", *Nature* 640:448. doi:10.1038/s41586-024-07780-8
- Wang et al. (2025) "Foundation model of neural activity predicts response to new stimulus types", *Nature* 640:470. doi:10.1038/s41586-025-08829-y
- Sarup & Boahen (2026) "Axonal ensembles repeatedly cluster and order synapses along dendrites in mouse cortex", bioRxiv (preprint, not peer reviewed). doi:10.64898/2026.03.31.715753
