---
title: Memory systems and complementary learning
category: function
tags: [memory, hippocampus, consolidation, sleep, replay, working-memory, complementary-learning-systems, hopfield, catastrophic-forgetting]
use_cases:
  - how does the brain store and recall memories
  - how does the brain learn continually without catastrophic forgetting
  - design a memory architecture for an AI agent inspired by the hippocampus
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1037/0033-295X.102.3.419
  - https://doi.org/10.1016/j.tics.2016.05.004
  - https://doi.org/10.1073/pnas.79.8.2554
  - https://doi.org/10.1073/pnas.1611835114
---

# Memory systems and complementary learning

## Summary
The brain has several memory systems, not one. The key design idea is
**Complementary Learning Systems (CLS)**. The **hippocampus** learns fast, storing
individual episodes after a single exposure in sparse, non-overlapping codes. The
**neocortex** learns slowly, gradually extracting general structure in
overlapping, distributed codes. During rest and sleep the hippocampus **replays**
recent memories, interleaving them into cortical training. This is how the brain
learns new things without overwriting old ones, the problem known in AI as
*catastrophic forgetting*.

## How it works

### Memory taxonomy
| System | Content | Main structures | Learning speed |
|---|---|---|---|
| Working memory | What you hold "in mind" now (~4 items) | Prefrontal cortex, persistent activity | Seconds |
| Episodic | Specific events ("my breakfast today") | Hippocampus → cortex | One-shot |
| Semantic | Facts and concepts ("Paris is in France") | Neocortex (temporal lobe) | Slow, extracted from episodes |
| Procedural | Skills and habits | Basal ganglia, cerebellum | Slow, practice |
| Priming / perceptual | Faster processing of seen stimuli | Sensory cortex | Implicit |
| Emotional / conditioning | Fear, value associations | Amygdala | Fast |

Patient H.M. (hippocampus removed in 1953) could not form new episodic memories
but could still learn motor skills. This is the classic evidence that the systems
are separable.

### The hippocampal circuit
- **Dentate gyrus: pattern separation.** Makes similar experiences distinct with
  very sparse codes, which avoids interference.
- **CA3: pattern completion.** A recurrent auto-associative network (Hopfield-like)
  that recalls a whole memory from a partial cue.
- **CA1**: compares recall with the current input and sends the result back to cortex.
- **Place cells** (O'Keefe) and **grid cells** (Moser & Moser) in the entorhinal
  cortex form a cognitive map of space. The same machinery may map abstract
  concept spaces (a hypothesis with growing support).

### Consolidation and sleep
- During slow-wave sleep, **sharp-wave ripples** in the hippocampus replay recent
  experience at ~10-20× speed, coordinated with cortical spindles and slow
  oscillations. Disrupting ripples impairs memory.
- Replay is selective: it favours rewarded or surprising events, like prioritised
  experience replay in RL.
- Over weeks to years, memories become less hippocampus-dependent
  (systems consolidation). Detailed episodes may stay hippocampus-dependent
  (multiple trace theory); this part is still debated.
- **Synaptic consolidation**: important synapses become less plastic (protein
  synthesis, synaptic tagging), protecting old knowledge. This inspired Elastic
  Weight Consolidation ([[brain-inspired-learning-algorithms]]).
- Recalled memories become labile again and are re-stored (reconsolidation), so
  memory is reconstructive, not a recording.

### Forgetting is a feature
Active forgetting (interference, decay, synapse pruning) keeps memory general and
retrieval fast. The brain is lossy by design.

## Relevance to building brain-like AI
CLS maps directly onto an architecture you can build today:

| Brain | AI component |
|---|---|
| Hippocampus (fast, episodic, sparse) | Episodic buffer / key-value store / vector DB with retrieval |
| Neocortex (slow, generalising) | Main neural network weights |
| Replay during sleep | Offline interleaved training on replayed and new data (experience replay, generative replay) |
| Synaptic consolidation | EWC / synaptic intelligence weight-importance penalties |
| Pattern separation | Sparse, high-dimensional keys |
| Pattern completion | Attention over memory (modern Hopfield networks ≈ transformer attention, Ramsauer et al. 2020) |
| Working memory | Context window / recurrent state |

LLM agents with a vector store plus periodic fine-tuning are a crude CLS: fast
retrieval memory plus slow weight learning. The missing piece is principled
consolidation from the fast store into the weights.

## Code: Hopfield network (CA3-style pattern completion)

```python
import numpy as np

rng = np.random.default_rng(0)
N, P = 200, 10                                   # neurons, stored patterns
patterns = rng.choice([-1, 1], size=(P, N))

W = patterns.T @ patterns / N                    # Hebbian one-shot storage
np.fill_diagonal(W, 0)

def recall(cue, steps=10):
    s = cue.copy()
    for _ in range(steps):
        s = np.sign(W @ s)
        s[s == 0] = 1
    return s

cue = patterns[3].copy()
flip = rng.choice(N, size=60, replace=False)     # corrupt 30% of bits
cue[flip] *= -1
out = recall(cue)
overlap = (out @ patterns[3]) / N
print(f"overlap with stored memory after recall: {overlap:.2f}")  # ~1.00
assert overlap > 0.95
```

A classical Hopfield network stores about 0.14·N random patterns before recall
breaks down. Modern (dense) Hopfield networks have exponential capacity and are
mathematically equivalent to attention.

## Open questions
- What exactly sleep replay optimises, and how the cortex integrates replayed data.
- How memories are indexed and how much of an episode's detail is kept.
- How the hippocampus decides what is worth storing.

## Related
- [[learning-and-plasticity]] - synaptic mechanisms behind storage.
- [[brain-inspired-learning-algorithms]] - EWC and replay in code.
- [[build-a-brain-like-learner]] - CLS as stage 3 of the roadmap.
- [[brain-structure-overview]] - where these regions sit.

## References
- McClelland, McNaughton & O'Reilly (1995) "Why there are complementary learning systems in the hippocampus and neocortex", *Psychological Review* 102:419. doi:10.1037/0033-295X.102.3.419
- Kumaran, Hassabis & McClelland (2016) "What learning systems do intelligent agents need? Complementary learning systems theory updated", *Trends Cogn Sci* 20:512. doi:10.1016/j.tics.2016.05.004
- Hopfield (1982), *PNAS* 79:2554. doi:10.1073/pnas.79.8.2554
- Kirkpatrick et al. (2017) "Overcoming catastrophic forgetting in neural networks", *PNAS* 114:3521. doi:10.1073/pnas.1611835114
- Ramsauer et al. (2020) "Hopfield Networks is All You Need", arXiv:2008.02217.
- Buzsáki (2015) "Hippocampal sharp wave-ripple: a cognitive biomarker for episodic memory and planning", *Hippocampus* 25:1073.
