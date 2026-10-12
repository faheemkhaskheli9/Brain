# A. Credit assignment: local approximations of backprop, explained

Part of [the 170 hypotheses, explained simply](README.md). Main table and status:
[learning-algorithm-hypotheses.md](../learning-algorithm-hypotheses.md). Every row is a
**hypothesis**, not an established fact.

## The big idea of this group

When a network with many layers makes a mistake, someone has to decide which of its
millions of connections were to blame and by how much. This is the **credit assignment
problem**. Deep learning solves it with **backpropagation** ("backprop"): the error at the
output is sent backwards through the same connections, layer by layer, to give every weight
its exact share of the blame. That share is called the **gradient**: the direction and size
of the change that would reduce the error fastest. It is established that backprop works
very well in machines, and also that a literal copy of it is hard for a brain: a synapse
only "sees" its own two neurons, and backprop needs the backward path to use the same
weights as the forward path (the **weight transport** problem; see
[brain-vs-deep-learning](../../learning/brain-vs-deep-learning.md)). The rows below each
claim a way the brain could get backprop-like learning using only **local** information
(what a synapse can see) plus signals that are broadcast or sent back by feedback
connections. Some rows describe the *signal* (H001, H004, H005, H019: errors living in
dendrites or bursts), some describe the *timing* (H006, H007, H012, H013, H020: two phases
compared), and some describe the *feedback path* (H002, H003, H008, H009, H018). H010,
H011, H014 and H016 drop exact gradients altogether. They overlap and often compete; the
brain may use more than one.

## H001 - Predictive coding approximates backprop
**Status:** open · **Tier:** T1 · **Source:** Whittington & Bogacz 2017, *Neural Comput*

**In simple words.** In a **predictive coding** network, each layer tries to predict the
activity of the layer below. The difference between the prediction and what really
happens is a local **error**, kept by special error units next to each layer. The network
lets activities settle until those errors balance out. The claim is that after this
settling, each weight change computed from its local error ends up almost the same as the
backprop gradient. It is like a team where each person only fixes the mismatch with their
neighbour, yet the whole chain ends up as if a manager had told everyone exactly what to fix.

**How it would work in the brain (if true).**
1. A sensory input drives the lowest layer; higher layers send predictions down
   (cortex has dense top-down connections: established).
2. Error neurons in each area compute "actual minus predicted" activity.
3. When the network sees the correct label, the top layer is held to it, and errors
   spread downward as activity relaxes.
4. Activities settle to an equilibrium where errors in neighbouring layers balance.
5. Each synapse changes by (presynaptic activity) x (postsynaptic error): a local,
   Hebbian-like product.
6. At equilibrium these local changes approximately equal backprop's gradients.

**How to test it here.** Inside the standard test loop:
1. Build the **Tiny MLP** twice: once trained by backprop, once as a predictive coding
   net with error units and a relaxation loop.
2. From the same weights and the same input, compute the PC weight update and the
   backprop gradient.
3. Measure **cosine similarity** (a score from -1 to 1 for how closely two arrows point
   the same way) per layer, as a function of relaxation steps.
4. Also train both to completion and compare final accuracy and learning curves.
5. Repeat for 5+ seeds and for a few settling step sizes.

**Counts against it if:** the cosine similarity between PC updates and backprop gradients
stays low even after the network has settled.

**Why it matters for a brain-like learner.** If true, a learner can get near-backprop
quality from local rules at the cost of extra settling time. It links to H005 and H019
(errors held in dendrites instead of separate error neurons) and competes with H090 (no
special algorithm, only scale).

## H002 - Random feedback weights are enough
**Status:** open · **Tier:** T1 · **Source:** Lillicrap et al. 2016, *Nat Commun*

**In simple words.** Backprop sends errors back through a copy of the forward weights,
which a brain probably cannot do. **Feedback alignment** (FA) says: send errors back
through fixed, *random* weights instead. Surprisingly, the forward weights then slowly
change so that they "agree" with the random feedback, and the error signals become useful.
It is like getting directions from a guide who speaks a different dialect: at first the
hints are odd, but you learn to read them, and the guide's hints end up pointing roughly
the right way.

**How it would work in the brain (if true).**
1. A stimulus passes forward through several cortical areas.
2. An error forms at the output (for example, in a motor or decision area).
3. The error travels back along separate feedback axons whose strengths are fixed and
   unrelated to the forward synapses (separate forward and feedback pathways exist:
   established).
4. Each hidden neuron receives a "fake" error equal to the random feedback times the
   output error.
5. Its synapses change by input activity times this fake error.
6. Over training, forward weights drift into alignment with the feedback weights, so the
   fake error comes to point in a useful direction.

**How to test it here.** Inside the standard test loop:
1. Use the **Tiny MLP** on XOR (and a small synthetic task, or MNIST if a loader exists).
2. Train three versions: backprop, FA (random fixed feedback matrix), and a "readout only"
   network whose hidden layer is frozen.
3. Record accuracy over training and the angle between the FA update and the true gradient.
4. Check whether hidden weights actually change in useful ways (readout-only is the floor).
5. Run 5+ seeds for each.

**Counts against it if:** FA fails to learn the hidden layers, so it does no better than
training only the readout (the last layer).

**Why it matters for a brain-like learner.** If it holds, the weight transport problem
largely disappears. H003 is a cheaper variant, and H009 and H018 try to improve on random
feedback.

## H003 - Broadcast the output error to every layer
**Status:** open · **Tier:** T1 · **Source:** Nøkland 2016, NeurIPS

**In simple words.** **Direct feedback alignment** (DFA) goes one step further than H002.
Instead of passing the error back layer by layer, the output error is sent *directly* to
every hidden layer, each through its own fixed random weights. No backward chain is needed
at all. Think of a coach who shouts the same score to every player at once, with each
player hearing it through their own slightly different radio; each player still learns to
make the score better.

**How it would work in the brain (if true).**
1. A stimulus passes forward through the hierarchy.
2. An error signal forms at the output stage.
3. That error is sent out along long-range projections that reach many layers at once,
   each with fixed random strengths.
4. Each hidden neuron combines the error it receives with its own activity.
5. Its incoming synapses change by input activity times this local error.
6. Forward weights align with the random broadcast, so learning becomes useful in every
   layer at the same time.

**How to test it here.** Inside the standard test loop:
1. Build a 3-layer MLP (two hidden layers) on a small task.
2. Train with backprop, with DFA, and with readout-only (hidden layers frozen).
3. Compare test accuracy and learning speed; also compare with FA (H002).
4. Measure how much the hidden representations change from initialisation (for example,
   how well a linear readout of each hidden layer can decode the classes).
5. Run 5+ seeds.

**Counts against it if:** DFA on a 3-layer MLP is no better than training only the readout.

**Why it matters for a brain-like learner.** DFA lets all layers learn in parallel with
one broadcast signal, which fits a brain with diffuse projections. It is close to the
three-factor rules in section B (one global signal, local eligibility), and simpler than
H002.

## H004 - Bursts carry the error, single spikes carry the signal
**Status:** open · **Tier:** T1/T3 · **Source:** Payeur et al. 2021, *Nat Neurosci*

**In simple words.** A pyramidal neuron (the main excitatory neuron of cortex) can fire
single spikes or **bursts** (several spikes very close together). The claim is that the
neuron sends two messages at once: the overall *rate of events* (a single spike or a burst
both count as one event) carries the normal feedforward signal, and the *fraction of
events that are bursts* carries the error. It is like a light that blinks to send one
message, while the colour of each blink sends a second message.

**How it would work in the brain (if true).**
1. Bottom-up input reaches the basal dendrites near the cell body and sets the event rate.
2. Top-down feedback reaches the apical dendrite in the upper layers of cortex
   (this layout is established).
3. When apical input coincides with somatic spikes, the cell tends to fire a burst
   (coupling between apical input and bursting: established).
4. Downstream cells read the event rate as the signal; cells upstream receive burst
   probability back through feedback synapses that respond differently to bursts.
5. A synapse strengthens if bursts are above their running average and weakens if below,
   in proportion to presynaptic activity.
6. This burst-dependent rule pushes each layer in a direction similar to the gradient.

**How to test it here.**
Inside the standard test loop:
1. T1: build a small spiking network (two-compartment neurons: soma + apical dendrite)
   with event and burst outputs.
2. Implement the burst-dependent plasticity rule and train it on XOR.
3. Compare with a rate network trained by backprop on XOR, and with readout-only training.
4. Check whether burst probability in hidden units tracks the backprop error for those units.
5. T3: a lab would need to record bursts and plasticity in identified pyramidal neurons
   during learning and show that changing burst fraction (not rate) changes what is learned.

**Counts against it if:** a spiking net with the burst-dependent rule cannot solve XOR.

**Why it matters for a brain-like learner.** If neurons can multiplex, one population can
carry both inference and learning signals without separate error neurons (contrast H001).
It links to H005 and H019, which also put the error in the apical dendrite.

## H005 - Apical dendrites hold the error
**Status:** open · **Tier:** T1 · **Source:** Sacramento et al. 2018, NeurIPS; Urbanczik & Senn 2014, *Neuron*

**In simple words.** A pyramidal neuron has two main input zones: the basal dendrites,
near the cell body, which get bottom-up input, and the long **apical dendrite**, which
reaches up and gets top-down input. The claim is that the apical dendrite compares what
higher areas "expect" with what the cell is actually doing. The mismatch becomes the
error that guides learning. Local inhibitory cells (interneurons) learn to cancel the
expected part, so only the surprise is left.

**How it would work in the brain (if true).**
1. Bottom-up input drives the basal dendrites and the cell body (established anatomy).
2. Top-down predictions from higher areas arrive at the apical dendrite (established anatomy).
3. Local interneurons learn to cancel the predictable part of that top-down input.
4. When there is a target, top-down input is nudged; the leftover apical voltage is now
   an error.
5. Basal synapses change to make somatic activity match what the dendrite predicts, using
   the leftover apical signal.
6. With the microcircuit in place, these local changes approximate backprop's updates.

**How to test it here.** Inside the standard test loop:
1. Build a small rate-based "dendritic microcircuit": pyramidal units with basal and
   apical compartments plus interneurons, 2 hidden layers, a few dozen units each.
2. First train the interneurons so apical voltage is near zero without a target.
3. Train on a small task (a nonlinear regression or the **Tiny MLP** task).
4. Compare each update with the backprop gradient (cosine similarity) and compare final
   accuracy with backprop.
5. Run 5+ seeds.

**Counts against it if:** the updates of the dendritic microcircuit model do not track
backprop.

**Why it matters for a brain-like learner.** If true, a neuron with two compartments can
compute its own error, which tells you to model dendrites rather than point neurons. It is
a close relative of H004 and H019 and an alternative to separate error units (H001).

## H006 - Equilibrium propagation: free phase, then nudged phase
**Status:** open · **Tier:** T1 · **Source:** Scellier & Bengio 2017, *Front Comput Neurosci*

**In simple words.** Picture the network as a landscape where activity rolls downhill and
settles in a valley; the height of this landscape is called the **energy**. In
**equilibrium propagation** (EqProp), the network first settles freely on an input (free
phase). Then the output is gently pulled toward the right answer, and the network settles
again (nudged phase). Each synapse compares how correlated its two neurons were in the two
phases and changes by the difference. That difference turns out to approximate the gradient.

**How it would work in the brain (if true).**
1. A stimulus arrives and recurrent cortical circuits settle into a stable activity
   pattern (the free phase).
2. Each synapse keeps a short-lived memory of how active its two neurons were together.
3. Feedback (a teacher, an outcome, or a higher area) gently nudges the output neurons
   toward a target.
4. Recurrent connections spread this nudge, and the network settles into a slightly
   different pattern.
5. Each synapse changes by (co-activity in nudged phase) minus (co-activity in free phase).
6. For small nudges and symmetric connections, this matches the gradient.

**How to test it here.** Inside the standard test loop:
1. Build a small energy-based network (a Hopfield-like net with one hidden layer, a few
   dozen units) in numpy.
2. Train with EqProp on XOR and a small classification task.
3. Train a feedforward net of similar size with backprop as the baseline.
4. Record accuracy, number of settling steps, and the effect of nudge strength.
5. Run 5+ seeds and report where EqProp fails or succeeds.

**Counts against it if:** EqProp on a small energy net fails where backprop succeeds.

**Why it matters for a brain-like learner.** EqProp needs only local co-activity and two
phases, which fits recurrent cortex. It is closely related to H007 (contrastive Hebbian
learning) and needs symmetric weights, which links it to H009.

## H007 - Contrastive Hebbian learning (GeneRec)
**Status:** open · **Tier:** T1 · **Source:** O'Reilly 1996, *Neural Comput* (GeneRec)

**In simple words.** **Hebbian learning** means "neurons that fire together wire
together": a synapse grows when its two neurons are active at the same time (established).
Contrastive Hebbian learning uses this twice. First comes a "minus" phase, where the
network shows what it *expects*. Then comes a "plus" phase, where it sees what *actually*
happens. The synapse learns from the difference between the two. It is like guessing the
next word of a song, then hearing it, and adjusting only where your guess was off.

**How it would work in the brain (if true).**
1. The network gets an input and settles into its expectation (minus phase).
2. Each synapse notes the co-activity of its two neurons in this phase.
3. The real outcome then arrives (sound, sight, feedback) and the network settles again
   (plus phase).
4. Each synapse notes the new co-activity.
5. Weights change by plus-phase co-activity minus minus-phase co-activity.
6. Over many trials, expectations come to match outcomes, and hidden layers learn useful
   features.

**How to test it here.** Inside the standard test loop:
1. Build a small bidirectional (recurrent) network of rate units in numpy.
2. Implement GeneRec (minus phase, plus phase, difference rule).
3. Train on XOR and on 2-3 small tasks; train the **Tiny MLP** with backprop on the same
   tasks.
4. Compare final accuracy and learning curves.
5. Run 5+ seeds.

**Counts against it if:** GeneRec shows a large accuracy gap compared with backprop on
small tasks.

**Why it matters for a brain-like learner.** It makes "expectation then outcome" the core
of learning. H013 claims the thalamus supplies the timing for these two phases, and H006
is the modern relative.

## H008 - Target propagation
**Status:** open · **Tier:** T1 · **Source:** Lee et al. 2015, ECML-PKDD

**In simple words.** Instead of sending gradients down, each layer above sends a
**target** to the layer below: "this is the activity you should have had". The layer
then just learns to hit its target with a simple local rule. The targets are made by
feedback connections that learn to *undo* the forward pass (like an inverse). **Difference
target propagation** adds a correction for the fact that this inverse is never perfect.
It is like each manager telling the next one down the exact result they wanted, instead
of a score.

**How it would work in the brain (if true).**
1. A stimulus flows forward through the areas.
2. At the top, the output is compared with the desired output, giving a top target.
3. Feedback connections, trained to invert the layer above, turn that target into a
   target for the layer below.
4. A correction term (the inverse of the actual activity) removes errors in that inverse.
5. Each layer changes its forward synapses to move its activity toward its target.
6. Separately, feedback synapses keep learning to invert the forward pass (an
   autoencoder-like local rule).

**How to test it here.** Inside the standard test loop:
1. Build a small MLP (2-3 hidden layers) with learned inverse feedback weights.
2. Train with difference target propagation, with FA (H002), and with backprop.
3. Use MNIST if a loader is available; otherwise a small synthetic classification task.
4. Compare test accuracy and track how well feedback weights invert the forward pass.
5. Run 5+ seeds.

**Counts against it if:** difference target propagation is much worse than FA.

**Why it matters for a brain-like learner.** Targets are easier to picture in neurons
than gradients, and inverse models fit the brain's dense feedback. It competes directly
with H002 for the role of the feedback pathway.

## H009 - Feedback weights learn to mirror the forward weights
**Status:** open · **Tier:** T1 · **Source:** Akrout et al. 2019, NeurIPS

**In simple words.** Backprop needs the backward weights to match the forward ones. H002
says random feedback is enough; H009 says the brain can do better and *make* the feedback
match, using its own local rule. In the **Kolen-Pollack** method, a forward synapse and
its partner feedback synapse get the same update and both slowly decay, so they drift
together. In **weight mirrors**, neurons fire noise, and the feedback synapses learn from
the resulting correlations. Like two dancers who copy each other's mistakes until they
move in sync.

**How it would work in the brain (if true).**
1. A forward synapse from A to B and a feedback synapse from B to A exist (reciprocal
   connections between areas: established).
2. During learning, both synapses receive updates built from the same local quantities
   (A's activity and B's error).
3. Both also slowly decay toward zero (weight decay).
4. Because they get equal updates and equal decay, their difference shrinks over time.
5. In the weight mirror version, periods of noisy activity let feedback synapses
   estimate the forward weights from correlations.
6. Once they are symmetric, errors sent backwards are close to true gradients.

**How to test it here.** Inside the standard test loop:
1. Use the **Tiny MLP** and a deeper version (3-4 layers) with separate feedback matrices.
2. Train with the KP rule, with FA (fixed random feedback), and with backprop.
3. Track the angle between each feedback matrix and the transpose of its forward matrix.
4. Compare accuracy across the three methods.
5. Run 5+ seeds and a few decay rates.

**Counts against it if:** under the KP rule the angle between feedback and forward weights
does not shrink.

**Why it matters for a brain-like learner.** If true, the weight transport problem is
solved by a local rule, so methods that need symmetry (H006, H007) become plausible. It
competes with H002 (random feedback is enough) and H018 (feedback is meta-learned).

## H010 - Perturb and correlate with reward
**Status:** open · **Tier:** T1 · **Source:** Williams 1992, *Mach Learn*; Fiete & Seung 2006, *PRL*

**In simple words.** Try a small random change, see whether things got better, and keep
the change if they did. In **node perturbation** (and the related REINFORCE rule), neurons
add a little noise to their activity. If a reward signal says the result was better than
usual, the synapses that produced that noise are pushed in the same direction. No error
needs to travel backwards. It is like a cook adding a pinch of random spice and keeping it
only if the guests smile more than usual.

**How it would work in the brain (if true).**
1. A circuit produces an action (for example, a song syllable).
2. A source of variability adds noise to some neurons (in songbirds, the area LMAN drives
   song variability: established).
3. Each synapse keeps a short memory of its input times the noise in its neuron
   (an **eligibility trace**: a temporary tag saying "I was just involved").
4. A reward signal arrives, saying whether the result was better than expected.
5. Synapses change by eligibility trace times (reward minus expected reward).
6. Over many trials the circuit climbs toward better outputs.

**How to test it here.** Inside the standard test loop:
1. Implement node perturbation on small networks of rising size (for example 10, 30, 100,
   300 units) on a fixed regression task.
2. Train the same networks with backprop as the baseline.
3. Measure the number of trials needed to reach a fixed error, per size.
4. Fit how learning time grows with network size, for both methods.
5. Run 5+ seeds per size.

**Counts against it if:** learning time grows so fast with network size that the method is
useless above about 100 units.

**Why it matters for a brain-like learner.** It needs only noise plus a broadcast reward,
which the brain clearly has (section B). If it scales badly, it may still fit small
circuits (birdsong), while bigger networks need H001-H009.

## H011 - Forward-forward: two forward passes instead of a backward one
**Status:** open · **Tier:** T1 · **Source:** Hinton 2022, arXiv:2212.13345

**In simple words.** **Forward-forward** (FF) removes the backward pass completely. The
network runs twice forward: once on real data ("positive") and once on fake or scrambled
data ("negative"). Each layer has its own simple score, called **goodness** (for example,
the sum of its squared activities). Each layer learns on its own to give high goodness to
real data and low goodness to fake data. Like a guard at every door who learns, alone, to
let in real guests and keep out impostors.

**How it would work in the brain (if true).**
1. Real sensory input arrives and flows forward (positive pass).
2. Each area raises its synaptic weights so that its activity (goodness) goes up.
3. At another time (perhaps during sleep or using internally made input), negative data
   flows forward.
4. Each area lowers its weights so that its goodness goes down for this data.
5. No error is ever sent backward; each area uses only its own activity.
6. Over time, each layer learns features that tell real from fake.

**How to test it here.** Inside the standard test loop:
1. Build a 2-3 layer FF network in numpy with a goodness threshold per layer.
2. Create negative data (for example, mixed images or inputs paired with wrong labels).
3. Train on MNIST if a loader is available, or a small synthetic task.
4. Baseline: a random-feature readout (random fixed hidden layers, train only the last
   layer); also compare with backprop.
5. Run 5+ seeds and compare test accuracy.

**Counts against it if:** FF on MNIST is no better than a random-feature readout.

**Why it matters for a brain-like learner.** If it works, each layer can learn with no
feedback at all, a strong form of locality. It links to H012 (a sleep-like phase for the
negative data) and to H016 (local losses).

## H012 - Wake-sleep: two phases train two pathways
**Status:** open · **Tier:** T1 · **Source:** Hinton et al. 1995, *Science*

**In simple words.** The network has two paths: a **recognition** path (from senses up to
causes) and a **generative** path (from causes down to imagined senses). In the "wake"
phase, real input goes up, and the generative path learns to recreate it. In the "sleep"
phase, the network dreams up input with the generative path, and the recognition path
learns to recognise what was dreamed. Each phase trains the other path with a simple local
rule. It is like drawing a picture of what you saw, then later checking whether you can
name what you drew.

**How it would work in the brain (if true).**
1. Awake: sensory input travels up the hierarchy (recognition).
2. Top-down connections try to predict the lower-level activity; their synapses change to
   reduce the local mismatch.
3. Asleep: the top layers produce activity on their own and send it down (generation).
4. Bottom-up connections try to recover the top activity from the generated lower activity;
   their synapses change to reduce that mismatch.
5. Each update uses only the activities on the two sides of the synapse.
6. Over cycles, both paths improve together.

**How to test it here.** Inside the standard test loop:
1. Build a small stochastic binary network (Helmholtz machine) with 2 layers in numpy.
2. Train it with wake-sleep on toy data with known causes (for example, small bar patterns).
3. Measure how well the generative model fits the data (log-likelihood estimate, or
   reconstruction error) over training.
4. Baseline: the untrained network, and the generative model with sleep turned off.
5. Run 5+ seeds.

**Counts against it if:** after wake-sleep on toy data, the generative model does not improve.

**Why it matters for a brain-like learner.** It gives sleep a direct job in training
(link to H020 and section F). It is also one source of the "negative data" H011 needs.

## H013 - Thalamus gives the "outcome" phase every alpha cycle
**Status:** open · **Tier:** T1/T3 · **Source:** O'Reilly et al. 2021, *J Cogn Neurosci*

**In simple words.** H007 needs two phases: an expectation and an outcome. This row says
the **pulvinar**, a part of the thalamus (a relay hub in the middle of the brain), supplies
them on a fixed clock. About every 100 ms, roughly one cycle of the **alpha rhythm** (a
brain wave near 10 Hz), cortex makes a prediction of what comes next. Then the pulvinar
passes the actual input, and cortex learns from the difference. Like a quiz master asking
"what comes next?" ten times a second and then showing the answer.

**How it would work in the brain (if true).**
1. The pulvinar connects with many cortical areas in both directions (established).
2. During the first part of an alpha cycle, deep cortical layers drive the pulvinar with
   a prediction of the next input (minus phase).
3. Near the end of the cycle, strong driving input reaches the pulvinar and shows the
   actual outcome (plus phase).
4. The pulvinar broadcasts this back to the cortical areas.
5. Cortical synapses change by plus-phase minus minus-phase co-activity (as in H007).
6. Repeated every cycle, cortex learns a predictive model of its inputs without labels.

**How to test it here.** Inside the standard test loop:
1. T1: build a small model with a "cortex" layer and a "pulvinar" layer that alternates
   prediction and outcome every simulated 100 ms, trained with a GeneRec-style rule.
2. Train it to predict the next frame of simple moving sequences (or next states in a
   **Brain World** recording).
3. Compare with the same network trained without the two-phase structure (outcome only,
   or random phase timing).
4. Measure next-step prediction error and the quality of learned features.
5. T3: a lab would need to silence the pulvinar (for example with optogenetics) during
   learning and test whether predictive learning is blocked while ordinary responses remain.

**Counts against it if:** the T1 model fails to learn; T3: silencing the pulvinar does not
block predictive learning.

**Why it matters for a brain-like learner.** It gives a concrete clock for error-driven
learning and makes the learner self-supervised (link to section C). It depends on H007
being workable.

## H014 - e-prop: eligibility traces instead of backprop through time
**Status:** open · **Tier:** T1 · **Source:** Bellec et al. 2020, *Nat Commun*

**In simple words.** To learn tasks that unfold over time, machine networks use
**backprop through time** (BPTT): they store the whole history, then run the error
backwards through every past step. The brain cannot rewind like this. **e-prop** says each
synapse keeps an **eligibility trace** (a fading memory of how much it recently helped
its neuron fire), and a **learning signal** broadcast to the neurons says how things are
going right now. The synapse changes by trace times signal. Like remembering who touched
the ball recently, so when the goal comes you know who to thank.

**How it would work in the brain (if true).**
1. A recurrent network of spiking neurons processes input over seconds.
2. Each synapse updates a local eligibility trace from its pre- and postsynaptic activity
   (synaptic tags of this kind are plausible but not established as e-prop traces).
3. An error or reward signal is computed and sent to neurons through feedback weights,
   all the time.
4. Each synapse multiplies its trace by its neuron's current learning signal.
5. Weights change online, without storing the full past.
6. Traces that last long enough (for example, through slow adaptation in neurons) let
   learning bridge delays.

**How to test it here.** Inside the standard test loop:
1. Build a small recurrent network (rate or spiking, around 100 units) in numpy.
2. Task: delayed recall: show a cue, wait a delay, then report the cue.
3. Train with e-prop and with BPTT at a range of delays, from short to several seconds of
   simulated time.
4. Measure recall accuracy versus delay for both.
5. Run 5+ seeds; include neurons with adaptation as an option.

**Counts against it if:** e-prop fails, compared with BPTT, at delays longer than a few
seconds.

**Why it matters for a brain-like learner.** Almost all real behaviour unfolds in time, so
a local way to learn across time is essential. It shares the "trace times broadcast"
form with section B's three-factor rules and with H010.

## H015 - Cerebellum predicts the error ahead of time
**Status:** open · **Tier:** T1 · **Source:** Jaderberg et al. 2017, ICML; Boven et al. 2023, *Nat Commun*

**In simple words.** Normally a layer must wait for the error to come back from the end
before it can learn. **Synthetic gradients** add a small helper network that *guesses* the
error each layer will get, so the layer can update right away. The helper is corrected
later when the real error arrives. The claim is that the **cerebellum** (the "little
brain" at the back, known for timing and motor learning) plays this helper for cortex.
Like a coach who tells you right after a shot whether it will probably go in, before the
ball lands.

**How it would work in the brain (if true).**
1. Cortex computes activity for a task.
2. A copy of this activity goes to the cerebellum (cortex-pons-cerebellum pathway:
   established).
3. The cerebellum outputs a prediction of the error (gradient) cortex will receive.
4. This prediction returns to cortex through the thalamus (cerebellum-thalamus-cortex
   loop: established) and drives cortical plasticity at once.
5. When the true outcome arrives, the cerebellum is corrected by its own teaching signal
   (climbing fibres carry error-like signals to Purkinje cells: established).
6. Over time, cortex learns faster because it does not wait for delayed feedback.

**How to test it here.** Inside the standard test loop:
1. Build a recurrent "cortex" network on a task with delayed feedback (for example, a
   timing or sequence task).
2. Add a small "cerebellum" network that predicts the cortical gradient from cortical
   activity and is trained on the true gradient when it arrives.
3. Baseline: the same cortex learning only from the delayed true feedback.
4. Measure learning speed (trials to criterion) and final accuracy.
5. Run 5+ seeds.

**Counts against it if:** the cortex + cerebellar critic model shows no speed-up over
cortex alone.

**Why it matters for a brain-like learner.** It gives the cerebellum a general role in
fast learning across many tasks, not only motor control. It is compatible with most other
rows, since it only changes *when* the error is available.

## H016 - Each layer has its own local loss
**Status:** open · **Tier:** T1 · **Source:** Nøkland & Eidnes 2019, ICML

**In simple words.** Instead of one global error at the end, each layer gets its own small
goal and learns only from that. For example, a layer can be trained so that a quick
readout from it already predicts the label, or so that inputs from the same class produce
similar activity. No error ever travels between layers. It is like a relay race where each
runner is coached only on their own leg, not on the final time.

**How it would work in the brain (if true).**
1. Each cortical area receives input from below.
2. A local circuit within or next to the area computes a goal for it (for example,
   "group similar things together" or "predict a coarse label").
3. The area compares its activity with this local goal.
4. Synapses in the area change to reduce the local loss, using only local signals.
5. Higher areas learn on top of whatever the lower areas provide, without sending
   errors down.

**How to test it here.** Inside the standard test loop:
1. Build a 3-4 layer MLP; give each layer its own small loss (a local linear classifier,
   or a similarity-matching loss).
2. Train it with local losses only, and the same net end-to-end with backprop.
3. Use a structured task where later layers must combine earlier features (for example,
   a compositional synthetic task), not only a flat one.
4. Compare test accuracy and transfer (optionally on the **H101 transfer setup**).
5. Run 5+ seeds.

**Counts against it if:** the local-loss net shows a large gap to end-to-end training on
structured tasks.

**Why it matters for a brain-like learner.** If it holds, areas can learn in parallel and
independently, which is simpler to build. It links to H011 (also layer-local) and is a
natural way to test whether credit really needs to cross layers.

## H017 - Attention tags, dopamine updates (AGREL)
**Status:** open · **Tier:** T1 · **Source:** Roelfsema & van Ooyen 2005, *Neural Comput*; Roelfsema & Holtmaat 2018, *Nat Rev Neurosci*

**In simple words.** When you choose an action, attention flows back from that choice to
the neurons that helped cause it and "tags" their synapses. Then a reward signal
(**dopamine**) arrives: better than expected makes the tagged synapses stronger, worse
makes them weaker. Untagged synapses are left alone. Like a teacher marking with a pen
the students who answered, then giving points only to the marked ones once the answer
is checked.

**How it would work in the brain (if true).**
1. A stimulus flows forward and the network selects one action.
2. Feedback from the selected action (attention) flows back to the neurons that
   contributed to it (attention feedback to earlier visual areas is established).
3. Synapses that were active and received this feedback get a temporary tag.
4. The outcome comes; dopamine neurons signal whether reward was better or worse than
   expected (reward prediction error: established).
5. Dopamine changes only the tagged synapses, in the direction of the error.
6. Over trials this approximates backprop for the chosen output.

**How to test it here.** Inside the standard test loop:
1. Build the **Tiny MLP** (or a slightly larger net) with an action-selection output.
2. Implement AGREL: feedback from the chosen output unit, synaptic tags, and a scalar
   reward prediction error.
3. Train on a small classification task given as trial-and-error (reward only when right).
4. Compare learning speed (trials to criterion) and final accuracy with backprop trained
   on the same task.
5. Run 5+ seeds.

**Counts against it if:** AGREL on a classification task learns much more slowly than
backprop.

**Why it matters for a brain-like learner.** It ties credit assignment to two systems the
brain clearly has, attention and dopamine, and links section A to section B's three-factor
rules. It is like H010, but the feedback makes it much more targeted.

## H018 - The feedback pathway is learned (learning to learn)
**Status:** open · **Tier:** T1 · **Source:** Lindsey & Litwin-Kumar 2020, NeurIPS

**In simple words.** Rows H002-H009 fix, in advance, how errors are sent back. H018 says
the feedback pathway itself is trained, over a slower timescale, to make the fast local
learning work well. This is **meta-learning**, or "learning to learn". An inner loop
learns tasks with local plasticity; an outer loop (in the brain, perhaps evolution or
development) tunes the feedback weights. Like a school improving how teachers give
feedback, while students keep learning in the usual way.

**How it would work in the brain (if true).**
1. Forward synapses learn with a local rule that uses whatever feedback arrives.
2. Feedback connections carry error-like signals into each layer.
3. Over many tasks (or evolution and development), feedback connections are slowly
   adjusted.
4. The adjustment favours feedback that makes the local rule learn quickly and well.
5. Once tuned, new tasks are learned quickly with fixed feedback and fast local plasticity.

**How to test it here.** Inside the standard test loop:
1. Build the **Tiny MLP** with a local learning rule driven by a feedback matrix.
2. Outer loop: optimise the feedback matrix (by backprop or by evolution, both allowed in
   the outer loop) over a family of small related tasks.
3. Test on new tasks from the same family with the feedback frozen.
4. Baseline: the same local rule with fixed random feedback (FA, H002); also backprop.
5. Measure accuracy after a fixed number of inner steps; run 5+ seeds.

**Counts against it if:** meta-learned feedback gives no gain over fixed random feedback.

**Why it matters for a brain-like learner.** If it holds, a good brain-like learner needs a
slow outer loop that shapes feedback wiring, which links to section E (innate priors) and
section J (meta-learning). It competes with H002 and H009 as the account of feedback.

## H019 - Dendrites predict somatic spikes
**Status:** open · **Tier:** T1 · **Source:** Urbanczik & Senn 2014, *Neuron*

**In simple words.** Inside one neuron, the dendrite tries to predict whether the cell body
(the **soma**) will fire. Sometimes the soma is pushed by a strong outside "teaching"
input. When it fires more or less than the dendrite predicted, that difference is an error
the dendrite can feel locally, and it changes its synapses to predict better. So one neuron
can learn to copy a teacher, using only signals inside itself.

**How it would work in the brain (if true).**
1. Many inputs arrive on the dendrite and make a dendritic voltage.
2. This voltage is the neuron's own prediction of its firing.
3. A separate input (a teacher, or top-down drive) also pushes the soma.
4. The soma fires; the dendrite senses the actual firing (spikes travel back into
   dendrites: established).
5. Each dendritic synapse changes by its input times (actual firing minus predicted firing).
6. Over time the dendrite alone can reproduce the teacher's output.

**How to test it here.** Inside the standard test loop:
1. Build a one-neuron, two-compartment model (dendrite + soma), rate or spiking.
2. Make a teacher neuron with random fixed weights on the same inputs; feed its output to
   the student's soma as teaching input.
3. Train the student's dendritic synapses with the Urbanczik-Senn rule.
4. Test with the teacher removed: how well does the student match the teacher's
   input-output map on new inputs? Compare with a simple delta-rule baseline.
5. Run 5+ seeds and a few input sizes.

**Counts against it if:** the one-neuron model cannot learn the teacher's input-output map.

**Why it matters for a brain-like learner.** It is the single-neuron building block for
H005 and related to H004, so it is the cheapest first test of the "error in the dendrite"
family.

## H020 - Backprop-like learning only happens in sleep
**Status:** open · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** Maybe the brain does not run its careful, backprop-like learning all
day. This row says that during waking it only stores experiences and marks them, and the
expensive credit assignment happens later, in slow, offline phases linked to sleep, when
memories are replayed. It is like a student who takes quick notes in class and does the
real studying at night. This idea comes from this research thread and has no published
source.

**How it would work in the brain (if true).**
1. Awake, experiences are stored quickly, for example in the hippocampus (fast episodic
   storage in hippocampus: established; see
   [memory-systems](../../function/memory-systems.md)).
2. Online plasticity in cortex is small or only local (simple tags or Hebbian changes).
3. During sleep, the hippocampus replays stored episodes (replay during sleep:
   established; see [sleep-and-memory-consolidation](../../function/sleep-and-memory-consolidation.md)).
4. Cortex runs a backprop-like rule (for example H001, H006 or H007) on the replayed
   episodes, with no new input to interfere.
5. Most of the deep credit assignment happens in these phases.

**How to test it here.** Inside the standard test loop:
1. Pick one local backprop-like rule from this section (for example H001 or H006).
2. Online version: apply the rule after every experience as it comes.
3. Sleep version: store experiences in a buffer while "awake", then apply the same rule
   in offline phases on replayed samples, with the same total number of updates.
4. Run both on the same task stream (the **Tiny MLP** task, then a **Brain World**
   sequence of skills); measure final accuracy and forgetting of earlier skills.
5. Run 5+ seeds.

**Counts against it if:** online-only and sleep-phase learning of the same rule show no
difference.

**Why it matters for a brain-like learner.** If true, a brain-like learner should separate
fast storage from slow offline learning, a design choice section F also points to. It
links to H012 (wake-sleep) and to the replay rows such as H104.
