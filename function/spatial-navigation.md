---
title: Spatial navigation and cognitive maps
category: function
tags: [navigation, place-cells, grid-cells, head-direction-cells, border-cells, path-integration, remapping, cognitive-map, successor-representation, hippocampus, entorhinal-cortex]
use_cases:
  - how does the brain know where it is
  - what are place cells and grid cells
  - build an agent that navigates with a cognitive map or path integration
  - represent knowledge as a map, not just space
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1016/0006-8993(71)90358-1
  - https://doi.org/10.1038/nature03721
  - https://doi.org/10.1523/JNEUROSCI.10-02-00420.1990
  - https://doi.org/10.1038/nn.4650
  - https://doi.org/10.1016/j.cell.2020.10.024
---

# Spatial navigation and cognitive maps

## Summary
The hippocampus and the entorhinal cortex next to it build a map of where the animal is.
**Place cells** fire at one location each; **grid cells** fire on a hexagonal lattice
that tiles the whole environment; **head-direction cells** fire for one heading,
like a compass; **border cells** fire along walls. Together they let an animal track
its position by adding up its own movements (**path integration**) and correct the
drift with landmarks. A leading hypothesis says the same machinery maps
non-spatial knowledge too, which makes it a template for structured memory in AI.

## How it works

### The cell types (established)
| Cell | Fires when | Where | Discovery |
|---|---|---|---|
| Place cell | The animal is in one spot of the room (its *place field*) | Hippocampus (CA1, CA3) | O'Keefe & Dostrovsky 1971 |
| Head-direction cell | The head points in one direction, wherever the animal is | Postsubiculum, thalamus and other areas | Taube, Muller & Ranck 1990 |
| Grid cell | The animal is on any vertex of a triangular (hexagonal) lattice covering the room | Medial entorhinal cortex | Hafting et al. 2005 |
| Border cell | The animal is near a wall in a given direction | Medial entorhinal cortex | Solstad et al. 2008 |

O'Keefe and the Mosers shared the 2014 Nobel Prize in Physiology or Medicine for
place and grid cells.

Grid spacing grows from the dorsal to the ventral end of the entorhinal cortex
(Hafting et al. 2005), and grid cells come in a few discrete **modules**, each with
its own scale (Stensola et al. 2012). A coding theory (hypothesis) says several
modules at different scales together pin down a position uniquely, like digits in a
number, giving a huge range from few cells (Fiete, Burak & Brookings 2008).

Grid-like signals have been found in humans too, both in fMRI (Doeller, Barry &
Burgess 2010) and in single neurons recorded from epilepsy patients (Jacobs et al. 2013).

### Path integration (established behaviour, mechanism partly hypothesis)
An animal that adds up its own velocity knows where it is relative to its start, and
can run straight home along a path it never took. Desert ants do this after long,
winding foraging trips (Müller & Wehner 1988). Every step is sensed with some error,
so the estimate **drifts**, and the error grows with distance walked. Landmarks
correct it: place fields anchor to visible cues.

That grid cells *are* the brain's path integrator is the leading hypothesis, backed
by models (continuous attractor networks) and by the finding that networks trained
to path-integrate develop grid-like units on their own (Banino et al. 2018). It is
not settled.

### Remapping (established)
Move the animal to a different room and place cells **remap**: each cell may get a
new field, stop firing, or start firing, so each room gets its own map (Muller &
Kubie 1987). Grid cells keep their lattice but shift and rotate it as a whole
(Fyhn et al. 2007). The
hippocampus thus stores many maps and picks one per context.

### Cognitive maps for knowledge (hypothesis)
Tolman (1948) argued that rats learn a *cognitive map* of a maze, not a chain of
turns, because they take novel shortcuts. Current theories generalise the idea:

- **Successor representation (SR).** Place cells may encode not where you are but
  where you are *likely to go next*: the expected future occupancy of each state
  (Stachenfeld, Botvinick & Gershman 2017). The SR is learnable by a TD rule, the
  same rule as dopamine (see [[learning-and-plasticity]]), and makes value
  computation a single dot product.
- **Tolman-Eichenbaum Machine (TEM).** Entorhinal cells learn the *structure* of a
  task (how states relate), the hippocampus binds that structure to the current
  sensory details, and the same structure transfers to new environments. Trained on
  this, the model grows grid-like and place-like cells (Whittington et al. 2020).
- Grid-like fMRI signals appear when people navigate an abstract two-dimensional
  "space" of bird shapes (Constantinescu, O'Reilly & Behrens 2016), which suggests
  the map is not only for physical space.

## Relevance to building brain-like AI
- **Factor structure from content.** TEM separates "how things relate" from "what is
  here", which is what lets a map transfer to a new world. A memory system for an
  agent can do the same: a reusable relational scaffold plus fast one-shot binding of
  content (compare [[memory-systems]]).
- **Predictive maps.** The successor representation sits between model-free and
  model-based RL: it adapts at once when rewards move, without replanning. It is a
  cheap upgrade to a TD learner (see [[build-a-brain-like-learner]]).
- **Vector navigation.** A grid-like code gives a metric, so a goal vector is a
  subtraction, and shortcuts come for free (Banino et al. 2018).
- **Drift and correction.** Any agent that integrates its own motion (robots, SLAM)
  meets the same trade-off between dead reckoning and landmark resets.

## Code
A grid cell's firing map from three plane waves 60° apart, and a successor
representation learned by TD on a ring of states, checked against its closed form.

```python
import numpy as np

# Grid cell: sum of three cosine gratings 60 degrees apart gives a hexagonal lattice.
spacing = 0.3
k = 4 * np.pi / (np.sqrt(3) * spacing)
xs = np.linspace(0, 1, 60)
X, Y = np.meshgrid(xs, xs)
rate = sum(np.cos(k * (X * np.cos(t) + Y * np.sin(t))) for t in (0, np.pi / 3, 2 * np.pi / 3))
rate = (rate + 1.5) / 4.5                      # 0..1
print("grid map peaks:", int((rate > 0.95).sum()), "pixels at firing > 95%")

def g(p):
    return (sum(np.cos(k * (p[0] * np.cos(t) + p[1] * np.sin(t))) for t in (0, np.pi / 3, 2 * np.pi / 3)) + 1.5) / 4.5
p, a = np.array([0.2, 0.3]), spacing * np.array([np.cos(np.pi / 6), np.sin(np.pi / 6)])
assert abs(g(p) - g(p + a)) < 1e-9             # one lattice step away fires the same

# Successor representation: M[s, s'] = expected discounted future visits to s' from s.
n, gamma, alpha = 10, 0.9, 0.01
T = np.zeros((n, n))
for s in range(n):                             # random walk on a ring
    T[s, (s - 1) % n] = T[s, (s + 1) % n] = 0.5
M = np.zeros((n, n))
rng = np.random.default_rng(0)
s = 0
for step in rng.choice([-1, 1], size=200_000):
    s2 = (s + step) % n
    M[s] += alpha * (np.eye(n)[s] + gamma * M[s2] - M[s])   # TD update, like dopamine
    s = s2
exact = np.linalg.inv(np.eye(n) - gamma * T)
print("SR learned by TD, max error vs closed form:", round(float(np.abs(M - exact).max()), 2))
assert np.abs(M - exact).max() < 0.3
reward = np.zeros(n); reward[5] = 1
print("value of each state = M @ reward:", np.round(M @ reward, 2))
```

The game's level 11, *Find your way home*, uses the grid map above as its
background and a noisy path integrator with landmark resets (`game/sim.py`).

## Open questions
- Do grid cells compute path integration, or do they inherit it from elsewhere?
- How are many maps stored without interfering, and what triggers remapping?
- Is the hippocampal map really used for abstract knowledge in everyday thought, or
  only in tasks built to look like spaces?
- How do place, grid and successor-representation accounts fit into one model?

## Related
- [[memory-systems]] - the hippocampus stores episodes on this map, and replays paths on it.
- [[learning-and-plasticity]] - the TD rule that learns both value and the successor representation.
- [[build-a-brain-like-learner]] - where a predictive map fits in the roadmap.
- [[brain-structure-overview]] - where the hippocampus and entorhinal cortex sit.
- [[brain-rhythms-and-oscillations]] - theta, and place cells' phase precession against it.
- [Brain Lab](../game/README.md) - level 11, *Find your way home*: noisy path integration, landmark resets and a grid cell's map.

## References
- O'Keefe & Dostrovsky (1971) "The hippocampus as a spatial map. Preliminary evidence from unit activity in the freely-moving rat", *Brain Research* 34:171. doi:10.1016/0006-8993(71)90358-1
- Taube, Muller & Ranck (1990) "Head-direction cells recorded from the postsubiculum in freely moving rats. I.", *J Neurosci* 10:420. doi:10.1523/JNEUROSCI.10-02-00420.1990
- Hafting, Fyhn, Molden, Moser & Moser (2005) "Microstructure of a spatial map in the entorhinal cortex", *Nature* 436:801. doi:10.1038/nature03721
- Solstad, Boccara, Kropff, Moser & Moser (2008) "Representation of geometric borders in the entorhinal cortex", *Science* 322:1865. doi:10.1126/science.1166466
- Stensola et al. (2012) "The entorhinal grid map is discretized", *Nature* 492:72. doi:10.1038/nature11649
- Fiete, Burak & Brookings (2008) "What grid cells convey about rat location", *J Neurosci* 28:6858.
- Fyhn, Hafting, Treves, Moser & Moser (2007) "Hippocampal remapping and grid realignment in entorhinal cortex", *Nature* 446:190.
- Muller & Kubie (1987) "The effects of changes in the environment on the spatial firing of hippocampal complex-spike cells", *J Neurosci* 7:1951.
- Müller & Wehner (1988) "Path integration in desert ants, *Cataglyphis fortis*", *PNAS* 85:5287. doi:10.1073/pnas.85.14.5287
- Tolman (1948) "Cognitive maps in rats and men", *Psychological Review* 55:189.
- Doeller, Barry & Burgess (2010) "Evidence for grid cells in a human memory network", *Nature* 463:657.
- Jacobs et al. (2013) "Direct recordings of grid-like neuronal activity in human spatial navigation", *Nature Neuroscience* 16:1188.
- Constantinescu, O'Reilly & Behrens (2016) "Organizing conceptual knowledge in humans with a gridlike code", *Science* 352:1464.
- Stachenfeld, Botvinick & Gershman (2017) "The hippocampus as a predictive map", *Nature Neuroscience* 20:1643. doi:10.1038/nn.4650
- Banino et al. (2018) "Vector-based navigation using grid-like representations in artificial agents", *Nature* 557:429. doi:10.1038/s41586-018-0102-6
- Whittington et al. (2020) "The Tolman-Eichenbaum Machine: unifying space and relational memory through generalization in the hippocampal formation", *Cell* 183:1249. doi:10.1016/j.cell.2020.10.024
- Nobel Prize in Physiology or Medicine 2014: https://www.nobelprize.org/prizes/medicine/2014/summary/
