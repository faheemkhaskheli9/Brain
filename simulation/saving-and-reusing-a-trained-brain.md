---
title: Saving and reusing a trained brain
category: simulation
tags: [checkpoint, save, load, serialization, continual-learning, catastrophic-forgetting, replay, consolidation, numpy, pickle, reproducibility]
use_cases:
  - how do I save a trained brain-like learner and load it later
  - what must a checkpoint of a learning agent contain
  - why does a loaded agent not act like the one I saved
  - is it safe to load someone else's model file
  - how does a brain keep what it learned, and how can a model learn more after loading
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1038/385533a0
  - https://doi.org/10.1016/j.tics.2016.05.004
  - https://doi.org/10.1038/s41467-020-17866-2
  - https://arxiv.org/abs/1811.11682
  - https://numpy.org/doc/stable/reference/generated/numpy.load.html
  - https://docs.python.org/3/library/pickle.html
---

# Saving and reusing a trained brain

## Summary
A brain keeps what it learned in its synapses, stabilises those changes over hours, and
consolidates them over days through replay. A simulated learner has to do the same within one
run, and then also be **saved**, which no brain does. A useful save holds everything that
decides the learner's next action, not just its weights, and it loads without running code
from the file. Learning more after loading brings back catastrophic forgetting, which replay
reduces in brains and in networks.

## How it works

### How the brain keeps a memory (established)
- **In the synapses.** A learned change is a change in synaptic strength (see
  [[learning-and-plasticity]]). Early LTP fades within hours. Late LTP needs new proteins and
  lasts. Frey & Morris (1997) showed that a weakly stimulated synapse sets a **tag**, and can
  capture proteins made after strong stimulation elsewhere on the same neuron, so its change
  lasts too (synaptic tagging and capture).
- **Systems consolidation.** The hippocampus learns fast. Replay of hippocampal activity,
  mostly during sleep, slowly trains the neocortex, which interleaves the new memory with old
  ones (complementary learning systems; Kumaran, Hassabis & McClelland 2016). See
  [[memory-systems]] and [[sleep-and-memory-consolidation]].

### What forgetting looks like in a network (established)
A network that stores every task in the same weights loses old tasks when it trains on a new
one: **catastrophic forgetting**. Replaying stored or generated examples of old tasks while
learning the new one reduces it. Rolnick et al. (2019) did this with a replay buffer of past
experience in reinforcement learning. Van de Ven, Siegelmann & Tolias (2020) replayed internal
representations made by the network itself instead of storing raw inputs.

### Saving is engineering, not biology
No brain is ever written to a file and read back. A save exists for the person running the
simulation. To make a loaded learner act exactly as the saved one would have, the save needs:

| Part | Why | Brain World (`game/world/brain.js`) |
|---|---|---|
| Learned weights | the memory itself | `v` (critic), `P` (actor) |
| Fixed random wiring | random projections are part of the brain; a different draw makes the weights meaningless | `idx`, `wIn`, `bias`, `gate` are stored, not regenerated |
| Normaliser state | running statistics change every output | `hh`, a running mean of hidden activity |
| Consolidation state | per-synapse importance or anchors, if the learner protects old skills | none yet (issue #56) |
| RNG state | without it, two copies sample different actions | `rand`, the state at the start of the episode |
| Progress | where training stands | `stage`, `episode`, success windows |
| Version | so old files fail loudly or are migrated, never read wrongly | `version: 3` |
| Metadata | what the brain can do and how it was made | none yet (issue #55) |

Storing only a seed instead of the fixed wiring makes the file smaller, but a later change to
the code that draws the wiring would quietly build a different brain under the old weights.
Brain World stores the wiring and checks every array's shape before loading.

### Loading safely in Python
`np.savez` writes plain numeric arrays into one `.npz` file. `np.load(path, allow_pickle=False)`
reads them back and refuses object arrays, which would need pickle (`allow_pickle=False` has been
the default since numpy 1.16.3). Never load a `pickle` file someone else made: the Python
documentation warns that unpickling can run arbitrary code.

## Relevance to building brain-like AI
- **Save the whole state that picks an action.** Weights alone reload a learner that acts
  differently, because the normaliser, the RNG and the random wiring are part of it.
- **Use a saved brain with learning off** to test what it knows. A learner that keeps learning
  while it is tested changes under you (issue #52).
- **Plan for learning after loading.** Adding a skill to a saved brain is a continual-learning
  problem. Replay of old skills is the established remedy. Brain World already replays earlier
  stages during training.
- **Check a load with behaviour, not just shapes.** The test below, and Brain World's
  `test_brain.mjs`, assert that the copy takes the same actions as the original.

## Code
Train Brain Lab's level 8 forager (the actor-critic of `game/sim.py`, inlined here), save it
with `np.savez`, load it with pickle off, and check the copy picks the same actions.

```python
import io
import numpy as np

# Brain Lab level 8 forager (game/sim.py): actor-critic on a 5x5 grid, food in the far corner.
SIZE, GAMMA, LAM, A_V, A_PI = 5, 0.95, 0.9, 0.3, 2.0
MOVES = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right

def act(pi, s, rng):
    p = np.exp(pi[s] - pi[s].max()); p /= p.sum()
    return rng.choice(4, p=p), p

def move(pos, a):
    return (min(max(pos[0] + MOVES[a][0], 0), SIZE - 1), min(max(pos[1] + MOVES[a][1], 0), SIZE - 1))

def train(steps=4000, seed=0):
    rng, n = np.random.default_rng(seed), SIZE * SIZE
    V, pi = np.zeros(n), np.zeros((n, 4))
    pos, e_v, e_pi = (0, 0), np.zeros(n), np.zeros((n, 4))
    for _ in range(steps):
        s = pos[1] * SIZE + pos[0]
        a, p = act(pi, s, rng)
        pos = move(pos, a)
        ate = pos == (SIZE - 1, SIZE - 1)
        delta = float(ate) + (0.0 if ate else GAMMA * V[pos[1] * SIZE + pos[0]]) - V[s]  # dopamine
        e_v *= GAMMA * LAM; e_pi *= GAMMA * LAM
        e_v[s] += 1; e_pi[s] += np.eye(4)[a] - p                                       # eligibility
        V += A_V * delta * e_v; pi += A_PI * delta * e_pi                               # third factor
        if ate:
            pos, e_v, e_pi = (0, 0), np.zeros(n), np.zeros((n, 4))
    return V, pi

def rollout(pi, seed, steps=200):
    rng, pos, actions = np.random.default_rng(seed), (0, 0), []
    for _ in range(steps):
        a, _ = act(pi, pos[1] * SIZE + pos[0], rng)
        actions.append(int(a)); pos = move(pos, a)
        if pos == (SIZE - 1, SIZE - 1):
            pos = (0, 0)
    return actions

V, pi = train()
f = io.BytesIO()   # a file path works the same way
np.savez(f, version=1, size=SIZE, gains=[GAMMA, LAM, A_V, A_PI], V=V, pi=pi)
f.seek(0)
with np.load(f, allow_pickle=False) as z:   # plain numeric arrays only: loading runs no code
    assert int(z["version"]) == 1 and int(z["size"]) == SIZE
    V2, pi2 = z["V"], z["pi"]

assert np.array_equal(V, V2) and np.array_equal(pi, pi2)
assert rollout(pi, seed=7) == rollout(pi2, seed=7)   # same weights + same RNG seed = same actions
print("first moves from the start:", [["up", "down", "left", "right"][a] for a in rollout(pi2, seed=7)[:8]])

g = io.BytesIO()
np.save(g, np.array([{"not": "numbers"}], dtype=object), allow_pickle=True)
g.seek(0)
try:
    np.load(g, allow_pickle=False)
    raise AssertionError("an object array loaded without pickle")
except ValueError:
    print("object array refused without allow_pickle=True")
```

The trained forager walks the shortest path, eight moves, to the food. The forager's
eligibility traces are not saved because they reset whenever it eats. A learner whose traces
carry across a save would need them in the file too.

## Open questions
- **Hypothesis:** per-synapse importance in continual-learning methods (synaptic intelligence,
  Zenke, Poole & Ganguli 2017; elastic weight consolidation, Kirkpatrick et al. 2017) models
  **metaplasticity**, where a synapse's history changes how easily it changes again. Benna &
  Fusi (2016) model consolidation as states inside a synapse that change at different speeds.
  How the brain marks which synapses matter is not settled.
- **Hypothesis:** the prefrontal cortex infers which task or context is active and selects the
  matching skill, so the brain need not be told the task (Heald, Lengyel & Wolpert 2021 show
  contextual inference in motor learning). Brain World is still told its task (issue #57).
- How much of consolidation happens during sleep replay, and how much awake, is still debated.

## Related
- [[learning-and-plasticity]] - LTP, STDP and the dopamine-gated rule whose weights are saved here.
- [[memory-systems]] - complementary learning systems and replay.
- [[sleep-and-memory-consolidation]] - when replay happens in the brain.
- [[build-a-brain-like-learner]] - the staged learner a save has to capture.
- [[evaluating-brain-models]] - scoring a loaded brain the same way every time.
- [Brain World](../game/world/README.md) - **Save brain** and **Load brain** in the browser, tested by `test_brain.mjs`.

## References
- Frey & Morris (1997) "Synaptic tagging and long-term potentiation", *Nature* 385:533. doi:10.1038/385533a0
- Kumaran, Hassabis & McClelland (2016) "What learning systems do intelligent agents need?", *Trends Cogn Sci* 20:512. doi:10.1016/j.tics.2016.05.004
- van de Ven, Siegelmann & Tolias (2020) "Brain-inspired replay for continual learning with artificial neural networks", *Nat Commun* 11:4069. doi:10.1038/s41467-020-17866-2
- Rolnick et al. (2019) "Experience Replay for Continual Learning", NeurIPS. https://arxiv.org/abs/1811.11682
- Zenke, Poole & Ganguli (2017) "Continual learning through synaptic intelligence", ICML. https://arxiv.org/abs/1703.04200
- Kirkpatrick et al. (2017) "Overcoming catastrophic forgetting in neural networks", *PNAS* 114:3521. doi:10.1073/pnas.1611835114
- Benna & Fusi (2016) "Computational principles of synaptic memory consolidation", *Nat Neurosci* 19:1697. doi:10.1038/nn.4401
- Heald, Lengyel & Wolpert (2021) "Contextual inference underlies the learning of sensorimotor repertoires", *Nature* 600:489. doi:10.1038/s41586-021-04129-3
- numpy `load` documentation (`allow_pickle`). https://numpy.org/doc/stable/reference/generated/numpy.load.html
- Python `pickle` documentation (security warning). https://docs.python.org/3/library/pickle.html
