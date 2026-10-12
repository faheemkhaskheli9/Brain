---
title: Prefrontal cortex, abstraction and generalisation
category: function
tags: [prefrontal-cortex, pfc, rules, task-sets, cognitive-control, mixed-selectivity, abstraction, schemas, compositionality, analogy, cognitive-map, generalisation]
use_cases:
  - what does the prefrontal cortex do
  - how does the brain represent rules and switch between tasks
  - what is mixed selectivity and why does it matter
  - why do new facts that fit what I already know get learned faster
  - how does the brain generalise and abstract, and what is still unknown
  - give my learner a representation that supports both flexible rules and transfer
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1146/annurev.neuro.24.1.167
  - https://doi.org/10.1038/nature12160
  - https://doi.org/10.1016/j.cell.2020.09.031
  - https://doi.org/10.1126/science.1135935
  - https://doi.org/10.1016/j.neuron.2018.10.002
  - https://doi.org/10.1038/s41586-023-06668-3
---

# Prefrontal cortex, abstraction and generalisation

## Summary
The **prefrontal cortex (PFC)**, the front of the frontal lobe, holds the current
goal, rule or task and uses it to steer the rest of the brain. Its neurons encode
abstract rules, and many respond to *combinations* of task variables (**mixed
selectivity**), which lets a simple readout implement many different rules. Abstraction
shows up as a measurable geometry in PFC and hippocampal activity, and prior knowledge
organised as **schemas** lets new, fitting facts be stored fast. These are established
findings. How the brain *learns* abstractions and composes them into new combinations
is not explained by any known learning rule: that gap is the one
[[build-a-brain-like-learner]] lists under "Honest limits".

## How it works

### Established: what PFC does
- **Rules and task sets.** Patients with frontal lesions keep sorting cards by an old
  rule after it has changed (perseveration on the Wisconsin Card Sorting Test; Milner
  1963). In monkeys trained to apply a "same" or "different" rule, many lateral PFC
  neurons fired according to the rule in force, whichever sensory cue signalled it
  (Wallis, Anderson & Miller 2001).
- **Cognitive control (framework, widely accepted).** Miller & Cohen (2001) proposed
  that PFC keeps goals and rules as patterns of sustained activity, and these bias
  processing in sensory, memory and motor areas towards what the task needs. Holding
  and gating those patterns is covered in [[attention-and-working-memory]].
- **Context-dependent routing.** Monkeys judged either the colour or the motion of the
  same dots, cued by context. PFC received both features on every trial; the context
  changed the network's recurrent dynamics so that only the relevant feature was
  integrated towards a choice (Mante, Sussillo, Shenoy & Newsome 2013). The data are
  established; the recurrent-network account is a model fitted to them.

### Established: mixed selectivity
In a monkey sequence-memory task, many PFC neurons did not respond to one variable
alone but to nonlinear mixtures (this object *at this position* *in this task*).
Rigotti et al. (2013) showed that these mixtures make the population code
high-dimensional, so a linear readout can compute many different functions of the
variables, including XOR-like rules that pure single-variable codes cannot support.
The dimensionality fell on error trials, linking it to behaviour. The code below shows
the XOR case.

### Supported: the geometry of abstraction
High dimensionality buys flexibility but not generalisation: a code that separates
everything treats every new situation as new. Bernardi et al. (2020) recorded PFC and
hippocampus in monkeys and defined a variable as **abstract** when a decoder trained on
some conditions works on conditions it never saw (cross-condition generalisation).
Some variables, including a hidden context, were represented in this abstract format
while the code stayed high-dimensional enough to decode many others. The same geometry
appeared in trained networks. That one code supports both readouts is the finding; how
widely it holds beyond these tasks is open.

### Established finding, debated mechanism: schemas
A **schema** is an organised body of prior knowledge that new information can be fitted
into. Rats first learned six flavour-place pairs in an arena over weeks. They then
learned two new pairs in a single trial, and removing the hippocampus 48 hours later
spared those memories, while a lesion 3 hours after learning abolished them (Tse et al.
2007). Consolidation that usually takes weeks happened in about two days because the
new pairs fitted the schema. Follow-up work found a strong rise in immediate-early gene
expression in prelimbic medial PFC during this learning, and blocking that area
prevented both new learning and recall (Tse et al. 2011).
- Rudy & Sutherland (2008) argued the fast independence could instead reflect
  disruption outside the hippocampus caused by the lesions; Tse and colleagues disputed
  this.
- This bends [[memory-systems]]' complementary learning systems story, in which cortex
  learns slowly to avoid interference. McClelland (2013) showed that a slow cortical
  network can take in schema-*consistent* items quickly without interference, because
  they need little change to existing weights.
- **Hypothesis (SLIMM; van Kesteren et al. 2012):** medial PFC supports encoding of
  schema-congruent information and the medial temporal lobe that of novel information.

### Supported: cognitive maps for abstract spaces
Behrens et al. (2018) argued that the hippocampal-entorhinal system, known for place and
grid cells, organises *any* structured knowledge as a map: relations between concepts,
social hierarchies, task states. The evidence (grid-like signals in a 2D space of bird
shapes; models such as the Tolman-Eichenbaum Machine that factor structure from content)
is in [[spatial-navigation]]. The reusable part, "how things relate", is what transfers
to a new task, and is one concrete proposal for what an abstraction *is*.

### Open: abstraction, analogy and composition
- **Analogy** maps relational structure from one domain to another (an atom is like a
  solar system), ignoring surface features (Gentner 1983's structure-mapping theory).
- **Compositionality**: people who learn "dax" and "twice" understand "dax twice"
  (systematic generalisation). Fodor & Pylyshyn (1988) argued neural networks cannot
  do this. Standard sequence-to-sequence networks indeed failed on such splits (Lake &
  Baroni 2018), but a network meta-trained on many composition tasks matched human
  systematic generalisation (Lake & Baroni 2023).
- **Meta-learning in PFC.** A recurrent PFC-like network trained by dopamine-driven RL
  learns its own fast learning algorithm (Wang et al. 2018), and networks trained on
  many tasks reuse shared, compositional task representations (Yang et al. 2019).
  Both are covered in [[one-brain-many-tasks]].

### What is known vs hypothesis
| Claim | Status |
|---|---|
| PFC lesions impair rule switching; PFC neurons encode abstract rules | Established |
| PFC codes are mixed-selective and high-dimensional; dimensionality tracks performance | Established (Rigotti 2013) |
| The same population carries abstract (generalising) variables | Supported (Bernardi 2020) |
| Schema-consistent memories consolidate fast | Established finding, mechanism debated |
| The hippocampal-entorhinal map is a general format for abstract knowledge | Supported, hypothesis in its general form |
| A specific synaptic learning rule produces abstraction and composition | **Unknown.** Models get them from backprop, meta-learning or scale, not from a known brain rule |

## Relevance to building brain-like AI
- **Random nonlinear expansion is cheap flexibility.** A fixed random layer with a
  threshold gives a linear learner access to conjunctions (the same idea as reservoir
  computing and the random expansion in [[build-a-brain-like-learner]]).
- **Context as an input that reshapes dynamics**, not a separate network per task,
  matches Mante et al. and is how task-conditioned networks work.
- **Train for generalisation geometry, not only accuracy.** Cross-condition
  generalisation is a cheap test: train a probe on half the conditions, test on the
  rest. Use it alongside [[evaluating-brain-models]].
- **Schema-aware memory.** Check how well a new item fits what the model already
  predicts. Fitting items can go straight into slow weights; surprising ones go to a
  fast episodic store and replay ([[memory-systems]], [[sleep-and-memory-consolidation]]).
- **Factor structure from content** (TEM) is a concrete design for transfer.
- Be honest about the limit: no brain-derived rule here yields compositional reasoning;
  current systems get it from meta-learning or scale ([[language-and-llms]]).

## Code
Two task variables (context, stimulus) and an XOR rule: the context flips which stimulus
means "go". Pure-selective neurons give a 2-dimensional code that no linear readout can
solve; random mixed-selective neurons give a 3-dimensional code that a linear readout
solves (Rigotti et al. 2013).

```python
import numpy as np

rng = np.random.default_rng(0)

# Two binary task variables: context (rule A or B) and stimulus (left or right).
# The correct response is their XOR: the rule flips which stimulus means "go".
conds = np.array([[c, s] for c in (0, 1) for s in (0, 1)], dtype=float)
target = np.logical_xor(conds[:, 0], conds[:, 1]).astype(float)
N = 100

# Pure selectivity: each neuron is tuned linearly to ONE variable.
which = rng.integers(0, 2, N)
W_pure = np.zeros((2, N))
W_pure[which, np.arange(N)] = rng.normal(size=N)
def pure(X):
    return X @ W_pure

# Nonlinear mixed selectivity: each neuron sums BOTH variables, then thresholds.
W_mix, b_mix = rng.normal(size=(2, N)), rng.normal(size=N)
def mixed(X):
    return np.maximum(0.0, (2 * X - 1) @ W_mix + b_mix)

def readout_accuracy(pop, n=50, noise=0.3):
    X, y = np.repeat(conds, n, axis=0), np.repeat(target, n)
    def noisy():
        R = pop(X) + noise * rng.normal(size=(len(X), N))
        return np.c_[R, np.ones(len(X))]
    w, *_ = np.linalg.lstsq(noisy(), 2 * y - 1, rcond=None)  # train a linear readout
    return ((noisy() @ w > 0) == y).mean()                    # test on fresh noise

def dimensionality(pop):
    M = pop(conds)                     # 4 condition means x N neurons
    return np.linalg.matrix_rank(M - M.mean(0), tol=1e-6)

acc_pure, acc_mix = readout_accuracy(pure), readout_accuracy(mixed)
d_pure, d_mix = dimensionality(pure), dimensionality(mixed)
print(f"XOR readout accuracy: pure {acc_pure:.2f}, mixed {acc_mix:.2f}")
print(f"dimensionality of the 4 condition means: pure {d_pure}, mixed {d_mix}")
assert acc_pure < 0.8 and acc_mix > 0.95   # a linear readout gets at most 3 of 4 XOR cells from pure codes
assert d_pure == 2 and d_mix == 3
```

## Open questions
- Which learning rule, if any, turns experience into abstract, transferable
  representations in cortex without backpropagation ([[brain-vs-deep-learning]]).
- Whether brains compose representations symbolically, with a neural binding
  mechanism, or approximate composition with learned high-dimensional geometry.
- What a schema is physically: a set of cortical weights, a hippocampal-entorhinal map,
  or a PFC-held task state, and how fast schema learning works at the synapse.
- Whether the trade-off between high dimensionality (flexibility) and abstract geometry
  (generalisation) is tuned by learning, by neuromodulators, or by task demands.

## Related
- [[attention-and-working-memory]] - how PFC holds and gates the rule it applies.
- [[one-brain-many-tasks]] - meta-RL in PFC (Wang 2018) and multi-task networks (Yang 2019).
- [[memory-systems]] - complementary learning systems, which schemas modify.
- [[sleep-and-memory-consolidation]] - the consolidation schemas speed up.
- [[spatial-navigation]] - cognitive maps, grid codes for abstract spaces, TEM.
- [[neural-coding-and-computation]] - population codes and their dimensionality.
- [[build-a-brain-like-learner]] - the "Honest limits" this topic expands on.
- [[language-and-llms]] - compositional generalisation in language models.

## References
- Milner (1963) "Effects of different brain lesions on card sorting", *Arch Neurol* 9:90. doi:10.1001/archneur.1963.00460070100010
- Wallis, Anderson & Miller (2001) "Single neurons in prefrontal cortex encode abstract rules", *Nature* 411:953. doi:10.1038/35082081
- Miller & Cohen (2001) "An integrative theory of prefrontal cortex function", *Annu Rev Neurosci* 24:167. doi:10.1146/annurev.neuro.24.1.167
- Mante, Sussillo, Shenoy & Newsome (2013) "Context-dependent computation by recurrent dynamics in prefrontal cortex", *Nature* 503:78. doi:10.1038/nature12742
- Rigotti, Barak, Warden, Wang, Daw, Miller & Fusi (2013) "The importance of mixed selectivity in complex cognitive tasks", *Nature* 497:585. doi:10.1038/nature12160
- Bernardi, Benna, Rigotti, Munuera, Fusi & Salzman (2020) "The geometry of abstraction in the hippocampus and prefrontal cortex", *Cell* 183:954. doi:10.1016/j.cell.2020.09.031
- Tse et al. (2007) "Schemas and memory consolidation", *Science* 316:76. doi:10.1126/science.1135935
- Tse et al. (2011) "Schema-dependent gene activation and memory encoding in neocortex", *Science* 333:891. doi:10.1126/science.1205274
- Rudy & Sutherland (2008) "Is it systems or cellular consolidation? Time will tell. An alternative interpretation of the Morris group's recent Science paper", *Neurobiol Learn Mem* 89:361.
- McClelland (2013) "Incorporating rapid neocortical learning of new schema-consistent information into complementary learning systems theory", *J Exp Psychol Gen* 142:1190. doi:10.1037/a0033812
- van Kesteren, Ruiter, Fernández & Henson (2012) "How schema and novelty augment memory formation", *Trends Neurosci* 35:211. doi:10.1016/j.tins.2012.02.001
- Behrens et al. (2018) "What is a cognitive map? Organizing knowledge for flexible behavior", *Neuron* 100:490. doi:10.1016/j.neuron.2018.10.002
- Gentner (1983) "Structure-mapping: a theoretical framework for analogy", *Cognitive Science* 7:155. doi:10.1207/s15516709cog0702_3
- Fodor & Pylyshyn (1988) "Connectionism and cognitive architecture: a critical analysis", *Cognition* 28:3. doi:10.1016/0010-0277(88)90031-5
- Lake & Baroni (2018) "Generalization without systematicity", *ICML*. https://arxiv.org/abs/1711.00350
- Lake & Baroni (2023) "Human-like systematic generalization through a meta-learning neural network", *Nature* 623:115. doi:10.1038/s41586-023-06668-3
- Wang et al. (2018) "Prefrontal cortex as a meta-reinforcement learning system", *Nat Neurosci* 21:860. doi:10.1038/s41593-018-0147-8
- Yang et al. (2019) "Task representations in neural networks trained to perform many cognitive tasks", *Nat Neurosci* 22:297. doi:10.1038/s41593-018-0310-2
