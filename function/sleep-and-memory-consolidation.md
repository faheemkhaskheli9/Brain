---
title: Sleep and memory consolidation
category: function
tags: [sleep, consolidation, replay, sharp-wave-ripples, slow-oscillations, spindles, synaptic-homeostasis, catastrophic-forgetting]
use_cases:
  - what happens to memories during sleep
  - why does the brain replay experiences during sleep
  - add an offline replay or sleep phase to a continual-learning system
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1152/physrev.00032.2012
  - https://doi.org/10.1126/science.8036517
  - https://doi.org/10.1038/nn.2384
  - https://doi.org/10.1016/j.neuron.2013.12.025
---

# Sleep and memory consolidation

## Summary
Sleep is not idle time for memory. During deep non-REM sleep the hippocampus
**replays** the day's experiences in compressed bursts called sharp-wave ripples,
locked to cortical slow oscillations and spindles. This replay is the brain's
version of offline, interleaved training: it moves new memories into the cortex
without overwriting old ones. Whether sleep also **downscales** synapses overall
(the synaptic homeostasis hypothesis) is a live **hypothesis**, not settled.

## How it works

### Sleep stages (established)
- Sleep alternates between **non-REM** (stages N1, N2 and N3; N3 is slow-wave
  sleep) and **REM** sleep, in cycles of roughly 90 minutes. Slow-wave sleep
  dominates the first half of the night and REM the second (Rasch & Born 2013).
- Three non-REM rhythms matter for memory (Rasch & Born 2013):
  - **Slow oscillations** (< 1 Hz) in neocortex: whole populations swing between
    active "up" states and silent "down" states.
  - **Spindles** (about 11-16 Hz) from the thalamus, mostly in N2.
  - **Sharp-wave ripples** (about 150-250 Hz in rodents) in the hippocampus
    (Buzsáki 2015).
- The three nest: ripples tend to ride spindle troughs, which ride slow-oscillation
  up states. This timing is thought to open a window for hippocampus-to-cortex
  transfer.

### Replay (established)
- Place cells that fired together on a track fire together again in later sleep
  (Wilson & McNaughton 1994), in the same order and many times faster than the
  original run. See [[spatial-navigation]] for place cells.
- Replay is causal, not a side effect: suppressing ripples during post-training
  sleep impaired rats' spatial learning (Girardeau et al. 2009).
- Replay is not only in sleep. During awake pauses ripples also replay paths,
  sometimes in reverse right after reward (Foster & Wilson 2006), which looks like
  credit being passed back along the path, as in TD learning
  ([[learning-and-plasticity]]).
- In humans, cueing a memory during slow-wave sleep strengthens it: an odour
  present during learning and re-presented in slow-wave sleep improved recall of
  card locations, and the same odour in REM or awake did not (Rasch et al. 2007).
- Boosting slow oscillations also helps. Slow oscillating transcranial stimulation
  in early sleep (Marshall et al. 2006) and sounds timed to slow-oscillation up
  states (Ngo et al. 2013) improved overnight retention of word pairs.

### Systems consolidation
- **Active systems consolidation** (Rasch & Born 2013): replay in the hippocampus
  repeatedly drives the cortex, which slowly builds its own copy. This is the sleep
  half of complementary learning systems ([[memory-systems]]). The broad picture
  is well supported; how much of an episode's detail ever leaves the hippocampus is
  still debated.

### Synaptic homeostasis (hypothesis)
- Tononi & Cirelli (2014) propose that waking learning mostly strengthens synapses,
  which costs energy and saturates plasticity, and that slow-wave sleep scales all
  synapses down, keeping the relative pattern while restoring headroom.
- Supporting evidence: in mouse cortex, the axon-spine interface was about 18%
  smaller after sleep than after wake (de Vivo et al. 2017).
- Against or unresolved: some synapses grow during sleep, and replay-driven
  strengthening and global downscaling may both happen. Treat SHY as a hypothesis.

### REM sleep (open)
REM has been linked to emotional memory and to procedural skills, but the evidence
is weaker and more mixed than for slow-wave sleep. Treat specific REM functions as
open questions.

## Relevance to building brain-like AI
| Brain | AI component |
|---|---|
| Sharp-wave ripple replay | Experience replay buffer, sampled offline |
| Replay favours reward and surprise | Prioritised experience replay |
| Hippocampus drives cortex during sleep | Distillation from a fast episodic store into slow weights |
| Interleaving old and new memories | Rehearsal against catastrophic forgetting |
| Synaptic downscaling (hypothesis) | Weight decay or normalisation applied in an offline phase |
| Dreaming as generation (hypothesis) | Generative replay; Hinton's wake-sleep algorithm (Hinton et al. 1995) |

**In this repo.** Brain Lab level 6, *Sleep on it*, has you learn task B with or
without replay of task A ([game/README.md](../game/README.md)). In
[Brain World](../game/world/), 30% of later episodes rehearse an earlier skill;
without that replay, grasping, listening and reading fell to chance once the
creature learned to write, and halving replay to 15% made one seed in ten fail
([game/world/README.md](../game/world/README.md)). That fraction is a game gain,
not a measurement.

## Code: replay stops catastrophic forgetting

A linear associator learns task A, then task B with a local delta rule. Without
replay, B overwrites A. With A interleaved into the night's training, both survive.
Replaying every A item is idealised; the brain replays a selected subset.

```python
import numpy as np

rng = np.random.default_rng(0)
n_in, n_out, n_items = 60, 10, 20
XA, XB = rng.normal(size=(2, n_items, n_in)) / np.sqrt(n_in)   # task A and task B inputs
YA, YB = rng.normal(size=(2, n_items, n_out))                  # their target outputs

def err(W, X, Y):
    return float(np.mean((X @ W - Y) ** 2))

def train(W, X, Y, epochs, lr=0.5):
    for _ in range(epochs):
        for i in rng.permutation(len(X)):                      # local delta rule, one item at a time
            W += lr * np.outer(X[i], Y[i] - X[i] @ W)
    return W

W0 = train(np.zeros((n_in, n_out)), XA, YA, 200)               # "day 1": learn A
print(f"A error after day 1: {err(W0, XA, YA):.3f}")

W_awake = train(W0.copy(), XB, YB, 200)                        # "day 2": B only, no sleep
replay = np.concatenate([XB, XA]), np.concatenate([YB, YA])    # sleep: replay A interleaved with B
W_sleep = train(W0.copy(), *replay, 200)

for name, W in (("no replay", W_awake), ("replay", W_sleep)):
    print(f"{name:9s}  A error {err(W, XA, YA):.3f}   B error {err(W, XB, YB):.3f}")
assert err(W_sleep, XA, YA) < 0.25 * err(W_awake, XA, YA)      # replay protects A
assert err(W_sleep, XB, YB) < 0.05                             # and B is still learned
```

## Open questions
- What selects which memories get replayed, and how much replay is enough.
- Whether SHY-style downscaling and replay-driven strengthening coexist, and how.
- What REM sleep contributes to memory, if anything specific.
- Whether the cortex stores a full copy of an episode or only its gist.

## Related
- [[memory-systems]] - complementary learning systems, which sleep replay serves.
- [[brain-inspired-learning-algorithms]] - EWC and generative replay in code.
- [[learning-and-plasticity]] - the synaptic changes replay drives.
- [[spatial-navigation]] - the place cells whose replay was first recorded.
- [Brain World](../game/world/) - replay keeps a creature's old skills while it learns new ones.
- [Brain Lab](../game/README.md) - level 6, *Sleep on it*: learn task B with or without replay of task A.

## References
- Rasch & Born (2013) "About sleep's role in memory", *Physiol Rev* 93:681. doi:10.1152/physrev.00032.2012
- Wilson & McNaughton (1994) "Reactivation of hippocampal ensemble memories during sleep", *Science* 265:676. doi:10.1126/science.8036517
- Girardeau, Benchenane, Wiener, Buzsáki & Zugaro (2009) "Selective suppression of hippocampal ripples impairs spatial memory", *Nat Neurosci* 12:1222. doi:10.1038/nn.2384
- Foster & Wilson (2006) "Reverse replay of behavioural sequences in hippocampal place cells during the awake state", *Nature* 440:680. doi:10.1038/nature04587
- Rasch, Büchel, Gais & Born (2007) "Odor cues during slow-wave sleep prompt declarative memory consolidation", *Science* 315:1426. doi:10.1126/science.1138581
- Marshall, Helgadóttir, Mölle & Born (2006) "Boosting slow oscillations during sleep potentiates memory", *Nature* 444:610. doi:10.1038/nature05278
- Ngo, Martinetz, Born & Mölle (2013) "Auditory closed-loop stimulation of the sleep slow oscillation enhances memory", *Neuron* 78:545. doi:10.1016/j.neuron.2013.03.006
- Tononi & Cirelli (2014) "Sleep and the price of plasticity", *Neuron* 81:12. doi:10.1016/j.neuron.2013.12.025
- de Vivo et al. (2017) "Ultrastructural evidence for synaptic scaling across the wake/sleep cycle", *Science* 355:507. doi:10.1126/science.aah5982
- Buzsáki (2015) "Hippocampal sharp wave-ripple: a cognitive biomarker for episodic memory and planning", *Hippocampus* 25:1073. doi:10.1002/hipo.22488
- Hinton, Dayan, Frey & Neal (1995) "The wake-sleep algorithm for unsupervised neural networks", *Science* 268:1158. doi:10.1126/science.7761831
