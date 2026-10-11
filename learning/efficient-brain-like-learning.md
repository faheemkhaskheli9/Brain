---
title: Making a brain-like learner efficient (energy and samples)
category: learning
tags: [efficiency, energy, sparse-coding, event-driven, eligibility-trace, k-wta, replay, dyna, priors, sample-efficiency, brain-world]
use_cases:
  - how do I make my brain simulation as efficient as the human brain
  - why does my brain-inspired learner waste compute on inactive units
  - make an actor-critic with eligibility traces update only active synapses
  - my agent needs thousands of episodes where a person needs a few, what can I borrow from the brain
status: draft
last_verified: 2026-10-11
sources:
  - doi:10.1016/S0960-9822(03)00135-0
  - doi:10.1097/00004647-200110000-00001
  - doi:10.1007/BF00992699
  - doi:10.1038/s41467-019-11786-6
---

# Making a brain-like learner efficient (energy and samples)

## Summary
"As efficient as the brain" means two separate things. **Energy per step**: the brain
runs on about 20 W because few neurons are active and work happens only where a spike
arrives ([[glia-and-energy-budget]]). **Samples to learn**: animals learn new skills from
far fewer trials than reward-only learners, helped by built-in wiring, replay and
other teachers ([[brain-vs-deep-learning]]). This topic lists methods for each side, ranked
by payoff for effort. It also gives measurements from this repo's Brain World learner
(`game/world/brain.js`).

## How it works

### Where a simple learner stands (measured here)
Brain World is an actor-critic over a fixed 1,000-unit random expansion, with eligibility
traces and a three-factor rule (trace times dopamine). On seed 1, the first 3,000 episodes
(241k steps, about 11 s in node, reaching the read stage) gave:

| Measure | Brain World | Brain |
|---|---|---|
| Hidden units active per step | 6.8% (68 of 1,000) | about 1% of cortical neurons (Lennie 2003) |
| Actor trace entries above 1e-3 | 3.9% of 12,177 | plasticity needs recent activity ([[learning-and-plasticity]]) |
| Work per step | about 12k multiply-adds each to act, fade traces and update weights, all dense | work only where spikes arrive |
| Episodes to learn all five skills | about 9,000-20,000 (README of `game/world/`) | not comparable without a matched task |

So activity is already sparse. The waste is that every step still touches every synapse.

### Energy side (established principle, game-level implementation)
The principle is established: spikes and synaptic transmission take most of the brain's
signalling energy (Attwell & Laughlin 2001), and that cost favours sparse firing (Levy &
Baxter 1996; [[neural-coding-and-computation]]). The methods, best payoff first:

1. **Event-driven trace and weight updates.** Fade and update only the traces of units
   that fired, or whose trace is still above a small threshold. Drop the rest to zero. This
   is an approximation: the dropped tail is below the threshold. The code below measures it.
2. **Event-driven action choice.** Sum only over active inputs when scoring actions. This
   is exact, since zero inputs add nothing.
3. **Sparser codes.** Keep only the k most active units (k-winners-take-all; Makhzani &
   Frey 2013), or use an adaptive per-unit threshold that holds a target firing rate
   (homeostasis). Fewer active units means less work. Whether it also cuts interference
   between tasks in a given learner has to be measured.
4. **Spikes and neuromorphic chips** pay off only on event-driven hardware
   ([[neuromorphic-hardware]]). On a CPU or GPU, simulating spikes costs more than a rate
   code.

### Sample side (mixed: the mechanisms are established, the payoff in a given agent is not)
5. **Offline replay of stored experience.** Rehearsing by playing new episodes costs fresh
   experience. Storing real transitions and replaying them between episodes gives many
   updates per real try (Lin 1992). The hippocampus replays recent experience during rest
   and sleep ([[sleep-and-memory-consolidation]]). Replayed transitions are off-policy for
   an actor-critic, so they need a correction or a value-only update.
6. **Built-in priors.** Much behaviour is wired by the genome, not learned from scratch
   (Zador 2019; [[brain-development-and-critical-periods]]). For an agent, this means
   reflexes such as orienting towards salient objects, or pattern generators for gait.
7. **Learning from a teacher.** A demonstration (imitation) can replace a long search for
   a rewarded action sequence, such as the strokes of a letter.
8. **Surprise-scaled plasticity.** Neuromodulators such as acetylcholine and noradrenaline
   are proposed to set the learning rate from uncertainty (Doya 2002; [[neuromodulators]]).
   This mapping is a **hypothesis**.
9. **A forward model plus planning.** Learn to predict the next state and practise in
   imagination (Dyna; Sutton 1990). The cerebellum as a forward model is an established
   theory ([[action-selection-and-motor-control]]). This is the most work.

## Relevance to building brain-like AI
- Count work per event, not per parameter. A learner with 7% activity that updates every
  synapse each step gets none of the brain's energy advantage.
- Do 1 and 2 first: they are cheap and change results little or not at all. Measure 3 and 5
  across several seeds before keeping them, because single-seed effects in Brain World have
  reversed before (see its README on replay and the fovea memory).

## Code: event-driven eligibility traces
Dense traces fade and update every weight each step. The event-driven version touches only
live traces, with activity that is sparse (7%) and persists for a few steps, as it does
when an agent keeps looking at one scene.

```python
import numpy as np

rng = np.random.default_rng(0)
n, T, d, lr, eps = 1000, 600, 0.96 * 0.85, 0.05, 1e-3   # d = gamma * lambda, as in Brain World

# Sparse, temporally correlated activity: 7% of units fire, and the active set
# changes every 10 steps (a scene the agent keeps looking at for a while).
H = np.zeros((T, n))
for t0 in range(0, T, 10):
    on = rng.choice(n, size=70, replace=False)
    H[t0:t0 + 10, on] = rng.random(70)
delta = rng.normal(0, 0.1, T)   # dopamine (TD error) each step

# Dense: every trace fades and every weight moves, every step.
w, e, dense_ops = np.zeros(n), np.zeros(n), 0
for h, dl in zip(H, delta):
    e = d * e + h
    w += lr * dl * e
    dense_ops += 2 * n

# Event-driven: touch only units that fired or whose trace is still above eps.
ws, es, live, sparse_ops = np.zeros(n), np.zeros(n), np.zeros(n, bool), 0
for h, dl in zip(H, delta):
    live |= h > 0
    idx = np.flatnonzero(live)
    es[idx] = d * es[idx] + h[idx]
    ws[idx] += lr * dl * es[idx]
    sparse_ops += 2 * len(idx)
    faded = idx[np.abs(es[idx]) <= eps]
    es[faded] = 0.0
    live[faded] = False

err = np.abs(w - ws).max() / np.abs(w).max()
print(f"ops: dense {dense_ops}, event-driven {sparse_ops} ({dense_ops / sparse_ops:.1f}x fewer)")
print(f"largest weight difference: {err:.2e} of the largest weight")
assert sparse_ops < dense_ops / 3
assert err < 1e-2
```

It prints about 3.6× fewer operations, with weights within 0.015% of the dense run. The
saving grows as activity gets sparser or persists longer. If every step drew a fresh
random 7%, traces would stay live for about 30 steps at d = 0.816, and little would be
saved.

## Open questions
- How much of the brain's sample efficiency comes from innate wiring and how much from
  better learning rules is debated (Zador 2019).
- Whether k-WTA sparsity speeds up or slows down Brain World's curriculum is untested.
- The size of the episode-count gap between Brain World and a person on matched tasks is
  unknown. No matched human data exist here.

## Related
- [[glia-and-energy-budget]] - where the brain's 20 W goes and why it favours sparse firing.
- [[neural-coding-and-computation]] - sparse and event-driven codes.
- [[neuromorphic-hardware]] - hardware where spikes actually save energy.
- [[brain-vs-deep-learning]] - sample efficiency as an open frontier.
- [[sleep-and-memory-consolidation]] - replay as the biological basis of method 5.
- [[build-a-brain-like-learner]] - the architecture these methods would speed up.

## References
- Lennie (2003) "The cost of cortical computation", *Curr Biol* 13:493. doi:10.1016/S0960-9822(03)00135-0
- Attwell & Laughlin (2001) "An energy budget for signaling in the grey matter of the brain", *J Cereb Blood Flow Metab* 21:1133. doi:10.1097/00004647-200110000-00001
- Levy & Baxter (1996) "Energy efficient neural codes", *Neural Comput* 8:531. doi:10.1162/neco.1996.8.3.531
- Makhzani & Frey (2013) "k-Sparse Autoencoders", arXiv:1312.5663.
- Lin (1992) "Self-improving reactive agents based on reinforcement learning, planning and teaching", *Machine Learning* 8:293. doi:10.1007/BF00992699
- Sutton (1990) "Integrated architectures for learning, planning, and reacting based on approximating dynamic programming", *Proceedings of ICML 1990*, 216-224.
- Zador (2019) "A critique of pure learning and what artificial neural networks can learn from animal brains", *Nat Commun* 10:3770. doi:10.1038/s41467-019-11786-6
- Doya (2002) "Metalearning and neuromodulation", *Neural Networks* 15:495. doi:10.1016/S0893-6080(02)00044-8
