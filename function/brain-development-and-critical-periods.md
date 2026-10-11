---
title: Brain development and critical periods
category: function
tags: [development, neurogenesis, synaptic-pruning, myelination, critical-period, ocular-dominance, language-acquisition, genomic-bottleneck]
use_cases:
  - how does the brain wire itself before and after birth
  - what is a critical period and why does plasticity close
  - why do children learn languages more easily than adults
  - what can AI learn from overproducing and pruning connections
  - how much of the brain is innate versus learned
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1038/nrn1787
  - https://doi.org/10.1113/jphysiol.1970.sp009022
  - https://doi.org/10.1073/pnas.1105108108
  - https://doi.org/10.1038/s41467-019-11786-6
  - https://doi.org/10.48550/arXiv.1711.08856
---

# Brain development and critical periods

## Summary
The brain is not trained from a blank slate. Genes lay out regions, cell types and
coarse wiring before birth; spontaneous activity tunes that wiring before the
senses switch on; then experience refines it, first by making far more synapses
than an adult keeps and then pruning them. Some of that refinement only works
inside **critical periods**, windows that open and close on a schedule. Zador
(2019) argued that the genome is too small to specify the wiring, so it encodes
compact wiring *rules*, the "genomic bottleneck". All of this suggests that AI
should start from good priors and plan when plasticity is high, not just how much
data to show.

## How it works

### Building the scaffold (established)
- **Neurogenesis.** Almost all cortical neurons are generated before birth from
  progenitors lining the ventricles, then migrate outwards along radial glia,
  which builds cortex as columns of related cells (radial unit hypothesis, Rakic
  1988).
- **Adult neurogenesis** in the human hippocampus is **disputed**: one study found
  it falls to undetectable levels in adults (Sorrells et al. 2018), another found
  it persists into old age (Boldrini et al. 2018).
- **Activity before experience.** Before the eyes open, waves of spontaneous
  activity sweep across the retina and help refine visual wiring (Meister et al.
  1991). The brain "pre-trains" on self-generated input.

### Overproduce, then prune (established)
- Synapse density in human cortex rises steeply after birth, peaks in the first
  years, and is then pruned back. The peak comes earlier in sensory cortex than in
  prefrontal cortex (Huttenlocher & Dabholkar 1997). In prefrontal cortex, spine
  density stays high through childhood and declines into the third decade
  (Petanjek et al. 2011).
- Pruning is activity-dependent: less active synapses are removed, partly by
  microglia ([[glia-and-energy-budget]]).
- **Myelination** continues long after: white-matter tracts keep maturing from
  childhood into the twenties and beyond (Lebel & Beaulieu 2011).

### Critical periods (established)
- **Ocular dominance.** Closing one eye in a young kitten shifts visual cortex
  neurons to respond to the open eye (Wiesel & Hubel 1963). The same closure in
  an adult cat has little effect; sensitivity peaks in the first weeks to months
  (Hubel & Wiesel 1970).
- **What opens and closes them.** The maturation of fast-spiking parvalbumin
  inhibitory interneurons opens the window; molecular "brakes" such as
  perineuronal nets around those cells close it (Hensch 2005). Dissolving the
  nets with an enzyme reopened ocular dominance plasticity in adult rats
  (Pizzorusso et al. 2002).
- **Language.** Infants of 6-8 months discriminate speech sounds of any language;
  by 10-12 months they lose most non-native contrasts (Werker & Tees 1984; Kuhl
  2004). A study of about 670,000 English speakers estimated that the ability to
  learn grammar stays high until about age 17 and declines after (Hartshorne,
  Tenenbaum & Pinker 2018). Whether that decline is a biological critical period
  or a change in learning circumstances is still argued.

### Innate structure and the genomic bottleneck (argument)
The human genome holds about 3 billion base pairs, far too little to list 10^14
or more synapses one by one. Zador (2019) argued that evolution therefore encodes
wiring rules and initial biases, and that much animal behaviour is largely innate
and is fine-tuned rather than learned from scratch. This is a framing argument,
not a measured result; see [[brain-vs-deep-learning]].

## Relevance to building brain-like AI
| Brain | AI component |
|---|---|
| Genomic bottleneck | Compact, generative wiring rules and strong priors (architecture, initialisation) instead of learning everything |
| Spontaneous retinal waves | Pre-training on self-generated or synthetic data before real input |
| Overproduce, then prune | Train large, prune small; the lottery-ticket result (Frankle & Carbin 2019) |
| Critical periods | Schedules for learning rate and plasticity; deep networks show critical periods too: an early input deficit leaves a permanent deficit (Achille, Rovere & Soatto 2019) |
| Brakes on plasticity | Freezing or consolidating mature parts to protect them from forgetting ([[memory-systems]]) |

## Code: the same deprivation, early and late

A neuron gets input from a left and a right eye. A Hebbian rule with weight
normalisation (competition between the eyes) sets its weights, and the learning
rate decays with age, a closing critical period. Weakening the left eye for 50
steps early in life shifts the neuron to the right eye; the same deprivation late
in life barely moves it (Hubel & Wiesel 1970). Rates are illustrative.

```python
import numpy as np

def deprive(start, length=50, tau=100.0):
    w = np.array([0.5, 0.5])                     # left eye, right eye
    for t in range(start + length):
        eta = 0.2 * np.exp(-t / tau)             # plasticity falls with age
        x = np.array([0.1, 1.0]) if t >= start else np.ones(2)   # left eye closed
        y = w @ x                                # postsynaptic activity
        w = w + eta * x * y                      # Hebb
        w = w / w.sum()                          # competition: total weight is fixed
    return w[1] - w[0]                           # ocular dominance shift toward the right eye

early, late = deprive(start=0), deprive(start=400)
print(f"shift toward the open eye: early deprivation {early:.2f}, late {late:.3f}")
assert early > 0.5                               # a young neuron is taken over by the open eye
assert early > 10 * late                         # the same closure in an adult does little
```

## Open questions
- How much adult neurogenesis humans have, and whether it matters for memory.
- Which critical periods can be safely reopened in adults, and at what cost to
  stability.
- How compact wiring rules in the genome actually unfold into circuits.
- Whether the language-learning decline is a critical period or a change in how
  and how much people learn.

## Related
- [[learning-and-plasticity]] - the synaptic rules that development schedules.
- [[glia-and-energy-budget]] - microglial pruning and adaptive myelination.
- [[brain-vs-deep-learning]] - innate structure versus learning from scratch (Zador 2019).
- [[sensory-systems-and-vision]] - the visual system whose critical period is best known.
- [[memory-systems]] - stability versus plasticity in the adult brain.

## References
- Rakic (1988) "Specification of cerebral cortical areas", *Science* 241:170. doi:10.1126/science.3291116
- Sorrells et al. (2018) "Human hippocampal neurogenesis drops sharply in children to undetectable levels in adults", *Nature* 555:377. doi:10.1038/nature25975
- Boldrini et al. (2018) "Human hippocampal neurogenesis persists throughout aging", *Cell Stem Cell* 22:589. doi:10.1016/j.stem.2018.03.015
- Meister, Wong, Baylor & Shatz (1991) "Synchronous bursts of action potentials in ganglion cells of the developing mammalian retina", *Science* 252:939. doi:10.1126/science.2035024
- Huttenlocher & Dabholkar (1997) "Regional differences in synaptogenesis in human cerebral cortex", *J Comp Neurol* 387:167.
- Petanjek et al. (2011) "Extraordinary neoteny of synaptic spines in the human prefrontal cortex", *PNAS* 108:13281. doi:10.1073/pnas.1105108108
- Lebel & Beaulieu (2011) "Longitudinal development of human brain wiring continues from childhood into adulthood", *J Neurosci* 31:10937. doi:10.1523/JNEUROSCI.5302-10.2011
- Wiesel & Hubel (1963) "Single-cell responses in striate cortex of kittens deprived of vision in one eye", *J Neurophysiol* 26:1003. doi:10.1152/jn.1963.26.6.1003
- Hubel & Wiesel (1970) "The period of susceptibility to the physiological effects of unilateral eye closure in kittens", *J Physiol* 206:419. doi:10.1113/jphysiol.1970.sp009022
- Hensch (2005) "Critical period plasticity in local cortical circuits", *Nat Rev Neurosci* 6:877. doi:10.1038/nrn1787
- Pizzorusso et al. (2002) "Reactivation of ocular dominance plasticity in the adult visual cortex", *Science* 298:1248. doi:10.1126/science.1072699
- Werker & Tees (1984) "Cross-language speech perception: evidence for perceptual reorganization during the first year of life", *Infant Behav Dev* 7:49. doi:10.1016/S0163-6383(84)80022-3
- Kuhl (2004) "Early language acquisition: cracking the speech code", *Nat Rev Neurosci* 5:831. doi:10.1038/nrn1533
- Hartshorne, Tenenbaum & Pinker (2018) "A critical period for second language acquisition: evidence from 2/3 million English speakers", *Cognition* 177:263. doi:10.1016/j.cognition.2018.04.007
- Zador (2019) "A critique of pure learning and what artificial neural networks can learn from animal brains", *Nat Commun* 10:3770. doi:10.1038/s41467-019-11786-6
- Frankle & Carbin (2019) "The lottery ticket hypothesis: finding sparse, trainable neural networks", ICLR. doi:10.48550/arXiv.1803.03635
- Achille, Rovere & Soatto (2019) "Critical learning periods in deep networks", ICLR. doi:10.48550/arXiv.1711.08856
