---
title: Decision-making and evidence accumulation (drift diffusion, confidence, value)
category: function
tags: [decision-making, evidence-accumulation, drift-diffusion, ddm, lip, fef, speed-accuracy, urgency, confidence, metacognition, orbitofrontal, vmpfc, value, explore-exploit, adaptive-compute]
use_cases:
  - how does the brain decide between two options under noise
  - what is the drift-diffusion model and why does it explain the speed-accuracy trade-off
  - how does the brain know how confident it is in a choice
  - where is value computed for economic choices
  - make an AI think longer when it is unsure, like the brain does
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1162/neco.2008.12-06-420
  - https://doi.org/10.1146/annurev.neuro.29.051605.113038
  - https://doi.org/10.1037/0033-295X.113.4.700
  - https://doi.org/10.1126/science.1169405
  - https://doi.org/10.1038/nature04676
  - https://doi.org/10.1038/nature04766
---

# Decision-making and evidence accumulation (drift diffusion, confidence, value)

## Summary
Most decisions are made on noisy evidence. The best-supported account is that the
brain **adds up evidence over time** until a running total reaches a **threshold**,
then commits. Raising the threshold buys accuracy at the cost of time: the
speed-accuracy trade-off. The same accumulated quantity tells the brain how
**confident** it should be. For choices between goods rather than percepts,
orbitofrontal and ventromedial prefrontal cortex hold a common-currency **value**,
learned with the help of dopamine prediction errors. Each idea has a direct AI
analogue: calibrated confidence and spending more compute when unsure.

## How it works

### Evidence accumulation and the drift-diffusion model
**The model (established as a description of behaviour).** The drift-diffusion
model (DDM; Ratcliff 1978; Ratcliff & McKoon 2008) treats a two-choice decision as
a variable `x` that starts near 0 and moves by `dx = v·dt + s·dW`: a **drift** `v`
set by evidence quality plus noise. The choice is made when `x` hits `+a` or `-a`.
Drift explains how easy the stimulus is; the **threshold** `a` explains strategy.
The DDM fits both accuracy and the full shape of reaction-time distributions in many
two-choice tasks (Ratcliff & McKoon 2008).

**Why it is a good algorithm (established, mathematical).** For two alternatives,
the DDM is the continuous form of the sequential probability ratio test, which gives
the shortest mean decision time for a given error rate (Bogacz et al. 2006). For an
unbiased start, accuracy is `1 / (1 + exp(-2va/s²))`, so a larger `a` gives more
accurate but slower choices: the speed-accuracy trade-off in one parameter.

**Neural ramps (supported, debated).** In monkeys judging the direction of noisy
moving dots, neurons in the **lateral intraparietal area (LIP)** ramp up during
viewing at a rate that grows with motion strength and reach a similar level just
before the eye movement that reports the choice (Roitman & Shadlen 2002). Movement
neurons in the **frontal eye field (FEF)** rise to a fixed level before a saccade,
and reaction-time variability is explained mostly by how fast they rise (Hanes &
Schall 1996). These ramps look like the DDM's `x` (review: Gold & Shadlen 2007).
Two findings complicate the picture:
- Inactivating LIP left monkeys' motion choices intact, while inactivating MT
  impaired them (Katz et al. 2016), so LIP may reflect the decision rather than be
  required for it.
- Single-trial LIP spike trains were fit better by a discrete **step** than by a
  smooth ramp (Latimer et al. 2015), so the average ramp may be steps at different
  times. This is contested.

**Urgency (supported).** Thresholds are not fixed in time. LIP activity contains an
evidence-independent signal that grows during the trial (Churchland, Kiani &
Shadlen 2008), and the urgency-gating model multiplies evidence by a rising urgency
term (Cisek, Puskas & El-Murr 2009). Both act like a threshold that collapses over
time, which caps how long a hard decision can take.

### Confidence and metacognition
- **Confidence is read out from the accumulator (supported).** Monkeys given a
  low-reward "sure" option took it more on hard trials, and LIP activity predicted
  whether they would opt out (Kiani & Shadlen 2009). Rats' willingness to wait for
  an uncertain reward tracked confidence, and orbitofrontal neurons carried a
  confidence-like signal (Kepecs et al. 2008).
- **Metacognition can be measured and dissociated (supported).** How well a
  person's confidence tracks their own accuracy varies between people and has been
  linked to anterior (rostrolateral) prefrontal cortex (Fleming & Dolan 2012).
- **Hypothesis:** a separate second-order system re-reads the evidence to judge
  confidence, rather than confidence being a direct function of the accumulator.
  Both accounts are argued for.

### Value-based choice
- **OFC encodes value (established for monkeys).** Neurons in orbitofrontal cortex
  encode the subjective value of offered and chosen goods, independent of the
  visual or motor details of the offer (Padoa-Schioppa & Assad 2006).
- **vmPFC and ventral striatum (supported).** A meta-analysis of fMRI studies found
  ventromedial prefrontal cortex and ventral striatum tracking subjective value
  across reward types (Bartra, McGuire & Kable 2013).
- **Accumulation applies here too (supported).** A DDM whose drift depends on the
  value difference, weighted by where the eyes look, fits choices and reaction times
  between snack foods (Krajbich, Armel & Rangel 2010).
- **Where values come from:** dopamine reward prediction errors train them
  ([[learning-and-plasticity]]); the basal ganglia then release the chosen action
  ([[action-selection-and-motor-control]]).

### Explore vs exploit
Choosing the best-known option forgoes information about the others. In a
four-armed bandit, a softmax model fit human choices best, and exploratory choices
activated **frontopolar cortex** and intraparietal sulcus (Daw et al. 2006). People
use both **random** exploration (noise in choice) and **directed** exploration
(seeking the most uncertain option) (Wilson et al. 2014). Adaptive gain theory
proposes that high tonic **noradrenaline** from the locus coeruleus promotes
exploring and phasic bursts promote exploiting (Aston-Jones & Cohen 2005); this is a
**hypothesis** ([[neuromodulators]]).

## Relevance to building brain-like AI
- **Calibrated confidence.** The brain's confidence tracks its accuracy well enough
  to drive opt-out choices. Modern deep networks tend to be overconfident, and a
  single temperature parameter fitted after training fixes much of it (Guo et al.
  2017). Large language models can be fairly well calibrated on multiple-choice
  questions and can be trained to predict whether they know an answer (Kadavath et
  al. 2022).
- **Adaptive compute: think longer when unsure.** A threshold on accumulated
  evidence spends time only where it is needed. Adaptive Computation Time lets a
  recurrent network learn how many steps to take per input, with a halting unit that
  plays the role of the threshold (Graves 2016). Sampling a model several times and
  stopping once the answers agree is the same idea.
- **Collapsing bounds** are a cheap way to cap worst-case latency.
- **Separate value from action**: a common-currency value that is learned and then
  compared mirrors the critic and the policy in actor-critic RL.

## Code
A drift-diffusion simulation. Raising the threshold makes decisions slower and more
accurate, and accuracy matches the closed form above.

```python
import numpy as np

rng = np.random.default_rng(0)

def ddm(threshold, drift=0.5, noise=1.0, dt=0.01, n=2000, max_t=20.0):
    """n trials of dx = drift*dt + noise*dW until |x| >= threshold.
    +threshold is the correct answer. Returns (accuracy, mean decision time)."""
    x, t = np.zeros(n), np.zeros(n)
    done = np.zeros(n, bool)
    for _ in range(int(max_t / dt)):
        live = ~done
        if not live.any():
            break
        x[live] += drift * dt + noise * np.sqrt(dt) * rng.standard_normal(live.sum())
        t[live] += dt
        done |= np.abs(x) >= threshold
    return (x[done] > 0).mean(), t[done].mean()

results = {}
for a in (0.5, 1.0, 1.5):
    acc, rt = ddm(a)
    theory = 1 / (1 + np.exp(-2 * 0.5 * a))   # P(correct), unbiased start, noise 1
    results[a] = (acc, rt)
    print(f"threshold {a}: accuracy {acc:.3f} (theory {theory:.3f}), "
          f"mean decision time {rt:.2f} s")
    assert abs(acc - theory) < 0.05

(acc_lo, rt_lo), (acc_hi, rt_hi) = results[0.5], results[1.5]
assert rt_hi > rt_lo    # higher threshold -> slower
assert acc_hi > acc_lo  # ... and more accurate
```

## Open questions
- Is LIP part of the decision computation or a read-out of it, and which areas are
  actually necessary (Katz et al. 2016)?
- Do single neurons ramp or step, and does the answer differ between areas?
- How are thresholds and urgency set and adjusted from moment to moment, and by
  which circuit (basal ganglia, neuromodulators)?
- How does accumulation extend to many options and to choices that unfold over
  minutes rather than seconds?
- Is confidence computed by the same accumulator or by a separate monitor?

## Related
- [[learning-and-plasticity]] - dopamine prediction errors that teach values.
- [[action-selection-and-motor-control]] - basal ganglia release the chosen action; model-based vs model-free control.
- [[neuromodulators]] - noradrenaline and exploration, serotonin and patience.
- [[attention-and-working-memory]] - holding evidence and goals while deciding.
- [[emotion-amygdala-and-interoception]] - value signals beside OFC.
- [[prefrontal-cortex-and-abstraction]] - frontal control over choice and metacognition.
- [[brain-disorders-and-computational-psychiatry]] - how altered value learning and choice show up in disorders.

## References
- Ratcliff (1978) "A theory of memory retrieval", *Psychol Rev* 85:59. doi:10.1037/0033-295X.85.2.59
- Ratcliff & McKoon (2008) "The diffusion decision model: theory and data for two-choice decision tasks", *Neural Comput* 20:873. doi:10.1162/neco.2008.12-06-420
- Bogacz, Brown, Moehlis, Holmes & Cohen (2006) "The physics of optimal decision making", *Psychol Rev* 113:700. doi:10.1037/0033-295X.113.4.700
- Gold & Shadlen (2007) "The neural basis of decision making", *Annu Rev Neurosci* 30:535. doi:10.1146/annurev.neuro.29.051605.113038
- Roitman & Shadlen (2002) "Response of neurons in the lateral intraparietal area during a combined visual discrimination reaction time task", *J Neurosci* 22:9475. doi:10.1523/JNEUROSCI.22-21-09475.2002
- Hanes & Schall (1996) "Neural control of voluntary movement initiation", *Science* 274:427. doi:10.1126/science.274.5286.427
- Katz, Yates, Pillow & Huk (2016) "Dissociated functional significance of decision-related activity in the primate dorsal stream", *Nature* 535:285. doi:10.1038/nature18617
- Latimer, Yates, Meister, Huk & Pillow (2015) "Single-trial spike trains in parietal cortex reveal discrete steps during decision-making", *Science* 349:184. doi:10.1126/science.aaa4056
- Churchland, Kiani & Shadlen (2008) "Decision-making with multiple alternatives", *Nat Neurosci* 11:693. doi:10.1038/nn.2123
- Cisek, Puskas & El-Murr (2009) "Decisions in changing conditions: the urgency-gating model", *J Neurosci* 29:11560. doi:10.1523/JNEUROSCI.1844-09.2009
- Kiani & Shadlen (2009) "Representation of confidence associated with a decision by neurons in the parietal cortex", *Science* 324:759. doi:10.1126/science.1169405
- Kepecs, Uchida, Zariwala & Mainen (2008) "Neural correlates, computation and behavioural impact of decision confidence", *Nature* 455:227. doi:10.1038/nature07200
- Fleming & Dolan (2012) "The neural basis of metacognitive ability", *Phil Trans R Soc B* 367:1338. doi:10.1098/rstb.2011.0417
- Padoa-Schioppa & Assad (2006) "Neurons in the orbitofrontal cortex encode economic value", *Nature* 441:223. doi:10.1038/nature04676
- Bartra, McGuire & Kable (2013) "The valuation system: a coordinate-based meta-analysis of BOLD fMRI experiments examining neural correlates of subjective value", *NeuroImage* 76:412. doi:10.1016/j.neuroimage.2013.02.063
- Krajbich, Armel & Rangel (2010) "Visual fixations and the computation and comparison of value in simple choice", *Nat Neurosci* 13:1292. doi:10.1038/nn.2635
- Daw, O'Doherty, Dayan, Seymour & Dolan (2006) "Cortical substrates for exploratory decisions in humans", *Nature* 441:876. doi:10.1038/nature04766
- Wilson, Geana, White, Ludvig & Cohen (2014) "Humans use directed and random exploration to solve the explore-exploit dilemma", *J Exp Psychol Gen* 143:2074. doi:10.1037/a0038199
- Aston-Jones & Cohen (2005) "An integrative theory of locus coeruleus-norepinephrine function", *Annu Rev Neurosci* 28:403. doi:10.1146/annurev.neuro.28.061604.135709
- Guo, Pleiss, Sun & Weinberger (2017) "On calibration of modern neural networks", ICML. arXiv:1706.04599
- Kadavath et al. (2022) "Language models (mostly) know what they know", arXiv:2207.05221
- Graves (2016) "Adaptive computation time for recurrent neural networks", arXiv:1603.08983
