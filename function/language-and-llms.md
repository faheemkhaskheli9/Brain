---
title: Language in the brain, and how it compares to LLMs
category: function
tags: [language, broca, wernicke, dual-stream, aphasia, surprisal, n400, llm, brain-score, encoding-model, confounds, variance-partitioning]
use_cases:
  - where is language in the brain, what do Broca's and Wernicke's areas do
  - what is the dual-stream model of speech processing
  - do large language models process language like the brain
  - how are LLM activations compared with fMRI or ECoG recordings
  - is language the same thing as thought
  - is the LLM-brain match real computation or just word rate, position and word statistics
status: draft
last_verified: 2026-10-16
sources:
  - https://doi.org/10.1038/nrn2113
  - https://doi.org/10.1073/pnas.1112937108
  - https://doi.org/10.1073/pnas.2105646118
  - https://doi.org/10.1038/s41593-022-01026-4
  - https://doi.org/10.1038/s41586-024-07522-w
  - https://doi.org/10.1038/s41467-026-72253-7
  - https://doi.org/10.1162/nol_a_00087
  - https://doi.org/10.1038/s41597-021-01033-3
---

# Language in the brain, and how it compares to LLMs

## Summary
Language runs on a left-lateralised network in frontal and temporal cortex. The
19th-century picture of one "speech production" area (Broca) and one
"comprehension" area (Wernicke) has been replaced by a dual-stream model and by
a language network that is selective for language and not for maths or music.
Since 2021, several groups have shown that the internal activations of large
language models predict brain responses to the same sentences, and that the
models that predict the next word best also predict the brain best. Later
controls showed that much of that match, in sentence-reading data, comes from
word rate, sentence position and static word identity, and that shuffled
train/test splits inflate it. A check in this repo on open story-listening fMRI
(Narratives, held-out stories) found that GPT-2 still explains variance in the
language network that word rate, word frequency, n-gram surprisal, GPT-2's own
surprisal and static word embeddings do not. What that extra variance is (shared
computation, or richer context statistics) is still open.

## How it works

### Classic areas and aphasia (established, revised)
- **Broca's area** (left inferior frontal gyrus) and **Wernicke's area** (left
  posterior superior temporal cortex) come from 19th-century lesion cases.
  Damage near the first gives slow, effortful, telegraphic speech; damage near
  the second gives fluent speech with poor comprehension.
- **Revision.** MRI of Broca's preserved brains shows the lesions reached well
  beyond the area now named after him, into deep white matter (Dronkers et al.
  2007). Lasting aphasia usually needs damage to more than one area, and
  "Broca's area" itself contains subregions with different jobs.

### The dual-stream model (established framework)
Speech processing splits into two streams from auditory cortex, as vision does
([[sensory-systems-and-vision]]) (Hickok & Poeppel 2007):
- **Ventral stream** (temporal lobe, both hemispheres): sound to meaning.
- **Dorsal stream** (left temporo-parietal to frontal cortex): sound to
  articulation, used to repeat words and to learn new ones.

### A language-selective network (established)
Using fMRI regions defined in each person, Fedorenko, Behr & Kanwisher (2011)
found frontal and temporal regions that respond to sentences far more than to
lists of non-words, and barely respond to arithmetic, working-memory tasks or
music. People with global aphasia, who lose almost all language, can still do
arithmetic, logic and theory-of-mind tasks. Fedorenko, Piantadosi & Gibson (2024)
argue from this that language is mainly a tool for communication, not the
medium of thought; that broader claim is a position, not a settled result.

### Prediction during comprehension (established)
- The **N400**, an EEG wave about 400 ms after a word, is larger for words that
  do not fit their context ("He spread the warm bread with *socks*") (Kutas &
  Hillyard 1980).
- Its size tracks **surprisal**, `-log P(word | context)`, estimated by language
  models: the less expected the word, the larger the N400 (Frank et al. 2015).
- Meaning is spread across cortex: voxel-wise models fitted on hours of
  stories map semantic categories onto large parts of both hemispheres (Huth
  et al. 2016).

### LLMs compared with brain recordings
The method is an **encoding model**: take a model's activations for each word,
fit a linear map to the brain response (fMRI voxel, ECoG electrode), and score
the prediction on held-out text ([[evaluating-brain-models]]).

| Result | Status |
|---|---|
| Transformer activations predict fMRI and ECoG responses to sentences (Schrimpf et al. 2021) | established |
| Across 43 models, the ones better at next-word prediction predict the brain better (Schrimpf et al. 2021) | **contested**: it used random sentence splits; with contiguous splits the link is not significant among contextual models (Hadidi et al. 2026) |
| ECoG shows the brain predicts the next word before it arrives, and its surprise after the word matches the model's, word by word (Goldstein et al. 2022) | established |
| Across many models, brain scores rise with language-modelling performance (Caucheteux & King 2022) | established in that data (Dutch sentences, fMRI and MEG); **contested** as a general law (see below) |
| Adding predictions of words further ahead improves fit, more so in frontal and parietal regions, so the brain may predict over a longer horizon and a hierarchy of timescales (Caucheteux, Gramfort & King 2023) | **hypothesis** about mechanism, result established |
| A decoder built on an LLM recovers the gist of heard or imagined stories from fMRI, but only for a person who trained it and only with their cooperation (Tang et al. 2023) | established |
| "The brain is a next-word predictor like an LLM" | **hypothesis**, not shown |

### Shared computation or word statistics? What the controls show (literature check, #89)
A brain score can be high for reasons that have nothing to do with what a model
computes: words arrive at a varying rate, sentences have positions, frequent and
surprising words evoke different responses, and fMRI samples are correlated in
time. Recent papers test these one by one.

| Confound | What the controls found | Status |
|---|---|---|
| **Train/test split** | With shuffled splits, a feature that only encodes temporal autocorrelation matches or beats GPT2-XL, and the best-layer profile flips when splits are made contiguous (Feghhi et al. 2024; Hadidi et al. 2026). Schrimpf et al. (2021), Kauf et al. (2024) and Hosseini et al. (2024) used random 80/20 splits of sentences or passages. | established for the three datasets tested (Pereira, Fedorenko, Blank) |
| **Word rate and position** | Position plus word rate explain essentially all (>98%) of what untrained GPT2-XL predicts. For trained GPT2-XL, position + word rate + static GloVe vectors (Pereira) or position + word rate alone (Fedorenko, Blank) explain over 85%, over 80% and nearly 100% of its explained variance; adding GPT2-XL helps in about 3.4% of voxels, 4.7% of electrodes and no functional ROIs (Hadidi et al. 2026) | established in those datasets, which are mostly single sentences; one is 8 stories, 5 listeners, 60 ROIs |
| **Static word embeddings** | In ECoG, GPT-2's contextual embeddings predict more electrodes than GloVe, and earlier (Goldstein et al. 2022). In fMRI, removing or swapping content words lowers predictivity more than scrambling word order (Kauf et al. 2024) | contested: context adds something in ECoG; in fMRI word identity carries most of the signal |
| **Untrained models** | A Hugging Face-initialised untrained GPT-2 predicts above chance, one with all weights drawn from N(0, 0.02) does not (Hosseini et al. 2024). On an audiobook fMRI set, small untrained models all beat chance, and a fixed random vector per word did better than untrained transformers (Pasquiou et al. 2022) | established: untrained scores reflect word identity, rate and position, not shared computation |
| **Next-word prediction** | Encoding performance tracks next-word performance (r = 0.847) about as closely as it tracks how general a representation is (r = 0.864), and GPT-2's last layer, its best next-word predictor, adds no variance above layer 9 (Antonello & Huth 2024). A GPT-2 trained on about 100M words already predicts as well as the fully trained one (Hosseini et al. 2024) | contested: "better predictor, better brain model" may be "better general features" |
| **Surprisal** | Sentences an LLM-based encoding model picked to drive or suppress the language network did so in new participants; surprisal and well-formedness were the main determinants (Tuckute et al. 2024) | established: surprisal drives response size, so it must be a control |

**What is still open.** Whether contextual LLM features explain variance in
*long, naturalistic* story listening, tested on held-out stories, that word rate,
word frequency, n-gram surprisal and static embeddings together do not. The
controlled studies above used mostly isolated sentences, and none combined an
n-gram surprisal baseline with untrained and static controls in a large
story-listening set (the check found none; it is not an exhaustive review).

### Open-data test: GPT-2 vs word statistics in story listening (#89, this repo)
*Status: one analysis in this repo, not peer reviewed; n = 10 held-out stories.*

**Method.** Script: `research/llm_brain_match.py`.
- **Data.** Narratives (Nastase et al. 2021): 10 spoken stories, 4,467 fMRI
  volumes of 1.5 s (about 1 h 52 min), five listeners per story (two in a
  replication), left hemisphere, averaged into the 74 Destrieux parcels
  (Destrieux et al. 2010). The *language* set is 9 parcels fixed before any
  result: the three parts of the inferior frontal gyrus, lateral superior
  temporal gyrus, superior temporal sulcus, middle temporal gyrus, temporal
  pole, planum temporale and angular gyrus. Auditory (Heschl's gyrus) and early
  visual parcels are controls.
- **Features**, summed per volume, with delays of 1.5-9 s:
  **b** word statistics = word count + unigram surprisal (-log2 word frequency) +
  trigram surprisal, counted on WikiText-103 (85.9M word tokens; Merity et al.
  2017; Dirichlet smoothing, validation perplexity 380);
  **a** GPT-2 small layer 9 (Radford et al. 2019; layer fixed in advance from
  Antonello & Huth 2024); **c** the same network untrained (random weights);
  **s** GPT-2's static input embedding of each word; **g** GPT-2's own surprisal
  of each word. Embedding bands keep their top 128 principal components, fitted
  on the training stories.
- **Model.** Ridge regression, leave-one-story-out (no volume of a test story
  in training), penalty per parcel chosen inside the training stories; in joint
  models the word statistics are unpenalised. Unique variance of a over b =
  held-out r²(b + a) - r²(b). Tests run across the 10 stories (exact sign-flip,
  bootstrap 95% CI); the smallest possible p is 0.002.
- **Timing.** With the dataset's event timing, the lag from word count to
  auditory cortex was 5-6 volumes for two stories and -2 to 1 for a third, in
  all five listeners, against 2-4 for the group means of the other seven; and
  two Pie Man listeners ran 2-3 volumes ahead of the other three. The main run aligns listeners and stories using
  auditory cortex only; results with the raw event timing are shown too.

**Result: language parcels, 5 listeners, aligned timing.**

| Model | Held-out r [95% CI] |
|---|---|
| b word statistics | 0.155 [0.132, 0.178] |
| c untrained GPT-2 | 0.122 [0.094, 0.156] |
| s static GPT-2 embeddings | 0.179 [0.132, 0.226] |
| a GPT-2 layer 9 | 0.249 [0.204, 0.296] |
| b + a | 0.254 [0.216, 0.294] |
| split-half noise ceiling | 0.591 |

| Unique variance (language parcels) | 5 listeners, aligned | 2 listeners, aligned | 5 listeners, event timing | 2 listeners, event timing |
|---|---|---|---|---|
| GPT-2 over word statistics (a over b) | **+0.042** [0.027, 0.058], p = 0.002 | +0.014 [0.007, 0.022], p = 0.002 | +0.037 [0.022, 0.053], p = 0.002 | +0.013 [0.007, 0.019], p = 0.004 |
| GPT-2 over word statistics + static embeddings (a over b + s) | **+0.025** [0.018, 0.033], p = 0.002 | +0.009 [0.004, 0.015], p = 0.004 | +0.021 [0.012, 0.030], p = 0.002 | +0.008 [0.004, 0.013], p = 0.016 |
| GPT-2 over word statistics + GPT-2 surprisal (a over b + g) | **+0.033** [0.020, 0.047], p = 0.002 | +0.011 [0.003, 0.019], p = 0.062 | +0.030 [0.017, 0.044], p = 0.002 | +0.011 [0.004, 0.018], p = 0.016 |
| Untrained GPT-2 over word statistics (c over b) | +0.007 [0.003, 0.010], p = 0.014 | +0.003 [0.001, 0.005], p = 0.031 | +0.004 [0.001, 0.007], p = 0.068 | +0.000 [-0.001, 0.002], p = 0.89 |
| Control: GPT-2 shifted by half a story | -0.001 [-0.003, -0.000], p = 0.068 | -0.001 [-0.003, 0.000], p = 0.12 | -0.002 [-0.006, 0.000], p = 0.31 | -0.003 [-0.005, -0.001], p = 0.059 |

What else the main run shows:
- In all 10 stories GPT-2 added variance over the word statistics. About half
  (51%) of what b + a explains in the language parcels is unique to GPT-2; the
  word statistics add 7% beyond GPT-2. 26 of the 74 parcels pass a
  false-discovery-rate test for a over b (all positive), 7 of them language
  parcels; the early visual control shows no unique variance (+0.004, p = 0.15).
- Trained layers 6-8 fit best (r 0.258-0.261; 0.186 at the input layer). The
  untrained network stays at r 0.10-0.14 at every layer.
- GPT-2's surprisal adds little over n-gram surprisal (+0.012, p = 0.047), far
  less than its layer-9 state.
- Aligning the timing raised the word-statistics baseline (language r 0.094 to
  0.155; auditory 0.225 to 0.369) and did not shrink GPT-2's unique variance
  (0.037 to 0.042), so mis-timing was not what made GPT-2 look better.
- With two listeners every effect is smaller and noisier. The GPT-2 over
  GPT-2-surprisal contrast is positive in only 5 of 10 stories (p = 0.062), and
  three parcels pass the false-discovery test even in the shifted control (one
  up, two down).

**What it means.** *Result:* in story listening, tested on held-out stories,
"any model with the same word statistics" does not match the brain as well as
GPT-2, for the statistics tested here: word rate, frequency, trigram and GPT-2
surprisal, and static word identity. The extra signal needs training; the
untrained network adds almost nothing. *Hypothesis, not shown:* that the extra
variance is shared computation. It could be longer-range context statistics,
such as topic or discourse, that any good contextual model would capture. This
differs from the sentence-reading results above (Hadidi et al. 2026), where
word rate, position and static vectors left little for GPT2-XL. The data differ:
isolated sentences there, hour-long stories with held-out stories here.

**Limits.** Anatomical parcels stand in for the individually defined language
network, and only the left hemisphere is used. Some listeners heard several
stories, so the stories are not fully independent and p is slightly
optimistic. The timing alignment was estimated from the same data, though only
from auditory cortex and word count, and it can only help the baseline. The
event-timing results agree. The n-gram model is Dirichlet-smoothed, not
Kneser-Ney; the GPT-2-surprisal control is a stronger predictability baseline
and gives the same answer. There are no acoustic or phoneme regressors. One
model size, 128 components per band, one parcellation.

**Run it.** `python research/llm_brain_match.py --subjects 5` (default 2;
`--quick` is a 3-story smoke test; `--no-align` keeps event timing). The first
run downloads about 5.2 GB for five listeners (2.1 GB for two) to
`~/.cache/brain-kb/narratives/` and keeps only the parcel averages (6.5 MB), plus
WikiText-103 (314 MB) and GPT-2 weights (548 MB). On a busy 20-core CPU it took
about 1-1.5 h the first time (download speed decides) and about 20 min per
later run.

### Where brains and LLMs differ (established)
- **Data.** Children reach fluent language from tens of millions of words;
  current LLMs train on trillions, several orders of magnitude more (Frank 2023).
- **Language vs thought.** LLMs are strong at formal language (grammar, fluent
  text) and weaker at functional competence (reasoning, world knowledge, tracking
  situations), which in the brain uses networks outside the language network
  (Mahowald et al. 2024).
- **Learning signal.** LLMs learn by backprop on next-token error; the brain has
  no confirmed equivalent ([[brain-vs-deep-learning]]), and children learn in a
  shared physical and social world, not from text alone.

## Relevance to building brain-like AI
| Brain | AI component |
|---|---|
| Next-word surprisal drives the N400 | Next-token loss is a plausible shared objective, and surprisal is a cheap model-to-brain test |
| Language network separate from reasoning networks | Keep a language module separate from planning and memory, connected through an interface |
| Dorsal stream maps sound to articulation | Learn words by imitation: hear, try to say, compare (a forward model) |
| Fluent language from ~10^7 words | Data efficiency is the gap to close; grounding and curriculum are candidate reasons |

## Code: surprisal from a bigram model

A word-pair (bigram) model estimates `P(word | previous word)` from a tiny corpus.
Surprisal, `-log2 P`, is high for a word that does not fit, which is the quantity
the N400 tracks (Frank et al. 2015). Real studies use transformer surprisal;
this shows the measure, not its size.

```python
import numpy as np

corpus = ("he spread the bread with butter . she spread the bread with jam . "
          "he spread the toast with butter . she ate the bread with jam . "
          "he wore socks . she wore socks .").split()
vocab = sorted(set(corpus))
idx = {w: i for i, w in enumerate(vocab)}

counts = np.ones((len(vocab), len(vocab)))           # add-one smoothing
for a, b in zip(corpus, corpus[1:]):
    counts[idx[a], idx[b]] += 1
p_next = counts / counts.sum(axis=1, keepdims=True)  # P(next | previous)

def surprisal(prev, word):
    return -np.log2(p_next[idx[prev], idx[word]])    # bits

fit = surprisal("with", "butter")
misfit = surprisal("with", "socks")
print(f"'with butter' {fit:.2f} bits, 'with socks' {misfit:.2f} bits")
assert misfit > fit + 1.5                            # the odd word is far more surprising
```

## Open questions
- What GPT-2's extra variance in story listening is. In Narratives it survives
  word rate, word frequency, n-gram and GPT-2 surprisal and static embeddings
  (#89, above), so "the same word statistics" is not enough. Whether it is shared
  computation or longer-range context statistics (topic, discourse) is untested.
  Next test: add context-statistics controls (for example a bag of the previous
  N words, a topic model) and refit GPT-2 with its context shuffled or truncated.
- How children learn so much from so little data, and which ingredient
  (grounding, social feedback, innate bias, curriculum) matters most.
- How syntax is built in neural tissue, and whether it needs a dedicated
  mechanism.
- Why language is left-lateralised in most people.

## Related
- [[brain-vs-deep-learning]] - the wider gap between brains and backprop-trained networks.
- [[predictive-processing]] - next-word prediction as one case of predictive perception.
- [[evaluating-brain-models]] - encoding models and Brain-Score, the method behind the LLM results.
- [[brain-development-and-critical-periods]] - the critical period for language.
- [[sensory-systems-and-vision]] - the visual dual-stream model the speech one parallels.
- [[brain-structure-overview]] - where these regions sit.

## References
- Dronkers, Plaisant, Iba-Zizen & Cabanis (2007) "Paul Broca's historic cases: high resolution MR imaging of the brains of Leborgne and Lelong", *Brain* 130:1432. doi:10.1093/brain/awm042
- Hickok & Poeppel (2007) "The cortical organization of speech processing", *Nat Rev Neurosci* 8:393. doi:10.1038/nrn2113
- Fedorenko, Behr & Kanwisher (2011) "Functional specificity for high-level linguistic processing in the human brain", *PNAS* 108:16428. doi:10.1073/pnas.1112937108
- Fedorenko, Piantadosi & Gibson (2024) "Language is primarily a tool for communication rather than thought", *Nature* 630:575. doi:10.1038/s41586-024-07522-w
- Kutas & Hillyard (1980) "Reading senseless sentences: brain potentials reflect semantic incongruity", *Science* 207:203. doi:10.1126/science.7350657
- Frank, Otten, Galli & Vigliocco (2015) "The ERP response to the amount of information conveyed by words in sentences", *Brain Lang* 140:1. doi:10.1016/j.bandl.2014.10.006
- Huth, de Heer, Griffiths, Theunissen & Gallant (2016) "Natural speech reveals the semantic maps that tile human cerebral cortex", *Nature* 532:453. doi:10.1038/nature17637
- Schrimpf et al. (2021) "The neural architecture of language: Integrative modeling converges on predictive processing", *PNAS* 118:e2105646118. doi:10.1073/pnas.2105646118
- Goldstein et al. (2022) "Shared computational principles for language processing in humans and deep language models", *Nat Neurosci* 25:369. doi:10.1038/s41593-022-01026-4
- Caucheteux & King (2022) "Brains and algorithms partially converge in natural language processing", *Commun Biol* 5:134. doi:10.1038/s42003-022-03036-1
- Caucheteux, Gramfort & King (2023) "Evidence of a predictive coding hierarchy in the human brain listening to speech", *Nat Hum Behav* 7:430. doi:10.1038/s41562-022-01516-2
- Tang, LeBel, Jain & Huth (2023) "Semantic reconstruction of continuous language from non-invasive brain recordings", *Nat Neurosci* 26:858. doi:10.1038/s41593-023-01304-9
- Frank (2023) "Bridging the data gap between children and large language models", *Trends Cogn Sci* 27:990. doi:10.1016/j.tics.2023.08.007
- Mahowald, Ivanova, Blank, Kanwisher, Tenenbaum & Fedorenko (2024) "Dissociating language and thought in large language models", *Trends Cogn Sci* 28:517. doi:10.1016/j.tics.2024.01.011
- Pasquiou, Lakretz, Hale, Thirion & Pallier (2022) "Neural language models are not born equal to fit brain data, but training helps", *Proc. ICML*, PMLR 162:17499. arXiv:2207.03380
- Antonello & Huth (2024) "Predictive coding or just feature discovery? An alternative account of why language models fit brain data", *Neurobiol Lang* 5(1):64. doi:10.1162/nol_a_00087
- Kauf, Tuckute, Levy, Andreas & Fedorenko (2024) "Lexical-semantic content, not syntactic structure, is the main contributor to ANN-brain similarity of fMRI responses in the language network", *Neurobiol Lang* 5(1):7. doi:10.1162/nol_a_00116
- Hosseini, Schrimpf, Zhang, Bowman, Zaslavsky & Fedorenko (2024) "Artificial neural network language models predict human brain responses to language even after a developmentally realistic amount of training", *Neurobiol Lang* 5(1):43. doi:10.1162/nol_a_00137
- Tuckute, Sathe, Srikant, Taliaferro, Wang, Schrimpf, Kay & Fedorenko (2024) "Driving and suppressing the human language network using large language models", *Nat Hum Behav* 8:544. doi:10.1038/s41562-023-01783-7
- Feghhi, Hadidi, Song, Blank & Kao (2024) "What are large language models mapping to in the brain? A case against over-reliance on brain scores", arXiv:2406.01538
- Hadidi, Feghhi, Song, Blank & Kao (2026) "Spurious alignment between large language models and brains can emerge from non-robust methods and overlooked confounds", *Nat Commun* 17:5769. doi:10.1038/s41467-026-72253-7 (preprint 2025: doi:10.1101/2025.03.09.642245)
- Nastase et al. (2021) "The 'Narratives' fMRI dataset for evaluating models of naturalistic language comprehension", *Sci Data* 8:250. doi:10.1038/s41597-021-01033-3
- Destrieux, Fischl, Dale & Halgren (2010) "Automatic parcellation of human cortical gyri and sulci using standard anatomical nomenclature", *NeuroImage* 53:1. doi:10.1016/j.neuroimage.2010.06.010
- Merity, Xiong, Bradbury & Socher (2017) "Pointer sentinel mixture models" (WikiText-103), *ICLR*. arXiv:1609.07843
- Radford, Wu, Child, Luan, Amodei & Sutskever (2019) "Language models are unsupervised multitask learners" (GPT-2), OpenAI technical report
