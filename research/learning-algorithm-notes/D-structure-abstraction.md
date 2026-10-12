# Paper notes: D. Structure, maps and abstraction

Structured notes on the 31 sources cited by hypotheses H055-H080 in `research/learning-algorithm-hypotheses.md`, generated 2026-10-12 from local PDFs (4), web full text (9) and abstracts in `sources.json` (18). Every figure comes from the text read; abstract-only notes are deliberately thin. H079 and H080 cite no source ("new") and have no note. Where only an abstract was available the "Bearing" line judges the abstract, not the full paper.

## Whittington 2020: The Tolman-Eichenbaum Machine
- **Cited for:** H055 (hippocampal-entorhinal system splits structure from content; structure code is reused on new problems)
- **Link:** https://doi.org/10.1016/j.cell.2020.10.024 · **Basis:** full text (web, first ~100k characters of PMC text)
- **Question:** Can one model explain spatial and relational memory by separating a reusable structural code from sensory content, and does it predict hippocampal remapping?
- **Method / model:** g (medial entorhinal analogue) is a recurrent network with learned action-dependent transition weights that path-integrates position on a graph. x (lateral entorhinal analogue) is temporally filtered sensory input. p (hippocampal analogue) is a conjunction of g and x stored in fast Hebbian weights and retrieved by attractor dynamics. Slow weights are trained by backpropagation through time in a generative/inference (wake-sleep-like) framework; Hebbian memories reset in each new environment.
- **Experiments:** Transitive inference on lines of 4-6 states; family-tree hierarchies (15 or 31 states); 2D square (64-121 nodes) and hexagonal (61-127 nodes) graphs; a 4-lap task with reward every fourth lap. Remapping data re-analysed from Barry et al. 2012 (7 rats, two 1 m x 1 m environments) and Chen et al. 2018 (4 mice, 60 cm arenas, real and VR).
- **Key results:**
  - g cells developed grid, band, border and object-vector properties depending on training transition statistics; p cells developed place and landmark properties and remapped.
  - TEM made first-presentation inferences in new environments (loop closure, transitive relations).
  - Place-grid relationships were preserved across remapping: r = 0.322 for 115 conservative pairs (p < 0.01) in Barry data; TEM r about 0.31. Chen data: r = 0.273 for 64 pairs (p < 0.05).
- **Limitations / caveats:** Authors say it is computational, not biophysical. Sensory stimuli were random with no spatial correlations; only noise-free inputs. Entorhinal predictions for the 4-lap task are untested.
- **Bearing on H055:** Supports. Structure-vs-content split and reuse across environments are the paper's core claim, with the remapping data as partial confirmation.
- **Reproduce in this repo:** Small TEM-like agent (learned transition matrices over g, Hebbian x-g memory) on random graphs; test zero-shot prediction of unseen edges on a new layout with the same structure.

## Behrens 2018: What is a cognitive map?
- **Cited for:** H056 (cognitive maps are a general format for any knowledge, not only space)
- **Link:** https://doi.org/10.1016/j.neuron.2018.10.002 · **Basis:** abstract only
- **Question:** Do map-like codes seen in spatial navigation reflect general principles for organising abstract, generalisable knowledge?
- **Method / model:** Review of experimental evidence and theory; discusses artificial agents that learn map-like representations.
- **Experiments:** None of its own (abstract only; no details read).
- **Key results:** Abstract states that spatial map-like representations "may be an instance of general coding mechanisms capable of organizing knowledge of all kinds"; it also says the authors "speculate" about extreme generalisation in human cognition.
- **Limitations / caveats:** Review; the claim is framed as a proposal.
- **Bearing on H056:** Partly supports. It proposes the general-format view but as a review-level hypothesis, not a demonstrated fact.
- **Reproduce in this repo:** Same map model (e.g. TEM-like) on a non-spatial graph such as a social hierarchy; test transfer to a new graph with the same structure.

## Constantinescu 2016: Organizing conceptual knowledge in humans with a gridlike code
- **Cited for:** H057 (humans use grid-like codes in abstract concept spaces)
- **Link:** https://doi.org/10.1126/science.aaf0941 · **Basis:** full text (web)
- **Question:** Does fMRI show hexagonally symmetric (grid-like) modulation when people navigate a 2D conceptual space?
- **Method / model:** fMRI test for six-fold symmetry in direction theta (sin(6 theta), cos(6 theta) regressors); grid angle estimated on one session and tested on another via cos(6[theta - phi]).
- **Experiments:** 28 subjects learned a 2D "bird space" (neck and leg length) with outcome symbols; 2-4 fMRI sessions over two days at least a week apart; behavioural accuracy 72.8 +/- 1.0%.
- **Key results:**
  - Hexagonal modulation in entorhinal (Z = 4.41), vmPFC (Z = 4.09), retrosplenial (Z = 4.73), lateral parietal (Z = 4.96) and other regions (quadrature test used only to define ROIs).
  - Cross-validated consistency within a day: vmPFC t26 = 2.61, entorhinal t27 = 2.36 (both p < 0.05); across days vmPFC t20 = 3.65 (p < 0.01).
  - 4-, 5-, 7-, 8-fold control symmetries not significant (all p > 0.15).
- **Limitations / caveats:** fMRI is coarse, so no claim about single-neuron grid cells; only continuous 2D conceptual spaces tested; whether spatial and conceptual grid phases are shared is untested.
- **Bearing on H057:** Supports, for one 2D continuous concept space in a small sample. "Humans use grid-like codes to move through abstract spaces" generalises beyond what was tested.
- **Reproduce in this repo:** n/a (T2).

## Bernardi 2020: The geometry of abstraction in the hippocampus and prefrontal cortex
- **Cited for:** H058 (abstraction is a geometry; decoder trained in one context works in another)
- **Link:** https://doi.org/10.1016/j.cell.2020.09.031 · **Basis:** abstract only
- **Question:** Do neural ensembles represent task variables in a geometry that supports cross-condition generalisation?
- **Method / model:** Abstraction defined operationally as generalisation of linear decoders to conditions not used in training; "shattering dimensionality" measures how many other variables are linearly decodable.
- **Experiments:** Monkeys on a task with hidden and explicit variables; recordings in prefrontal cortex and hippocampus; simulated neural networks.
- **Key results:** PFC, hippocampus and simulated networks represent several variables in an abstract geometry while keeping high shattering dimensionality; the geometry changed with task events and performance (numbers not in abstract).
- **Limitations / caveats:** Not assessed beyond abstract.
- **Bearing on H058:** Supports. Operational definition matches the hypothesis; "no link to transfer" would be tested in agents.
- **Reproduce in this repo:** Compute cross-condition generalisation performance (train decoder on some contexts, test on held-out) and shattering dimensionality of hidden units in trained Brain World agents; correlate with transfer score.

## Rigotti 2013: The importance of mixed selectivity in complex cognitive tasks
- **Cited for:** H059 (mixed selectivity gives a high-dimensional code any rule can read out linearly)
- **Link:** https://doi.org/10.1038/nature12160 · **Basis:** full text (web)
- **Question:** What computational role does heterogeneous mixed selectivity in PFC play?
- **Method / model:** Decoding and dimensionality analyses; dimensionality d = log2(number of implementable dichotomies); toy model contrasting pure, linear-mixed and non-linear-mixed selectivity.
- **Experiments:** Two monkeys, 237 lateral PFC (area 46) neurons, object-sequence memory task with recognition/recall (24 conditions in the two-object delay); 121 neurons for error-trial analysis.
- **Key results:**
  - Each task aspect remains decodable after removing each neuron's classical selectivity; decoding grows with population size (resampled to 1,000 neurons).
  - Recorded dimensionality reaches the maximum (d = 8 for one-object, d = 24 conditions for two-object delay); a pure-selectivity population gives fewer than 8.
  - Dimensionality is about 12 on correct recall trials and drops on error trials; removing the non-linear component eliminates the drop.
- **Limitations / caveats:** Overtrained task with few conditions; toy model; Whittington 2023 (H062) argues mixed selectivity may not be general across associative cortex.
- **Bearing on H059:** Partly supports. High-dimensional mixed codes allow more linear readouts, but "any rule" overstates (advantage is for the repertoire of input-output functions of a trained task set).
- **Reproduce in this repo:** Random mixed (ReLU) layer vs identity/pure layer feeding a linear readout on all dichotomies of 3-4 binary variables; count readable dichotomies.

## Plate 1995: Holographic reduced representations
- **Cited for:** H060 (variables bound to roles by circular convolution/XOR give compositional symbols)
- **Link:** https://doi.org/10.1109/72.377968 · **Basis:** abstract only
- **Question:** How can compositional structure be held in fixed-width distributed vectors?
- **Method / model:** Circular convolution associates items; arbitrary variable bindings, short sequences and frame-like structures fit in one fixed vector; a separate associative cleanup memory repairs noisy reconstructions.
- **Experiments:** None stated in abstract.
- **Key results:** Fixed-width compositional representations are possible; retrieval is noisy and needs cleanup.
- **Limitations / caveats:** Cognitive-architecture proposal, no neural learning or brain data in abstract.
- **Bearing on H060:** Supports the binding-operation half (circular convolution). It says nothing about the brain using it or learning it by local rules. XOR binding is not in Plate.
- **Reproduce in this repo:** HRR/HDC bind-unbind of role-filler pairs with a Hebbian cleanup memory; test retrieval of a new role-filler combination.

## Kanerva 2009: Hyperdimensional computing
- **Cited for:** H060 (as above; XOR binding)
- **Link:** https://doi.org/10.1007/s12559-009-9009-8 · **Basis:** abstract only (sources.json holds no abstract; nothing can be reported)
- **Question:** not available.
- **Method / model:** not available from the supplied text.
- **Experiments:** not available.
- **Key results:** not available.
- **Limitations / caveats:** Not assessed.
- **Bearing on H060:** Does not test it from available text; unverified. Title ("introduction to computing in distributed representation with high-dimensional random vectors") is consistent with the XOR-binding attribution but could not be confirmed here.
- **Reproduce in this repo:** See Plate note (binary spatter code with XOR binding).

## Singer 1999: Neuronal synchrony: a versatile code for the definition of relations?
- **Cited for:** H061 (features that belong together are bound by synchrony)
- **Link:** https://doi.org/10.1016/s0896-6273(00)80821-1 · **Basis:** abstract only (sources.json holds no abstract; nothing can be reported)
- **Question:** not available.
- **Method / model:** not available.
- **Experiments:** not available.
- **Key results:** not available.
- **Limitations / caveats:** Not assessed; synchrony binding is known to be debated, but nothing here supports a specific statement.
- **Bearing on H061:** Does not test it from available text; unverified. The title fits the hypothesis attribution.
- **Reproduce in this repo:** Spiking or phase-coded model with synchrony-binding vs rate code on a two-object feature-binding task.

## Whittington 2023: Disentanglement with biological constraints: a theory of functional cell types
- **Cited for:** H062 (non-negative rates and energy cost push networks to disentangled factors)
- **Link:** https://doi.org/10.48550/arxiv.2210.01768 · **Basis:** full text (web, arXiv PDF)
- **Question:** Do simple biological constraints (nonnegativity, energy efficiency in activity and weights) make single neurons selective for single task factors?
- **Method / model:** Theorem 1: for a linear nonnegative representation z = M e + b of independent zero-mean factors e with fixed total variance, minimal activity energy E||z||^2 implies each neuron is selective for at most one factor. Theorem 2 extends to entangled input x = D e with a generative readout x = W z + b. Empirical tests in linear nets, deep nonlinear nets, autoencoders and VAEs.
- **Experiments:** Shallow linear nets, 5-hidden-layer nonlinear nets, linear autoencoders; VAE on a standard disentanglement benchmark (Kim & Mnih 2018 setup) plus dSprites in the appendix, scored by MIG and a mutual-information ratio; spatial-cell simulations producing grid-like and object-vector-like modules, and entangled tasks giving entangled representations and grid warping.
- **Key results:**
  - Nonnegative VAE with weight regularisation gave MIG scores competitive with or better than the beta-VAEs compared (Locatello et al. 2019), without asking for a factorised posterior; adding ReLU improves beta-VAE disentanglement too.
  - Appendix: sparsity alone (activity or weights) does not give disentanglement.
  - Entangled task factors lead to entangled representations (mixed selectivity, grid warping).
- **Limitations / caveats:** Proofs are for linear/simple settings; the authors state state-of-the-art disentanglement is not their aim; the discussion concedes they say nothing about how each factor itself is coded.
- **Bearing on H062:** Supports. Note the paper also says the effect requires factorised (independent) task factors; entangled factors give entangled codes, and it sits in tension with H059's mixed-selectivity story.
- **Reproduce in this repo:** Linear autoencoder on mixed independent factors with ReLU latent plus L2 activity/weight penalty vs unconstrained; compare fraction of single-factor neurons.

## Tse 2007: Schemas and memory consolidation
- **Cited for:** H063 (prior schemas in medial PFC let new facts be consolidated in a day instead of weeks)
- **Link:** https://doi.org/10.1126/science.1135935 · **Basis:** abstract only
- **Question:** Can systems consolidation be rapid if a schema already exists?
- **Method / model:** Rat hippocampal-dependent paired-associate (flavour-place) task; schema built gradually over training; new associations trained in one trial.
- **Experiments:** Rats; details (n, delays) not in abstract.
- **Key results:** Memory for flavour-place associations became persistent as a "putative neocortical schema" developed; one-trial new traces became assimilated and rapidly hippocampal-independent; schemas played a causal role in lasting memory.
- **Limitations / caveats:** Abstract does not name medial PFC or give a "one day" figure.
- **Bearing on H063:** Partly supports. "Rapid consolidation given a schema" matches; "medial PFC" and "a day vs weeks" are not in the abstract (unverified from it).
- **Reproduce in this repo:** Two-store model; pre-train a slow store on a structure, then compare time to hippocampus-independent recall of a new item with vs without pre-training.

## McClelland 1995: Why there are complementary learning systems
- **Cited for:** H064 (abstraction extracted slowly by cortex from many hippocampal replays)
- **Link:** https://doi.org/10.1037/0033-295x.102.3.419 · **Basis:** abstract only
- **Question:** Why does the brain have a fast hippocampal and a slow neocortical learning system?
- **Method / model:** Connectionist argument: networks discover structure only if learning is gradual and interleaved; hippocampal reinstatement interleaves new memories into cortex.
- **Experiments:** Not in abstract.
- **Key results:** Neocortex learns slowly to discover structure; hippocampus learns new items quickly without disrupting it; remote memory reflects accumulated cortical change.
- **Limitations / caveats:** Not assessed beyond abstract.
- **Bearing on H064:** Supports. Abstract states exactly this division of labour.
- **Reproduce in this repo:** Fast episodic store plus slow learner trained from replay vs a single slow learner trained online on a new layout; compare generalisation on held-out layouts.

## Kumaran 2016: What learning systems do intelligent agents need?
- **Cited for:** H064 (CLS updated)
- **Link:** https://doi.org/10.1016/j.tics.2016.05.004 · **Basis:** abstract only (sources.json holds no abstract; nothing can be reported)
- **Question / Method / Experiments / Key results:** not available.
- **Limitations / caveats:** Not assessed.
- **Bearing on H064:** Does not test it from available text; unverified.
- **Reproduce in this repo:** See McClelland note.

## Kurth-Nelson 2023: Replay and compositional computation
- **Cited for:** H065 (replay recombines pieces of past episodes into new sequences, i.e. compositional computation)
- **Link:** https://doi.org/10.1016/j.neuron.2022.12.028 · **Basis:** full text (local PDF)
- **Question:** Can replay do compositional computation by assembling role-bound entities into new statements?
- **Method / model:** Perspective/hypothesis paper. Hippocampus binds objects to generalisable roles (what/where pathways); replay strings role-bound objects into compound statements; items in a replay event need not be successive states of one transition model.
- **Experiments:** Reviews rodent replay and preplay, Sun et al. mouse four-lap task (place cells remap while lap-position codes persist), and human MEG replay: Kurth-Nelson et al. graph replay with decoders trained on stimulus-evoked MEG, and Liu et al. (eight objects in two sequences with sequence and position decoders, held-out items generalise, replay of abstract sequence-position codes).
- **Key results:**
  - Cited evidence that hippocampal codes include non-spatial roles and that replay sequences carry abstract role codes with objects.
  - Proposes testable experiments for recombination in replay.
  - States replay's compositional use is "unproven" and experiments so far are mostly spatial or simple visual objects.
- **Limitations / caveats:** No model or new data; most replay work is spatial.
- **Bearing on H065:** Partly supports. It is the source of the hypothesis but explicitly presents it as an unproven proposal, so "which is compositional computation" is stated more firmly in the row than in the paper.
- **Reproduce in this repo:** Replay buffer that samples recombined (role, filler) tuples vs faithful trajectories; test on novel combinations.

## Barreto 2017: Successor features for transfer in reinforcement learning
- **Cited for:** H066 (successor features split dynamics from reward, so skills transfer to new goals at once)
- **Link:** https://doi.org/10.48550/arxiv.1606.05312 · **Basis:** full text (web, arXiv PDF)
- **Question:** How can an agent transfer between tasks that share dynamics but differ in reward?
- **Method / model:** Reward assumed linear in features, r = phi . w. Successor features psi^pi (expected discounted feature sums) give Q = psi . w, decoupling dynamics from reward. Generalised policy improvement (GPI) acts greedily over the max of Q across a set of stored policies. Two theorems give performance bounds for the transferred policy even before learning on the new task.
- **Experiments:** (1) Four-room continuous navigation with 3 object classes whose rewards change every 20,000 transitions; 250 tasks, reward weights drawn from [-1, 1]^3; SFQL (known features, learned features) vs Q-learning and probabilistic policy reuse (PRQL); 30 runs. (2) MuJoCo two-joint reacher: 12 target tasks, training on only 4, SFDQN vs DQN.
- **Key results:**
  - All SFQL versions "significantly" beat PRQL and QL; average return gain over PRQL above 100% (PRQL itself about 100% over QL).
  - Learned features (SFQL-h) reached good overall performance faster than hand-supplied ones.
  - On the reacher, performance on the 8 untrained tasks improves while training others.
- **Limitations / caveats:** Reward must be (near-)linear in the features; dynamics must be fixed; learned features are approximate.
- **Bearing on H066:** Supports. Transfer to new reward weights without new learning is the paper's main result.
- **Reproduce in this repo:** Tabular SF agent on a gridworld: learn psi for 2-3 reward vectors, then evaluate GPI zero-shot on a new reward vs a model-free baseline.

## Graybiel 1998: The basal ganglia and chunking of action repertoires
- **Cited for:** H067 (basal ganglia chunk action sequences into reusable units)
- **Link:** https://doi.org/10.1006/nlme.1998.3843 · **Basis:** abstract only (sources.json holds no abstract; nothing can be reported)
- **Question / Method / Experiments / Key results:** not available.
- **Limitations / caveats:** Not assessed.
- **Bearing on H067:** Does not test it from available text; the title matches the chunking attribution but "reused like words" is unverified.
- **Reproduce in this repo:** Agent that promotes frequent action subsequences to macro-actions vs a flat agent on tasks sharing subsequences.

## Badre 2009: Is the rostro-caudal axis of the frontal lobe hierarchical?
- **Cited for:** H068 (frontal cortex is a front-to-back hierarchy of increasingly abstract rules)
- **Link:** https://doi.org/10.1038/nrn2667 · **Basis:** full text (web, first ~100k of ~160k characters)
- **Question:** Do anatomy, imaging, electrophysiology and development support a hierarchical rostro-caudal organisation?
- **Method / model:** Review.
- **Experiments:** Surveys fMRI (Koechlin 2003, Badre & D'Esposito 2007, Koechlin & Jubault 2006), monkey recordings and lesions, a stroke-patient study (Badre et al. 2009), anatomy and connectivity.
- **Key results:**
  - Gradient from premotor to pre-PMd, mid-DLPFC and frontopolar cortex with increasing abstraction.
  - Anterior activity explained caudal variance but not the reverse; stroke lesions impaired only abstract levels (strongest evidence).
  - Conclusion: the frontal cortex could be hierarchical; evidence is suggestive, hierarchy is "one intriguing possibility".
- **Limitations / caveats:** "Abstractness" is defined differently across studies; PMd can represent abstract rules; asymmetric influence needs direct perturbation tests.
- **Bearing on H068:** Partly supports. The row states hierarchy as fact; the review is cautious ("could be").
- **Reproduce in this repo:** Hierarchical-rule vs flat RNN/agent on nested rules (rule at level 2 selects rule at level 1); compare learning curves.

## Mastrogiuseppe 2018: Linking connectivity, dynamics and computations in low-rank recurrent neural networks
- **Cited for:** H069 (tasks are low-rank recurrent structure; abstraction means reusing the same low-rank parts)
- **Link:** https://doi.org/10.1016/j.neuron.2018.07.003 · **Basis:** full text (local PDF)
- **Question:** How do low-dimensional dynamics and computations follow from connectivity that is a random part plus minimal low-rank structure?
- **Method / model:** Connectivity J = random + P with P = rank-one (m n^T / N) or rank-two. Mean-field theory gives the dynamics from overlaps between connectivity vectors m, n and input vectors; geometry determines the equilibria and the dynamical range.
- **Experiments:** Analytical theory plus simulations (e.g. N = 3500 networks) on: Go-NoGo discrimination (rank one, m = readout w, n = input pattern), noisy detection, context-dependent discrimination (rank two, XOR-like), context-dependent evidence integration (rank two).
- **Key results:**
  - Minimal connectivity for each task is derived; dynamical range and computational capacity grow quickly with connectivity rank.
  - The context-dependent evidence task reuses the same rank-two configuration as basic context-dependent discrimination.
  - Predicts that neurons with large loadings on the dominant components share connectivity.
- **Limitations / caveats:** Authors study one task at a time with hand-derived low-rank structure; no learning of multiple tasks and no reuse of low-rank parts across a task family beyond the one context-dependent pair.
- **Bearing on H069:** Partly supports. Low-rank structure implementing tasks is shown; "abstraction = reuse of low-rank parts" is not tested (one shared rank-two motif is a hint).
- **Reproduce in this repo:** Train low-rank (rank 1-2) vs full-rank RNNs on two related tasks; measure overlap of the learned low-rank vectors.

## Yang 2019: Task representations in neural networks trained to perform many cognitive tasks
- **Cited for:** H070 (multitask networks reuse shared dynamical motifs / compositional representations)
- **Link:** https://doi.org/10.1038/s41593-018-0310-2 · **Basis:** abstract only
- **Question:** What representations arise when one RNN learns many cognitive tasks?
- **Method / model:** Single RNN trained on 20 tasks (working memory, decision making, categorisation, inhibitory control); a measure of task variance between units quantifies task relationships; a continual-learning technique for sequential training.
- **Experiments:** 20 tasks; details not in abstract.
- **Key results:** Units form functionally specialised clusters; learning often gives compositional task representations (a task can be performed by recombining instructions for other tasks); mixed task selectivity resembling PFC arises after sequential learning.
- **Limitations / caveats:** Not assessed beyond abstract. The paper discusses compositional task representations and clusters, not "dynamical motifs" (that term is Driscoll).
- **Bearing on H070:** Supports the compositional-representation half.
- **Reproduce in this repo:** See Driscoll note.

## Driscoll 2024: Flexible multitask computation in recurrent networks utilizes shared dynamical motifs
- **Cited for:** H070
- **Link:** https://doi.org/10.1038/s41593-024-01668-6 · **Basis:** abstract only
- **Question:** How do multitask RNNs reconfigure for different computations?
- **Method / model:** Dynamical-systems analysis of multitask RNNs; unit activation restricted to positive to obtain clustered units; lesions; transfer learning.
- **Experiments:** Multitask artificial RNNs (task count not in abstract).
- **Key results:** Dynamical motifs (attractors, decision boundaries, rotations) are reused across tasks (e.g. one ring attractor for circular-variable memory); cluster lesions cause modular deficits; motifs are reconfigured for fast transfer after an initial learning phase.
- **Limitations / caveats:** Abstract only; trained with standard methods, not local rules.
- **Bearing on H070:** Supports. Shared motifs across tasks is the stated result.
- **Reproduce in this repo:** Train a small RNN on 3-4 related tasks (e.g. memory of an angle, delayed match); cluster units and fixed-point-analyse shared motifs; repeat with a local-rule net.

## Chater 2003: Simplicity: a unifying principle in cognitive science?
- **Cited for:** H071 (the brain abstracts by compression: it prefers the simplest description)
- **Link:** https://doi.org/10.1016/s1364-6613(02)00005-0 · **Basis:** full text (local PDF)
- **Question:** Can simplicity (shortest code) explain how cognition chooses patterns among the infinitely many compatible with data?
- **Method / model:** Opinion article. Description length via Shannon code length log2(1/p) and Kolmogorov complexity K(x); preferred pattern is the one giving the shortest code; justified by the universal prior and prediction-convergence results.
- **Experiments:** Reviews examples: perceptual organisation (Box 1), Boolean concept learning speed predicted by shortest code length (Feldman 2000), similarity as transformation, Shepard's law, early-vision compression, grammar induction.
- **Key results:**
  - Simplicity gives a candidate solution to the problem of induction and fits a range of cognitive models (Table 1).
  - Concludes simplicity "is worth pursuing as a potentially important unifying principle."
  - Notes the brain also uses highly redundant sparse codes.
- **Limitations / caveats:** Representation problem and search problem prevent precise empirical predictions; Kolmogorov complexity is not computable.
- **Bearing on H071:** Partly supports. It is a proposal with mixed evidence, not a demonstration that the brain abstracts by compression.
- **Reproduce in this repo:** MDL/weight-penalised learner vs plain learner on transfer tasks across layouts.

## Gentner 1983: Structure-mapping: a theoretical framework for analogy
- **Cited for:** H072 (analogy maps relations, not features)
- **Link:** https://doi.org/10.1207/s15516709cog0702_3 · **Basis:** abstract only
- **Question:** How is an analogy's meaning derived from its parts?
- **Method / model:** Rules map knowledge from a base to a target domain based only on syntactic properties of the representation; principles: relations (not attributes) are mapped; systematicity (higher-order relations) selects which.
- **Experiments:** None stated.
- **Key results:** Analogy is distinguished from literal similarity and abstraction by these principles.
- **Limitations / caveats:** Cognitive theory, not neural; not assessed beyond abstract.
- **Bearing on H072:** Supports (this is the structure-mapping claim itself).
- **Reproduce in this repo:** Relation-matching mapper (graph isomorphism) vs feature-matching on surface-different layouts.

## Quian Quiroga 2005: Invariant visual representation by single neurons in the human brain
- **Cited for:** H073 (concept cells are sparse, invariant codes built by learning, not innate detectors)
- **Link:** https://doi.org/10.1038/nature03687 · **Basis:** abstract only
- **Question:** How do human neurons achieve invariant recognition?
- **Method / model:** Single-neuron recordings in human medial temporal lobe.
- **Experiments:** Human MTL; numbers not in abstract.
- **Key results:** A subset of MTL neurons responds selectively to different pictures of given individuals, landmarks or objects and sometimes to their written names, suggesting an "invariant, sparse and explicit code".
- **Limitations / caveats:** Says nothing about whether such neurons are learned or innate (the paper suggests relevance to long-term, abstract memories).
- **Bearing on H073:** Partly supports. Invariant, sparse code is shown; "built by learning, not innate" is the hypothesis's own addition, not shown by the abstract.
- **Reproduce in this repo:** Sparse Hebbian/competitive net on multiple views of a few entities; test whether single units become view-invariant.

## Eichenbaum 2014: Time cells in the hippocampus: a new dimension for mapping memories
- **Cited for:** H074 (time cells give an abstract time axis reused for any sequence)
- **Link:** https://doi.org/10.1038/nrn3827 · **Basis:** full text (web, first ~100k of ~141k characters)
- **Question:** Do hippocampal neurons represent the flow of time in memories independently of space and behaviour?
- **Method / model:** Review.
- **Experiments:** Surveys odour-sequence drift (Manns 2007), wheel-running delays (Pastalkova 2008), object-odour delays of 10 s or 20 s (MacDonald 2011; cells re-time when the delay is lengthened), treadmill speed manipulation (Kraus 2013), head-fixed studies and mouse eyeblink conditioning.
- **Key results:**
  - Time cells encode elapsed time independent of place and movement; over 80% of active neurons were time-modulated in the treadmill study.
  - Firing sequences develop with learning, differ between memories, and predict memory accuracy; later-firing cells have longer fields (scalar coding).
  - Some neurons are active across all odour memories and may represent shared trial temporal structure.
- **Limitations / caveats:** Early confounds with location/distance; origin of timing unresolved; human evidence is mostly gradual population drift; the review does not test one time axis reused across sequences.
- **Bearing on H074:** Partly supports. Time cells exist, but reuse of one abstract time axis for any sequence is a hypothesis.
- **Reproduce in this repo:** Temporal-context (drifting-context) model vs fixed delay lines; train on one sequence, test generalisation to a new item order.

## Howard 2002: A distributed representation of temporal context
- **Cited for:** H074 (temporal-context model)
- **Link:** https://doi.org/10.1006/jmps.2001.1388 · **Basis:** abstract only (sources.json holds no abstract; nothing can be reported)
- **Question / Method / Experiments / Key results:** not available.
- **Limitations / caveats:** Not assessed.
- **Bearing on H074:** Does not test it from available text; unverified.
- **Reproduce in this repo:** See Eichenbaum note.

## Collins 2013: Cognitive control over learning: creating, clustering, and generalizing task-set structure
- **Cited for:** H075 (people infer hidden task states, cluster them, reuse a cluster's policy)
- **Link:** https://doi.org/10.1037/a0030852 · **Basis:** abstract only
- **Question:** How do learners infer hidden task-set structure and decide to reuse or create new structure?
- **Method / model:** Context-task-set (C-TS) model inspired by nonparametric Bayesian methods (reuse or create structure in new situations); a neurobiologically explicit frontal-BG network approximating C-TS.
- **Experiments:** Human behavioural experiments with generalisation tests (numbers not in abstract).
- **Key results:** Participants spontaneously build task-set structure when not cued, predicting positive and negative transfer; C-TS fits human choice sequences quantitatively.
- **Limitations / caveats:** Abstract only.
- **Bearing on H075:** Supports. This is the better source for "cluster and reuse" than Gershman & Niv.
- **Reproduce in this repo:** Chinese-restaurant-process latent-cause agent that reuses a policy for a returning layout; compare relearning speed.

## Gershman 2010: Learning latent structure: carving nature at its joints
- **Cited for:** H075
- **Link:** https://doi.org/10.1016/j.conb.2010.02.008 · **Basis:** full text (web)
- **Question:** Does inferring task structure make reinforcement learning faster?
- **Method / model:** Review of structure learning; Bayesian inference over latent causes with an automatic Occam's razor; approximations by sampling or policy search.
- **Experiments:** Reviews renewal, reinstatement and spontaneous recovery of fear (original latent cause re-activates in the acquisition context); Redish's state-splitting model and hippocampal lesion/developmental data; gating framework (dopamine prediction errors control working memory); effector-specific value decomposition with human fMRI.
- **Key results:**
  - Learning is averaged only over trials attributed to the same latent cause.
  - Return of fear is explained as reactivation of the original cause.
  - Does not discuss the Chinese restaurant process or explicit reuse of whole policies.
- **Limitations / caveats:** Review; exact inference is intractable.
- **Bearing on H075:** Partly supports (latent-cause inference), but the "reuse a whole cluster's policy" part is not in this paper; it belongs to Collins & Frank.
- **Reproduce in this repo:** See Collins note.

## Kemp 2008: The discovery of structural form
- **Cited for:** H076 (the brain chooses among structural forms to organise knowledge)
- **Link:** https://doi.org/10.1073/pnas.0802631105 · **Basis:** full text (web)
- **Question:** Can a model discover which form (tree, ring, chain, grid, ...) best fits a dataset?
- **Method / model:** Hierarchical Bayesian model, P(S,F|D) proportional to P(D|S) P(S|F) P(F), with forms generated by graph grammars; prior favours fewer clusters, likelihood favours features that vary smoothly on the graph; greedy search per form.
- **Experiments:** Real data: 33 animals x 106 features (tree), 13 Supreme Court judges x 1,596 cases (chain), 14 hues (ring), faces (grid), 35 cities (cylinder), dominance data (order), 13 administration members (hierarchy), inmates (partition), 20 armshell trade communities (ring); five synthetic datasets with true form recovered in all.
- **Key results:**
  - Discovers the intuitive form in each real dataset.
  - Developmental simulation: with 5 features per animal it chooses a partition; between 5 and 20 features it shifts to a tree.
  - No human experiments reported in this text.
- **Limitations / caveats:** Computational-level model, no neural claim; hypothesis space not exhaustive; parameter fixed; greedy search; links to cognition "speculative".
- **Bearing on H076:** Partly supports. It shows form selection is computable, not that "the brain chooses" among forms. The row overstates.
- **Reproduce in this repo:** Score a small set of forms (chain, ring, tree) on category data with and without form selection; compare fit.

## Flesch 2022: Orthogonal representations for robust context-dependent task performance in brains and neural networks
- **Cited for:** H077 (orthogonal contexts allow many tasks without interference)
- **Link:** https://doi.org/10.1016/j.neuron.2022.01.005 · **Basis:** abstract only
- **Question:** How do neural populations code for multiple conflicting tasks?
- **Method / model:** Simulations of "lazy" (random-projection, input dimensionality expanded) vs "rich" (structured, relevant features privileged) learning; one rich solution projects tasks onto low-dimensional orthogonal manifolds.
- **Experiments:** Human behaviour and neuroimaging; macaque PFC data.
- **Key results:** Biological coding patterns have dimensionality and geometry consistent with the rich regime (numbers not in abstract); lazy vs rich trades learning speed against robustness.
- **Limitations / caveats:** Abstract only.
- **Bearing on H077:** Supports the orthogonal-representation half.
- **Reproduce in this repo:** Context-dependent net trained in rich vs lazy regime; measure subspace angle between contexts and cross-context interference.

## Zeng 2019: Continual learning of context-dependent processing in neural networks
- **Cited for:** H077
- **Link:** https://doi.org/10.1038/s42256-019-0080-x · **Basis:** full text (local PDF)
- **Question:** Can one network learn many mapping rules sequentially without forgetting?
- **Method / model:** Orthogonal weights modification (OWM): the update is projected orthogonal to the span of previously seen input vectors, dW = lambda * P * dW_BP with P = I - A(A^T A + alpha I)^-1 A^T, computed iteratively (recursive least squares). A context-dependent processing (CDP) module rotates the sensory input space as a function of context so identical inputs can use OWM in different contexts.
- **Experiments:** Shuffled MNIST (3, 10, 100 tasks), disjoint MNIST, disjoint CIFAR-10, 3,755 Chinese characters, ImageNet with a pretrained feature extractor, 40 face attributes as 40 sequential rules.
- **Key results:**
  - Shuffled MNIST: 97.52 +/- 0.03% (10 tasks, 4-layer net) vs EWC 97.0 and CAB 95.2; 100 tasks 85.4% vs EWC 70.8 and SI 82.3.
  - Sequentially learns all 3,755 characters with final accuracy about 92%; 500 characters suffice to learn the remaining 3,255 at near 80%.
  - 40 attribute rules learned with one classifier, close to multi-task training; about 20 faces reach plateau.
  - Capacity falls as the rank of the projector decreases.
- **Limitations / caveats:** Regularisation-type approach with a trade-off between old and new tasks; limited capacity; the authors say it is unknown whether the brain does anything like OWM; backprop-based.
- **Bearing on H077:** Partly supports. OWM orthogonalises weight updates relative to inputs, not context representations; it shows interference-free sequential learning but is a different mechanism from Flesch's orthogonal context manifolds.
- **Reproduce in this repo:** OWM-style projected update vs plain SGD on sequential tasks; measure forgetting.

## Papadimitriou 2020: Brain computation by assemblies of neurons
- **Cited for:** H078 (assembly calculus is the brain's unit of computation)
- **Link:** https://doi.org/10.1073/pnas.2001893117 · **Basis:** abstract only
- **Question:** Which operations on assemblies can generic random networks with Hebbian plasticity realise?
- **Method / model:** n excitatory neurons per area, random connectivity, k-cap (only the k highest-input neurons fire), Hebbian plasticity with homeostasis. Operations: projection, reciprocal projection, association, merge, pattern completion.
- **Experiments:** Analytical proofs in a simplified model plus simulations; a proposed assembly-based brain architecture for syntactic processing of language (numbers not in abstract).
- **Key results:** The operations are plausible in this model; "in principle capable of carrying out arbitrary computations" under assumptions; hypothesised to underlie reasoning, planning and language.
- **Limitations / caveats:** Simplified model; abstract frames it as a hypothesis.
- **Bearing on H078:** Supports as a model proposal; it does not show the brain actually uses it.
- **Reproduce in this repo:** k-cap random network with Hebbian updates: test projection and merge, then a tiny grammar parse.

## Buzsaki 2010: Neural syntax: cell assemblies, synapsembles, and readers
- **Cited for:** H078
- **Link:** https://doi.org/10.1016/j.neuron.2010.09.023 · **Basis:** abstract only
- **Question:** How do cell assemblies form, disband and sequence, and how are they defined?
- **Method / model:** Review/hypothesis: assemblies defined by their "reader-actuator" output; hierarchical assembly organisation as neural syntax; synapsembles.
- **Experiments:** None of its own.
- **Key results:** Proposes a tripartite framework and experimental strategies.
- **Limitations / caveats:** Review.
- **Bearing on H078:** Does not test the assembly calculus; supports only "assemblies are a unit of computation" in a loose sense.
- **Reproduce in this repo:** See Papadimitriou note.

## Corrections to the hypotheses file
- H060: Plate 1995 covers circular convolution only; XOR (binary) binding belongs to Kanerva, which could not be verified here. Phrase "binding, not shown to be brain-implemented".
- H063: the abstract of Tse 2007 says "neocortical schema", not "medial PFC", and gives no "a day" figure; verify or soften.
- H065: Kurth-Nelson 2023 states the compositional-replay idea as an unproven hypothesis; mark as "proposal".
- H068: Badre & D'Esposito conclude hierarchy "could be" and is one possibility; phrase as "may be".
- H069: Mastrogiuseppe 2018 does not test reuse of low-rank parts across tasks; cite it for "tasks can be implemented by low-rank structure" only.
- H071: Chater & Vitanyi is a proposal and also notes sparse redundant neural codes; use "may" and not "the brain abstracts by compression".
- H073: "built by learning, not innate" is not in Quian Quiroga 2005.
- H075: "cluster and reuse a policy" is supported by Collins & Frank 2013; Gershman & Niv 2010 covers latent-cause inference and does not discuss clustering or policy reuse.
- H076: Kemp & Tenenbaum is a computational-level model; "the brain chooses" overstates.
- H077: Zeng 2019 orthogonalises weight updates relative to inputs, not context representations; Flesch 2022 is the representational source.
- H062 and H059 are in tension: Whittington 2023 argues mixed selectivity is not general and that factorised tasks give disentangled single-factor neurons; cross-reference them.
- H079 and H080: no source ("new"); nothing verified.
