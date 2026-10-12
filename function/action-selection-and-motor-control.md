---
title: Action selection and motor control (basal ganglia, cerebellum, motor cortex)
category: function
tags: [basal-ganglia, striatum, direct-pathway, indirect-pathway, go-nogo, habits, cerebellum, forward-model, marr-albus-ito, motor-cortex, population-vector, model-based-rl, model-free-rl]
use_cases:
  - how does the brain choose which action to take
  - what do the basal ganglia and cerebellum compute
  - build an actor with separate Go and NoGo learning
  - map model-based vs model-free reinforcement learning onto brain systems
  - learn a forward model for motor control like the cerebellum
status: stable
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1016/0166-2236(89)90074-X
  - https://doi.org/10.1016/S0306-4522(98)00319-4
  - https://doi.org/10.1162/0898929052880093
  - https://doi.org/10.1038/nn1560
  - https://doi.org/10.1113/jphysiol.1969.sp008820
  - https://doi.org/10.1016/S1364-6613(98)01221-2
  - https://doi.org/10.1126/science.3749885
---

# Action selection and motor control (basal ganglia, cerebellum, motor cortex)

## Summary
Three systems share the job of acting. The **basal ganglia** pick *which* action to
release, learning from dopamine which actions pay off. The **cerebellum** learns
*how* to make a movement accurate and well-timed, using error signals to fit
predictive (forward) models of the body. **Motor cortex** turns the chosen plan into
population activity that drives the spinal cord. These map closely onto two AI
ideas: model-free vs model-based reinforcement learning, and forward models in
robot control.

## How it works

### Basal ganglia: selection by disinhibition (established)
The striatum (caudate, putamen, nucleus accumbens) receives input from almost all of
cortex. Its output nuclei (internal globus pallidus GPi and substantia nigra pars
reticulata SNr) are tonically active and **inhibit** the thalamus and brainstem
motor centres. An action is released when the striatum inhibits the part of the
output that holds it back: selection by disinhibition (Mink 1996; Redgrave, Prescott
& Gurney 1999).

Two pathways leave the striatum (Albin, Young & Penney 1989):

| Pathway | Striatal cells | Route | Net effect on thalamus | Dopamine receptor |
|---|---|---|---|---|
| Direct ("Go") | D1-expressing medium spiny neurons | striatum → GPi/SNr | disinhibits → facilitates the action | D1: dopamine excites and strengthens |
| Indirect ("NoGo") | D2-expressing medium spiny neurons | striatum → GPe → STN → GPi/SNr | more inhibition → suppresses the action | D2: dopamine inhibits |

Optogenetically driving direct-pathway neurons in mice increased movement, and
driving indirect-pathway neurons froze it (Kravitz et al. 2010). Losing dopamine, as
in Parkinson's disease, tips the balance toward NoGo, which is why the disease
causes slowness and difficulty starting movements.

**Go/NoGo learning (model, well supported).** Frank (2005) modelled the two pathways
as separate learners: dopamine bursts after a better-than-expected outcome
strengthen the Go weights of the chosen action, and dopamine dips after a worse
outcome strengthen its NoGo weights. Parkinson's patients off medication learned
better from negative outcomes, and on medication better from positive ones, as the
model predicts (Frank, Seeberger & O'Reilly 2004).

**Habits vs goal-directed control (established behaviour, hypothesised mapping).**
Early in training, animals stop pressing a lever when its reward is devalued
(goal-directed); after overtraining they keep pressing (habit). Lesion work ties
goal-directed control to dorsomedial striatum and prefrontal cortex and habits to
dorsolateral striatum (Yin & Knowlton 2006). Daw, Niv & Dayan (2005) proposed the
two are **model-based** and **model-free** RL controllers, and that the brain
trusts whichever is less uncertain at the moment. That arbitration is a
**hypothesis**.

### Cerebellum: a supervised learner and forward model
The cerebellum holds most of the brain's neurons: about 69 of 86 billion in
the human brain (Azevedo et al. 2009). Its circuit is very regular:

- **Mossy fibres** bring context (sensory, motor-command copies) to granule cells,
  which expand it into a huge, sparse code carried by **parallel fibres**.
- Each **Purkinje cell** sums a very large number of parallel-fibre inputs, but gets
  a single **climbing fibre** from the inferior olive.
- Purkinje cells inhibit the deep cerebellar nuclei, the cerebellum's output.

**Marr-Albus-Ito theory (established framework).** Marr (1969) and Albus (1971)
proposed that the climbing fibre is a **teaching signal**: when it fires together
with a parallel fibre, that synapse changes (Albus: weakens). Ito and colleagues
found this plasticity, long-term depression at parallel-fibre-Purkinje synapses
(Ito 2008 reviews it). In machine-learning terms: a fixed, high-dimensional
expansion (granule cells) followed by a linear readout trained with an error signal,
the delta rule.

**Forward models (hypothesis with strong support).** Wolpert, Miall & Kawato (1998)
proposed the cerebellum learns **internal models**: a forward model predicts the
sensory result of a motor command, and an inverse model gives the command for a
desired result. A forward model lets a movement be corrected before slow sensory
feedback arrives, and lets you cancel the sensation of your own actions (why you
cannot tickle yourself).

**Timing.** Patients with cerebellar damage are worse at producing and judging
precise intervals (Ivry & Keele 1989), and eyeblink conditioning, which needs
the conditioned blink to land at the right moment, depends on the cerebellum.

### Motor cortex: population vectors and dynamics
Single neurons in primary motor cortex are broadly tuned to reach direction, roughly
as a cosine of the angle between the reach and the cell's preferred direction.
Summing each neuron's preferred direction weighted by its firing rate, the
**population vector**, points close to the actual reach (Georgopoulos, Schwartz &
Kettner 1986). Later work argued motor cortex is better described as a dynamical
system that generates the movement than as a map of parameters: during reaching its
population activity rotates in a low-dimensional state space (Churchland et al.
2012). Both views are used in brain-computer interfaces.

## Relevance to building brain-like AI
- **Separate Go and NoGo learners.** Splitting an actor into "evidence for" and
  "evidence against" weights, trained by positive and negative prediction errors,
  lets an agent learn asymmetrically from gains and losses. It is a small change to
  an actor-critic.
- **Arbitrate between model-based and model-free control** by their uncertainty,
  as Daw et al. propose: plan (expensive) when the cached values are unreliable,
  act from habit (cheap) when they are well learned.
- **Cerebellum = random expansion + supervised linear readout.** This is the same
  architecture as an extreme learning machine or reservoir computer. It suits
  learning fast, precise sensorimotor maps from an error signal.
- **Forward models** are standard in robotics and model-based RL (world models):
  predict the next state from the action and correct the controller before feedback
  arrives.

## Code
A Go/NoGo actor (Frank 2005 style) picks among three actions, and a cerebellum-like
learner (fixed random expansion + delta rule) learns a forward model of a 1-D arm.

```python
import numpy as np

rng = np.random.default_rng(0)

# --- Basal ganglia: Go/NoGo actor with a critic ---
p_reward = np.array([0.8, 0.5, 0.2])     # action 0 is best
go, nogo, v = np.zeros(3), np.zeros(3), 0.0
alpha, beta = 0.1, 3.0
for t in range(2000):
    q = go - nogo
    p = np.exp(beta * (q - q.max())); p /= p.sum()
    a = rng.choice(3, p=p)
    r = float(rng.random() < p_reward[a])
    delta = r - v                         # dopamine: reward prediction error
    v += 0.05 * delta
    go[a] += alpha * max(delta, 0)        # burst strengthens D1 Go
    nogo[a] += alpha * max(-delta, 0)     # dip strengthens D2 NoGo
print("Go:", go.round(2), "NoGo:", nogo.round(2))
assert np.argmax(go - nogo) == 0
assert go[2] < nogo[2]                    # the bad action: more NoGo than Go

# --- Cerebellum: forward model, next position = f(position, command) ---
def arm(x, u):                            # unknown nonlinear plant
    return x + 0.5 * np.tanh(u) - 0.1 * x**3

n_granule = 200
W_in = rng.normal(size=(n_granule, 2))    # mossy -> granule, fixed
b_in = rng.normal(size=n_granule)
w_out = np.zeros(n_granule)               # parallel fibre -> Purkinje, learned

def granule(x, u):
    return np.maximum(0, W_in @ np.array([x, u]) + b_in)

def test_error():
    xs, us = rng.uniform(-1, 1, 200), rng.uniform(-2, 2, 200)
    return np.mean([(granule(x, u) @ w_out - arm(x, u))**2 for x, u in zip(xs, us)])

before = test_error()
for _ in range(5000):
    x, u = rng.uniform(-1, 1), rng.uniform(-2, 2)
    g = granule(x, u)
    err = arm(x, u) - g @ w_out          # climbing fibre: prediction error
    w_out += 0.01 * err * g / (g @ g)     # normalised delta rule
after = test_error()
print(f"forward-model MSE: {before:.3f} -> {after:.4f}")
assert after < before / 20
```

## Open questions
- How the brain arbitrates between goal-directed and habitual control, and whether
  "model-based vs model-free" is the right split.
- What the cerebellum contributes to cognition and language, beyond movement
  (it is connected to prefrontal cortex too).
- Whether the climbing fibre carries a pure error, or also reward and prediction
  signals; recent recordings suggest it is richer than Marr-Albus assumed.
- Whether motor cortex represents movement parameters or only generates dynamics.

## Related
- [[learning-and-plasticity]] - dopamine as TD error, the teacher of the Go/NoGo actor.
- [[neuromodulators]] - the other modulators acting on striatum and cortex.
- [[brain-structure-overview]] - where the basal ganglia and cerebellum sit.
- [[predictive-processing]] - forward models as prediction of the senses.
- [[attention-and-working-memory]] - basal ganglia also gate what enters working memory.
- [[brain-inspired-learning-algorithms]] - actor-critic and three-factor rules.

## References
- Albin, Young & Penney (1989) "The functional anatomy of basal ganglia disorders", *Trends Neurosci* 12:366. doi:10.1016/0166-2236(89)90074-X
- Mink (1996) "The basal ganglia: focused selection and inhibition of competing motor programs", *Prog Neurobiol* 50:381. doi:10.1016/S0301-0082(96)00042-1
- Redgrave, Prescott & Gurney (1999) "The basal ganglia: a vertebrate solution to the selection problem?", *Neuroscience* 89:1009. doi:10.1016/S0306-4522(98)00319-4
- Kravitz et al. (2010) "Regulation of parkinsonian motor behaviours by optogenetic control of basal ganglia circuitry", *Nature* 466:622. doi:10.1038/nature09159
- Frank (2005) "Dynamic dopamine modulation in the basal ganglia: a neurocomputational account of cognitive deficits in medicated and nonmedicated Parkinsonism", *J Cogn Neurosci* 17:51. doi:10.1162/0898929052880093
- Frank, Seeberger & O'Reilly (2004) "By carrot or by stick: cognitive reinforcement learning in parkinsonism", *Science* 306:1940. doi:10.1126/science.1102941
- Yin & Knowlton (2006) "The role of the basal ganglia in habit formation", *Nat Rev Neurosci* 7:464. doi:10.1038/nrn1919
- Daw, Niv & Dayan (2005) "Uncertainty-based competition between prefrontal and dorsolateral striatal systems for behavioral control", *Nat Neurosci* 8:1704. doi:10.1038/nn1560
- Azevedo et al. (2009) "Equal numbers of neuronal and nonneuronal cells make the human brain an isometrically scaled-up primate brain", *J Comp Neurol* 513:532. doi:10.1002/cne.21974
- Marr (1969) "A theory of cerebellar cortex", *J Physiol* 202:437. doi:10.1113/jphysiol.1969.sp008820
- Albus (1971) "A theory of cerebellar function", *Math Biosci* 10:25. doi:10.1016/0025-5564(71)90051-4
- Ito (2008) "Control of mental activities by internal models in the cerebellum", *Nat Rev Neurosci* 9:304. doi:10.1038/nrn2332
- Wolpert, Miall & Kawato (1998) "Internal models in the cerebellum", *Trends Cogn Sci* 2:338. doi:10.1016/S1364-6613(98)01221-2
- Ivry & Keele (1989) "Timing functions of the cerebellum", *J Cogn Neurosci* 1:136. doi:10.1162/jocn.1989.1.2.136
- Georgopoulos, Schwartz & Kettner (1986) "Neuronal population coding of movement direction", *Science* 233:1416. doi:10.1126/science.3749885
- Churchland et al. (2012) "Neural population dynamics during reaching", *Nature* 487:51. doi:10.1038/nature11129
