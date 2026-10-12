---
title: Theories of consciousness (hypotheses)
category: function
tags: [consciousness, global-workspace, iit, higher-order, recurrent-processing, ignition, adversarial-collaboration, pci, machine-consciousness]
use_cases:
  - what are the main scientific theories of consciousness
  - what is global workspace theory, what is integrated information theory
  - what did the adversarial collaboration between GNWT and IIT find
  - how do doctors measure consciousness in unresponsive patients
  - could an AI system be conscious
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1038/s41583-022-00587-4
  - https://doi.org/10.1016/j.neuron.2011.03.018
  - https://doi.org/10.1038/nrn.2016.44
  - https://doi.org/10.1038/s41586-025-08888-1
  - https://doi.org/10.1126/scitranslmed.3006294
---

# Theories of consciousness (hypotheses)

## Summary
Every theory on this page is a **hypothesis**. None is established, and they
disagree on basic points, such as whether the prefrontal cortex is needed. What
*is* established is the experimental toolkit (contrasting seen and unseen
stimuli) and a few clinical measures. This file is kept apart so that the
debate does not leak into the established topics; when another file mentions
consciousness, it links here.

## How it works

### What is measured (established)
- **Contrastive method.** Keep the stimulus the same and compare trials where
  the person reports seeing it with trials where they do not (masking,
  binocular rivalry, threshold stimuli). The brain activity that differs is a
  candidate **neural correlate of consciousness** (NCC).
- **Blindsight.** Patients with damage to primary visual cortex can point to or
  guess about objects in their blind field above chance while reporting that
  they see nothing (Weiskrantz et al. 1974). Processing and awareness can come
  apart.
- **Perturbational complexity index (PCI).** Pulse the cortex with TMS, record
  the EEG echo and compress it. Awake and dreaming brains give complex,
  widespread echoes; deep sleep and anaesthesia give simple or local ones
  (Casali et al. 2013). PCI is used to look for covert consciousness in
  unresponsive patients. It is motivated by integration theories but works as a
  clinical measure whichever theory is right.

### The main theories (all hypotheses)
Reviewed in Seth & Bayne (2022).

| Theory | Claim | Where | Signature it predicts |
|---|---|---|---|
| **Global (neuronal) workspace**, GNWT (Baars 1988; Dehaene & Changeux 2011) | Content becomes conscious when it wins a competition and is broadcast to many specialist systems at once | Prefrontal and parietal cortex with long-range connections | Late, all-or-none **ignition** (~300 ms) when a stimulus is seen |
| **Integrated information theory**, IIT (Tononi 2004; Tononi et al. 2016) | Consciousness is integrated information (Φ), a property of a system's causal structure, not of what it computes | A posterior "hot zone" of cortex | Sustained activity and synchrony in posterior cortex for as long as the experience lasts |
| **Higher-order theories**, HOT (Lau & Rosenthal 2011; Brown, Lau & LeDoux 2019) | A state is conscious when another state represents it, a kind of internal monitoring | Prefrontal cortex | Prefrontal activity linked to confidence and metacognition |
| **Recurrent processing theory**, RPT (Lamme 2006) | Local feedback within sensory cortex is enough for experience; the workspace adds only access and report | Sensory cortex | Recurrent activity in visual cortex, even without report |

IIT is the most contested. Its Φ cannot be computed for any real brain, and it
implies that simple but highly integrated grids of logic gates are more
conscious than a person. In 2023 over 100 researchers signed a letter calling
it pseudoscience (Fleming et al. 2023); many others objected to that label.

### The adversarial collaboration (established result, contested reading)
GNWT and IIT proponents agreed in advance on predictions that would count
against their own theory, and labs not aligned with either ran the experiments
with fMRI, MEG and intracranial EEG (Melloni et al. 2023 protocol; Cogitate
Consortium 2025). Outcome, in brief:
- Information about what was seen (category, orientation) was found in
  posterior cortex, with less in prefrontal cortex than GNWT expected.
- GNWT's predicted ignition when the stimulus went away was mostly absent.
- IIT's predicted sustained synchrony within posterior cortex was not found.

Both theories had key predictions fail; neither was falsified outright, and
both camps published rebuttals. The lasting result is the method: pre-registered
tests that theories agree can hurt them.

## Relevance to building brain-like AI
| Idea | What a system can borrow |
|---|---|
| Global workspace | A capacity-limited shared buffer that modules compete to write to and all read from; a known architecture for coordination (see [[attention-and-working-memory]]) |
| Ignition | Nonlinear recurrent amplification turns graded evidence into an all-or-none commitment |
| Higher-order monitoring | A model of the system's own confidence: calibrated uncertainty, knowing what it does not know |
| Indicator properties | Butlin et al. (2023) list properties each theory treats as indicators and check AI systems against them; they found no current system that has most of them. This is an assessment method, not a test that settles the question |

Building a workspace does not make a system conscious under every theory: under
IIT, a conventional computer running any software has low Φ.

## Code: ignition in a recurrent workspace

GNWT's signature is ignition: a stimulus below threshold fades, one above
threshold triggers self-sustaining activity. A single rate unit with strong
self-excitation shows this (an illustration of the mechanism, not of
consciousness). Parameters are illustrative.

```python
import numpy as np

def run(stimulus, w_self=6.0, theta=3.0, steps=200, dt=0.1, stim_steps=20):
    r = 0.0
    trace = []
    for t in range(steps):
        inp = stimulus if t < stim_steps else 0.0       # brief stimulus, then nothing
        drive = w_self * r + inp
        r += dt * (-r + 1 / (1 + np.exp(-(drive - theta) * 2)))   # sigmoid rate unit
        trace.append(r)
    return np.array(trace)

strengths = np.linspace(0, 4, 21)
final = np.array([run(s)[-1] for s in strengths])
for s, f in zip(strengths[::4], final[::4]):
    print(f"stimulus {s:.1f} -> activity long after it ends {f:.2f}")

assert final[0] < 0.1                       # no stimulus: stays quiet
assert final[-1] > 0.9                      # strong stimulus: ignites and holds
gaps = np.diff(final)
assert gaps.max() > 0.5                     # all-or-none jump, not a graded rise
```

## Open questions
- Whether consciousness needs the prefrontal cortex.
- Whether report is needed to study it, and how to separate experience from
  the act of reporting it (no-report paradigms).
- Whether Φ, or any measure, can be computed and tested in a real brain.
- Whether any AI system could be conscious, and how anyone would tell.

## Related
- [[attention-and-working-memory]] - the workspace and working memory are closely linked.
- [[predictive-processing]] - some accounts treat experience as the brain's best prediction.
- [[emotion-amygdala-and-interoception]] - feeling and the insula, the bodily side of the question.
- [[brain-rhythms-and-oscillations]] - synchrony, which IIT and binding accounts rely on.
- [[evaluating-brain-models]] - testing models against the brain, the same problem in miniature.
- [[sleep-and-memory-consolidation]] - sleep stages, where PCI and consciousness change together.
- [[neuroethics]] - what follows if a simulation or organoid might be conscious.

## References
- Seth & Bayne (2022) "Theories of consciousness", *Nat Rev Neurosci* 23:439. doi:10.1038/s41583-022-00587-4
- Weiskrantz, Warrington, Sanders & Marshall (1974) "Visual capacity in the hemianopic field following a restricted occipital ablation", *Brain* 97:709. doi:10.1093/brain/97.1.709
- Casali et al. (2013) "A theoretically based index of consciousness independent of sensory processing and behavior", *Sci Transl Med* 5:198ra105. doi:10.1126/scitranslmed.3006294
- Baars (1988) *A Cognitive Theory of Consciousness*, Cambridge University Press.
- Dehaene & Changeux (2011) "Experimental and theoretical approaches to conscious processing", *Neuron* 70:200. doi:10.1016/j.neuron.2011.03.018
- Tononi (2004) "An information integration theory of consciousness", *BMC Neurosci* 5:42. doi:10.1186/1471-2202-5-42
- Tononi, Boly, Massimini & Koch (2016) "Integrated information theory: from consciousness to its physical substrate", *Nat Rev Neurosci* 17:450. doi:10.1038/nrn.2016.44
- Lau & Rosenthal (2011) "Empirical support for higher-order theories of conscious awareness", *Trends Cogn Sci* 15:365. doi:10.1016/j.tics.2011.05.009
- Brown, Lau & LeDoux (2019) "Understanding the higher-order approach to consciousness", *Trends Cogn Sci* 23:754. doi:10.1016/j.tics.2019.06.009
- Lamme (2006) "Towards a true neural stance on consciousness", *Trends Cogn Sci* 10:494. doi:10.1016/j.tics.2006.09.001
- Fleming et al. (2023) "The integrated information theory of consciousness as pseudoscience", PsyArXiv. doi:10.31234/osf.io/zsr78
- Melloni et al. (2023) "An adversarial collaboration protocol for testing contrasting predictions of global neuronal workspace and integrated information theory", *PLoS One* 18:e0268577. doi:10.1371/journal.pone.0268577
- Cogitate Consortium et al. (2025) "Adversarial testing of global neuronal workspace and integrated information theories of consciousness", *Nature* 642:133. doi:10.1038/s41586-025-08888-1
- Butlin et al. (2023) "Consciousness in artificial intelligence: insights from the science of consciousness", arXiv:2308.08708.
