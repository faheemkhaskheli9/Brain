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

### Measured: k-WTA in Brain World (issue #82)
Pre-registered hypothesis: k-WTA with k = 20-50 of 1,000 hidden units cuts per-step
multiply-adds by at least 2x, with at most a 10% rise in episodes to learn all five
skills. Run: `node game/world/sweep.mjs --arms rehearse30,kwta20,kwta35,kwta50`, seeds
1-10, exact paired sign-flip test on per-seed episode totals.

| Arm | Passed | Hidden units on per step | Episodes, all five skills (mean / median) | vs baseline |
|---|---|---|---|---|
| Baseline (no k-WTA) | 10/10 | 79 | 18,202 / 17,826 | - |
| k = 20 | 10/10 | 20 | 13,642 / 12,698 | -4,560 (p = 0.066) |
| k = 35 | 10/10 | 35 | 16,809 / 17,307 | -1,392 (p = 0.57) |
| k = 50 | 10/10 | 49 | 17,189 / 15,475 | -1,013 (p = 0.64) |

- **Learning: no cost.** No arm needed more episodes. k = 20 was faster on 7 of 10 seeds
  and kept every skill above the test's bars on all 10, but p = 0.066 is not significant.
- **Work: under 2x, so the work half of the hypothesis fails.** Over the whole curriculum the
  baseline has 79 units on (7.9%, higher than the 6.8% measured over the first 3,000
  episodes). k = 20 cuts that 4x. But the hidden units are only part of each step:
  - encoding drives about 500 ungated units × 8 inputs whatever k is;
  - every action score also sums the 107 raw inputs;
  - the dense trace and weight updates (about 12k each) do not shrink at all.

  Even with event-driven action choice (method 2), each action's dot product falls
  from at most 186 terms to at most 127 (about 1.5x), and the whole step saves far less.
- **So:** sparsity pays only together with methods 1 and 2. On its own, k-WTA changes how
  much is active, not how much the code computes. It stays off by default.

This is a result about this learner, not about cortex.

### Measured: innate prior vs better learning rule in Brain World (issue #83)
Pre-registered on #83 before any run. It is a 2x2 design:
- **Prior:** an orienting reflex. It adds a fixed, never-learned bias to the leg-push
  logits that turns toward the brighter side of the retina (`GAINS.orient = 1`, untuned).
- **Rule:** the three-factor rule alone, or the same rule plus sleep replay of actor and
  critic (`sleepEvery 20`, `sleepActor`). Rehearsal stays at 30% in every cell.

Run: `node game/world/sweep.mjs --arms rehearse30,orient,sleepActor30,orient+sleepActor30`,
seeds 1-10, 20,000-episode cap per stage. Cells show seeds that passed / mean episodes over
those seeds.

| Arm | Grasp | Listen | Read | Write | All five |
|---|---|---|---|---|---|
| Neither | 10/10, 840 | 10/10, 3,042 | 10/10, 5,424 | 10/10, 8,773 | 10/10, 18,202 |
| Prior (reflex) | 10/10, 53 | 3/10, 13,492 | 3/10, 9,722 | 3/10, 10,655 | 3/10, 34,047 |
| Rule (actor sleep) | 10/10, 808 | 10/10, 2,369 | 9/10, 4,182 | 9/10, 9,022 | 9/10, 16,322 |
| Both | 10/10, 77 | 6/10, 13,806 | 3/10, 5,628 | 3/10, 12,091 | 3/10, 29,160 |

- **The prior wins the stage it matches.** On grasp, where every run passed, the prior
  saves 759 episodes (95% CI 474-1,043, exact sign-flip p = 0.002), about 90%. The rule
  saves 4 (p = 0.91), and the interaction is +56 (p = 0.54).
- **It then blocks the next stage.** Listen asks for the object that matches a tone, not
  the brightest one in view. With the reflex on, 7 of 10 seeds never learned listen in
  20,000 episodes, and the 3 that did needed about 4x the baseline. The reflex adds a fixed
  amount to the logits that the learned weights must outweigh on every step.
- **The rule did little.** Actor sleep replay saved 1,670 episodes in total over the 9
  seeds that passed both arms (p = 0.56), and lost seed 7 on read.
- **The pre-registered prediction was wrong on listen and read.** The paired 2x2 over
  totals could not be computed, because no seed passed in all four cells. Grasp is the
  only stage with a full 2x2.

So a prior saves episodes only on the task it was built for, and it costs more on any
task that needs a different response to the same input. Next is a prior the learner can
turn down: a gain that decays with practice, or one gated by the task context. That gated
or decaying reflexes would fix this is a **hypothesis**, not tested here. This is
computational evidence about one toy agent with one hand-set prior, not about brains.

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
  better learning rules is debated (Zador 2019). Brain World data point (issue #83,
  2026-10-12): a fixed orienting reflex cut grasp by about 90% but blocked listen on 7 of
  10 seeds, and actor sleep replay changed little. Still open: whether a prior the learner
  can turn down (decaying or context-gated) keeps the saving without the cost.
- Answered here (issue #82, 2026-10-12): k-WTA does not slow Brain World's curriculum,
  but on its own it does not halve the work per step either. See "Measured: k-WTA" below.
  Still open: whether an adaptive per-unit threshold (homeostasis) does as well, and
  whether the faster learning at k = 20 holds over more seeds.
- The size of the episode-count gap between Brain World and a person on matched tasks is
  unknown. No matched human data exist here.

## Related
- [[glia-and-energy-budget]] - where the brain's 20 W goes and why it favours sparse firing.
- [[neural-coding-and-computation]] - sparse and event-driven codes.
- [[neuromorphic-hardware]] - hardware where spikes actually save energy.
- [[brain-vs-deep-learning]] - sample efficiency as an open frontier.
- [[sleep-and-memory-consolidation]] - replay as the biological basis of method 5.
- [[build-a-brain-like-learner]] - the architecture these methods would speed up.
- [[open-questions-register]] - the k-WTA and priors questions above are issues #82 and #83.

## References
- Lennie (2003) "The cost of cortical computation", *Curr Biol* 13:493. doi:10.1016/S0960-9822(03)00135-0
- Attwell & Laughlin (2001) "An energy budget for signaling in the grey matter of the brain", *J Cereb Blood Flow Metab* 21:1133. doi:10.1097/00004647-200110000-00001
- Levy & Baxter (1996) "Energy efficient neural codes", *Neural Comput* 8:531. doi:10.1162/neco.1996.8.3.531
- Makhzani & Frey (2013) "k-Sparse Autoencoders", arXiv:1312.5663.
- Lin (1992) "Self-improving reactive agents based on reinforcement learning, planning and teaching", *Machine Learning* 8:293. doi:10.1007/BF00992699
- Sutton (1990) "Integrated architectures for learning, planning, and reacting based on approximating dynamic programming", *Proceedings of ICML 1990*, 216-224.
- Zador (2019) "A critique of pure learning and what artificial neural networks can learn from animal brains", *Nat Commun* 10:3770. doi:10.1038/s41467-019-11786-6
- Doya (2002) "Metalearning and neuromodulation", *Neural Networks* 15:495. doi:10.1016/S0893-6080(02)00044-8
