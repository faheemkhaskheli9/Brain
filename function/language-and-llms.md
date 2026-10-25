---
title: Language in the brain, and how it compares to LLMs
category: function
tags: [language, broca, wernicke, dual-stream, aphasia, surprisal, n400, llm, brain-score, encoding-model]
use_cases:
  - where is language in the brain, what do Broca's and Wernicke's areas do
  - what is the dual-stream model of speech processing
  - do large language models process language like the brain
  - how are LLM activations compared with fMRI or ECoG recordings
  - is language the same thing as thought
status: draft
last_verified: 2026-10-25
sources:
  - https://doi.org/10.1038/nrn2113
  - https://doi.org/10.1073/pnas.1112937108
  - https://doi.org/10.1073/pnas.2105646118
  - https://doi.org/10.1038/s41593-022-01026-4
  - https://doi.org/10.1038/s41586-024-07522-w
  - https://doi.org/10.1038/s41597-023-02437-z
---

# Language in the brain, and how it compares to LLMs

## Summary
Language runs on a left-lateralised network in frontal and temporal cortex. The
19th-century picture of one "speech production" area (Broca) and one
"comprehension" area (Wernicke) has been replaced by a dual-stream model and by
a language network that is selective for language and not for maths or music.
Since 2021, several groups have shown that the internal activations of large
language models predict brain responses to the same sentences, and that the
models that predict the next word best also predict the brain best. What that
convergence means is open: the shared ingredient may just be prediction.

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
| Transformer activations predict fMRI and ECoG responses to sentences; across 43 models, the ones better at next-word prediction predict the brain better (Schrimpf et al. 2021) | established |
| ECoG shows the brain predicts the next word before it arrives, and its surprise after the word matches the model's, word by word (Goldstein et al. 2022) | established |
| Across many models, brain scores rise with language-modelling performance (Caucheteux & King 2022) | established |
| Adding predictions of words further ahead improves fit, more so in frontal and parietal regions, so the brain may predict over a longer horizon and a hierarchy of timescales (Caucheteux, Gramfort & King 2023) | **hypothesis** about mechanism, result established |
| A decoder built on an LLM recovers the gist of heard or imagined stories from fMRI, but only for a person who trained it and only with their cooperation (Tang et al. 2023) | established |
| "The brain is a next-word predictor like an LLM" | **hypothesis**, not shown |

**Does GPT-2 explain story fMRI beyond word statistics? (#89, measured here,
2026-10-25.)** [`research/llm_brain_match.py`](../research/llm_brain_match.py)
(method pre-registered in its docstring) fits leave-one-story-out ridge encoding
models to 5 subjects listening to 25 stories (LeBel et al. 2023), on the 2,000
voxels per subject with the highest repeat reliability on a sixth story heard five
times. Word statistics (W) are word rate plus unigram and trigram surprisal from
the other 83 transcripts. GPT-2 (small, 124M) features are layer-9 states. Unique
variance = held-out r² of base + block minus r² of base, per story averaged over
subjects; 95% CI from story bootstraps, sign-flip p over the 25 stories.

| Added block over base | Unique r² | 95% CI | Stories > 0 | Subjects > 0 | p |
|---|---|---|---|---|---|
| **GPT-2 over W (primary)** | **+0.029** | [+0.026, +0.033] | 25/25 | 5/5 | < 0.0001 |
| GPT-2 over W + static embeddings | +0.021 | [+0.018, +0.024] | 25/25 | 5/5 | < 0.0001 |
| GPT-2 over W + GPT-2 surprisal | +0.029 | [+0.026, +0.032] | 25/25 | 5/5 | < 0.0001 |
| Untrained GPT-2 over W | +0.006 | [+0.005, +0.009] | 24/25 | 5/5 | < 0.0001 |
| GPT-2 shifted by half a story over W | -0.0003 | [-0.0004, -0.0002] | 4/25 | 0/5 | 1.0 |

- **GPT-2 explains variance word statistics cannot.** W alone reaches r² 0.018,
  W + GPT-2 0.047 (mean voxel r 0.086 vs 0.180; repeat-reliability ceiling r 0.244).
  The gain survives static word embeddings and GPT-2's own surprisal, so it is not
  only word identity or predictability.
- **The controls stay small.** An untrained GPT-2 adds a fifth as much (its
  architecture alone mixes neighbouring words), and the same GPT-2 features shifted
  out of alignment add nothing, so the gain needs trained, time-locked context.
- **What it does not show.** Context features predicting the brain is not proof the
  brain computes like GPT-2: richer phrase-level statistics than trigrams, which
  were not tested, could carry the same signal. One model, one layer, one dataset;
  the TR alignment offset (5 TR) was picked by the word-statistics fit before any
  GPT-2 model was fitted. The unique r² +0.042 in the #89 issue comment (Narratives
  data, never pushed) is not reproduced.

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
- Whether brain-LLM similarity comes from shared computation or just from both
  predicting the same text statistics. On story fMRI, GPT-2 beats unigram and
  trigram statistics and its controls (#89, above); richer statistics and other
  models are untested.
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
- [[social-cognition-and-theory-of-mind]] - theory of mind, which aphasic patients keep, and whether LLMs have it.

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
- LeBel et al. (2023) "A natural language fMRI dataset for voxelwise encoding models", *Sci Data* 10:555. doi:10.1038/s41597-023-02437-z
- Tang, LeBel, Jain & Huth (2023) "Semantic reconstruction of continuous language from non-invasive brain recordings", *Nat Neurosci* 26:858. doi:10.1038/s41593-023-01304-9
- Frank (2023) "Bridging the data gap between children and large language models", *Trends Cogn Sci* 27:990. doi:10.1016/j.tics.2023.08.007
- Mahowald, Ivanova, Blank, Kanwisher, Tenenbaum & Fedorenko (2024) "Dissociating language and thought in large language models", *Trends Cogn Sci* 28:517. doi:10.1016/j.tics.2024.01.011
