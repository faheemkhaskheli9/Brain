# B. Reward, neuromodulators and three-factor rules, explained

Part of [the 170 hypotheses, explained simply](README.md). Main table and status:
[learning-algorithm-hypotheses.md](../learning-algorithm-hypotheses.md). Every row is a
**hypothesis**, not an established fact.

## The big idea of this group

A brain gets very little direct teaching. Mostly it gets rewards and punishments, often
seconds after the action that earned them. So how does a synapse know whether its last
change was a good idea? These rows say the answer involves **neuromodulators**: chemicals
such as dopamine, acetylcholine, noradrenaline and serotonin that a few small groups of
neurons spray widely across the brain. Some background is established textbook science:
dopamine neurons fire more for unexpected reward and less when an expected reward is
missing, and neuromodulators change how easily synapses change (see
[neuromodulators](../../function/neuromodulators.md) and
[learning-and-plasticity](../../function/learning-and-plasticity.md)). What is claimed here
goes further: what exactly each signal means (H022-H026, H035, H037), how a delayed signal
reaches the right synapse (H021, H028, H032, H036), and how reward learning could produce
maps, plans, habits and abstraction (H027, H029-H031, H033, H034, H038). Some rows compete:
H025, H026 and H035 give different accounts of what sets the learning rate, and H022 (one
scalar error) competes with H023 and H024 (richer error signals).

## H021 - Three factors: Hebb, trace, neuromodulator
**Status:** open · **Tier:** T1 · **Source:** Gerstner et al. 2018, *Front Neural Circuits*

**In simple words.** Plain Hebbian learning says "cells that fire together wire together".
That alone cannot tell good wiring from bad. This hypothesis adds two pieces. When two
connected neurons fire together, the synapse between them gets a temporary tag, called an
**eligibility trace**, which fades over a few seconds. If a third signal (a
neuromodulator like dopamine) arrives while the tag is still there, the tag is turned into
a real, lasting weight change. It is like marking pages with sticky notes while you read,
and only copying the marked pages into your notebook if the teacher later says "good".

**How it would work in the brain (if true).**
1. A presynaptic neuron fires and the postsynaptic neuron fires soon after (established:
   coincident firing is the trigger for Hebbian and STDP changes).
2. Instead of changing the weight at once, the synapse sets a chemical tag that decays over
   seconds.
3. The animal acts, and some time later an outcome happens.
4. A neuromodulator burst (for example dopamine after a better-than-expected outcome)
   reaches many synapses at once.
5. Only tagged synapses change. The sign and size of the change depend on the
   neuromodulator signal times the tag.
6. Untagged synapses ignore the broadcast, so credit goes only to recently active paths.

**How to test it here.**
Inside the standard test loop:
1. Build a small numpy network (for example the **Tiny MLP** size, or a single layer of
   about 100 units) that picks one of a few actions from an input pattern.
2. Deliver reward only after a delay of several time steps, so the network must bridge the
   gap.
3. Learning rule: Hebbian product into a decaying trace, then weight change = trace times
   a delayed reward signal.
4. Baselines: the same net with no trace (reward meets only current activity) and a random
   policy (chance).
5. Metric: fraction of correct choices after training, across at least 5 seeds and a range
   of delays and trace time constants.

**Counts against it if:** the three-factor net on the delayed-reward task does no better
than chance.

**Why it matters for a brain-like learner.** This is the basic local rule that most other
rows in this section build on, and [Brain World](../../game/world/) already uses a version
of it. It is the reward-based alternative to the backprop approximations in section A.

## H022 - Dopamine as a prediction error
**Status:** open · **Tier:** T1 · **Source:** Schultz, Dayan & Montague 1997, *Science*

**In simple words.** A **reward-prediction error** is "what I got minus what I expected".
**Temporal-difference (TD) learning** is a way to learn predictions by comparing each
guess with the next, slightly better-informed guess. This row says the short bursts and
dips of dopamine neurons (phasic dopamine) are exactly this TD error. The table notes that
this is strongly supported for reward. The open question here is different: is a TD error
enough to learn abstract structure, not just which actions pay off?

**How it would work in the brain (if true).**
1. An unexpected reward arrives, and dopamine neurons in the VTA and substantia nigra burst
   (established).
2. After repeated pairing, the burst moves to the earliest cue that predicts the reward
   (established).
3. If the predicted reward then fails to arrive, dopamine dips below baseline at the
   expected time (established).
4. The claim: this burst or dip is the TD error δ = reward + discounted next value − current
   value, and it is broadcast to striatum and cortex.
5. Synapses that were recently active (H021) strengthen after a positive δ and weaken after
   a negative δ.
6. The open part: whether this alone builds the abstract rules and maps needed for
   transfer.

**How to test it here.**
Inside the standard test loop:
1. Use the existing TD actor-critic in **Brain World** as the agent.
2. Run it in the **H101 transfer setup**: train on some layouts, test on new ones that share
   structure.
3. Compare with an agent given an explicit structure prior or model (for example from
   H029 or H027).
4. Metric: performance on new layouts in the first episodes, and episodes needed to reach
   the pass rate, over at least 5 seeds.
5. Probe hidden units for a code of the shared structure (for example decode letter or
   goal identity independent of layout).

**Counts against it if:** the Brain World TD agent cannot learn the structure (no transfer
to new layouts).

**Why it matters for a brain-like learner.** TD learning is the core of the current Brain
World learner. If it cannot build structure, the extra machinery of H023, H024, H027 and
H029 is needed on top.

## H023 - Dopamine carries a reward distribution
**Status:** open · **Tier:** T1 · **Source:** Dabney et al. 2020, *Nature*

**In simple words.** Standard TD learning predicts one number: the average future reward.
**Distributional reinforcement learning (RL)** instead predicts the whole spread of
possible rewards. Some predictors are optimistic and some are pessimistic. This row says
different dopamine neurons act like these different predictors, so together they encode a
full distribution. Think of a weather forecast that gives "a 30% chance of heavy rain"
instead of only "average rainfall: light". The claim is that this richer signal also
teaches the rest of the network better features.

**How it would work in the brain (if true).**
1. A cue appears that predicts an uncertain reward (sometimes small, sometimes large).
2. Each dopamine neuron weighs positive and negative surprises differently. Some react
   more to good surprises (optimistic), others more to bad ones (pessimistic).
3. Because of this, each neuron's value prediction settles at a different point of the
   reward distribution.
4. Downstream, the target synapses of each neuron learn their own part of the distribution.
5. The claim: the many different error signals push shared upstream features to capture
   more about the world than one average error would.

**How to test it here.**
Inside the standard test loop:
1. In **Brain World**, replace the single critic with a set of critics, each with its own
   ratio of positive to negative learning rates (distributional TD).
2. Keep everything else the same, including the policy and total learning budget.
3. Baseline: the standard scalar TD critic.
4. Metrics: speed to pass each skill, and how well a simple linear readout from hidden
   units decodes task variables (a representation-quality probe).
5. At least 5 seeds; also test in the **H101 transfer setup**.

**Counts against it if:** distributional TD gives no representation gain over scalar TD in
Brain World.

**Why it matters for a brain-like learner.** It competes with plain H022 and is a cheap
upgrade if it works. It also pairs with H024: both say the dopamine signal is richer than
one number.

## H024 - Dopamine as a vector of errors
**Status:** open · **Tier:** T1/T2 · **Source:** Engelhard et al. 2019, *Nature*

**In simple words.** The classic view says all dopamine neurons send the same message: one
number for "better or worse than expected". This row says dopamine is more like a set of
separate messages. Different dopamine neurons carry errors about different features of the
task (for example where you are, what you see, how you move). Each message reaches a
different part of the network. It is like a coach giving each player their own feedback
instead of shouting one score at the whole team.

**How it would work in the brain (if true).**
1. The animal does a task with several relevant features at once.
2. Different dopamine neurons respond to different features, not only to reward (the
   source reports diverse dopamine responses in mice).
3. Each dopamine neuron projects to its own patch of striatum or cortex.
4. Synapses in that patch use their local error as the third factor (H021).
5. The claim: learning then goes to the parts of the network that handle that feature,
   which speeds up learning compared with one shared error.

**How to test it here.**
Inside the standard test loop:
1. Build a small numpy task with several independent features that each affect reward
   (for example a multi-armed task where colour and position both matter).
2. Split the network into modules, one per feature.
3. Vector RPE: each module gets an error about its own feature. Baseline: every module gets
   the same scalar RPE.
4. Metric: trials to reach a fixed accuracy, at least 5 seeds.
5. For T2: check open dopamine recording datasets for neurons tuned to non-reward variables.

**Counts against it if:** vector RPE gives no speed-up over scalar RPE in the
multi-feature task.

**Why it matters for a brain-like learner.** A vector error is a step from reward learning
towards targeted credit assignment (section A). It competes with the one-number view of
H022 and links to H023.

## H025 - ACh and noradrenaline report two uncertainties
**Status:** open · **Tier:** T1 · **Source:** Yu & Dayan 2005, *Neuron*

**In simple words.** There are two kinds of uncertainty. **Expected uncertainty** is known
noise: "this cue is right 70% of the time". **Unexpected uncertainty** is a sign the rules
just changed: "this cue used to be reliable and now it is wrong every time". This row says
acetylcholine (ACh) reports the first and noradrenaline (NA) the second. Together they set
how much you trust what you already know versus what you see now. It is like a sailor who
knows the compass wobbles a bit (expected), but who should throw away the old map when the
coastline no longer matches (unexpected).

**How it would work in the brain (if true).**
1. The brain holds a current belief about which rule or context is in force.
2. ACh level rises when that belief is known to be unreliable. This lowers the weight of
   top-down predictions and raises the weight of sensory input.
3. When observations strongly contradict the belief, NA from the locus coeruleus rises.
4. A high NA signal says "the world changed": the old belief is dropped or reset.
5. Learning then focuses on the new context, while ACh again tracks ordinary noise.

**How to test it here.**
Inside the standard test loop:
1. Build a switching task in numpy: cues predict outcomes with known noise, and the rule
   changes at random times.
2. Agent with two signals: an ACh-like estimate of cue unreliability and an NA-like
   change detector that resets beliefs.
3. Baseline: the same agent with a fixed learning rate, tuned on the task.
4. Metric: accuracy right after switches and in stable periods; at least 5 seeds.
5. Ablation: remove each signal in turn to see which one carries any gain.

**Counts against it if:** the agent with both signals shows no gain over a fixed learning
rate on the switching task.

**Why it matters for a brain-like learner.** It gives a principled way to set learning
rates without hand tuning. It overlaps and competes with H026 and H035, which assign these
roles differently.

## H026 - Neuromodulators set learning meta-parameters
**Status:** open · **Tier:** T1 · **Source:** Doya 2002, *Neural Netw*

**In simple words.** A **meta-parameter** is a setting that controls learning itself, not
what is learned. Every RL agent has a few: how big the error is, how far into the future
it cares (the time horizon), how much it explores, and how fast it learns (learning rate).
This row says four neuromodulators set these four dials. Dopamine carries the error,
serotonin sets the time horizon, noradrenaline sets exploration, and acetylcholine sets the
learning rate. It is like a sound mixer with four sliders that the brain moves to suit the
situation.

**How it would work in the brain (if true).**
1. Dopamine carries the TD error that drives value learning (H022; the error part is the
   best-supported piece).
2. Serotonin level sets the discount factor: high serotonin means caring about rewards
   further away.
3. Noradrenaline sets the randomness of action choice (how much to explore).
4. Acetylcholine sets how fast synapses update.
5. Brain areas that monitor progress adjust these levels as tasks change.

**How to test it here.**
Inside the standard test loop:
1. Take a simple numpy RL agent (or the **Brain World** agent) with four meta-parameters.
2. Add a controller that changes them online from simple signals (recent reward rate,
   error size, surprise).
3. Baseline: constants tuned for each task separately, and one set of constants for all
   tasks.
4. Run a mix of tasks (short and long reward delays, stable and changing). Metric: average
   reward per task, at least 5 seeds.

**Counts against it if:** the agent with modulated meta-parameters shows no gain across
tasks over tuned constants.

**Why it matters for a brain-like learner.** If true, a single learner can handle many
tasks without retuning. It competes with H025 and H035 on what controls the learning rate,
and links to H038 (the dials could change across a lifetime).

## H027 - Dopamine trains a fast prefrontal learner
**Status:** open · **Tier:** T1 · **Source:** Wang et al. 2018, *Nat Neurosci*

**In simple words.** **Meta-RL** means "learning to learn". Dopamine slowly adjusts the
weights of a **recurrent network** (a network whose neurons feed back into each other, so it
keeps a running state) in prefrontal cortex. After training on many related tasks, the
network can solve a new task of the same kind within one episode. It does this by changing
its activity, not its weights. It is like an experienced puzzle solver who quickly works
out a new puzzle's rules in their head, without having to relearn how puzzles work.

**How it would work in the brain (if true).**
1. Prefrontal cortex has dense recurrent connections and holds information in activity
   (established: persistent activity in working memory).
2. On each step it receives the current input, its last action and the last reward.
3. Dopamine RPE slowly changes its recurrent weights across many tasks.
4. The weights come to encode a general strategy for this family of tasks.
5. On a new task, the network's activity tracks what works, so behaviour improves within
   the episode with no weight change.
6. The claim: the abstract rule lives in this activity pattern.

**How to test it here.**
Inside the standard test loop:
1. Build a small numpy recurrent network that gets observation, last action and last
   reward.
2. Train its weights slowly with RL across many **Brain World** layouts.
3. Freeze the weights. Test on new layouts (the **H101 transfer setup**).
4. Metric: does reward rise within a test episode? Compare early vs late trials of each
   test episode.
5. Baseline: a feedforward agent with no recurrence, at least 5 seeds.

**Counts against it if:** the meta-RL network shows no in-episode learning on new
layouts.

**Why it matters for a brain-like learner.** It moves fast learning out of synapses into
activity, which avoids slow weight updates for each new task. It links to H034 (gating
into working memory) and offers one route past the limits of plain H022.

## H028 - One event rewrites synapses: BTSP
**Status:** open · **Tier:** T1 · **Source:** Bittner et al. 2017, *Science*

**In simple words.** **Behavioural-timescale synaptic plasticity (BTSP)** is a kind of
learning where one strong event in a neuron changes synapses that were active seconds
before or after it. Normal STDP needs spikes within milliseconds of each other; BTSP works
over seconds, the time scale of behaviour. The source found that a single such event in
hippocampal place cells can create a new **place field** (a spot where the cell fires) in
one pass. This row claims BTSP is a general tool for one-shot learning. It is like
remembering a whole street after one surprising thing happened there.

**How it would work in the brain (if true).**
1. A mouse runs along a track. Inputs for each location reach a CA1 pyramidal neuron.
2. At some point a strong dendritic event (a **plateau potential**, a long electrical
   burst in the dendrite) occurs.
3. Synapses that were active within a window of seconds around this plateau strengthen,
   on both sides in time.
4. After this single event, the neuron fires at that place on later laps.
5. The claim: the same mechanism lets other areas store a new association after one
   exposure.

**How to test it here.**
Inside the standard test loop:
1. Build a numpy model: a ring track with location inputs to a set of CA1-like units.
2. Plasticity rule: each synapse keeps a slow trace of its input; a random or
   reward-triggered plateau adds weight in proportion to that trace on both sides in time.
3. Run one lap with plateaus, then test laps with plasticity off.
4. Metric: fraction of units with a stable place field, and how well location can be
   decoded from the population; at least 5 seeds.
5. Baseline: standard STDP with a millisecond window over the same single lap.

**Counts against it if:** the BTSP model cannot form a place map in one lap.

**Why it matters for a brain-like learner.** One-shot learning is a big gap between brains
and most deep learning. It links to H021 (the trace idea) and to fast hippocampal memory
(H037, section F).

## H029 - Hippocampus learns a successor map
**Status:** open · **Tier:** T1 · **Source:** Dayan 1993, *Neural Comput*; Stachenfeld et al. 2017, *Nat Neurosci*

**In simple words.** A **successor representation (SR)** stores, for each place or state,
"where am I likely to be soon if I keep behaving as usual?". It separates two things: the
map of where things lead and the value of each place. If a reward moves, you only update
the rewards and combine them with the old map. You do not have to relearn everything. It is
like knowing which bus stops follow which: if your friend moves house, you can plan a new
trip at once.

**How it would work in the brain (if true).**
1. The animal moves through an environment and visits states in sequence.
2. Hippocampal cells learn, by a TD-like rule, a predictive code: each state's code
   includes its likely future states.
3. Place-cell firing fields stretch and skew towards where the animal usually goes next
   (the source argues this matches known place-cell data).
4. Value = SR map combined with current reward per state.
5. When reward moves, only the reward weights change, and new values follow at once.

**How to test it here.**
Inside the standard test loop:
1. Build a small numpy grid world (or use **Brain World** layouts).
2. SR agent: learn the SR matrix by TD and a separate reward vector.
3. Baseline: a model-free TD agent of the same size.
4. Train, then change reward locations (reward revaluation). Metric: performance in the
   first episodes after the change; at least 5 seeds.
5. Also test a path change (a new wall), where the SR is expected to adapt more slowly, to
   map its limits.

**Counts against it if:** the SR agent shows no transfer advantage over a model-free
agent after reward revaluation.

**Why it matters for a brain-like learner.** The SR sits between model-free and
model-based learning and gives cheap transfer when goals change. It links to H031 (replay
can update the map) and to [spatial-navigation](../../function/spatial-navigation.md).

## H030 - Learning progress as intrinsic reward
**Status:** open · **Tier:** T1 · **Source:** Oudeyer et al. 2007, *IEEE Trans Evol Comput*; Schmidhuber 1991

**In simple words.** An **intrinsic reward** is a reward the learner gives itself, with no
food or points from outside. This row says the reward is **learning progress**: how fast
your prediction errors are dropping. Things you already know are boring (no progress).
Pure noise is also boring (no progress, however hard you try). The fun zone is in between,
where you are getting better. A child does this when they practise a new trick until it is
easy, then move on. The result is a curriculum the learner makes for itself.

**How it would work in the brain (if true).**
1. The brain keeps predicting the results of its actions in different activities.
2. It tracks how prediction error changes over time for each activity.
3. A drop in error (improvement) is turned into an internal reward signal, perhaps through
   dopamine.
4. Action selection favours activities with the most recent improvement.
5. As an activity is mastered, progress stops and attention moves to the next learnable
   activity.

**How to test it here.**
Inside the standard test loop:
1. Build a numpy environment with several activities: some easy, some hard but learnable,
   some pure noise.
2. Learning-progress agent: chooses activities by the recent drop in its own prediction
   error.
3. Baselines: random choice of activity, and choice by raw prediction error (curiosity
   that gets stuck on noise).
4. Metric: final competence across all learnable activities after a fixed budget; at least
   5 seeds.
5. Option: let the **Brain World** creature choose its own order of skills.

**Counts against it if:** the learning-progress agent reaches the same final competence
as random exploration.

**Why it matters for a brain-like learner.** A self-made curriculum means less hand design
of tasks. It links to H038 (exploration across a lifetime) and to section C (prediction
error as the base signal).

## H031 - Replay prioritised by usefulness
**Status:** open · **Tier:** T1 · **Source:** Mattar & Daw 2018, *Nat Neurosci*

**In simple words.** **Replay** is when the hippocampus rapidly re-runs sequences of past
(or possible) experience during rest or sleep. This row says the brain does not replay at
random. It picks the memories whose replay would most improve future choices. A memory is
worth replaying if it would change your plan (**gain**) and if you are likely to be in
that situation again soon (**need**). So replay is a kind of planning. It is like a
student who rehearses only the exam questions they are likely to get and still get wrong.

**How it would work in the brain (if true).**
1. During rest or sleep, hippocampal cells fire in fast sequences that match past paths
   (established: replay exists).
2. The claim: each candidate memory gets a priority = gain × need.
3. The highest-priority experience is replayed first.
4. Each replay updates values (through a TD-like step) as if the experience happened again.
5. Replay of paths ahead of the animal works as planning; replay of paths behind spreads
   new reward information backwards.

**How to test it here.**
Inside the standard test loop:
1. Use a numpy grid world, then **Brain World**, with a memory buffer of past steps.
2. Prioritised agent: replay steps chosen by an estimate of gain × need.
3. Baselines: random replay with the same number of replays, and no replay.
4. Metric: sample efficiency (real steps to reach the pass rate); at least 5 seeds.
5. Record which steps get replayed and check whether they cluster near choice points and
   goals, as the source predicts.

**Counts against it if:** prioritised replay gives the same sample efficiency as random
replay in Brain World.

**Why it matters for a brain-like learner.** Smart replay can save a lot of real
experience. It links to H029 (replay can train a successor map) and to section F on
consolidation; see [sleep-and-memory-consolidation](../../function/sleep-and-memory-consolidation.md).

## H032 - R-STDP solves the distal-reward problem
**Status:** open · **Tier:** T1 · **Source:** Izhikevich 2007, *Cereb Cortex*

**In simple words.** The **distal-reward problem** is: a reward comes seconds after the
spikes that caused it, and by then many other spikes have happened. How does the brain
credit the right ones? **Reward-modulated STDP (R-STDP)** combines spike-timing-dependent
plasticity with dopamine. A pre-before-post spike pair does not change the synapse right
away. It leaves a decaying tag, and dopamine arriving later turns the tag into a weight
change. This is H021 tested in a network of spiking neurons, where timing is exact to the
millisecond.

**How it would work in the brain (if true).**
1. Pre- and postsynaptic spikes at a synapse follow the STDP timing rule (established:
   STDP exists in many synapses).
2. Each STDP event adds to a slowly decaying eligibility trace instead of the weight.
3. The network keeps firing; most traces decay without effect.
4. A reward causes a dopamine release a second or more later.
5. Dopamine times trace changes each weight. Synapses tagged just before the reward-causing
   pattern change most.
6. Over repeats, the causal synapse stands out from random coincidences.

**How to test it here.**
Inside the standard test loop:
1. Build a numpy spiking network (leaky integrate-and-fire neurons, a few hundred units).
2. Reward a chosen pre-post spike pattern after a delay. Sweep the delay from short to
   several seconds.
3. Baseline: plain STDP (no dopamine), and R-STDP with no trace.
4. Metric: growth of the target synapse(s) relative to the rest, at each delay; at least 5
   seeds.
5. Vary trace time constant and background firing rate to find where it breaks.

**Counts against it if:** the R-STDP spiking net fails at delays over 1 s.

**Why it matters for a brain-like learner.** It shows whether three-factor learning still
works with real spike timing, which matters for neuromorphic hardware. See
[spiking-neural-networks](../../simulation/spiking-neural-networks.md).

## H033 - Habits from an action-prediction error
**Status:** open · **Tier:** T1/T2 · **Source:** Miller, Shenhav & Ludvig 2019, *Psychol Rev*

**In simple words.** A **habit** is a behaviour you repeat even when its result is no
longer wanted. The usual RL story says habits come from slowly learned values. This row
says habits come from a different signal: an **action-prediction error**, "what did I just
do, compared with what I usually do here?". Repeating an action strengthens it, whether or
not it paid off. Value learning runs alongside as a separate system. It is like taking
your usual route home out of pure repetition, even on the day you meant to go to the shop.

**How it would work in the brain (if true).**
1. In a given situation, the brain predicts which action it will take.
2. After acting, it compares the actual action with that prediction (an action-prediction
   error, with no reward in it).
3. A "habit" system strengthens the link from situation to the action just taken.
4. A separate value system learns from reward-prediction errors (H022).
5. Choice mixes both systems; with more repetition the habit side gets stronger.
6. In **outcome devaluation** tests (the reward is made unpleasant after training), the
   habit side keeps the old action going (established: overtrained animals keep pressing
   after devaluation).

**How to test it here.**
Inside the standard test loop:
1. Build a small numpy model with two parts: a habit learner (action-prediction error) and
   a value learner (RPE).
2. Simulate a standard devaluation experiment with short and long training.
3. Baseline: a value-only model (including a model-based plus model-free value model).
4. Metric: fit to the pattern of behaviour after devaluation, compared with fewer free
   parameters favoured; at least 5 seeds for simulations.
5. For T2: fit both models to open behavioural datasets from devaluation or sequential
   choice tasks.

**Counts against it if:** the habit-plus-value model gives no better fit to devaluation
data.

**Why it matters for a brain-like learner.** Value-free habits make stable skills cheap to
run and hard to overwrite. See
[action-selection-and-motor-control](../../function/action-selection-and-motor-control.md).

## H034 - Basal ganglia learn when to gate
**Status:** open · **Tier:** T1 · **Source:** O'Reilly & Frank 2006, *Neural Comput*

**In simple words.** **Working memory** holds a few items "in mind" for seconds.
**Gating** means deciding when to let a new item in and when to protect what is already
there. This row says the basal ganglia (deep brain nuclei involved in action selection)
learn by RL when to open the gate into prefrontal working memory. The model is called
**PBWM** (prefrontal cortex basal ganglia working memory). The deeper claim is that
learning what to hold, and when, is a form of abstraction. It is like a secretary who
learns which notes to pin on the board and which to ignore.

**How it would work in the brain (if true).**
1. Prefrontal cortex holds items in stripes of persistent activity (established:
   prefrontal persistent activity supports working memory).
2. For each stripe, the striatum decides "update now" or "keep" (Go or NoGo), like
   choosing an action.
3. If the task later succeeds, dopamine reinforces the gating choices that led there.
4. Over time the basal ganglia learn to store task rules and context, not every input.
5. Stored context then controls how later inputs are handled, which supports hierarchical
   rules.

**How to test it here.**
Inside the standard test loop:
1. Build a hierarchical rule task in numpy (for example 1-2-AX: an outer cue sets which
   inner sequence is the target).
2. PBWM-style model: a few memory slots with gates trained by RL from reward.
3. Baseline: a plain recurrent network of similar size trained on the same reward.
4. Metric: trials to reach a fixed accuracy, and accuracy when the rule changes; at least 5
   seeds.
5. Option: test whether a gated memory helps **Brain World** stage 4 (holding a seen
   letter).

**Counts against it if:** PBWM-style gating gives no gain over a plain RNN on the
hierarchical rule task.

**Why it matters for a brain-like learner.** It explains how reward learning could
control what is held in mind, which H027 also needs. See
[prefrontal-cortex-and-abstraction](../../function/prefrontal-cortex-and-abstraction.md).

## H035 - Learning rate follows volatility
**Status:** open · **Tier:** T1 · **Source:** Behrens et al. 2007, *Nat Neurosci*

**In simple words.** **Volatility** is how often the world changes its rules. In a stable
world you should learn slowly, so one odd result does not throw you off. In a fast-changing
world you should learn fast, so you keep up. This row says the brain estimates volatility
and sets its learning rate from it. It is like trusting yesterday's weather forecast in a
calm season but checking the sky every hour in a stormy one.

**How it would work in the brain (if true).**
1. The brain makes predictions about outcomes (for example which option pays).
2. It tracks how surprising recent outcomes have been and how quickly the true rates seem
   to drift.
3. From this it keeps an estimate of volatility (the source links this to anterior
   cingulate cortex activity).
4. High volatility raises the learning rate; low volatility lowers it.
5. Value updates use this adjusted rate.

**How to test it here.**
Inside the standard test loop:
1. Build a two-armed switching bandit in numpy with stable blocks and volatile blocks.
2. Volatility learner: a simple Bayesian or heuristic estimate of change rate that sets
   the learning rate.
3. Baseline: a fixed-rate learner with the best single rate for the whole task.
4. Metric: total reward and prediction accuracy in each block type; at least 5 seeds.

**Counts against it if:** the volatility-tracking learner shows no gain over a fixed rate
on the switching bandit.

**Why it matters for a brain-like learner.** It removes a hand-tuned constant. It is
closely related to H025 (where noradrenaline would report the change) and competes with
H026's assignment of the learning rate to acetylcholine.

## H036 - Synapses that know their own uncertainty
**Status:** open · **Tier:** T1 · **Source:** Aitchison et al. 2021, *Nat Neurosci*

**In simple words.** **Bayesian inference** means keeping a best guess plus how sure you
are about it, and updating both with new evidence. This row says each synapse does this.
It stores a weight and an uncertainty. A synapse that is unsure changes a lot when new
evidence comes in. A synapse that is sure barely moves. It is like a jury member who has
heard little evidence yet and is easily swayed, compared with one who has heard a lot. The
claim is that this makes learning more data-efficient.

**How it would work in the brain (if true).**
1. Each synapse holds a mean strength and an estimate of its own uncertainty.
2. Local signals (pre- and postsynaptic activity, error or modulator) arrive.
3. The weight changes in proportion to its uncertainty: unsure synapses change more.
4. With each update, uncertainty shrinks; with little recent input, it may grow again.
5. The source argues that synaptic variability (noisy release) could be a way of sampling
   from this uncertainty.

**How to test it here.**
Inside the standard test loop:
1. Use the **Tiny MLP** or a small linear classifier in numpy.
2. Bayesian-synapse version: each weight has a variance that sets its own learning rate
   (for example a diagonal Kalman-filter-like update).
3. Baseline: plain SGD with a tuned learning rate.
4. Metric: test accuracy as a function of the number of training examples (a data
   efficiency curve); at least 5 seeds.
5. Extra: a task with a switch, to see if uncertainty helps relearning.

**Counts against it if:** the Bayesian-synapse net shows no gain in data efficiency over
plain SGD.

**Why it matters for a brain-like learner.** Per-synapse learning rates could protect
well-learned skills while letting new ones form fast. It is a local cousin of H025 and
H035, and links to forgetting in section F.

## H037 - Acetylcholine switches encode and retrieve
**Status:** open · **Tier:** T1 · **Source:** Hasselmo 2006, *Curr Opin Neurobiol*

**In simple words.** The hippocampus both stores new memories (**encoding**) and recalls
old ones (**retrieval**). If it did both at once, recall of old memories would leak into
new ones and blur them (**interference**). This row says acetylcholine works as a switch.
High ACh means "write mode": strengthen new input and quiet recall. Low ACh means "read
mode": recall freely and pass memories on. It is like a recorder that switches off the
playback speaker while it records.

**How it would work in the brain (if true).**
1. ACh levels are high during active waking and lower during quiet rest and slow-wave
   sleep (established, as a broad pattern).
2. High ACh: input from entorhinal cortex dominates, recurrent connections in CA3 and the
   path from CA3 to CA1 are suppressed, and plasticity is boosted.
3. So new patterns are stored without being pulled towards old ones.
4. Low ACh: recurrent connections are strong again, and stored patterns complete from
   partial cues.
5. Retrieval (and replay to cortex) happens mostly in low-ACh states.

**How to test it here.**
Inside the standard test loop:
1. Build a small numpy associative memory (Hopfield-style recurrent network).
2. Store a sequence of overlapping patterns.
3. Model with ACh switch: recurrent input scaled down and learning up during storage;
   recurrent input up and learning off during recall.
4. Baseline: same network with no switch (recall and learning always on).
5. Metric: recall accuracy of all stored patterns and amount of blending between them; at
   least 5 seeds.

**Counts against it if:** the model with an ACh switch shows no less interference than
the one without.

**Why it matters for a brain-like learner.** A simple mode switch could reduce memory
interference without extra memory. It links to H025 (another ACh role) and section F. See
[memory-systems](../../function/memory-systems.md).

## H038 - A lifetime schedule of neuromodulators
**Status:** open · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** Young children explore a lot. Adults mostly use what they already
know (**exploitation**). This row proposes that part of this shift comes from a change in
the balance of neuromodulators across a lifetime. The idea that exploration falls with age
is a common observation; the neuromodulator cause is the new claim here. The same brain
then behaves like a curious explorer early and an efficient expert later. It is like a
company that spends its early years trying many products and its later years selling the
ones that worked.

**How it would work in the brain (if true).**
1. Early in life, the neuromodulator balance favours high exploration and high plasticity.
2. The young learner samples widely and builds a broad model of the world.
3. With age the balance shifts: less exploration, slower and more selective plasticity.
4. The adult learner exploits its model and protects existing skills.
5. Surprise or big life changes could still partly reopen exploration (links to H025 and
   H035).

**How to test it here.**
Inside the standard test loop:
1. Take the **Brain World** agent (or a simple numpy bandit series) and give it a
   lifetime: a long run of different tasks.
2. Lifetime agent: exploration and learning rate start high and decrease on a fixed
   schedule.
3. Baselines: the best single constant setting, and a setting tuned per task (H026-style
   modulation).
4. Metric: total reward over the whole lifetime and performance on late tasks; at least 5
   seeds.

**Counts against it if:** the agent with a lifetime schedule shows no gain on lifelong
tasks over a constant one.

**Why it matters for a brain-like learner.** A schedule is cheap to build and might help
long-lived agents. It links to H026 (the dials), H030 (curiosity) and section E; see
[brain-development-and-critical-periods](../../function/brain-development-and-critical-periods.md).
