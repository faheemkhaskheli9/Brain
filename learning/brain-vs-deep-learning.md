---
title: Brain vs deep learning
category: learning
tags: [backpropagation, credit-assignment, feedback-alignment, equilibrium-propagation, forward-forward, biological-plausibility, neuroai, sample-efficiency]
use_cases:
  - how is learning in the brain different from deep learning
  - can the brain do backpropagation
  - what should AI borrow from the brain next
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1038/ncomms13276
  - https://doi.org/10.1038/s41583-020-0277-3
  - https://doi.org/10.3389/fncom.2017.00024
  - https://arxiv.org/abs/2212.13345
---

# Brain vs deep learning

## Summary
Deep learning already borrowed a lot from the brain: neurons, hierarchy,
convolution (from V1), reinforcement learning (from dopamine) and replay (from
the hippocampus). But it learns very differently. Backprop sends exact error
gradients backwards through the same weights, needs separate training and
inference phases, and needs huge labelled or curated datasets. The brain learns
**continually**, **locally**, from **few examples**, while **acting**, on
**20 W**. How the brain solves **credit assignment** (which synapse caused an
error) is the central open question, and the answer is what would let computers
learn like humans.

## How it works

### Side by side
| | Brain | Deep learning (today) |
|---|---|---|
| Learning signal | Mostly self-supervised prediction + reward + social | Labelled data, next-token prediction, RLHF |
| Credit assignment | Local rules + neuromodulators + (probably) feedback circuits | Exact global gradient (backprop) |
| Training vs use | Always learning, while acting | Train once, then frozen (in-context learning aside) |
| Forgetting | Graceful; CLS + consolidation | Catastrophic without replay or tricks |
| Data | A child hears on the order of 100 million words or fewer by early adolescence (Frank 2023) | Frontier LLMs train on trillions of tokens |
| Prior knowledge | Strong innate structure from evolution | Mostly architecture + initialisation |
| Embodiment | Learns through a body acting in the world | Mostly passive datasets |
| Memory | Separate fast (hippocampus) and slow (cortex) systems | Weights + context window (+ optional retrieval) |
| Energy | ~20 W | Training runs use megawatts |
| Units | Spiking, noisy, sparse, recurrent everywhere | Dense, deterministic, mostly feedforward |
| Where deep learning wins | - | Raw scale, speed, precision, copying knowledge instantly between machines |

### Why the brain probably cannot do exact backprop
1. **Weight transport.** Backprop needs the backward pass to use the transpose of
   forward weights. Synapses are one-way, so there is no obvious way to copy them.
2. **Separate phases.** Backprop needs a forward pass, a stored activation, then a
   backward pass. Neurons are continuously active.
3. **Signed error signals** would need to be carried by firing rates, which cannot go below zero.
4. **Backprop through time** across long sequences needs storing past states;
   the brain is online.

### Candidate brain-plausible credit assignment
| Method | Idea | Status |
|---|---|---|
| **Feedback alignment** (Lillicrap et al. 2016) | Use *random fixed* feedback weights instead of the transpose; forward weights learn to align with them | Works on simple tasks, weaker on deep conv nets |
| **Predictive coding** (Whittington & Bogacz 2017) | Errors computed locally at every layer; at equilibrium the updates approximate backprop | Runnable example in [[brain-inspired-learning-algorithms]] |
| **Equilibrium propagation** (Scellier & Bengio 2017) | Energy-based network relaxes twice (free, then nudged toward target); a local contrastive rule recovers the gradient | Promising for analog/neuromorphic hardware |
| **Dendritic error / burst-dependent plasticity** (Sacramento 2018; Payeur 2021) | Apical dendrites receive top-down error; bursts vs single spikes multiplex the signal | Fits cortical anatomy |
| **Forward-Forward** (Hinton 2022) | Two forward passes (real vs negative data) with a local "goodness" objective per layer | Simple, local; weaker than backprop at scale |
| **Three-factor rules + eligibility traces** | Hebbian tag × global neuromodulator | Solid for RL-type signals; slow for high-dimensional credit |
| **Node perturbation / weight perturbation** | Random noise + reward correlation | Correct in expectation but very slow (high variance) |

Lillicrap et al. (2020) argue the brain implements something *like* backprop via
feedback-driven activity differences ("NGRAD"). This is a strong hypothesis, not
a proven fact.

### What deep learning already took from the brain
- Artificial neurons (McCulloch-Pitts 1943), perceptrons, Hebbian ideas.
- **CNNs** from V1 simple and complex cells (Hubel & Wiesel → Neocognitron → LeNet).
- **TD learning / actor-critic** from animal conditioning and dopamine.
- **Experience replay** from hippocampal replay (cited in the DQN paper).
- **Attention** (loosely) from cognitive attention; transformer attention is
  mathematically a modern Hopfield network.
- **Dropout** (loosely, by analogy with noisy synapses), normalisation (divisive normalisation).

### What it has not taken yet (the frontier)
1. **Continual, lifelong learning** without catastrophic forgetting.
2. **Fast + slow memory systems** with consolidation (CLS).
3. **Sample efficiency** through strong priors, curiosity and active exploration.
4. **Local learning rules** that run on-device with no backward pass.
5. **Sparse, event-driven computation** for energy efficiency.
6. **Embodied world models** learned through sensorimotor interaction.
7. **Neuromodulation**: global signals that adapt learning rate, exploration
   and attention on the fly (meta-learning).

## Relevance to building brain-like AI
The pragmatic path today: keep backprop where it works (it is the best credit
assignment method we have), and add the brain's *system-level* ideas, because they
are what is missing: CLS memory, replay and sleep, intrinsic motivation, world
models, embodiment, sparse activity. Swap in local learning rules where hardware
or continual learning demands it. See [[build-a-brain-like-learner]].

## Related
- [[learning-and-plasticity]] - the biological rules.
- [[brain-inspired-learning-algorithms]] - runnable versions.
- [[predictive-processing]] - the predictive coding account.
- [[memory-systems]] - CLS and catastrophic forgetting.
- [[key-papers]] - one-line findings of every paper cited here.

## References
- Lillicrap, Cownden, Tweed & Akerman (2016) "Random synaptic feedback weights support error backpropagation for deep learning", *Nat Commun* 7:13276. doi:10.1038/ncomms13276
- Lillicrap, Santoro, Marris, Akerman & Hinton (2020) "Backpropagation and the brain", *Nat Rev Neurosci* 21:335. doi:10.1038/s41583-020-0277-3
- Scellier & Bengio (2017) "Equilibrium Propagation", *Front Comput Neurosci* 11:24. doi:10.3389/fncom.2017.00024
- Hinton (2022) "The Forward-Forward Algorithm: Some Preliminary Investigations", arXiv:2212.13345.
- Sacramento, Costa, Bengio & Senn (2018) "Dendritic cortical microcircuits approximate the backpropagation algorithm", NeurIPS.
- Payeur, Guerguiev, Zenke, Richards & Naud (2021) "Burst-dependent synaptic plasticity can coordinate learning in hierarchical circuits", *Nat Neurosci* 24:1010.
- Richards et al. (2019) "A deep learning framework for neuroscience", *Nat Neurosci* 22:1761.
- Hassabis, Kumaran, Summerfield & Botvinick (2017) "Neuroscience-Inspired Artificial Intelligence", *Neuron* 95:245.
- Frank (2023) "Bridging the data gap between children and large language models", *Trends Cogn Sci* 27:990.
- Zador (2019) "A critique of pure learning and what artificial neural networks can learn from animal brains", *Nat Commun* 10:3770.
