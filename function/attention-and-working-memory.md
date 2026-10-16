---
title: Attention and working memory
category: function
tags: [attention, working-memory, prefrontal-cortex, persistent-activity, activity-silent, short-term-plasticity, pbwm, gating, biased-competition, normalization, thalamus, pulvinar, transformer, softmax, capacity, slots-vs-resource, variable-precision, tcc, delayed-estimation, model-comparison]
use_cases:
  - how does working memory hold information and why is its capacity limited
  - is working-memory capacity set by slots or by a shared resource (fit on open data)
  - how does the brain select what to attend to
  - is transformer attention like attention in the brain
  - add a gated working-memory buffer to an agent
status: stable
last_verified: 2026-10-16
sources:
  - https://doi.org/10.1017/S0140525X01003922
  - https://doi.org/10.1037/a0035234
  - https://doi.org/10.1038/s41562-020-00938-0
  - https://github.com/NYUMaLab/delayed_estimation_benchmark
  - https://doi.org/10.1152/jn.1989.61.2.331
  - https://doi.org/10.1126/science.1150769
  - https://doi.org/10.1162/089976606775093909
  - https://doi.org/10.1146/annurev.ne.18.030195.001205
  - https://doi.org/10.1016/j.neuron.2009.01.002
  - https://doi.org/10.3389/fncom.2020.00029
---

# Attention and working memory

## Summary
**Working memory** holds a few items "in mind" for seconds so they can be used.
**Attention** decides which of many inputs gets processed. They are tightly linked:
what you attend to gets into working memory, and what is in working memory steers
attention. Both are limited, and that limit is a feature: the brain has to choose.
Transformer "attention" borrows the name and shares one ingredient
(normalised, input-dependent weighting), but differs in most others.

## How it works

### Working memory capacity (established)
Miller (1956) put short-term memory span at "seven, plus or minus two" items. When
rehearsal and chunking are prevented, the limit is closer to **3-5 chunks** (Cowan
2001). For simple visual objects, Luck & Vogel (1997) measured about 4 items, and
found that objects with several features cost about the same as single-feature ones,
suggesting storage is in units of objects.

### Slots or resource? A cross-validated re-fit on open colour-wheel data (#90)
In delayed estimation, a person sees a few coloured squares, waits a second, then
clicks the remembered colour of one of them on a colour wheel. The error distribution
gets wider and grows heavier tails as the set size N goes up. Two families explain
this. **Slot** models say memory holds at most K items; the rest are guessed. **Resource**
models say a continuous resource is spread over all items, so each item gets less
precision as N grows, and nothing is ever fully lost.

**Step 0, what is already published (checked 2026-10-16).**
- Zhang & Luck (2008) fitted a slots-plus-averaging model: about three slots, and a
  fixed precision once N exceeds them.
- van den Berg, Shin, Chou, George & Ma (2012) proposed **variable precision** (VP):
  precision itself varies from item to item and trial to trial, and VP beat slot models.
- van den Berg, Awh & Ma (2014) crossed three model factors into 32 models and fitted
  them to 10 delayed-estimation experiments from 6 labs (164 subjects, 131,452 trials),
  scored by AIC. Quantized precision (slots plus averaging) was rejected; the best
  model was VP with a Poisson-distributed item limit and non-target reports. The data
  are public as a benchmark (GitHub `NYUMaLab/delayed_estimation_benchmark`, no licence
  stated).
- Schurgin, Wixted & Brady (2020) proposed **TCC** (target confusability competition):
  each colour on the wheel gets a noisy familiarity signal with mean d′ times its
  separately measured psychophysical similarity to the target, and the person reports
  the most familiar colour. One parameter, d′, per condition. On their own data TCC
  matched the two- and three-parameter mixture models in leave-one-out
  cross-validation and was preferred by BIC. Data and code are on OSF (`j2h65`, no
  licence stated).
- Oberauer (2023) placed the mixture model, his interference model and TCC in one
  space of 12 measurement models and fitted 8 data sets (Oberauer & Lin 2017 and the
  five Schurgin et al. experiments). A von Mises signal with a signal-detection choice
  rule fitted best, not TCC's exponential-like signal.
- Tomić & Bays (2024) measured similarity and memory in the same 396 participants
  across four feature spaces. Measured similarity did not predict the memory error
  distributions; for colour, the evidence between TCC and a population-coding model
  was weak (mean ΔAIC 1.57).
- Schneegans, Taylor & Bays (2020) showed that slots plus averaging, VP and population
  coding are points in one sampling framework, fitted to 15 single-report experiments,
  and found random variation in the number of samples per item matters most. TCC was
  not in that comparison.

**What is still open.** No study found here fits TCC next to the slot, slots-plus-
averaging and VP models on the 2014 benchmark, with every model fitted jointly across
set sizes and scored on held-out trials. The Schurgin et al. set-size data have only
been fitted with measurement models (mixture, IMM, TCC), not with these set-size
models. That narrow comparison is what this analysis adds. It cannot say what neurons
do: a better fit is evidence about which description of the error distributions
generalises, not about mechanism.

**Pre-registration (written before the fits were run).**
- *Data.* Colour delayed-estimation with wheel responses: benchmark E1 (Wilken & Ma
  2004, 15 subjects), E2 (Zhang & Luck 2008, 8), E3 (Bays, Catalao & Husain 2009, 12)
  and E8 (van den Berg et al. 2012, 13), plus the Schurgin et al. (2020) set-size
  experiment (20 subjects, set sizes 1, 3, 6, 8). 68 subjects. Orientation sets are
  excluded because TCC's similarity function was measured for colour, and E7 because
  its responses were made by scrolling, not on a wheel. Errors are binned at the data's
  own resolution: 2 degrees for E2 and E8 (180 possible values), 1 degree for the
  others. Every model gives a probability per bin.
- *Models,* each fitted jointly across all set sizes, without non-target reports:
  (1) **slots**: K slots (integer 1-8), an item is stored with probability min(1, K/N)
  at a fixed concentration, else guessed (2 parameters);
  (2) **slots + averaging**: K quanta (1-12) of precision J1, shared as evenly as
  possible among min(N, K) items, plus response noise (3);
  (3) **VP**: mean precision J1 N^-α, precision gamma-distributed with scale τ, plus
  response noise, no item limit (4);
  (4) **TCC**: uncorrelated-noise version with the published colour similarity function
  and fixed 2-degree motor noise, d′ = d1 N^-β (2).
  Secondary: TCC with a free d′ per set size, the measurement model as published.
- *Fit and score.* Maximum likelihood per subject. 10-fold cross-validation stratified
  by set size with a fixed seed; the score is the summed held-out log likelihood
  (CV-LL, in nats per subject).
- *Report.* Per data set and pooled: mean ΔCV-LL of each model against VP with a 95%
  bootstrap CI over subjects (10,000 resamples), and how many subjects each model wins.
- *Control.* Model recovery: synthetic subjects simulated from each model (parameters
  and designs of randomly drawn real subjects), refitted the same way, to check that
  cross-validation can tell the four models apart at these trial counts.
- *Predictions.* (a) Replication: VP beats both slot models on the benchmark sets, as
  with AIC in 2014. (b) TCC vs VP: no prediction; this is the open comparison.
- *What would count against resource models:* a slot model beating both VP and TCC,
  with the CI excluding zero, in most data sets.

**Result (measured, 68 subjects, 38,183 trials; `research/wm_capacity.py`, per-subject
scores in `research/data/wm_capacity_results.csv`).** ΔCV-LL against VP, in nats per
subject, mean [95% bootstrap CI]; negative means VP predicted the held-out trials better:

| Set | n | Slots | Slots + averaging | TCC | TCC, free d′ |
|---|---|---|---|---|---|
| E1 Wilken & Ma | 15 | -13.3 [-20.1, -6.5] | -14.3 [-20.6, -7.7] | -4.9 [-6.2, -3.2] | +0.6 [-2.0, +3.3] |
| E2 Zhang & Luck | 8 | -38.6 [-57.1, -20.3] | -28.6 [-40.9, -15.0] | -1.6 [-5.5, +3.5] | +2.1 [-3.1, +8.9] |
| E3 Bays et al. | 12 | -70.5 [-88.1, -55.0] | -40.4 [-51.6, -28.6] | +0.1 [-3.6, +4.0] | -1.0 [-4.8, +2.7] |
| E8 van den Berg et al. | 13 | -48.1 [-60.0, -36.8] | -38.2 [-50.0, -26.6] | -4.7 [-8.5, -1.2] | -2.6 [-8.1, +2.9] |
| Schurgin et al. | 20 | -25.0 [-32.6, -18.0] | -19.5 [-27.7, -12.6] | +1.7 [-1.5, +5.5] | +2.5 [+0.1, +5.9] |
| All | 68 | -36.5 [-43.7, -29.8] | -26.7 [-31.7, -21.8] | -1.6 [-3.3, +0.1] | +0.4 [-1.4, +2.3] |

Subjects won among the four primary models: VP 42, TCC 23, slots 2, slots + averaging 1.
VP won 12 of 15 (E1), 6 of 8 (E2), 6 of 12 (E3) and 12 of 13 (E8); TCC won 14 of the 20
Schurgin et al. subjects. Fitted slot counts were small: median K = 3 in E1, E3 and E8,
and 2 in E2 and the Schurgin et al. set (slots model). VP's precision fell with set size
as N^-α with median α = 1.11 (IQR 0.83-1.39), and TCC's d′ as N^-β with median β = 0.62
(IQR 0.46-0.74).

Model recovery (10 synthetic subjects per model): the generating model won 31 of 40
times (slots 8, slots + averaging 7, VP 8, TCC 8 of 10). Errors stayed mostly inside a
family: slots and slots + averaging swapped 5 times, VP and TCC 3 times, and one
VP-generated subject went to slots. So at these trial counts cross-validation separates
slot from resource accounts reliably (1 of 40 crossed), and VP from TCC about four times
in five.

**What this shows.**
- *Slots vs resource (replication, measured).* Both slot models lost to VP in every data
  set, with every CI below zero, and won 3 of 68 subjects. This repeats van den Berg et
  al.'s (2014) AIC result with held-out likelihood and extends it to the Schurgin et al.
  data. The pre-registered result that would have counted against resource models did
  not occur.
- *VP vs TCC (the open comparison, measured).* Pooled, there is no reliable difference
  (-1.6 nats per subject, CI -3.3 to +0.1). It depends on the data set: VP is better on
  E1 and E8, the two are level on E2 and E3, and TCC wins most subjects on the Schurgin
  et al. data, where its free-d′ version is ahead by +2.5 [+0.1, +5.9].
- *Why TCC does best on its own data (hypothesis, untested).* TCC's similarity function
  was measured on the Schurgin et al. colour wheel. The benchmark sets used other
  wheels, so the function is only an approximation there. Fitting a similarity function
  per wheel, or measuring it, would test this; Tomić & Bays (2024) found measured
  similarity did not predict memory errors even within a wheel.
- *What it does not show.* A better fit says which description of the error
  distributions generalises. It does not show whether neurons hold items in slots or
  share a resource; population-coding models of the resource idea (Schneegans, Taylor &
  Bays 2020) were not fitted here.

**Limits and deviations.** No model has non-target (swap) reports or a lapse rate, and
VP with an item limit, the 2014 winner, was not fitted, so "resource" here means VP and
TCC as defined above. E1 and E3 errors are continuous and were rounded to 1-degree bins.
Before the final run, a code review and a convergence check led to three
implementation fixes that leave the model definitions unchanged: the response-noise
convolution was changed from FFT to an exact circulant product (FFT round-off made tiny
tail probabilities zero), the recovery sampler now draws from the same 2-degree bins the
likelihood scores, and slots + averaging got an extra start after it missed its optimum
by up to 7.9 nats on 2 of 10 checked subjects (after the fix, on the same 10 subjects,
at least 25 random restarts per model improved no full-data fit by more than 0.005 nats). A 10-subject, 2-fold smoke run had been
seen before these fixes.

### Mechanism 1: persistent activity (established)
Neurons in prefrontal cortex keep firing through a delay while a monkey remembers a
cue (Fuster & Alexander 1971). In a delayed saccade task, dorsolateral prefrontal
neurons fired during the delay for specific remembered locations (Funahashi, Bruce
& Goldman-Rakic 1989). The standard model is an **attractor**: recurrent excitation
(slow NMDA receptors help) keeps a "bump" of activity alive after the input ends
(Wang 2001).

### Mechanism 2: activity-silent storage (hypothesis, growing support)
Some items seem to be held without sustained firing. Mongillo, Barak & Tsodyks
(2008) proposed that **short-term synaptic facilitation** stores the item in the
synapses for about a second, and occasional bursts of activity refresh it. Stokes
(2015) argued that working memory combines active states (for the item in use) and
silent synaptic traces (for items held in reserve). How much of working memory is
silent is still debated.

### Gating: prefrontal cortex and basal ganglia (model)
A buffer that updates on every input forgets what it holds; one that never updates
is useless. **PBWM** (prefrontal cortex basal ganglia working memory; O'Reilly &
Frank 2006) proposes that the basal ganglia **gate** each prefrontal "stripe": a Go
signal lets new input in, otherwise the stripe keeps its content. Dopamine teaches
the gate when updating paid off, the same Go/NoGo learning as for actions
([[action-selection-and-motor-control]]). This is a well-developed **model**; the
stripe anatomy it assumes is not fully confirmed. LSTM gates solve the same
problem in machine learning.

### Attention: biased competition (established)
Two stimuli inside one neuron's receptive field compete: the response to the pair
is roughly an average of the two alone. Attending to one of them pulls the response
toward what that stimulus alone would give (Moran & Desimone 1985). Desimone &
Duncan (1995) called this **biased competition**: stimuli compete for
representation, and top-down signals (from prefrontal and parietal cortex) bias the
competition toward the behaviourally relevant one.

### Attention as normalization (model, quantitatively supported)
Reynolds & Heeger (2009) unified many results with one equation. A neuron's
response is its excitatory drive, multiplied by an attention field, divided by the
pooled drive of its neighbours (also attention-weighted):

`R = (A · E) / (Σ_pool A · E + σ)`

Depending on the relative sizes of the stimulus and the attention field, this
reproduces both "contrast gain" and "response gain" effects of attention.

### The thalamic gate (hypothesis)
Crick (1984) proposed that the thalamic reticular nucleus, a sheet of inhibitory
neurons wrapped around the thalamus, acts as an attentional "searchlight". In mice,
prefrontal cortex controls which sensory stream reaches cortex through this nucleus
(Wimmer et al. 2015), and the pulvinar coordinates synchrony between visual areas
(Saalmann et al. 2012).
Halassa & Kastner (2017) review the thalamus as a controller of cortical
communication rather than a passive relay.

### Transformer attention compared
| | Brain attention | Transformer attention |
|---|---|---|
| What is weighted | Neural responses to stimuli, across space, features or objects | Value vectors of other tokens |
| Normalisation | Divisive normalisation by a pooled drive (established) | Softmax over keys |
| Who decides | Top-down goals plus bottom-up salience | Learned query-key similarity, computed for every token |
| Capacity | Strongly limited (a few items) | All tokens in context, every layer |
| Cost | Saves resources by ignoring most input | Quadratic in sequence length; ignores nothing |

**Analogous:** both are dynamic, input-dependent re-weighting followed by
normalisation, and softmax attention is equivalent to one step of a modern Hopfield
network retrieval (Ramsauer et al. 2020), a link to associative memory. **Not
analogous:** transformers have no capacity limit, no top-down goal separate from
the input, and no serial bottleneck. Whether transformer attention is a good model of
any brain process is an **open question** (Lindsay 2020 compares the uses of the
word).

## Relevance to building brain-like AI
- **Gate the memory, learn the gate.** A working-memory buffer with learned
  input gates (PBWM, LSTM) holds task-relevant items against distractors.
- **Use a hard capacity limit** where you want selection and compositional
  structure, not just more context; slot-based models do this. Note that this is a
  design choice: human colour-memory errors are better described by a graded resource
  that thins as items are added than by a fixed number of slots (#90).
- **Normalisation is cheap attention.** Divisive normalisation with a top-down gain
  field biases processing toward the goal without computing all-pairs similarity.
- **Silent storage** suggests a cheap memory: keep items in fast synaptic weights
  (fast weights, short-term plasticity) instead of in activity.

## Code
The normalization model reproduces biased competition: a neuron's response to a
preferred plus a non-preferred stimulus moves toward the preferred-alone response
when attention is on the preferred one. Then a gated buffer keeps a cue through
distractors, where an ungated one loses it.

```python
import numpy as np

# --- Normalization model of attention (Reynolds & Heeger 2009, two stimuli) ---
def response(drive, attn, sigma=0.1):
    e = np.asarray(drive, float)          # excitatory drive of each stimulus
    a = np.asarray(attn, float)           # attention gain on each stimulus
    return (a * e).sum() / (a.sum() + sigma)

pref, nonpref = 1.0, 0.2
alone = response([pref], [1.0])
pair = response([pref, nonpref], [1.0, 1.0])
attend_pref = response([pref, nonpref], [3.0, 1.0])
attend_non = response([pref, nonpref], [1.0, 3.0])
print(f"pref alone {alone:.2f}  pair {pair:.2f}  "
      f"attend pref {attend_pref:.2f}  attend nonpref {attend_non:.2f}")
assert attend_non < pair < attend_pref < alone

# --- Gated working memory: a cue followed by distractors ---
rng = np.random.default_rng(0)
cue = 7
stream = [cue] + list(rng.integers(0, 10, 5))
gate = [True] + [False] * 5               # basal-ganglia Go only for the cue
ungated, gated = None, None
for item, go in zip(stream, gate):
    ungated = item                        # updates on every input
    if go:
        gated = item                      # updates only when the gate opens
print("stream:", stream, "| ungated holds", ungated, "| gated holds", gated)
assert gated == cue
```

## Open questions
- How much of working memory is persistent firing and how much is silent synaptic
  storage, and whether this differs by task.
- What sets the capacity limit: a fixed number of slots, or a shared resource spread
  over items. On open colour-wheel data, resource models (VP, TCC) predict held-out
  errors better than slot models in all five data sets tested (#90, above). Still open:
  VP vs TCC (no reliable pooled difference, and the winner depends on the data set),
  whether the answer holds with swap reports and item-limited VP in the comparison, and
  what neural mechanism implements the resource.
- How top-down attention signals are routed: through cortical feedback, the
  thalamus, synchrony between areas, or all three.
- Whether anything in the brain does all-pairs, content-based attention like a
  transformer; the hippocampus has been proposed.

## Related
- [[action-selection-and-motor-control]] - the basal ganglia gate actions and working-memory updates alike.
- [[memory-systems]] - working memory vs long-term memory; Hopfield retrieval.
- [[predictive-processing]] - attention as precision-weighting of prediction errors.
- [[neuromodulators]] - acetylcholine and noradrenaline as uncertainty and attention signals.
- [[brain-vs-deep-learning]] - where transformers depart from the brain.
- [Brain World](../game/world/) - context gating: each of 8 context slots switches off half of a shared layer, and the brain infers the slot from what it has sensed (adaptive resonance), a hypothesis-level model of prefrontal top-down gating.

## References
- Miller (1956) "The magical number seven, plus or minus two", *Psychol Rev* 63:81. doi:10.1037/h0043158
- Cowan (2001) "The magical number 4 in short-term memory: a reconsideration of mental storage capacity", *Behav Brain Sci* 24:87. doi:10.1017/S0140525X01003922
- Luck & Vogel (1997) "The capacity of visual working memory for features and conjunctions", *Nature* 390:279. doi:10.1038/36846
- Wilken & Ma (2004) "A detection theory account of change detection", *J Vis* 4(12):11. doi:10.1167/4.12.11
- Zhang & Luck (2008) "Discrete fixed-resolution representations in visual working memory", *Nature* 453:233. doi:10.1038/nature06860
- Bays, Catalao & Husain (2009) "The precision of visual working memory is set by allocation of a shared resource", *J Vis* 9(10):7. doi:10.1167/9.10.7
- van den Berg, Shin, Chou, George & Ma (2012) "Variability in encoding precision accounts for visual short-term memory limitations", *PNAS* 109:8780. doi:10.1073/pnas.1117465109
- van den Berg, Awh & Ma (2014) "Factorial comparison of working memory models", *Psychol Rev* 121:124. doi:10.1037/a0035234. Benchmark data: https://github.com/NYUMaLab/delayed_estimation_benchmark (no licence stated)
- Oberauer & Lin (2017) "An interference model of visual working memory", *Psychol Rev* 124:21. doi:10.1037/rev0000044
- Schurgin, Wixted & Brady (2020) "Psychophysical scaling reveals a unified theory of visual memory strength", *Nat Hum Behav* 4:1156. doi:10.1038/s41562-020-00938-0. Data and code: https://osf.io/j2h65/ (no licence stated)
- Schneegans, Taylor & Bays (2020) "Stochastic sampling provides a unifying account of visual working memory limits", *PNAS* 117:20959. doi:10.1073/pnas.2004306117
- Oberauer (2023) "Measurement models for visual working memory: a factorial model comparison", *Psychol Rev* 130:841. doi:10.1037/rev0000328
- Tomić & Bays (2024) "Perceptual similarity judgments do not predict the distribution of errors in working memory", *J Exp Psychol Learn Mem Cogn* 50:535. doi:10.1037/xlm0001172
- Fuster & Alexander (1971) "Neuron activity related to short-term memory", *Science* 173:652. doi:10.1126/science.173.3997.652
- Funahashi, Bruce & Goldman-Rakic (1989) "Mnemonic coding of visual space in the monkey's dorsolateral prefrontal cortex", *J Neurophysiol* 61:331. doi:10.1152/jn.1989.61.2.331
- Wang (2001) "Synaptic reverberation underlying mnemonic persistent activity", *Trends Neurosci* 24:455. doi:10.1016/S0166-2236(00)01868-3
- Mongillo, Barak & Tsodyks (2008) "Synaptic theory of working memory", *Science* 319:1543. doi:10.1126/science.1150769
- Stokes (2015) "'Activity-silent' working memory in prefrontal cortex: a dynamic coding framework", *Trends Cogn Sci* 19:394. doi:10.1016/j.tics.2015.05.004
- O'Reilly & Frank (2006) "Making working memory work: a computational model of learning in the prefrontal cortex and basal ganglia", *Neural Comput* 18:283. doi:10.1162/089976606775093909
- Moran & Desimone (1985) "Selective attention gates visual processing in the extrastriate cortex", *Science* 229:782. doi:10.1126/science.4023713
- Desimone & Duncan (1995) "Neural mechanisms of selective visual attention", *Annu Rev Neurosci* 18:193. doi:10.1146/annurev.ne.18.030195.001205
- Reynolds & Heeger (2009) "The normalization model of attention", *Neuron* 61:168. doi:10.1016/j.neuron.2009.01.002
- Crick (1984) "Function of the thalamic reticular complex: the searchlight hypothesis", *PNAS* 81:4586. doi:10.1073/pnas.81.14.4586
- Wimmer et al. (2015) "Thalamic control of sensory selection in divided attention", *Nature* 526:705. doi:10.1038/nature15398
- Saalmann, Pinsk, Wang, Li & Kastner (2012) "The pulvinar regulates information transmission between cortical areas based on attention demands", *Science* 337:753. doi:10.1126/science.1223082
- Halassa & Kastner (2017) "Thalamic functions in distributed cognitive control", *Nat Neurosci* 20:1669. doi:10.1038/s41593-017-0020-1
- Vaswani et al. (2017) "Attention is all you need", arXiv:1706.03762.
- Ramsauer et al. (2020) "Hopfield Networks is All You Need", arXiv:2008.02217.
- Lindsay (2020) "Attention in psychology, neuroscience, and machine learning", *Front Comput Neurosci* 14:29. doi:10.3389/fncom.2020.00029
