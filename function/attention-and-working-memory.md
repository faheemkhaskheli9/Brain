---
title: Attention and working memory
category: function
tags: [attention, working-memory, prefrontal-cortex, persistent-activity, activity-silent, short-term-plasticity, pbwm, gating, biased-competition, normalization, thalamus, pulvinar, transformer, softmax]
use_cases:
  - how does working memory hold information and why is its capacity limited
  - how does the brain select what to attend to
  - is transformer attention like attention in the brain
  - add a gated working-memory buffer to an agent
status: stable
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1017/S0140525X01003922
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
  structure, not just more context; slot-based models do this.
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
  over items.
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
- [Brain World](../game/world/) - task-context gating: each skill switches off half of a shared layer, a hypothesis-level model of prefrontal top-down gating.

## References
- Miller (1956) "The magical number seven, plus or minus two", *Psychol Rev* 63:81. doi:10.1037/h0043158
- Cowan (2001) "The magical number 4 in short-term memory: a reconsideration of mental storage capacity", *Behav Brain Sci* 24:87. doi:10.1017/S0140525X01003922
- Luck & Vogel (1997) "The capacity of visual working memory for features and conjunctions", *Nature* 390:279. doi:10.1038/36846
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
