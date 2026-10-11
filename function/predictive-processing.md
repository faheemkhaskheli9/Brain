---
title: Perception and predictive processing
category: function
tags: [predictive-coding, free-energy, active-inference, bayesian-brain, visual-cortex, perception, attention, world-model]
use_cases:
  - how does the brain perceive the world
  - what is predictive coding and the free-energy principle
  - how can an AI learn a world model the way the brain might
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1038/4580
  - https://doi.org/10.1038/nrn2787
  - https://doi.org/10.1017/S0140525X12000477
---

# Perception and predictive processing

## Summary
Perception is not a passive camera feed. A leading theory, **predictive
processing**, says the cortex constantly *predicts* its sensory input from an
internal model of the world. Higher areas send predictions down; lower areas send
up only the **prediction error** (what was not expected). Learning means
adjusting the model to reduce future errors, which is self-supervised learning on
the sensory stream. This is a strong and influential **hypothesis**, with
supporting evidence, not settled fact.

## How it works

### Established facts about perception
- **Visual hierarchy.** Retina → thalamus (LGN) → V1 (edges) → V2 (textures,
  contours) → V4 (shapes, colour) → IT (objects, faces). Receptive fields grow
  and features get more abstract up the hierarchy. A trained CNN's layers match
  this progression surprisingly well (Yamins & DiCarlo 2016).
- **Two streams.** Ventral "what" (object identity) and dorsal "where/how"
  (location, action guidance).
- **Massive feedback.** Top-down connections are as numerous as bottom-up ones.
  Context strongly changes what we see (illusions, filling in the blind spot).
- **Attention** boosts the gain of relevant neurons and suppresses others. It is
  controlled by frontal and parietal areas and the thalamus.
- **Multisensory integration** weights each sense by its reliability, close to
  Bayes-optimal in many experiments (Ernst & Banks 2002).

### Predictive coding (Rao & Ballard 1999)
Each level `l` holds a representation `r_l` and predicts the level below:
`prediction = f(W_l · r_l)`, `error ε_{l-1} = r_{l-1} − prediction`.
- Inference: adjust `r_l` to reduce errors at the level below and its own error.
- Learning: adjust `W_l` by a **local Hebbian** product, `ΔW ∝ ε_{l-1} · r_lᵀ`.
- Only errors are passed up. Expected input gets "explained away", which accounts
  for effects like extra-classical receptive fields and repetition suppression.

Code: [[brain-inspired-learning-algorithms]].

### Free-energy principle and active inference (Friston)
A broader framework. Organisms minimise *variational free energy*, an upper bound
on sensory surprise, in two ways:
1. **Perception**: update beliefs to match the senses (predictive coding).
2. **Action**: change the world so the senses match predictions (active inference).
Attention is then precision-weighting of errors (how much to trust each error
signal). This framework is mathematically general and hard to falsify as a whole;
specific process models can be tested.

### Evidence and debate
- For: mismatch negativity (an EEG response to unexpected sounds), suppressed
  responses to predicted stimuli, layer-specific feedforward and feedback pathways
  that fit error and prediction units.
- Against or unresolved: distinct "error neurons" have not been clearly identified
  in all areas; some prediction-related results also fit alternative models.

## Relevance to building brain-like AI
- **Self-supervised prediction is how the brain gets most of its training
  signal.** Next-token prediction in LLMs, masked autoencoding and JEPA-style
  latent prediction (LeCun 2022) are engineering cousins of this idea.
- Predictive coding networks learn with **local rules**. Under some conditions
  they approximate backprop (Whittington & Bogacz 2017), which makes them a
  candidate for brain-plausible deep learning ([[brain-vs-deep-learning]]).
- Active inference gives a single objective for perception, action and curiosity
  (seeking information that reduces uncertainty). See [[build-a-brain-like-learner]].

## Related
- [[sensory-systems-and-vision]] - the visual hierarchy in detail, and CNNs as models of it.
- [[neural-coding-and-computation]] - normalisation, gain and attention primitives.
- [[brain-inspired-learning-algorithms]] - a runnable predictive coding network.
- [[emotion-amygdala-and-interoception]] - interoceptive inference: the same scheme applied to the body.
- [[brain-vs-deep-learning]] - predictive coding as a backprop alternative.

## References
- Rao & Ballard (1999) "Predictive coding in the visual cortex", *Nature Neuroscience* 2:79. doi:10.1038/4580
- Friston (2010) "The free-energy principle: a unified brain theory?", *Nat Rev Neurosci* 11:127. doi:10.1038/nrn2787
- Clark (2013) "Whatever next? Predictive brains, situated agents, and the future of cognitive science", *Behav Brain Sci* 36:181. doi:10.1017/S0140525X12000477
- Yamins & DiCarlo (2016) "Using goal-driven deep learning models to understand sensory cortex", *Nat Neurosci* 19:356.
- Whittington & Bogacz (2017) "An approximation of the error backpropagation algorithm in a predictive coding network with local Hebbian synaptic plasticity", *Neural Computation* 29:1229.
- LeCun (2022) "A Path Towards Autonomous Machine Intelligence", OpenReview.
