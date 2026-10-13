---
title: One brain, many tasks (general organs vs one network)
category: function
tags: [multitask, continual-learning, catastrophic-forgetting, task-set, context-inference, gating, complementary-learning-systems, thalamus, prefrontal-cortex, adaptive-resonance, brain-world]
use_cases:
  - how does one brain learn many tasks without a separate module per task
  - should a brain-like learner be one big network or several organs
  - how can an agent tell which task it is in without being told
  - why does training a network on a new task wipe out the old ones
  - what does Brain World do to keep five skills in one brain
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1038/s41593-018-0310-2
  - https://doi.org/10.1038/s41593-024-01668-6
  - https://doi.org/10.1038/s41593-018-0147-8
  - https://arxiv.org/abs/2205.06175
  - https://doi.org/10.1016/S0893-6080(99)00046-5
  - https://doi.org/10.1037/0033-295X.102.3.419
  - https://doi.org/10.1016/j.tics.2016.05.004
  - https://doi.org/10.1126/science.1225266
  - https://doi.org/10.1038/s41593-018-0269-z
  - https://doi.org/10.1038/s41586-021-04129-3
  - https://doi.org/10.1037/a0030852
  - https://doi.org/10.1016/S0734-189X(87)80014-2
  - https://doi.org/10.1073/pnas.1803839115
---

# One brain, many tasks (general organs vs one network)

## Summary
A brain does not grow a new module for each skill it learns. The same cortex, basal ganglia,
cerebellum and hippocampus serve walking, reading and cooking. Two views compete for how that
works in a model: **one undifferentiated network** that finds its own task structure, or **a few
organs** that differ by learning rule and are shared by every task. The synthesis this KB uses is
a design hypothesis: fixed organs defined by learning rule, with **which task am I in** treated as a
latent the brain infers from its senses, not as an input it is handed. Brain World now infers which
of its context slots to use from a pooled scene summary (issue #60). Two task labels remain: the
at-board input and the action set chosen from the mode.

## How it works

### View 1: one network learns every task
- **Yang et al. (2019)** trained one recurrent network on 20 cognitive tasks, with a rule input
  naming the task. Units organised themselves into clusters that each served a subset of tasks,
  and task representations were compositional: a new task could be cued by combining old rule
  vectors.
- **Driscoll, Shenoy & Sussillo (2024)** found that multitask recurrent networks reuse the same
  **dynamical motifs** (attractors, decision boundaries, rotations) across tasks that need the
  same computation. With unit activity restricted to be positive, each motif lived in a cluster
  of units, and lesioning a cluster caused modular deficits in the tasks that used it.
- **Wang et al. (2018)** proposed the prefrontal cortex as a **meta-reinforcement learner**: a
  recurrent network trained by a dopamine-like signal across many related tasks learns, in its
  activity, a fast learning algorithm for the next one. This is a **supported** model, not a fact.
- **Gato (Reed et al. 2022)** is the engineering extreme: one transformer, with one set of
  weights, plays games, captions images, chats and controls a robot arm. It is trained by
  supervised imitation, with the task given by the prompt, so it is not a model of a brain.

### View 2: a few organs, shared by every task
- **Doya (1999)** argued that the big structures differ by **learning rule**, not by task:
  cerebellum supervised (error-driven), basal ganglia reinforcement (reward-driven), cerebral
  cortex unsupervised. Any task recruits all three. This is a well-supported theory, not settled.
- **Complementary learning systems (McClelland, McNaughton & O'Reilly 1995; Kumaran, Hassabis &
  McClelland 2016):** a fast hippocampus stores episodes, and replay trains a slow cortex by
  interleaving new memories with old ones. The division is by speed of learning, again not by task.
  See [[memory-systems]].
- **Spaun (Eliasmith et al. 2012):** about 2.5 million spiking neurons, wired as named modules
  (visual, working memory, action selection, motor), perform eight different tasks with one model.
  Most of it is built by hand, not learned, which is the price of its breadth.

### What is established, supported and hypothesis
- **Established:** a network that stores every task in the same weights loses old tasks when
  trained on a new one (**catastrophic interference**, McCloskey & Cohen 1989). Dopamine neurons
  signal reward prediction error (Schultz, Dayan & Montague 1997). The hippocampus replays recent
  experience during sleep (Wilson & McNaughton 1994), and interleaved replay reduces forgetting in
  networks too. CLS as a theory of why there are two memory systems has strong support.
- **Supported (evidence, debated):** in mice, the mediodorsal thalamus helps switch prefrontal
  representations when the rule changes (Rikhye, Gilra & Halassa 2018). In human motor learning,
  which memory is expressed and updated follows an inference of the current context (Heald,
  Lengyel & Wolpert 2021).
- **Hypothesis:** the brain forms **task sets** by clustering situations it has met, founding a new
  one when nothing fits (Collins & Frank 2013 give a Bayesian model of this for human behaviour).
  Synapses track their own importance and resist change once a skill depends on them, as in
  synaptic intelligence (Zenke, Poole & Ganguli 2017). Plasticity is gated by uncertainty, so a
  surprising world speeds learning and a familiar one protects old skills (Yu & Dayan 2005; see
  [[neuromodulators]]).

### Synthesis (a design hypothesis, not biology)
Keep the organs fixed and general, each with its own learning rule: an expansion layer, an
actor-critic, an episodic store with replay, later a forward model. Make **task structure a learned
latent**. A context selector clusters a summary of the scene, with no labels, and its choice gates
which units learn. Then nothing in the brain is indexed by task, and capacity is set by how many
units and context slots it has, not by how many tasks exist.

## Relevance to building brain-like AI

### What Brain World does today (`game/world/brain.js`)
- **Shared:** one fixed random expansion of 1,000 units, one actor `P` and one critic `v` serve
  walk, grasp, listen, read and write. There are no per-task heads, and the learning rule (trace
  times dopamine) is the same for every skill.
- **Replay against forgetting:** 30% of later episodes rehearse an earlier skill. Without it,
  grasp, listen and read fell to chance once the creature learned to write (README).
- **Context inferred, not told (issue #60, 2026-10-13).** `Brain.encode(x, slot)` applies the gate
  row of one of 8 context slots, a fixed random half of the units (context-dependent gating, Masse,
  Grant & Freedman 2018). The slot comes from `brain.infer(z)`: `z` is the running max over the
  episode of five thresholded channels (white, colour, tone, fovea letter, board), matched to slot
  prototypes by adaptive resonance; each training episode commits `z` to its slot or founds one.
  Over seeds 1-10, 9 graduate (told: 10), mean kept scores 0.87 / 0.70 / 0.59 / 0.65 (told:
  0.82 / 0.69 / 0.55 / 0.66), and every skill ends at least 99.9% of its episodes in its own slot.
  The failing seed infers correctly but never learns to read (README "Inferred context").
- **Still task labels, in two places.** The at-board input is `mode === "write"`, a task label
  under another name until a second board task exists. And `step()` picks the allowed action set
  (body, habit or pen) from the mode (issue #61).
- **What gating bought:** per the README, the jump from 5 to 8 of 10 passing seeds came from
  growing the layer from 600 to 1,000 units; gating added a little on top (9 of 10), mostly to
  listening. It did not let replay be halved.
- The code below is a standalone toy of the same selector, not Brain World's code.

### Engineering, not biology: saving, slots and growth
- A brain is never saved. A saved learner must hold everything that picks its next action, and an
  inferred context adds to that list: the prototypes and their use counts, or a loaded brain no
  longer recognises its own tasks. See [[saving-and-reusing-a-trained-brain]].
- **Slot reclaim:** with fixed capacity, a new scene that finds every slot taken can take over a
  slot that never consolidated (few uses) before merging into the nearest one. **Growth** (more
  slots or units) is a capacity change the owner makes, never one a task triggers. Both are design
  choices, not measurements.

## Code
An adaptive-resonance clusterer (after Carpenter & Grossberg 1987) sees noisy binary scene
summaries from three hidden types, with no labels. It joins a prototype when enough bits agree
(the vigilance), and founds a new one otherwise. The asserts check, over five seeds, that it founds
exactly three prototypes and that each scene type maps to exactly one of them.

```python
import numpy as np

# Adaptive-resonance clustering of noisy binary "scene summaries". No labels: it must found one
# prototype per scene type by itself, from a fixed bank of slots.
N_BITS, N_TYPES, NOISE, SLOTS = 100, 3, 0.05, 8
VIGILANCE, RATE = 0.7, 0.1   # match needed to join a prototype; how fast a prototype moves

def run(seed):
    rng = np.random.default_rng(seed)
    types = rng.integers(0, 2, size=(N_TYPES, N_BITS))     # three hidden scene types
    proto = np.zeros((SLOTS, N_BITS))                        # fixed capacity, like a fixed set of neurons
    used = np.zeros(SLOTS, dtype=bool)
    hits = np.zeros((N_TYPES, SLOTS), dtype=int)             # for the check only; the learner never sees it
    for _ in range(600):
        t = rng.integers(N_TYPES)
        x = np.where(rng.random(N_BITS) < NOISE, 1 - types[t], types[t])   # flip 5% of bits
        match = 1 - np.abs(proto - x).mean(axis=1)           # share of bits that agree with each prototype
        match[~used] = -1
        best = int(np.argmax(match))
        if used.any() and match[best] >= VIGILANCE:          # resonance: join and move the prototype
            proto[best] += RATE * (x - proto[best])
        else:                                                # mismatch reset: found a new prototype
            if used.all():
                raise RuntimeError("out of slots")
            best = int(np.argmin(used))
            proto[best], used[best] = x, True
        hits[t, best] += 1
    return used, hits

for seed in range(5):
    used, hits = run(seed)
    assert used.sum() == N_TYPES, f"seed {seed}: founded {used.sum()} prototypes"
    owner = hits.argmax(axis=1)
    assert len(set(owner)) == N_TYPES, f"seed {seed}: two scene types share a prototype"
    assert (hits[np.arange(N_TYPES), owner] == hits.sum(axis=1)).all(), f"seed {seed}: a type split"
print("prototypes founded:", int(used.sum()), "| scenes per prototype:", hits[:, used].tolist())
```

The scene types here are random and far apart, and the noise is mild, so this is the easy case.
Real scene summaries overlap, and the vigilance then decides whether two situations count as one
task or two.

## Open questions
- How does the brain decide that a situation is a new task rather than noise in an old one? The
  thalamus and prefrontal cortex are candidates; the mechanism is open.
- Are a few general organs enough, or does a brain also carve task-specific circuits through
  development and practice (for example reading areas)? See [[brain-development-and-critical-periods]].
- Can a context selector built on general sensory channels find tasks it was not designed for?
  In Brain World this is untested.
- How much of the reuse found in multitask networks (motifs, compositional rules) holds in brains
  is still being tested against recordings.

## Related
- [[memory-systems]] - complementary learning systems, catastrophic forgetting and replay.
- [[attention-and-working-memory]] - top-down gating and the thalamus, the candidate task switch.
- [[learning-and-plasticity]] - the three-factor rule every Brain World skill shares.
- [[saving-and-reusing-a-trained-brain]] - what a save must hold, including context memory.
- [[build-a-brain-like-learner]] - stage 6 integrates the organs into one continual learner.
- [[neuromodulators]] - uncertainty signals as a gate on plasticity.
- [[prefrontal-cortex-and-abstraction]] - task sets, rules and the prefrontal cortex.
- [Brain World](../game/world/README.md) - five skills in one shared network that infers its own context slot.

## References
- Yang, Joglekar, Song, Newsome & Wang (2019) "Task representations in neural networks trained to perform many cognitive tasks", *Nat Neurosci* 22:297. doi:10.1038/s41593-018-0310-2
- Driscoll, Shenoy & Sussillo (2024) "Flexible multitask computation in recurrent networks utilizes shared dynamical motifs", *Nat Neurosci* 27:1349. doi:10.1038/s41593-024-01668-6
- Wang et al. (2018) "Prefrontal cortex as a meta-reinforcement learning system", *Nat Neurosci* 21:860. doi:10.1038/s41593-018-0147-8
- Reed et al. (2022) "A Generalist Agent", *Transactions on Machine Learning Research*. https://arxiv.org/abs/2205.06175
- Doya (1999) "What are the computations of the cerebellum, the basal ganglia and the cerebral cortex?", *Neural Networks* 12:961. doi:10.1016/S0893-6080(99)00046-5
- McClelland, McNaughton & O'Reilly (1995) "Why there are complementary learning systems in the hippocampus and neocortex", *Psychol Rev* 102:419. doi:10.1037/0033-295X.102.3.419
- Kumaran, Hassabis & McClelland (2016) "What learning systems do intelligent agents need?", *Trends Cogn Sci* 20:512. doi:10.1016/j.tics.2016.05.004
- Eliasmith et al. (2012) "A large-scale model of the functioning brain", *Science* 338:1202. doi:10.1126/science.1225266
- McCloskey & Cohen (1989) "Catastrophic interference in connectionist networks: the sequential learning problem", *Psychology of Learning and Motivation* 24:109. doi:10.1016/S0079-7421(08)60536-8
- Schultz, Dayan & Montague (1997) "A neural substrate of prediction and reward", *Science* 275:1593. doi:10.1126/science.275.5306.1593
- Wilson & McNaughton (1994) "Reactivation of hippocampal ensemble memories during sleep", *Science* 265:676. doi:10.1126/science.8036517
- Rikhye, Gilra & Halassa (2018) "Thalamic regulation of switching between cortical representations enables cognitive flexibility", *Nat Neurosci* 21:1753. doi:10.1038/s41593-018-0269-z
- Heald, Lengyel & Wolpert (2021) "Contextual inference underlies the learning of sensorimotor repertoires", *Nature* 600:489. doi:10.1038/s41586-021-04129-3
- Collins & Frank (2013) "Cognitive control over learning: creating, clustering, and generalizing task-set structure", *Psychol Rev* 120:190. doi:10.1037/a0030852
- Zenke, Poole & Ganguli (2017) "Continual learning through synaptic intelligence", ICML. https://arxiv.org/abs/1703.04200
- Yu & Dayan (2005) "Uncertainty, neuromodulation, and attention", *Neuron* 46:681. doi:10.1016/j.neuron.2005.04.026
- Carpenter & Grossberg (1987) "A massively parallel architecture for a self-organizing neural pattern recognition machine", *Computer Vision, Graphics, and Image Processing* 37:54. doi:10.1016/S0734-189X(87)80014-2
- Masse, Grant & Freedman (2018) "Alleviating catastrophic forgetting using context-dependent gating and synaptic stabilization", *PNAS* 115:E10467. doi:10.1073/pnas.1803839115
