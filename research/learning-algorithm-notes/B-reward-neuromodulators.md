# Paper notes: B. Reward, neuromodulators and three-factor rules

Per-source notes for hypotheses H021-H038 of `research/learning-algorithm-hypotheses.md`, generated 2026-10-12 from `research/pdfs/learning-algorithm/sources.json` plus the four local PDFs. "Basis" says what was actually read; where only an abstract was available the note is deliberately thin and nothing beyond the abstract is claimed. Most sources had no readable full text (paywalled or bot-blocked), so those verdicts are about the abstract's claim only.

## Gerstner 2018: Eligibility Traces and Plasticity on Behavioral Time Scales
- **Cited for:** H021 - plasticity is Hebb x eligibility trace x neuromodulator, the third factor arriving seconds later.
- **Link:** https://doi.org/10.3389/fncir.2018.00053 · **Basis:** full text (local PDF is the arXiv v1 preprint 1801.05219, not the published version)
- **Question:** Learning rules must bridge ms spikes and second-scale behaviour; is there experimental evidence for synaptic eligibility traces plus a third factor?
- **Method / model:** Review. Formalises the neoHebbian three-factor rule: pre x post activity sets a synaptic flag (eligibility trace) that decays over about a second or more; the weight changes only if a third factor (reward, surprise, a neuromodulator) arrives while the flag is up. Links it to policy-gradient and TD learning, where the third factor is reward minus expected reward.
- **Experiments:** Reviews four slice/in-vivo studies. Yagishita 2014 (nucleus accumbens spines: glutamate uncaging + 3 spikes, x10, plus dopamine fibre stimulation at varied delays); He 2015 (L2/3 cortex, STDP then NE/5-HT/DA/ACh at delay); Brzosko 2015/2017 (CA1 STDP with dopamine/ACh after the protocol); Bittner 2017 (CA1 plateau potentials).
- **Key results:**
  - Striatal spines: dopamine promoted spine enlargement only if given during or just after the ~1 s STDP protocol; still visible at 1 s delay.
  - Cortex (He 2015): NE converts LTP traces if it arrives within 5 s (not 10 s); 5-HT converts LTD traces within 2.5 s (not 5 s); pre-before-post trace decays over 5-10 s, post-before-pre over about 3 s. Dopamine/ACh had no effect in visual cortex.
  - Hippocampus: dopamine or ACh after pairing can flip or enable LTP/LTD; Bittner's plateau potential works with 1-2 s gaps in either direction.
- **Limitations / caveats:** The review itself says the evidence is only a handful of preparations, mostly in slices, and that time constants differ per brain area and per neuromodulator; alternatives to traces (e.g. persistent activity) are discussed and not excluded.
- **Bearing on H021:** Supports. Note the paper shows the third factor is area- and transmitter-specific (NE for LTP, 5-HT for LTD in cortex), so "the neuromodulator" in the row is a simplification.
- **Reproduce in this repo:** Spiking or rate net with e_ij decaying (tau ~1 s) and dw = r(t) * e_ij on a task whose reward lags the action by 0, 1, 2, 5 s; plot success vs delay and compare with a no-trace baseline (chance).

## Schultz, Dayan & Montague 1997: A Neural Substrate of Prediction and Reward
- **Cited for:** H022 - phasic dopamine is a TD reward-prediction error.
- **Link:** https://doi.org/10.1126/science.275.5306.1593 · **Basis:** full text (local PDF, two-column text extraction; skimmed)
- **Question:** Can the temporal-difference algorithm explain what primate midbrain dopamine neurons signal during conditioning?
- **Method / model:** Value V(t) = E[sum_k gamma^k r(t+k)]; TD error delta(t) = r(t) + gamma V(t+1) - V(t); weights on a tapped-delay stimulus representation updated as w_i += lr * x_i(t) * delta(t). Dopamine firing is proposed to be delta(t) (a scalar broadcast to targets). The paper also sketches an actor-critic use of delta for action choice, and uses TD for bee foraging and simple cognitive maps.
- **Experiments:** Re-presents Schultz lab single-neuron recordings from alert monkeys (juice reward, conditioned light/sound cues; Fig. 1: unpredicted reward gives a burst, a learned cue moves the burst to the cue, an omitted reward gives a dip at the expected time). A simulated TD model trained on a cue followed by reward 20 time steps later (Fig. 3) reproduces this transfer.
- **Key results:**
  - Dopamine response to reward vanishes once reward is predicted and shifts to the earliest reliable predictor; omission produces a pause at the expected time.
  - The TD error reproduces these three response patterns qualitatively; the model also accounts for blocking.
- **Limitations / caveats:** Qualitative match on a small set of monkey tasks; the paper says how V(t) and the delay representation are neurally realised is unknown. A review/theory paper, not a new causal test. The sources.json entry lists Schultz, Dayan, Montague as authors, matching the row.
- **Bearing on H022:** Supports for reward learning. The row's open question (is it enough for abstraction?) is not addressed here; the paper's own extensions are small maze and foraging problems.
- **Reproduce in this repo:** Tabular TD(0) on a cue -> 20-step delay -> reward chain; log delta(t) at the cue, at reward and on omission; then run on a Brain World layout and probe whether learned V encodes structure beyond reward.

## Dabney 2020: A distributional code for value in dopamine-based reinforcement learning
- **Cited for:** H023 - dopamine neurons encode a distribution of future reward.
- **Link:** https://doi.org/10.1038/s41586-019-1924-6 · **Basis:** abstract only (PMC and nature.com blocked)
- **Question:** Does the brain represent the full distribution of possible rewards rather than only the mean?
- **Method / model:** Distributional TD from AI research: different value predictors weight positive and negative prediction errors asymmetrically and so converge to different points (expectile-like) of the reward distribution. (Only "inspired by distributional RL" is stated in the abstract.)
- **Experiments:** Single-unit recordings from mouse ventral tegmental area; analyses compared with the model (details not available from the abstract).
- **Key results:** Abstract: the recordings are "consistent with" a model in which the brain represents future reward as a distribution, and the authors call this strong evidence for a neural realisation of distributional RL.
- **Limitations / caveats:** Cannot be assessed from the abstract.
- **Bearing on H023:** Supports the first clause. "Giving richer learning signals" is the benefit claimed in AI work; the abstract does not test it in a downstream learning benefit.
- **Reproduce in this repo:** Population of TD units with asymmetric positive/negative learning rates on a stochastic-reward task; check the reversal points spread over the reward distribution, then compare representation quality against a scalar TD agent.

## Engelhard 2019: Specialized coding of sensory, motor and cognitive variables in VTA dopamine neurons
- **Cited for:** H024 - dopamine is a vector of feature-specific errors that target learning to specific network parts.
- **Link:** https://doi.org/10.1038/s41586-019-1261-9 · **Basis:** abstract only (bioRxiv/nature.com blocked)
- **Question:** Do individual dopamine neurons multiplex many behavioural variables, or do subsets specialise?
- **Method / model:** Two-photon calcium imaging through an implanted lens of VTA dopamine neurons in mice doing a decision task in virtual reality.
- **Experiments:** More than 300 dopamine neurons recorded during a complex VR navigation/decision task.
- **Key results:** Neurons encoded sensory, motor and cognitive variables in addition to reward; responses formed functional clusters (subpopulations carrying a subset of variables); clusters were spatially organised, with neighbours more likely in the same cluster.
- **Limitations / caveats:** The abstract only claims that specialisation "may aid downstream circuits".
- **Bearing on H024:** Partly supports. It shows heterogeneous, clustered dopamine coding, but the abstract does not say these are prediction errors about different features, nor that learning targets parts of a network. The row overstates this; the paper is evidence of a vector-like code, not of vector RPEs.
- **Reproduce in this repo:** Vector-valued TD error (one component per feature channel, each gating plasticity of its own weight block) vs scalar error in a multi-feature task; measure learning speed.

## Yu & Dayan 2005: Uncertainty, Neuromodulation, and Attention
- **Cited for:** H025 - ACh reports expected uncertainty, NE unexpected uncertainty; together they set trust in old vs new information.
- **Link:** https://doi.org/10.1016/j.neuron.2005.04.026 · **Basis:** full text (local PDF)
- **Question:** Can ACh and NE be interpreted as signals of two kinds of uncertainty in a Bayesian inference and learning scheme?
- **Method / model:** Hidden-Markov-style generative model of a context. Expected uncertainty = known unreliability of a cue within a context (cue invalidity); unexpected uncertainty = gross context change that strongly violates expectations. ACh is mapped to the first and NE to the second. Both suppress top-down (expectation-driven) relative to bottom-up input and promote learning about the context. The exact Bayesian learner is intractable, so an approximate iterative algorithm is used.
- **Experiments:** Simulations of (i) the Posner cueing task with cholinergic manipulation (nicotine and scopolamine/ACh depletion changing the validity effect), and (ii) an attention-shifting task with NE manipulation, plus an extended Posner task in which cue identity and validity change over blocks. Simulated results are compared qualitatively with published pharmacological data; e.g. Posner simulations run over 1000 trials.
- **Key results:**
  - ACh level modulates the validity effect in the model as in the drug data; enhanced NE speeds detection of context change but can cause false alarms.
  - The two signals interact, part antagonistic, part synergistic.
  - Predicts a class of attentional cueing tasks needing both signals.
- **Limitations / caveats:** Theory plus simulation matched to prior data, no new recordings; a mapping of transmitter to computation that remains a proposal; approximate inference.
- **Bearing on H025:** Supports the mapping. The paper's main effects are on inference and learning-about-context; it does not test a "fixed learning rate vs both signals" agent, which is the repo's own test.
- **Reproduce in this repo:** Switching-bandit or Posner-style agent with a Kalman/HMM learner; ACh-like term = estimated cue noise, NE-like term = surprise-triggered reset; compare with a fixed learning rate.

## Doya 2002: Metalearning and neuromodulation
- **Cited for:** H026 - neuromodulators set RL meta-parameters (dopamine error, serotonin time horizon, noradrenaline exploration, ACh learning rate).
- **Link:** https://doi.org/10.1016/s0893-6080(02)00044-8 · **Basis:** abstract only (sources.json holds no abstract; nothing could be fetched, so this note rests on the title and the row)
- **Question:** (From the title) How can neuromodulators implement the tuning of learning parameters, i.e. metalearning?
- **Method / model:** Not read.
- **Experiments:** Not read.
- **Key results:** Not read. The row's four-way mapping is the paper's well-known proposal, but I could not verify it from text in this session.
- **Limitations / caveats:** Unverified.
- **Bearing on H026:** Unverified; the citation is plausible by title. Re-check against the paper before relying on the exact assignments (especially ACh = learning rate).
- **Reproduce in this repo:** Agent whose gamma, softmax temperature and learning rate are driven by four scalar signals vs the same agent with tuned constants, across several tasks.

## Wang 2018: Prefrontal cortex as a meta-reinforcement learning system
- **Cited for:** H027 - slow dopamine-trained PFC weights give fast in-activity learning (meta-RL).
- **Link:** https://doi.org/10.1038/s41593-018-0147-8 · **Basis:** abstract only (bioRxiv/nature.com blocked)
- **Question:** Can reward-based learning be reframed so that dopamine trains PFC to be its own learning system?
- **Method / model:** Per the abstract, draws on AI advances; the dopamine system trains the prefrontal cortex to operate as a free-standing learning system. (Network and training details are not in the abstract.)
- **Experiments:** Not available from the abstract.
- **Key results:** Abstract claims the theory accommodates the findings behind the standard dopamine model and handles a wider range of observations.
- **Limitations / caveats:** Cannot be assessed.
- **Bearing on H027:** Supports the first sentence (slow dopamine training of prefrontal recurrent dynamics). "Abstraction lives in activity, not weights" is the row's extension; the abstract does not state it.
- **Reproduce in this repo:** Small LSTM/GRU trained by policy gradient across many Brain World layouts with frozen weights at test time; check whether performance rises within an episode on a new layout.

## Bittner 2017: Behavioral time scale synaptic plasticity underlies CA1 place fields
- **Cited for:** H028 - a single event rewrites synapses active seconds before or after (one-shot learning).
- **Link:** https://doi.org/10.1126/science.aan3846 · **Basis:** abstract only, plus Gerstner 2018's account of it (secondary)
- **Question:** How do CA1 place fields form? Is Hebbian pairing enough?
- **Method / model:** In vivo, in vitro and modelling data. Abstract: non-Hebbian plasticity; a single strong Ca2+ plateau potential in dendrites paired with spatial inputs may suffice to make a place cell.
- **Experiments:** Per Gerstner's review of the slice experiment: CA3 inputs stimulated by 10 pulses over 1 s, paired with a postsynaptic plateau (complex spike); LTP occurred even if the plateau came 1-2 s after or before the input, about 200 percent potentiation after only 5 pairings, NMDA receptors and calcium channels involved.
- **Key results:** Instead of many pairings, one plateau event can create a place field (abstract); second-scale window in both directions (Gerstner).
- **Limitations / caveats:** Not fully assessable from an abstract; slice protocol is more repetitive than "one lap".
- **Bearing on H028:** Supports. Caveat: the in-vitro result used 5 pairings; "one-shot" refers to the in-vivo plateau-induced field.
- **Reproduce in this repo:** Weight update dw_i = eta * trace_i(t) * plateau(t) with a symmetric 1-2 s kernel on trace_i (the synapse's recent input); run one lap past a plateau and test whether a place-like tuning appears.

## Dayan 1993 and Stachenfeld 2017: Successor representation
- **Cited for:** H029 - the hippocampus learns a successor representation by TD that transfers when rewards change.
- **Link:** https://doi.org/10.1162/neco.1993.5.4.613 and https://doi.org/10.1038/nn.4650 · **Basis:** abstract only (both)
- **Question:** Dayan: which representation lets TD generalise between states? Stachenfeld: which spatial representation is best for maximising reward, and does the hippocampus have it?
- **Method / model:** Dayan: TD machinery learns representations whose generalisation follows how similar states' successors are (the successor representation, SR); illustrated on a navigation task. Stachenfeld: argues the answer is a predictive representation and that entorhinal grid cells give a low-dimensional basis set for it.
- **Experiments:** Dayan: a navigation task. Stachenfeld: model comparison with place-cell and grid-cell data (details not in the abstract).
- **Key results:** Dayan: "appropriately distributed" representations result. Stachenfeld: the SR captures aspects of place cells beyond a pure cognitive map.
- **Limitations / caveats:** Abstracts only.
- **Bearing on H029:** Partly supports. Dayan 1993 is an RL paper, not a hippocampus paper; the neural claim comes from Stachenfeld only. Reward-revaluation transfer is not mentioned in either abstract; it is a known property of SR but unverified here.
- **Reproduce in this repo:** Tabular SR (M += alpha*(onehot(s)+gamma*M[s'] - M[s])) with V = M @ r; change r and compare the number of episodes to re-converge vs a model-free Q agent.

## Oudeyer 2007 and Schmidhuber 1991: Learning progress as intrinsic reward
- **Cited for:** H030 - learning progress is the intrinsic reward driving a self-made curriculum.
- **Link:** https://doi.org/10.1109/tevc.2006.890271 and https://doi.org/10.7551/mitpress/3115.003.0030 · **Basis:** abstract only (both)
- **Question:** Can a machine have an intrinsic drive towards learnable novelty?
- **Method / model:** Oudeyer: Intelligent Adaptive Curiosity, which pushes a robot to situations that maximise its learning progress, neither too predictable nor too unpredictable. Schmidhuber: curious neural controllers with a model network and a controller network, with a desire to improve the model's knowledge (the abstract does not say the reward is the drop in error; the later "learning progress" framing belongs to later work).
- **Experiments:** Oudeyer: two experiments, one with a physical robot on a play mat; the robot moves from easy to harder situations and avoids ones where nothing can be learned. Schmidhuber: framework paper.
- **Key results:** Oudeyer: stage-like developmental sequences self-organise without supervision.
- **Limitations / caveats:** Abstracts only; robot-scale demonstrations.
- **Bearing on H030:** Supports for Oudeyer. Schmidhuber 1991 is cited more loosely: the abstract describes curiosity as improving the model, not explicitly learning progress.
- **Reproduce in this repo:** Agent choosing among regions (some noise-only, some learnable, some trivial) by the recent slope of prediction error vs random choice; compare final competence.

## Mattar & Daw 2018: Prioritized memory access explains planning and hippocampal replay
- **Cited for:** H031 - replay is prioritised by usefulness for future choices, so replay is planning.
- **Link:** https://doi.org/10.1038/s41593-018-0232-z · **Basis:** full text (web; Europe PMC author manuscript)
- **Question:** Which memories should be accessed at each moment to optimise future decisions, and does this explain replay phenomena?
- **Method / model:** Dyna-style Q-learning: Q(s,a) += alpha[R + gamma max Q(s',.) - Q(s,a)] applied to real transitions and to remembered ones. Each candidate update has an expected value of backup, EVB = Gain x Need. Gain = expected improvement in policy return from the update; Need = discounted expected number of future visits to the state. The highest-EVB backup is performed first.
- **Experiments:** Grid-world simulations: a linear track (shuttle to rewards at the ends) and an open field; 20 planning steps at episode start and end; compared prioritised replay, random replay (original Dyna) and model-free learning from direct experience.
- **Key results:**
  - Prioritised replay learns faster than the others (value information propagates along relevant trajectories).
  - Reproduces replay findings: forward replay before a run (driven by need), reverse replay after reward (driven by gain), initiation bias at the animal's location, asymmetric effect of positive vs negative prediction errors, and open-field replay of future paths.
- **Limitations / caveats:** Authors say priority is defined abstractly and no brain mechanism for computing it is offered. Tabular punctate states, deterministic worlds (alpha = 1), qualitative match to recorded data.
- **Bearing on H031:** Supports; framing replay as planning is the paper's own. The repo's test (same sample efficiency?) is directly contradicted for the paper's simple grids, where prioritised replay was faster.
- **Reproduce in this repo:** Dyna agent on a gridworld: replay buffer sampled uniformly vs by Gain x Need; plot steps-per-episode vs episodes.

## Izhikevich 2007: Solving the Distal Reward Problem through Linkage of STDP and Dopamine Signaling
- **Cited for:** H032 - reward-modulated STDP plus slow dopamine solves distal reward in spiking nets.
- **Link:** https://doi.org/10.1093/cercor/bhl152 · **Basis:** abstract only
- **Question:** How can reward seconds after an action credit the right synapses despite ongoing activity?
- **Method / model:** Network of cortical spiking neurons with STDP modulated by dopamine; STDP is triggered on a ms scale, but the slow kinetics of the subsequent plasticity makes it sensitive to dopamine during a critical period of a few seconds.
- **Experiments:** Simulation (details not in the abstract).
- **Key results:** Random firing during the wait does not affect STDP, so the network is insensitive to ongoing activity, unlike earlier models that need a quiet network.
- **Limitations / caveats:** Abstract only. "A few seconds" is the stated critical period, so the row's planned failure beyond 1 s is a repo test, not a paper claim.
- **Bearing on H032:** Supports.
- **Reproduce in this repo:** Izhikevich-neuron net: dw = c * d with c' = -c/tau_c + STDP(pre,post), d' = -d/tau_d + reward pulses; vary reward delay 0.5-5 s and plot success.

## Miller, Shenhav & Ludvig 2019: Habits without values
- **Cited for:** H033 - habits come from an action-prediction error, separate from value.
- **Link:** https://doi.org/10.1037/rev0000120 · **Basis:** abstract only
- **Question:** Can habits be modelled without outcome value, as direct strengthening of recent actions?
- **Method / model:** Value-free model in which habit strength grows by repeating recent actions rather than by encoding outcomes.
- **Experiments:** Simulations against behavioural phenomena.
- **Key results:** Accounts for insensitivity to outcome devaluation and contingency degradation, the effect of reinforcement schedule on habit formation, and perseveration in repeated-choice tasks.
- **Limitations / caveats:** Abstract only; the abstract does not name an "action prediction error" and the row's phrase is a paraphrase (the model's update is a repetition-based strengthening).
- **Bearing on H033:** Supports in spirit; "action-prediction error" should be checked in the full text.
- **Reproduce in this repo:** n/a on the model fit; for a quick check, habit-trace-plus-value agent on a devaluation task.

## O'Reilly & Frank 2006: Making Working Memory Work (PBWM)
- **Cited for:** H034 - basal ganglia learn by RL when to gate information into PFC working memory; learning to gate is learning to abstract.
- **Link:** https://doi.org/10.1162/089976606775093909 · **Basis:** abstract only
- **Question:** How can a model of PFC control its own working-memory updating without a homunculus?
- **Method / model:** Actor-critic architecture based on midbrain, basal ganglia and amygdala: the critic learns which prefrontal representations are task relevant and trains the actor, which provides dynamic gating of working-memory updating; designed to solve temporal and structural credit assignment together.
- **Experiments:** 1-2-AX working-memory task and other benchmark working-memory tasks.
- **Key results:** The model "compares favorably" with standard backprop-based temporal learning (e.g. on 1-2-AX).
- **Limitations / caveats:** Abstract only; no numbers available.
- **Bearing on H034:** Supports the first sentence. "Learning to gate is learning to abstract" is not in the abstract.
- **Reproduce in this repo:** Gated memory cell (open/close via an RL-trained gate) vs plain RNN on a 1-2-AX-style task.

## Behrens 2007: Learning the value of information in an uncertain world
- **Cited for:** H035 - learning rate tracks volatility; the brain estimates volatility.
- **Link:** https://doi.org/10.1038/nn1954 · **Basis:** abstract only
- **Question:** How much weight should past outcomes carry, and does the brain scale it by environmental volatility?
- **Method / model:** Optimal (Bayesian) estimate of volatility, compared with human choices.
- **Experiments:** Human subjects in a reward-learning task with fMRI.
- **Key results:** Humans assess volatility near-optimally; anterior cingulate fMRI signal reflects the volatility estimate and the salience of new information; across-subject variation in the ACC signal predicts variation in learning rates.
- **Limitations / caveats:** Abstract only; fMRI correlation.
- **Bearing on H035:** Supports. Phrase "faster when the world changes" matches the abstract's logic.
- **Reproduce in this repo:** Switching bandit with learner lr = f(running surprise) vs fixed lr; regret vs switch rate.

## Aitchison 2021: Synaptic plasticity as Bayesian inference
- **Cited for:** H036 - each synapse keeps an uncertainty and changes more when unsure.
- **Link:** https://doi.org/10.1038/s41593-021-00809-5 · **Basis:** full text (local PDF is the submitted pre-peer-review manuscript)
- **Question:** If synapses estimate weights with error bars, what learning rules result, and do they beat classical rules?
- **Method / model:** Two hypotheses: Bayesian plasticity (each synapse keeps mean mu_i and variance sigma_i^2; mu changes by an effective learning rate proportional to sigma_i^2, times presynaptic term x_i and a postsynaptic term f(feedback); sigma_i^2 shrinks on presynaptic spikes and grows back toward a prior otherwise) and Synaptic Sampling (trial-to-trial PSP variability reads out uncertainty). Generalises the delta rule.
- **Experiments:** Simulated single neurons tracking a drifting target weight (linear, cerebellar-like and other feedback signals) and a recurrent network whose output weights are trained to a target function; classical rules swept over their learning rate; medians over n = 400 network/target pairs; PSP variability compared with data.
- **Key results:**
  - Mean weights track the target; the 95 percent interval covers the target 95 percent of the time.
  - Bayesian rules beat classical rules at every learning rate in single neurons, and in the network the mean squared error is about an order of magnitude smaller.
  - Predicts uncertainty-dependent learning rates across synapses and the PSP variability relation.
- **Limitations / caveats:** Baselines are classical delta-like rules with a single learning rate, not backprop-trained deep nets; the plasticity experiments needed to test it do not yet exist (authors).
- **Bearing on H036:** Supports in simulation. The row's comparison ("vs plain SGD in a net") goes beyond the paper, which only tests output weights of a small recurrent net.
- **Reproduce in this repo:** Linear regression with per-weight Kalman updates (variance-scaled lr) vs fixed-lr delta rule on a drifting target; compare MSE.

## Hasselmo 2006: The role of acetylcholine in learning and memory
- **Cited for:** H037 - ACh switches the hippocampus between encoding (high) and retrieval (low) to reduce interference.
- **Link:** https://doi.org/10.1016/j.conb.2006.09.002 · **Basis:** abstract only (Europe PMC abstract)
- **Question:** What is ACh's role in encoding new memories?
- **Method / model:** Review of pharmacology, lesion/antagonist work and computational modelling.
- **Experiments:** Review.
- **Key results:** Muscarinic and nicotinic receptors both matter for encoding; ACh increases the strength of afferent input relative to feedback, contributes to theta rhythm, activates persistent spiking mechanisms and increases synaptic modification; this may aid encoding of new episodic memories in entorhinal, perirhinal and hippocampal regions.
- **Limitations / caveats:** Abstract only; the abstract does not mention low ACh for retrieval or interference.
- **Bearing on H037:** Partly supports (encoding side). The retrieval-at-low-ACh half and the interference-avoidance purpose are not in the abstract and need checking in the full text.
- **Reproduce in this repo:** Hopfield or autoassociator with a mode flag: encoding mode weakens recurrent feedback and boosts learning, retrieval mode the reverse; measure interference between sequentially stored sets.

## H038 (no citation)
- **Cited for:** H038 - infants vs adults use different neuromodulator balances, changing exploration vs exploitation across a lifetime. The row marks it **new**; there is no source to check. No note.

## Corrections to the hypotheses file
- H024: "Dopamine is a vector, not a scalar: different neurons carry errors about different features" overstates Engelhard 2019, which shows clustered coding of sensory, motor and cognitive variables (plus reward). Rephrase as "dopamine neurons form functional clusters encoding different variables; whether they are feature-specific prediction errors is open".
- H029: Dayan 1993 is not about the hippocampus; attribute the hippocampal claim to Stachenfeld 2017 and the SR/TD algorithm to Dayan 1993. Reward-revaluation transfer is not stated in either abstract.
- H030: Schmidhuber 1991's abstract talks of improving the model network's knowledge, not explicitly learning progress; Oudeyer 2007 is the direct source for learning progress.
- H033: "action-prediction error" is not in the abstract; check full text or soften to "value-free strengthening of recent actions".
- H034: the second sentence ("learning to gate is learning to abstract") is the repo's extension, not O'Reilly & Frank's claim.
- H036: the paper compares with delta-like single-learning-rate rules, not SGD in deep nets.
- H037: abstract does not support "low ACh for retrieval to avoid interference"; verify against full text.
- H038: uncited ("new"); mark as speculation.
- H026 (Doya) could not be verified from text; H023, H024, H027, H028 rest on abstracts (H028 also on Gerstner's account).
