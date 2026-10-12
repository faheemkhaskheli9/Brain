---
title: Cognitive architectures (ACT-R, Soar, Nengo/NEF, Spaun, Thousand Brains)
category: simulation
tags: [cognitive-architecture, act-r, soar, nengo, nef, neural-engineering-framework, spaun, semantic-pointer, thousand-brains, cortical-columns, llm-agents, coala]
use_cases:
  - what is a cognitive architecture and how do ACT-R and Soar work
  - how does the Neural Engineering Framework build cognition out of spiking neurons
  - what is Spaun and what can it do
  - is the Thousand Brains theory established neuroscience
  - how do LLM agent designs compare with brain-inspired architectures
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1037/0033-295X.111.4.1036
  - https://doi.org/10.1016/0004-3702(87)90050-6
  - https://doi.org/10.1609/aimag.v38i4.2744
  - https://doi.org/10.1126/science.1225266
  - https://doi.org/10.3389/fninf.2013.00048
  - https://doi.org/10.3389/fncir.2018.00121
  - https://arxiv.org/abs/2309.02427
---

# Cognitive architectures (ACT-R, Soar, Nengo/NEF, Spaun, Thousand Brains)

## Summary
A cognitive architecture is a fixed set of modules, memories and a control cycle
that is meant to run *any* task, the way one brain does. Three traditions matter
here. **Symbolic** architectures (ACT-R, Soar) model the mind as rules acting on
buffers and memories, and fit human reaction times and errors well. **Neural**
architectures built with the Neural Engineering Framework (Nengo, Spaun) make the
same kind of modules out of spiking neurons. **Theory-driven** proposals such as
Hawkins' Thousand Brains are hypotheses about cortex, not working systems at scale.
LLM agents (an LLM plus memory, planning and tools) are a modern, engineering-first
version of the same idea.

## How it works

### Symbolic architectures: ACT-R and Soar
**ACT-R** (Anderson et al. 2004) has modules (visual, manual, declarative memory,
goal), each exposed to the rest through a small **buffer**, and a central
**procedural** system of if-then production rules that reads and writes buffers.
- **Established (as a modelling result):** one production fires per cycle, and the
  cycle is set to about 50 ms. Declarative facts have an *activation* that rises with
  use and decays with time, which sets retrieval time and error rate. Models built
  this way predict human latencies and error patterns in tasks such as arithmetic,
  list memory and skill learning (Anderson et al. 2004).
- **Supported:** Anderson et al. map buffers onto brain regions (goal to
  dorsolateral prefrontal cortex, retrieval to ventrolateral prefrontal cortex,
  procedural matching to the basal ganglia) and predict fMRI activity from the time
  each module is busy. The mapping is a claim of the architecture, tested in
  specific tasks, not a settled anatomy.

**Soar** (Laird, Newell & Rosenbloom 1987) frames every task as search in a
**problem space**. A decision cycle proposes, evaluates and applies operators. When
no rule decides, an **impasse** creates a subgoal, and **chunking** caches the
subgoal's result as a new rule, so deliberate reasoning turns into fast skill.
Later versions added reinforcement learning on operator preferences and separate
episodic and semantic memories (Laird 2012).

**The Common Model of Cognition** (Laird, Lebiere & Rosenbloom 2017) is the
field's own summary of what ACT-R, Soar and Sigma share: a working memory, a
procedural memory selecting one action per ~50 ms cycle, declarative long-term
memory, and perception and motor modules. It is a consensus *proposal*.

### Neural architectures: NEF, Nengo and Spaun
The **Neural Engineering Framework** (Eliasmith & Anderson 2003) has three principles:
1. **Representation.** A population encodes a vector `x`: neuron `i` fires at
   `a_i(x) = G(α_i e_i·x + b_i)`, with a preferred direction `e_i`, gain and bias.
   Linear **decoders** `d_i`, found by least squares, read it back: `x̂ = Σ a_i d_i`.
2. **Transformation.** Decoders for `f(x)` instead of `x` compute a function; folding
   decoders into the next population's encoders gives the connection weights.
3. **Dynamics.** Recurrent connections built the same way implement a chosen
   differential equation (integrators for working memory, oscillators).

This is **established as an engineering method**: it reliably compiles a specified
computation into spiking networks. Whether real cortex computes this way is a
**hypothesis**. **Nengo** is the Python implementation (Bekolay et al. 2014); it
runs the same model on CPUs, GPUs and neuromorphic back ends such as Loihi.

**Spaun** (Eliasmith et al. 2012) is a **2.5-million-neuron** spiking model built
with Nengo and the Semantic Pointer Architecture (compressed vectors that are bound
and unbound to build structures). It sees images, and answers by drawing with a
physically modelled arm. It performs **eight tasks** (the paper's list includes
digit recognition, copy drawing, serial working memory, counting, question
answering, a bandit task and a Raven-style pattern completion), switching between
them from the input alone. Its modules map to named regions: visual hierarchy,
working memory in prefrontal-like recurrent populations, and action selection in a
basal ganglia-thalamus loop. Limit: the tasks and their wiring are designed, not
learned; the bandit task is the one that requires learning from reward. Why one network serving
many tasks through separate organs matters is argued in [[one-brain-many-tasks]].

### Thousand Brains theory (Hawkins) - hypothesis
Hawkins and colleagues propose that **every cortical column** learns a complete
model of objects, each in its own **reference frame** anchored by grid-cell-like
location signals in cortex, and that columns **vote** through long-range
connections to reach a consensus (Hawkins et al. 2017, 2019).
- **Supported pieces:** columnar organisation, grid cells in the entorhinal cortex
  ([[spatial-navigation]]) and grid-like fMRI signals while people navigate an
  abstract two-dimensional concept space (Constantinescu, O'Reilly & Behrens 2016).
- **Hypothesis:** grid-cell-like location coding in every neocortical column, and
  object models replicated across columns. Neither is directly demonstrated in
  cortex. The Thousand Brains Project's open-source Monty framework
  (https://github.com/thousandbrainsproject/tbp.monty) implements the idea as a
  sensorimotor learning system; that tests it as engineering, not as biology.

### LLM agents as a modern analogue
An LLM agent wraps a language model in a loop with memory, planning and tools.
Sumers et al. (2024, *CoALA*) describe such agents in the vocabulary of Soar and
ACT-R: working memory (the context window), episodic, semantic and procedural
long-term memory, and a decision cycle that proposes, evaluates and selects
actions. Generative Agents (Park et al. 2023) add a memory stream with retrieval by
recency, importance and relevance, plus periodic "reflection" that writes summaries
back to memory. **Established:** these designs work as engineering. **Not
claimed:** that they resemble the brain's mechanisms; the analogy is functional.

### Comparison with the roadmap
How each architecture covers the components of [[build-a-brain-like-learner]]:

| Component (roadmap) | ACT-R | Soar | Spaun / NEF | Thousand Brains | LLM agent |
|---|---|---|---|---|---|
| Cortex: predictive world model | Perceptual modules, no learned world model | Problem spaces, hand-written | Fixed visual hierarchy | Core claim: a model in every column | The LLM itself, pretrained |
| Hippocampus: fast episodic memory | Declarative memory with activation | Episodic memory (Soar 9) | Not in 2012 model | Not specified | Vector or text memory store |
| Basal ganglia: action selection | Production selection by utility | Operator preferences | Spiking basal ganglia-thalamus loop | Not specified | Prompted choice among tools |
| Prefrontal: working memory and goals | Goal and other buffers | Working memory, subgoals | Recurrent integrator populations | Not specified | Context window |
| Learning | Utility learning, activation | Chunking, RL | Reward learning in the bandit task | Hebbian-style learning on dendritic segments (proposed) | Mostly in pretraining; in-context |
| Spiking neurons | No | No | Yes | No; small models use binary neurons with dendritic segments | No |

## Relevance to building brain-like AI
- **Pick the architecture for the question.** ACT-R or Soar if you need to predict
  human timing and errors; Nengo if you need a cognitive model that also runs as
  spiking neurons or on neuromorphic chips ([[neuromorphic-hardware]]); an LLM
  agent if you need a system that works today.
- **NEF decoders are a cheap way to put functions into spiking networks** without
  training the network end to end. The code below is the core of it.
- **The weak point everywhere is learning the architecture itself.** Symbolic and
  NEF models are mostly hand-built; LLM agents learn their core but not their loop.

## Code
An NEF population: LIF tuning curves with random preferred directions, least-squares
decoders, and decoding of `x` and `x²` from the same noisy rates.

```python
import numpy as np

rng = np.random.default_rng(0)
tau_rc, tau_ref = 0.02, 0.002                    # LIF time constants (s), Nengo defaults

def lif_rate(J):
    r = np.zeros_like(J)
    on = J > 1
    r[on] = 1.0 / (tau_ref - tau_rc * np.log1p(-1.0 / J[on]))
    return r

def population(n):
    enc = rng.choice([-1.0, 1.0], n)             # preferred direction of each neuron
    max_rate = rng.uniform(200, 400, n)          # rate (Hz) at x = enc
    intercept = rng.uniform(-0.95, 0.95, n)      # x where the neuron starts firing
    J_max = 1.0 / (1.0 - np.exp((tau_ref - 1.0 / max_rate) / tau_rc))
    gain = (J_max - 1.0) / (1.0 - intercept)
    bias = 1.0 - gain * intercept
    return enc, gain, bias

def rates(x, enc, gain, bias):                   # encoding: a_i(x) = G(gain * e_i * x + bias)
    return lif_rate(gain * np.outer(x, enc) + bias)

def decoders(A, target, noise=0.1):              # regularised least squares
    sigma = noise * A.max()
    return np.linalg.solve(A.T @ A + len(A) * sigma**2 * np.eye(A.shape[1]), A.T @ target)

def test_rmse(n, f):
    enc, gain, bias = population(n)
    x = np.linspace(-1, 1, 200)
    A = rates(x, enc, gain, bias)
    d = decoders(A, f(x))
    x_test = rng.uniform(-1, 1, 500)
    A_test = rates(x_test, enc, gain, bias)
    A_test += rng.normal(0, 0.1 * A.max(), A_test.shape)   # spiking-like noise on every rate
    return float(np.sqrt(np.mean((A_test @ d - f(x_test)) ** 2)))

errs = {n: test_rmse(n, lambda x: x) for n in (10, 50, 400)}
sq = test_rmse(400, lambda x: x ** 2)            # same kind of population, different decoders
print("RMSE decoding x:", {n: round(e, 3) for n, e in errs.items()})
print(f"RMSE decoding x^2 with 400 neurons: {sq:.3f}")
assert errs[400] < 0.05                          # a few hundred neurons represent x well
assert errs[400] < errs[50] < errs[10]           # error falls as the population grows
assert sq < 0.05                                 # a function of x comes out of the same rates
```

It prints an RMSE of about 0.08 with 10 neurons, 0.04 with 50 and 0.013 with 400,
and 0.018 for `x²`.

## Open questions
- Whether the brain has anything like a central production system with a fixed
  cycle, or whether the ~50 ms figure is only a good fit at the behavioural level.
- Whether NEF-style linear decoding describes real downstream readout, or is only a
  convenient way to build models.
- Whether cortical columns each hold full object models (Thousand Brains) or divide
  the work hierarchically.
- How an architecture could *learn* its own modules and control loop rather than
  have them designed.

## Related
- [[one-brain-many-tasks]] - why one system with specialised organs, using Spaun as evidence.
- [[build-a-brain-like-learner]] - the roadmap the comparison table is scored against.
- [[levels-of-brain-modeling]] - cognitive architectures sit at Marr's algorithmic level.
- [[spiking-neural-networks]] - the neuron models Nengo builds on.
- [[neuromorphic-hardware]] - chips Nengo models can run on.
- [[action-selection-and-motor-control]] - the basal ganglia loop Spaun and ACT-R both model.
- [[attention-and-working-memory]] - the biology behind buffers and integrators.
- [[spatial-navigation]] - grid cells, the basis of Thousand Brains reference frames.
- [[language-and-llms]] - the LLMs at the core of LLM agents.

## References
- Anderson, Bothell, Byrne, Douglass, Lebiere & Qin (2004) "An integrated theory of the mind", *Psychological Review* 111:1036. doi:10.1037/0033-295X.111.4.1036
- Laird, Newell & Rosenbloom (1987) "SOAR: An architecture for general intelligence", *Artificial Intelligence* 33:1. doi:10.1016/0004-3702(87)90050-6
- Laird (2012) *The Soar Cognitive Architecture*. MIT Press.
- Laird, Lebiere & Rosenbloom (2017) "A Standard Model of the Mind", *AI Magazine* 38(4):13. doi:10.1609/aimag.v38i4.2744
- Kotseruba & Tsotsos (2020) "40 years of cognitive architectures: core cognitive abilities and practical applications", *Artificial Intelligence Review* 53:17. doi:10.1007/s10462-018-9646-y
- Eliasmith & Anderson (2003) *Neural Engineering: Computation, Representation, and Dynamics in Neurobiological Systems*. MIT Press.
- Eliasmith (2013) *How to Build a Brain: A Neural Architecture for Biological Cognition*. Oxford University Press.
- Eliasmith, Stewart, Choo, Bekolay, DeWolf, Tang & Rasmussen (2012) "A large-scale model of the functioning brain", *Science* 338:1202. doi:10.1126/science.1225266
- Bekolay et al. (2014) "Nengo: a Python tool for building large-scale functional brain models", *Front Neuroinform* 7:48. doi:10.3389/fninf.2013.00048
- Hawkins, Ahmad & Cui (2017) "A theory of how columns in the neocortex enable learning the structure of the world", *Front Neural Circuits* 11:81. doi:10.3389/fncir.2017.00081
- Hawkins, Lewis, Klukas, Purdy & Ahmad (2019) "A framework for intelligence and cortical function based on grid cells in the neocortex", *Front Neural Circuits* 12:121. doi:10.3389/fncir.2018.00121
- Constantinescu, O'Reilly & Behrens (2016) "Organizing conceptual knowledge in humans with a gridlike code", *Science* 352:1464. doi:10.1126/science.aaf0941
- Sumers, Yao, Narasimhan & Griffiths (2024) "Cognitive Architectures for Language Agents", *Transactions on Machine Learning Research*. arXiv:2309.02427
- Park et al. (2023) "Generative Agents: Interactive Simulacra of Human Behavior", *UIST '23*. doi:10.1145/3586183.3606763
