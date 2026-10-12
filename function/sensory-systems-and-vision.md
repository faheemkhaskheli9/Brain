---
title: Sensory systems - the visual hierarchy and CNNs
category: function
tags: [vision, visual-cortex, v1, ventral-stream, dorsal-stream, receptive-field, gabor, cnn, brain-score, audition, touch, somatotopy]
use_cases:
  - how does the brain turn light into recognised objects
  - what are simple and complex cells in V1
  - why are CNNs called models of the visual cortex and where do they differ from it
  - how do hearing and touch compare to vision
status: stable
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1113/jphysiol.1962.sp006837
  - https://doi.org/10.1093/cercor/1.1.1-a
  - https://doi.org/10.1073/pnas.1403112111
  - https://doi.org/10.1016/j.neuron.2020.07.040
  - https://arxiv.org/abs/1811.12231
---

# Sensory systems - the visual hierarchy and CNNs

## Summary
Vision is the best-mapped sense and the one that inspired convolutional neural
networks. Light is converted in the retina, relayed through the thalamus (LGN) to
primary visual cortex (V1), then processed along a hierarchy of areas that split
into a ventral "what" stream and a dorsal "where/how" stream. CNNs trained on
object recognition predict neural responses along the ventral stream better than
any hand-built model, but they differ from it in telling ways: they are fooled by
imperceptible noise and rely on texture where people rely on shape.

## How it works

### Retina to cortex (established)
- **Retina.** A human retina holds on average about 92 million rods and 4.6
  million cones (Curcio et al. 1990). Its output neurons, retinal ganglion cells,
  number about a million (Curcio & Allen 1990), so the image is compressed roughly a hundredfold
  before it leaves the eye. Ganglion cells have **centre-surround** receptive
  fields: they report local contrast, not raw brightness.
- **LGN** (lateral geniculate nucleus of the thalamus) relays the signal to V1,
  keeping centre-surround fields. Only a small fraction of the synapses onto LGN
  relay cells come from the retina; many come back from cortex (Sherman &
  Guillery 2002), a first sign of the heavy feedback described in
  [[predictive-processing]].
- **V1.** Hubel and Wiesel (1959, 1962) found **simple cells**, which respond to
  an edge or bar at one orientation *and* position, and **complex cells**, which
  respond to the same orientation anywhere in a small region. Nearby cells share
  a preferred orientation (orientation columns), and the map of visual space is
  retinotopic. Simple-cell receptive fields are well described by **Gabor
  filters** (a sine wave under a Gaussian), and sparse coding of natural images
  produces the same filters (Olshausen & Field 1996).

### The hierarchy and two streams (established)
- Felleman and Van Essen (1991) mapped over 30 visual areas in the macaque,
  arranged in a hierarchy whose connections between areas are mostly reciprocal
  (feedforward and feedback). Up the ventral stream (V1 → V2 → V4 → IT), receptive fields grow and the
  preferred features become more complex and more invariant to position and size:
  edges, then contours and textures, then shapes, then objects and faces in
  inferior temporal (IT) cortex.
- **Ventral stream** (to temporal cortex): what an object is. **Dorsal stream**
  (to parietal cortex): where it is and how to act on it. Goodale and Milner
  (1992) framed the split as perception versus action, based partly on patients
  who can grasp objects they cannot recognise, and the reverse. The two streams
  interact a lot; the clean split is a simplification.
- Responses are fast: object category can be read out from IT about 100 ms after
  an image appears (Hung et al. 2005), which leaves little time for many recurrent loops. That is
  one reason feedforward models of the first pass work as well as they do.

### CNNs as models of the ventral stream
- The idea is old: Fukushima's **Neocognitron** (1980) stacked alternating
  simple-like (feature) and complex-like (pooling) layers; HMAX (Riesenhuber &
  Poggio 1999) did the same as a model of the ventral stream. Convolution plus
  pooling is the simple-cell/complex-cell pair repeated.
- **Goal-driven modelling.** Yamins et al. (2014) found that the better a CNN
  was at object recognition, the better its top layers predicted IT neuron
  responses, and intermediate layers predicted V4. Nobody fit the network to
  neural data; training on the task was enough (Yamins & DiCarlo 2016).
- **Brain-Score** (Schrimpf et al. 2018, 2020) turned this into a public
  benchmark: many models scored on predicting V1, V2, V4 and IT responses and
  primate behaviour. A finding from the leaderboard is that ImageNet accuracy and
  brain score correlate, but beyond a point higher accuracy stops buying a better
  brain match. How to score a model: [[evaluating-brain-models]].
- The same recipe works for hearing: a CNN trained to recognise words and music
  genres predicted human auditory cortex responses, with early layers matching
  primary and later layers non-primary auditory cortex (Kell et al. 2018).

### Where CNNs diverge from vision (established findings, debated causes)
- **Adversarial examples.** A change to an image too small for a person to see
  can flip a CNN's label (Szegedy et al. 2014). People are not fooled by these
  perturbations, so the networks are using features humans do not weight.
- **Texture bias.** ImageNet-trained CNNs classify a cat shape filled with
  elephant skin as an elephant; people say cat. Training on style-transferred
  images raised the shape bias and improved robustness (Geirhos et al. 2019).
- **Different errors.** Matching accuracy is not matching behaviour: CNNs and
  people get different individual images wrong (see error consistency in
  [[evaluating-brain-models]]).
- **Missing parts.** Standard CNNs have no feedback, no recurrence within a
  layer, no eye movements and no learning from an unlabelled stream. Which of
  these explains the gaps above is an open question (**hypothesis** territory).

### Hearing and touch (established, brief)
- **Audition.** The cochlea splits sound by frequency along its length, so the
  auditory system is **tonotopic**: neighbouring neurons prefer neighbouring
  frequencies, from the cochlea to primary auditory cortex. Sound passes through
  more brainstem stages than vision before reaching the thalamus (medial
  geniculate nucleus) and cortex, and timing is coded with sub-millisecond
  precision for locating sounds.
- **Touch.** Four classes of mechanoreceptor in the glabrous skin of the hand
  signal different features: slow-adapting types for pressure and skin stretch,
  fast-adapting types for vibration and slip (Johansson & Flanagan 2009). The
  map in primary somatosensory cortex is **somatotopic**, with lips and
  fingertips given far more cortex than the back (Penfield & Boldrey 1937).
- The shared design: topographic maps, receptive fields that grow up a
  hierarchy, and lateral inhibition and normalisation at each stage
  ([[neural-coding-and-computation]]).

## Relevance to building brain-like AI
- Convolution (weight sharing over space) and pooling are borrowed directly from
  V1. They encode the prior that the same feature can appear anywhere.
- **Train on the task, then compare to the brain** is the working method of
  neuro-AI: it does not require fitting to neural data, and the brain match is a
  test, not a training target.
- The divergences are the to-do list. Adding recurrence and feedback, shape bias
  and robustness to small perturbations are concrete ways to make a vision model
  more brain-like, each measurable on Brain-Score-style benchmarks.
- Self-supervised learning from video is closer to how infants learn to see than
  labelled ImageNet; see [[predictive-processing]] and [[build-a-brain-like-learner]].

## Code
A V1 simple cell as a rectified Gabor filter, and a complex cell as the
**energy model**: the summed squares of two Gabors 90° out of phase. Both are
orientation-tuned; only the complex cell ignores where the edge falls (phase).
Max pooling in a CNN plays the same role.

```python
import numpy as np

# V1 simple and complex cells (Hubel & Wiesel) as Gabor filters + the energy model.
n = 32
y, x = np.mgrid[-n // 2:n // 2, -n // 2:n // 2] / n

def gabor(theta, phase, freq=4.0, sigma=0.15):
    u = x * np.cos(theta) + y * np.sin(theta)
    return np.exp(-(x**2 + y**2) / (2 * sigma**2)) * np.cos(2 * np.pi * freq * u + phase)

def grating(theta, phase, freq=4.0):
    return np.cos(2 * np.pi * freq * (x * np.cos(theta) + y * np.sin(theta)) + phase)

def simple(img, theta):           # one receptive field, half-wave rectified
    return max(0.0, float(np.sum(gabor(theta, 0.0) * img)))

def complex_cell(img, theta):     # energy model: sum of squares of a quadrature pair
    even, odd = np.sum(gabor(theta, 0.0) * img), np.sum(gabor(theta, np.pi / 2) * img)
    return float(np.hypot(even, odd))

pref = 0.0
orients = np.linspace(0, np.pi, 8, endpoint=False)
tuning = [complex_cell(grating(t, 0.3), pref) for t in orients]
phases = np.linspace(0, 2 * np.pi, 8, endpoint=False)
s = [simple(grating(pref, p), pref) for p in phases]
c = [complex_cell(grating(pref, p), pref) for p in phases]

print("orientation tuning:", np.round(np.array(tuning) / max(tuning), 2))
print("simple  vs phase:", np.round(np.array(s) / max(s), 2))
print("complex vs phase:", np.round(np.array(c) / max(c), 2))
assert int(np.argmax(tuning)) == 0 and tuning[4] < 0.1 * tuning[0]  # orientation selective
assert min(s) < 0.05 * max(s)                                        # simple: phase sensitive
assert min(c) > 0.95 * max(c)                                        # complex: phase invariant
```

Output: the complex cell falls to 0 for the orthogonal orientation and stays at
1.0 for every phase; the simple cell drops to 0 for half the phases.

## Open questions
- What does feedback in the visual hierarchy compute: prediction, attention,
  recognition of hard images, or all three? (See [[predictive-processing]].)
- Why are CNNs adversarially fragile while brains are not: architecture,
  training data, training objective, or the noise in real neurons?
- Do better brain scores keep coming from bigger models, or has the
  accuracy-to-brain-match link saturated?
- How much of the ventral stream's organisation is learned versus genetically
  set up before visual experience?

## Related
- [[predictive-processing]] - perception as prediction; feedback in the hierarchy.
- [[evaluating-brain-models]] - neural predictivity, Brain-Score and error consistency.
- [[neural-coding-and-computation]] - normalisation and sparse codes used at every stage.
- [[measuring-the-brain-and-open-datasets]] - the recordings these comparisons use.

## References
- Curcio, Sloan, Kalina & Hendrickson (1990) "Human photoreceptor topography", *J Comp Neurol* 292:497. doi:10.1002/cne.902920402
- Curcio & Allen (1990) "Topography of ganglion cells in human retina", *J Comp Neurol* 300:5. doi:10.1002/cne.903000103
- Sherman & Guillery (2002) "The role of the thalamus in the flow of information to the cortex", *Phil Trans R Soc B* 357:1695. doi:10.1098/rstb.2002.1161
- Hung, Kreiman, Poggio & DiCarlo (2005) "Fast readout of object identity from macaque inferior temporal cortex", *Science* 310:863. doi:10.1126/science.1117593
- Hubel & Wiesel (1959) "Receptive fields of single neurones in the cat's striate cortex", *J Physiol* 148:574. doi:10.1113/jphysiol.1959.sp006308
- Hubel & Wiesel (1962) "Receptive fields, binocular interaction and functional architecture in the cat's visual cortex", *J Physiol* 160:106. doi:10.1113/jphysiol.1962.sp006837
- Olshausen & Field (1996) "Emergence of simple-cell receptive field properties by learning a sparse code for natural images", *Nature* 381:607. doi:10.1038/381607a0
- Felleman & Van Essen (1991) "Distributed hierarchical processing in the primate cerebral cortex", *Cereb Cortex* 1:1. doi:10.1093/cercor/1.1.1-a
- Goodale & Milner (1992) "Separate visual pathways for perception and action", *Trends Neurosci* 15:20. doi:10.1016/0166-2236(92)90344-8
- Fukushima (1980) "Neocognitron: a self-organizing neural network model for a mechanism of pattern recognition unaffected by shift in position", *Biol Cybern* 36:193. doi:10.1007/BF00344251
- Riesenhuber & Poggio (1999) "Hierarchical models of object recognition in cortex", *Nat Neurosci* 2:1019. doi:10.1038/14819
- Yamins et al. (2014) "Performance-optimized hierarchical models predict neural responses in higher visual cortex", *PNAS* 111:8619. doi:10.1073/pnas.1403112111
- Yamins & DiCarlo (2016) "Using goal-driven deep learning models to understand sensory cortex", *Nat Neurosci* 19:356. doi:10.1038/nn.4244
- Schrimpf et al. (2018) "Brain-Score: Which Artificial Neural Network for Object Recognition is most Brain-Like?", bioRxiv 407007.
- Schrimpf et al. (2020) "Integrative benchmarking to advance neurally mechanistic models of human intelligence", *Neuron* 108:413. doi:10.1016/j.neuron.2020.07.040
- Kell et al. (2018) "A task-optimized neural network replicates human auditory behavior, predicts brain responses, and reveals a cortical processing hierarchy", *Neuron* 98:630. doi:10.1016/j.neuron.2018.03.044
- Szegedy et al. (2014) "Intriguing properties of neural networks", ICLR. arXiv:1312.6199
- Geirhos et al. (2019) "ImageNet-trained CNNs are biased towards texture; increasing shape bias improves accuracy and robustness", ICLR. arXiv:1811.12231
- Johansson & Flanagan (2009) "Coding and use of tactile signals from the fingertips in object manipulation tasks", *Nat Rev Neurosci* 10:345. doi:10.1038/nrn2621
- Penfield & Boldrey (1937) "Somatic motor and sensory representation in the cerebral cortex of man as studied by electrical stimulation", *Brain* 60:389. doi:10.1093/brain/60.4.389
