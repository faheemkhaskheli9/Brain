---
title: Reservoir computing (echo-state networks, liquid-state machines)
category: simulation
tags: [reservoir-computing, echo-state-network, esn, liquid-state-machine, lsm, spectral-radius, edge-of-chaos, fading-memory, physical-reservoir, photonic, memristor, time-series]
use_cases:
  - what is reservoir computing and why is only the readout trained
  - build an echo-state network to predict a time series
  - how do I choose the spectral radius of a reservoir
  - is a cortical circuit a reservoir
  - can a physical system such as a photonic or memristor device compute as a reservoir
status: draft
last_verified: 2026-10-11
sources:
  - https://www.ai.rug.nl/minds/uploads/EchoStatesTechRep.pdf
  - https://doi.org/10.1126/science.1091277
  - https://doi.org/10.1162/089976602760407955
  - https://doi.org/10.1016/j.cosrev.2009.03.005
  - https://doi.org/10.1016/j.neunet.2012.07.005
  - https://doi.org/10.1016/j.neunet.2019.03.005
  - https://doi.org/10.1038/nrn2558
---

# Reservoir computing (echo-state networks, liquid-state machines)

## Summary
Reservoir computing drives a **fixed, random recurrent network** (the reservoir)
with an input stream and trains only a **linear readout** from its state. The
recurrent dynamics turn recent input history into a high-dimensional state; the
readout picks out what a task needs with one linear regression, so there is no
backpropagation through time. It was found twice around 2001-2002: **echo-state
networks** (Jaeger) with rate units and **liquid-state machines** (Maass et al.)
with spiking neurons. It is a cheap, strong baseline for time series, a
candidate account of how cortex handles temporal input, and the main way to compute
with physical substrates that cannot be trained.

## How it works

### The echo-state network
State update for a leaky rate reservoir of `N` units (Lukoševičius 2012):

`x(t+1) = (1−a)·x(t) + a·tanh(W·x(t) + W_in·u(t+1))`, readout `y(t) = W_out·x(t)`

- `W` (N×N) and `W_in` are random and **never trained**. `a` is the leak rate,
  which sets the reservoir's time scale.
- Run the input through, drop an initial **washout** period, collect the states
  as rows of `S`, and solve ridge regression `W_out = (SᵀS + λI)⁻¹ Sᵀ y`.
- **Established:** this works well on chaotic time-series prediction. Jaeger &
  Haas (2004) reported a 2400-fold accuracy gain over earlier methods on a chaotic
  benchmark (Mackey-Glass) and better channel equalisation in wireless links.

### The echo-state property and the spectral radius
The **echo-state property** means the state is eventually a function of the input
history alone: two runs from different initial states converge. Without it, the
readout learns from noise in the initial condition.
- **Established:** Jaeger (2001) gives a sufficient condition, largest singular
  value of `W` below 1. Scaling `W` to a **spectral radius** (largest absolute
  eigenvalue) just under 1 is the standard heuristic.
- **Established, and often misquoted:** the spectral radius below 1 is neither
  sufficient in general nor necessary once input is present; Yildiz, Jaeger &
  Kiebel (2012) give the corrected conditions. In practice the spectral radius is a
  hyperparameter tuned on validation data: larger values give longer memory and
  slower dynamics (Lukoševičius 2012).

### Edge of chaos - supported, but debated
Bertschinger & Natschläger (2004) found that random networks compute best on
time-dependent tasks near the boundary between ordered dynamics (perturbations die
out) and chaotic dynamics (they grow). The idea is **supported** in such models, but
the best operating point depends on the task, and "edge of chaos" is not a general
law of either reservoirs or brains.

### Liquid-state machines (spiking reservoirs)
Maass, Natschläger & Markram (2002) used a recurrent circuit of integrate-and-fire
neurons as the "liquid". Its transient response to a perturbation acts as an
**analog fading memory** of recent inputs, and readout neurons extract, in real time,
information about current and past inputs. They prove universal computational power
for time-varying inputs **under idealised conditions** (enough separation in the
liquid, a rich enough readout); real circuits meet these only approximately.
Stable attractor states are not needed for a stable output.

### Physical reservoirs
Any physical system with nonlinear, fading-memory dynamics that can be driven and
read can serve as a reservoir, since nothing inside it has to be trained (review:
Tanaka et al. 2019).
- **Delay-based / photonic:** Appeltant et al. (2011) replaced the network with a
  **single nonlinear node plus a delayed feedback loop**, time-multiplexing virtual
  nodes along the delay. The design was built in electronics and then adopted for
  photonic reservoirs.
- **Memristive:** Du et al. (2017) used dynamic memristors, whose short-term
  memory comes from their ionic dynamics, as a reservoir. A system of only 88
  memristors recognised handwritten digits fed in as pulse streams and solved a
  second-order nonlinear dynamic task.
- **Weak spot:** device noise and drift change the reservoir, so the readout needs
  retraining or must be robust to it.

### Why it is brain-plausible, and where it falls short
- **Supported:** cortical circuits are recurrent and partly random, respond to input
  with rich transient dynamics, and neurons show mixed selectivity, as reservoir
  units do. Buonomano & Maass (2009) argue that cortex computes timing and sequences
  through this kind of state-dependent dynamics; Enel et al. (2016) trained a reservoir on a
  monkey task and found the dynamic mixed selectivity they compared with recordings
  from dorsal anterior cingulate cortex. Treating cortex *as* a
  reservoir is a **hypothesis**.
- **Plausible learning:** only the readout learns, and a linear readout can be
  trained by a local delta rule or online least squares, with no error sent back
  through time. FORCE learning (Sussillo & Abbott 2009) trains such a readout online
  with feedback into the reservoir to produce stable complex outputs.
- **Shortfalls:** brain synapses inside recurrent circuits *are* plastic, so a
  frozen reservoir is a simplification. Random weights use capacity less well than
  trained recurrent networks (LSTMs, transformers), which usually win on large
  datasets. Memory is limited by the reservoir size and the spectral radius.

## Relevance to building brain-like AI
- **A strong baseline for temporal data** that trains in seconds with one linear
  solve. Try it before training a recurrent network by backprop through time.
- **Fits neuromorphic and analog hardware**: the expensive recurrent part can be a
  spiking chip or a physical device that is never trained; only a small linear
  readout learns ([[neuromorphic-hardware]]).
- **Same pattern as the cerebellum**: a fixed random expansion plus a supervised
  linear readout ([[action-selection-and-motor-control]]).
- **Next-generation reservoir computing** (Gauthier et al. 2021) shows that an
  ESN-like readout over time-delayed inputs and their polynomial products can
  match a reservoir with no random network at all, which helps explain what the
  reservoir contributes.

## Code
An echo-state network predicting the chaotic Mackey-Glass series (`τ = 17`, Mackey
& Glass 1977) 20 time units ahead. The same pipeline with the recurrent weights
removed shows that the reservoir's fading memory is what does the work.

```python
import numpy as np

rng = np.random.default_rng(0)

# Mackey-Glass series, tau = 17 (chaotic), Euler steps of 0.1, sampled every 1 time unit
def mackey_glass(n, tau=17, dt=0.1, beta=0.2, gamma=0.1, p=10):
    lag, steps = int(tau / dt), int(n / dt)
    x = np.full(steps + lag, 1.2)
    for t in range(lag, steps + lag - 1):
        x[t + 1] = x[t] + dt * (beta * x[t - lag] / (1 + x[t - lag] ** p) - gamma * x[t])
    return x[lag::int(1 / dt)][:n]

series = mackey_glass(3000)
u = (series - series.mean()) / series.std()
horizon = 20                                    # predict 20 time units ahead
u_in, y = u[:-horizon], u[horizon:]
washout, split = 200, 2000
nrmse = lambda p, t: np.sqrt(np.mean((p - t) ** 2)) / t.std()

# Fixed random reservoir: W and W_in are never trained
N = 300
W = rng.normal(0, 1, (N, N)) * (rng.random((N, N)) < 0.1)   # 10% sparse
W *= 0.9 / np.max(np.abs(np.linalg.eigvals(W)))             # spectral radius 0.9
W_in = rng.uniform(-0.5, 0.5, (N, 2))                       # input + bias

def test_error(W, leak):
    x, states = np.zeros(N), []
    for v in u_in:
        x = (1 - leak) * x + leak * np.tanh(W @ x + W_in @ np.array([v, 1.0]))
        states.append(x)
    S = np.array(states)
    S_tr, y_tr = S[washout:split], y[washout:split]           # drop the washout transient
    W_out = np.linalg.solve(S_tr.T @ S_tr + 1e-6 * np.eye(N), S_tr.T @ y_tr)  # ridge readout
    return nrmse(S[split:] @ W_out, y[split:])

esn = test_error(W, leak=0.3)
no_memory = test_error(np.zeros((N, N)), leak=1.0)  # same features, but of the present input only
persist = nrmse(u_in[split:], y[split:])            # "the future equals now"
print(f"test NRMSE {horizon} steps ahead: ESN {esn:.3f}, "
      f"memoryless {no_memory:.3f}, persistence {persist:.3f}")
assert esn < 0.05                     # low error on held-out data
assert esn < 0.1 * no_memory          # the recurrent fading memory is what does the work
assert esn < 0.1 * persist
```

It prints a test NRMSE of 0.003 for the ESN, 0.496 for the memoryless version
and 1.857 for persistence. The task is deterministic and noise-free, which is why
the ESN error is so low; add observation noise to see it degrade.

## Open questions
- How much of cortical computation is reservoir-like (fixed dynamics, learned
  readout) and how much depends on plasticity inside the recurrent circuit.
- How to choose or adapt a reservoir for a task without falling back on gradient
  training of the recurrent weights (intrinsic plasticity, evolved reservoirs).
- Whether physical reservoirs can be made stable and dense enough to beat digital
  hardware on energy for real workloads, not only benchmarks.

## Related
- [[spiking-neural-networks]] - the integrate-and-fire neurons a liquid-state machine is made of.
- [[brain-inspired-learning-algorithms]] - other ways to avoid backprop through time.
- [[neuromorphic-hardware]] - spiking chips and memristor crossbars that can host a reservoir.
- [[action-selection-and-motor-control]] - the cerebellum as random expansion plus readout.
- [[neural-coding-and-computation]] - population codes and high-dimensional representations.
- [[levels-of-brain-modeling]] - rate versus spiking units, the ESN/LSM split.
- [[cognitive-architectures]] - NEF, the opposite approach: recurrent weights designed rather than random.

## References
- Jaeger (2001) "The 'echo state' approach to analysing and training recurrent neural networks", GMD Report 148, German National Research Center for Information Technology. https://www.ai.rug.nl/minds/uploads/EchoStatesTechRep.pdf
- Jaeger & Haas (2004) "Harnessing nonlinearity: predicting chaotic systems and saving energy in wireless communication", *Science* 304:78. doi:10.1126/science.1091277
- Maass, Natschläger & Markram (2002) "Real-time computing without stable states: a new framework for neural computation based on perturbations", *Neural Computation* 14:2531. doi:10.1162/089976602760407955
- Lukoševičius & Jaeger (2009) "Reservoir computing approaches to recurrent neural network training", *Computer Science Review* 3:127. doi:10.1016/j.cosrev.2009.03.005
- Lukoševičius (2012) "A practical guide to applying echo state networks", in *Neural Networks: Tricks of the Trade*, LNCS 7700:659. doi:10.1007/978-3-642-35289-8_36
- Yildiz, Jaeger & Kiebel (2012) "Re-visiting the echo state property", *Neural Networks* 35:1. doi:10.1016/j.neunet.2012.07.005
- Bertschinger & Natschläger (2004) "Real-time computation at the edge of chaos in recurrent neural networks", *Neural Computation* 16:1413. doi:10.1162/089976604323057443
- Tanaka et al. (2019) "Recent advances in physical reservoir computing: a review", *Neural Networks* 115:100. doi:10.1016/j.neunet.2019.03.005
- Appeltant et al. (2011) "Information processing using a single dynamical node as complex system", *Nat Commun* 2:468. doi:10.1038/ncomms1476
- Du et al. (2017) "Reservoir computing using dynamic memristors for temporal information processing", *Nat Commun* 8:2204. doi:10.1038/s41467-017-02337-y
- Buonomano & Maass (2009) "State-dependent computations: spatiotemporal processing in cortical networks", *Nat Rev Neurosci* 10:113. doi:10.1038/nrn2558
- Enel, Procyk, Quilodran & Dominey (2016) "Reservoir computing properties of neural dynamics in prefrontal cortex", *PLoS Comput Biol* 12:e1004967. doi:10.1371/journal.pcbi.1004967
- Sussillo & Abbott (2009) "Generating coherent patterns of activity from chaotic neural networks", *Neuron* 63:544. doi:10.1016/j.neuron.2009.07.018
- Gauthier, Bollt, Griffith & Barbosa (2021) "Next generation reservoir computing", *Nat Commun* 12:5564. doi:10.1038/s41467-021-25801-2
- Mackey & Glass (1977) "Oscillation and chaos in physiological control systems", *Science* 197:287. doi:10.1126/science.267326
