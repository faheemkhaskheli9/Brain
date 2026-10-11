---
title: Roadmap - build a computer that learns like a brain
category: guides
tags: [roadmap, architecture, digital-brain, cognitive-architecture, continual-learning, world-model, embodiment, neuroai]
use_cases:
  - how can we create a digital simulation of the brain that learns like a human
  - plan a brain-inspired AI project step by step
  - what architecture combines memory, learning rules and world models like the brain
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1016/j.neuron.2017.06.011
  - https://doi.org/10.1016/j.tics.2016.05.004
  - https://openreview.net/forum?id=BZ5a1r-kVsf
---

# Roadmap: build a computer that learns like a brain

## Summary
You cannot copy a human brain today: its wiring is unmapped and its full
learning algorithm is unknown ([[whole-brain-emulation-projects]]). What you *can*
do is build a system that uses the brain's **known principles**. This roadmap
stacks them in six stages. Each stage is a runnable project that adds one brain
capability, so you have something working at every step. Stages 1-2 are about
neurons and synapses; 3-6 are about the system-level ideas that matter most for
human-like learning.

## The target architecture

```
                 ┌──────────────── Neuromodulators ─────────────────┐
                 │ dopamine = reward prediction error (learning rate,│
                 │ value) · ACh = uncertainty · NE = surprise/reset  │
                 └───────┬──────────────┬──────────────┬────────────┘
                         ▼              ▼              ▼
 senses ──► CORTEX: hierarchical ◄──► HIPPOCAMPUS:   BASAL GANGLIA:
 (events,   predictive world model     fast episodic   action selection
  vision,   (slow weights, self-       memory (one-    (actor-critic RL)
  text)     supervised, sparse)        shot, replay)        │
                 ▲        ▲               │ sleep replay     ▼
                 │        └───────────────┘ (consolidation) actions ──► world/body
                 └──────────── prediction errors ◄────────────────────────┘
          PREFRONTAL: working memory + goals (gated recurrent state)
```

## The stages

### Stage 1: Neurons and local learning (1-2 weeks)
Build: LIF and Izhikevich neurons, Hebbian/Oja and STDP in numpy.
Done when: one neuron discovers a correlated input group with no labels.
Read: [[neurons-and-synapses]], [[spiking-neural-networks]], [[learning-and-plasticity]].

A minimal version of that test, with a rate neuron and Oja's rule
([[brain-inspired-learning-algorithms]]) before you move to spikes:

```python
import numpy as np

rng = np.random.default_rng(0)
n_in, group = 20, 5                          # inputs 0-4 share one hidden cause
w = rng.uniform(0, 0.1, n_in)
eta = 0.01                                   # learning rate (a tuning knob)
for _ in range(5000):
    x = rng.normal(0, 1, n_in) * 0.5         # independent noise on every input
    x[:group] += rng.normal()                # plus a shared signal on the group
    y = w @ x
    w += eta * y * (x - y * w)               # Oja's rule: Hebb plus a forgetting term
in_group = np.abs(w[:group]).mean()
out_group = np.abs(w[group:]).mean()
print(f"mean |w| on the correlated group {in_group:.2f}, on the rest {out_group:.2f}, |w| = {np.linalg.norm(w):.2f}")
assert in_group > 5 * out_group              # the neuron found the group, with no labels
assert abs(np.linalg.norm(w) - 1) < 0.1      # and Oja's term kept the weights bounded
```

It prints a mean weight of 0.45 on the group against 0.03 on the rest, at length 1.01.

### Stage 2: A self-organising sensory layer (2-4 weeks)
Build: a spiking layer with STDP + lateral inhibition (winner-take-all) +
homeostasis, trained unsupervised on MNIST, as in Diehl & Cook (2015). Then try
a surrogate-gradient SNN in snnTorch on the same data and compare accuracy and
spike counts.
Brain principles: sparse coding, competition, homeostatic stability.
Read: [[neural-coding-and-computation]].

### Stage 3: Complementary memory and sleep (3-6 weeks)
Build: a slow learner (any network) + a fast episodic store (key-value memory with
sparse keys, i.e. pattern separation) + a "sleep" phase that replays stored
episodes interleaved with old data, plus EWC on the slow weights. Train on a
sequence of tasks (e.g. split-MNIST or Permuted MNIST).
Done when: accuracy on task 1 survives learning tasks 2-5 far better than plain
fine-tuning, and new facts are usable *immediately* via the fast store.
Read: [[memory-systems]], [[brain-inspired-learning-algorithms]].

### Stage 4: A predictive world model (1-2 months)
Build: a predictive-coding or latent-prediction model (JEPA-style) that learns
to predict the next observation in a simple environment (a gridworld, then
MiniGrid or a small 3D world). Learning is self-supervised from prediction error.
Done when: the model predicts the consequences of actions and its prediction
error drops on familiar situations and spikes on novel ones.
Read: [[predictive-processing]].

### Stage 5: Reward, curiosity and action (1-2 months)
Build: an actor-critic on top of the world model, with a TD error as the
dopamine signal, plus intrinsic reward = world-model prediction error (curiosity).
Plan by imagining rollouts inside the model, the way the hippocampus replays and
"preplays" paths.
Done when: the agent explores a sparse-reward environment and solves it faster
than without curiosity.
Read: [[learning-and-plasticity]] (dopamine), [[brain-inspired-learning-algorithms]] sections 3 and 6.

### Stage 6: Integrate, embody, and scale (open-ended)
Build: one agent combining stages 3-5. It should learn **online and continually** in
an environment that keeps changing, consolidate during sleep phases, and use
working memory for the current goal. Optional extras:
- Neuromodulator-like meta-parameters: learning rate rises with surprise
  (noradrenaline), exploration rises with uncertainty (acetylcholine).
- Port the spiking parts to neuromorphic hardware ([[neuromorphic-hardware]]).
- Constrain part of the architecture with real connectome data (fly visual
  system) as an inductive bias.

## Measuring "learns like a brain"
Benchmarks that test brain-like *learning*, not just accuracy:
| Property | Test |
|---|---|
| Continual learning | Accuracy on old tasks after new ones (backward transfer) |
| One-shot learning | Omniglot-style: recognise a class from one example |
| Sample efficiency | Score after N environment steps (e.g. Atari 100k) |
| Online / no epochs | Single pass over a data stream |
| Energy | Synaptic operations or joules per inference |
| Generalisation | Performance in held-out environments |
| Neural similarity | Brain-Score: match to recorded primate neural data |

## Honest limits
- **Accuracy**: purely local rules still lose to backprop on hard tasks. Use
  backprop where you must and treat local rules as a research thread.
- **Unknowns**: human-level abstraction, language and reasoning are not explained
  by any known brain learning rule. LLMs get them by scale, not by brain-likeness.
- **Consciousness**: no simulation stage here produces or tests subjective
  experience. No scientific consensus exists on how to.
- **Compute**: a human-scale spiking simulation is a supercomputer-class problem
  ([[levels-of-brain-modeling]]). Prototype small; the principles transfer.

## Related
- [[start-here]] - map of the whole KB.
- [[brain-vs-deep-learning]] - why these stages target what deep learning lacks.
- [[memory-systems]] - the CLS design behind stage 3.
- [[spatial-navigation]] - cognitive maps and the successor representation, a structured memory for an agent.
- [[whole-brain-emulation-projects]] - the other route: copying a real brain.
- [Brain World](../game/world/) - stages 3 and 5 in one embodied creature: actor-critic, traces and replay.
- [Brain Lab](../game/README.md) - level 8, *Tiny brain*: a forager that needs both dopamine and an eligibility trace.

## References
- Hassabis, Kumaran, Summerfield & Botvinick (2017) "Neuroscience-Inspired Artificial Intelligence", *Neuron* 95:245. doi:10.1016/j.neuron.2017.06.011
- Kumaran, Hassabis & McClelland (2016), *Trends Cogn Sci* 20:512. doi:10.1016/j.tics.2016.05.004
- LeCun (2022) "A Path Towards Autonomous Machine Intelligence", OpenReview.
- Diehl & Cook (2015), *Front Comput Neurosci* 9:99.
- Lake, Ullman, Tenenbaum & Gershman (2017) "Building machines that learn and think like people", *Behav Brain Sci* 40:e253.
- Zador et al. (2023) "Catalyzing next-generation Artificial Intelligence through NeuroAI", *Nat Commun* 14:1597.
- Schrimpf et al. (2018) "Brain-Score: Which Artificial Neural Network for Object Recognition is most Brain-Like?", bioRxiv 407007.
