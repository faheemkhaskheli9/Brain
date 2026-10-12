---
title: Hyperdimensional computing and vector-symbolic architectures
category: learning
tags: [hyperdimensional-computing, vector-symbolic-architecture, vsa, hdc, holographic-reduced-representations, binding, bundling, permutation, sparse-distributed-memory, binding-problem, cerebellum, attention]
use_cases:
  - how can a brain-like system store a structured record like {country: Mexico, currency: peso}
  - what is hyperdimensional computing and how do binding and bundling work
  - how could neurons solve the binding problem of roles and fillers
  - how is Kanerva's sparse distributed memory related to the cerebellum and to transformer attention
  - answer "what is the dollar of Mexico?" with vector arithmetic
status: draft
last_verified: 2026-10-11
sources:
  - doi:10.1007/s12559-009-9009-8
  - doi:10.1109/72.377968
  - doi:10.1145/3538531
  - https://arxiv.org/abs/cs/0412059
  - https://arxiv.org/abs/2111.05498
  - doi:10.1126/science.1225266
---

# Hyperdimensional computing and vector-symbolic architectures

## Summary
Hyperdimensional computing (HDC), also called a vector-symbolic architecture (VSA),
represents every item, role and structure as one very long random vector, often
10,000 dimensions (Kanerva 2009). Three operations do all the work: **binding** ties
a role to a filler, **bundling** superposes several items into one vector, and
**permutation** marks order. The result is a symbol system made of distributed
patterns. It degrades gracefully with noise and is a candidate answer to how
neurons could represent "who did what to whom". The maths is **established**; the
claim that the brain computes this way is a **hypothesis**.

## How it works

### Why high dimensions (established, mathematics)
Two random bipolar vectors (entries +1 or -1) of length D have a cosine similarity
near 0, with a spread of about 1/sqrt(D): 0.01 for D = 10,000. So a space this large
holds a huge number of nearly orthogonal vectors, and a vector corrupted by a lot of
noise is still far closer to its original than to anything else (Kanerva 2009).
That is why a stored item can be recovered from a noisy, superposed query by
comparing it against an **item memory** of known vectors ("clean-up").

### The three operations
| Operation | What it does | Common forms | Result is similar to its inputs? |
|---|---|---|---|
| **Binding** (`a ⊗ b`) | Ties a role to a filler, e.g. `currency ⊗ peso` | XOR of binary vectors (binary spatter codes); elementwise multiply of bipolar vectors (MAP, Gayler 2003); circular convolution of real vectors (HRR, Plate 1995) | No: dissimilar to both, so pairs do not interfere |
| **Bundling** (`a + b + c`) | Superposes a set into one vector | Elementwise sum, then majority vote or sign | Yes: similar to each member |
| **Permutation** (`ρ(a)`) | Marks position or order, e.g. a sequence `ρ²(a) + ρ(b) + c` | A fixed shuffle or cyclic shift of the coordinates | No |

Binding is invertible: with XOR or bipolar multiply, binding is its own inverse, so
`(currency ⊗ peso) ⊗ currency = peso`. Plate's **holographic reduced representations**
(HRR) bind real-valued vectors by circular convolution and unbind with an approximate
inverse (circular correlation), so the answer is noisy and needs clean-up (Plate 1995).
Kleyko et al. (2022) survey the model families and compare them.

### Records and analogy: "what is the dollar of Mexico?" (established, Kanerva 2010)
A record is a bundle of role-filler bindings:
`USA = country⊗usa + capital⊗washington + currency⊗dollar`, and the same for MEX.
Unbinding a role reads a field: `MEX ⊗ currency ≈ peso`. More striking, binding the
two records, `USA ⊗ MEX`, gives a vector that maps each USA filler to its Mexican
counterpart. Binding `dollar` with it gives a noisy `peso`, without ever naming the
role "currency" (Kanerva 2010). That trick needs a self-inverse binding such as XOR or
bipolar multiply. The code below runs it.

### Sparse distributed memory (established model; brain mapping is supported)
Kanerva's **sparse distributed memory** (SDM, 1988) stores long binary words at a
fixed set of random "hard locations". A write updates counters at every location
within a set Hamming distance of the address; a read sums those counters and
thresholds them. Recall is content-addressable and tolerates noisy cues. Kanerva
pointed out its resemblance to cerebellar cortex: many granule cells act as address
decoders and Purkinje cells read out the stored data, close to the Marr (1969) and
Albus (1971) theory of the cerebellum as a pattern recogniser over an expanded code
([[action-selection-and-motor-control]]). The mapping is **supported** by the anatomy,
not shown cell by cell.

A related random expansion appears in the fly: the olfactory circuit projects odour
inputs into many Kenyon cells and keeps only the most active ones, a variant of
locality-sensitive hashing (Dasgupta, Stevens & Navlakha 2017).

### Link to attention (supported)
Bricken & Pehlevan (2021) show that the transformer attention update closely
approximates an SDM read under certain data conditions, and that pre-trained GPT-2
models meet those conditions. The softmax over query-key similarities plays the
role of the Hamming-radius neighbourhood ([[attention-and-working-memory]],
[[language-and-llms]]).

### The binding problem (open question)
The brain must keep track of which features belong together ("red square, blue
circle") and which filler fills which role ("dog bites man" vs "man bites dog")
(Treisman 1996). Proposed answers:
- **Synchrony.** Neurons coding the same object fire in phase (Singer & Gray 1995).
  **Supported but debated** ([[brain-rhythms-and-oscillations]]).
- **Conjunctive codes.** A dedicated unit per combination. Established for some
  features, but the number of combinations explodes.
- **Vector binding.** A VSA binds with a fixed-width operation, so structure does not
  explode the code size. Gayler (2003) argues VSAs meet Jackendoff's challenges for a
  neural account of language. Spaun, a 2.5-million-neuron spiking model, implements
  circular-convolution binding in spiking neurons and performs eight tasks
  (Eliasmith et al. 2012). That the cortex does this is a **hypothesis**.

## Relevance to building brain-like AI
- **Structured memory without backprop.** One-shot writes (bind and add) and reads
  (unbind and clean up) give a symbolic store that a learner can use alongside slow
  weight learning ([[memory-systems]]).
- **Compositional generalisation.** Roles and fillers are separate vectors, so a new
  filler slots into an old role at no cost: the substrate for analogy.
- **Cheap, robust hardware.** Operations are elementwise and tolerate bit errors,
  which suits low-precision and neuromorphic chips ([[neuromorphic-hardware]]).
- **Limits.** Capacity is finite: a bundle of too many items blurs, and HDC has no
  built-in way to learn good item vectors. Most systems pair it with a learned
  encoder.

## Code
Encode two country records by binding and bundling, read a field back, and answer
"what is the dollar of Mexico?" by mapping one record onto the other.

```python
import numpy as np

rng = np.random.default_rng(0)
D = 10_000                                  # dimensions


def hv():                                   # random bipolar hypervector
    return rng.choice([-1, 1], size=D)


def bind(a, b):                             # elementwise multiply: self-inverse
    return a * b


def bundle(*vs):                            # majority vote (odd count, no ties)
    return np.sign(np.sum(vs, axis=0))


def cos(a, b):
    return a @ b / D


names = ["country", "capital", "currency", "usa", "mexico",
         "washington", "mexico_city", "dollar", "peso"]
item = {n: hv() for n in names}             # item (clean-up) memory

# Random vectors are nearly orthogonal: cosine about 0 +- 1/sqrt(D) = 0.01
sims = [abs(cos(item[a], item[b])) for a in names for b in names if a < b]
assert max(sims) < 0.05, max(sims)

# A record is a bundle of role*filler pairs
usa = bundle(bind(item["country"], item["usa"]),
             bind(item["capital"], item["washington"]),
             bind(item["currency"], item["dollar"]))
mex = bundle(bind(item["country"], item["mexico"]),
             bind(item["capital"], item["mexico_city"]),
             bind(item["currency"], item["peso"]))


def cleanup(q):                             # nearest stored item
    return max(names, key=lambda n: cos(q, item[n]))


# 1. Query a field: unbind the role, then clean up
assert cleanup(bind(mex, item["currency"])) == "peso"
assert cleanup(bind(usa, item["capital"])) == "washington"

# 2. "What is the dollar of Mexico?" without naming the role:
#    map USA -> Mexico, then apply the map to "dollar"
mapping = bind(usa, mex)
answer = bind(item["dollar"], mapping)
assert cleanup(answer) == "peso"
s = cos(answer, item["peso"])
assert s > 0.15 and all(cos(answer, item[n]) < 0.05 for n in names if n != "peso")
print(f"dollar of Mexico -> {cleanup(answer)} (cosine {s:.2f})")
```

The answer has cosine about 0.25 with `peso` and near 0 with everything else: noisy,
but unambiguous after clean-up. Across seeds 0-9 it ranged 0.23-0.27.

## Open questions
- Do cortical populations implement anything like binding by multiplication or
  convolution? Dendritic nonlinearities could multiply ([[dendritic-computation]]),
  but no recording has shown a role-filler binding code.
- How are item vectors learned rather than drawn at random, and how does the brain
  keep them stable while learning ([[learning-and-plasticity]])?
- Is the SDM-cerebellum correspondence more than an analogy? It predicts specific
  granule-cell sparsity and readout rules that could be tested.
- How many bindings can a bundle hold in a spiking network with realistic noise,
  compared with working-memory limits?

## Related
- [[neural-coding-and-computation]] - distributed and sparse codes, the substrate HDC assumes.
- [[memory-systems]] - associative memory; SDM as a content-addressable store.
- [[action-selection-and-motor-control]] - the cerebellum, whose wiring resembles SDM.
- [[attention-and-working-memory]] - attention as an SDM read; holding bound items.
- [[brain-rhythms-and-oscillations]] - binding by synchrony, the main rival proposal.
- [[dendritic-computation]] - single neurons that could multiply inputs.
- [[neuromorphic-hardware]] - hardware that suits elementwise, noise-tolerant operations.
- [[language-and-llms]] - roles, fillers and transformer attention.
- [[cognitive-architectures]] - symbolic and semantic-pointer architectures built on VSAs.
- [[reservoir-computing]] - another fixed random high-dimensional expansion.

## References
- Kanerva (2009) "Hyperdimensional computing: an introduction to computing in distributed representation with high-dimensional random vectors", *Cognitive Computation* 1:139. doi:10.1007/s12559-009-9009-8
- Kanerva (2010) "What we mean when we say 'What's the dollar of Mexico?': prototypes and mapping in concept space", AAAI Fall Symposium: Quantum Informatics for Cognitive, Social, and Semantic Processes, pp. 2-6.
- Kanerva, *Sparse Distributed Memory* (MIT Press, 1988).
- Plate (1995) "Holographic reduced representations", *IEEE Trans Neural Networks* 6:623. doi:10.1109/72.377968
- Gayler (2003) "Vector symbolic architectures answer Jackendoff's challenges for cognitive neuroscience", ICCS/ASCS joint conference. arXiv:cs/0412059
- Kleyko, Rachkovskij, Osipov & Rahimi (2022) "A survey on hyperdimensional computing aka vector symbolic architectures, Part I: models and data transformations", *ACM Computing Surveys* 55(6):1-40. doi:10.1145/3538531
- Bricken & Pehlevan (2021) "Attention approximates sparse distributed memory", NeurIPS 2021. arXiv:2111.05498
- Marr (1969) "A theory of cerebellar cortex", *J Physiol* 202:437. doi:10.1113/jphysiol.1969.sp008820
- Albus (1971) "A theory of cerebellar function", *Math Biosci* 10:25. doi:10.1016/0025-5564(71)90051-4
- Dasgupta, Stevens & Navlakha (2017) "A neural algorithm for a fundamental computing problem", *Science* 358:793. doi:10.1126/science.aam9868
- Treisman (1996) "The binding problem", *Curr Opin Neurobiol* 6:171. doi:10.1016/S0959-4388(96)80070-5
- Singer & Gray (1995) "Visual feature integration and the temporal correlation hypothesis", *Annu Rev Neurosci* 18:555. doi:10.1146/annurev.ne.18.030195.003011
- Eliasmith et al. (2012) "A large-scale model of the functioning brain", *Science* 338:1202. doi:10.1126/science.1225266
