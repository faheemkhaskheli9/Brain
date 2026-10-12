# Hypotheses: the brain's learning algorithm

**Research thread** (owner, started 2026-10-11). This file is the place to resume the
thread from any machine or chat session: open it, read **Next up** and the **Log**, then
carry on.

## The problem
We know some local learning rules: Hebbian learning, STDP and dopamine as a
reward-prediction error. No known rule explains how humans learn abstraction, language or
reasoning. LLMs, Claude included, get those abilities from scale and backpropagation, not
by working like a brain (see
[build-a-brain-like-learner](../guides/build-a-brain-like-learner.md)).

The working question:

> Can rules that are **local** (each synapse sees only its own two neurons plus broadcast
> signals such as dopamine) learn **reusable abstract structure**? If not, what extra
> ingredient does the brain add?

## How to read this file
- **Every row is a hypothesis, not an established fact.** A source means "this idea was
  proposed or argued in that paper", not "that paper proved it".
- Sources were written from memory on 2026-10-12. **Check each one** (authors, year,
  venue) before you cite it anywhere, as step 0 of
  [research-with-ai](../guides/research-with-ai.md).
- Rows marked **new** come from this research thread and have no published source.
- Many rows compete (for example H001 vs H090: "the brain approximates gradients" vs
  "there is no special algorithm, only scale"). A result that supports one weakens the
  other. Rows can also combine: the brain probably uses several of these at once.
- **Tier** says what can answer the question. T1 = a simulation in this repo (days to
  weeks). T2 = open data (weeks). T3 = needs a lab, new instruments or theory.
- **Status** is one of: `open`, `in progress`, `supported`, `weakened`, `refuted`,
  `answered elsewhere`. Change it when there is evidence, and add a Log line.

**Plain-language version.** Every row is explained in simple words, with a step-by-step
workflow of how it would work in the brain and how to test it, in
[hypotheses-explained/](hypotheses-explained/README.md).

## How to continue
1. Pick a row: start with **Next up**, or any T1 row.
2. Step 0: check whether the literature has already answered it.
3. Pre-register in a GitHub issue labelled `research-gap`: the hypothesis, the metric,
   and what result would count against it. Do this before running anything.
4. Build the smallest numpy experiment. Run several seeds.
5. Record the result in the topic file, in the **Log** below and in this row's Status.
   Then close the issue.

To resume in Claude from anywhere, say: "continue the learning-algorithm research, read
research/learning-algorithm-hypotheses.md".

## Next up (cheapest T1 rows with the biggest payoff)
1. **H001**: predictive coding updates match backprop gradients on a tiny MLP. A day's
   work in numpy, and a good Brain Lab level.
2. **H002 + H003**: feedback alignment and direct feedback alignment on the same tiny MLP.
3. **H101**: the main transfer experiment in Brain World (local rule vs backprop on
   layouts with shared structure).
4. **H103**: does a built-in prior close more of the transfer gap than a better rule
   does? (Feeds issue #83.)
5. **H104**: does replay turn episodes into a reusable schema?

---

## A. Credit assignment: local approximations of backprop
| ID | Hypothesis | Source | Test → counts against it if | Tier | Status |
|---|---|---|---|---|---|
| H001 | Predictive coding networks compute weight updates that converge to backprop's gradients, using only local errors. | Whittington & Bogacz 2017, *Neural Comput* | Compare PC updates with backprop gradients on a tiny MLP → cosine similarity stays low at equilibrium | T1 | open |
| H002 | Fixed random feedback weights are enough: the forward weights learn to align with them (feedback alignment). | Lillicrap et al. 2016, *Nat Commun* | FA vs backprop on MNIST/XOR → FA fails to learn hidden layers | T1 | open |
| H003 | The output error can be broadcast straight to every layer through random weights (direct feedback alignment). | Nøkland 2016, NeurIPS | DFA on a 3-layer MLP → no better than training only the readout | T1 | open |
| H004 | Pyramidal neurons multiplex: event rate carries the feedforward signal and burst probability carries the error. | Payeur et al. 2021, *Nat Neurosci* | Burst-dependent rule in a spiking net → cannot solve XOR | T1/T3 | open |
| H005 | Apical dendrites compare top-down predictions with somatic activity. The mismatch acts as the error. | Sacramento et al. 2018, NeurIPS; Urbanczik & Senn 2014, *Neuron* | Dendritic microcircuit model → updates do not track backprop | T1 | open |
| H006 | The brain runs two phases (free, then gently nudged toward the target) and learns from the difference (equilibrium propagation). | Scellier & Bengio 2017, *Front Comput Neurosci* | EqProp on a small energy net → fails where backprop succeeds | T1 | open |
| H007 | Contrastive Hebbian learning between a "minus" (expectation) phase and a "plus" (outcome) phase is cortex's error-driven rule. | O'Reilly 1996, *Neural Comput* (GeneRec) | GeneRec vs backprop on small tasks → large accuracy gap | T1 | open |
| H008 | Each layer learns to hit a target sent down from above, not a gradient (target propagation). | Lee et al. 2015, ECML-PKDD | Difference target prop on MNIST → much worse than FA | T1 | open |
| H009 | Feedback weights become symmetric through their own local rule, so no weight transport is needed (Kolen-Pollack, weight mirrors). | Akrout et al. 2019, NeurIPS | KP rule → feedback/forward angle does not shrink | T1 | open |
| H010 | Perturbing activity or weights and correlating the change with reward is enough (node perturbation, REINFORCE). It works in small circuits such as birdsong. | Williams 1992, *Mach Learn*; Fiete & Seung 2006, *PRL* | Scaling test → learning time grows so fast with network size that it is useless above ~100 units | T1 | open |
| H011 | Two forward passes, one on real data and one on negative data, with a local goodness per layer replace backward passes (forward-forward). | Hinton 2022, arXiv:2212.13345 | FF on MNIST → no better than a random-feature readout | T1 | open |
| H012 | Alternating a wake phase and a sleep phase trains recognition and generative paths with local rules (wake-sleep). | Hinton et al. 1995, *Science* | Wake-sleep on toy data → generative model does not improve | T1 | open |
| H013 | The thalamus (pulvinar) supplies the "outcome" phase: every ~100 ms alpha cycle compares the cortical prediction with actual input. | O'Reilly et al. 2021, *J Cogn Neurosci* | T1 model works; T3: pulvinar silencing should block predictive learning | T1/T3 | open |
| H014 | Learning across time uses eligibility traces plus a broadcast learning signal, not backprop through time (e-prop). | Bellec et al. 2020, *Nat Commun* | e-prop vs BPTT on a delayed-recall task → e-prop fails at delays over a few seconds | T1 | open |
| H015 | The cerebellum predicts the future error signal for cortex, so cortex can learn without waiting (synthetic gradients). | Jaderberg et al. 2017, ICML; Boven et al. 2023, *Nat Commun* | Cortex + cerebellar critic model → no speed-up over cortex alone | T1 | open |
| H016 | Each layer optimises its own local loss, so no global error is needed. | Nøkland & Eidnes 2019, ICML | Local-loss net → large gap to end-to-end training on structured tasks | T1 | open |
| H017 | Attention feedback tags the neurons that caused an action, and dopamine then updates only the tagged synapses (AGREL). | Roelfsema & van Ooyen 2005, *Neural Comput*; Roelfsema & Holtmaat 2018, *Nat Rev Neurosci* | AGREL on a classification task → much slower than backprop | T1 | open |
| H018 | Credit assignment is learned: the feedback pathway is itself trained (learning to learn) together with local plasticity. | Lindsey & Litwin-Kumar 2020, NeurIPS | Meta-learned feedback → no gain over fixed random feedback | T1 | open |
| H019 | Somatic spikes are predicted by dendrites, and the prediction error at the dendrite drives plasticity. | Urbanczik & Senn 2014, *Neuron* | One-neuron model → cannot learn a teacher's input-output map | T1 | open |
| H020 | Backprop-like learning happens only in slow, sleep-linked phases, not online. | **new** | Online-only vs sleep-phase learning of the same rule → no difference | T1 | open |

## B. Reward, neuromodulators and three-factor rules
| ID | Hypothesis | Source | Test → counts against it if | Tier | Status |
|---|---|---|---|---|---|
| H021 | Plasticity is Hebb × eligibility trace × neuromodulator: the third factor arrives seconds later and converts traces into weight changes. | Gerstner et al. 2018, *Front Neural Circuits* | Three-factor net on delayed reward → no better than chance | T1 | open |
| H022 | Phasic dopamine is a temporal-difference reward-prediction error. | Schultz, Dayan & Montague 1997, *Science* | (Strongly supported for reward. Open question here: is it enough for abstraction?) Brain World TD agent → cannot learn structure | T1 | open |
| H023 | Dopamine neurons encode a whole distribution of future reward (distributional RL), giving richer learning signals. | Dabney et al. 2020, *Nature* | Distributional vs scalar TD in Brain World → no representation gain | T1 | open |
| H024 | Dopamine is a vector, not a scalar: different neurons carry errors about different features, so learning targets specific parts of the network. | Engelhard et al. 2019, *Nature* | Vector vs scalar RPE in a multi-feature task → no speed-up | T1/T2 | open |
| H025 | Acetylcholine reports expected uncertainty and noradrenaline unexpected uncertainty. Together they set how much to trust old knowledge vs new input. | Yu & Dayan 2005, *Neuron* | Agent with both signals vs fixed learning rate on a switching task → no gain | T1 | open |
| H026 | Neuromodulators set the meta-parameters of learning: dopamine the error, serotonin the time horizon, noradrenaline exploration, acetylcholine the learning rate. | Doya 2002, *Neural Netw* | Agent with modulated meta-parameters vs tuned constants → no gain across tasks | T1 | open |
| H027 | Dopamine slowly trains prefrontal recurrent weights. That network then learns new tasks fast within its activity (meta-RL). Abstraction lives in activity, not weights. | Wang et al. 2018, *Nat Neurosci* | Meta-RL RNN in Brain World → no in-episode learning on new layouts | T1 | open |
| H028 | A single event can rewrite synapses active seconds before or after it (behavioural-timescale plasticity), giving one-shot learning. | Bittner et al. 2017, *Science* | BTSP model → cannot form a place map in one lap | T1 | open |
| H029 | The hippocampus learns a successor representation (expected future states) by TD. That map transfers when rewards change. | Dayan 1993, *Neural Comput*; Stachenfeld et al. 2017, *Nat Neurosci* | SR agent vs model-free agent on reward revaluation → no transfer advantage | T1 | open |
| H030 | Learning progress (how fast prediction error falls) is the intrinsic reward that drives a self-made curriculum. | Oudeyer et al. 2007, *IEEE Trans Evol Comput*; Schmidhuber 1991 | Learning-progress agent vs random exploration → same final competence | T1 | open |
| H031 | Replay is prioritised by how useful it is for future choices, which makes replay a form of planning. | Mattar & Daw 2018, *Nat Neurosci* | Prioritised vs random replay in Brain World → same sample efficiency | T1 | open |
| H032 | Reward-modulated STDP plus slow dopamine solves the distal-reward problem in spiking nets. | Izhikevich 2007, *Cereb Cortex* | R-STDP spiking net → fails at delays over 1 s | T1 | open |
| H033 | Habits come from an action-prediction error (repeat what you did), separate from value. | Miller, Shenhav & Ludvig 2019, *Psychol Rev* | Habit-plus-value model → no better fit to devaluation data | T1/T2 | open |
| H034 | The basal ganglia learn by RL **when** to gate information into prefrontal working memory. Learning to gate is learning to abstract. | O'Reilly & Frank 2006, *Neural Comput* | PBWM-style gating vs plain RNN on a hierarchical rule task → no gain | T1 | open |
| H035 | Learning rate tracks environmental volatility. The brain estimates volatility and learns faster when the world changes. | Behrens et al. 2007, *Nat Neurosci* | Volatility-tracking learner vs fixed rate on a switching bandit → no gain | T1 | open |
| H036 | Each synapse keeps an uncertainty estimate and changes more when it is unsure (plasticity as Bayesian inference). | Aitchison et al. 2021, *Nat Neurosci* | Bayesian-synapse net vs plain SGD → no gain in data efficiency | T1 | open |
| H037 | Acetylcholine switches the hippocampus between encoding (high ACh) and retrieval (low ACh) to avoid interference. | Hasselmo 2006, *Curr Opin Neurobiol* | Model with an ACh switch vs without → no less interference | T1 | open |
| H038 | Infants and adults use different neuromodulator balances, which changes exploration vs exploitation across a lifetime. | **new** | Agent with a lifetime schedule vs a constant one → no gain on lifelong tasks | T1 | open |

## C. Self-supervised objectives: cortex learns a world model
| ID | Hypothesis | Source | Test → counts against it if | Tier | Status |
|---|---|---|---|---|---|
| H039 | Cortex learns by minimising sensory prediction error, with higher areas predicting lower ones. | Rao & Ballard 1999, *Nat Neurosci* | Hierarchical PC on natural images → no extra-classical receptive fields | T1 | open |
| H040 | All learning and action minimise one quantity, variational free energy. | Friston 2010, *Nat Rev Neurosci* | (Hard to falsify as stated.) Pick a specific active-inference agent vs RL in Brain World → worse on every metric | T1 | open |
| H041 | Sensory cortex is tuned to predict the near future of its input. | Singer et al. 2018, *eLife*; Lotter et al. 2017, ICLR | Temporal-prediction model vs non-predictive model → worse fit to V1 receptive fields | T1/T2 | open |
| H042 | Invariant features (objects, not pixels) come from preferring signals that change slowly. | Wiskott & Sejnowski 2002, *Neural Comput* | SFA on a moving-object stream → no position-invariant units | T1 | open |
| H043 | Local, layer-wise contrastive prediction (contrast future with unrelated input) can train deep representations. | Illing et al. 2021, NeurIPS | Local CPC vs backprop CPC → large gap on linear probe | T1 | open |
| H044 | Cortex predicts in an abstract embedding space, not in pixels (joint-embedding prediction). | LeCun 2022, OpenReview position paper | JEPA-like local model vs pixel prediction → no better transfer | T1 | open |
| H045 | Neurons learn a sparse code: few active units, each standing for an independent cause. | Olshausen & Field 1996, *Nature* | Sparse coding on Brain World observations → no reuse across layouts | T1 | open |
| H046 | Learning removes redundancy, so each neuron carries non-overlapping information. | Barlow 1961 (*Sensory Communication*); Bell & Sejnowski 1995, *Neural Comput* | Infomax/ICA features → no better downstream learning than PCA | T1 | open |
| H047 | Hebbian plus anti-Hebbian rules follow from a "similarity matching" objective (keep similar inputs similar). | Pehlevan, Hu & Chklovskii 2015, *Neural Comput* | Derived network → fails to find the principal subspace online | T1 | open |
| H048 | Every cortical column learns whole objects in its own reference frame, and columns vote (thousand brains). | Hawkins et al. 2019, *Front Neural Circuits* | Column-voting model → no gain over one big model on object recognition from touches | T1 | open |
| H049 | Dendritic segments let neurons predict sequences: a distal match puts a cell in a "predicted" state (HTM). | Hawkins & Ahmad 2016, *Front Neural Circuits* | Sequence-memory model vs LSTM on noisy sequences → worse with equal parameters | T1 | open |
| H050 | Learning comes from the sensory results of one's own movements (sensorimotor contingencies). | O'Regan & Noë 2001, *Behav Brain Sci* | Active learner vs passive learner seeing the same frames → same representation | T1 | open |
| H051 | Two senses supervise each other: agreement across modalities stands in for labels. | de Sa 1994, NeurIPS | Two-modality self-supervision → no better than one modality | T1 | open |
| H052 | Lateral inhibition plus Hebbian learning, with no feedback at all, is enough to learn deep features. | Krotov & Hopfield 2019, *PNAS*; Journé et al. 2023, ICLR (SoftHebb) | SoftHebb vs backprop on CIFAR-10 → gap does not close with depth | T1 | open |
| H053 | Spiking STDP with winner-take-all and homeostasis learns digit prototypes without labels. | Diehl & Cook 2015, *Front Comput Neurosci* | (Already shown for MNIST.) Brain World observations → prototypes do not transfer | T1 | open |
| H054 | Prediction errors are only computed where the brain cares (precision-weighted by attention), so most input causes no learning. | Friston 2010; Feldman & Friston 2010, *Front Hum Neurosci* | Precision-weighted PC vs unweighted PC → no sample saving | T1 | open |

## D. Structure, maps and abstraction
| ID | Hypothesis | Source | Test → counts against it if | Tier | Status |
|---|---|---|---|---|---|
| H055 | The hippocampal-entorhinal system splits structure (grid-like) from content (sensory). The structure code is reused on new problems. | Whittington et al. 2020, *Cell* (Tolman-Eichenbaum Machine) | TEM-like model in Brain World → no zero-shot inference on new layouts | T1 | open |
| H056 | Cognitive maps are a general format for any knowledge (social, conceptual), not only space. | Behrens et al. 2018, *Neuron* | Same map model on a non-spatial graph task → no transfer | T1/T2 | open |
| H057 | Humans use grid-like codes to move through abstract concept spaces. | Constantinescu, O'Reilly & Behrens 2016, *Science* | Reanalysis of open fMRI → no hexagonal modulation | T2 | open |
| H058 | An abstraction is a geometry: variables coded along shared directions, so a decoder trained in one context works in another. | Bernardi et al. 2020, *Cell* | Measure cross-condition generalisation in trained Brain World agents → no link to transfer | T1 | open |
| H059 | Mixed selectivity (neurons tuned to combinations) gives a high-dimensional code that any rule can read out linearly. | Rigotti et al. 2013, *Nature* | Random mixed layer vs pure-selectivity layer → no readout gain | T1 | open |
| H060 | Variables are bound to roles by vector operations (circular convolution or XOR), which gives compositional symbols. | Plate 1995, *IEEE Trans Neural Netw*; Kanerva 2009, *Cogn Comput* | HDC binding learnt by local rules → cannot represent new role-filler pairs | T1 | open |
| H061 | Features that belong together are bound by firing in synchrony. | Singer 1999, *Neuron* | Synchrony-binding model → no gain on a binding task over rate code | T1/T3 | open |
| H062 | Biological constraints (non-negative rates, energy cost) push networks to learn disentangled factors. | Whittington et al. 2023, ICLR | Net with these constraints vs without → no more disentanglement | T1 | open |
| H063 | Prior schemas in medial PFC let new related facts be consolidated in a day instead of weeks. | Tse et al. 2007, *Science* | Model with schema vs without → same consolidation speed | T1 | open |
| H064 | Abstraction is extracted slowly by cortex from many hippocampal replays of specific episodes (complementary learning systems). | McClelland, McNaughton & O'Reilly 1995, *Psychol Rev*; Kumaran et al. 2016, *Trends Cogn Sci* | Fast+slow system vs one system → no better generalisation | T1 | open |
| H065 | Replay recombines pieces of past episodes into new sequences, which is compositional computation. | Kurth-Nelson et al. 2023, *Neuron* | Recombining replay vs faithful replay → no gain on new combinations | T1 | open |
| H066 | Successor features split "what the world does" from "what I want", so skills transfer to new goals at once. | Barreto et al. 2017, NeurIPS | SF agent vs model-free on new rewards in Brain World → no zero-shot gain | T1 | open |
| H067 | The basal ganglia chunk action sequences into units that are reused like words. | Graybiel 1998, *Neurobiol Learn Mem* | Chunking agent vs flat agent on tasks sharing subsequences → no speed-up | T1 | open |
| H068 | Frontal cortex is a front-to-back hierarchy of increasingly abstract rules. | Badre & D'Esposito 2009, *Nat Rev Neurosci* | Hierarchical-rule model vs flat model on nested rules → same learning curve | T1/T2 | open |
| H069 | Tasks are implemented by low-rank structure in recurrent weights, and abstraction means reusing the same low-rank parts. | Mastrogiuseppe & Ostojic 2018, *Neuron* | Low-rank RNN vs full-rank RNN on task families → no reuse | T1 | open |
| H070 | Networks trained on many tasks reuse shared dynamical motifs (compositional task representations). | Yang et al. 2019, *Nat Neurosci*; Driscoll, Shenoy & Sussillo 2024, *Nat Neurosci* | Motif analysis of a local-rule multitask net → no shared motifs | T1 | open |
| H071 | The brain abstracts by compression: it prefers the simplest description of its data. | Chater & Vitányi 2003, *Trends Cogn Sci* | MDL-penalised learner vs plain learner → no better transfer | T1 | open |
| H072 | Analogy is mapping one structure onto another by matching relations, not features. | Gentner 1983, *Cogn Sci* | Structure-mapping model in Brain World → no transfer on surface-different layouts | T1 | open |
| H073 | Concept cells are sparse, invariant abstract codes built by learning, not innate detectors. | Quian Quiroga et al. 2005, *Nature* | Sparse local-rule net → no invariant "concept units" | T1/T3 | open |
| H074 | Time cells give an abstract time axis, reused for any sequence. | Eichenbaum 2014, *Nat Rev Neurosci*; Howard & Kahana 2002, *J Math Psychol* | Temporal-context model vs fixed delay lines → no sequence transfer | T1 | open |
| H075 | People infer hidden task states (latent causes) and cluster them, then reuse a whole cluster's policy. | Collins & Frank 2013, *Psychol Rev*; Gershman & Niv 2010, *Curr Opin Neurobiol* | Latent-cause agent in Brain World → no faster relearning of returning layouts (links to #57/#60) | T1 | open |
| H076 | The brain chooses among structural forms (tree, ring, grid) to organise knowledge. | Kemp & Tenenbaum 2008, *PNAS* | Form-discovery model vs fixed form → same fit to category data | T1 | open |
| H077 | Separating contexts into orthogonal subspaces lets one network do many tasks without interference. | Flesch et al. 2022, *Neuron*; Zeng et al. 2019, *Nat Mach Intell* | Orthogonalising rule vs plain rule → same forgetting | T1 | open |
| H078 | Cell assemblies that fire together, and project and merge, are the brain's unit of computation (assembly calculus). | Papadimitriou et al. 2020, *PNAS*; Buzsáki 2010, *Neuron* | Assembly-calculus model → cannot parse a small grammar | T1 | open |
| H079 | Abstraction needs variety: it forms only if structure stays fixed while surface details keep changing. | **new** | Brain World with low vs high surface variety → no difference in transfer | T1 | open |
| H080 | Representations first expand (high dimension, to learn) and then compress (low dimension, to generalise) during learning. | **new** | Track participation ratio during training → no expand-then-compress pattern | T1 | open |

## E. Innate priors and development
| ID | Hypothesis | Source | Test → counts against it if | Tier | Status |
|---|---|---|---|---|---|
| H081 | The genome cannot store synapses, so it stores compact wiring and learning rules. That bottleneck itself forces generalisation. | Zador 2019, *Nat Commun* | Compress a trained net's wiring into rules → no better transfer than the uncompressed net | T1 | open |
| H082 | Spontaneous activity (retinal waves) pre-trains sensory maps before birth. | Katz & Shatz 1996, *Science* | Pre-train on synthetic waves → no speed-up on later tasks | T1 | open |
| H083 | Starting with limited memory or perception helps learning ("less is more", "starting small"). | Newport 1990, *Cogn Sci*; Elman 1993, *Cognition* | Growing-capacity vs full-capacity learner → same or better at full capacity | T1 | open |
| H084 | Infants start with core knowledge systems (objects, agents, number, space, geometry) that learning builds on. | Spelke & Kinzler 2007, *Dev Sci* | Agent with object/agent priors vs without in Brain World → no sample saving | T1 | open |
| H085 | Critical periods are a learning-rate schedule: high plasticity early, locked down later. | Hensch 2005, *Nat Rev Neurosci* | Decaying vs constant plasticity → no stability gain | T1 | open |
| H086 | Blurry early vision is a feature: it forces learning of large-scale configural features. | Vogelsang et al. 2018, *PNAS* | Train with a blur-then-sharp schedule vs sharp only → no robustness gain | T1 | open |
| H087 | Architecture alone already carries strong priors, before any learning. | Ulyanov et al. 2018, CVPR; Gaier & Ha 2019, NeurIPS | Untrained connectome-like net vs random net → no difference in readout performance | T1 | open |
| H088 | Pruning many synapses early, at a falling rate, gives efficient and robust networks. | Navlakha, Barth & Bar-Joseph 2015, *PLoS Comput Biol* | Prune schedules in a local-rule net → no robustness gain | T1 | open |
| H089 | Babies make their own curriculum by what they look at and handle (egocentric, embodied data). | Smith & Gasser 2005, *Artif Life*; Orhan, Gupta & Lake 2020, NeurIPS | Self-supervised learning on a child's headcam (SAYCam) → no useful categories | T2 | open |
| H090 | There is no special algorithm: the brain "direct-fits" a huge, over-parameterised model to a lifetime of dense embodied data, just like deep nets. | Hasson, Nastase & Goldstein 2020, *Neuron* | Matched-data comparison (BabyLM) → models still need far more data than children | T2 | open |
| H091 | Evolution was the outer loop: it meta-learned the plasticity rules that a lifetime then uses. | Confavreux et al. 2020, NeurIPS; Najarro & Risi 2020, NeurIPS | Meta-learn rules in Brain World → evolved rules no better than Hebb/Oja | T1 | open |
| H092 | Plasticity itself is plastic: each synapse has a learnable plasticity coefficient (differentiable plasticity). | Miconi, Clune & Stanley 2018, ICML; Miconi et al. 2019, ICLR | Plastic-plasticity net vs fixed rule → no gain on new tasks | T1 | open |

## F. Memory, consolidation and forgetting
| ID | Hypothesis | Source | Test → counts against it if | Tier | Status |
|---|---|---|---|---|---|
| H093 | Replaying generated (not stored) past experience prevents forgetting. | van de Ven, Siegelmann & Tolias 2020, *Nat Commun*; Shin et al. 2017, NeurIPS | Generative vs exact replay vs none on split tasks → no protection | T1 | open |
| H094 | Sleep scales all synapses down, which keeps the strongest ones and improves signal-to-noise. | Tononi & Cirelli 2014, *Neuron* | Downscaling step vs none → no less forgetting (issue #84) | T1 | open |
| H095 | Only synapses "tagged" by an important event capture the proteins needed for long-term change. | Frey & Morris 1997, *Nature* | Tag-and-capture model vs plain rule → no selective retention | T1 | open |
| H096 | Synapses have hidden internal states with many timescales, which balance learning and forgetting. | Fusi, Drew & Abbott 2005, *Neuron*; Benna & Fusi 2016, *Nat Neurosci* | Cascade synapse vs simple synapse → same memory lifetime | T1 | open |
| H097 | Synapses estimate their own importance and resist change in proportion. | Kirkpatrick et al. 2017, *PNAS*; Zenke, Poole & Ganguli 2017, ICML | Local importance estimate vs EWC with a Fisher matrix → much worse | T1 | open |
| H098 | Retrieving a memory makes it changeable again (reconsolidation), which lets old knowledge be updated. | Nader, Schafe & LeDoux 2000, *Nature* | Retrieve-then-update model vs append-only → no better adaptation | T1 | open |
| H099 | The hippocampus works like attention over stored patterns (a modern Hopfield network ≈ transformer attention). | Ramsauer et al. 2021, ICLR; Whittington, Warren & Behrens 2022, ICLR | Hopfield-memory agent → no one-shot recall advantage | T1 | open |
| H100 | Fast weights give short-term binding: a second, fast-decaying weight set stores recent context. | Ba et al. 2016, NeurIPS | Fast-weight net vs plain RNN on associative recall → no gain | T1 | open |
| H101 | **Main transfer experiment.** With equal parameters, a local rule plus replay reaches backprop's transfer to new Brain World layouts that share structure but differ on the surface. | **new** | Episodes to criterion on a new layout: local+replay stays far behind backprop | T1 | open |
| H102 | Working memory can be silent: it is held in short-term synaptic changes, not firing. | Mongillo, Barak & Tsodyks 2008, *Science* | Silent-memory model → cannot hold items across a distractor | T1/T3 | open |
| H103 | A built-in structural prior closes more of the transfer gap than a better learning rule does. | **new** (links to Zador 2019 and issue #83) | Prior vs better rule at equal compute → the rule wins | T1 | open |
| H104 | Replay that overlaps several episodes builds schemas (what episodes share). | Lewis & Durrant 2011, *Trends Cogn Sci* | Overlapping vs single-episode replay → no schema transfer | T1 | open |
| H105 | Sleep produces insight: hidden rules are found after sleep, not after the same time awake. | Wagner et al. 2004, *Nature* | Model with an offline replay phase → no rule discovery advantage | T1 | open |
| H106 | Adult-born neurons help keep similar memories apart (pattern separation). | Sahay et al. 2011, *Nature* | Add-new-units model vs fixed units → no less interference | T1 | open |
| H107 | A sparse random expansion (fly mushroom body) makes one-shot learning and similarity search easy. | Dasgupta, Stevens & Navlakha 2017, *Science* | Random-expansion layer vs dense layer → no one-shot gain | T1 | open |
| H108 | Context switches on a different subset of neurons per task, which stops interference. | Masse, Grant & Freedman 2018, *PNAS*; Iyer et al. 2022, *Front Neurorobot* | Context gating vs none on many tasks → same forgetting | T1 | open |

## G. Language and reasoning
| ID | Hypothesis | Source | Test → counts against it if | Tier | Status |
|---|---|---|---|---|---|
| H109 | Infants find words by tracking transition probabilities between syllables (statistical learning). | Saffran, Aslin & Newport 1996, *Science* | Local Hebbian sequence learner → cannot segment a syllable stream | T1 | open |
| H110 | The language network is a next-word predictor, like LLMs. | Schrimpf et al. 2021, *PNAS*; Goldstein et al. 2022, *Nat Neurosci* | Reanalysis of Narratives fMRI: prediction-free features fit as well (issue #89) | T2 | open |
| H111 | The brain predicts at many timescales at once (words, phrases, ideas), not just the next word. | Caucheteux, Gramfort & King 2023, *Nat Hum Behav* | Multi-horizon vs next-word model features → no better brain fit | T2 | open |
| H112 | Language is mainly a tool for communication. Reasoning is done elsewhere and does not need language. | Fedorenko, Piantadosi & Gibson 2024, *Nature* | (Tier 3 for the claim itself.) Agent with reasoning but no language module → fails reasoning tasks | T1/T3 | open |
| H113 | Social interaction gates language learning: babies learn speech sounds from a live person, not from video. | Kuhl, Tsao & Liu 2003, *PNAS* | Agent with a social-attention gate vs none → no learning difference | T1/T3 | open |
| H114 | Humans have an innate operation (Merge) that builds hierarchical structure, and learning cannot replace it. | Berwick & Chomsky 2016, *Why Only Us* | Local learner with no Merge prior → learns hierarchical generalisation anyway | T1 | open |
| H115 | Humans compress sequences into nested patterns (a "language of thought" for sequences); other primates do not. | Dehaene et al. 2015, *Neuron*; Dehaene et al. 2022, *Trends Cogn Sci* | Sequence-compression model → no better fit to human sequence-learning data | T2 | open |
| H116 | Concepts are learned as small programs from few examples (Bayesian program learning). | Lake, Salakhutdinov & Tenenbaum 2015, *Science* | BPL-like learner vs a neural learner on Omniglot one-shot → no gain | T1 | open |
| H117 | Learning is Bayesian inference over structured hypotheses, so a few examples are enough. | Tenenbaum et al. 2011, *Science* | Bayesian concept learner vs neural learner on few-shot generalisation → same | T1 | open |
| H118 | Reasoning about the physical world is mental simulation with an internal physics engine. | Battaglia, Hamrick & Tenenbaum 2013, *PNAS* | Simulation agent vs pattern-match agent on new physical scenes → no gain | T1 | open |
| H119 | Inner speech scaffolds reasoning: talking to yourself chains steps together. | Alderson-Day & Fernyhough 2015, *Psychol Bull* | Agent with an internal symbol loop vs without on multi-step tasks → no gain | T1 | open |
| H120 | Words speed up abstraction: a shared label pulls different examples together (label-feedback). | Lupyan 2012, *Front Psychol* | Learner with labels vs without on category transfer → no gain | T1 | open |
| H121 | Analogy needs explicit relational binding (role and filler kept separate), done by timing. | Hummel & Holyoak 1997, *Psychol Rev*; Doumas, Hummel & Sandhofer 2008, *Psychol Rev* | LISA/DORA-like model vs plain net on analogy → same | T1 | open |
| H122 | What makes humans different is the ability to reason about relations between relations (relational reinterpretation). | Penn, Holyoak & Povinelli 2008, *Behav Brain Sci* | (Mostly T3.) Model without higher-order relations → still solves relational match-to-sample | T1/T3 | open |
| H123 | Rostrolateral PFC integrates relations for analogy. | Bunge et al. 2005, *Cereb Cortex* | Reanalysis of open analogy fMRI → no relational-integration effect | T2 | open |
| H124 | A global workspace broadcasts one content to many modules, letting them be combined flexibly. | Dehaene, Kerszberg & Changeux 1998, *PNAS* | Workspace architecture vs fully modular one → no gain on new combinations | T1 | open |
| H125 | The cerebellum learns internal models of thoughts as well as movements, making familiar reasoning automatic. | Ito 2008, *Nat Rev Neurosci* | Agent with a cerebellum-like forward model of its own reasoning → no speed-up | T1 | open |
| H126 | Abstraction is mostly learned from other people (culture and teaching), not invented alone. | Tomasello 1999, *The Cultural Origins of Human Cognition* | Agents taught by another agent vs alone → same abstraction | T1 | open |
| H127 | Learners assume a teacher picks examples to be helpful, and learn more from each one. | Shafto, Goodman & Griffiths 2014, *Cogn Psychol* | Pedagogical vs random examples → no data saving | T1 | open |
| H128 | Shared symbols emerge when two agents with local rules must cooperate through a narrow channel. | Lazaridou & Baroni 2020, arXiv:2006.02419 | Two Brain World agents with a message channel → no stable, compositional code | T1 | open |
| H129 | Systematic compositional generalisation comes from meta-learning over many small tasks. | Lake & Baroni 2023, *Nature* | Meta-learned local-rule net → fails systematic generalisation | T1 | open |
| H130 | The bursty, Zipf-like statistics of natural input are what make in-context learning emerge. | Chan et al. 2022, NeurIPS | Train on bursty vs uniform input → same in-context learning | T1 | open |

## H. Scale, neurons and dendrites
| ID | Hypothesis | Source | Test → counts against it if | Tier | Status |
|---|---|---|---|---|---|
| H131 | Humans differ mainly by having more cortical neurons, not by a different algorithm. | Herculano-Houzel 2009, *Front Hum Neurosci* | Scaling a local-rule model → abstraction does not appear with size | T1/T2 | open |
| H132 | Human dendrites are more compartmentalised, which gives each neuron more independent computing units. | Beaulieu-Laroche et al. 2018, *Cell* | Compartmentalised vs lumped neuron model (#85) → same capacity | T1 | open |
| H133 | Human cortical dendrites can compute XOR on their own. | Gidon et al. 2020, *Science* | Dendritic-XOR neuron net vs point-neuron net → no capacity gain | T1 | open |
| H134 | A single cortical neuron is as powerful as a 5-8 layer deep net. | Beniaguev, Segev & London 2021, *Neuron* | Fit-a-neuron replication → a shallow net does as well | T1 | open |
| H135 | Each dendritic branch is a separate learning unit (two-layer neuron). | Poirazi, Brannon & Mel 2003, *Neuron* | Branch-local plasticity vs neuron-global → no storage gain | T1 | open |
| H136 | Learning is confined to the existing low-dimensional manifold of activity. New patterns are hard to learn. | Sadtler et al. 2014, *Nature* | Model learns on- and off-manifold perturbations equally fast | T1/T2 | open |
| H137 | Synapses are the real budget: more synapses per neuron matters more than more neurons. | **new** | Equal-synapse vs equal-neuron scaling in a local-rule net → neurons matter more | T1 | open |

## I. Dynamics and alternative computing primitives
| ID | Hypothesis | Source | Test → counts against it if | Tier | Status |
|---|---|---|---|---|---|
| H138 | Most circuits are fixed random reservoirs. Only readouts learn. | Jaeger 2001 (GMD report 148); Maass, Natschläger & Markram 2002, *Neural Comput* | Reservoir + local readout vs fully plastic net in Brain World → reservoir falls clearly short of it | T1 | open |
| H139 | Feedback from the output, with fast local learning, can tame chaotic recurrent activity into a task (FORCE). | Sussillo & Abbott 2009, *Neuron* | Local FORCE-like rule → cannot learn a motor pattern | T1 | open |
| H140 | Memories and categories are attractors in a recurrent network. | Hopfield 1982, *PNAS* | Attractor net on Brain World states → no category formation | T1 | open |
| H141 | The theta cycle splits time into encoding and retrieval phases, so learning and recall do not interfere. | Hasselmo, Bodelón & Wyble 2002, *Neural Comput* | Phase-split model vs unsplit → same interference | T1 | open |
| H142 | Theta sequences compress behaviour into short bursts that STDP can learn from. | Skaggs et al. 1996, *Hippocampus* | Model with phase precession vs without → no sequence learning gain | T1 | open |
| H143 | The brain runs near criticality, which maximises information transmission and learning. | Beggs & Plenz 2003, *J Neurosci* | Tune a model's gain → learning not best near critical point | T1 | open |
| H144 | Neural variability is sampling from a probability distribution, which supports Bayesian learning. | Fiser et al. 2010, *Trends Cogn Sci*; Kappel et al. 2015, *PLoS Comput Biol* | Sampling net vs deterministic net → no better uncertainty or learning | T1 | open |
| H145 | Inhibitory plasticity keeps excitation and inhibition balanced, which lets excitatory learning stay stable. | Vogels et al. 2011, *Science* | Model without inhibitory plasticity → learns as well and stays stable | T1 | open |
| H146 | Homeostatic synaptic scaling keeps firing rates in range so Hebbian learning does not run away. | Turrigiano et al. 1998, *Nature* | Hebbian net without scaling → stays stable | T1 | open |
| H147 | A sliding threshold (BCM) decides when activity strengthens or weakens a synapse. | Bienenstock, Cooper & Munro 1982, *J Neurosci* | BCM vs Oja on Brain World input → no selectivity difference | T1 | open |
| H148 | Astrocytes add a slow, many-synapse memory and could make attention-like computation. | Kozachkov et al. 2023, *PNAS* | Neuron-astrocyte model → no memory capacity gain | T1 | open |
| H149 | Growing and removing synapses (structural plasticity) stores long-term memories. | Holtmaat & Svoboda 2009, *Nat Rev Neurosci* | Rewiring model vs weight-only model → no capacity gain | T1 | open |
| H150 | Activity-dependent myelination tunes timing between areas, a form of learning. | Fields 2015, *Nat Rev Neurosci* | Delay-learning model vs fixed delays on a timing task → no gain | T1 | open |
| H151 | Synaptic transmission failures act like dropout and stop overfitting. | **new** | Net with random transmission failure vs without → no generalisation gain | T1 | open |

## J. Control, attention and meta-learning
| ID | Hypothesis | Source | Test → counts against it if | Tier | Status |
|---|---|---|---|---|---|
| H152 | PFC holds the current goal and rule and biases other areas toward it (top-down control). | Miller & Cohen 2001, *Annu Rev Neurosci* | Agent with a goal-bias module vs without on rule switching → no gain | T1 | open |
| H153 | The thalamus switches cortical connectivity for the current context. | Schmitt et al. 2017, *Nature* | Thalamic-gating model vs none on a context task → no gain | T1 | open |
| H154 | Top-down input to apical dendrites gates which feedforward inputs can drive learning. | Larkum 2013, *Trends Neurosci* | Apical-gated model vs plain → no multitask gain | T1 | open |
| H155 | Behaviour is organised as hierarchical options (sub-skills) learned by RL. | Botvinick, Niv & Barto 2009, *Cognition* | Options agent vs flat agent in Brain World → no speed-up | T1 | open |
| H156 | Agents act to reduce uncertainty, not only to get reward (epistemic value). | Friston et al. 2015, *Cogn Neurosci* | Epistemic agent vs reward-only agent → no faster structure learning | T1 | open |
| H157 | The brain combines cues as a Bayesian observer, weighting each by its reliability. | Knill & Pouget 2004, *Trends Neurosci* | (Supported for perception.) Local-rule net → cannot learn reliability weighting | T1 | open |
| H158 | Divisive normalisation is a canonical computation that makes learning invariant to scale. | Carandini & Heeger 2012, *Nat Rev Neurosci* | Net with normalisation vs without → no learning gain | T1 | open |
| H159 | The canonical cortical microcircuit implements predictive coding in its layers. | Bastos et al. 2012, *Neuron* | Laminar recordings: prediction and error not in separate layers (T2 with Allen data) | T2 | open |
| H160 | Supervised learning happens in the cerebellum, with climbing fibres carrying the error. | Marr 1969, *J Physiol*; Albus 1971, *Math Biosci*; Raymond & Medina 2018, *Annu Rev Neurosci* | Cerebellar model in Brain World → no motor error correction | T1 | open |
| H161 | Humans represent tasks on a successor-like predictive map, measured in behaviour. | Momennejad et al. 2017, *Nat Hum Behav* | Model comparison on open revaluation data → model-based fits as well | T2 | open |

## K. Combinations and new ideas from this thread
| ID | Hypothesis | Source | Test → counts against it if | Tier | Status |
|---|---|---|---|---|---|
| H162 | A small set of rule types (Hebbian, anti-Hebbian, three-factor, homeostatic), switched by neuromodulators, is enough for everything. | **new** | Model with these four plus switching fails a task that backprop solves at equal size | T1 | open |
| H163 | Two timescales of weights (fast and slow) are necessary for in-context abstraction. | **new** | Single-timescale net matches the two-timescale net on in-context tasks | T1 | open |
| H164 | Local rules are enough for features. Abstraction needs only one extra piece: replay that recombines. | **new** | Local rule + recombining replay still fails transfer (H101) | T1 | open |
| H165 | k-WTA sparsity improves abstraction, not only efficiency. | **new** (links to issue #82) | Sparse vs dense at equal parameters → same transfer | T1 | open |
| H166 | The gap between local rules and backprop shrinks with network width, so scale hides the rule's weakness. | **new** | FA/PC gap vs width → gap does not shrink | T1 | open |
| H167 | Prediction errors from the world model, used as curiosity, give the agent the varied data that abstraction needs (links H030, H079). | **new** | Curious vs random explorer → same surface variety and same transfer | T1 | open |
| H168 | Abstraction emerges in activity first (in-context) and is then consolidated into weights during sleep. | **new** (links H027, H064) | Block consolidation → in-context abstraction still becomes permanent | T1 | open |
| H169 | A learning rule's quality can be measured by how well it transfers, not only by its accuracy, and the ranking of rules differs between the two. | **new** | Rank rules by accuracy and by transfer → same order | T1 | open |
| H170 | No single row above explains abstraction alone. Removing any one of: local credit assignment, replay, structural priors, or meta-learned neuromodulation drops transfer sharply. | **new** | Ablation of each piece in the H101 setup → at least one ablation has no effect | T1 | open |

---

## Log
One line per result. Newest at the bottom.

| Date | ID | Result | Where recorded |
|---|---|---|---|
| 2026-10-12 | - | File created with 170 hypotheses. All `open`. Sources from memory, not yet verified. | this file |
