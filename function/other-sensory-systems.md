---
title: Other senses - hearing, touch, smell and pain
category: function
tags: [audition, cochlea, tonotopy, sound-localisation, jeffress, itd, touch, proprioception, somatotopy, homunculus, body-schema, olfaction, mushroom-body, flyhash, locality-sensitive-hashing, pain, nociception, gate-control, placebo]
use_cases:
  - how does the cochlea analyse sound and how do we locate sounds
  - what is the Jeffress model of interaural time differences
  - what is somatotopy, the homunculus and the body schema
  - how does the fly olfactory circuit work and what is FlyHash
  - use a brain-inspired hash for nearest-neighbour similarity search
  - how does the brain modulate pain (gate control, placebo)
status: draft
last_verified: 2026-10-11
sources:
  - https://www.nobelprize.org/prizes/medicine/1961/summary/
  - https://doi.org/10.1152/physrev.00026.2009
  - https://doi.org/10.1152/physrev.00048.2011
  - https://doi.org/10.1126/science.aam9868
  - https://doi.org/10.1126/science.150.3699.971
---

# Other senses - hearing, touch, smell and pain

## Summary
Vision gets most of the attention ([[sensory-systems-and-vision]]), but the other
senses show computational tricks that vision does not. The **cochlea** is a mechanical
frequency analyser, and sound localisation computes microsecond time differences
between the ears. **Touch and proprioception** build maps of the body that can be
remapped and even fooled. The fly's **olfactory circuit** is a random sparse
expansion followed by winner-take-all, which turned out to be a better
locality-sensitive hash (**FlyHash**). **Pain** is not a raw signal: the spinal cord
and brain gate and modulate it from the top down.

## How it works

### Hearing (established)
- **Cochlea as a frequency analyser.** Sound sets up a travelling wave on the basilar
  membrane whose peak sits at a place set by frequency: high frequencies near the
  base, low near the apex (von Békésy, Nobel Prize 1961). Outer hair cells change
  length when stimulated (Brownell et al. 1985), actively amplifying the motion.
  The result is a bank of overlapping band-pass filters, and the **tonotopic** map
  is kept from cochlea to primary auditory cortex.
- **Two cues for direction.** Low-frequency sounds are located mainly by the
  **interaural time difference (ITD)**, high-frequency sounds by the **interaural
  level difference**, since the head shadows high frequencies (Grothe, Pecka &
  McAlpine 2010).
- **Jeffress model (1948).** Axons from the two ears act as **delay lines** feeding a
  row of **coincidence detectors**; each detector fires most when its internal delay
  cancels the external ITD, so position along the row is a place map of direction.
  The barn owl's nucleus laminaris matches this design (Carr & Konishi 1990).
- **Mammals differ (supported, debated).** In the gerbil medial superior olive,
  precisely timed inhibition shifts ITD tuning, and the best delays of most neurons
  lie outside the natural range (Brand et al. 2002). Grothe et al. (2010) argue that
  mammals code ITD by the relative firing **rate** of two broadly tuned channels,
  one per hemisphere, rather than a Jeffress place map.

### Touch and proprioception (established)
- **Somatotopy.** Primary somatosensory cortex (postcentral gyrus) holds an ordered
  map of the body; electrical stimulation in patients produced the "homunculus", in
  which lips, tongue and hands get far more cortex than the trunk (Penfield &
  Boldrey 1937). The map is plastic in adults: after a digit was amputated in
  monkeys, neighbouring digits took over its cortex (Merzenich et al. 1984).
- **Proprioception** is the sense of limb position, movement and force. Muscle
  spindles signal muscle length and its rate of change, Golgi tendon organs signal
  force, and skin and joint receptors contribute (Proske & Gandevia 2012).
- **Body schema (supported).** The brain's model of where the body is can be
  rewritten by multisensory input: when a visible rubber hand and a hidden real hand
  are stroked in synchrony, people feel the touch on the rubber hand (Botvinick &
  Cohen 1998). That body ownership is an inference from coincident vision, touch and
  proprioception is the leading **hypothesis**.

### Smell: the fly olfactory circuit (established circuit, algorithmic reading supported)
- Odorants bind a large family of odorant receptor proteins (Buck & Axel 1991, Nobel
  Prize 2004), so an odour is a combinatorial pattern across receptor types.
- In *Drosophila*, receptor neurons converge onto glomeruli of the antennal lobe;
  projection neurons carry the ~50-glomerulus pattern to about 2000 **Kenyon cells**
  in the mushroom body, each sampling about six glomeruli (Dasgupta et al. 2017).
  Which glomeruli each Kenyon cell samples looks **random**, with no detectable
  structure (Caron et al. 2013).
- A single inhibitory neuron (APL) gets input from Kenyon cells and inhibits them
  all. This feedback keeps the Kenyon cell code sparse and decorrelated; blocking it
  made flies unable to learn to tell similar odours apart (Lin et al. 2014).
- **FlyHash.** Dasgupta, Stevens & Navlakha (2017) read the circuit as a
  locality-sensitive hash in three steps: equalise the mean of the input, a sparse
  binary random projection with a 40-fold expansion (50 to 2000), and a
  winner-take-all that keeps the top-firing 5% of Kenyon cells as the odour's tag.
  Classic LSH instead uses a dense random projection that *reduces* dimension.
  Similar odours get overlapping tags, so learning about one odour generalises to
  similar ones. The fly version improved similarity search on standard benchmark
  datasets compared with classic LSH.

### Pain (established, with a revised theory)
- **Nociceptors** are free nerve endings that respond to damaging heat, pressure or
  chemicals. TRPV1, the capsaicin receptor, is a heat-activated ion channel on them
  (Caterina et al. 1997). People with loss-of-function mutations in *SCN9A*, which
  encodes a sodium channel in nociceptors, cannot feel pain (Cox et al. 2006).
- **Gate control theory** (Melzack & Wall 1965): large-fibre touch input inhibits
  transmission of small-fibre pain input in the spinal dorsal horn, which is why
  rubbing a knock helps. The specific circuit they drew has been revised, but the
  core claim, that pain is modulated at its first relay, is **supported**.
- **Top-down modulation (established).** A descending pathway from the
  periaqueductal grey through the rostral ventromedial medulla to the dorsal horn,
  using endogenous opioids, can suppress pain (Basbaum & Fields 1984). Placebo
  analgesia is partly blocked by the opioid antagonist naloxone (Levine, Gordon &
  Fields 1978), and placebos reduce pain-evoked activity in thalamus, insula and
  anterior cingulate (Wager et al. 2004).
- **Pain as inference (hypothesis).** Büchel et al. (2014) cast placebo analgesia in
  predictive-coding terms: experienced pain combines nociceptive input with a prior
  expectation, weighted by their precision ([[predictive-processing]]).

## Relevance to building brain-like AI
- **Front ends.** Mel spectrograms and gammatone filterbanks are engineered cochleas;
  audio networks trained on them predict auditory cortex responses (Kell et al.
  2018, in [[sensory-systems-and-vision]]).
- **Delay lines + coincidence detection** is a cheap, spike-native way to compute
  time differences, and maps directly onto spiking hardware
  ([[spiking-neural-networks]]).
- **Random expansion + sparsity** (FlyHash) gives similarity-preserving binary codes
  without training, useful for nearest-neighbour search and as a fixed first layer
  for fast associative learning ([[efficient-brain-like-learning]]).
- **Body models and pain** argue for an agent that predicts its own body state and
  treats damage signals as inputs to be weighted by context, not fixed costs.

## Code
FlyHash against a dense random projection at the same hash length `k`: 2000 noisy
odour-like vectors, recall of each query's true 2% nearest neighbours.

```python
import numpy as np

rng = np.random.default_rng(0)

# "Odours": 2000 nonnegative 50-d vectors (one value per glomerulus) in 40 noisy clusters.
d, n, n_q, k = 50, 2000, 100, 16          # k = hash length: bits for LSH, active units for the fly
centres = rng.gamma(2.0, 1.0, (40, d))
X = centres[rng.integers(0, 40, n)] * rng.lognormal(0, 0.6, (n, d))
X = X - X.mean(axis=1, keepdims=True)    # fly step 1: equalise mean activity per odour

queries = rng.choice(n, n_q, replace=False)
n_nn = n // 50                            # true neighbours = closest 2% in input space

def recall(dist_fn):
    hits = 0
    for i in queries:
        true = np.linalg.norm(X - X[i], axis=1)
        true[i] = np.inf
        dist = dist_fn(i).astype(float) + 1e-9 * rng.random(n)   # random tie-break
        dist[i] = np.inf
        hits += len(set(np.argsort(true)[:n_nn]) & set(np.argsort(dist)[:n_nn]))
    return hits / (n_q * n_nn)

# Dense random projection: k Gaussian directions. Classic LSH keeps the sign (k bits);
# keeping the k real values is shown for comparison.
P = rng.normal(size=(d, k))
Y = X @ P
dense_real = recall(lambda i: np.linalg.norm(Y - Y[i], axis=1))
B = Y > 0
dense_bits = recall(lambda i: (B != B[i]).sum(axis=1))

# FlyHash: sparse binary expansion to m = 20k Kenyon-cell-like units, each summing
# 6 random inputs, then winner-take-all keeps the top k (the APL neuron's job).
m = 20 * k
M = np.zeros((d, m))
for j in range(m):
    M[rng.choice(d, 6, replace=False), j] = 1.0
A = X @ M
H = np.zeros(A.shape, dtype=bool)
H[np.arange(n)[:, None], np.argsort(-A, axis=1)[:, :k]] = True
fly = recall(lambda i: -(H & H[i]).sum(axis=1))           # more shared active units = closer

print(f"recall of true 2% neighbours, k={k}: dense sign-LSH {dense_bits:.2f}, "
      f"dense real-valued {dense_real:.2f}, FlyHash {fly:.2f}")
assert H.sum(axis=1).max() == k == H.sum(axis=1).min()     # exactly k active units per odour
assert fly > dense_bits + 0.1                              # beats dense LSH at equal hash length
```

On this synthetic data FlyHash roughly doubles the recall of sign-based LSH with the
same `k`, and about matches keeping `k` real-valued projections, using only binary
units with no multiplications in the projection. The fly tag lives in a larger
space (16 active of 320 units), so "same hash length" is not "same bits"; how to
compare the two fairly is part of the debate around the method.

## Open questions
- Whether mammals use a Jeffress-like place code for ITD anywhere, or only the
  two-channel rate code.
- How the brain builds and updates the body schema, and why phantom limbs persist.
- Whether the random Kenyon cell wiring is truly random or tuned in ways not yet
  detected, and how much of FlyHash's advantage holds on real-world data.
- How far pain can be explained as inference, and why chronic pain persists after
  tissue heals.

## Related
- [[sensory-systems-and-vision]] - vision, and the short overview of hearing and touch this file extends.
- [[neural-coding-and-computation]] - temporal codes, sparse codes and winner-take-all used here.
- [[predictive-processing]] - pain and body ownership as inference.
- [[emotion-amygdala-and-interoception]] - interoception, the inward-facing sense, and the insula.
- [[efficient-brain-like-learning]] - sparse codes for cheap learning.
- [[spiking-neural-networks]] - coincidence detection in spiking models.
- [[comparative-and-evolutionary-neuroscience]] - the fly brain as a model system.

## References
- Nobel Prize in Physiology or Medicine 1961, Georg von Békésy. https://www.nobelprize.org/prizes/medicine/1961/summary/
- Brownell, Bader, Bertrand & de Ribaupierre (1985) "Evoked mechanical responses of isolated cochlear outer hair cells", *Science* 227:194. doi:10.1126/science.3966153
- Jeffress (1948) "A place theory of sound localization", *J Comp Physiol Psychol* 41:35. doi:10.1037/h0061495
- Carr & Konishi (1990) "A circuit for detection of interaural time differences in the brain stem of the barn owl", *J Neurosci* 10:3227. doi:10.1523/JNEUROSCI.10-10-03227.1990
- Brand, Behrend, Marquardt, McAlpine & Grothe (2002) "Precise inhibition is essential for microsecond interaural time difference coding", *Nature* 417:543. doi:10.1038/417543a
- Grothe, Pecka & McAlpine (2010) "Mechanisms of sound localization in mammals", *Physiol Rev* 90:983. doi:10.1152/physrev.00026.2009
- Penfield & Boldrey (1937) "Somatic motor and sensory representation in the cerebral cortex of man as studied by electrical stimulation", *Brain* 60:389. doi:10.1093/brain/60.4.389
- Merzenich et al. (1984) "Somatosensory cortical map changes following digit amputation in adult monkeys", *J Comp Neurol* 224:591. doi:10.1002/cne.902240408
- Proske & Gandevia (2012) "The proprioceptive senses: their roles in signaling body shape, body position and movement, and muscle force", *Physiol Rev* 92:1651. doi:10.1152/physrev.00048.2011
- Botvinick & Cohen (1998) "Rubber hands 'feel' touch that eyes see", *Nature* 391:756. doi:10.1038/35784
- Buck & Axel (1991) "A novel multigene family may encode odorant receptors: a molecular basis for odor recognition", *Cell* 65:175. doi:10.1016/0092-8674(91)90418-X
- Caron, Ruta, Abbott & Axel (2013) "Random convergence of olfactory inputs in the *Drosophila* mushroom body", *Nature* 497:113. doi:10.1038/nature12063
- Lin et al. (2014) "Sparse, decorrelated odor coding in the mushroom body enhances learned odor discrimination", *Nat Neurosci* 17:559. doi:10.1038/nn.3660
- Dasgupta, Stevens & Navlakha (2017) "A neural algorithm for a fundamental computing problem", *Science* 358:793. doi:10.1126/science.aam9868
- Caterina et al. (1997) "The capsaicin receptor: a heat-activated ion channel in the pain pathway", *Nature* 389:816. doi:10.1038/39807
- Cox et al. (2006) "An SCN9A channelopathy causes congenital inability to experience pain", *Nature* 444:894. doi:10.1038/nature05413
- Melzack & Wall (1965) "Pain mechanisms: a new theory", *Science* 150:971. doi:10.1126/science.150.3699.971
- Basbaum & Fields (1984) "Endogenous pain control systems: brainstem spinal pathways and endorphin circuitry", *Annu Rev Neurosci* 7:309. doi:10.1146/annurev.ne.07.030184.001521
- Levine, Gordon & Fields (1978) "The mechanism of placebo analgesia", *Lancet* 312:654. doi:10.1016/S0140-6736(78)92762-9
- Wager et al. (2004) "Placebo-induced changes in fMRI in the anticipation and experience of pain", *Science* 303:1162. doi:10.1126/science.1093065
- Büchel, Geuter, Sprenger & Eippert (2014) "Placebo analgesia: a predictive coding perspective", *Neuron* 81:1223. doi:10.1016/j.neuron.2014.02.042
- Kell et al. (2018) "A task-optimized neural network replicates human auditory behavior, predicts brain responses, and reveals a cortical processing hierarchy", *Neuron* 98:630. doi:10.1016/j.neuron.2018.03.044
