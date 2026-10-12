# Paper notes: I. Dynamics and alternative computing primitives

Structured notes on the sources cited by hypotheses H138-H151, generated 2026-10-12. Only one source (Kappel 2015) had a usable local PDF and was read in full. Every other note rests on the abstract stored in sources.json, so it says little by design. The PDF tool needed poppler and was unavailable here, so the Kappel text was extracted with pypdf.

## Jaeger 2001: The "echo state" approach to analysing and training recurrent neural networks
- **Cited for:** H138 (most circuits are fixed random reservoirs; only readouts learn)
- **Link:** https://www.semanticscholar.org/paper/8430c0b9afa478ae660398704b11dca1221ccf22 · **Basis:** abstract only (sources.json holds no abstract and no PDF, so this is title only)
- **Question:** Not stated in the material available.
- **Method / model:** Title only: a training approach for recurrent nets (echo state networks). No details were read.
- **Experiments:** Not read.
- **Key results:** Not read.
- **Limitations / caveats:** Nothing can be assessed from the title.
- **Bearing on H138:** does not test it from what was read. The title concerns training RNNs, not claims about which brain circuits are fixed reservoirs.
- **Reproduce in this repo:** Fixed random recurrent reservoir plus ridge-regression readout versus a fully trained recurrent net on a Brain World memory-lag task, in numpy.

## Maass, Natschläger & Markram 2002: Real-Time Computing Without Stable States
- **Cited for:** H138 (fixed random reservoirs, only readouts learn)
- **Link:** https://doi.org/10.1162/089976602760407955 · **Basis:** abstract only
- **Question:** How can generic recurrent circuits process a continuous input stream in real time without task-specific construction or stable internal states?
- **Method / model:** The liquid state machine. A large, heterogeneous recurrent circuit of integrate-and-fire neurons acts as a high-dimensional dynamical system. Its transient state serves as a universal analog fading memory, and readout neurons learn to extract current and past input information from it.
- **Experiments:** Not described in the abstract. It cites rigorous results on universal computational power under idealised conditions.
- **Key results:**
  - The circuit needs no task-dependent construction.
  - Transient internal states can be mapped to stable outputs by readouts, because the dynamics are high-dimensional.
- **Limitations / caveats:** Universality results hold under idealised conditions. The abstract gives no empirical numbers.
- **Bearing on H138:** partly supports it. The paper gives a computational framework in which only readouts learn. It does not show that most biological circuits are fixed random reservoirs. "Most circuits" is the hypothesis row's claim, not the paper's.
- **Reproduce in this repo:** Same experiment as Jaeger, using a spiking or tanh reservoir. Compare readout-only learning with a fully plastic recurrent net on a time-varying input task.

## Sussillo & Abbott 2009: Generating Coherent Patterns of Activity from Chaotic Neural Networks
- **Cited for:** H139 (output feedback with fast learning can tame chaotic recurrent activity into a task, i.e. FORCE)
- **Link:** https://doi.org/10.1016/j.neuron.2009.07.018 · **Basis:** abstract only
- **Question:** How do spontaneous chaotic activity and task-driven activity relate, and can plasticity turn one into the other?
- **Method / model:** FORCE learning modifies synaptic strengths, either external to the network or within it, to turn chaotic spontaneous activity into desired patterns. The feedback loops stay intact and unclamped during learning.
- **Experiments:** Per the abstract: complex output patterns, input-output transformations that need memory, multiple outputs switched by control inputs, and motor patterns matching human motion-capture data. It also reproduces pre-movement activity in motor and premotor cortex.
- **Key results:**
  - FORCE learning works although the networks are spontaneously chaotic.
  - It yields a wide variety of target patterns.
- **Limitations / caveats:** The abstract does not mention that the learning algorithm is recursive least squares, which is not obviously local. Whether "local" holds is not verifiable from the abstract.
- **Bearing on H139:** supports the dynamical claim. The row's test ("local FORCE-like rule") goes beyond the abstract, because locality is not shown.
- **Reproduce in this repo:** Chaotic rate net (N=200, gain 1.5) with a feedback loop and an RLS readout learning a sine sum. Then swap RLS for an LMS-style local update and compare the error.

## Hopfield 1982: Neural networks and physical systems with emergent collective computational abilities
- **Cited for:** H140 (memories and categories are attractors in a recurrent network)
- **Link:** https://doi.org/10.1073/pnas.79.8.2554 · **Basis:** abstract only
- **Question:** Can useful computation, such as content-addressable memory, emerge as a collective property of many simple neuron-like units?
- **Method / model:** Asynchronous binary-threshold units with a content-addressable memory defined by the phase-space flow of the system state. The abstract does not give the weight rule.
- **Experiments:** Not described in the abstract.
- **Key results:**
  - Memories are recovered correctly from any subpart of sufficient size.
  - Emergent properties include some generalisation, familiarity recognition, categorisation, error correction and time-sequence retention.
  - The properties are only weakly sensitive to device failure.
- **Limitations / caveats:** Model-level claims only. Abstract-level reading.
- **Bearing on H140:** supports the mechanism and gives categorisation as an emergent property. Whether the brain does this is not tested.
- **Reproduce in this repo:** Hebbian Hopfield net storing prototypes of Brain World states. Recall from noisy cues, and count whether noisy exemplars of one category fall into one attractor.

## Hasselmo, Bodelón & Wyble 2002: A Proposed Function for Hippocampal Theta Rhythm
- **Cited for:** H141 (theta splits time into encoding and retrieval phases, so learning and recall do not interfere)
- **Link:** https://doi.org/10.1162/089976602317318965 · **Basis:** abstract only
- **Question:** Why do theta-blocking lesions impair reversal of prior learning, such as T-maze reversal?
- **Method / model:** A hippocampal model with two phases per 100-300 ms theta cycle. In the encoding phase, entorhinal input and LTP at CA3 synapses are strong while CA3 synaptic currents are weak, so prior associations do not interfere. In the retrieval phase, CA3 input is strong and depotentiation occurs, so old associations that do not match the input are extinguished.
- **Experiments:** T-maze reversal modelling. The abstract cites new data that synaptic transmission in stratum radiatum is weakest at the positive theta peak, when LTP induction is strongest.
- **Key results:**
  - Phase separation can explain reversal impairment after theta loss.
  - LTP must be strongest when transmission is weakest.
- **Limitations / caveats:** The abstract does not report a quantitative comparison against an unsplit model.
- **Bearing on H141:** partly supports it. The paper's stated function is reversal of prior learning (interference reduction). The hypothesis phrasing is a fair summary, but the test "same interference" would be a new test.
- **Reproduce in this repo:** Associative net with a toggled encode/retrieve phase mask versus always-on learning on an A to B then A to C reversal task. Compare the interference.

## Skaggs et al. 1996: Theta phase precession in hippocampal neuronal populations and the compression of temporal sequences
- **Cited for:** H142 (theta sequences compress behaviour into bursts STDP can learn from)
- **Link:** https://doi.org/10.1002/(sici)1098-1063(1996)6:2<149::aid-hipo6>3.0.co;2-k · **Basis:** abstract only (sources.json holds no abstract, so this is title only)
- **Question:** Title only: phase precession and the compression of temporal sequences in hippocampal populations.
- **Method / model:** Not read.
- **Experiments:** Not read.
- **Key results:** Not read.
- **Limitations / caveats:** Nothing can be assessed.
- **Bearing on H142:** does not test it as far as can be verified. The title supports sequence compression. The STDP link is not verified here, so check the full text before relying on the "STDP can learn from" part.
- **Reproduce in this repo:** Phase-precessing place-cell inputs feeding an STDP synapse versus the same inputs without compression. Measure learned forward association strength.

## Beggs & Plenz 2003: Neuronal avalanches in neocortical circuits
- **Cited for:** H143 (brain near criticality maximises information transmission and learning)
- **Link:** https://doi.org/10.1523/jneurosci.23-35-11167.2003 · **Basis:** abstract only
- **Question:** Does spontaneous cortical network activity follow avalanche (critical branching) statistics?
- **Method / model:** 60-channel multielectrode-array recordings of spontaneous local field potentials, continuously, in mature organotypic cultures and acute slices of rat cortex. Event sizes are compared to a critical branching process, plus simulations.
- **Experiments:** Organotypic cultures and acute rat cortical slices (counts not in the abstract). Simulations of feedforward networks.
- **Key results:**
  - Event sizes follow a power law with exponent -3/2.
  - The branching parameter is close to the critical value of 1.
  - Simulations show a branching parameter at 1 optimises information transmission in feedforward networks and prevents runaway excitation.
- **Limitations / caveats:** The information-transmission claim comes from simulation. The abstract has no claim about learning.
- **Bearing on H143:** partly supports it. Criticality in cortex and optimal transmission (in simulation) are shown. "And learning" is not tested, so the row overstates.
- **Reproduce in this repo:** Branching-process network where gain sets the branching ratio. Sweep it from 0.5 to 1.5 and plot the performance of a readout task and the learning speed.

## Fiser et al. 2010: Statistically optimal perception and learning
- **Cited for:** H144 (neural variability is sampling from a distribution, which supports Bayesian learning)
- **Link:** https://doi.org/10.1016/j.tics.2010.01.003 · **Basis:** abstract only
- **Question:** How could perception and learning be treated jointly as statistical inference, and what neural representation of uncertainty fits?
- **Method / model:** A review. It proposes that spontaneous activity has a functional role in a sampling-based framework for how cortex represents information and uncertainty.
- **Experiments:** None (a review of evidence for statistically optimal learning in humans and animals).
- **Key results:** A proposal, with no numbers in the abstract.
- **Limitations / caveats:** Hypothesis-level.
- **Bearing on H144:** supports the sampling idea. It is a proposal, not a demonstration.
- **Reproduce in this repo:** Stochastic network sampling hidden states versus a deterministic network on calibration of predicted uncertainty.

## Kappel et al. 2015: Network Plasticity as Bayesian Inference
- **Cited for:** H144 (as above, sampling-based learning)
- **Link:** https://doi.org/10.1371/journal.pcbi.1004485 · **Basis:** full text
- **Question:** Can stochastic plasticity and spine motility be understood as sampling from a posterior over network parameters instead of converging to a maximum-likelihood point?
- **Method / model:** Each parameter obeys dθ_i = b (∂/∂θ_i log p_S(θ) + ∂/∂θ_i log p_N(x|θ)) dt + sqrt(2b) dW_i (Eq. 3), a Langevin equation. It has three terms: an activity-dependent (Hebbian or STDP) drift from the likelihood, a prior term enforcing structural rules, and Wiener-process noise. The parameter distribution converges to the posterior p*(θ|x) ∝ p_S(θ)·p_N(x|θ). Retracted spines map to a negative parameter with zero efficacy, which integrates structural rewiring with STDP.
- **Experiments:**
  - RBM with 784 visible and 9 hidden units trained on 5 MNIST "1" samples, tested on 100 other "1"s, 100 runs.
  - Spiking winner-take-all circuit of 10 neurons with 784 inputs (MNIST), with a distribution shift (phase 1: all 6742 digit 1s, phase 2: 1s plus 5958 2s, phase 3 back).
  - Spiking generative network with 8 WTA circuits (auditory and visual populations of 40 hidden neurons each) subjected to two lesions in a session over 7 hours.
- **Key results:**
  - With a uniform prior (maximum likelihood), test log-likelihood rises and then degrades with prolonged training (overfitting). With a bimodal prior it stays constant at a high level (Fig. 2D vs 2F).
  - In the WTA circuit, synapses are eliminated and regrown while connectivity stays sparse. Regrowth is driven almost entirely by the prior and noise.
  - After removing 16 of 40 neurons, and after removing all hidden-hidden synapses, the network recovered. After the second lesion 294 new connections emerged, restoring performance to about 75% of the earlier level.
- **Limitations / caveats:** Unsupervised generative models only. Sampling is over weights (a slow timescale), not over fast neural states. Gains are shown versus maximum-likelihood learning with a flat prior, not versus dropout or other regularisers.
- **Bearing on H144:** partly supports it. The paper shows Bayesian learning by sampling of parameters, so the variability is in the plasticity, not in neural activity as such. Fiser's idea (sampling activity) differs. The row combines two related but different sampling claims.
- **Reproduce in this repo:** Weight update with prior gradient plus sqrt(2b) noise on an RBM trained on 5 digits. Compare test log-likelihood against the noise-free update.

## Vogels et al. 2011: Inhibitory Plasticity Balances Excitation and Inhibition in Sensory Pathways and Memory Networks
- **Cited for:** H145 (inhibitory plasticity keeps E/I balance so excitatory learning stays stable)
- **Link:** https://doi.org/10.1126/science.1211095 · **Basis:** abstract only (the abstract in sources.json is a single line: plasticity at inhibitory synapses maintains balanced excitatory and inhibitory inputs at cortical neurons)
- **Question:** How is E/I balance established and maintained?
- **Method / model:** A model of inhibitory plasticity. Details are not in the abstract.
- **Experiments:** Not stated beyond the title (sensory pathways and memory networks).
- **Key results:** Only the one-line abstract.
- **Limitations / caveats:** Not assessable.
- **Bearing on H145:** partly supports it. Balanced input is the paper's claim. Whether it keeps excitatory learning stable is not verifiable from the abstract.
- **Reproduce in this repo:** Spiking or rate E/I network with and without a rate-based inhibitory plasticity rule. Compare stability of STDP learning.

## Turrigiano et al. 1998: Activity-dependent scaling of quantal amplitude in neocortical neurons
- **Cited for:** H146 (synaptic scaling keeps rates in range so Hebbian learning does not run away)
- **Link:** https://doi.org/10.1038/36103 · **Basis:** abstract only (no abstract in sources.json, so this is title only)
- **Question:** Title only: whether quantal amplitude is scaled by activity.
- **Method / model:** Not read.
- **Experiments:** Not read.
- **Key results:** Not read.
- **Limitations / caveats:** Nothing can be assessed.
- **Bearing on H146:** does not test it as far as verifiable. The title supports activity-dependent scaling of quantal amplitude. The role in stabilising Hebbian learning is an interpretation that is not verified here.
- **Reproduce in this repo:** Hebbian layer with and without multiplicative scaling to a target rate. Track weight and rate divergence.

## Bienenstock, Cooper & Munro 1982: Theory for the development of neuron selectivity
- **Cited for:** H147 (a sliding threshold decides when activity strengthens or weakens a synapse)
- **Link:** https://doi.org/10.1523/jneurosci.02-01-00032.1982 · **Basis:** abstract only
- **Question:** How does stimulus selectivity develop in primary sensory cortex?
- **Method / model:** Synaptic change depends on instantaneous pre- and postsynaptic activity and on a slowly varying time average of postsynaptic activity (the sliding threshold). A nonlinear form of that dependence produces selectivity. No nonlinear neuron or special intracortical circuitry is required.
- **Experiments:** Analysis of an environment with two stimuli presented alternately at random, then simulations of orientation selectivity and binocular interaction in visual cortex under normal and altered rearing.
- **Key results:**
  - With two stimuli, the state converges with probability 1 to points of maximum selectivity.
  - Simulated tuning curves and ocular dominance are comparable to those in normally reared cats or monkeys.
- **Limitations / caveats:** Theory plus simulation. The abstract does not compare to Oja.
- **Bearing on H147:** supports it. The abstract matches the row.
- **Reproduce in this repo:** BCM with sliding threshold versus Oja's rule on a mixture of two input patterns. Measure the selectivity index.

## Kozachkov et al. 2023: Building transformers from neurons and astrocytes
- **Cited for:** H148 (astrocytes add slow many-synapse memory and could make attention-like computation)
- **Link:** https://doi.org/10.1073/pnas.2219150120 · **Basis:** abstract only
- **Question:** What is the computational role of neuron-astrocyte interactions?
- **Method / model:** Neuron-astrocyte networks are shown to perform the core Transformer computation. A normative, experimentally testable account is given. Details are not in the abstract.
- **Experiments:** Not described in the abstract. It mentions astrocyte imaging technology as motivation.
- **Key results:** Neuron-astrocyte networks "can naturally perform" the core computation of a Transformer.
- **Limitations / caveats:** The result is a model-level mapping.
- **Bearing on H148:** partly supports it. The attention-like computation is the paper's claim. The "slow, many-synapse memory" phrasing and the test "memory capacity gain" are not in the abstract, so they are the row's own addition.
- **Reproduce in this repo:** Associative memory with a slow shared modulatory variable per group of synapses versus one without. Compare the stored-pattern capacity.

## Holtmaat & Svoboda 2009: Experience-dependent structural synaptic plasticity in the mammalian brain
- **Cited for:** H149 (growing and removing synapses stores long-term memories)
- **Link:** https://doi.org/10.1038/nrn2699 · **Basis:** abstract only
- **Question:** What does long-term in vivo imaging show about structural plasticity in adult cortex?
- **Method / model:** A review of in vivo imaging studies.
- **Experiments:** Not detailed in the abstract (somatosensory and visual cortex, normal and injured adult brain).
- **Key results:**
  - Axon and dendrite morphology, and a subpopulation of small synaptic structures, are remarkably stable.
  - Some boutons and spines appear and disappear with experience, accompanied by synapse formation and elimination.
- **Limitations / caveats:** The abstract says it outlines open questions.
- **Bearing on H149:** partly supports it. It shows experience-dependent structural change. That structural change stores long-term memory is not asserted in the abstract, so the row overstates.
- **Reproduce in this repo:** Sparse network with rewiring (prune and regrow by Hebbian gain) versus a fixed-topology weight-only model. Compare pattern capacity at the same synapse count.

## Fields 2015: A new mechanism of nervous system plasticity: activity-dependent myelination
- **Cited for:** H150 (activity-dependent myelination tunes timing between areas, a form of learning)
- **Link:** https://doi.org/10.1038/nrn4023 · **Basis:** abstract only
- **Question:** Could conduction velocity be modified through myelin changes to optimise timing in circuits?
- **Method / model:** An opinion article. It combines imaging of white-matter changes in the human brain during learning with cellular studies that show action-potential firing can influence myelination.
- **Experiments:** None of its own.
- **Key results:** Presents "the possibility" of activity-dependent conduction-velocity changes.
- **Limitations / caveats:** Hypothesis-level.
- **Bearing on H150:** supports it as a hypothesis. The abstract says "possibility", so call H150 a hypothesis rather than established.
- **Reproduce in this repo:** Learnable per-connection delays versus fixed delays on a coincidence-detection timing task.

## H151: Synaptic transmission failures act like dropout
- **Cited for:** H151 (marked "new", no source)
- **Link:** none · **Basis:** abstract only (no source in sources.json, so no note is possible)
- **Bearing on H151:** not testable against a paper. Dropout itself (Srivastava et al. 2014) and the stochastic-release literature would be the natural citations. Kappel 2015 is related only loosely, because it concerns plasticity noise, not transmission failure.
- **Reproduce in this repo:** Net with Bernoulli transmission failure (p=0.5) versus the same net without, compared on test accuracy with a small training set.

## Corrections to the hypotheses file
- H138: "Most circuits are fixed random reservoirs" goes beyond Maass 2002 and Jaeger 2001, which give a framework. Soften to "Some circuits could act as fixed random reservoirs".
- H143: the paper's information-transmission result is from simulation, and it does not test learning. Drop "and learning" or mark it as the hypothesis's own extension.
- H144: Kappel 2015 samples network parameters (weights and connections), whereas Fiser 2010 proposes sampling of neural activity. Say so in the row.
- H148: the paper shows a Transformer-like computation, not "slow many-synapse memory". The test should target attention-like computation, not memory capacity.
- H149: Holtmaat & Svoboda show structural turnover, not memory storage. Reword to "structural plasticity changes circuits with experience".
- H150: mark the evidence as hypothesis-level (Fields 2015 is an opinion article).
- H151: add a citation (for example dropout, Srivastava 2014), or keep "new".
- H142, H146: the citations could not be checked (no abstract). Verify that the STDP link (Skaggs) and the Hebbian-stability role (Turrigiano) are stated in the full text.
