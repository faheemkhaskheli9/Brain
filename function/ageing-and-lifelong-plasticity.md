---
title: Ageing and lifelong plasticity
category: function
tags: [ageing, plasticity, cognitive-reserve, fluid-intelligence, crystallised-intelligence, adult-neurogenesis, exercise, critical-period, loss-of-plasticity, continual-learning]
use_cases:
  - how does learning and memory change as the brain ages
  - why does fluid intelligence fall while vocabulary keeps growing
  - do adults grow new neurons
  - can a critical period be reopened in an adult brain
  - why do neural networks lose the ability to learn in continual training and how to fix it
status: draft
last_verified: 2026-10-12
sources:
  - https://doi.org/10.1038/nrn1809
  - https://doi.org/10.1177/0956797614567339
  - https://doi.org/10.1073/pnas.1015950108
  - https://doi.org/10.1126/science.1150516
  - https://doi.org/10.1038/s41586-024-07711-7
---

# Ageing and lifelong plasticity

## Summary
The adult brain keeps learning all its life, but what it is good at shifts. Speed
of processing and fluid reasoning peak early and decline, while vocabulary and
knowledge keep growing into late middle age. Normal ageing loses few neurons; it
mostly changes synapses, white matter and the regions that matter most for memory
and control (hippocampus, prefrontal cortex). Some plasticity can be raised again
in adults by exercise, enrichment and, in animals, by drugs that reopen critical
periods. Deep networks have their own version of ageing: under long continual
training they lose the ability to learn new tasks (Dohare et al. 2024), and the
fixes look like the brain's: keep some units young.

## How it works

### Which abilities change, and when (established)
- **Fluid vs crystallised.** Horn & Cattell (1967) split intelligence into
  *fluid* (reasoning on new problems) and *crystallised* (accumulated knowledge).
  Fluid scores fall with age; crystallised scores hold or rise.
- **Different abilities peak at different ages.** Across large online and
  standardised samples, processing speed peaked around age 18-19, short-term
  memory for faces in the early 30s, and vocabulary in the late 60s or early 70s
  (Hartshorne & Germine 2015).
- **Processing speed** is one strong common factor: slower processing explains a
  large share of age differences on many other tasks (Salthouse 1996). Some
  decline in reasoning and speed is already measurable in healthy adults in their
  20s and 30s (Salthouse 2009); when decline "begins" depends on the design
  (cross-sectional vs longitudinal), which is still argued.

### What changes in the brain (established)
- **Few neurons are lost in normal ageing**; the changes are in dendrites,
  spines, synapses and their plasticity (Morrison & Hof 1997; Burke & Barnes
  2006). Neuron death on a large scale is a sign of disease, not of normal ageing
  ([[brain-disorders-and-computational-psychiatry]]).
- **Region by region.** Volume loss is greatest in prefrontal cortex and the
  hippocampus and smallest in primary sensory cortex (Raz et al. 2005).
- **Weaker long-term potentiation.** In aged rodents LTP is harder to induce and
  decays faster, and place-cell maps are less stable (Burke & Barnes 2006).
- **Sleep.** Slow-wave sleep and sleep spindles decline with age, and the loss
  of slow-wave sleep is linked to worse overnight memory consolidation (Mander,
  Winer & Walker 2017; see [[sleep-and-memory-consolidation]]).

### Adult neurogenesis (disputed)
Rodents make new hippocampal neurons throughout life, more with running
(van Praag et al. 1999) and enriched environments (Kempermann et al. 1997).
In humans the evidence conflicts: Sorrells et al. (2018) found neurogenesis falls
to undetectable levels in adults, while Boldrini et al. (2018) and
Moreno-Jiménez et al. (2019) report it into old age. Tissue handling and
markers differ between the studies. Treat any claim about adult human
neurogenesis as **unsettled**.

### Cognitive reserve and what protects it
- **Cognitive reserve** (Stern 2002) names an observation: people with more
  education or more demanding lives show fewer symptoms for the same amount of
  brain pathology. That the observation is real is established; *how* reserve
  works (more efficient networks, compensation by other regions) is a
  **hypothesis**, with the scaffolding theory one account (Park & Reuter-Lorenz
  2009).
- **Exercise.** In a randomised trial of 120 older adults, a year of aerobic
  walking increased hippocampal volume by about 2%, while the stretching control
  group lost about 1.4% (Erickson et al. 2011).

### Reopening critical periods (animal studies; human evidence thin)
Critical periods close partly through molecular brakes such as perineuronal nets
([[brain-development-and-critical-periods]]). In adult animals they have been
partly reopened:
- dissolving perineuronal nets restored ocular-dominance plasticity in adult rats
  (Pizzorusso et al. 2002);
- the antidepressant fluoxetine restored it in adult rats (Maya Vetencourt et al.
  2008);
- MDMA reopened a critical period for social reward learning in adult mice
  (Nardou et al. 2019).

In humans, one small trial reported that valproate improved adult learning of
absolute pitch (Gervain et al. 2013); this has not been replicated at scale.
Whether reopening is safe in humans, and what stability it costs, is open.

## Relevance to building brain-like AI
| Brain | AI component |
|---|---|
| Fluid declines, crystallised grows | A system that stops learning new skills can still keep improving its stored knowledge (retrieval, a growing memory store) |
| Weaker LTP, slower learning with age | **Loss of plasticity**: networks trained on a long sequence of tasks learn new ones worse than a fresh network (Dohare et al. 2024; Lyle et al. 2023) |
| Adult neurogenesis (if real, in hippocampus) | Re-initialising unused units: continual backprop (Dohare et al. 2024), ReDo for dormant neurons (Sokar et al. 2023) |
| Brakes on plasticity, reopened by drugs | Shrink-and-perturb: scale weights down and add noise before each new task (Ash & Adams 2020); learning-rate warm restarts |
| Cognitive reserve | Over-provisioned capacity that degrades gracefully when parts fail |
| Less slow-wave sleep, worse consolidation | Offline replay as a resource that can run short ([[memory-systems]]) |

The mapping in the right column is an analogy, not a claim that the mechanisms
are the same. In networks the measured causes of plasticity loss include
growing weights, saturated or dead units and lost feature diversity (Dohare et
al. 2024; Lyle et al. 2023); the brain's causes are listed above.

## Code: a network that ages, and a refresh that keeps it young

A small tanh network gets 150 tasks in a row, each a fresh random labelling of
the same 128 inputs, with the same practice budget per task. At first it learns
every task fully; by the end it learns only about two thirds, because its weights
have grown and its units saturate. Shrinking the weights and adding noise before
each task (Ash & Adams 2020) keeps it learning. Settings are illustrative.

```python
import numpy as np

def lifetime(refresh, seed=0, tasks=150, steps=100, n=128, d=16, H=16, lr=10.0):
    rng = np.random.default_rng(seed)
    X = rng.normal(0, 1, (n, d))                             # the same inputs all life
    new = lambda: (rng.normal(0, d ** -0.5, (d, H)), rng.normal(0, H ** -0.5, H))
    W1, w2 = new()
    acc = []
    for t in range(tasks):
        y = rng.choice([-1.0, 1.0], n)                       # a new task: fresh random labels
        if refresh:                                          # shrink and perturb (Ash & Adams 2020)
            R1, r2 = new()
            W1, w2 = 0.5 * W1 + 0.5 * R1, 0.5 * w2 + 0.5 * r2
        for _ in range(steps):                               # a fixed practice budget per task
            h = np.tanh(X @ W1)
            p = h @ w2
            g = -y / (1 + np.exp(np.clip(y * p, -50, 50)))   # logistic-loss gradient
            dh = np.outer(g, w2) * (1 - h ** 2)
            w2 -= lr * h.T @ g / n
            W1 -= lr * X.T @ dh / n
        acc.append(np.mean(np.sign(p) == y))
    return np.mean(acc[:10]), np.mean(acc[-10:]), np.abs(W1).mean()

young, old, w = lifetime(refresh=False)
_, old_r, w_r = lifetime(refresh=True)
print(f"plain:   tasks 1-10 {young:.2f}, tasks 141-150 {old:.2f}, mean |weight| {w:.2f}")
print(f"refresh: tasks 141-150 {old_r:.2f}, mean |weight| {w_r:.2f}")
assert young > 0.95 and old < 0.8                            # same budget, much less learned
assert old_r > 0.95 and w > 3 * w_r                          # big weights saturate tanh; refresh keeps them small
```

On seeds 0-7 the plain network ends at 0.65-0.69 accuracy and the refreshed one
at 1.00.

## Open questions
- Whether adults grow new hippocampal neurons, and if so whether they matter for
  memory.
- What cognitive reserve is made of, and whether it can be built late in life.
- Which plasticity brakes can be released safely in adult humans.
- Whether loss of plasticity in networks and in ageing brains share a cause, or
  only a symptom.

## Related
- [[brain-development-and-critical-periods]] - how plasticity is scheduled early in life.
- [[learning-and-plasticity]] - LTP and the rules whose strength changes with age.
- [[sleep-and-memory-consolidation]] - the slow-wave sleep that ageing erodes.
- [[memory-systems]] - stability versus plasticity and replay.
- [[brain-disorders-and-computational-psychiatry]] - where normal ageing ends and Alzheimer's begins.

## References
- Horn & Cattell (1967) "Age differences in fluid and crystallized intelligence", *Acta Psychol* 26:107. doi:10.1016/0001-6918(67)90011-X
- Hartshorne & Germine (2015) "When does cognitive functioning peak? The asynchronous rise and fall of different cognitive abilities across the life span", *Psychol Sci* 26:433. doi:10.1177/0956797614567339
- Salthouse (1996) "The processing-speed theory of adult age differences in cognition", *Psychol Rev* 103:403. doi:10.1037/0033-295X.103.3.403
- Salthouse (2009) "When does age-related cognitive decline begin?", *Neurobiol Aging* 30:507. doi:10.1016/j.neurobiolaging.2008.09.023
- Morrison & Hof (1997) "Life and death of neurons in the aging brain", *Science* 278:412. doi:10.1126/science.278.5337.412
- Burke & Barnes (2006) "Neural plasticity in the ageing brain", *Nat Rev Neurosci* 7:30. doi:10.1038/nrn1809
- Raz et al. (2005) "Regional brain changes in aging healthy adults: general trends, individual differences and modifiers", *Cereb Cortex* 15:1676. doi:10.1093/cercor/bhi044
- Mander, Winer & Walker (2017) "Sleep and human aging", *Neuron* 94:19. doi:10.1016/j.neuron.2017.02.004
- Kempermann, Kuhn & Gage (1997) "More hippocampal neurons in adult mice living in an enriched environment", *Nature* 386:493. doi:10.1038/386493a0
- van Praag, Kempermann & Gage (1999) "Running increases cell proliferation and neurogenesis in the adult mouse dentate gyrus", *Nat Neurosci* 2:266. doi:10.1038/6368
- Sorrells et al. (2018) "Human hippocampal neurogenesis drops sharply in children to undetectable levels in adults", *Nature* 555:377. doi:10.1038/nature25975
- Boldrini et al. (2018) "Human hippocampal neurogenesis persists throughout aging", *Cell Stem Cell* 22:589. doi:10.1016/j.stem.2018.03.015
- Moreno-Jiménez et al. (2019) "Adult hippocampal neurogenesis is abundant in neurologically healthy subjects and drops sharply in patients with Alzheimer's disease", *Nat Med* 25:554. doi:10.1038/s41591-019-0375-9
- Stern (2002) "What is cognitive reserve? Theory and research application of the reserve concept", *J Int Neuropsychol Soc* 8:448. doi:10.1017/S1355617702813248
- Park & Reuter-Lorenz (2009) "The adaptive brain: aging and neurocognitive scaffolding", *Annu Rev Psychol* 60:173. doi:10.1146/annurev.psych.59.103006.093656
- Erickson et al. (2011) "Exercise training increases size of hippocampus and improves memory", *PNAS* 108:3017. doi:10.1073/pnas.1015950108
- Pizzorusso et al. (2002) "Reactivation of ocular dominance plasticity in the adult visual cortex", *Science* 298:1248. doi:10.1126/science.1072699
- Maya Vetencourt et al. (2008) "The antidepressant fluoxetine restores plasticity in the adult visual cortex", *Science* 320:385. doi:10.1126/science.1150516
- Nardou et al. (2019) "Oxytocin-dependent reopening of a social reward learning critical period with MDMA", *Nature* 569:116. doi:10.1038/s41586-019-1075-9
- Gervain et al. (2013) "Valproate reopens critical-period learning of absolute pitch", *Front Syst Neurosci* 7:102. doi:10.3389/fnsys.2013.00102
- Dohare et al. (2024) "Loss of plasticity in deep continual learning", *Nature* 632:768. doi:10.1038/s41586-024-07711-7
- Lyle et al. (2023) "Understanding plasticity in neural networks", ICML. doi:10.48550/arXiv.2303.01486
- Sokar, Agarwal, Castro & Evci (2023) "The dormant neuron phenomenon in deep reinforcement learning", ICML. doi:10.48550/arXiv.2302.12902
- Ash & Adams (2020) "On warm-starting neural network training", NeurIPS. doi:10.48550/arXiv.1910.08475
