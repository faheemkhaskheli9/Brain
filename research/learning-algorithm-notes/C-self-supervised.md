# Paper notes: C. Self-supervised objectives

Structured notes on the sources cited by hypotheses H039-H054 of `research/learning-algorithm-hypotheses.md` (section C, "Self-supervised objectives: cortex learns a world model"). Generated 2026-10-12 from the local PDFs in `research/pdfs/learning-algorithm/` (8 sources), full text fetched from the web (3), and abstracts only (8). Basis is stated per note; for "abstract only" notes nothing beyond the abstract is claimed.

## Rao 1999: Predictive coding in the visual cortex: a functional interpretation of some extra-classical receptive-field effects
- **Cited for:** H039 (cortex minimises sensory prediction error, higher areas predicting lower ones).
- **Link:** https://doi.org/10.1038/4580 · **Basis:** abstract only (Europe PMC abstract; sources.json had none)
- **Question:** Can extra-classical receptive-field effects (e.g. end-stopping) be explained as a by-product of hierarchical prediction of lower-level activity?
- **Method / model:** Per the abstract: feedback connections from a higher to a lower visual area carry predictions of lower-level activity; feedforward connections carry the residual errors between prediction and actual activity.
- **Experiments:** Hierarchical network of model neurons exposed to natural images (sizes, image set, training details not available from the abstract).
- **Key results:** Units developed simple-cell-like receptive fields; the subset of error-carrying units showed end-stopping and other extra-classical effects.
- **Limitations / caveats:** Not assessable from the abstract. The abstract frames this as a functional interpretation of surround effects, not a test that cortex learns by this scheme.
- **Bearing on H039:** Partly supports. The model is the canonical form of the idea (feedback predictions, feedforward errors), but the paper shows consistency with receptive-field phenomena, not that this is how cortex learns.
- **Reproduce in this repo:** Two-level linear predictive-coding net on whitened image patches; check that error units show end-stopping-like surround suppression when a bar extends past the classical field, and that removing the top-down prediction removes it.

## Friston 2010: The free-energy principle: a unified brain theory?
- **Cited for:** H040 (all learning and action minimise one quantity, variational free energy).
- **Link:** https://doi.org/10.1038/nrn2787 · **Basis:** abstract only (Europe PMC abstract; sources.json had none)
- **Question:** Can several global brain theories be unified by one optimisation principle?
- **Method / model:** A review. Per the abstract: it re-reads theories such as neural Darwinism, information theory and optimal control from the free-energy perspective; the common quantity is value (expected reward/utility) or its complement, surprise (prediction error, expected cost).
- **Experiments:** None stated (review).
- **Key results:** The claim, as phrased in the abstract, is that "several global brain theories might be unified within a free-energy framework", with action, perception and learning all accounted for.
- **Limitations / caveats:** The abstract says "might be unified", a weaker wording than "all learning and action minimise one quantity". It offers no empirical test; the hypotheses file itself flags it as hard to falsify.
- **Bearing on H040:** Partly supports. It is the right source for the framework, but the paper proposes it as a unifying lens, not as an established fact.
- **Reproduce in this repo:** Active-inference agent (free-energy minimising) vs a plain RL agent in the Brain World task; compare reward, sample efficiency and exploration. Only meaningful once a specific agent is fixed.

## Singer 2018: Sensory cortex is optimized for prediction of future input
- **Cited for:** H041 (sensory cortex is tuned to predict the near future of its input).
- **Link:** https://doi.org/10.7554/elife.31557 · **Basis:** full text (web; Europe PMC XML of PMC6108826)
- **Question:** Do the receptive fields (RFs) of V1 and A1 neurons match those of a model optimised to predict the immediate future of natural video or sound from the recent past?
- **Method / model:** Feedforward network with one hidden layer of nonlinear (sigmoid) units: linear map from past input, nonlinearity, linear map to the predicted future. Trained by minimising prediction error with L1 regularisation on the weights (sparse wiring, not sparse activity). The hidden unit's input weights are its RF.
- **Experiments:** Vision: natural movie patches, predict 1 frame (40 ms) from 7 frames (280 ms). Audition: cochleagrams, predict 3 time steps (15 ms) from 40 (200 ms). Compared with 114 ferret A1/AAF neurons (76 single units, 5 animals) recorded by the authors, with V1 simple-cell RFs from Ohzawa et al. 1996 and Ringach 2002, and with a sparse coding model (Olshausen-Field style) trained on the same data. Auditory net: 1600 hidden units, 167 active after L1 shrinkage.
- **Key results:**
  - Model RFs show V1-like oriented, space-time separable and inseparable structure, and A1-like diverse spectrotemporal RFs, with temporally asymmetric power concentrated near the present.
  - Sparse coding RFs lacked the temporal asymmetry and spanned a much larger region of an MDS embedding than real A1 and temporal-prediction RFs, which overlapped.
  - The better a network predicted the future, the more its RFs resembled real ones.
- **Limitations / caveats:** Single hidden layer, trained by gradient descent, not a cortical learning rule. The control that matters is sparse coding, not a generic non-predictive model. A1 data were from anaesthetised ferrets. Similarity is by chosen RF measures.
- **Bearing on H041:** Supports (for V1 and A1 RFs in these models). The paper compares against sparse coding, so "non-predictive" in the proposed test is best read as sparse coding.
- **Reproduce in this repo:** Train a one-hidden-layer net to predict frame t+1 from frames t-6..t of a small moving-pattern stream, and a sparse-coding net on the same patches; compare RF temporal asymmetry (power at most recent vs oldest frame).

## Lotter 2017: Deep predictive coding networks for video prediction and unsupervised learning
- **Cited for:** H041 (second source: sensory cortex tuned to near-future prediction).
- **Link:** https://doi.org/10.48550/arxiv.1605.08104 · **Basis:** full text (web; arXiv PDF)
- **Question:** Is next-frame prediction a useful unsupervised learning rule, using a predictive-coding-inspired architecture (PredNet)?
- **Method / model:** Stacked modules, each with an input layer A, a convolutional-LSTM representation R, a prediction A-hat = ReLU(conv(R)) and an error E = [ReLU(A - A-hat); ReLU(A-hat - A)]. Errors are the only signal sent forward (conv, ReLU, maxpool gives the next layer's target); R also gets top-down input from the layer above. Loss: weighted sum of error-unit activity over time and layers (L1 at the lowest layer). Trained end to end with backprop (Adam).
- **Experiments:** Rendered rotating faces (16K training sequences, 64x64); KITTI car-mounted video (about 41K frames, 128x160) with transfer to Caltech Pedestrian; baselines: copy last frame and a CNN-LSTM encoder-decoder that forwards activations rather than errors. Readouts: linear decoding of latent parameters, face identity SVM, steering angle.
- **Key results:**
  - Faces: MSE 0.0152, SSIM 0.937 (PredNet) vs 0.0180 / 0.907 (CNN-LSTM) and 0.125 / 0.631 (copy last frame).
  - Caltech: MSE 3.13e-3, SSIM 0.884 vs 3.67e-3 / 0.865 (CNN-LSTM) and 7.95e-3 / 0.762 (copy).
  - Linear readout of steering angle from 1K labelled examples explained 74% of variance (35% better than the CNN-LSTM); with 25K examples MSE 2.14 deg^2.
- **Limitations / caveats:** Deep-learning paper; "predictive coding" is the inspiration, training uses backprop through time. It makes no comparison with V1 receptive fields. Loss weights on upper layers changed which downstream task did best.
- **Bearing on H041:** Does not test it. It shows prediction yields useful features for ML tasks, which is not evidence that cortex is tuned to predict the future. Better cited for H039/H043-style "prediction as learning signal" than for the V1 claim; Singer is the actual test.
- **Reproduce in this repo:** n/a (not a T1 core claim; covered by the Singer-style experiment above).

## Wiskott 2002: Slow Feature Analysis: Unsupervised Learning of Invariances
- **Cited for:** H042 (invariant features come from preferring slowly varying signals).
- **Link:** https://doi.org/10.1162/089976602317318938 · **Basis:** full text
- **Question:** Can invariances be learned unsupervised by finding functions of the input whose output varies as slowly as possible?
- **Method / model:** Find functions g_j(x) so that the output y_j(t) minimises the mean squared temporal derivative <dy_j^2> under zero mean, unit variance and decorrelation across outputs (ordered by slowness). Algorithm: nonlinear expansion of the input (e.g. quadratic), whitening, then PCA on the time derivative and take the smallest-variance directions; solved in closed form (an eigenvalue problem), not by a synaptic rule. Hierarchy: alternating linear and quadratic SFA layers.
- **Experiments:** Examples 1-2: complex-cell, disparity and motion features from simple-cell input. Example 3: repeated SFA finds a hidden slow feature (correlation 0.59, 0.61, 0.97 over three successive SFAs). Example 4: 1-D retina with 65 sensors, hierarchical network, low-pass-filtered Gaussian-noise patterns (15-30 units) sliding at 1 unit per step; translation invariance tested on new patterns. Example 5: size, contrast, illumination invariances with Lambertian 1-D objects.
- **Key results:**
  - Translation-invariant recognition of unseen patterns: average angle between response vectors across locations 12.6 degrees (random vectors would give 90).
  - 20 training patterns were enough for good generalisation; performance degraded only slowly down to 5 patterns.
  - Learning several invariances at once degraded performance considerably (authors' own caveat).
- **Limitations / caveats:** Synthetic 1-D patterns; the authors list learning from real-world image sequences and a neural (online, local) implementation as open. The slowness objective needs temporal continuity of identity.
- **Bearing on H042:** Supports on synthetic data (position-invariant units do emerge from a moving-object stream). It does not show it for natural images, nor that cortex does it.
- **Reproduce in this repo:** Closed-form SFA (quadratic expansion + generalised eigenproblem) on a 1-D moving random-pattern stream; test whether a top feature is position-invariant (angle between responses at shifted positions) vs PCA features.

## Illing 2021: Local plasticity rules can learn deep representations using self-supervised contrastive predictions
- **Cited for:** H043 (local, layer-wise contrastive prediction trains deep representations).
- **Link:** https://doi.org/10.48550/arxiv.2010.08262 · **Basis:** full text (web; arXiv PDF)
- **Question:** Can a rule using only pre/post activity, a dendritic prediction and broadcast factors build deep hierarchical representations without backprop?
- **Method / model:** CLAPP (Contrastive, Local And Predictive Plasticity). Each layer predicts its own future encoding through W_pred; the dendritic prediction modulates plasticity but not activity. A binary hinge-type loss per layer: align prediction with the next encoding during fixation (positive update) and push it away from the encoding of the post-saccade input (negative update, signalled by a broadcast saccade factor). No gradients between layers; W_retro avoids weight transport.
- **Experiments:** STL-10 (images read as 16x16 patch sequences, VGG-6 encoder, 300 epochs on the unlabelled set), LibriSpeech phone classification, UCF-101 video. Linear readouts on frozen features. Baselines: random encoder, greedy supervised, CPC, layer-wise GIM, Hinge-loss CPC with end-to-end backprop.
- **Key results:**
  - STL-10 linear accuracy: random encoder 21.8%, CPC 73.2%, Hinge-loss CPC end-to-end 80.3%, layer-wise CLAPP-s 74.0%, fully local CLAPP 73.6% (layer 5). Accuracy rises with depth, unlike a random conv encoder.
  - Gap between local and end-to-end is about 6-7 points on STL-10; the largest single cause was blocking gradients between layers.
  - Fully local CLAPP on video needed many negative samples and converged too slowly in their setup.
- **Limitations / caveats:** Time is simulated for static images by patch scanning; the saccade/negative signal is assumed. Authors state CLAPP does not give general credit assignment. Table columns for LibriSpeech/UCF-101 are partly illegible in the extracted text, so only STL-10 figures are quoted here.
- **Bearing on H043:** Supports (deep features, layer-wise, no backprop). "Large gap" in the proposed test overstates it: the measured gap to end-to-end CPC-style training is moderate and CLAPP roughly matches the original CPC number.
- **Reproduce in this repo:** Small layer-wise contrastive-prediction net on a temporal stream (e.g. moving digits), with and without gradients between layers; compare linear-probe accuracy per depth.

## LeCun 2022: A path towards autonomous machine intelligence
- **Cited for:** H044 (cortex predicts in an abstract embedding space, not in pixels).
- **Link:** https://openreview.net/forum?id=BZ5a1r-kVsf · **Basis:** abstract only (sources.json held no abstract; OpenReview refused the fetch with a bot challenge, so nothing about the paper's content was read)
- **Question:** Not verifiable from what was retrieved.
- **Method / model:** Not read. The paper is known to be a position paper (the hypotheses file calls it one).
- **Experiments:** Not read.
- **Key results:** None extracted.
- **Limitations / caveats:** A position paper presenting a proposed architecture; no brain-data test is expected. This note makes no claim about its content.
- **Bearing on H044:** Does not test it, as far as can be said. It is an AI-architecture proposal, so it cannot be evidence that cortex predicts in embedding space; the hypothesis needs neuroscience or experimental support, with LeCun cited only as the origin of the idea. Needs a re-check against the actual text.
- **Reproduce in this repo:** Local model predicting next-step latent codes (target encoder with stop-gradient) vs a pixel-predicting model on a Brain World stream; compare linear-probe transfer to a held-out layout.

## Olshausen 1996: Emergence of simple-cell receptive field properties by learning a sparse code for natural images
- **Cited for:** H045 (neurons learn a sparse code, few active units, each an independent cause).
- **Link:** https://doi.org/10.1038/381607a0 · **Basis:** abstract only (Europe PMC abstract; sources.json had none)
- **Question:** Does maximising sparseness of a linear code for natural scenes produce localised, oriented, bandpass receptive fields like V1 simple cells?
- **Method / model:** Per the abstract: a learning algorithm that finds sparse linear codes for natural scenes.
- **Experiments:** Natural images (details not in the abstract).
- **Key results:** A complete family of localised, oriented, bandpass receptive fields emerges, resembling simple cells; the sparse code has a higher degree of statistical independence among its outputs.
- **Limitations / caveats:** Not assessable from the abstract. It shows that sparseness suffices to explain static RF shape, not that the brain learns by it.
- **Bearing on H045:** Partly supports. The abstract confirms sparse coding gives V1-like RFs and increased output independence; "each unit stands for an independent cause" is the hypothesis's gloss (the abstract only claims higher statistical independence).
- **Reproduce in this repo:** Sparse coding (ISTA inference, gradient dictionary update) on whitened Brain World observation patches; then test dictionary reuse across layouts via a linear probe.

## Barlow 1961: Possible principles underlying the transformations of sensory messages
- **Cited for:** H046 (learning removes redundancy so each neuron carries non-overlapping information).
- **Link:** https://doi.org/10.7551/mitpress/9780262518420.003.0013 · **Basis:** abstract only (sources.json abstract of the book chapter)
- **Question:** What are sensory relays for? The abstract lists three hypotheses: "password" (specific stimulus detectors), relays as control points that modulate information flow, and redundancy reduction.
- **Method / model:** A theoretical chapter; no model or data in the abstract.
- **Experiments:** None stated.
- **Key results:** The third hypothesis states that reduction of redundancy is an important principle guiding the organisation of sensory messages, carried out at relays in sensory pathways.
- **Limitations / caveats:** It is a verbal proposal, one of three, and about sensory relays rather than learning. The abstract does not describe a learning rule.
- **Bearing on H046:** Partly supports. Redundancy reduction is the stated principle, but the paper does not say it comes from learning; that link is later work (e.g. Bell and Sejnowski).
- **Reproduce in this repo:** See Bell & Sejnowski below.

## Bell 1995: An information-maximization approach to blind separation and blind deconvolution
- **Cited for:** H046 (learning removes redundancy; infomax/ICA).
- **Link:** https://doi.org/10.1162/neco.1995.7.6.1129 · **Basis:** abstract only
- **Question:** Can a self-organising network maximising information transfer separate statistically independent sources?
- **Method / model:** Per the abstract: a self-organising algorithm that maximises information transferred through a network of nonlinear units, in the zero-noise limit, with no assumption about the input distribution. The nonlinearities pick up higher-order moments, giving "something akin to true redundancy reduction" between output units.
- **Experiments:** Source separation (cocktail party) of unknown mixtures of up to 10 speakers; blind deconvolution (cancelling echoes/reverberation in speech); a derivation of dependence of information transfer on time delays.
- **Key results:** Separation of up to 10 speakers; described as a higher-order generalisation of PCA.
- **Limitations / caveats:** The abstract frames it as signal processing; no neural data. Details (sample sizes, error numbers) not available.
- **Bearing on H046:** Partly supports. It supplies the algorithm that approximates redundancy reduction, but it does not test whether neurons in a brain carry non-overlapping information. Note also that the abstract says it generalises PCA, so "infomax/ICA no better than PCA downstream" is an open empirical question.
- **Reproduce in this repo:** Infomax ICA vs PCA features on Brain World observations; compare a downstream linear learner's sample efficiency.

## Pehlevan 2015: A Hebbian/anti-Hebbian neural network for linear subspace learning: a derivation from multidimensional scaling of streaming data
- **Cited for:** H047 (Hebbian plus anti-Hebbian rules follow from a similarity-matching objective).
- **Link:** https://doi.org/10.1162/neco_a_00745 · **Basis:** full text (local PDF is the arXiv v1 preprint, 1503.00669)
- **Question:** Can a biologically plausible (local) network that learns the principal subspace of streaming data be derived from a principled cost function?
- **Method / model:** Start from classical multidimensional scaling (strain cost: match pairwise input similarities x_t.x_t' with output similarities y_t.y_t'). Online version gives a network with feedforward weights W and lateral weights M: y = W x - M y (solved by asynchronous coordinate descent, y = (I+M)^-1 W x). Updates: D += y_i^2; W_ij += y_i (x_j - W_ij y_i)/D; M_ij += (y_i y_j - M_ij y_i)/D. Hebbian for W; anti-Hebbian for the lateral M (because of the sign in y = Wx - My). Same form as Oja's rule, with learning rate 1/D set by cumulative activity.
- **Experiments:** Synthetic coloured Gaussian input, n = 64 input channels, m = 4 outputs (top 4 components held 0.54 of the power ratio to the remaining 60); 40 random datasets; compared with APEX and Foldiak's network on strain error, subspace error and non-orthonormality; also a subspace-tracking test with non-stationary data.
- **Key results:**
  - The derived network reached lower strain error, found the principal subspace and orthonormalised its filters faster than APEX and Foldiak's networks (stated as observed in simulation).
  - Local stability analysis shows the stationary point gives orthonormal filters spanning the principal subspace.
  - With a modified learning-rate rule (floor on the rate) the same network tracks a changing subspace.
- **Limitations / caveats:** Linear units only; the network finds the principal subspace, not the individual components. No global convergence proof (the stability analysis is local). Synthetic data only. The term "similarity matching" is not used in this version; it uses "classical multidimensional scaling / strain cost".
- **Bearing on H047:** Supports. The Hebbian and anti-Hebbian rules are derived from a cost matching input and output similarities. The proposed test ("fails to find the principal subspace online") is already answered in the affirmative for Gaussian data here.
- **Reproduce in this repo:** Implement the W/M updates with 1/D learning rates on a 64-d Gaussian stream; plot subspace error (dB) against samples, with PCA as reference.

## Hawkins 2019: A framework for intelligence and cortical function based on grid cells in the neocortex
- **Cited for:** H048 (each cortical column learns whole objects in its own reference frame and columns vote).
- **Link:** https://doi.org/10.3389/fncir.2018.00121 · **Basis:** full text
- **Question:** Can grid-cell-like location signals in every cortical column explain how the neocortex learns object models?
- **Method / model:** A hypothesis and theory paper. Proposes grid cells in each column (suggested layer 6) encoding sensor location relative to the object, displacement cells (layer 5) for relations between objects and composition, and columns that observe the same object reach agreement through non-hierarchical connections between object representations ("voting"). Argues mechanisms for learning environments in entorhinal cortex/hippocampus are reused for objects.
- **Experiments:** None in this paper. It cites fMRI and single-cell evidence for grid-like signals outside entorhinal cortex (Doeller 2010, Constantinescu 2016, Jacobs 2013) and refers to Hawkins et al. 2017 and Lewis et al. 2018 for simulations of column voting and location-based object learning.
- **Key results:**
  - Proposes that every column learns complete object models, with many models of each object across the cortex.
  - Predicts location cells in L6 and displacement cells in L5 (stated as predictions to test).
  - Hierarchy is retained but passes representations of objects, not only features.
- **Limitations / caveats:** The paper states that its capacity analysis needs a better understanding of hierarchical flow and is out of scope; no quantitative model results appear in it. The voting mechanism is described briefly, with details deferred to the 2017 paper.
- **Bearing on H048:** Partly supports as a statement of the theory; does not test it. The voting simulations that would back the comparison with a single large model live in Hawkins et al. 2017 ("A theory of how columns in the neocortex enable learning the structure of the world"), not in this paper.
- **Reproduce in this repo:** Several small sensor-patch "columns" each building an object-reference-frame memory, voting by overlapping candidate-object sets, vs one model seeing the full touch sequence; accuracy vs number of touches.

## Hawkins 2016: Why neurons have thousands of synapses, a theory of sequence memory in neocortex
- **Cited for:** H049 (dendritic segments let neurons predict sequences; distal match puts cell in "predicted" state).
- **Link:** https://doi.org/10.3389/fncir.2016.00023 · **Basis:** full text (local PDF is the Oct 2015 submitted manuscript, not the published version)
- **Question:** How can neurons with thousands of synapses on active dendrites support a sequence memory?
- **Method / model:** HTM neuron: proximal synapses drive spikes; distal basal segments act as threshold coincidence detectors (an NMDA spike once about 8-20 co-active synapses; threshold 10 in the worked example, segments hold 15-40 synapses); a segment match depolarises the cell into a "predicted" state without a spike. Network: mini-columns (sparse column activation) with several cells per column; the predicted cell wins within an active column, giving high-order context. Learning is Hebbian-like with synaptic permanence values (permanence above a threshold gives weight 1).
- **Experiments:** Mathematical estimates of false-positive pattern recognition on a dendritic segment under sparsity (e.g. 10 synapses onto a 2,000-of-200K active population: false match probability about 9.8e-21). Network simulation: 2048 mini-columns (2% active, 40 per input), 32 cells per column, 128 basal segments per cell, up to 40 synapses per segment; artificial stream mixing random elements and repeated 6-element sequences ("XABCDE" / "YABCFG").
- **Key results:**
  - The high-order network reached the maximum achievable prediction accuracy (50%) while a first-order version (one cell per column) reached about 33%; it recovered after the embedded sequences were changed.
  - Minimal performance impact until about 40% of cells were inactivated; at higher cell death it relearned.
  - Capacity estimate: about 320,000 transitions for the stated configuration, scaling linearly with cells per column and patterns per neuron.
- **Limitations / caveats:** Comparison with LSTM and HMM is a qualitative table (continual learning, robustness, locality), not a benchmark; no experiment compares HTM to an LSTM at equal parameters. Results are on one artificial data stream. Biological support for distal-segment prediction is cited, not tested here.
- **Bearing on H049:** Partly supports. The mechanism and a robustness advantage on one artificial task are shown; the specific claim "better than LSTM at equal parameters on noisy sequences" is not tested in the paper and remains the proposed experiment.
- **Reproduce in this repo:** Minimal HTM sequence memory vs a small GRU/LSTM on a noisy high-order sequence stream with matched parameter counts; compare next-element accuracy after a sequence change.

## O'Regan 2001: A sensorimotor account of vision and visual consciousness
- **Cited for:** H050 (learning comes from the sensory results of one's own movements).
- **Link:** https://doi.org/10.1017/s0140525x01000115 · **Basis:** abstract only
- **Question:** Is seeing a way of acting, mastered through sensorimotor contingencies, rather than activation of an internal representation?
- **Method / model:** A theoretical proposal. Per the abstract: the outside world serves as its own representation; the experience of seeing occurs when the organism masters the governing laws of sensorimotor contingency.
- **Experiments:** None run in the paper; it brings forward evidence from sensorimotor adaptation, visual filling-in, visual stability across eye movements, change blindness, sensory substitution and colour perception.
- **Key results:** A theory that accounts for visual consciousness and for differences in the quality of experience across modalities.
- **Limitations / caveats:** A theory of perception and consciousness; the abstract makes no claim about how neural representations are learned.
- **Bearing on H050:** Partly supports. It supports the role of action-contingent sensory change in perception, but the hypothesis as phrased (learning from the sensory results of own movement; active vs passive learner) is a learning claim that the paper does not frame or test. Its explicit anti-representation stance also conflicts with the representation-learning test proposed.
- **Reproduce in this repo:** Agent that sees frames caused by its own actions vs a passive learner shown the same frames; train the same predictive net and compare representation quality (linear probe on position).

## de Sa 1994: Learning classification with unlabeled data
- **Cited for:** H051 (two senses supervise each other; agreement stands in for labels).
- **Link:** http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.891.888 · **Basis:** abstract only
- **Question:** Can structure between pattern distributions in different sensory modalities substitute for class labels?
- **Method / model:** Per the abstract: minimise the disagreement between the outputs of networks that process patterns from different modalities, as an approximation to minimising misclassifications in each.
- **Experiments:** Peterson-Barney vowel dataset (the abstract gives no further details).
- **Key results:** The algorithm performs well in placing codebook vectors, particularly when the confusable classes differ between the two modalities.
- **Limitations / caveats:** Not assessable beyond the abstract; a small dataset (vowels) and a simple codebook-vector model.
- **Bearing on H051:** Supports at the level of the abstract. The "no better than one modality" test is the natural control; the abstract says the benefit is largest when confusable classes differ across modalities.
- **Reproduce in this repo:** Two-view synthetic data (two noisy Gaussian-class views with different class overlaps); train codebooks by minimising output disagreement vs single-view k-means; compare classification error after labelling clusters.

## Krotov 2019: Unsupervised learning by competing hidden units
- **Cited for:** H052 (lateral inhibition plus Hebbian learning, no feedback, can learn deep features).
- **Link:** https://doi.org/10.1073/pnas.1820458116 · **Basis:** full text
- **Question:** Can useful early-layer representations be learned with a local, unsupervised plasticity rule, without backprop?
- **Method / model:** A single hidden layer with global lateral inhibition: dh_mu/dt = I_mu - w_inh r(h_mu) - h_mu, where I_mu is the input current and r = ReLU. After the activities reach a steady state, weights are updated by a Hebbian-like rule with a nonlinear function g(h): positive for the most active unit(s), negative (anti-Hebbian) for weakly active ones, plus a bound on weight norm (Lebesgue norm p = 4 for MNIST). The top layer is then trained with SGD on labels to read out the features.
- **Experiments:** MNIST (2000 hidden units, one hidden layer) and CIFAR-10 (3072 x 2000), compared with the same architecture trained end to end with SGD; permutation-invariant setting.
- **Key results:**
  - MNIST test error 1.52% for the unsupervised-then-linear-readout network, equal to end-to-end SGD (1.5%); train error 0.41%.
  - CIFAR-10: test error 49.25% (biological) vs 44.74% (SGD, early-stopped at 100 epochs).
  - Hidden units learned sub-digit features, not just templates; optimal activation power about 4.5 for the best generalisation.
- **Limitations / caveats:** Only one hidden layer was tested; the paper says additional layers could be trained with the same rule but did not do so. The algorithm is slow (online, waits for steady state per example). The readout layer is trained with labels.
- **Bearing on H052:** Partly supports. It shows lateral inhibition plus Hebbian learning gives good first-layer features without feedback, but "deep features" is overstated for this paper; depth is Journé et al. 2023.
- **Reproduce in this repo:** Single-layer competitive Hebbian net on a small digit-like dataset vs random features and vs SGD features, linear-readout error.

## Journé 2023: Hebbian deep learning without feedback
- **Cited for:** H052 (SoftHebb: Hebbian learning with soft winner-take-all competition and no feedback learns deep features).
- **Link:** https://doi.org/10.48550/arxiv.2209.11883 · **Basis:** full text
- **Question:** Can a multilayer network trained only with local, unsupervised, feedback-free Hebbian plasticity approach backprop accuracy?
- **Method / model:** SoftHebb: softmax competition y_k = exp(u_k)/sum exp(u_l) within a layer; plasticity dw_ik = lr * y_k * (x_i - u_k * w_ik), local to the synapse (Bayesian inference of hidden causes, Moraitis et al. 2021). New soft anti-Hebbian term (negate the update in all but the most active neuron), convolutional layers, one epoch of unsupervised training, followed by a supervised linear classifier on top.
- **Experiments:** MNIST, CIFAR-10, STL-10, ImageNet and ImageNette, up to 5 hidden layers, widths growing 4x per layer; comparisons with random weights, hard winner-take-all and backprop on the same architecture (not on full ImageNet).
- **Key results:**
  - Accuracy (SoftHebb): MNIST 99.35%, CIFAR-10 80.31%, STL-10 76.23%, ImageNet 27.3%, ImageNette 80.98%.
  - Backprop on the same network: MNIST 99.45%, CIFAR-10 83.97%, STL-10 74.51%, ImageNette 85.30%; SoftHebb beat backprop on STL-10.
  - Hard WTA failed to improve with depth; SoftHebb's accuracy kept improving with layers, provided width of deep layers scales (Fig. 4).
- **Limitations / caveats:** The classifier on top is trained with labels; convolution with weight sharing is not literally biological; the authors note random networks often beat Hebbian rules, and report that random layers also gain accuracy to a variable depth.
- **Bearing on H052:** Supports. It shows depth up to 5 layers with a modest CIFAR-10 gap to backprop (about 3.7 points). The proposed test "gap does not close with depth" needs care since width scaling matters.
- **Reproduce in this repo:** Stack 2-3 soft-WTA Hebbian layers (softmax with temperature, the update above) on a small image set; compare linear-probe accuracy per layer to a random-weight network and to a backprop net.

## Diehl 2015: Unsupervised learning of digit recognition using spike-timing-dependent plasticity
- **Cited for:** H053 (spiking STDP with winner-take-all and homeostasis learns digit prototypes without labels).
- **Link:** https://doi.org/10.3389/fncom.2015.00099 · **Basis:** full text
- **Question:** Can a spiking network with STDP, lateral inhibition and homeostasis learn MNIST digits unsupervised?
- **Method / model:** Conductance-based leaky integrate-and-fire neurons. Input pixels are Poisson spike trains (rate proportional to intensity); 784 inputs project to a layer of excitatory neurons, each connected one-to-one to an inhibitory neuron that inhibits all other excitatory neurons (winner-take-all). STDP uses synaptic traces; weights are normalised divisively; an adaptive membrane threshold gives homeostasis. Labels are used only afterward to assign each neuron a class from its responses to the training set; the weights are learned without labels.
- **Experiments:** MNIST (60,000 train, 10,000 test). Networks with 100, 400, 1600 and 6400 excitatory neurons; three STDP variants (power-law, exponential weight dependence, pre-and-post/triplet).
- **Key results:**
  - Test accuracy 82.9%, 87.0%, 91.9% and 95.0% for 100, 400, 1600 and 6400 neurons (power-law/default rule); about 200,000 examples before performance plateaued.
  - Accuracy grows with the number of neurons because each learns a prototype of a digit variant.
  - Compared with other spiking networks on MNIST in the paper's Table 1.
- **Limitations / caveats:** Needs a labelled assignment step after training; performance tied to network size; a rate-coded image input; simulation of spiking dynamics is expensive. Static MNIST only.
- **Bearing on H053:** Supports. "Learns digit prototypes without labels" matches the paper, with the caveat that a small labelled set is used to name the neurons. The row already notes MNIST was shown; the Brain World transfer is untested.
- **Reproduce in this repo:** Rate-based WTA with a trace-STDP-like Hebbian update and an adaptive threshold on digit-like patterns; compare accuracy vs number of units and verify the units are prototypes.

## Feldman 2010: Attention, uncertainty, and free-energy
- **Cited for:** H054 (prediction errors precision-weighted by attention, so most input causes no learning).
- **Link:** https://doi.org/10.3389/fnhum.2010.00215 · **Basis:** full text
- **Question:** Can attention be modelled as inferring the precision (inverse variance) of sensory signals during hierarchical perception, via synaptic gain on prediction-error units?
- **Method / model:** Generalised predictive coding derived from free-energy minimisation for a hierarchical dynamic model with state-dependent noise. Precision modulates the post-synaptic gain of prediction-error units (attention is the optimisation of gain). Recognition dynamics are ordinary differential equations on states, gain and efficacy.
- **Experiments:** Neuronal simulations of the Posner cueing paradigm (valid and invalid cues, varying stimulus onset asynchrony) and of biased competition.
- **Key results:**
  - The model reproduces validity effects on reaction time and their time course; a cost/benefit asymmetry for invalid and valid trials.
  - Early P1-like attentional enhancement is attributed to boosting of sensory prediction errors; later P3-like invalidity effects to prediction errors about context.
  - Biased competition emerges because only one context can exist at a time, and the context distributes precision over sensory channels.
- **Limitations / caveats:** A minimal, simplified model on a perceptual-inference task. Learning is mentioned but explicitly left for future work (the paper focuses on activity-dependent gain, not slower learning of when to apply it). No energy or sample-efficiency measures.
- **Bearing on H054:** Partly supports; the gain/precision weighting of prediction errors is exactly what the paper models, but "most input causes no learning" and sample savings are not tested; the paper is about inference and attention, not learning.
- **Reproduce in this repo:** Two-level predictive-coding net with a per-channel precision weight on errors vs unweighted; count samples to reach a given error when half the input channels are noisy.

## Corrections to the hypotheses file
- **H041:** Lotter et al. 2017 (PredNet) does not compare to V1 receptive fields; it is a video-prediction ML paper trained with backprop. Move it to a "prediction as a learning signal" note, or reword; Singer et al. 2018 alone carries the V1/A1 claim. Also the control in Singer is a sparse coding model, not a generic "non-predictive model".
- **H043:** The measured gap between local CLAPP and end-to-end training is moderate (about 6-7 points on STL-10: 73.6-74.0% vs 80.3%), not "large". Reword the test to a quantitative threshold.
- **H044:** The note on LeCun 2022 could not use the paper text (OpenReview blocked and sources.json has no abstract). The citation is a position paper and cannot support a claim about cortex; add a neuroscience or experimental source or mark it as AI-motivated speculation.
- **H047:** The cited paper's title and abstract speak of "multidimensional scaling of streaming data" (strain cost); the phrase "similarity matching" is the later name. Mention that the paper is an exact derivation (not just a motivation).
- **H048:** The column-voting mechanism is described in Hawkins et al. 2017 (Front Neural Circuits, "A theory of how columns in the neocortex enable learning the structure of the world") and Lewis et al. 2018; the 2019 grid-cell paper is a theory paper without voting simulations. Add the 2017 paper as a source.
- **H049:** The 2016 paper contains no LSTM benchmark, only a qualitative comparison table; the "worse than LSTM at equal parameters" test is new work, not a replication. Also the local PDF is the 2015 submitted manuscript.
- **H050:** O'Regan and Noë is a theory of visual consciousness, anti-representational; it motivates active sensing but does not provide a learning claim. Reword "Learning comes from..." to "Perception is constituted by...", or cite an active-learning source.
- **H052:** Krotov and Hopfield 2019 tested one hidden layer only; depth results belong to Journé et al. 2023 (up to 5 layers, with a classifier trained on labels). Reword to "depth" only for Journé.
- **H054:** Feldman and Friston 2010 models precision-weighted prediction errors in attention and inference; it does not model learning or sample savings. The "most input causes no learning" clause is the hypothesis's extension.
