---
title: Brain-computer interfaces and neural decoding
category: simulation
tags: [bci, brain-computer-interface, neural-decoding, utah-array, eeg, ecog, kalman-filter, population-vector, speech-neuroprosthesis, deep-brain-stimulation, cochlear-implant, retinal-implant, neuralink, synchron, plasticity]
use_cases:
  - how does a brain-computer interface turn neural activity into cursor movement or speech
  - decode reach velocity from motor cortex neurons with linear regression
  - which BCI recording method should I use, EEG, ECoG or implanted arrays
  - what is the state of brain implant companies like Neuralink and Synchron
  - what do BCIs teach about brain plasticity
status: draft
last_verified: 2026-10-11
sources:
  - doi:10.1038/nature04970
  - doi:10.1162/089976606774841585
  - doi:10.1038/s41586-023-06377-x
  - doi:10.1038/s41586-023-06443-4
  - doi:10.1056/NEJMoa2314132
  - doi:10.1371/journal.pbio.1000153
  - doi:10.1038/nature13665
  - https://neuralink.com/updates/two-years-of-telepathy/
---

# Brain-computer interfaces and neural decoding

## Summary
A brain-computer interface (BCI) records brain activity, decodes an intended
movement, word or choice from it, and drives a cursor, robot arm or speech
synthesiser. The reverse direction, **stimulation**, writes signals in: deep brain
stimulation, cochlear and retinal implants. The decoders are mostly simple (linear
maps, Kalman filters, recurrent networks), and performance is limited above all by
how many neurons are recorded and for how long. BCIs are also a plasticity
experiment: users learn the decoder as the decoder learns them.

## How it works

### Recording: the trade-off is invasiveness against resolution (established)
| Method | Where | Signal | Used for |
|---|---|---|---|
| **EEG** | Scalp | Summed fields of many cortical neurons | P300 spellers (Farwell & Donchin 1988), motor imagery; no surgery, low bandwidth (Wolpaw et al. 2002) |
| **ECoG** | Electrode sheet on the cortex surface | Local field potentials, finer than EEG | Speech decoding (Metzger et al. 2023) |
| **Endovascular** | Stent electrode in a vein over motor cortex | ECoG-like signals | Synchron Stentrode, placed through the jugular vein without opening the skull (Oxley et al. 2021) |
| **Intracortical arrays** | Needles in cortex, e.g. the Utah array (Maynard et al. 1997) | Spikes of single neurons and small groups | Cursor, robot arm and speech BCIs; BrainGate used a 96-microelectrode array (Hochberg et al. 2006) |
| **Neuropixels** | Silicon shank, mostly research | Hundreds of neurons per probe | Animal studies; see [[measuring-the-brain-and-open-datasets]] |

### Decoding movement (established)
- **Population vector.** Motor cortex neurons are cosine-tuned to reach direction;
  summing each neuron's preferred direction weighted by its firing gives the reach
  direction (Georgopoulos, Schwartz & Kettner 1986; [[action-selection-and-motor-control]]).
- **Linear regression.** Fit velocity = W x firing counts on calibration data. The code
  below does this.
- **Kalman filter.** Adds a model of how velocity evolves over time, so each estimate
  combines the new spikes with the previous estimate. It gave more accurate offline
  reconstructions than earlier methods (Wu et al. 2006). ReFIT-KF, which refits the
  filter on what the user intended during closed-loop use, halved target acquisition
  time in monkeys (Gilja et al. 2012).
- **Milestones.** A person with tetraplegia moved a cursor and opened a prosthetic hand
  (Hochberg et al. 2006); monkeys fed themselves with a robot arm (Velliste et al. 2008);
  people reached and grasped with one (Hochberg et al. 2012). Decoding attempted
  handwriting with a recurrent network reached 90 characters per minute at 94.1% raw
  accuracy (Willett et al. 2021).

### Decoding speech (established, single participants)
| Study | Recording | Result |
|---|---|---|
| Willett et al. 2023 | Intracortical arrays, ALS | 62 words/min; 9.1% word error rate on a 50-word vocabulary, 23.8% on 125,000 words |
| Metzger et al. 2023 | ECoG, brainstem stroke | Median 78 words/min text at 25% median word error rate (large vocabulary); also a synthesised voice and a talking avatar |
| Card et al. 2024 | Four arrays, 256 electrodes, ALS | 99.6% accuracy on 50 words on day one; 90.2% on 125,000 words on day two; 97.5% sustained over 8.4 months; about 32 words/min in conversation |

Each is one or two people, so these are case reports, not trial results.

### Stimulation: writing into the nervous system (established)
- **Deep brain stimulation (DBS)** delivers adjustable pulses to deep targets such as
  the subthalamic nucleus for Parkinson's disease and tremor. It works, but which
  targets suit which patients, and exactly how it changes circuit activity, are still
  open (Lozano et al. 2019).
- **Cochlear implants** stimulate the auditory nerve at points along the cochlea, so
  electrode position stands in for sound frequency (Wilson & Dorman 2008). As of
  December 2019 about 736,900 registered devices had been implanted worldwide, per
  the NIDCD fact sheet. Users need months of practice: the brain learns the new code.
- **Retinal implants.** The PRIMA subretinal photovoltaic chip, driven by
  near-infrared light from camera glasses, gave a clinically meaningful acuity gain in
  26 of 32 people with geographic atrophy assessed at 12 months (38 implanted), with
  26 serious adverse events in 19 participants (Holz et al. 2026).

### Implant companies (dated; check the source before reuse)
- **Neuralink**: as of 2026-01-28, 21 participants enrolled in its trials worldwide,
  with an implant of about 1,000 electrodes, per Neuralink's "Two Years of Telepathy"
  update (also reported by Reuters the same day). CBC News reported on 2026-07-02 that
  a Canadian participant with ALS was the 26th person to receive the implant.
- **Synchron** (Stentrode): as of 2024-09-30, its U.S. COMMAND early feasibility study
  met its primary safety endpoint in all six patients over 12 months, per Synchron's
  press release and Clinical Trials Arena (2024-10-01). As of 2026-10-11 Synchron's
  newsroom lists the device as investigational and announces no pivotal-trial start.
- **Precision Neuroscience**: as of 2025-03-30, FDA 510(k) clearance (K242618) for
  Layer 7-T cortical electrodes for temporary use under 30 days, per the FDA 510(k)
  database.
- **Paradromics** (Connexus): FDA approved the Connect-One study on 2025-11-20 (two
  initial participants), and the first study implant at University of Michigan Health
  was announced on 2026-06-17, per Paradromics press releases.

### What BCIs teach about plasticity (supported)
- Monkeys can learn to raise the firing of a single cortical neuron when rewarded
  (Fetz 1969): the brain adapts to whatever readout it is given.
- With a fixed decoder, motor cortex settles into a stable "cortical map" for the
  prosthesis that is recalled across days; a second map can be learned alongside it
  (Ganguly & Carmena 2009).
- Learning is constrained: monkeys quickly learn a new decoder that uses activity
  patterns within the population's existing low-dimensional **intrinsic manifold**,
  but struggle with one that needs patterns outside it (Sadtler et al. 2014;
  [[population-dynamics-and-neural-manifolds]]).
- So a BCI is two learners, the decoder and the brain. How to make them co-adapt
  without chasing each other is an engineering **open question**.

## Relevance to building brain-like AI
- **Decoders are tests of a code.** If a linear readout recovers velocity, the
  information is linearly available in the population, the same test used to score
  brain models ([[evaluating-brain-models]]).
- **Closed loop changes everything.** Offline fits and online control differ because
  the user reacts to the decoder; ReFIT shows that modelling the user's intent is part
  of the decoder.
- **The manifold constraint** suggests that a brain-like learner adapts fastest by
  recombining existing activity patterns, not inventing new ones.
- **Stimulation devices** show that the brain can learn an artificial input code it
  was never built for, as in cochlear implants.

## Code
Simulate 80 cosine-tuned motor neurons with Poisson spikes in 50 ms bins, decode 2D
reach velocity with linear regression, and compare with the population vector.

```python
import numpy as np

rng = np.random.default_rng(0)
N, T, dt = 80, 4000, 0.05                   # neurons, time bins, 50 ms bins

# Smooth 2D reach velocity: a random walk low-pass filtered
v = np.zeros((T, 2))
for t in range(1, T):
    v[t] = 0.9 * v[t - 1] + rng.normal(0, 0.1, 2)

# Cosine tuning: rate = baseline + depth * (velocity . preferred direction)
theta = rng.uniform(0, 2 * np.pi, N)
pd = np.c_[np.cos(theta), np.sin(theta)]    # preferred directions
base = rng.uniform(10, 30, N)               # Hz
depth = rng.uniform(5, 20, N)               # Hz per unit speed
rate = np.clip(base + depth * (v @ pd.T), 0, None)
counts = rng.poisson(rate * dt)             # spike counts per bin


def fit_and_score(X, Y, n_train):
    X1 = np.c_[X, np.ones(len(X))]          # add bias column
    W, *_ = np.linalg.lstsq(X1[:n_train], Y[:n_train], rcond=None)
    pred = X1[n_train:] @ W
    resid = ((Y[n_train:] - pred) ** 2).sum()
    total = ((Y[n_train:] - Y[n_train:].mean(0)) ** 2).sum()
    return 1 - resid / total                # R^2 on held-out bins


split = 3000
r2_all = fit_and_score(counts, v, split)
r2_few = fit_and_score(counts[:, :5], v, split)

# Population vector (Georgopoulos): sum preferred directions weighted by
# each neuron's normalised rate change. Gives direction, not calibrated speed.
z = (counts / dt - base) / depth
pv = z @ pd
cos_pv = np.sum(pv[split:] * v[split:], 1) / (
    np.linalg.norm(pv[split:], axis=1) * np.linalg.norm(v[split:], axis=1) + 1e-9)

print(f"R2 80 neurons {r2_all:.2f}, 5 neurons {r2_few:.2f}, "
      f"population-vector direction cosine {np.median(cos_pv):.2f}")
assert r2_all > 0.3                         # noisy 50 ms bins: about 0.4-0.55
assert r2_few < r2_all - 0.2                # more neurons, better decoding
assert np.median(cos_pv) > 0.5              # population vector points the right way
```

On seeds 0-19, held-out R² was 0.39-0.55 with 80 neurons and about 0 with 5: spike
noise in short bins is why real BCIs need many neurons, smoothing or a Kalman filter.

## Open questions
- **Longevity.** Intracortical recordings degrade over years as tissue reacts to the
  electrodes; how to keep thousands of channels stable for decades is unsolved.
- **Co-adaptation.** How fast should the decoder change so that it helps, rather than
  disrupts, the brain's own learning?
- **Beyond motor cortex.** Can BCIs decode abstract intentions or inner speech
  reliably, and should they? Mental privacy and consent are open questions here.
- **How DBS works.** Whether it jams, drives or retunes circuits is still debated
  (Lozano et al. 2019).
- **Company claims.** Most commercial results are press releases or single-patient
  reports; peer-reviewed trial data are still sparse.

## Related
- [[measuring-the-brain-and-open-datasets]] - EEG, ECoG and Neuropixels in detail, and data to practise decoding on.
- [[action-selection-and-motor-control]] - motor cortex tuning and the population vector.
- [[neural-coding-and-computation]] - population codes that decoders read.
- [[population-dynamics-and-neural-manifolds]] - the intrinsic manifold that limits BCI learning.
- [[learning-and-plasticity]] - the synaptic learning behind adapting to a decoder.
- [[language-and-llms]] - speech areas and the language models used in speech decoders.
- [[sensory-systems-and-vision]] - the visual pathway that retinal implants feed.
- [[evaluating-brain-models]] - linear decodability as a test of a model.
- [[neuroethics]] - consent, mental privacy and the laws that cover neural data.

## References
- Farwell & Donchin (1988) "Talking off the top of your head: toward a mental prosthesis utilizing event-related brain potentials", *Electroencephalogr Clin Neurophysiol* 70:510. doi:10.1016/0013-4694(88)90149-6
- Wolpaw et al. (2002) "Brain-computer interfaces for communication and control", *Clin Neurophysiol* 113:767. doi:10.1016/S1388-2457(02)00057-3
- Maynard, Nordhausen & Normann (1997) "The Utah intracortical electrode array: a recording structure for potential brain-computer interfaces", *Electroencephalogr Clin Neurophysiol* 102:228. doi:10.1016/S0013-4694(96)95176-0
- Georgopoulos, Schwartz & Kettner (1986) "Neuronal population coding of movement direction", *Science* 233:1416. doi:10.1126/science.3749885
- Wu et al. (2006) "Bayesian population decoding of motor cortical activity using a Kalman filter", *Neural Comput* 18:80. doi:10.1162/089976606774841585
- Gilja et al. (2012) "A high-performance neural prosthesis enabled by control algorithm design", *Nat Neurosci* 15:1752. doi:10.1038/nn.3265
- Hochberg et al. (2006) "Neuronal ensemble control of prosthetic devices by a human with tetraplegia", *Nature* 442:164. doi:10.1038/nature04970
- Velliste et al. (2008) "Cortical control of a prosthetic arm for self-feeding", *Nature* 453:1098. doi:10.1038/nature06996
- Hochberg et al. (2012) "Reach and grasp by people with tetraplegia using a neurally controlled robotic arm", *Nature* 485:372. doi:10.1038/nature11076
- Willett et al. (2021) "High-performance brain-to-text communication via handwriting", *Nature* 593:249. doi:10.1038/s41586-021-03506-2
- Willett et al. (2023) "A high-performance speech neuroprosthesis", *Nature* 620:1031. doi:10.1038/s41586-023-06377-x
- Metzger et al. (2023) "A high-performance neuroprosthesis for speech decoding and avatar control", *Nature* 620:1037. doi:10.1038/s41586-023-06443-4
- Card et al. (2024) "An accurate and rapidly calibrating speech neuroprosthesis", *N Engl J Med* 391:609. doi:10.1056/NEJMoa2314132
- Oxley et al. (2021) "Motor neuroprosthesis implanted with neurointerventional surgery improves capacity for activities of daily living tasks in severe paralysis: first in-human experience", *J NeuroInterv Surg* 13:102. doi:10.1136/neurintsurg-2020-016862
- Lozano et al. (2019) "Deep brain stimulation: current challenges and future directions", *Nat Rev Neurol* 15:148. doi:10.1038/s41582-018-0128-2
- Wilson & Dorman (2008) "Cochlear implants: a remarkable past and a brilliant future", *Hear Res* 242:3. doi:10.1016/j.heares.2008.06.005
- NIDCD, "Cochlear implants" fact sheet: https://www.nidcd.nih.gov/health/cochlear-implants
- Holz et al. (2026) "Subretinal photovoltaic implant to restore vision in geographic atrophy due to AMD", *N Engl J Med* 394:232. doi:10.1056/NEJMoa2501396
- Fetz (1969) "Operant conditioning of cortical unit activity", *Science* 163:955. doi:10.1126/science.163.3870.955
- Ganguly & Carmena (2009) "Emergence of a stable cortical map for neuroprosthetic control", *PLoS Biol* 7:e1000153. doi:10.1371/journal.pbio.1000153
- Sadtler et al. (2014) "Neural constraints on learning", *Nature* 512:423. doi:10.1038/nature13665
- Neuralink (2026-01-28) "Two Years of Telepathy": https://neuralink.com/updates/two-years-of-telepathy/
- Reuters (2026-01-28) "Elon Musk's Neuralink says it has 21 participants enrolled in trials": https://www.reuters.com/legal/litigation/elon-musks-neuralink-says-it-has-21-participants-enrolled-trials-2026-01-28/
- CBC News (2026-07-02) Vancouver ALS patient receives Neuralink implant: https://www.cbc.ca/news/canada/british-columbia/vancouver-neuralink-patient-als-vpd-sergeant-9.7253579
- Clinical Trials Arena (2024-10-01) "Synchron's BCI meets primary endpoint in feasibility trial": https://www.clinicaltrialsarena.com/news/synchrons-bci-meets-primary-endpoint-in-feasibility-trial/
- Synchron newsroom: https://synchron.com/news
- FDA 510(k) K242618, Layer 7-T: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K242618
- Paradromics (2025-11-20) Connect-One FDA approval: https://paradromics.com/news/paradromics-receives-fda-approval-for-the-connect-one-clinical-study-with-the-connexus-brain-computer-interface/
- Paradromics (2026-06-17) first Connexus implant: https://paradromics.com/news/paradromics-completes-first-human-brain-computer-interface-bci-implantation/
