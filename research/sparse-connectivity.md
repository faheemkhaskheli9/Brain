# Sparse regional connectivity: topology, event gating and computation

**Status:** separate, runnable *engineering prototype*. This is not a mapped
human connectome, a spiking/neuron simulation, a learned brain, or a
demonstration of intelligence. Brain World's backprop-free learner remains
untouched. The design extends [the structural graph](structural-connectome.md)
and accepts input packets from [the multimodal bridge](multimodal-io.md).

## Two kinds of sparsity

1. **Physical/structural:** the 78-region schematic lists exactly **142**
   region-to-region connections. Twelve are undirected and are represented
   by two traversable arcs each. Therefore the runtime stores **154 outgoing
   arcs**, compared with 78 × 77 = 6,006 potential directed non-self arcs:
   **2.5641% density**. This is a *property of the hand-authored scaffold*,
   NOT an empirical measurement of a human brain. Every missing edge is
   genuinely absent from memory, not represented as a zero in a dense
   adjacency matrix. There is one unassigned weight slot **per structural
   edge**, not per possible region pair.

2. **Dynamic/activity:** for each tick, only regions whose absolute input
   is above the configurable activation threshold are examined. For each
   such region, the runtime touches **only its outgoing adjacency list**.
   Disabled edges, zero weights and `None` (unassigned) weights transmit
   nothing. Remaining outgoing contributions must exceed a threshold,
   after which up to `max_fanout` of the strongest are sent. Default fan-out
   is 4; setting it to `None` disables the per-source activity cap.
   Fan-out gating does **not** destroy anatomical edges or learn weights.

No prespecified weight magnitude or sign is taken from diffusion MRI,
brain regions or sensory media. When all weights are `None`, input packets
are accepted but **no activity propagates and no body motion is generated**.

## Try it

```bash
python research/sparse_connectivity.py
python -m unittest discover -s research -p 'test_sparse_connectivity.py' -v
python research/sparse_connectivity_benchmark.py
```

Use from a research experiment:

```python
# not run here: import from the repository's research directory
from sparse_connectivity import make_sparse_schematic

network = make_sparse_schematic(max_fanout=4)
assert network.topology.structural_edges == 142
assert network.topology.directed_arcs == 154
assert network.step({"L_v1": 0.8}).activity == {}  # weights not trained

# Demonstrate routing ONLY: this is a manually assigned parameter, not learning.
edge = next(e for e in network.graph.connections
            if e.source == "L_v1" and e.target == "L_visual_assoc")
network.weights.set(edge.id, 0.6)
step = network.step({"L_v1": 0.8})
assert abs(step.activity["L_visual_assoc"] - 0.48) < 1e-12
assert step.stats.weighted_products == 1
```

`network.input_packets(packets)` reduces each *already validated* sensory
packet to a scalar average absolute activation per cortical target. This
is deliberately a **lossy, fixed engineering summary**, not image
understanding or text comprehension. Its result can be passed to
`network.step(...)`; text, image and video adapters themselves are not
changed. To implement a meaningful learner later, we need trained local
representations that retain important within-region information.

### Exact operation-count baseline

`research/sparse_connectivity_benchmark.py` uses 10 fixed seeds, picks
two active regions per trial, and assigns the artificial value 0.4 to
every existing graph edge. The results are deterministic and count
**visited connections, multiply operations and delivered events**:

| Quantity | Count |
|---|---:|
| Potential dense region pairs | 6,006 |
| Stored structural arcs | 154 |
| Mean examined outgoing arcs per event step (10 seeds) | 4.5 |
| Mean weighted products per step | 4.5 |
| Mean delivered events per step | 3.5 |

These are **operation counts, not wall-clock benchmarks**, energy estimates
or evidence of neural/cognitive efficiency. No parameter learning occurs.
The test `test_dense_reference_equivalence_without_gating` creates a dense
matrix solely as a mathematical oracle, checks the sparse router's output
when gates are disabled, and never uses the dense representation at runtime.
Comparing different numbers of visited arcs does not prove an improvement
in task performance. Python's sparse dictionary overhead could exceed
a vectorized dense implementation for tiny graphs.

## Adversarial review

- **Brain connectivity depends on scale.** Individual distant neurons
  connect sparsely, while *inter-area* graphs can be much denser than
  neuron-scale graphs. Our 2.56% number must never be cited as anatomical
  density. A region-level model also ignores local dense microcircuits.
- **Not every DNN is fully connected.** CNNs, attention masks and sparse
  training algorithms already exploit connectivity sparsity. See RigL.
- **Top-k gating can throw away essential information.** The gate picks
  absolute-magnitude contributions, not task importance or biological
  relevance. Run equal-budget comparisons with `max_fanout=None`,
  disconnection, shuffled links and alternative gating thresholds.
- **No weights = no useful computation.** No random artificial weights
  are silently substituted. A real learner must update separate weight
  slots and test generalization, reversal, forgetting and transfer.
- **Algorithmic scalability:** sparse storage is O(regions + edges);
  propagation examines outgoing arcs **only from active sources**.
  Candidate sorting adds O(d log d) per active source with out-degree d.
  Dense reference complexity is O(regions²). This does not establish
  lower elapsed time or power on any hardware.
- **No unearned brain claims.** Clipped scalar region-to-region messages
  omit axonal delays, excitatory/inhibitory cell types, neurotransmitters,
  dendrites, synaptic plasticity, neuron firing and physiological circuits.

## Research context

- Rosen & Halgren (2022), *PLOS Biology*: estimates of sparse **long-range
  axons** between cortical regions, with major tractography uncertainties.
  https://doi.org/10.1371/journal.pbio.3001575
- Litwin-Kumar et al. (2017), *Neuron*: optimal synaptic input degree
  depends on cell type and plasticity objective; sparsity is not
  universally superior. https://doi.org/10.1016/j.neuron.2017.01.030
- van Essen et al. (2016), review: area-level connectivity and cellular
  sparsity are distinct scales.
  https://www.ncbi.nlm.nih.gov/books/NBK435771/
- Evci et al. (2020), ICML RigL: dynamic sparse training is possible for
  ordinary deep neural networks.
  https://proceedings.mlr.press/v119/evci20a.html
