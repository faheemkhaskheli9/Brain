---
title: Innate priors and infant learning
category: function
tags: [innate, priors, inductive-bias, core-knowledge, infants, development, intuitive-physics, number-sense, genomic-bottleneck, statistical-learning, curiosity, sample-efficiency, curriculum]
use_cases:
  - what do babies know at birth or in the first months
  - what is core knowledge (Spelke)
  - how can the genome build a brain if it cannot store every synapse
  - how do infants find words in continuous speech
  - how much of human sample efficiency comes from priors versus the learning algorithm
  - which inductive biases should I build into a learner instead of learning them
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1111/j.1467-7687.2007.00569.x
  - https://doi.org/10.1038/s41467-019-11786-6
  - https://doi.org/10.1073/pnas.2409160121
  - https://doi.org/10.1126/science.274.5294.1926
  - https://doi.org/10.1126/science.aaa3799
  - https://doi.org/10.1038/s41562-022-01394-8
---

# Innate priors and infant learning

## Summary
Infants do not start as blank slates. In the first months they already expect objects
to persist and move continuously, tell large sets apart by number, treat agents as
goal-directed, and use the shape of a space to reorient: Spelke's **core knowledge**
systems. On top of that start, they are fast statistical learners and active,
curiosity-driven explorers. Zador's **genomic bottleneck** argument explains why the
start must be compressed: the genome encodes wiring and learning rules, not weights.
How much of human sample efficiency comes from these priors and how much from the
learning algorithm is an open question, and it is the one that decides what an AI
should build in versus learn.

## How it works

### Established: core knowledge systems (Spelke & Kinzler 2007)
Most of this evidence uses **violation of expectation**: infants look longer at an
event that breaks a rule they hold.

| System | Classic finding | Source |
|---|---|---|
| Objects | 5-month-olds looked longer when a screen appeared to rotate through the space occupied by a box hidden behind it; objects are expected to persist and be solid | Baillargeon, Spelke & Wasserman 1985 |
| Number | 6-month-olds told 8 dots from 16 but not 8 from 12, with area and density controlled: an approximate, ratio-limited number sense | Xu & Spelke 2000 |
| Agents | 6-month-olds encoded the goal object of a reaching hand but not of a moving rod | Woodward 1998 |
| Agents | 12-month-olds expected an agent to take the efficient path to its goal | Gergely, Nádasdy, Csibra & Bíró 1995 |
| Geometry | Young children who were disoriented searched by the room's shape and ignored a coloured wall that would have told them where to look | Hermer & Spelke 1994 |

Spelke & Kinzler (2007) argue these systems are domain-specific, present early,
shared with other animals and kept into adulthood. **Supported, not settled:** that
infants show the behaviour is established; whether it is innate or learned very fast
in the first months, and how rich a meaning looking time carries, are debated (Haith
1998). Controlled-rearing studies get closer to "innate": newborn chicks shown a single
virtual object in their first week recognised it from new viewpoints (Wood 2013).

### Argument: the genomic bottleneck (Zador 2019)
The genome is far too small to list every synapse of a brain (the numbers are in
[[brain-development-and-critical-periods]]). Zador (2019) argued that evolution
therefore stores compact **wiring rules and learning rules**, and that much animal
behaviour is mostly innate and only tuned by experience. Shuvaev, Lachi, Koulakov &
Zador (2024) turned this into a method: a small "genomic" network generates the weights
of a larger one from neuron labels. Standard networks could be compressed this way by
several orders of magnitude while keeping much of their performance, and for complex
tasks the compressed network transferred better to new tasks. The bottleneck acts as a
regulariser. The argument is a framing; the 2024 result shows it can work in artificial
networks, not that the brain does it this way.

### Established: statistical learning
Saffran, Aslin & Newport (1996) played 8-month-olds a continuous, monotone stream of
four made-up three-syllable words, with no pauses or stress cues. After 2 minutes the
infants listened differently to the words than to "part-words" spanning a word
boundary. The only cue was **transitional probability**, how likely one syllable is to
follow another, which is higher inside words than across their edges. The same learning
works for sequences of visual shapes in 2- to 8-month-olds (Kirkham, Slemmer & Johnson
2002), so it is not specific to speech. The code below segments such a stream.

### Supported: curiosity and active exploration
- **Goldilocks attention.** 7- and 8-month-olds were most likely to look away from
  visual sequences that an ideal-learner model rated as very predictable or very
  unpredictable (Kidd, Piantadosi & Aslin 2012): attention goes to what can be learned.
- **Surprise drives learning.** 11-month-olds who saw an object break a core-knowledge
  rule (pass through a wall, hang unsupported) learned a new fact about that object
  better, explored it more, and tested the violated property, for example banging an
  object that had passed through a wall (Stahl & Feigenson 2015).
Priors and learning interact here: core knowledge sets the predictions, and the
violations decide where the infant looks and learns next ([[predictive-processing]]).

### Open: priors versus the learning algorithm
- **Priors side.** People learn new concepts from a few examples because they bring
  intuitive physics, intuitive psychology and compositional structure; Lake, Ullman,
  Tenenbaum & Gershman (2017) argue machines need these built in.
- **Data side.** A fairly generic network trained on 61 hours of head-camera video and
  speech from one child, aged 6 to 25 months, learned many word-referent mappings
  (Vong, Wang, Orhan & Lake 2024). That data is a small slice of what the child heard.
- **Both.** An object-centric model (PLATO) learned infant-style physical concepts from
  video and did markedly better than the same kind of model without object-level
  representations (Piloto, Weinstein, Battaglia & Botvinick 2022): a built-in structure
  plus learning, not one or the other.
No study yet splits human sample efficiency into a "prior" share and an "algorithm"
share. **Open question.**

## Relevance to building brain-like AI
| Brain | AI counterpart |
|---|---|
| Core knowledge of objects | Object-centric representations (PLATO); slot-based perception |
| Innate visual machinery | Architectural inductive biases: convolution gives translation equivariance; an untrained CNN already acts as an image prior (Ulyanov, Vedaldi & Lempitsky 2018) |
| Genomic bottleneck | Generate weights from a small network or rule; search architectures that work before training (weight-agnostic networks; Gaier & Ha 2019) |
| Statistical learning | Self-supervised next-token or next-frame prediction |
| Curiosity, Goldilocks attention | Intrinsic reward from prediction error (Pathak et al. 2017), with care to avoid unlearnable noise |
| Developmental schedule | Curriculum learning: start simple (Elman 1993; Bengio et al. 2009) |

Practical rule: build in what is cheap to state and stable across tasks (objects,
space, number, agents), learn the rest, and measure the prior's effect with an
ablation rather than assuming it ([[efficient-brain-like-learning]]).

## Code
A transitional-probability word segmenter in the style of Saffran et al. (1996). The
stream has no pauses; the learner counts syllable pairs, computes TP(x -> y) =
count(xy) / count(x), and puts a boundary at each local TP minimum. With words in random
order and no immediate repeats, TP is 1.0 inside a word and about 1/3 across a boundary.

```python
import numpy as np

rng = np.random.default_rng(0)

# Four made-up three-syllable words, in the style of Saffran et al. (1996).
words = [("tu", "pi", "ro"), ("go", "la", "bu"), ("bi", "da", "ku"), ("pa", "do", "ti")]

# A continuous stream: words in random order, never the same word twice in a row,
# with no pauses or stress cues. Only syllable statistics mark the boundaries.
order, prev = [], -1
for _ in range(180):
    w = rng.choice([i for i in range(len(words)) if i != prev])
    order.append(w)
    prev = w
stream = [syl for w in order for syl in words[w]]

# Transitional probability TP(x -> y) = count(xy) / count(x).
sylls = sorted(set(stream))
idx = {s: i for i, s in enumerate(sylls)}
pair = np.zeros((len(sylls), len(sylls)))
for x, y in zip(stream, stream[1:]):
    pair[idx[x], idx[y]] += 1
tp = pair / pair.sum(1, keepdims=True)
tps = np.array([tp[idx[x], idx[y]] for x, y in zip(stream, stream[1:])])

# Segment: put a boundary wherever TP is a local minimum (lower than both neighbours).
cuts = [i + 1 for i in range(1, len(tps) - 1) if tps[i] < tps[i - 1] and tps[i] < tps[i + 1]]
pieces = [tuple(stream[a:b]) for a, b in zip([0] + cuts, cuts + [len(stream)])]
found = {p for p in pieces if pieces.count(p) >= 5}

within = [tp[idx[w[i]], idx[w[i + 1]]] for w in words for i in range(2)]
across = [tp[idx[a[-1]], idx[b[0]]] for a in words for b in words if a != b]
print("segmented lexicon:", sorted(" ".join(p) for p in found))
print(f"TP inside words {min(within):.2f}, across boundaries {np.mean(across):.2f}")
assert found == set(words)                    # all four words, nothing else
assert min(within) == 1.0 and max(across) < 0.6
```

## Open questions
- How much of human sample efficiency is prior and how much algorithm, and whether the
  answer differs by domain (physics, language, social reasoning).
- Which core-knowledge behaviours are present at birth and which are learned in the
  first weeks; what the genome actually specifies to produce them.
- Whether infant statistical learning scales from syllable pairs to grammar, or needs
  further built-in structure ([[language-and-llms]]).
- Which intrinsic-motivation signal infants use: prediction error, learning progress,
  or information gain.

## Related
- [[brain-development-and-critical-periods]] - wiring, pruning, critical periods and the genome numbers.
- [[brain-vs-deep-learning]] - innate structure versus learning from scratch.
- [[efficient-brain-like-learning]] - built-in priors as one of the sample-efficiency methods.
- [[predictive-processing]] - prediction error as the signal that drives looking and learning.
- [[language-and-llms]] - how far statistical learning goes towards language.
- [[sensory-systems-and-vision]] - the visual machinery that newborn object recognition relies on.
- [[prefrontal-cortex-and-abstraction]] - schemas: prior knowledge that speeds up new learning.
- [[social-cognition-and-theory-of-mind]] - false-belief tasks and learning by watching others.

## References
- Spelke & Kinzler (2007) "Core knowledge", *Dev Sci* 10:89. doi:10.1111/j.1467-7687.2007.00569.x
- Baillargeon, Spelke & Wasserman (1985) "Object permanence in five-month-old infants", *Cognition* 20:191. doi:10.1016/0010-0277(85)90008-3
- Xu & Spelke (2000) "Large number discrimination in 6-month-old infants", *Cognition* 74:B1. doi:10.1016/S0010-0277(99)00066-9
- Woodward (1998) "Infants selectively encode the goal object of an actor's reach", *Cognition* 69:1. doi:10.1016/S0010-0277(98)00058-4
- Gergely, Nádasdy, Csibra & Bíró (1995) "Taking the intentional stance at 12 months of age", *Cognition* 56:165. doi:10.1016/0010-0277(95)00661-H
- Hermer & Spelke (1994) "A geometric process for spatial reorientation in young children", *Nature* 370:57. doi:10.1038/370057a0
- Haith (1998) "Who put the cog in infant cognition? Is rich interpretation too costly?", *Infant Behav Dev* 21:167.
- Wood (2013) "Newborn chickens generate invariant object representations at the onset of visual object experience", *PNAS* 110:14000. doi:10.1073/pnas.1308246110
- Zador (2019) "A critique of pure learning and what artificial neural networks can learn from animal brains", *Nat Commun* 10:3770. doi:10.1038/s41467-019-11786-6
- Shuvaev, Lachi, Koulakov & Zador (2024) "Encoding innate ability through a genomic bottleneck", *PNAS*. doi:10.1073/pnas.2409160121
- Saffran, Aslin & Newport (1996) "Statistical learning by 8-month-old infants", *Science* 274:1926. doi:10.1126/science.274.5294.1926
- Kirkham, Slemmer & Johnson (2002) "Visual statistical learning in infancy: evidence for a domain general learning mechanism", *Cognition* 83:B35. doi:10.1016/S0010-0277(02)00004-5
- Kidd, Piantadosi & Aslin (2012) "The Goldilocks effect: human infants allocate attention to visual sequences that are neither too simple nor too complex", *PLoS ONE* 7:e36399. doi:10.1371/journal.pone.0036399
- Stahl & Feigenson (2015) "Observing the unexpected enhances infants' learning and exploration", *Science* 348:91. doi:10.1126/science.aaa3799
- Lake, Ullman, Tenenbaum & Gershman (2017) "Building machines that learn and think like people", *Behav Brain Sci* 40:e253. doi:10.1017/S0140525X16001837
- Vong, Wang, Orhan & Lake (2024) "Grounded language acquisition through the eyes and ears of a single child", *Science* 383:504. doi:10.1126/science.adi1374
- Piloto, Weinstein, Battaglia & Botvinick (2022) "Intuitive physics learning in a deep-learning model inspired by developmental psychology", *Nat Hum Behav*. doi:10.1038/s41562-022-01394-8
- Ulyanov, Vedaldi & Lempitsky (2018) "Deep image prior", *CVPR*. https://arxiv.org/abs/1711.10925
- Gaier & Ha (2019) "Weight agnostic neural networks", *NeurIPS*. https://arxiv.org/abs/1906.04358
- Pathak, Agrawal, Efros & Darrell (2017) "Curiosity-driven exploration by self-supervised prediction", *ICML*. https://arxiv.org/abs/1705.05363
- Elman (1993) "Learning and development in neural networks: the importance of starting small", *Cognition* 48:71. doi:10.1016/0010-0277(93)90058-4
- Bengio, Louradour, Collobert & Weston (2009) "Curriculum learning", *ICML*. doi:10.1145/1553374.1553380
