---
title: Population dynamics and neural manifolds
category: function
tags: [population-dynamics, neural-manifold, dynamical-systems, attractor, ring-attractor, line-attractor, pca, jpca, gpfa, rnn, representational-drift, head-direction]
use_cases:
  - what is a neural manifold and what does low-dimensional population activity mean
  - how does a ring attractor hold a head direction or a line attractor hold a value
  - what does PCA or jPCA on neural recordings prove and not prove
  - can a task-trained RNN be used as a model of cortex
  - what is representational drift and how can behaviour stay stable through it
  - build a continuous attractor network in numpy
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1146/annurev-neuro-092619-094115
  - https://doi.org/10.1038/nature11129
  - https://doi.org/10.1038/nature12742
  - https://doi.org/10.1038/s41593-018-0310-2
  - https://doi.org/10.1038/nn.4617
  - https://doi.org/10.1038/s41593-019-0460-x
  - https://doi.org/10.1016/j.conb.2019.08.005
---

# Population dynamics and neural manifolds

## Summary
Single-neuron tuning curves ([[neural-coding-and-computation]]) describe what one
cell responds to. The **computation-through-dynamics** view looks instead at the joint
activity of many neurons as a point moving through a state space, and asks what
rules move it (Vyas et al. 2020). In many recordings that point stays near a
**low-dimensional manifold** (Gallego et al. 2017), and its motion looks like a simple dynamical system:
a rotation, a slide along a line, a bump that stays put on a ring. Task-trained
recurrent networks show the same structures, which makes them testable models of
cortex. Two caveats run through this topic: dimensionality reduction can find
structure that simpler facts already explain, and the neurons carrying a stable
manifold can change from week to week.

## How it works

### Attractors: line, ring and torus
An **attractor** is a state the network returns to after a small push. A
*continuous* attractor is a whole line or ring of such states, so the network can
hold any value along it with no input.
- **Line attractor (established model, supported in data).** The brainstem
  oculomotor integrator holds the eyes still at any position between saccades.
  Seung (1996) modelled it as recurrent feedback tuned so that activity neither
  decays nor grows along one direction: a line of fixed points that integrates
  velocity commands into position.
- **Ring attractor (established model, strong evidence in flies and mice).** For an
  angle such as head direction, cells arranged by preferred angle excite near
  neighbours and inhibit distant ones, so activity forms one **bump** that can sit
  anywhere on the ring; an angular-velocity input shifts it (Zhang 1996). In
  *Drosophila* the bump of the ellipsoid-body compass neurons persists in darkness,
  and when an optogenetic stimulus creates activity at another position the bump
  jumps there instead of a second one forming (Kim et al. 2017). In mouse
  anterodorsal thalamus, head-direction population activity lies on a 1-D ring
  manifold, and keeps that ring structure during sleep when there is no heading to
  track (Chaudhuri et al. 2019). Grid-cell module activity lies on a torus, again
  preserved in sleep (Gardner et al. 2022) ([[spatial-navigation]]).
- **Fine-tuning (established theoretical point).** A perfect continuous attractor
  needs precisely balanced weights; small mismatches make the stored value drift
  towards a few discrete points (Seung 1996). How real circuits stay tuned is open.

Discrete attractors (Hopfield networks, [[memory-systems]]) store separate patterns;
continuous ones store a quantity.

### Rotational dynamics in motor cortex (supported, debated)
Churchland et al. (2012) recorded monkey motor and premotor cortex during reaching
and introduced **jPCA**, which finds planes where the population state rotates
(fitting `dx/dt = M x` with `M` skew-symmetric). Different reaches started from
different preparatory states and then rotated in a consistent direction, which they
argued shows motor cortex acting as a pattern generator for muscle commands, not a
map of reach parameters ([[action-selection-and-motor-control]]). Critics argue
rotations can come from simpler features of the data (below).

### Dimensionality reduction: what it does and does not prove
| Method | Does | Watch out |
|---|---|---|
| PCA | Linear axes of largest variance, usually on trial-averaged rates | Averaging hides single-trial variability; variance is not importance |
| jPCA | Finds planes with rotational linear dynamics | Will report the most rotational plane even in data with weak rotation |
| GPFA (Yu et al. 2009) | Smooth latent trajectories on single trials, with per-neuron noise | Assumes linear mapping and Gaussian-process smoothness |

What these analyses **do** show: the activity measured in that task lies mostly in a
subspace, and how the state moves within it. What they **do not** show on their own:
- *That the structure is special.* Elsayed & Cunningham (2017) built null models that
  keep single-neuron tuning and the correlations across time, neurons and conditions,
  then asked whether a reported population structure exceeds them. Without such a
  null, a "manifold" or "rotation" may be a by-product of smooth, tuned neurons.
- *That the brain is low-dimensional.* Measured dimensionality is bounded by the
  complexity of the task and of the stimulus set (Gao & Ganguli 2015). Mouse V1
  responses to many natural images spread variance over a power-law spectrum with
  exponent close to 1, i.e. high-dimensional (Stringer et al. 2019).
- *That the manifold is causal.* Stronger evidence is interventional: in a
  brain-computer interface, monkeys quickly learned decoder changes that stayed
  inside the existing manifold but not ones that required leaving it (Sadtler et al.
  2014), so the manifold constrains learning on short timescales (**supported**).

### Task-trained RNNs as models of cortex (supported, a method not a fact)
Train a recurrent network on the animal's task, then compare its hidden dynamics with
recordings. Mante, Sussillo et al. (2013) had monkeys integrate either motion or colour
of a stimulus depending on context. Prefrontal neurons mixed all variables, and an RNN
trained on the same task reproduced this: both inputs entered the network, and context
changed which one was integrated along a line attractor. Fixed-point analysis, finding
states where `dx/dt ≈ 0` and linearising around them, is the tool for reading such
networks (Sussillo & Barak 2013). Yang et al. (2019) trained one RNN on 20 cognitive
tasks; units formed clusters specialised for groups of tasks, and task representations
composed (a task's representation could be built from others'). Matching an RNN to data
shows the mechanism is *sufficient*, not that cortex uses it; different architectures
can match equally well ([[evaluating-brain-models]]).

### Representational drift (established phenomenon, causes open)
Imaging the same neurons over days shows the code changing while behaviour does not.
In mouse CA1 the set of active place cells changed from day to day, yet position could
still be decoded from each day's population (Ziv et al. 2013). In posterior parietal
cortex, activity patterns for a well-learned navigation task reorganised over weeks
(Driscoll et al. 2017). At the level of latent dynamics, motor cortex trajectories for
the same behaviour stayed stable over long periods once aligned across sessions
(Gallego et al. 2020). **Hypotheses** for why drift happens and is tolerated include
synaptic turnover, ongoing learning that reuses neurons, and drift confined to
directions the downstream readout ignores (Rule, O'Leary & Harvey 2019).

## Relevance to building brain-like AI
- **Analyse your own networks the same way.** PCA of hidden states, fixed points and
  linearisation (Sussillo & Barak 2013) explain what a trained RNN or state-space model
  computes, and give something to compare with recordings beyond accuracy.
- **Ring attractors are a ready-made module** for angles and phases: heading, a
  periodic variable, a clock hand. They integrate velocity with no learning, and need
  landmark correction because noise makes the bump diffuse.
- **Drift is a continual-learning lesson (hypothesis).** If brains keep behaviour stable
  while the units change, readouts that track a stable latent subspace, rather than
  fixed units, may tolerate weight change and pruning better.
- **Test structure against a null** before claiming your model has a manifold or
  rotations; the same trap applies to model analysis as to brain data.

## Code
A ring attractor: 100 rate neurons with cosine connectivity hold a head-direction bump
after the cue is gone, a velocity input turns it, and the bump states for 36 headings
lie close to a 2-D plane (a ring) in 100-D space.

```python
import numpy as np

rng = np.random.default_rng(0)
N = 100
theta = np.linspace(0, 2 * np.pi, N, endpoint=False)
# Ring attractor: neighbours excite, far cells inhibit (cosine weights)
W = (-1.0 + 6.0 * np.cos(theta[:, None] - theta[None, :])) / N
dt, tau = 0.001, 0.02              # seconds

def f(x):                          # firing rate, saturating at 1
    return np.tanh(np.maximum(x, 0))

def decode(r):                     # population vector -> angle in degrees
    return np.degrees(np.angle(r @ np.exp(1j * theta))) % 360

def run(r, steps, cue=None, shift=0.0, noise=0.05):
    for _ in range(steps):
        inp = W @ r + 0.1
        if cue is not None:
            inp += 1.0 * np.cos(theta - np.radians(cue))
        # angular velocity input: an asymmetric push that moves the bump
        inp += shift * np.sin(theta - np.radians(decode(r)))
        r = r + dt / tau * (-r + f(inp)) + noise * np.sqrt(dt) * rng.normal(size=N)
    return r

def err(a, b):
    return abs((a - b + 180) % 360 - 180)

# 1. A brief cue at 90 deg starts a bump; it persists for 2 s with no input.
r = run(rng.uniform(0, 0.1, N), 300, cue=90.0)
r = run(r, 2000)
print(f"bump after 2 s of no input: {decode(r):.1f} deg, peak rate {r.max():.2f}")
assert err(decode(r), 90) < 20 and r.max() > 0.5 and np.sort(r)[N // 4] < 0.1

# 2. A velocity input rotates the bump; when it stops, the new heading is held.
r = run(r, 400, shift=-1.0)
moved = decode(r)
r = run(r, 1000)
print(f"after turning: {moved:.1f} deg, 1 s later: {decode(r):.1f} deg")
assert err(moved, 90) > 30 and err(decode(r), moved) < 20

# 3. The states lie on a ring: bumps at 36 headings span roughly a 2-D plane.
states = [run(run(rng.uniform(0, 0.1, N), 300, cue=float(a)), 300) for a in range(0, 360, 10)]
X = np.array(states) - np.mean(states, axis=0)
var = np.linalg.svd(X, compute_uv=False) ** 2
top2 = var[:2].sum() / var.sum()
print(f"variance in top 2 PCs of 36 bump states: {top2:.2f}")
assert top2 > 0.7
```

The top two PCs do not hold all the variance because the bump is narrower than a
cosine, so higher harmonics of the ring take PCs 3, 4 and so on: a manifold can be
1-D (a ring) while needing more than two linear dimensions to embed.

## Open questions
- Is low-dimensional activity a property of cortex, or of the simple, low-dimensional
  tasks used in the lab (Gao & Ganguli 2015)?
- Are motor-cortex rotations the computation itself, or a by-product of smooth,
  tuned activity that a better null model would explain?
- How do real continuous attractors stay tuned, given that a perfect one needs exact
  weights?
- What keeps behaviour stable under representational drift: a downstream readout that
  re-learns, drift confined to a null space, or something else?

## Related
- [[neural-coding-and-computation]] - single-neuron and population codes; attractors as a computational primitive.
- [[spatial-navigation]] - head-direction and grid cells, whose activity lies on a ring and a torus.
- [[action-selection-and-motor-control]] - motor cortex, where rotational dynamics were found.
- [[evaluating-brain-models]] - how to compare a model's representations and dynamics with recordings.
- [[measuring-the-brain-and-open-datasets]] - the multi-neuron recordings these analyses need.
- [[memory-systems]] - discrete attractors (Hopfield networks) for stored patterns.
- [[attention-and-working-memory]] - persistent activity, held by attractor dynamics.
- [[timing-and-sequence-learning]] - population clocks and sequences as trajectories in state space.
- [[reservoir-computing]] - untrained recurrent dynamics read out linearly.

## References
- Vyas, Golub, Sussillo & Shenoy (2020) "Computation through neural population dynamics", *Annu Rev Neurosci* 43:249. doi:10.1146/annurev-neuro-092619-094115
- Churchland et al. (2012) "Neural population dynamics during reaching", *Nature* 487:51. doi:10.1038/nature11129
- Mante, Sussillo, Shenoy & Newsome (2013) "Context-dependent computation by recurrent dynamics in prefrontal cortex", *Nature* 503:78. doi:10.1038/nature12742
- Yang et al. (2019) "Task representations in neural networks trained to perform many cognitive tasks", *Nat Neurosci* 22:297. doi:10.1038/s41593-018-0310-2
- Sussillo & Barak (2013) "Opening the black box: low-dimensional dynamics in high-dimensional recurrent neural networks", *Neural Comput* 25:626. doi:10.1162/NECO_a_00409
- Seung (1996) "How the brain keeps the eyes still", *PNAS* 93:13339. doi:10.1073/pnas.93.23.13339
- Zhang (1996) "Representation of spatial orientation by the intrinsic dynamics of the head-direction cell ensemble: a theory", *J Neurosci* 16:2112. doi:10.1523/JNEUROSCI.16-06-02112.1996
- Kim, Rouault, Druckmann & Jayaraman (2017) "Ring attractor dynamics in the *Drosophila* central brain", *Science* 356:849. doi:10.1126/science.aal4835
- Chaudhuri et al. (2019) "The intrinsic attractor manifold and population dynamics of a canonical cognitive circuit across waking and sleep", *Nat Neurosci* 22:1512. doi:10.1038/s41593-019-0460-x
- Gardner et al. (2022) "Toroidal topology of population activity in grid cells", *Nature* 602:123. doi:10.1038/s41586-021-04268-7
- Yu et al. (2009) "Gaussian-process factor analysis for low-dimensional single-trial analysis of neural population activity", *J Neurophysiol* 102:614. doi:10.1152/jn.90941.2008
- Elsayed & Cunningham (2017) "Structure in neural population recordings: an expected byproduct of simpler phenomena?", *Nat Neurosci* 20:1310. doi:10.1038/nn.4617
- Gao & Ganguli (2015) "On simplicity and complexity in the brave new world of large-scale neuroscience", *Curr Opin Neurobiol* 32:148. doi:10.1016/j.conb.2015.04.003
- Stringer et al. (2019) "High-dimensional geometry of population responses in visual cortex", *Nature* 571:361. doi:10.1038/s41586-019-1346-5
- Sadtler et al. (2014) "Neural constraints on learning", *Nature* 512:423. doi:10.1038/nature13665
- Gallego, Perich, Miller & Solla (2017) "Neural manifolds for the control of movement", *Neuron* 94:978. doi:10.1016/j.neuron.2017.05.025
- Ziv et al. (2013) "Long-term dynamics of CA1 hippocampal place codes", *Nat Neurosci* 16:264. doi:10.1038/nn.3329
- Driscoll et al. (2017) "Dynamic reorganization of neuronal activity patterns in parietal cortex", *Cell* 170:986. doi:10.1016/j.cell.2017.07.021
- Gallego et al. (2020) "Long-term stability of cortical population dynamics underlying consistent behavior", *Nat Neurosci* 23:260. doi:10.1038/s41593-019-0555-4
- Rule, O'Leary & Harvey (2019) "Causes and consequences of representational drift", *Curr Opin Neurobiol* 58:141. doi:10.1016/j.conb.2019.08.005
