# Human-inspired structural connectome (untrained)

**Scope:** an executable, *mesoscopic/macroscopic* graph scaffold. It is **not** a human neuron-by-neuron connectome, not a faithful whole-brain simulator and not evidence that the repo has acquired intelligence. This research module is isolated from `game/world/` and its backprop-free learner.

## What is anatomy, what is a hypothesis?

- **Measured:** HCP multimodal cortical parcellation has 180 cortical areas per hemisphere. This is an anatomical *parcellation*, **not** a synapse-level connectivity map (Glasser et al., 2016).
- **Measured/inferred:** Diffusion MRI and tractography estimate undirected regional white-matter connectivity, but may have substantial false positives and negatives (Hagmann et al., 2008; Maier-Hein et al., 2017). A tractography score is **not** a synaptic efficacy.
- **Designed schematic:** The bundled model uses 39 deliberately coarse regions per hemisphere, pathways such as thalamocortical, cortico-basal-ganglia-thalamic, cortico-ponto-cerebellar and selective homotopic callosal links. Each connection is tagged `schematic-anatomical-pathway`. Selected projection direction is an abstraction, not MRI-measured direction. Relays, cell types, inhibitory signs, cortical layers, individual axons, actual geometry and many pathways are omitted. Bilaterality is simplified (especially in cerebellar circuits).
- **Unassigned:** All learning weights start `null` in a separate store, never copied from MRI streamline counts. No learning algorithm is claimed or included.

## Run

```bash
python research/structural_connectome.py --out /tmp/brain-graph.json --weights-out /tmp/brain-weights.json
python -m unittest discover -s research -p 'test_structural_connectome.py' -v
```

The schematic exports **78 regions and 142 connections** (130 directed projections, including two simplified crossed corticospinal pathways; 12 undirected commissural links). It has no measured spatial coordinates; `xyz` is `null`. JSON formats are `brain-structural-graph/1` and `brain-learning-weights/1`. To train later, use each unique connection `id` as the key for a learning parameter; the structural graph remains unchanged. Signs and magnitudes are **not** constrained by the schematic; a biologically constrained future learning layer would need cell types and neurotransmitter identities.

## Sensory cortices and motor output

The research-only sensorimotor_bridge.py adds separate visual (LGN -> V1),
auditory (MGB -> A1), somatosensory (thalamus -> S1/S2),
proprioceptive (thalamus -> S1), olfactory (bulb -> piriform),
gustatory (thalamus -> insula/operculum), vestibular (vestibular nuclei
-> thalamus -> vestibular cortical network) and internal-state (posterior
insula) ports. Channel widths are software contracts, not anatomical
cell counts. Hemisphere-specific sensory packets carry normalized values.

Motor pathways extend supplementary/premotor and primary motor cortex to
contralateral spinal circuits and spinal motor pools, with separate brainstem
motor paths. A bounded, configurable joint simulator accepts **external**
motor-pool activity and provides proprioceptive feedback. The sensorimotor bridge itself has no
neural propagation or trained input-to-motor mapping. Unassigned weights
cannot move the body; absent motor activity causes zero drive.

Run:
    python research/sensorimotor_bridge.py
    python -m unittest discover -s research -p test_sensorimotor_bridge.py -v

**Adversarial limitations:** the architecture omits actual bilateral and
decussating sensory streams, corticospinal crossing fractions, efference
copies, reflexes, neuron types, brainstem relays, delays, signal processing,
and all physiology. The abstract joint integrator is not a biomechanics
simulation. Do not count injected motor drives as learned behavior.

Before integrating a learner, preregister matched seeds and budgets, held-out
sensorimotor control and proprioception ablations; compare against
random-rewired and disconnected network controls, measure repeated
errors and retention, and record negative outcomes.

References:
- Auditory relay: https://doi.org/10.1016/j.bandl.2012.05.004
- Olfactory circuits: https://pmc.ncbi.nlm.nih.gov/articles/PMC3077578/
- Gustatory cortex: https://pubmed.ncbi.nlm.nih.gov/21305668/
- Vestibular cortex: https://doi.org/10.1152/jn.00907.2017
- Interoception: https://doi.org/10.1016/S0959-4388(03)00090-4
- Motor pathways: https://doi.org/10.1146/annurev.neuro.31.060407.125547

## Image, video and text adapters

The independent [multimodal image/video/text adapter](multimodal-io.md)
routes spatial vision, frame differences and symbolic UTF-8 packets to
the relevant simplified visual/language populations. Its output interfaces
encode externally supplied pixels, video frames and Unicode; it does not
infer new content or learn neural weights.

## Sparse event-driven activity

The optional [sparse regional router](sparse-connectivity.md) keeps this
anatomical graph as an adjacency list and processes only outgoing arcs
from active regions. It uses the same `LearningWeights` slots, initially
all unassigned; missing weights transmit no signal. The router supports
per-source activity thresholds, reversible pathway inhibition and a
configurable fan-out limit. It does not learn weights, model neurons,
perform real brain dynamics or directly control the body.

The 78-region scaffold has 142 stored connections and 154 traversable
arcs, **2.56% of its 6,006 potential directed region pairs**. This is an
engineered example, not a measurement of human cellular wiring. Cortical
area-level density must not be confused with neuron-level sparsity.

## Import an actual atlas-derived connectivity matrix

Provide two files in the same region order. `regions.csv`:

```csv
id,name,hemisphere,system,x,y,z
L_A,Example A,L,cortex,-20,20,40
L_B,Example B,L,cortex,-30,10,30
R_A,Example C,R,cortex,20,20,40
```

These **example coordinates are invented placeholders**, not measured anatomy. If real atlas coordinates are available, document their template, units and registration; otherwise leave `x,y,z` blank.

`matrix.csv` (example scalar observations; **not biological synaptic weights**):

```csv
region,L_A,L_B,R_A
L_A,0,12,0
L_B,12,0,5
R_A,0,5,0
```

```bash
python research/structural_connectome.py --matrix matrix.csv --regions regions.csv \
  --threshold 6 --provenance 'dataset DOI or HCP subject+processing pipeline' \
  --coordinate-space 'MNI152, millimeters' --out /tmp/atlas-graph.json \
  --weights-out /tmp/atlas-weights.json
```

The importer requires a **finite, symmetric, nonnegative, zero-diagonal** matrix; it retains an undirected edge only when its observed scalar exceeds the declared threshold, discarding the scalar. It **does not** pretend to recover projection direction. This importer accepts a processed matrix, not raw diffusion MRI. Users must independently verify atlas correspondence, connectome provenance, streamline-count normalization, threshold sensitivity, scan QC and data-use rights. No empirical dataset is bundled.

## Adversarial review and evaluation plan

1. **Wrong identity/units:** verify region labels and coordinate transforms against the chosen atlas. Synthetic examples are never labeled empirical.
2. **False connectivity:** repeat analyses at multiple prespecified thresholds, against an appropriate null network, across subjects; compare inter- and intra-hemisphere connection patterns. No topology accuracy claim is made here.
3. **No directionality from diffusion MRI:** reject asymmetric matrices and represent each observed edge as undirected. Do not treat functional correlation as structural evidence.
4. **No learning claims:** preregister a held-out transfer task, matched edge count, same seeds/data/optimizer, and random-rewired and fully random network controls before trying learned weights. Measure error correction, transfer, retention, cost and uncertainty. Topology alone is not an intelligence result.
5. **Engineering limits:** model omits neuron/synapse resolution, lateralized circuits, detailed cerebellar crossing, cell populations and delays. Do not integrate into Brain World's baseline until a separate controlled benchmark shows value.

## Sources

- Glasser et al. (2016), *Nature*, multimodal human cortical atlas. https://doi.org/10.1038/nature18933
- Hagmann et al. (2008), *PLoS Biology*, structural core of human cerebral cortex. https://doi.org/10.1371/journal.pbio.0060159
- Maier-Hein et al. (2017), *Nature Communications*, tractography false-positive limitations. https://doi.org/10.1038/s41467-017-01285-x
- Felleman & Van Essen (1991), *Cerebral Cortex*, primate cortical hierarchy (not human proof). https://doi.org/10.1093/cercor/1.1.1-a
- Alexander, DeLong & Strick (1986), *Annual Review of Neuroscience*, parallel basal-ganglia circuits. https://doi.org/10.1146/annurev.ne.09.030186.002041
- Takahashi & Shinoda (2021), *Neuroscience*, cerebellar cortical/nuclear circuitry. https://doi.org/10.1016/j.neuroscience.2020.07.051
