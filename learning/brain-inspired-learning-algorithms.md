---
title: Brain-inspired learning algorithms (with code)
category: learning
tags: [hebbian, oja, predictive-coding, three-factor, actor-critic, ewc, replay, continual-learning, local-learning, curiosity]
use_cases:
  - implement a learning rule that works like the brain
  - train a network with only local updates and no backpropagation
  - make a model learn continually without catastrophic forgetting
status: stable
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1007/BF00275687
  - https://doi.org/10.1162/NECO_a_00949
  - https://doi.org/10.1073/pnas.1611835114
  - https://doi.org/10.1126/science.275.5306.1593
---

# Brain-inspired learning algorithms (with code)

## Summary
Working implementations of the main brain learning principles, from single
synapses up to memory systems. Every numpy block below was run, and its output is
shown. They are teaching-size: small enough to read in a minute, real enough
to extend.

| Principle (brain) | Algorithm | Section |
|---|---|---|
| Hebbian plasticity + normalisation | Oja's rule (learns PCA) | 1 |
| Predictive coding in cortex | Predictive coding network (local updates) | 2 |
| Dopamine RPE + eligibility | Three-factor actor-critic | 3 |
| Spike timing | STDP | [[spiking-neural-networks]] |
| Synaptic consolidation | Elastic Weight Consolidation | 4 |
| Hippocampal replay | Experience / generative replay | 5 |
| Pattern completion | Hopfield network | [[memory-systems]] |
| Curiosity / novelty (dopamine, ACh) | Prediction-error intrinsic reward | 6 |

## 1. Hebbian learning with Oja's rule
Pure Hebb (`Δw = ηxy`) explodes. Oja's decay term keeps `|w| = 1` and makes the
neuron extract the input's first principal component, all with local information.

```python
import numpy as np

rng = np.random.default_rng(0)
C = np.array([[3.0, 1.0], [1.0, 1.0]])
X = rng.multivariate_normal([0, 0], C, size=5000)
w = rng.normal(size=2)
for x in X:
    y = w @ x
    w += 0.005 * y * (x - y * w)            # Hebbian term y*x minus decay y^2*w
pc1 = np.linalg.eigh(C)[1][:, -1]
print(f"|cos(w, PC1)| = {abs(w @ pc1) / np.linalg.norm(w):.3f}, |w| = {np.linalg.norm(w):.2f}")
# |cos(w, PC1)| = 1.000, |w| = 1.00
```

## 2. Predictive coding network (learns XOR with local updates)
Hidden units first **relax** to reduce prediction errors (inference). Then each
weight changes by *its own layer's error × its own presynaptic activity*. There is
no backward pass of gradients through the network, yet it solves XOR, a
nonlinear problem. Under small-error conditions this approximates backprop
(Whittington & Bogacz 2017). See [[predictive-processing]].

```python
import numpy as np

rng = np.random.default_rng(1)
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], float)
Y = np.array([[0], [1], [1], [0]], float)
sizes = [2, 8, 1]
W = [rng.normal(0, 1, (sizes[i + 1], sizes[i])) for i in range(2)]
b = [np.zeros(sizes[i + 1]) for i in range(2)]
f, df = np.tanh, lambda a: 1 - np.tanh(a) ** 2

def forward(x):
    h = W[0] @ x + b[0]
    return h, W[1] @ f(h) + b[1]

for epoch in range(3000):
    for x, y in zip(X, Y):
        h, _ = forward(x)                   # start hidden units at the feedforward guess
        for _ in range(20):                 # inference: relax hidden units to cut prediction error
            e1 = h - (W[0] @ x + b[0])      # error at hidden layer
            e2 = y - (W[1] @ f(h) + b[1])   # error at output (clamped to target)
            h += 0.1 * (-e1 + df(h) * (W[1].T @ e2))
        e1 = h - (W[0] @ x + b[0])
        e2 = y - (W[1] @ f(h) + b[1])
        W[0] += 0.05 * np.outer(e1, x);    b[0] += 0.05 * e1   # local: error x presynaptic activity
        W[1] += 0.05 * np.outer(e2, f(h)); b[1] += 0.05 * e2

print(np.round([forward(x)[1][0] for x in X], 2))   # [0. 1. 1. 0.]
```

Remove the output clamp and the same network becomes a generative model that
learns to predict its input: the unsupervised mode the cortex is thought to use.

**Measured in this repo** ([`research/credit_assignment.py`](../research/credit_assignment.py),
issue #92, 10 seeds, 64-32-32-10 tanh net on 8x8 digits). How close is the PC update
to backprop's gradient (cosine, 1 = same direction)? With every layer at equal
variance it is close but not equal: median 0.95-0.96 per layer at equilibrium, and
shrinking the output error does not help, because that scales every layer's error
alike. What matters is the precision: give the output layer a larger variance than the
hidden layers (Σ(0) in Whittington & Bogacz 2017) and the cosine reaches 0.991 at 10x
and 1.000 at 100x. A computational replication, not evidence that cortex does this.
Feedback alignment and its direct variant were measured in the same script: see
*Choosing / trade-offs*.

## 3. Three-factor learning: dopamine as reward prediction error
A Hebbian eligibility term (which action fired versus what was expected) is
gated by a global prediction error `δ = r − V(s)`, the signal dopamine neurons
carry (Schultz, Dayan & Montague 1997). This is actor-critic RL written as a
synaptic rule.

```python
import numpy as np

rng = np.random.default_rng(2)
S, A = 4, 2
correct = np.array([0, 1, 1, 0])            # rewarded action per state
W_pi, V = np.zeros((A, S)), np.zeros(S)
for trial in range(2000):
    s = rng.integers(S)
    p = np.exp(W_pi[:, s]); p /= p.sum()
    a = rng.choice(A, p=p)
    r = float(a == correct[s])
    delta = r - V[s]                        # reward prediction error ("dopamine")
    V[s] += 0.1 * delta                     # critic (striatum / value)
    elig = np.eye(A)[a] - p                 # Hebbian eligibility: chosen action vs expected
    W_pi[:, s] += 0.5 * delta * elig        # third factor gates the Hebbian change
print(f"accuracy {(W_pi.argmax(0) == correct).mean():.0%}")   # accuracy 100%
```

For delayed rewards, let `elig` decay over time (`elig = λ·elig + new`) instead of
using it immediately, the way eligibility traces at real synapses last about a second.

## 4. Synaptic consolidation: Elastic Weight Consolidation (EWC)
Brain: synapses that matter for old memories become less plastic.
Algorithm (Kirkpatrick et al. 2017): after task A, estimate each weight's
importance with the diagonal Fisher information `F_i`, then train task B with

`L(θ) = L_B(θ) + (λ/2) · Σ_i F_i · (θ_i − θ*_A,i)²`

Important weights are anchored near their task-A values; unimportant ones stay
free to learn. Relatives: Synaptic Intelligence (online importance), MAS.

## 5. Hippocampal replay
Brain: the hippocampus replays recent experience during sleep and interleaves it
with old knowledge ([[memory-systems]]).
Algorithms:
- **Experience replay**: store past samples in a buffer and mix them into each
  new batch. Simple and very effective; the standard baseline for continual learning.
- **Prioritised replay**: replay surprising or rewarding samples more often
  (the hippocampus is biased the same way).
- **Generative replay** (Shin et al. 2017): a generative model produces pseudo-old
  data instead of storing raw samples, closer to how the brain "re-imagines" memories.
- **Sleep phases**: alternate an online "wake" phase (learn new data fast, store
  episodes) with an offline "sleep" phase (replay + consolidate into slow weights).

## 6. Curiosity and intrinsic motivation
Brain: novelty and surprise drive dopamine and acetylcholine; infants explore to
learn. Algorithm: intrinsic reward = the prediction error of a learned forward
model (ICM, Pathak et al. 2017), or the disagreement of an ensemble, or
information gain (active inference, [[predictive-processing]]). The agent seeks
experiences it can *learn from*, not just ones that are rewarded.

## Choosing / trade-offs
- **Accuracy today**: backprop leads on hard benchmarks. Feedback alignment and
  target propagation fell well behind it on ImageNet (Bartunov et al. 2018), and
  pure Hebbian/STDP rules trail further. The order among the other local rules is
  not settled. At small scale they work: on 8x8 digits (64-64-64-10, 10 seeds, this
  repo's `research/credit_assignment.py`) test error was backprop 3.7%, direct
  feedback alignment 4.2%, feedback alignment 4.5%, and 12.9% when only the readout
  learns. Both random-feedback rules beat the frozen-hidden baseline in every seed.
- **Hardware fit**: local rules (1, 2, 3, STDP) suit neuromorphic chips and
  on-device learning. Backprop needs stored activations and a global backward pass.
- **Continual learning**: replay is the strongest simple method. EWC helps when you
  cannot store data. Combining both (with a CLS-style fast memory) works best.

## Related
- [[learning-and-plasticity]] - the biology behind each rule.
- [[brain-vs-deep-learning]] - where these rules stand against backprop.
- [[spiking-neural-networks]] - STDP in spiking neurons.
- [[build-a-brain-like-learner]] - how to combine them into one system.
- [[sleep-and-memory-consolidation]] - the biology behind replay and offline "sleep" phases.
- [[dendritic-computation]] - dendritic error signals as a route to local credit assignment.
- [Brain Lab](../game/README.md) - level 9, *Find the pattern*: Hebb against Oja's rule on 2-D inputs.

## References
- Bartunov, Santoro, Richards, Marris, Hinton & Lillicrap (2018) "Assessing the scalability of biologically-motivated deep learning algorithms and architectures", *NeurIPS 2018*. arXiv:1807.04587
- Oja (1982) "Simplified neuron model as a principal component analyzer", *J Math Biol* 15:267. doi:10.1007/BF00275687
- Whittington & Bogacz (2017), *Neural Computation* 29:1229. doi:10.1162/NECO_a_00949
- Schultz, Dayan & Montague (1997), *Science* 275:1593. doi:10.1126/science.275.5306.1593
- Kirkpatrick et al. (2017) "Overcoming catastrophic forgetting in neural networks", *PNAS* 114:3521. doi:10.1073/pnas.1611835114
- Shin, Lee, Kim & Kim (2017) "Continual Learning with Deep Generative Replay", NeurIPS.
- Pathak, Agrawal, Efros & Darrell (2017) "Curiosity-driven Exploration by Self-supervised Prediction", ICML.
- Millidge, Seth & Buckley (2021) "Predictive Coding: a Theoretical and Experimental Review", arXiv:2107.12979.
