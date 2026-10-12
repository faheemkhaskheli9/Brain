# Paper notes: J. Control, attention and meta-learning

Structured notes on the sources cited by hypotheses H152-H161, generated 2026-10-12. No local PDFs exist for these sources. Schmitt 2017 and Carandini 2012 were read through their PMC pages (first 100,000 characters of each). The other notes rest on the abstracts in sources.json, so they say little by design.

## Miller & Cohen 2001: An Integrative Theory of Prefrontal Cortex Function
- **Cited for:** H152 (PFC holds the current goal and rule and biases other areas toward it)
- **Link:** https://doi.org/10.1146/annurev.neuro.24.1.167 · **Basis:** abstract only
- **Question:** What is the neural basis of cognitive control?
- **Method / model:** A review and theory. Control stems from active maintenance of PFC activity patterns that represent goals and the means to achieve them. These provide bias signals to other structures, guiding activity along pathways that map inputs, internal states and outputs for the task.
- **Experiments:** None of its own. It reviews neurophysiological, neurobiological, neuroimaging and computational studies.
- **Key results:** The guided-activation proposal. The abstract gives no numbers.
- **Limitations / caveats:** The abstract flags open issues to be addressed.
- **Bearing on H152:** supports it. The row restates the theory accurately.
- **Reproduce in this repo:** Small net with a gated goal-bias input versus a plain net on a rule-switching task (a stimulus-response mapping that flips). Count the trials to recover.

## Schmitt et al. 2017: Thalamic amplification of cortical connectivity sustains attentional control
- **Cited for:** H153 (the thalamus switches cortical connectivity for the current context)
- **Link:** https://doi.org/10.1038/nature22073 · **Basis:** full text (web, first 100,000 of about 127,000 characters)
- **Question:** What does the mediodorsal (MD) thalamus contribute to PFC rule representations beyond relaying information?
- **Method / model:** Mice performed a cross-modal attention task (2AFC with a rule cue: attend vision or attend audition, and a 4AFC variant separating executive from sensory errors). Single-unit recordings, optogenetic silencing and excitation, stabilised step-function opsin (SSFO) boosting of excitability, Granger causality for connectivity, and a leaky integrate-and-fire PFC-MD model.
- **Experiments:** 43 male mice. 3,444 PFC and 974 MD single units, split into regular-spiking (RS) and fast-spiking (FS). Silencing MD, LGN or PFC during the delay, and a medial geniculate body (MGB) control.
- **Key results:**
  - MD silencing impaired performance and produced executive errors like PFC silencing. LGN silencing instead raised sensory errors. MD silencing reduced the maintenance of PFC rule tuning but spared initial rule encoding.
  - MD activation increased FS firing and RS connectivity without raising RS firing rates. MD input gave supralinear amplification of evoked responses.
  - SSFO excitation of MD raised rule information and performance (26% reduction in lapse rate). Excitation of PFC reduced performance and rule information. The MGB control did not give the same enhancement.
  - The model reproduced rule-specific sequences from MD amplification of local connectivity plus synchronised starter-neuron input.
- **Limitations / caveats:** Mice and a single attention task. The portion beyond 100,000 characters was not read. MD neurons were mostly non-selective, so the thalamus does not carry the rule itself.
- **Bearing on H153:** partly supports it. The paper shows the thalamus amplifies local PFC connectivity to sustain a rule representation. It does not show the thalamus "switches" connectivity between contexts. The row overstates.
- **Reproduce in this repo:** Recurrent net with a gain-modulating thalamic unit (amplifying recurrent weights for the active context) versus none, on a two-context task with a delay.

## Larkum 2013: A cellular mechanism for cortical associations
- **Cited for:** H154 (top-down input to apical dendrites gates which feedforward inputs can drive learning)
- **Link:** https://doi.org/10.1016/j.tins.2012.11.006 · **Basis:** abstract only (no abstract in sources.json, so this is title only)
- **Question:** Title only: a cellular mechanism for associations in cortex, presented as an organising principle.
- **Method / model:** Not read.
- **Experiments:** Not read.
- **Key results:** Not read.
- **Limitations / caveats:** Nothing can be assessed.
- **Bearing on H154:** does not test it as far as verifiable. The title suggests an association mechanism, but "gates what can drive learning" is not verified. Check the full text.
- **Reproduce in this repo:** Two-compartment units where a basal input drives the output only when an apical input is present, versus plain units. Compare multitask interference.

## Botvinick, Niv & Barto 2009: Hierarchically organized behavior and its neural foundations
- **Cited for:** H155 (behaviour is organised as hierarchical options learned by RL)
- **Link:** https://doi.org/10.1016/j.cognition.2008.08.011 · **Basis:** abstract only
- **Question:** How does hierarchical reinforcement learning (HRL) map onto behavioural hierarchy and its neural substrates?
- **Method / model:** A review. HRL extends RL by letting the agent aggregate actions into reusable subroutines (skills). Its components are mapped onto regions of dorsolateral and orbital prefrontal cortex.
- **Experiments:** None of its own.
- **Key results:** A mapping proposal. The abstract names the discovery of useful new routines as an important open question.
- **Limitations / caveats:** The abstract does not claim the options are learned in the way the row says. How options are learned is stated as open.
- **Bearing on H155:** partly supports it. It supports the framework. "Learned by RL" is an open question in the paper, not a result.
- **Reproduce in this repo:** Options agent versus flat Q-learning on a four-room grid world. Count the episodes to reach the goal.

## Friston et al. 2015: Active inference and epistemic value
- **Cited for:** H156 (agents act to reduce uncertainty, not only to get reward)
- **Link:** https://doi.org/10.1080/17588928.2015.1020053 · **Basis:** abstract only
- **Question:** Can choice behaviour be derived from minimising expected free energy?
- **Method / model:** The expected free energy of a policy decomposes into extrinsic value (expected utility under prior preferences) and epistemic value (information gain). Epistemic value dominates until no information gain remains, then exploitation follows. Softmax parameters become the expected precision of beliefs about policies.
- **Experiments:** Simulations illustrate the theory. The abstract names precision updates resembling dopaminergic discharges in conditioning paradigms.
- **Key results:** A resolution of exploration versus exploitation in a formal framework.
- **Limitations / caveats:** Theory and simulations, with no behavioural data described.
- **Bearing on H156:** supports the principle. "Faster structure learning" is not shown in the abstract.
- **Reproduce in this repo:** Bandit or maze agent with an information-gain bonus versus a reward-only agent on a hidden-structure task. Compare the steps to learn the structure.

## Knill & Pouget 2004: The Bayesian brain
- **Cited for:** H157 (cues combined as a Bayesian observer weighted by reliability)
- **Link:** https://doi.org/10.1016/j.tins.2004.10.007 · **Basis:** abstract only (no abstract in sources.json, so this is title only)
- **Question:** Title only: the role of uncertainty in neural coding and computation.
- **Method / model:** Not read.
- **Experiments:** Not read.
- **Key results:** Not read.
- **Limitations / caveats:** Nothing can be assessed.
- **Bearing on H157:** the title fits the row's framing, but nothing here verifies the cue-combination claim. The row notes it is "supported for perception". Check the full text.
- **Reproduce in this repo:** Two noisy cue inputs with different variances. Train a local-rule net and compare its weights with inverse-variance weights.

## Carandini & Heeger 2012: Normalization as a canonical neural computation
- **Cited for:** H158 (divisive normalisation makes learning invariant to scale)
- **Link:** https://doi.org/10.1038/nrn3136 · **Basis:** full text (web, first 100,000 of about 168,000 characters)
- **Question:** Is normalisation a canonical computation repeated across brain regions and modalities?
- **Method / model:** A review. R_j = γ D_j^n / (σ^n + Σ_k D_k^n), where D_j is the driving input, the sum runs over a normalisation pool, σ sets saturation and n is an exponent.
- **Experiments:** None of its own. It lists olfaction (fly antennal lobe), retinal light adaptation, retina and LGN contrast normalisation, V1 (contrast saturation, cross-orientation and surround suppression, winner-take-all), MT, V4, IT, auditory cortex, multisensory integration, value coding in LIP and attention.
- **Key results:**
  - Normalisation can give invariance along some stimulus dimensions at the expense of others (for example V1 discards contrast to encode orientation, and fly olfaction supports recognition regardless of concentration).
  - The text makes no claim that normalisation is learned or affects learning. Associative learning rules are listed as a separate canonical computation.
- **Limitations / caveats:** Invariance here is of responses to stimuli, not of learning.
- **Bearing on H158:** does not test it. The paper supports normalisation as a canonical computation with stimulus invariance. "Makes learning invariant to scale" is the row's own extension.
- **Reproduce in this repo:** Net with divisive normalisation on inputs versus without, trained on inputs whose scale varies across batches. Compare the learning curves.

## Bastos et al. 2012: Canonical microcircuits for predictive coding
- **Cited for:** H159 (the canonical cortical microcircuit implements predictive coding in its layers)
- **Link:** https://doi.org/10.1016/j.neuron.2012.10.038 · **Basis:** abstract only
- **Question:** Does cortical microcircuitry correspond to the connectivity implied by predictive coding?
- **Method / model:** A theoretical review that derives canonical message-passing forms for Bayesian inference in hierarchical cortex. It associates specific neuronal populations with computational roles, and explains the feedforward/feedback asymmetries and characteristic frequencies.
- **Experiments:** None of its own.
- **Key results:** The abstract reports a "remarkable correspondence" between cortical column microcircuitry and predictive-coding connectivity.
- **Limitations / caveats:** A correspondence argument, not a test. The hypothesis row's T2 test is therefore the right kind.
- **Bearing on H159:** supports it as a hypothesis. It does not test it.
- **Reproduce in this repo:** n/a (T2).

## Marr 1969: A theory of cerebellar cortex
- **Cited for:** H160 (supervised learning in the cerebellum, with climbing fibres carrying the error)
- **Link:** https://doi.org/10.1113/jphysiol.1969.sp008820 · **Basis:** abstract only
- **Question:** How can cerebellar cortex learn motor skills?
- **Method / model:** Each Purkinje cell receives a climbing fibre from one olivary cell. For actions, the olivary cell responds to a cerebral instruction for an elemental movement. Mossy-fibre context is learned during rehearsal, so the context alone later fires the Purkinje cell. The abstract predicts that parallel-fibre to Purkinje synapses are facilitated by conjunction of presynaptic and climbing-fibre activity, and that no other cerebellar synapses are modifiable. For maintenance reflexes, the olivary cell is driven by receptors whose activity is reduced by the effect of the Purkinje cell.
- **Experiments:** None. A theoretical paper.
- **Key results:** The climbing fibre acts as an instruction signal in the action case, and the sign of the synaptic change is facilitation.
- **Limitations / caveats:** In the action-learning case the climbing fibre carries an instruction, not an error. Only the reflex case has error-like feedback.
- **Bearing on H160:** partly supports it. Supervised learning in the cerebellum is supported in spirit. "Climbing fibres carry the error" is not Marr's action-learning claim as stated in the abstract.
- **Reproduce in this repo:** Parallel-fibre to Purkinje delta rule driven by a teaching signal on a motor-correction task in Brain World, versus no teaching signal.

## Albus 1971: A theory of cerebellar function
- **Cited for:** H160
- **Link:** https://doi.org/10.1016/0025-5564(71)90051-4 · **Basis:** abstract only (no abstract in sources.json, so this is title only)
- **Question:** Title only.
- **Method / model:** Not read.
- **Experiments:** Not read.
- **Key results:** Not read.
- **Limitations / caveats:** Nothing can be assessed.
- **Bearing on H160:** does not test it as far as verifiable.
- **Reproduce in this repo:** n/a (covered under Marr 1969).

## Raymond & Medina 2018: Computational Principles of Supervised Learning in the Cerebellum
- **Cited for:** H160
- **Link:** https://doi.org/10.1146/annurev-neuro-080317-061948 · **Basis:** abstract only
- **Question:** What computational principles underlie supervised learning in the cerebellum?
- **Method / model:** A review. The cerebellum is said to implement supervised learning using: extensive preprocessing of input representations, a massively recurrent circuit architecture, linear input-output computations, sophisticated instructive signals that can be regulated and are predictive, plasticity with multiple timescales, and task-specific hardware specialisations.
- **Experiments:** None of its own.
- **Key results:** The abstract says instructive signals are "sophisticated", "regulated" and "predictive", which is more than a plain error signal.
- **Limitations / caveats:** The abstract notes notable differences from artificial networks.
- **Bearing on H160:** partly supports it. Supervised learning is stated outright. The instructive signal is described as more than a simple error, so "carrying the error" is a simplification.
- **Reproduce in this repo:** Linear readout over an expanded random feature layer with a delta rule from a teaching signal, versus a reward-only update, on a motor tracking task.

## Momennejad et al. 2017: The successor representation in human reinforcement learning
- **Cited for:** H161 (humans use a successor-like predictive map, measured in behaviour)
- **Link:** https://doi.org/10.1038/s41562-017-0180-8 · **Basis:** abstract only (the full-text fetch from bioRxiv returned HTTP 403)
- **Question:** Does human choice show the signature of the successor representation (SR), an intermediate between model-free and model-based learning?
- **Method / model:** The SR stores predictions about future states. It predicts insensitivity to changes in the task's sequence of events, but flexible adjustment after reward changes.
- **Experiments:** Two behavioural studies with humans. Sizes and designs are not in the abstract.
- **Key results:**
  - The authors report evidence for the differential sensitivity predicted by the SR.
  - They conclude the SR is a computational substrate for semi-flexible choice in humans.
- **Limitations / caveats:** Sample sizes and model fits cannot be assessed from the abstract.
- **Bearing on H161:** supports it. The row's T2 test (model comparison on open revaluation data) matches the paper's design.
- **Reproduce in this repo:** n/a (T2).

## Corrections to the hypotheses file
- H153: Schmitt 2017 shows the thalamus amplifies local PFC connectivity to sustain a rule. It does not show it "switches" connectivity between contexts. Reword.
- H155: how options are learned is an open question in Botvinick 2009. Mark "learned by RL" as the hypothesis's extension.
- H156: the "faster structure learning" test is not claimed by Friston 2015. Keep it as a repo test only.
- H158: Carandini & Heeger do not link normalisation to learning invariance. Reword to "normalisation gives scale invariance of responses, which may help learning".
- H160: Marr's action-learning climbing fibre carries an instruction, not an error. Raymond & Medina describe the instructive signal as predictive and regulated. Soften "carrying the error".
- H154 and H157: could not be verified (no abstract). Check the full texts.
