---
title: Spiking neural networks and simulators
category: simulation
tags: [snn, lif, izhikevich, stdp, surrogate-gradient, brian2, nest, neuron, snntorch, norse, lava]
use_cases:
  - simulate a spiking neuron or network in Python
  - train a spiking neural network with gradients or STDP
  - choose a brain simulator (Brian2, NEST, NEURON, snnTorch)
status: stable
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1109/MSP.2019.2931595
  - https://doi.org/10.1109/JPROC.2023.3308088
  - https://doi.org/10.7554/eLife.47314
  - https://doi.org/10.1109/TNN.2003.820440
---

# Spiking neural networks and simulators

## Summary
A spiking neural network (SNN) uses neurons that integrate input over time and
emit discrete spikes, like real neurons. SNNs are the main tool both for brain
simulation and for energy-efficient neuromorphic AI. They can learn with
**biological rules** (STDP, three-factor) or with **surrogate-gradient backprop
through time**, which currently gives much better accuracy. The code below is
plain numpy and was run to produce the printed output.

## How it works

### 1. A single LIF neuron

```python
import numpy as np

dt, T = 0.1, 200.0                         # ms
tau_m, v_rest, v_th, v_reset, R = 10.0, -70.0, -55.0, -75.0, 10.0
v, spikes = v_rest, []
for step in range(int(T / dt)):
    t = step * dt
    I = 2.0 if 50 <= t < 150 else 0.0        # nA step current
    v += dt / tau_m * (-(v - v_rest) + R * I)  # Euler step of tau dV/dt = -(V-Vrest) + RI
    if v >= v_th:
        spikes.append(t)
        v = v_reset
print(f"LIF: {len(spikes)} spikes, first at {spikes[0]:.1f} ms")
# LIF: 6 spikes, first at 63.7 ms
```

### 2. Izhikevich neuron (rich firing patterns, still cheap)

```python
def izhikevich(a, b, c, d, I=10.0, T=300.0, dt=0.25):
    v, u, n = -65.0, b * -65.0, 0
    for _ in range(int(T / dt)):
        v += dt * (0.04 * v * v + 5 * v + 140 - u + I)
        u += dt * a * (b * v - u)
        if v >= 30:
            v, u, n = c, u + d, n + 1
    return n

print("regular spiking:", izhikevich(0.02, 0.2, -65, 8))   # 7  (cortical pyramidal)
print("fast spiking:   ", izhikevich(0.1, 0.2, -65, 2))    # 34 (PV interneuron)
```

### 3. Unsupervised learning with STDP
One neuron, 100 inputs. Inputs 0-19 often fire together; the rest fire randomly.
With trace-based STDP and no labels, the neuron strengthens the correlated group:
it discovers the hidden structure on its own.

```python
import numpy as np

rng = np.random.default_rng(0)
N, steps, dt = 100, 20000, 1.0              # 100 inputs, 20 s at 1 ms
group = np.arange(20)                       # inputs 0-19 are correlated
w = np.full(N, 0.5)
tau_m, v_th = 20.0, 1.0
tau_pre, tau_post = 20.0, 20.0
A_plus, A_minus = 0.01, 0.0105              # slight depression bias keeps weights bounded
x_pre, x_post, v = np.zeros(N), 0.0, 0.0

for t in range(steps):
    pre = rng.random(N) < 0.01              # 10 Hz background
    if rng.random() < 0.02:                 # shared events drive the group together
        pre[group] = rng.random(group.size) < 0.9
    x_pre = x_pre * np.exp(-dt / tau_pre) + pre   # presynaptic trace
    x_post *= np.exp(-dt / tau_post)              # postsynaptic trace
    v += dt / tau_m * -v + 0.1 * w @ pre
    w -= A_minus * x_post * pre             # pre after post -> depress
    if v >= v_th:
        v = 0.0
        x_post += 1
        w += A_plus * x_pre                 # pre before post -> potentiate
    np.clip(w, 0, 1, out=w)

print(f"correlated {w[group].mean():.2f}, others {w[20:].mean():.2f}")
# correlated 1.00, others 0.62
```

Add lateral inhibition between several such neurons (winner-take-all) and each
one specialises on a different pattern. Diehl & Cook (2015) reached ~95% on MNIST
this way, with no labels during learning.

To make it **reinforcement** learning, do not apply `x_pre`/`x_post` changes
directly. Accumulate them in an eligibility trace and multiply by a reward signal
(dopamine): the three-factor rule from [[learning-and-plasticity]].

### 4. Training SNNs with surrogate gradients
A spike is a step function, whose derivative is zero almost everywhere, so
backprop fails. **Surrogate gradients** keep the hard spike on the forward pass
but use a smooth function's derivative (e.g. a fast sigmoid) on the backward
pass, then run backprop through time (Neftci, Mostafa & Zenke 2019). This is
how competitive SNN accuracy is reached today. It is effective but not
biologically plausible (see [[brain-vs-deep-learning]]).

```python
# pip install snntorch torch   (sketch, not run here)
import snntorch as snn
from snntorch import surrogate
lif = snn.Leaky(beta=0.9, spike_grad=surrogate.fast_sigmoid())  # drop-in PyTorch layer
```

## Choosing a simulator

| Tool | Level | Best for | Notes |
|---|---|---|---|
| **Brian2** | Point / few-compartment neurons | Research prototyping; you write the equations as strings | Python, generates C++ code; very readable |
| **NEST** | Point neurons | Very large networks (millions of neurons) on clusters | Used by EBRAINS; PyNEST interface |
| **NEURON** | Detailed multi-compartment | Biophysically detailed single cells and circuits | Used by Blue Brain; ModelDB has nearly 2,000 models |
| **snnTorch / Norse / SpikingJelly** | LIF layers in PyTorch | Training SNNs with surrogate gradients on GPU | Best for ML tasks |
| **Lava** (Intel) | LIF, neuromorphic | Deploying to Loihi chips | See [[neuromorphic-hardware]] |
| **The Virtual Brain** | Neural mass per region | Whole-brain dynamics from MRI connectivity | Clinical and systems research |
| **numpy** (as above) | Anything small | Learning how it works | Write it yourself first |

## Gotchas
- **Time step.** Euler with `dt` too large misses spikes or goes unstable. 0.1 ms
  for HH or Izhikevich, ≤1 ms for LIF.
- **Weight explosion.** Unbalanced STDP saturates all weights at the max. Keep
  slight depression dominance, normalisation, or homeostasis.
- **Encoding inputs.** Static data (images) must be turned into spikes: rate
  (Poisson) coding, latency coding, or direct current. The choice changes accuracy
  and energy a lot.
- **Energy claims** only hold on neuromorphic hardware. On a GPU, an SNN is
  usually *slower* than the equivalent ANN.

## Relevance to building brain-like AI
- SNNs are the only models here that carry spike timing, so they are where STDP,
  three-factor rules and temporal codes can be tested ([[learning-and-plasticity]]).
- Sparse, event-driven spiking is what neuromorphic chips need for their energy savings
  ([[neuromorphic-hardware]]); a dense ANN does not map onto them well.
- Today the best SNN accuracy comes from surrogate-gradient backprop through time,
  which is not biologically plausible. A brain-like learner needs a local rule that
  comes close (stage 2 of [[build-a-brain-like-learner]]).

## Open questions
- Whether spike timing adds computational power that rate-based networks lack on
  real tasks, or mainly saves energy.
- Whether local rules (STDP, three-factor, e-prop) can train deep SNNs to the accuracy
  of surrogate gradients.
- Which level of neuron detail (LIF, adaptive LIF, Izhikevich, multi-compartment) a
  task needs; see [[levels-of-brain-modeling]].

## Related
- [[levels-of-brain-modeling]] - where LIF and Izhikevich sit on the ladder.
- [[learning-and-plasticity]] - the biology behind STDP and three-factor rules.
- [[neuromorphic-hardware]] - running SNNs efficiently.
- [[build-a-brain-like-learner]] - SNNs in stage 2 of the roadmap.
- [Brain Lab](../game/README.md) - level 1, *Spark*: drive a leaky integrate-and-fire neuron to exactly five spikes.

## References
- Izhikevich (2003), *IEEE Trans Neural Networks* 14:1569. doi:10.1109/TNN.2003.820440
- Neftci, Mostafa & Zenke (2019) "Surrogate Gradient Learning in Spiking Neural Networks", *IEEE Signal Processing Magazine* 36:51. doi:10.1109/MSP.2019.2931595
- Eshraghian et al. (2023) "Training Spiking Neural Networks Using Lessons From Deep Learning", *Proc IEEE* 111:1016. doi:10.1109/JPROC.2023.3308088
- Stimberg, Brette & Goodman (2019) "Brian 2, an intuitive and efficient neural simulator", *eLife* 8:e47314. doi:10.7554/eLife.47314
- Diehl & Cook (2015) "Unsupervised learning of digit recognition using spike-timing-dependent plasticity", *Front Comput Neurosci* 9:99.
- Bellec et al. (2020) "A solution to the learning dilemma for recurrent networks of spiking neurons", *Nat Commun* 11:3625. doi:10.1038/s41467-020-17236-y (e-prop)
- Gerstner et al. (2014) *Neuronal Dynamics*: https://neuronaldynamics.epfl.ch/
