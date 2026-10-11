---
title: Evaluating brain models
category: simulation
tags: [evaluation, benchmark, rsa, brain-score, neural-predictivity, error-consistency, babylm, neurobench, allen-cell-types, scorecard]
use_cases:
  - how do I measure whether my model is brain-like
  - compare a neural network with brain recordings or fMRI
  - which benchmark should a brain-inspired model report
  - what is representational similarity analysis
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.3389/neuro.06.004.2008
  - https://doi.org/10.1016/j.neuron.2020.07.040
  - https://arxiv.org/abs/2407.07530
  - https://doi.org/10.1038/s41467-025-56739-4
---

# Evaluating brain models

## Summary
"Brain-like" is not one number. A model can match the brain at five different
levels: single-cell **mechanism**, internal **representations**, **behaviour**,
**learning efficiency**, and **cost** (energy). Each level has its own data and
metric, and the metrics disagree with each other, so the honest output is a
**scorecard** with one row per level and per dataset, not a single score.

## How it works

### The five levels
| Level | Question | Method | Data / tool |
|---|---|---|---|
| Mechanism | Does a model neuron respond to input the way a recorded neuron does? | Fit parameters to recordings, test on held-out stimuli | Allen Cell Types Database; GLIF models (Teeter et al. 2018) |
| Representation | Do model activations carry the same information as brain activity? | RSA (Kriegeskorte et al. 2008); neural predictivity (linear regression from model units to neurons or voxels) | Brain-Score (Schrimpf et al. 2018, 2020); Algonauts challenges (Cichy et al. 2019; Gifford et al. 2024) |
| Behaviour | Does the model make the *same* mistakes as people, not just as many? | Error consistency (Geirhos et al. 2020) | model-vs-human toolbox (bethgelab) |
| Learning efficiency | Does it learn from a human-sized amount of data? | Fix the data budget, compare scores | BabyLM: language models trained on 100M words or fewer (Hu et al. 2024) |
| Cost | Does it compute as cheaply as the brain? | Energy, operations, activation sparsity, memory footprint | NeuroBench (Yik et al. 2025) |

### Mechanism: fit, then test on held-out stimuli
Teeter et al. (2018) fit five levels of generalised LIF (GLIF) models to mouse
visual-cortex neurons from the Allen Cell Types Database and scored each on how
well it predicted spike times for stimuli it was not fit on. Holding out stimuli is
what makes it an evaluation rather than a curve fit. Brain Lab does the same at a
small scale: `game/eval.py` scores the level 1 LIF neuron against an Allen cell's
measured f-I curve and rheobase.

### Representation: RSA and neural predictivity
**Representational similarity analysis** (Kriegeskorte, Mur & Bandettini 2008)
avoids having to match model units to neurons one by one:
1. Show the model and the brain the same stimuli.
2. For each, build a **representational dissimilarity matrix (RDM)**: entry
   `(i, j)` is how differently stimuli `i` and `j` are represented (e.g.
   `1 − correlation` of the activity patterns).
3. Compare the two RDMs, usually with a rank correlation of their upper triangles.

RDMs from fMRI voxels, spikes, or network layers all have the same shape (stimuli ×
stimuli), so any of them can be compared with any other.

**Neural predictivity** (the core of Brain-Score) instead fits a regularised linear
map from model features to each recorded neuron on some stimuli and reports the
cross-validated correlation on the rest, normalised by how well the neurons predict
themselves across repeats (the noise ceiling).

### Behaviour: error consistency
Two classifiers with 90 % accuracy can get very different images wrong. Geirhos,
Meding & Wichmann (2020) measure **error consistency**: Cohen's kappa on whether
two observers are right or wrong on the same trials, corrected for the agreement
expected from their accuracies alone. Kappa near 0 means the model gets the right
*number* of answers through a different strategy. Klein et al. (2025) show that
kappa estimates from typical trial counts are noisy and give methods for confidence
intervals, so report uncertainty with it.

### Learning efficiency and cost
- BabyLM fixes the training data budget at a scale closer to what a child hears
  than to what large language models see: a 10M-word and a 100M-word text track,
  plus a 100M-word image-and-text track in 2024. Architectures and learning rules
  then compete on sample efficiency (Hu et al. 2024).
- NeuroBench (Yik et al. 2025) defines shared tasks plus cost metrics (footprint,
  activation sparsity, synaptic operations) for algorithms, and energy and
  throughput for neuromorphic hardware. See [[neuromorphic-hardware]].

### Why a scorecard, not one score
Ahlert, Klein, Wichmann & Geirhos (2024) compared many alignment metrics across
vision models: across the 80 Brain-Score models evaluated on all 69 metrics they
considered, the average pairwise correlation between metrics was only 0.198, and
neural and behavioural scores sometimes correlated negatively. A model's "brain-likeness" rank
depends on which metric you pick. Report each level separately and say which data
each row comes from.

## Relevance to building brain-like AI
- Decide up front **which level you claim**. A spiking network on a neuromorphic chip
  makes a cost claim; a predictive-coding vision model makes a representation claim.
  Test the claim you make.
- Always hold out data: stimuli for mechanism and representation, trials for
  behaviour.
- Report the **noise ceiling**. A model at 0.5 correlation with neurons whose repeats
  correlate at 0.6 is doing well; at a ceiling of 0.95 it is not.
- Compare against a baseline that is *not* brain-inspired (a plain CNN or
  transformer) on the same rows; much of the alignment comes from scale and data,
  not brain-like mechanisms (an open question, see below).
- Keep **correctness** and **evidence** apart. A unit test asks "does the code do what
  I designed?"; an evaluation asks "how close is its output to a published
  observation?". Passing the first says nothing about the second.
- Record where each reference curve came from: paper or dataset, figure or cell id,
  units, how it was digitised or transformed, and its license. Keep only small
  redistributable arrays in the repo; download large datasets with a script.

## Code
RSA in numpy: two "models" see the same 20 stimuli. One shares the brain's latent
structure, one is random. The structured model's RDM correlates with the brain's.

```python
import numpy as np

rng = np.random.default_rng(0)
n_stim = 20
latent = rng.normal(size=(n_stim, 5))                      # what the stimuli "are"

def responses(proj, noise):
    return latent @ proj + noise * rng.normal(size=(n_stim, proj.shape[1]))

brain = responses(rng.normal(size=(5, 100)), noise=1.0)   # 100 "voxels"
model_a = responses(rng.normal(size=(5, 64)), noise=1.0)  # different units, same latents
model_b = rng.normal(size=(n_stim, 64))                    # unrelated to the latents

def rdm(x):
    return 1 - np.corrcoef(x)                              # stimuli x stimuli

def rank(v):
    return np.argsort(np.argsort(v))

def spearman(a, b):
    iu = np.triu_indices(n_stim, 1)
    return np.corrcoef(rank(a[iu]), rank(b[iu]))[0, 1]

r_a, r_b = spearman(rdm(brain), rdm(model_a)), spearman(rdm(brain), rdm(model_b))
print(f"RSA brain vs structured model: {r_a:.2f}, vs random model: {r_b:.2f}")
assert r_a > 0.5 and abs(r_b) < 0.3
```

## Open questions
- How much of the alignment between deep networks and the brain comes from
  brain-like mechanisms, and how much from scale, data and task? (open)
- Which metric should win when RSA, predictivity and behaviour disagree? There is no
  agreed answer; Ahlert et al. (2024) argue for reporting several.
- Benchmarks for learning dynamics (how a model's errors change over training,
  compared with children) are still immature.

## Related
- [[levels-of-brain-modeling]] - which level of detail a model sits at decides which rows it can be scored on.
- [[neuromorphic-hardware]] - the cost row in practice.
- [[build-a-brain-like-learner]] - the evaluation plan for the roadmap.
- [[neural-coding-and-computation]] - what the population codes being compared are.
- [[measuring-the-brain-and-open-datasets]] - where the recordings come from and how to load them.
- [[sensory-systems-and-vision]] - the visual hierarchy that Brain-Score models are scored against.

## References
- Kriegeskorte, Mur & Bandettini (2008) "Representational similarity analysis - connecting the branches of systems neuroscience", *Front Syst Neurosci* 2:4. doi:10.3389/neuro.06.004.2008
- Schrimpf et al. (2018) "Brain-Score: Which Artificial Neural Network for Object Recognition is most Brain-Like?", bioRxiv 407007.
- Schrimpf et al. (2020) "Integrative benchmarking to advance neurally mechanistic models of human intelligence", *Neuron* 108:413. doi:10.1016/j.neuron.2020.07.040
- Teeter et al. (2018) "Generalized leaky integrate-and-fire models classify multiple neuron types", *Nat Commun* 9:709. doi:10.1038/s41467-017-02717-4
- Cichy, Roig & Oliva (2019) "The Algonauts Project: A platform for communication between the sciences of biological and artificial intelligence", arXiv:1905.05675.
- Gifford et al. (2024) "The Algonauts Project 2025 Challenge: How the human brain makes sense of multimodal movies", arXiv:2501.00504.
- Geirhos, Meding & Wichmann (2020) "Beyond accuracy: quantifying trial-by-trial behaviour of CNNs and humans by measuring error consistency", NeurIPS. arXiv:2006.16736
- Klein, Meyen, Brendel, Wichmann & Meding (2025) "Quantifying uncertainty in error consistency: towards reliable behavioral comparison of classifiers", arXiv:2507.06645.
- Hu, Mueller, Ross et al. (2024) "Findings of the Second BabyLM Challenge: sample-efficient pretraining on developmentally plausible corpora", arXiv:2412.05149.
- Yik et al. (2025) "The neurobench framework for benchmarking neuromorphic computing algorithms and systems", *Nat Commun* 16:1545. doi:10.1038/s41467-025-56739-4
- Ahlert, Klein, Wichmann & Geirhos (2024) "How aligned are different alignment metrics?", arXiv:2407.07530.
