# Paper notes: G. Language and reasoning

Structured notes on the sources cited by hypotheses H109-H130 in `research/learning-algorithm-hypotheses.md`, generated 2026-10-12. Six sources were read in full from the local PDFs. The other 19 are **abstract only** (the PDFs are not local, and PMC, Nature, PNAS and Europe PMC could not be fetched). Where `sources.json` holds no abstract at all, the note says so and makes no claim about the paper's content. Nothing here is invented: every number comes from the text that was read.

## Saffran 1996: Statistical learning by 8-month-old infants
- **Cited for:** H109 (infants find words by tracking transition probabilities between syllables)
- **Link:** https://doi.org/10.1126/science.274.5294.1926 · **Basis:** abstract only
- **Question:** Can 8-month-olds segment words from fluent speech using only statistics between neighbouring sounds?
- **Method / model:** Behavioural infant study (details not available in the abstract).
- **Experiments:** Not stated in the abstract beyond "2 minutes of exposure".
- **Key results:**
  - Word segmentation was achieved by 8-month-old infants "based solely on the statistical relationships between neighbouring speech sounds".
  - Learning came from only 2 minutes of exposure.
- **Limitations / caveats:** Not assessable from the abstract. The abstract does not mention a computational model.
- **Bearing on H109:** Supports the behavioural claim (infants segment by sequence statistics). It does not test whether a local Hebbian learner can do it; that is the repo's T1 check.
- **Reproduce in this repo:** Generate a stream of 4 trisyllabic nonsense words in random order, no pauses. Train a Hebbian/STDP-style bigram sequence learner on it. Check that its syllable-to-syllable transition weights are higher inside words than across word boundaries (dips in the weight/probability give the boundaries).

## Schrimpf 2021: The neural architecture of language: integrative modeling converges on predictive processing
- **Cited for:** H110 (the language network is a next-word predictor, like LLMs)
- **Link:** https://doi.org/10.1073/pnas.2105646118 · **Basis:** abstract only
- **Question:** Which artificial neural networks best predict human neural and behavioural responses to language, and does that relate to next-word prediction?
- **Method / model:** Compares many ANN language models to human recordings (the abstract says "across different datasets"; the models and metrics are not named in it).
- **Experiments:** Not detailed in the abstract.
- **Key results:**
  - "The most powerful models predict neural and behavioral responses across different datasets up to noise levels."
  - "Models that perform better at predicting the next word ... also better predict brain measurements."
- **Limitations / caveats:** Correlational. A good brain fit does not show the brain optimises next-word prediction. The abstract gives no controls.
- **Bearing on H110:** Partly supports. Next-word skill tracks brain fit. The paper does not rule out that non-predictive features fit as well; that is the repo's issue #89.
- **Reproduce in this repo:** n/a (T2).

## Goldstein 2022: Shared computational principles for language processing in humans and deep language models
- **Cited for:** H110 (the language network is a next-word predictor, like LLMs)
- **Link:** https://doi.org/10.1038/s41593-022-01026-4 · **Basis:** full text
- **Question:** Does the human brain, like an autoregressive deep language model (GPT-2), (1) predict the next word before onset, (2) compute post-onset surprise, (3) use contextual embeddings?
- **Method / model:** Linear encoding models predict ECoG high-gamma power (70-200 Hz) from GloVe or word2vec static embeddings, arbitrary random embeddings, or GPT-2 contextual embeddings, at lags around word onset. Entropy (confidence) and cross-entropy (surprise) are taken from GPT-2. A nonlinear decoder classifies word identity from neural windows.
- **Experiments:** 9 epilepsy patients with ECoG listened to a 30-min podcast (5,113 words); 1,106 left-hemisphere electrodes. A behavioural arm had 50 people predict each next word in a sliding 10-word window.
- **Key results:**
  - Humans predicted 28% of words (s.e. 0.5%) versus 6% for always guessing "the". Human and GPT-2 predictability correlated r = 0.79, with the match rising from r = 0.46 at a 2-word context to an asymptote near 100 words, above 2- to 5-gram baselines.
  - Static-embedding encoding of 160 electrodes was above chance up to 800 ms before word onset, also with arbitrary embeddings and after removing the previous word's information.
  - Pre-onset activity fell with GPT-2 entropy; post-onset activity rose with surprise (peak near 400 ms).
  - GPT-2 contextual embeddings gave 208 significant left electrodes (71 not significant with GloVe), predicting responses up to 4 s before onset. A contextual decoder beat static ones, with word information up to about 1 s before onset.
- **Limitations / caveats:** The authors state that sharing principles "do not imply that the human brain and DLMs implement these computations in a similar way". Transformers are "not biologically feasible". Epilepsy patients, one story, and an encoding correlation that is not causal.
- **Bearing on H110:** Supports that the brain shows pre-onset prediction signals and surprise like GPT-2. It does not show that prediction is the only or main objective, nor test prediction-free features.
- **Reproduce in this repo:** n/a (T2).

## Caucheteux 2023: Evidence of a predictive coding hierarchy in the human brain listening to speech
- **Cited for:** H111 (the brain predicts at many timescales at once, not only the next word)
- **Link:** https://doi.org/10.1038/s41562-022-01516-2 · **Basis:** full text
- **Question:** Does adding long-range, higher-level predictions to a language model improve its fit to brain activity, and are they organised hierarchically?
- **Method / model:** Ridge regression from GPT-2 activations (layer 8) to voxel fMRI; "brain score" = held-out correlation. A "forecast window" (7 words of future-word activations, at distance d) is concatenated to the present-word activations; forecast score = brain-score gain. Syntactic and semantic parts are separated by averaging activations over 10 syntax-matched possible futures. GPT-2 was also fine-tuned with an added objective of predicting layer 8 of word t+8.
- **Experiments:** Narratives fMRI dataset, 304 participants, 27 stories (7-56 min, 26 min on average per participant).
- **Key results:**
  - Peak brain score R = 0.23 (superior temporal sulcus), about 60% of the noise ceiling.
  - Forecast gain peaked at d = 8 words (about 3.15 s), a 23% (+/-9% across individuals) improvement in brain score. Random forecast vectors did not help. GPT-2-generated words instead of true future words gave lower but similar gains.
  - Longer forecast distance and deeper layers in frontoparietal cortex than in temporal cortex (for example Heschl's gyri k* = 2.5 versus associative cortices k* > 6).
  - Semantic forecasts reached d* = 8; syntactic d* = 5. Fine-tuning with the long-range, high-level objective gave over 2% gain in IFG and angular/supramarginal gyri.
- **Limitations / caveats:** Forecast windows use the actual future words, so a gain may reflect future-context information as much as prediction. Fit gains are small in absolute terms. Syntactic long-range forecasts were not detectable (dimensionality).
- **Bearing on H111:** Supports. Multi-horizon features improve the fit over next-word features, with a hierarchy of horizons.
- **Reproduce in this repo:** n/a (T2).

## Fedorenko 2024: Language is primarily a tool for communication rather than thought
- **Cited for:** H112 (language is mainly for communication; reasoning is done elsewhere and does not need language)
- **Link:** https://doi.org/10.1038/s41586-024-07522-w · **Basis:** abstract only (no abstract in sources.json; the page needs authentication)
- **Question:** Not verified. The title states the thesis.
- **Method / model:** Not verified (a Nature perspective/review, according to the row's venue).
- **Experiments:** Not verified.
- **Key results:** Not verified beyond the title's claim.
- **Limitations / caveats:** Not assessable.
- **Bearing on H112:** The title matches the hypothesis. The "does not need language" half could not be checked against the text.
- **Reproduce in this repo:** n/a (the row is T1/T3 and the claim itself is Tier 3).

## Kuhl 2003: Foreign-language experience in infancy: effects of short-term exposure and social interaction on phonetic learning
- **Cited for:** H113 (social interaction gates language learning: live person, not video)
- **Link:** https://doi.org/10.1073/pnas.1532872100 · **Basis:** abstract only
- **Question:** What conditions reverse the 6-12-month decline in foreign phonetic discrimination?
- **Method / model:** Two behavioural infant experiments with Mandarin Chinese speech.
- **Experiments:** Exp. 1: 9-month-old American infants had 12 laboratory sessions with native Mandarin speakers; a control group had 12 sessions of English only. Exp. 2: same speakers and material, via audiovisual or audio-only recordings.
- **Key results:**
  - Live Mandarin exposure reversed the decline seen in the English-control group.
  - Recorded exposure (audiovisual or audio-only), without interpersonal interaction, had no effect.
- **Limitations / caveats:** Numbers (sample sizes, percent correct) are not in the abstract. One language contrast, one age, short-term exposure.
- **Bearing on H113:** Supports. Live, but not prerecorded, exposure produced phonetic learning. It does not separate social gating from other differences between live and recorded input (the abstract does not discuss this).
- **Reproduce in this repo:** Two agents hear the same speech-like input stream; one has a "social-attention gate" that scales the plasticity of its sound categories by whether a live partner is present. Compare category separation after equal exposure.

## Berwick & Chomsky 2016: Why Only Us: Language and Evolution
- **Cited for:** H114 (an innate operation, Merge, builds hierarchical structure and learning cannot replace it)
- **Link:** https://doi.org/10.7551/mitpress/9780262034241.001.0001 · **Basis:** abstract only (no abstract in sources.json)
- **Question:** Not verified from a source in hand.
- **Method / model:** Book-length argument; no description was available in this pass.
- **Experiments:** n/a
- **Key results:** Not verified.
- **Limitations / caveats:** Not assessable. A theoretical argument, not an experiment.
- **Bearing on H114:** Cannot be assessed here. The title and row attribute the Merge claim to this book; the details were not checked.
- **Reproduce in this repo:** Train a local-rule sequence learner on strings from a nested grammar with no built-in composition operation; test generalisation to deeper nesting than seen in training. Passing would falsify "learning cannot replace Merge" for that learner.

## Dehaene 2015: The neural representation of sequences: from transition probabilities to algebraic patterns and linguistic trees
- **Cited for:** H115 (humans compress sequences into nested patterns; other primates do not)
- **Link:** https://doi.org/10.1016/j.neuron.2015.09.019 · **Basis:** abstract only (no abstract in sources.json)
- **Question:** Not verified; the title indicates a review of sequence representations from transition probabilities up to tree structures.
- **Method / model:** Not verified.
- **Experiments:** Not verified.
- **Key results:** Not verified.
- **Limitations / caveats:** Not assessable.
- **Bearing on H115:** Cannot be assessed. The "other primates do not" part is better supported by the 2022 abstract below than by anything checked for this paper.
- **Reproduce in this repo:** n/a (T2).

## Dehaene 2022: Symbols and mental programs: a hypothesis about human singularity
- **Cited for:** H115 (humans compress sequences into nested patterns; other primates do not)
- **Link:** https://doi.org/10.1016/j.tics.2022.06.010 · **Basis:** abstract only
- **Question:** Is human singularity due to multiple internal "languages of thought" that compress structure in many domains, not to natural language alone?
- **Method / model:** A hypothesis article. Each language has discretisation of a domain into a small symbol set and recursive composition into "mental programs" encoding nested repetitions with variations. Minimum description length (MDL) in these languages is the predictor of behaviour and brain activity.
- **Experiments:** The abstract refers to "elementary shape or sequence perception" tasks; no figures given.
- **Key results:**
  - MDL in the proposed languages "captures human behavior and brain activity" in these tasks.
  - "Non-human primate data are captured by simpler nonsymbolic models."
- **Limitations / caveats:** Abstract only. The authors call it a hypothesis. The primate contrast rests on model-comparison fits, not a proven absence.
- **Bearing on H115:** Supports the human-versus-primate claim as stated in the abstract. The repo's T2 check (compression model versus alternatives on human sequence data) is not itself reported in the abstract.
- **Reproduce in this repo:** n/a (T2).

## Lake 2015: Human-level concept learning through probabilistic program induction
- **Cited for:** H116 (concepts are learned as small programs from few examples; Bayesian program learning)
- **Link:** https://doi.org/10.1126/science.aab3050 · **Basis:** abstract only
- **Question:** Can a model that learns characters as probabilistic programs learn quickly and generalise like people?
- **Method / model:** Bayesian Program Learning (BPL), from the title and the editor's summary: a generative model of handwritten characters used to classify, parse and recreate characters.
- **Experiments:** The summary mentions "Turing-like tests" of generated characters against human drawings. Other details were not available.
- **Key results:**
  - The model "classifies, parses, and recreates handwritten characters, and can generate new letters" and "does so better than current deep learning algorithms" (editor's summary, without numbers).
- **Limitations / caveats:** No numbers or comparison details in the abstract. Omniglot is a narrow domain.
- **Bearing on H116:** Supports in direction (the summary says it beats deep learning on this task). The size of the gain and the baselines were not checked.
- **Reproduce in this repo:** Few-shot one-shot classifier on a toy stroke dataset: a program-like stroke-sequence model versus a small MLP trained on pixels, 1 example per class; compare accuracy.

## Tenenbaum 2011: How to grow a mind: statistics, structure, and abstraction
- **Cited for:** H117 (learning is Bayesian inference over structured hypotheses, so a few examples suffice)
- **Link:** https://doi.org/10.1126/science.1192788 · **Basis:** abstract only
- **Question:** How does abstract knowledge guide learning from sparse data, in what forms does it exist, and how is it acquired?
- **Method / model:** A review of "probabilistic inference over hierarchies of flexibly structured representations".
- **Experiments:** None as such (review).
- **Key results:** The abstract claims these models "can address some of the deepest questions" about the origins of human thought. It gives no results.
- **Limitations / caveats:** A review that advocates one framework. No head-to-head against neural learners is in the abstract.
- **Bearing on H117:** Supports as a statement of the framework. It does not itself test Bayesian versus neural learners.
- **Reproduce in this repo:** Number game or shape-concept few-shot task: a Bayesian learner over a small hypothesis space versus a small neural net, at 1-5 examples.

## Battaglia 2013: Simulation as an engine of physical scene understanding
- **Cited for:** H118 (physical reasoning is mental simulation with an internal physics engine)
- **Link:** https://doi.org/10.1073/pnas.1306572110 · **Basis:** abstract only (no abstract in sources.json; PMC returned a verification page)
- **Question:** Not verified; the title states the thesis.
- **Method / model:** Not verified.
- **Experiments:** Not verified.
- **Key results:** Not verified.
- **Limitations / caveats:** Not assessable.
- **Bearing on H118:** Cannot be assessed here; the title matches the hypothesis.
- **Reproduce in this repo:** Stable-versus-falling block towers: a small noisy-physics rollout agent versus a pattern-match classifier on new tower configurations.

## Alderson-Day & Fernyhough 2015: Inner speech: development, cognitive functions, phenomenology, and neurobiology
- **Cited for:** H119 (inner speech scaffolds reasoning; talking to yourself chains steps together)
- **Link:** https://doi.org/10.1037/bul0000021 · **Basis:** abstract only
- **Question:** What is known about inner speech: theory, development, function, neural basis?
- **Method / model:** A review plus a proposed multicomponent model of inner speech.
- **Experiments:** None (review of children and adults, typical and atypical).
- **Key results:**
  - "Inner speech appears to perform significant functions in human cognition", in some cases reflecting its developmental origins and shared resources with other cognitive processes.
  - It has been implicated in theories of cognitive development, speech monitoring, executive function and psychopathology.
- **Limitations / caveats:** The abstract notes variability among individuals and across the life span and "methodological challenges" in studying it.
- **Bearing on H119:** Partly supports. The abstract supports "significant functions" in cognition and executive function. "Chains steps together" for multi-step reasoning is the row's specific wording, not an abstract-level claim.
- **Reproduce in this repo:** Agent with an internal symbol loop (writes and reads its own intermediate tokens) versus none, on a 3-step composition task.

## Lupyan 2012: Linguistically modulated perception and cognition: the label-feedback hypothesis
- **Cited for:** H120 (words speed up abstraction: a shared label pulls different examples together)
- **Link:** https://doi.org/10.3389/fpsyg.2012.00054 · **Basis:** full text
- **Question:** How can effects of language on perception and categorisation be both deep and vulnerable to verbal interference?
- **Method / model:** Review plus a small fully recurrent connectionist network. A perceptual layer gets feature input for a distorted prototype (two categories, "chairs" and "tables"). The net learns to produce and comprehend category labels. Allowing label activity to feed back onto the perceptual/hidden layer pulls same-category items together (shown by principal-components plots); blocking feedback reverts to the perceptual structure; presenting the label exogenously enhances it further.
- **Experiments:** Reviews human studies (e.g. colour discrimination under verbal interference). One reviewed training study (Lupyan et al. 2007): learning to classify 16 "aliens" with redundant nonsense labels ("leebish", "grecious") versus no labels, equal trials. Labelled learners learned faster and kept accuracy at test; replacing labels with non-linguistic cues did not help.
- **Key results:**
  - The label-feedback model shows category structure is enhanced by label feedback (qualitative PCA, no accuracy numbers).
  - In the alien study, labels sped up category learning, though they were redundant with the response feedback.
  - Verbal interference attenuates linguistic effects, which the author reads as evidence for on-line, not permanent, modulation.
- **Limitations / caveats:** The author says that "in its present form, the label-feedback hypothesis is merely a sketch" and that its neural underpinnings "remain almost completely unexplored". The model is a small illustration, not a fit to data. The hypothesis is not claimed to cover all Whorfian effects.
- **Bearing on H120:** Supports the claim that labels help category learning and pull exemplars together. "Speed up abstraction" in a transfer sense goes slightly beyond what is shown (categorisation and perception tasks, not abstraction transfer).
- **Reproduce in this repo:** Small recurrent net with and without a label unit feeding back onto the hidden layer, trained on two noisy prototype categories; compare category-separation in hidden space and few-shot transfer to new exemplars.

## Hummel & Holyoak 1997: Distributed representations of structure: a theory of analogical access and mapping
- **Cited for:** H121 (analogy needs explicit relational binding, role and filler separate, by timing)
- **Link:** https://doi.org/10.1037/0033-295x.104.3.427 · **Basis:** abstract only (no abstract in sources.json)
- **Question:** Not verified; the title indicates a theory (LISA) of analogical access and mapping.
- **Method / model:** Not verified.
- **Experiments:** Not verified.
- **Key results:** Not verified.
- **Limitations / caveats:** Not assessable.
- **Bearing on H121:** Cannot be assessed here.
- **Reproduce in this repo:** Relational match-to-sample with a role-filler binding by synchrony (oscillation phase) versus a plain MLP; compare on novel fillers.

## Doumas, Hummel & Sandhofer 2008: A theory of the discovery and predication of relational concepts
- **Cited for:** H121 (analogy needs explicit relational binding, role and filler separate, by timing)
- **Link:** https://doi.org/10.1037/0033-295x.115.1.1 · **Basis:** abstract only (no abstract in sources.json)
- **Question:** Not verified. Only the citation title in `sources.json` was available.
- **Method / model:** Not verified.
- **Experiments:** Not verified.
- **Key results:** Not verified.
- **Limitations / caveats:** Not assessable.
- **Bearing on H121:** Cannot be assessed here.
- **Reproduce in this repo:** Same check as for Hummel & Holyoak 1997.

## Penn, Holyoak & Povinelli 2008: Darwin's mistake: explaining the discontinuity between human and nonhuman minds
- **Cited for:** H122 (what makes humans different is reasoning about relations between relations)
- **Link:** https://doi.org/10.1017/s0140525x08003543 · **Basis:** abstract only
- **Question:** Are human and nonhuman minds different in degree or in kind?
- **Method / model:** A target article (review and argument). It proposes a representational-level account of how well animals approximate a physical symbol system (PSS) and points to symbolic-connectionist models.
- **Experiments:** A literature review across cognitive domains, no new data in the abstract.
- **Key results:**
  - The authors argue there is "a significant discontinuity in the degree to which human and nonhuman animals are able to approximate the higher-order, systematic, relational capabilities of a physical symbol system".
  - This discontinuity "pervades nearly every domain of cognition and runs much deeper than even the spectacular scaffolding provided by language or culture alone can explain".
- **Limitations / caveats:** A position paper; it is peer-commented in BBS (commentary not read).
- **Bearing on H122:** Supports in outline. The abstract speaks of higher-order, systematic relational capabilities; "relational reinterpretation" and "relations between relations" are the row's more specific wording, not verified in the abstract.
- **Reproduce in this repo:** n/a (mostly T3).

## Bunge 2005: Analogical reasoning and prefrontal cortex: evidence for separable retrieval and integration mechanisms
- **Cited for:** H123 (rostrolateral PFC integrates relations for analogy)
- **Link:** https://doi.org/10.1093/cercor/bhh126 · **Basis:** abstract only (no abstract in sources.json)
- **Question:** Not verified. The title mentions separable retrieval and integration mechanisms in prefrontal cortex.
- **Method / model:** Not verified.
- **Experiments:** Not verified.
- **Key results:** Not verified.
- **Limitations / caveats:** Not assessable.
- **Bearing on H123:** Cannot be assessed here. The title suggests the study separates retrieval and integration, which matches the row only if rostrolateral PFC is the integration site; that was not checked.
- **Reproduce in this repo:** n/a (T2).

## Dehaene, Kerszberg & Changeux 1998: A neuronal model of a global workspace in effortful cognitive tasks
- **Cited for:** H124 (a global workspace broadcasts one content to many modules, allowing flexible combination)
- **Link:** https://doi.org/10.1073/pnas.95.24.14529 · **Basis:** abstract only
- **Question:** What brain processes underlie effortful tasks?
- **Method / model:** A neuronal model with two computational spaces: a unique global workspace of distributed neurons with long-range axons, and specialised modular processors (perceptual, motor, memory, evaluative, attentional). Workspace neurons "selectively mobilize or suppress, through descending connections" the processors. Workspace states are modulated by vigilance signals and selected by reward signals.
- **Experiments:** A computer simulation of the Stroop task.
- **Key results:**
  - Workspace activation increases during acquisition of a novel task, during effortful execution, and after errors.
  - Predicts spatio-temporal imaging patterns, especially for dorsolateral prefrontal cortex and anterior cingulate.
- **Limitations / caveats:** Simulation of one task; the abstract reports no quantitative fits.
- **Bearing on H124:** Partly supports. The model has a workspace that mobilises specialised processors in effortful tasks. The abstract does not test "combining modules in new combinations" or compare against a fully modular architecture.
- **Reproduce in this repo:** Train modules on single skills; compare a shared workspace vector (read and written by all) versus fixed pairwise connections on novel skill combinations.

## Ito 2008: Control of mental activities by internal models in the cerebellum
- **Cited for:** H125 (the cerebellum learns internal models of thoughts as well as movements, making familiar reasoning automatic)
- **Link:** https://doi.org/10.1038/nrn2332 · **Basis:** abstract only (no abstract in sources.json)
- **Question:** Not verified; the title states that internal models in the cerebellum control mental activities.
- **Method / model:** Not verified.
- **Experiments:** Not verified.
- **Key results:** Not verified.
- **Limitations / caveats:** Not assessable.
- **Bearing on H125:** Cannot be assessed here; the title matches the row.
- **Reproduce in this repo:** Agent with a learned forward model of its own reasoning steps (predicts the next internal state) versus none; measure steps to complete a familiar multi-step task.

## Tomasello 1999: The Cultural Origins of Human Cognition
- **Cited for:** H126 (abstraction is mostly learned from other people, not invented alone)
- **Link:** https://doi.org/10.4159/9780674044371 · **Basis:** abstract only (no abstract in sources.json)
- **Question:** Not verified from a source in hand.
- **Method / model:** Book-length argument; details not checked.
- **Experiments:** n/a
- **Key results:** Not verified.
- **Limitations / caveats:** Not assessable.
- **Bearing on H126:** Cannot be assessed here; the title matches the row's theme.
- **Reproduce in this repo:** Agent that sees demonstrations from a trained agent versus an agent exploring alone; compare abstraction on held-out items.

## Shafto, Goodman & Griffiths 2014: A rational account of pedagogical reasoning: teaching by, and learning from, examples
- **Cited for:** H127 (learners assume the teacher picks helpful examples and learn more from each one)
- **Link:** https://doi.org/10.1016/j.cogpsych.2013.12.004 · **Basis:** abstract only (no abstract in sources.json)
- **Question:** Not verified. Only the citation title was available.
- **Method / model:** Not verified.
- **Experiments:** Not verified.
- **Key results:** Not verified.
- **Limitations / caveats:** Not assessable.
- **Bearing on H127:** Cannot be assessed here; the title matches the row.
- **Reproduce in this repo:** Concept learning with a learner that assumes helpful (pedagogical) sampling versus random sampling; count examples needed to reach the target concept.

## Lazaridou & Baroni 2020: Emergent multi-agent communication in the deep learning era
- **Cited for:** H128 (shared symbols emerge when two agents with local rules must cooperate through a narrow channel)
- **Link:** https://arxiv.org/abs/2006.02419 · **Basis:** full text
- **Question:** Under what conditions do communities of deep agents develop a shared language, and what are its features?
- **Method / model:** A survey. Agents are deep networks trained by deep reinforcement learning, with discrete messages trained by the REINFORCE update rule or continuous relaxations (Gumbel-softmax). Success in the game is the only training signal.
- **Experiments:** Reviews referential games (for example Lazaridou et al. 2017; Havrylov & Titov 2017 with variable-length strings), multi-turn games, a symmetric fruit/tool game and contact-linguistics simulations. No new experiments.
- **Key results:**
  - Agents can develop effective protocols using game success as the sole signal, but evidence for human-like words for generic concepts was "mixed".
  - Measuring real communication is hard: ablating the channel does not prove use, and agents can encode information in the number of turns. Lowe et al. propose causal influence of communication as the necessary and sufficient test of positive listening.
  - Compositionality: topographic similarity is the common measure; emergent languages can generalise to novel combinations without being compositional; compositionality emerges more easily with attribute-value input, generational transmission and larger communities. The authors say the knowledge of which pressures are necessary is "still very sketchy".
  - Agents in symmetric games can develop role-specific idiolects; a third agent can be enough to produce a shared code.
- **Limitations / caveats:** It is a review of deep-RL agents, not of local-rule agents or neuroscience. Many findings are mixed or partial.
- **Bearing on H128:** Partly supports the general claim (cooperative pressure through a discrete channel yields usable protocols), but **the row misdescribes the source**: the agents are backprop and policy-gradient trained deep networks, not "local rules", and the survey reports compositional codes are not reliably produced. The T1 test (two Brain World agents with local rules) is not tested by this paper.
- **Reproduce in this repo:** Two agents with a one-symbol channel in a referential game, using only a local reward-modulated update. Measure the sender's message-to-object mutual information and topographic similarity.

## Lake & Baroni 2023: Human-like systematic generalization through a meta-learning neural network
- **Cited for:** H129 (systematic compositional generalisation comes from meta-learning over many small tasks)
- **Link:** https://doi.org/10.1038/s41586-023-06668-3 · **Basis:** full text
- **Question:** Can a standard neural network reach human-like systematic generalisation if it is optimised for compositional skill?
- **Method / model:** Meta-learning for compositionality (MLC). A standard transformer (3 layers, 8 heads per layer) sees many episodes, each drawn from a new random grammar, with a few study examples plus a query. It is trained with ordinary gradient descent on the query outputs across episodes; at test time the weights are frozen and the network performs new tasks in context. Training used 100,000 episodes (batch of 25 episodes) with the Adam optimiser.
- **Experiments:** Human instruction-learning with an artificial pseudolanguage (few-shot task n = 25; open-ended n = 29), compared with seven model variants: MLC and variants, a symbolic probabilistic model with and without biases, a basic seq2seq, and others. Also the SCAN and COGS benchmarks.
- **Key results:**
  - Humans produced the algebraic output in 80.7% of cases, and 72.5% on longer output sequences. MLC produced the algebraic output at 82.4% and 77.8% on longer sequences. In the open-ended task MLC matched the modal human response in 65.0% of samples.
  - Model errors resembled humans' (one-to-one translations 56.3% of MLC errors versus 24.4% for people; iconic concatenation 13.8% versus 23.3%). Only MLC captured both systematicity and flexibility, according to log-likelihood of human behaviour.
  - SCAN/COGS lexical splits: MLC error 0.22% or lower on the SCAN splits and 0.87% on COGS lexical generalisation, versus 99.27% (SCAN add jump) for basic seq2seq.
  - MLC failed productivity splits (longer outputs, new structures), with 100% error.
- **Limitations / caveats:** The authors say MLC "does not automatically handle unpractised forms of generalization or concepts outside the meta-learning distribution", cannot emit new symbols, and is untested on full natural language. GPT-4 results are preliminary.
- **Bearing on H129:** Supports for gradient-trained transformers: meta-learning over many small episodes yields human-like systematicity on lexical splits. It does not test local learning rules, which is what the repo's falsifier tests.
- **Reproduce in this repo:** Meta-train a small recurrent net (local-rule or backprop baseline) on episodes of random word-to-symbol grammars; test on held-out combinations of known primitives, as in the SCAN add-jump split.

## Chan 2022: Data distributional properties drive emergent in-context learning in transformers
- **Cited for:** H130 (bursty, Zipf-like statistics of natural input are what make in-context learning emerge)
- **Link:** https://doi.org/10.52202/068431-1371 · **Basis:** full text
- **Question:** Which properties of training data (not just architecture) cause in-context learning to emerge?
- **Method / model:** Causal transformer (12 layers, embedding size 64) with a ResNet image embedder, trained on sequences of Omniglot image-label pairs (8 context pairs plus a query), with softmax cross-entropy on the query label. Training data mix "bursty" sequences (query class appears 3 times in the context) with i.i.d. ones. Evaluation: in-context learning (4-shot 2-way on held-out classes with relabelled 0/1) and in-weights learning (trained classes, labels as in training).
- **Experiments:** Varied the burstiness proportion, the number of training classes (100, 1,600, 12,800 using rotations and flips), label multiplicity, within-class variation, and Zipf exponent of the class distribution. Compared transformers with vanilla RNNs and LSTMs (parameter-matched, 15 runs per architecture).
- **Key results:**
  - In-context learning emerged only with burstiness together with a large number of rarely occurring classes. More burstiness and more classes increased in-context learning and reduced in-weights learning (a trade-off).
  - Dynamic item meaning (label multiplicity, within-class variation) pushed the model further toward in-context learning.
  - A Zipfian class distribution allowed both in-context and in-weights learning in one model. A Zipf exponent of 1, close to natural-language skew, was a sweet spot.
  - Recurrent models (RNN, LSTM) never performed above chance in-context learning on the same data; "attention is not all you need" (architecture and data both matter).
- **Limitations / caveats:** Image-label classification on Omniglot, small models; the link to natural-language LLMs is by analogy. The trade-off between in-context and in-weights learning is only resolved by the Zipfian setting.
- **Bearing on H130:** Supports. Bursty, many-rare-class (and, for coexistence, Zipfian) data drive in-context learning in transformers. The paper already contains the bursty-versus-uniform comparison, so the repo's T1 test is a replication. It also shows the architecture matters, so "what make it emerge" is not data alone.
- **Reproduce in this repo:** Train a small attention model on sequences of random vectors and labels with p(bursty) of 0, 0.5 and 0.9; test on held-out classes with relabelling. Compare few-shot accuracy.

## Corrections to the hypotheses file

- **H128:** The Lazaridou & Baroni 2020 source is a survey of deep-RL agents (REINFORCE or relaxed discrete channels, not local rules), and it reports that compositional codes are not reliably produced. Rephrase to "shared symbols can emerge when agents must cooperate through a discrete channel (deep-RL agents, per Lazaridou & Baroni 2020); whether local-rule agents do the same is untested" and keep the T1 test as the open question.
- **H129:** Lake & Baroni 2023 used a backprop-trained transformer. The claim holds for that model; the falsifier (meta-learned local-rule net) is not covered by the paper. Say so in the row.
- **H130:** The paper's own experiments already compared bursty and uniform training and found a difference. Mark the falsifier as "replication in a different setting" rather than an open test, and note that architecture also matters (RNNs and LSTMs fail).
- **H110:** Goldstein 2022's authors state that shared principles do not imply the same implementation; consider adding "in behaviour and activity patterns, not in mechanism".
- **H119:** The abstract of Alderson-Day & Fernyhough 2015 supports "significant functions in cognition (including executive function)", not specifically "chains steps together"; soften the row's wording.
- **H112, H114, H118, H121, H123, H125, H126, H127:** Sources.json holds no abstract, and the full text was not reachable in this pass. These claims are unverified here and the notes make no claim about the papers' contents. They need a re-check with the PDFs.
