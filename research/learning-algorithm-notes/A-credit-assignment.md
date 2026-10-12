# Paper notes: A. Credit assignment

Structured notes on the 22 sources cited by hypotheses H001-H020 in `research/learning-algorithm-hypotheses.md`, generated 2026-10-12 from the local PDFs, web full texts, or abstracts as marked per note. Every number below comes from the text read; where only an abstract was available, little is claimed.

## Whittington 2017: An Approximation of the Error Backpropagation Algorithm in a Predictive Coding Network with Local Hebbian Synaptic Plasticity
- **Cited for:** H001 (predictive coding networks compute weight updates that converge to backprop's gradients using only local errors)
- **Link:** https://doi.org/10.1162/neco_a_00949 · **Basis:** full text (web; PMC5467749, first ~100k characters read)
- **Question:** Can a predictive coding network learn supervised tasks with only local Hebbian plasticity, and how close are its weight changes to backprop's?
- **Method / model:** Each layer has value nodes x and prediction-error nodes e (value minus top-down prediction). Inference relaxes activity to equilibrium with input clamped and, during learning, output clamped to the target. Weights change by presynaptic activity times postsynaptic error node (Hebbian). The error-node variances Sigma(l) set precision; the derivation assumes linear output nodes.
- **Experiments:** Toy 3-layer network with one node per layer (300 samples, outputs tanh(tanh(s_in))), angle comparisons with Sigma(0) in {1, 8, 256}; MNIST 784-600-600-10 sigmoid net vs an ANN with backprop (10 runs, batch 20, Adam lr 0.001, 20 inference steps, Sigma(0) = 1 or 100).
- **Key results:**
  - Weight changes equal backprop's when predictions equal the targets, and are similar when they are close.
  - A large Sigma(0) relative to the other Sigma(l) (weak clamping of the output) drives the weight change toward backprop's in the limit; the paper states it converges.
  - MNIST: 0.00% training error and 1.7-1.8% validation error for all networks, learning rate not tuned.
- **Limitations / caveats:** Convergence is a limit result (error-node activity near zero). Authors list: one-to-one value/error node pairing, symmetric weights, negative-valued error nodes, fixed rather than learned Sigma, only 20 inference steps in MNIST.
- **Bearing on H001:** Supports, with the proviso that equality holds in a parameter limit (large output variance / small errors), not for any setting. The row's falsifier ("cosine stays low at equilibrium") is therefore a test of the regime, not of the paper's claim.
- **Reproduce in this repo:** Tiny MLP, PC inference to equilibrium with output nudged; sweep output-layer variance and report cosine between PC weight updates and backprop gradients.

## Lillicrap 2016: Random synaptic feedback weights support error backpropagation for deep learning
- **Cited for:** H002 (fixed random feedback weights suffice; forward weights align to them)
- **Link:** https://doi.org/10.1038/ncomms13276 · **Basis:** full text
- **Question:** Is backprop's symmetric feedback (W transpose) needed, or can random fixed B deliver useful teaching signals?
- **Method / model:** Feedback alignment (FA): output weights update as in backprop; hidden weights update by delta W0 proportional to B e x^T (B fixed random) instead of W^T e x^T. In nonlinear nets the rule is three-factor: modulator d_j times input x_i times a function of postsynaptic activity. Mechanism: information about B flows into W0 and then into W, so W aligns with B^T (possibly with B's pseudoinverse).
- **Experiments:** Linear 3-layer function fitting vs shallow, reinforcement-style, backprop; MNIST 784-1000-10 logistic net (20 runs); 4-layer function fitting; 50% sparse W and B; stochastic spiking 784-1500-1500-1500-1000 net on MNIST; SVHN and deeper/wider nets in the supplement.
- **Key results:**
  - Angle between FA and backprop modulator vectors starts near 90 degrees, shrinks, but never reaches zero.
  - MNIST test error: backprop 2.4%, FA 2.1%, shallow 7.2%.
  - Spiking 3-hidden-layer net: 1.8% test error.
  - Freezing phases (Fig. 5c) show learning in the hidden layer becomes effective only after W aligned with B^T.
- **Limitations / caveats:** Small/medium networks; proofs only under restricted conditions (supplement). Authors state it leaves open how errors are computed and how feedforward/feedback pathways interact. Later work (Akrout 2019, below) finds FA fails on ImageNet.
- **Bearing on H002:** Supports on MNIST-scale tasks. The row's falsifier (FA fails to learn hidden layers on MNIST/XOR) is contradicted by the paper's own control experiments; the open question is scaling.
- **Reproduce in this repo:** MLP on XOR/MNIST subset: backprop vs FA (fixed random B); log test error and the angle between FA and backprop hidden-layer updates.

## Nokland 2016: Direct Feedback Alignment Provides Learning in Deep Neural Networks
- **Cited for:** H003 (output error broadcast straight to every layer through random weights)
- **Link:** https://doi.org/10.48550/arxiv.1609.01596 · **Basis:** full text (web; arXiv PDF text extracted)
- **Question:** Can hidden layers be trained from a zero initial condition with the output error sent directly via fixed random matrices, skipping layer-by-layer backward passes?
- **Method / model:** For hidden layer i, delta a_i = (B_i e) times f'(a_i), with e = y_hat - y and B_i fixed random (DFA). Compared with backprop (W^T) and FA (chain of B). Theorem 1: with constant update directions per data point, the layerwise criterion K being minimised raises an alignment criterion L, so a feedback path with L > 0 gives a descent direction (does not prove convergence). Indirect FA (IFA) also tested.
- **Experiments:** MNIST (2x800 and other tanh/logistic/ReLU nets, 7x240, 100x240), CIFAR-10/100 (1x1000, 3x1000, conv), dropout and adversarial regularisation, RMSprop, zero init for FA/DFA; BP, FA, DFA compared; t-SNE of features.
- **Key results:**
  - MNIST test error 2x800 tanh: BP 1.60%, FA 1.64%, DFA 1.74%; with dropout BP 1.26%, DFA 1.45%.
  - 7x240 tanh: BP 2.16%, FA 2.20%, DFA 2.32% (difference target propagation reported 1.94%); only DFA trained the 100x240 net (3.92%).
  - CIFAR-10 conv tanh: BP 22.5%, FA 27.1%, DFA 26.9%; CIFAR-100 conv: BP 51.7%, FA 60.5%, DFA 59.0%.
  - Frozen-first-layer experiment: unfreezing with DFA first raises then lowers training error to 0%, so the hidden layer learns useful features.
- **Limitations / caveats:** Gap to BP grows for conv nets and CIFAR-100. DFA gives no improvement if layers above are not adapted. Error is "almost local" but the output error must reach every layer.
- **Bearing on H003:** Contradicts the falsifier: DFA reaches test errors close to full backprop and clearly beyond a readout-only baseline on MNIST. Supports the claim as phrased; scaling to hard tasks is weak.
- **Reproduce in this repo:** 3-layer MLP on a small digits set: backprop vs DFA vs train-readout-only, same init and lr.

## Payeur 2021: Burst-dependent synaptic plasticity can coordinate learning in hierarchical circuits
- **Cited for:** H004 (event rate carries the feedforward signal, burst probability carries the error)
- **Link:** https://doi.org/10.1038/s41593-021-00857-x · **Basis:** abstract only (full text not retrievable: bioRxiv/Nature returned 403)
- **Question:** Can burst-regulated plasticity in pyramidal neurons solve credit assignment in hierarchical networks?
- **Method / model:** From the abstract: plasticity regulated by high-frequency bursts, combined with short-term synaptic dynamics, regenerative apical-dendrite activity and plasticity in feedback pathways.
- **Experiments:** Abstract says simulations and mathematical analyses; "challenging tasks that require deep network architectures". Specific tasks, sizes and numbers not available to me.
- **Key results:** Abstract-level claim only: the rule can solve tasks that need deep architectures.
- **Limitations / caveats:** Cannot be assessed from the abstract.
- **Bearing on H004:** Partly supports (the abstract matches the multiplexing idea, though it does not use the word "multiplex"). Whether XOR or deeper tasks were solved is not stated in the abstract, so the row's falsifier is untested here.
- **Reproduce in this repo:** Spiking or rate net with burst-gated plasticity on XOR; compare to a rule using total event rate only.

## Sacramento 2018: Dendritic cortical microcircuits approximate the backpropagation algorithm
- **Cited for:** H005 (apical dendrites compare top-down predictions with somatic activity; the mismatch acts as the error)
- **Link:** https://doi.org/10.48550/arxiv.1810.11393 · **Basis:** full text (web; arXiv PDF text extracted)
- **Question:** Can a layered network of three-compartment pyramidal cells plus lateral interneurons approximate backprop continuously in time, without separate phases?
- **Method / model:** Pyramidal cells have basal (bottom-up), apical (top-down + lateral) and somatic compartments; a lateral interneuron population (SST-like) learns to predict the next layer's pyramidal activity and cancels top-down input. The apical voltage is the error, produced by the mismatch between top-down input and interneuron prediction. Output neurons are weakly nudged toward targets. Plasticity follows Urbanczik-Senn-style dendritic prediction of somatic activity at basal synapses. Analytically, in the weak-feedback limit, the updates equal backprop's when top-down weights equal the transposed forward weights; with fixed random top-down weights it reduces to feedback alignment.
- **Experiments:** Regression (30-50-10 pyramidal net learning a random 30-20-10 teacher); MNIST with 784-500-500-10 net (55000/5000 train/val split).
- **Key results:**
  - MNIST test error 1.96% (backprop reference 1.53%, single-layer shallow 8.4%).
  - 2.11% with two fully trained hidden layers variant noted in text; 2.48% for the 784-1000-10 net with learned top-down weights.
  - Network reaches a self-predicting state in which the apical compartment is silent without a target.
- **Limitations / caveats:** Analysis is in the weak-feedback limit; simulations use strong feedback outside it. I found no direct angle-vs-backprop measurement in the text. Interneuron-specific wiring is a model prediction.
- **Bearing on H005:** Partly supports, but the row's wording is off: in this model the apical error is top-down input minus the lateral interneuron prediction, not top-down vs somatic activity. The somatic-vs-dendritic comparison is Urbanczik and Senn's basal rule. Row phrasing should be corrected.
- **Reproduce in this repo:** Two-layer rate model with apical error = top-down minus learned lateral prediction; track cosine of hidden-layer updates with backprop.

## Urbanczik 2014: Learning by the Dendritic Prediction of Somatic Spiking
- **Cited for:** H005, H019 (dendritic prediction of somatic spiking; prediction error drives plasticity)
- **Link:** https://doi.org/10.1016/j.neuron.2013.11.030 · **Basis:** abstract only (abstract from PubMed; sources.json abstract empty)
- **Question:** Can one local plasticity rule for dendritic synapses minimise the discrepancy between somatic firing and a local dendritic potential?
- **Method / model:** Compartmental neuron with a non-Hebbian three-factor rule: presynaptic activity, postsynaptic firing, and a local dendritic potential. Prediction errors come from stochastic fluctuations or from synaptic input that targets the soma directly.
- **Experiments:** Not described in the abstract.
- **Key results:** Abstract states: depending on the nature of the direct somatic input the rule gives supervised or unsupervised learning; a reward signal modulating the learning rate gives reinforcement learning.
- **Limitations / caveats:** Nothing beyond the abstract was read.
- **Bearing on H019:** Supports (the abstract states dendrites predict somatic firing and the discrepancy drives plasticity). Bearing on H005: supports only the somatic-vs-dendritic part; the "top-down" apical comparison is Sacramento's.
- **Reproduce in this repo:** One-neuron model, dendritic weights learning to reproduce a teacher's somatic output; check the learned weights approach the teacher's.

## Scellier 2017: Equilibrium Propagation: Bridging the Gap between Energy-Based Models and Backpropagation
- **Cited for:** H006 (two phases: free, then gently nudged; learn from the difference)
- **Link:** https://doi.org/10.3389/fncom.2017.00024 · **Basis:** full text
- **Question:** Can an energy-based recurrent network with a weakly clamped second phase compute backprop-like gradients with a local rule?
- **Method / model:** Symmetric-weight Hopfield-style network with total energy F = E + beta C, C a squared output cost. Free phase (beta = 0) settles to a fixed point; weakly clamped phase (beta > 0) nudges outputs toward targets and the perturbation propagates backward through hidden layers. Update: delta W_ij proportional to (1/beta)(s_i^beta s_j^beta - s_i^0 s_j^0), which equals the gradient of the objective in the limit beta to 0; equivalent to a rule using the temporal derivative of postsynaptic activity (STDP-like).
- **Experiments:** Permutation-invariant MNIST, networks with 1, 2 and 3 hidden layers of 500 units, GPU implementation.
- **Key results:**
  - 0.00% training error; generalisation (test) error between 2% and 3% depending on architecture.
  - Free-phase relaxation needs many iterations, growing fast with the number of layers (Table 2).
- **Limitations / caveats:** Requires symmetric weights (authors flag this as the main biological issue); long free-phase relaxation; static inputs only. I saw no side-by-side backprop run in the text I read.
- **Bearing on H006:** Supports as a mechanism claim (two phases give gradient-like updates). The paper does not claim the brain runs it, and does not test the falsifier (failure where backprop succeeds).
- **Reproduce in this repo:** Small energy net: free and nudged phases, compare delta W with backprop gradient for a small beta, then train on a toy task.

## O'Reilly 1996: Biologically Plausible Error-Driven Learning Using Local Activation Differences: The Generalized Recirculation Algorithm
- **Cited for:** H007 (contrastive Hebbian learning between minus and plus phases is cortex's error-driven rule)
- **Link:** https://doi.org/10.1162/neco.1996.8.5.895 · **Basis:** full text (web; ccnlab.org PDF)
- **Question:** Can error backprop be computed with local activation differences, and how does that relate to contrastive Hebbian learning (CHL)?
- **Method / model:** GeneRec: recurrent sigmoidal network with a minus (expectation) phase and a plus (outcome) phase; the hidden-unit error is the difference between plus- and minus-phase activations. GeneRec computes the same error derivatives as Almeida-Pineda recurrent backprop if weights are symmetric. CHL is shown to be a symmetry-preserving GeneRec with a midpoint-method approximation, explaining faster learning.
- **Experiments:** XOR (50 networks), 4-2-4 encoder (50), shifter (10), family trees (10) with BP, AP and GeneRec variants. Metric: epochs to criterion and number of networks solving.
- **Key results:**
  - XOR epochs: BP 305, AP 164, plain GeneRec 3795 (rarely succeeds), GR Sym 334, GR Mid 97, CHL 59.
  - Shifter: plain GeneRec and GR Mid did not learn; GR Sym 409 epochs, CHL 328, BP 129, AP 181.
  - Family trees: CHL solves it reliably (with 18 encoding / 18 hidden units), in roughly the same epochs as AP; GeneRec without symmetry fails.
  - A biological mechanism is proposed (two activation states in quick succession in cortex).
- **Limitations / caveats:** Small tasks; symmetric weights needed; the author notes a biologically plausible backprop variant does not make all backprop forms plausible.
- **Bearing on H007:** Supports the mechanism (CHL/GeneRec approximates backprop and learns the tasks tested). It does not test cortical use, and the row's falsifier is about accuracy while the paper measures epochs; it reports comparable, not large-gap, results once symmetry is enforced.
- **Reproduce in this repo:** Settling network with minus/plus phases and CHL update on XOR and a 4-2-4 encoder; compare epochs with backprop.

## Lee 2015: Difference Target Propagation
- **Cited for:** H008 (each layer learns to hit a target sent from above, not a gradient)
- **Link:** https://doi.org/10.1007/978-3-319-23528-8_31 · **Basis:** full text
- **Question:** Can targets, not gradients, be propagated down a network, even for discrete and stochastic units?
- **Method / model:** Each layer has a feedforward map f_i and a learned approximate inverse g_i. Targets: h_hat_{i-1} = h_{i-1} + g_i(h_hat_i) - g_i(h_i) (the "difference" correction). Each f_i is trained on a layer-local loss ||f_i(h_{i-1}) - h_hat_i||^2; the top layer uses the true loss. Inverses g_i train on a local denoising reconstruction loss.
- **Experiments:** MNIST 7 hidden layers of 240 tanh units (RMSprop); CIFAR-10 3072-1000-1000-1000-10; discrete-transmission nets; stochastic binary 784-200-200-10 net; a backprop-free autoencoder.
- **Key results:**
  - MNIST test error 1.94% (target prop) vs 1.86% (backprop); ReLU: 3.15% vs 1.62%.
  - CIFAR-10 test accuracy 50.71% (target prop) vs 53.72% (backprop).
  - Stochastic nets: 1.54% (best reported for stochastic nets then) vs 1.71% straight-through baseline.
- **Limitations / caveats:** Weak with ReLU; small networks; Nokland 2016 reports TP at 1.94% vs FA 2.20% on the same 7x240 setup.
- **Bearing on H008:** Contradicts the falsifier ("much worse than FA on MNIST"): DTP matches backprop closely and beats FA/DFA in the 7x240 comparison. Supports the claim as phrased.
- **Reproduce in this repo:** 4-layer tanh MLP with learned inverses; DTP vs FA vs backprop on a small digit set.

## Akrout 2019: Deep Learning without Weight Transport
- **Cited for:** H009 (feedback weights become symmetric through their own local rule)
- **Link:** https://doi.org/10.48550/arxiv.1904.05391 · **Basis:** full text (web; arXiv PDF text extracted)
- **Question:** Can the feedback path learn the transpose of the forward weights without weight transport, on hard tasks where FA fails?
- **Method / model:** Weight mirror (WM): in a mirror mode, drive forward neurons with noise x, and update B by delta B proportional to x y^T (with weight decay), so B converges to a multiple of W^T. Kolen-Pollack (KP): feedback weights receive the same local update as forward weights plus weight decay, so B converges to W^T. Compared with FA and sign-symmetry (SS).
- **Experiments:** ImageNet, ResNet-18 and ResNet-50, up to 140 epochs; matrix angles between B and W^T per layer.
- **Key results:**
  - ResNet-18 top-1 error: WM 30.2%, KP 29.2%, FA 97.4%, SS 39.2%, backprop 30.1%.
  - ResNet-50: WM 23.4%, KP 23.9%, FA 98.9%, SS 33.8%, backprop 22.9%.
  - WM keeps matrix angles under 12 degrees; KP brings angles near zero within 20 epochs; FA angles stay above 80 degrees in most layers.
- **Limitations / caveats:** Authors note KP's convergence rate depends on weight decay, with no proof a good balance always exists; more tests needed in other architectures. WM needs a separate mirror mode.
- **Bearing on H009:** Supports the claim; the row's falsifier (angle does not shrink) is contradicted for these ImageNet runs. The paper also gives the strongest evidence that plain FA (H002) does not scale.
- **Reproduce in this repo:** Two-layer MLP: update B with the same delta as W plus weight decay; plot angle(B, W^T) over training.

## Williams 1992: Simple statistical gradient-following algorithms for connectionist reinforcement learning
- **Cited for:** H010 (perturb activity or weights and correlate with reward; node perturbation, REINFORCE)
- **Link:** https://doi.org/10.1007/bf00992696 · **Basis:** full text
- **Question:** Which simple update rules for stochastic units follow the gradient of expected reinforcement?
- **Method / model:** REINFORCE: delta w_ij = alpha_ij (r - b_ij) * d ln g_i / d w_ij, i.e. learning rate times (reward minus baseline) times characteristic eligibility. Theorem 1: the inner product of E[delta W | W] with the gradient of E[r | W] is non-negative, and equals alpha times the gradient if alpha is uniform. Episodic and delayed-reward versions, Gaussian units, and compatibility with backprop are treated.
- **Experiments:** Analytical paper; no simulation results presented.
- **Key results:**
  - Updates are unbiased estimates of the reward gradient without computing the gradient explicitly.
  - Special cases include Bernoulli-logistic units and the linear reward-inaction rule.
  - Author states REINFORCE is "generally very slow even when it succeeds" and episodic REINFORCE especially slow, since it spreads credit uniformly over past times.
- **Limitations / caveats:** Convergence properties poorly understood; high variance (hence baselines). No neural or scaling data.
- **Bearing on H010:** Supports the gradient-following claim and the slowness; it does not discuss node perturbation by name, birdsong, or network-size scaling, so the ~100 unit threshold in the falsifier is not from this paper.
- **Reproduce in this repo:** REINFORCE on a one-hidden-layer stochastic net; time to reach a fixed loss vs hidden width (10 to 1000 units).

## Fiete 2006: Gradient Learning in Spiking Neural Networks by Dynamic Perturbation of Conductances
- **Cited for:** H010 (perturbation works in small circuits such as birdsong)
- **Link:** https://doi.org/10.1103/physrevlett.97.048104 · **Basis:** full text
- **Question:** How can the gradient of an objective w.r.t. synaptic weights of a spiking recurrent network be estimated from fluctuations caused by perturbing conductances?
- **Method / model:** Perturb the conductance g_i(t) of each neuron (white noise) rather than weights; a "sensitivity lemma" shows the weight gradient is obtained from the covariance of reward with the perturbation weighted by a local eligibility, so N conductance perturbations estimate N^2 weight gradients. Update delta W_ij = (R - R0) times eligibility e_ij; the perturbations could be provided by "empiric" synapses driven by an external random spike train; a critic broadcasts a scalar reward R.
- **Experiments:** None reported in this paper; the application to a model of birdsong is cited as developed elsewhere (refs 12, 13, a thesis and a submitted paper).
- **Key results:** Derivation only: generalises node perturbation to recurrent spiking networks with parallel perturbation; compatible with conductance-based neurons and dynamic synapses; requires inputs to a neuron to combine additively.
- **Limitations / caveats:** Relies on additive input combination; baseline choice affects learning time; biological realisation of "empiric" synapses is hypothesised.
- **Bearing on H010:** Partly supports (theory for perturbation learning). The birdsong claim is not demonstrated here; the row should cite the birdsong model papers if that claim is kept. No scaling data for the ~100 unit threshold.
- **Reproduce in this repo:** Node perturbation on an MLP: learning time vs hidden size compared with weight perturbation and backprop.

## Hinton 2022: The Forward-Forward Algorithm: Some Preliminary Investigations
- **Cited for:** H011 (two forward passes, positive and negative data, with a per-layer goodness replace backward passes)
- **Link:** https://doi.org/10.48550/arxiv.2212.13345 · **Basis:** full text
- **Question:** Can layers learn with two forward passes, each with a local objective, instead of backprop?
- **Method / model:** Each layer is trained to give high goodness (sum of squared ReLU activities) on positive (real) data and low on negative data, relative to a threshold; the activity vector is length-normalised before the next layer so only its orientation passes on. Negative data: hybrid images (mask-mixed digits) or the same image with a wrong label; later a recurrent version with top-down input.
- **Experiments:** MNIST (4x2000 ReLU nets, local receptive fields, recurrent net with top-down input), CIFAR-10 (2-3 hidden layers of 3072 ReLUs, 11x11 receptive fields).
- **Key results:**
  - MNIST test error: 1.37% (hybrid-image negatives, 4x2000), 1.36% (label-as-input, 60 epochs), 1.31% (recurrent), 0.64% with local receptive fields on jittered data; backprop MLP reference about 1.4%.
  - CIFAR-10 test error: BP 37% (2 layers) vs FF 41-46% depending on goodness and test procedure; 3 layers BP 39% vs FF 41-46%.
  - Gap between BP and FF does not grow with more hidden layers (per author).
- **Limitations / caveats:** Author says FF is somewhat slower than backprop and generalises a bit worse; separating positive and negative phases (wake/sleep) did not replicate and an earlier positive result was probably a bug (Section 5, listed as the most important open question).
- **Bearing on H011:** Supports as an algorithm, but not as a brain claim: the paper presents it as a possible model of cortex, with negative-phase generation an open problem. The row's falsifier (no better than a random-feature readout) is not tested; the paper compares only with backprop.
- **Reproduce in this repo:** FF on MNIST/digits with label-embedded negatives; compare to a random-feature readout of equal width.

## Hinton 1995: The "Wake-Sleep" Algorithm for Unsupervised Neural Networks
- **Cited for:** H012 (alternating wake and sleep phases train recognition and generative paths with local rules)
- **Link:** https://doi.org/10.1126/science.7761831 · **Basis:** full text (web; Toronto author preprint dated 3 April 1995, not the journal version)
- **Question:** How can recognition and generative weights of a multilayer stochastic network be learned without a teacher, using only local information?
- **Method / model:** Wake phase: recognition weights drive the units, and generative weights are adapted to better reconstruct the layer below (local delta rule). Sleep phase: generative weights drive the network from top to bottom and recognition weights are adapted to recover the generating activities. The objective is description length / Helmholtz free energy; recognition distributions are factorial.
- **Experiments:** Toy 4x4 bar-image model (Fig. 2) and 8x8 binary handwritten digits (CEDAR CDROM, 700 examples per digit): ten 64-16-16-4 digit-specific networks and one 64-32-32-16 network, 500 sweeps, lr 0.01.
- **Key results:**
  - The toy generative model is learned correctly; KL between recognition and true posterior is 0.08 bits after learning.
  - Digit classification via description length: 4.8% error vs 6.7% nearest neighbour and a minimum of 5.6% for a supervised one-hidden-layer net.
  - Average code length per test digit: 59.0 bits (pixel base rates), 33.8 bits (ten digit networks), 37.3 bits (single network).
- **Limitations / caveats:** Sleep phase trains recognition on fantasy data, which differs from real data early on; factorial recognition is a serious restriction (authors argue it is not fatal). Not a statement about the brain's sleep.
- **Bearing on H012:** Supports (the algorithm as stated is local and phase-alternating). The paper claims no biological sleep correspondence.
- **Reproduce in this repo:** Small Helmholtz machine on bars data; track description length of real data over wake/sleep sweeps.

## O'Reilly 2021: Deep Predictive Learning in Neocortex and Pulvinar
- **Cited for:** H013 (the pulvinar supplies the outcome phase every ~100 ms alpha cycle)
- **Link:** https://doi.org/10.1162/jocn_a_01708 · **Basis:** full text (arXiv version 2006.14800)
- **Question:** Can the thalamocortical circuit implement predictive error-driven learning with a temporal-difference signal?
- **Method / model:** Layer 6CT cortical cells send many weak projections to the pulvinar, generating a prediction in the first ~75 ms of each ~100 ms alpha cycle; layer 5IB bursting cells provide the outcome as a strong driver input in the last ~25 ms. The prediction-to-outcome difference in activation drives local plasticity (Leabra, a GeneRec/CHL descendant).
- **Experiments:** Reber finite-state grammar sequence prediction; a large-scale visual model (V1 to IT) trained only to predict the next of 8 movie frames of 156 3D objects from 20 basic-level categories, with saccades; comparison to backprop (Bp) and PredNet variants; RSA vs human similarity ratings (30 participants) and macaque IT data.
- **Key results:**
  - Grammar model needed about 20 epochs of 25 sequences to reach 5 error-free epochs in a row.
  - IT layers develop category structure that diverges progressively from V1 similarity, with no category labels.
  - Bp and PredNet comparison networks showed no significant progressive divergence in higher layers.
- **Limitations / caveats:** The biological mapping is a hypothesis; the model is large and tuned. The paper's testable predictions are blocking 5IB bursting, blocking plasticity in 6CT-to-pulvinar synapses early in development, and LTD/LTP on alpha timescale depending on prediction vs outcome activity.
- **Bearing on H013:** Partly supports (it proposes exactly this mechanism and shows a working model). The row's T3 test (pulvinar silencing blocks predictive learning) is close to, but not one of, the paper's stated predictions; those concern 5IB bursting and 6CT plasticity.
- **Reproduce in this repo:** Sequence predictor with a minus phase (prediction) and plus phase (next input) and a difference-based update; compare with a model using the plus phase only.

## Bellec 2020: A solution to the learning dilemma for recurrent networks of spiking neurons
- **Cited for:** H014 (eligibility traces plus broadcast learning signal, not BPTT)
- **Link:** https://doi.org/10.1038/s41467-020-17236-y · **Basis:** full text
- **Question:** Can recurrent spiking networks learn online with local eligibility traces and top-down learning signals, approaching BPTT?
- **Method / model:** e-prop: delta W_ji = sum_t L_j^t e_ji^t, where e_ji^t is a locally computed eligibility trace (including slow components for adapting neurons) and L_j^t a learning signal. Variants: symmetric e-prop (learning-signal weights equal the readout weights), random e-prop (fixed random broadcast weights, like broadcast alignment), adaptive e-prop. Networks: LSNNs with LIF and adapting (ALIF) neurons.
- **Experiments:** TIMIT phoneme recognition (framewise, 800 neurons; sequence-level, 2400 neurons), a cue-accumulation task with a delay of 500-1500 ms in a 2250 ms trial (learning signals non-zero only in the last 150 ms; first cues at 1050 ms before), reward-based e-prop on Atari Pong, sparse Dale's-law LSNN.
- **Key results:**
  - e-prop approximates BPTT performance on both TIMIT versions and learns slower than BPTT.
  - The cue task is solved by symmetric, random and adaptive e-prop with LSNNs, while BPTT on a plain RSNN without adapting neurons does not solve it.
  - Failure case: symmetric e-prop fails if hidden feedforward layers block the future gradient route, while BPTT still works (Supp. Fig. 8).
- **Limitations / caveats:** Authors know of no task where random e-prop clearly fails, but expect failures like broadcast alignment in deep feedforward nets. The longest dependency tested is about one to two seconds.
- **Bearing on H014:** Supports the mechanism. The row's falsifier (fails at delays over a few seconds) is untested: the paper's longest demonstrated gap is around 1-2 s.
- **Reproduce in this repo:** Rate RNN with e-prop traces vs BPTT on a delayed-recall task; sweep delay length.

## Jaderberg 2017: Decoupled Neural Interfaces using Synthetic Gradients
- **Cited for:** H015 (predict the future error signal so layers need not wait)
- **Link:** https://doi.org/10.48550/arxiv.1608.05343 · **Basis:** full text (web; arXiv PDF text extracted)
- **Question:** Can modules be trained without update locking by predicting the error gradient with a learned model?
- **Method / model:** Each module i has a synthetic-gradient model M_{i+1} that predicts dL/dh_i from h_i (optionally conditioned on labels, cDNI); the module updates immediately with the prediction, and M is regressed onto the true (or bootstrapped) gradient when it arrives. For RNNs, predicting future gradients extends effective BPTT horizon.
- **Experiments:** MNIST/CIFAR-10 FCNs and CNNs with 3-6 layers; copy, repeat-copy and Penn Treebank RNNs; a two-RNN multi-network system; stochastic layer updates (p_update); fully unlocked training.
- **Key results:**
  - MNIST FCN 3 layers: backprop 2.0% vs DNI 1.9% error; CIFAR-10 CNN 3 layers: BP 17.9%, DNI 19.5%, cDNI 19.0%; CIFAR-10 FCN 5 layers: BP 42%, DNI 47%, cDNI 44%.
  - cDNI trained 21-layer MNIST FCNs to 2% error.
  - Layers updated with only 5% update probability still trained to near 2% on MNIST (slower).
  - PTB LSTM: DNI with future synthetic gradients at T=5 matched vanilla LSTM at T=20 and needed 58% of the data (2x faster wall clock to 1.35 BPC).
- **Limitations / caveats:** A machine learning paper; it makes no cerebellum claim. Stale-gradient baselines are far worse (9.1% to 19.0% on 3-6 layer MNIST).
- **Bearing on H015:** Does not test the cerebellar claim; it supports only the "learned gradient predictor allows decoupled updates" half. The cerebellum mapping belongs to Boven 2023.
- **Reproduce in this repo:** MLP with a linear synthetic-gradient module per layer; compare accuracy and update-delay robustness with backprop.

## Boven 2023: Cerebro-cerebellar networks facilitate learning through feedback decoupling
- **Cited for:** H015 (cerebellum predicts the future error signal for cortex)
- **Link:** https://doi.org/10.1038/s41467-022-35658-8 · **Basis:** full text
- **Question:** Can a cerebellar network predicting cerebral feedback explain faster cortical learning and dysmetria after cerebellar damage?
- **Method / model:** Cerebral area as an RNN (cRNN) plus a feedforward cerebellar module C that predicts the feedback signal from current cerebral activity (ccRNN). C is trained by an inferior-olive-like error between actual and predicted feedback, using self-predictions (bootstrapping) when real feedback is missing. The scheme follows Jaderberg's synthetic gradients.
- **Experiments:** Seven-target line-drawing sensorimotor task; online line/digit drawing from MNIST pixel rows; online visual discrimination of digits; caption generation from images; in silico cerebellar and inferior-olive lesions; dPCA of representations; 10 initial conditions.
- **Key results:**
  - ccRNN learns faster with less variability than cRNN and shows reduced dysmetria-like error.
  - Benefit holds only for short-to-medium feedback horizons (below 50% of the trial in the simple task); long horizons can be impaired by cerebellar feedback.
  - Cue-specific dPCs explain 95.4% of variance in cerebellar activity.
  - Lesions of cerebellar output vs inferior olive differ in effect, giving testable predictions; captions from ccRNN capture context better, mainly for longer captions.
- **Limitations / caveats:** Abstract-level modelling; predictions are untested; the cerebellar module is feedforward; one-to-one anatomical mapping is assumed.
- **Bearing on H015:** Supports (the paper is exactly this proposal, with the proviso that the speed-up depends on feedback horizon). The falsifier (no speed-up) is contradicted within the model.
- **Reproduce in this repo:** RNN with a small predictor of the sparse end-of-trial error; compare learning speed with and without it across feedback delays.

## Nokland 2019: Training Neural Networks with Local Error Signals
- **Cited for:** H016 (each layer optimises its own local loss, no global error)
- **Link:** https://doi.org/10.48550/arxiv.1901.06656 · **Basis:** full text (web; arXiv PDF text extracted)
- **Question:** How close can layer-wise training with local losses get to global backprop on image classification?
- **Method / model:** Each hidden layer feeds a single-layer local classifier (pred loss, cross-entropy to the labels) and/or a similarity-matching loss (sim, cosine-similarity matrices of layer outputs vs label similarity); combined as predsim with weight 0.99. Graph detached after each layer. Backprop-free variants (pred-bpf, sim-bpf, predsim-bpf) use random target projection and no backprop even within a layer.
- **Experiments:** MNIST, Fashion-MNIST, Kuzushiji-MNIST, CIFAR-10/100, SVHN, STL-10; MLPs and VGG-like nets (VGG8B, VGG11B), against global loss and WideResNet baselines; single runs.
- **Key results:**
  - CIFAR-10 test error: VGG11B(3x) 3.97% (predsim) vs 5.02% (global), 3.60% with cutout; local pred loss alone is 7.37%; WRN 3.87% (global).
  - CIFAR-100 VGG11B(3x): 20.1% (predsim) vs 23.7% (global); STL-10 VGG8B 20.51% vs 33.08% (global).
  - Backprop-free CIFAR-10: predsim-bpf 9.02% (VGG8B), 7.80% (VGG8B(2x)); the best previously reported backprop-free result cited is 12.6%.
  - Global backprop reaches lower training error faster; local losses mainly help generalisation.
- **Limitations / caveats:** Each local loss uses label information, so credit assignment comes from a target, not from nothing; works best on VGG-like nets and worse with residual connections; heavy reliance on dropout and batch norm; single runs.
- **Bearing on H016:** Contradicts the falsifier ("large gap to end-to-end"): on these benchmarks local losses match or beat the global-loss baseline. Supports the claim as phrased, with the caveat that each layer sees the label.
- **Reproduce in this repo:** MLP with per-layer linear local classifiers and a detached graph vs end-to-end training on a small image set.

## Roelfsema 2005: Attention-Gated Reinforcement Learning of Internal Representations for Classification
- **Cited for:** H017 (attention feedback tags the neurons responsible, and a reward signal then updates only the tagged synapses)
- **Link:** https://doi.org/10.1162/0899766054615699 · **Basis:** abstract only (full text blocked)
- **Question:** Can a global reward plus an attentional feedback signal solve credit assignment in a multilayer network?
- **Method / model:** AGREL: two factors determine plasticity, (1) a reward-dependent signal homogeneous across the network and (2) attentional feedback from the selected output unit that restricts plasticity to earlier units that contributed.
- **Experiments:** Classification tasks (per abstract); details not available.
- **Key results:** Abstract states AGREL is "as efficient as supervised learning in classification tasks".
- **Limitations / caveats:** Cannot be assessed beyond the abstract.
- **Bearing on H017:** Partly supports. The abstract does not name dopamine for the global signal (that link is in the 2018 review). The falsifier (much slower than backprop) conflicts with the abstract's efficiency claim, though the abstract gives no numbers.
- **Reproduce in this repo:** Small net with winner-take-all output: global reward signal times feedback tag from the chosen output; compare epochs with backprop.

## Roelfsema 2018: Control of synaptic plasticity in deep cortical networks
- **Cited for:** H017 (attention feedback and neuromodulators gate plasticity)
- **Link:** https://doi.org/10.1038/nrn.2018.6 · **Basis:** abstract only (sources.json abstract empty; abstract paraphrase from the KNAW repository page, accepted manuscript at pure.knaw.nl not readable)
- **Question:** How do neuromodulators and feedback connections jointly control plasticity in sensory cortex?
- **Method / model:** Review; proposes a framework where the factors determining synaptic strength, including neuromodulatory and feedback signals, interact to improve whole-network function.
- **Experiments:** None (review).
- **Key results:** No quantitative results.
- **Limitations / caveats:** Review, not a test.
- **Bearing on H017:** Partly supports (conceptual: feedback and neuromodulators gating plasticity). It cannot support a quantitative claim, and the dopamine-specific detail in the row is unverified from what I read.
- **Reproduce in this repo:** n/a (review); see the 2005 note.

## Lindsey 2020: Learning to Learn with Feedback and Local Plasticity
- **Cited for:** H018 (credit assignment is learned: the feedback pathway is itself trained together with local plasticity)
- **Link:** https://doi.org/10.48550/arxiv.2006.09549 · **Basis:** full text (web; arXiv PDF text extracted)
- **Question:** Can meta-learning find feedback weights plus local plasticity rules that do online credit assignment, without weight transport?
- **Method / model:** FLP: direct feedback from output (or error) to each layer through matrices B_i; layer activations updated as x_i <- (1 - lambda_i) x_i + lambda_i ReLU(B_i y - b); a local plasticity rule then updates forward weights. An outer meta-learning loop optimises B, initial weights and plasticity rates; they are fixed within a lifetime.
- **Experiments:** Online regression (incremental sine waves, 9-layer fully connected net; i.i.d. and continual), few-shot Omniglot and Mini-ImageNet; baselines: feature reuse (readout only), a gradient-based OML baseline, original OML.
- **Key results:**
  - Regression MSE: FLP (3 plastic layers) 0.00051 i.i.d. vs gradient-based 0.00057; continual: FLP 0.0068/0.0016 (3 or 2 layers) vs gradient-based 0.069.
  - Omniglot error: FLP 3.0% vs gradient-based 3.2%; continual 2.7% vs 3.4%; Mini-ImageNet 42.5% for both.
  - FLP updates are weakly or negatively correlated with the gradient in some layers and reduce interference.
- **Limitations / caveats:** Few benchmarks; heavy meta-training (days of GPU time); the meta-learning is an outer-loop and is not claimed to occur in the brain's lifetime; preprint.
- **Bearing on H018:** Supports. I found no baseline with fixed random feedback (untrained B) in the text, so the row's falsifier is a new experiment, not a result in the paper.
- **Reproduce in this repo:** Tiny meta-learning of B with a DFA-like local update vs fixed random B on a few-shot regression task.

## Corrections to the hypotheses file
- **H005:** The apical-error description is Sacramento's top-down input minus the learned lateral-interneuron prediction, not top-down minus somatic activity. The somatic-vs-dendritic comparison is Urbanczik and Senn's basal rule; reword or separate them (H019 already carries the Urbanczik claim).
- **H010:** Fiete and Seung 2006 contains no simulations and no birdsong demonstration (it cites separate works for the birdsong model), and Williams 1992 does not mention node perturbation or scaling; the "~100 units" threshold is not from either paper. Cite the birdsong papers or drop that clause.
- **H015:** Jaderberg 2017 does not make a cerebellar claim; only Boven 2023 does. Phrase as "synthetic gradients (Jaderberg) mapped onto cerebellum (Boven)".
- **H016:** Label information is used by every layer's local loss; "no global error" is accurate but "no teacher" would be wrong. The falsifier is contradicted by the paper's CIFAR/STL results.
- **H017:** Roelfsema and van Ooyen 2005 abstract does not name dopamine; the dopamine assignment comes from the 2018 review and should be marked as such. The slowdown falsifier conflicts with the abstract's "as efficient as supervised learning".
- **H018:** The paper has no fixed-random-feedback baseline; mark the falsifier as untested by the paper. The meta-learning is an outer loop, not within-lifetime learning.
- **H013:** The paper's own predictions are 5IB burst blocking, 6CT-to-pulvinar plasticity blocking and alpha-timescale LTD/LTP; the pulvinar-silencing T3 test is an adaptation.
- **H014:** The longest delay demonstrated is about 1-2 s (cue period 1050 ms before learning signals, delay 500-1500 ms), so the falsifier ("fails over a few seconds") is untested, not contradicted.
- **H002, H003, H008, H009, H016:** The falsifier clauses are contradicted by the cited papers' own results (FA 2.1% vs BP 2.4% on MNIST; DFA 1.74% vs 1.60%; DTP 1.94% vs 1.86%; KP angles near zero; local losses matching global loss). Keep them as replication checks, not as open predictions.
- **H020 (no citation):** The closest sources are Hinton 2022 Section 5 (he could not separate positive and negative phases reliably) and Hinton 1995 (wake-sleep); neither claims backprop-like learning occurs only during sleep. Leave it uncited or label it as the author's own hypothesis.
