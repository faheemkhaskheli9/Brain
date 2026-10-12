# C. Self-supervised objectives: cortex learns a world model, explained

Part of [the 170 hypotheses, explained simply](README.md). Main table and status:
[learning-algorithm-hypotheses.md](../learning-algorithm-hypotheses.md). Every row is a
**hypothesis**, not an established fact.

## The big idea of this group
A child sees millions of images and hears endless sounds, but almost nobody tells it
what each one is. So most learning must come from the input itself, with no labels. This
is called **self-supervised learning**: the learner makes up its own exercise, such as
"guess what comes next" or "guess the hidden part", and learns from its own mistakes.
It is established that the cortex changes with experience, that much of this happens
without explicit teaching, and that sensory neurons develop tuned responses such as
edge detectors in early visual cortex (Hubel & Wiesel). What is claimed is *which
objective* drives that learning. The rows below offer several answers: predict the input
(H039, H041, H044, H054), keep only slow or sparse or non-redundant signals (H042,
H045, H046, H047), learn from agreement between senses or from one's own actions (H050,
H051), use purely local competition (H052, H053), or use specific cortical circuits
(H048, H049). H040 claims one quantity covers them all. Many of these can be true at the
same time, but they make different predictions about which features appear and how
well they transfer. Background: [predictive-processing](../../function/predictive-processing.md),
[neural-coding-and-computation](../../function/neural-coding-and-computation.md),
[sensory-systems-and-vision](../../function/sensory-systems-and-vision.md).

## H039 - Cortex learns by predicting its input
**Status:** open · **Tier:** T1 · **Source:** Rao & Ballard 1999, *Nat Neurosci*

**In simple words.** Imagine a teacher who checks homework only for mistakes. The higher
brain areas guess what the lower areas should be seeing. The lower areas send back only
the part the guess got wrong, the **prediction error**. Learning means changing
connections so that these errors get smaller. Over time the higher areas build a model
that explains the input. This is called **predictive coding** (PC).

**How it would work in the brain (if true).**
1. Light hits the retina and activity reaches primary visual cortex, V1 (established).
2. A higher area, such as V2, holds a guess about the cause of the image. It sends that
   guess down through feedback connections, which exist in cortex (established).
3. Error neurons in V1 compute "actual input minus predicted input".
4. The error goes up through feedforward connections and nudges the higher area's guess
   until the error is small.
5. Then synapses change with a local rule: each weight moves by (error below) x
   (activity above), so the next guess is better.
6. Because the higher area predicts a whole region, a V1 cell's response depends on the
   surroundings too. This would explain **extra-classical receptive field** effects:
   a neuron responds less when a line continues beyond its small "window".

**How to test it here.**
Inside the standard test loop:
1. Build a two-level numpy PC network in the style of Rao & Ballard, trained on small
   natural-image patches (for example 16x16 pixels, from a public image set).
2. Probe the trained level-1 units with bars of different lengths and with gratings
   that extend into the surround.
3. Measure end-stopping: response to a long bar divided by response to an optimal short
   bar.
4. Baseline: the same network with feedback from level 2 removed (a one-level sparse
   model). Run at least 5 seeds each.

**Counts against it if:** hierarchical PC trained on natural images produces no
extra-classical receptive field effects. (The original paper reported these effects, so
this is mainly a replication.)

**Why it matters for a brain-like learner.** If it holds, one local rule can train a
whole hierarchy without labels. It links to H001 (PC can approximate backprop) and
H054 (precision-weighted errors), and it competes with H044 (predict in embedding space,
not in pixels).

## H040 - One quantity: free energy
**Status:** open · **Tier:** T1 · **Source:** Friston 2010, *Nat Rev Neurosci*

**In simple words.** This is the most ambitious claim in the group. It says that
perception, learning and action all do one thing: lower **variational free energy**.
Free energy is a number that is roughly "how surprised the brain's model is by what it
senses", plus a cost for overly complex beliefs. You can lower surprise in two ways:
change your beliefs (perceive and learn) or change the world (act). Using action this
way is called **active inference**. Think of a thermostat that either updates its idea of
the room's temperature or turns on the heater.

**How it would work in the brain (if true).**
1. The brain holds a generative model: beliefs about hidden causes and how they produce
   sensations.
2. Sensory input arrives and is compared with predictions, as in H039.
3. Fast neural activity changes beliefs to reduce prediction error (perception).
4. Slower synaptic changes improve the model itself (learning).
5. Actions are chosen because their predicted results reduce expected free energy, which
   mixes "reach preferred states" and "gain information".
6. Neuromodulators set how much each error counts (see H054).

**How to test it here.**
Inside the standard test loop:
1. As stated, the claim is very hard to falsify, so pick one concrete active-inference
   agent with a fixed, written-down model and settings.
2. Implement it in numpy for a small Brain World task (or a grid-world version of it).
3. Baseline: a standard RL agent, such as tabular Q-learning or actor-critic, with a
   similar amount of tuning.
4. Metrics: reward, steps to learn, exploration of new states, and transfer in the
   H101 transfer setup. Run at least 5 seeds each.

**Counts against it if:** the chosen active-inference agent is worse than RL on every
metric. Note that this weakens that specific agent, not the whole principle.

**Why it matters for a brain-like learner.** If one objective really covers learning and
action, the learner needs no separate reward system. It overlaps with H039 and H054 and
is an alternative to the reward-based rows in section B.

## H041 - Predict the near future
**Status:** open · **Tier:** T1/T2 · **Source:** Singer et al. 2018, *eLife*; Lotter et al. 2017, ICLR

**In simple words.** Instead of explaining the current image, sensory cortex may be
tuned to guess the next moment, a few tens of milliseconds ahead. A tennis player does
this with the ball. Features that help predict the future are the useful ones: motion,
edges that move together, objects that persist.

**How it would work in the brain (if true).**
1. A short stretch of recent input, such as the last few video frames, drives V1 neurons.
2. Each neuron's connections are shaped so that its response helps predict the next
   input frame.
3. A downstream readout (or the next layer) compares the prediction with what actually
   arrives.
4. The mismatch drives synaptic change, so neurons that carried predictive information
   are strengthened.
5. After development, V1 receptive fields are those that best predict the near future,
   including their tuning to direction and speed of motion.

**How to test it here.**
Inside the standard test loop:
1. T1: train a small numpy network to predict the next frame of natural-movie patches
   from the previous few frames (Singer et al. used a model of this kind).
2. Baseline: a non-predictive model on the same data, such as a sparse-coding model or
   an autoencoder that reconstructs the current frame.
3. T2: compare receptive fields of both models with open V1 recordings, for example
   tuning to orientation, spatial frequency and motion direction, from public datasets
   (see [measuring-the-brain-and-open-datasets](../../simulation/measuring-the-brain-and-open-datasets.md)).
4. Metric: how well each model's units predict real neuron responses on held-out
   stimuli. Run at least 5 seeds.

**Counts against it if:** the temporal-prediction model fits V1 receptive fields worse
than the non-predictive model.

**Why it matters for a brain-like learner.** "Predict the next moment" is free training
data for an agent in a moving world. It is a time-based cousin of H039 and is closely
linked to H042 (slow features) and H043 (contrastive future prediction).

## H042 - Slow signals reveal objects
**Status:** open · **Tier:** T1 · **Source:** Wiskott & Sejnowski 2002, *Neural Comput*

**In simple words.** When a cat walks across your view, the pixels change very fast but
"there is a cat" stays the same for seconds. So a good rule is: find the signals in your
input that change slowly. Those tend to be about objects, not about pixels. A feature
that does not change when the object moves is called **invariant**. The method of
finding such signals is **slow feature analysis** (SFA).

**How it would work in the brain (if true).**
1. A neuron receives many fast-changing inputs, for example from edge detectors in V1.
2. The rule prefers outputs that vary slowly over time, while staying active (they
   cannot simply go silent) and not copying each other.
3. Synapses from inputs that keep firing together while the same object is in view get
   stronger, so the output stays steady as the object moves.
4. Higher in the visual stream, units become selective to object identity across
   positions and sizes. That such invariance exists in inferotemporal cortex is
   established; that slowness causes it is the claim.

**How to test it here.**
Inside the standard test loop:
1. Make a simple stream: a few small shapes drifting across a 2D image, with random
   jumps between shapes.
2. Train a two-stage numpy SFA (expand inputs with quadratic terms, then whiten and keep
   the slowest directions).
3. Test each output unit: how much its response depends on object identity versus
   position.
4. Baseline: PCA on the same frames, which ignores time order. Run at least 5 seeds.

**Counts against it if:** SFA on the moving-object stream produces no position-invariant
units.

**Why it matters for a brain-like learner.** Slowness gives object-level features for
free, using only time. It is a simple, local alternative to H041 and H043, and it could
help the transfer tests in H101.

## H043 - Local contrastive prediction trains depth
**Status:** open · **Tier:** T1 · **Source:** Illing et al. 2021, NeurIPS

**In simple words.** **Contrastive** learning means learning by comparison: "this future
moment goes with this present; that random moment does not". Contrastive predictive
coding (CPC) usually trains a deep network end-to-end with backprop. This hypothesis says
each layer can do the comparison on its own, using only local signals, and the whole
stack still learns good features. Picture each floor of a building doing its own
spot-check, with no message from the top floor.

**How it would work in the brain (if true).**
1. A layer produces a representation of the current input.
2. A short moment later, the same layer sees the real next input. At other times it sees
   unrelated input, for example during a saccade or from a different scene.
3. A third factor, a global signal that is the same for every synapse (like a
   neuromodulator), says "true future now" or "unrelated now".
4. Each synapse changes by (presynaptic activity) x (postsynaptic activity) x (that sign),
   so matching pairs grow together and unrelated pairs are pushed apart.
5. Each layer does this alone. No error passes back from higher layers.

**How to test it here.**
Inside the standard test loop:
1. Build a 3-4 layer numpy network on short sequences, such as moving digits or small
   audio-like signals.
2. Train it with a layer-local contrastive loss (each layer has its own predictor and
   loss).
3. Baseline: the same architecture trained with end-to-end CPC using backprop.
4. Freeze each network and train a linear classifier (a **linear probe**) on top to read
   out the label. Compare accuracy. Run at least 5 seeds.

**Counts against it if:** local CPC shows a large gap to backprop CPC on the linear probe.

**Why it matters for a brain-like learner.** It would give deep self-supervised learning
with no backward pass. It links to H041 and to the credit-assignment rows in section A,
such as H001.

## H044 - Predict in abstract space, not pixels
**Status:** open · **Tier:** T1 · **Source:** LeCun 2022, OpenReview position paper

**In simple words.** Predicting every pixel of the next frame is wasteful: leaves move
at random, and nobody needs to predict each one. A **joint-embedding predictive
architecture** (JEPA) first turns both the present and the future into a compact summary,
an **embedding**. It then predicts the summary of the future from the summary of the
present. It is like predicting "the ball will land near the net" instead of painting the
whole next scene.

**How it would work in the brain (if true).**
1. Two encoder pathways turn the current input and the coming input into embeddings.
2. A predictor circuit maps the current embedding to a guess of the future embedding.
3. The error is computed between embeddings, not between raw sensory signals.
4. Learning changes the predictor and the encoders to reduce this error.
5. A mechanism stops collapse, the trivial solution where every input maps to the same
   embedding. Examples are keeping units decorrelated or using a slowly updated copy of
   the encoder.

**How to test it here.**
Inside the standard test loop:
1. Build a small JEPA-like model in numpy with local updates (each module trains on its
   own error, plus a decorrelation term against collapse).
2. Baseline: a model of the same size that predicts the next observation in pixel space.
3. Train both on Brain World observation streams from some layouts.
4. Use the H101 transfer setup: freeze the encoders, train a small policy or probe on new
   layouts, and compare transfer. Run at least 5 seeds.

**Counts against it if:** the JEPA-like local model transfers no better than pixel
prediction.

**Why it matters for a brain-like learner.** It decides where the error neurons should
compare things: at the sensor or at a higher level. It competes with pixel-level
predictive coding (H039, H041) and links to H101.

## H045 - A sparse code of independent causes
**Status:** open · **Tier:** T1 · **Source:** Olshausen & Field 1996, *Nature*

**In simple words.** At any moment only a few neurons in a group are strongly active,
and each one stands for one cause in the world, like "an edge here at this angle". This
is a **sparse code**. It is like describing a room with a few words ("chair, lamp,
window") instead of listing every colour. Olshausen & Field showed that asking for a
sparse code of natural images produces edge-like features similar to V1 simple cells.

**How it would work in the brain (if true).**
1. An image patch drives a group of neurons.
2. The neurons compete, through inhibition, until only a few stay active, and those few
   together explain the input well.
3. The leftover error, input minus reconstruction, is available locally.
4. Each active neuron's input weights move toward the part of the error it can explain.
5. Over many images the weights become a dictionary of common causes, such as oriented
   edges. That V1 has edge-like receptive fields is established; that sparsity is the
   reason is the claim.

**How to test it here.**
Inside the standard test loop:
1. Implement numpy sparse coding (for example with iterative soft thresholding) on
   small patches of Brain World observations.
2. Train on some layouts only.
3. Test reuse: on new layouts, check how well the learned dictionary reconstructs new
   observations, and whether a small policy built on the sparse code learns faster
   (H101 transfer setup).
4. Baseline: PCA features or random features of the same size. Run at least 5 seeds.

**Counts against it if:** sparse coding on Brain World observations finds features that
are not reused across layouts.

**Why it matters for a brain-like learner.** Sparse codes are cheap in energy and easy to
learn with local rules. The row is close to H046 (remove redundancy) and is used by H053.

## H046 - Learning removes redundancy
**Status:** open · **Tier:** T1 · **Source:** Barlow 1961 (*Sensory Communication*); Bell & Sejnowski 1995, *Neural Comput*

**In simple words.** Neighbouring pixels in an image are almost always similar, so
sending both is wasteful. Barlow proposed that sensory neurons learn to remove this
repetition, so that each one carries information the others do not. Bell & Sejnowski
turned this into an algorithm: maximise the information passed through the network
(**infomax**). This turns out to be the same as **independent component analysis** (ICA),
which separates mixed signals, like picking out one voice at a party.

**How it would work in the brain (if true).**
1. Correlated inputs arrive, for example neighbouring pixels.
2. Each neuron's output passes through a saturating curve, since firing rates have
   limits (established).
3. Synapses change so that the outputs carry as much information as possible about the
   input. In practice this pushes outputs to become statistically independent.
4. Neurons that respond to the same thing get pushed apart, so their codes do not
   overlap.
5. On natural images the result is edge-like filters, similar to H045.

**How to test it here.**
Inside the standard test loop:
1. Learn features from small patches of Brain World observations (or natural images)
   with numpy infomax or ICA.
2. Baseline: PCA features with the same number of units. PCA removes only pairwise
   correlation, not full redundancy.
3. Train the same small downstream learner (a linear classifier or a simple policy) on
   each feature set.
4. Metric: samples needed to reach a fixed accuracy or reward, plus final score. Run at
   least 5 seeds.

**Counts against it if:** infomax or ICA features give no better downstream learning than
PCA.

**Why it matters for a brain-like learner.** If redundancy reduction helps later
learning, early sensory layers can be trained without any task. It overlaps strongly
with H045 and gives a different reason (information, not sparseness) for similar
features.

## H047 - Hebbian rules from similarity matching
**Status:** open · **Tier:** T1 · **Source:** Pehlevan, Hu & Chklovskii 2015, *Neural Comput*

**In simple words.** A **Hebbian** rule strengthens a synapse when the two cells fire
together ("cells that fire together wire together"). An **anti-Hebbian** rule weakens
it, which makes neurons push each other apart. This hypothesis says these two rules are
not just a lucky guess. They follow from one clear goal: if two inputs are similar, the
outputs should be similar too. That goal is called **similarity matching**. It is like
drawing a map where cities that are close stay close.

**How it would work in the brain (if true).**
1. Inputs arrive at a layer through feedforward synapses.
2. Output neurons are linked to each other by lateral (sideways) inhibitory synapses.
3. Feedforward synapses follow a Hebbian rule, so outputs track the main patterns in the
   input.
4. Lateral synapses follow an anti-Hebbian rule, so outputs do not all learn the same
   pattern.
5. The network settles into outputs that keep the similarity structure of the input.
   Mathematically, it finds the **principal subspace**, the few directions along which
   the input varies most. All updates are local.

**How to test it here.**
Inside the standard test loop:
1. Generate synthetic data with a known low-dimensional structure plus noise (for example
   5 strong directions in 50 dimensions).
2. Implement the derived Hebbian/anti-Hebbian network in numpy, with one sample at a
   time (online).
3. Metric: angle between the learned subspace and the true principal subspace, measured
   over training.
4. Baseline: Oja's rule (Oja 1982) and batch PCA. Run at least 5 seeds.

**Counts against it if:** the derived network fails to find the principal subspace
online.

**Why it matters for a brain-like learner.** It gives a principled reason for the local
rules that are known to exist, and a way to design new local rules from goals. It is a
building block for H045, H046 and H052.

## H048 - Thousand brains: columns vote
**Status:** open · **Tier:** T1 · **Source:** Hawkins et al. 2019, *Front Neural Circuits*

**In simple words.** The cortex is made of many repeated small units called **cortical
columns**. This hypothesis says each column learns complete models of objects, not just
small pieces, using its own **reference frame**: a map of where features sit on the
object. Columns then vote to agree on what the object is. Think of several blindfolded
people each touching a different part of an elephant and talking until they agree.

**How it would work in the brain (if true).**
1. One column receives input from a small patch of skin or retina (established: columns
   have local inputs).
2. It also gets a location signal, "where this sensor is relative to the object",
   possibly from grid-cell-like circuits in the column.
3. The column stores pairs of (feature, location) for each object it has learned.
4. Each touch narrows the column's list of objects that fit.
5. Columns share their lists through long-range lateral connections and settle on the
   object most columns agree on.
6. Learning adds new (feature, location) pairs with local, Hebbian-like changes.

**How to test it here.**
Inside the standard test loop:
1. Build a toy world of simple 3D or 2D objects, each made of features at locations, that
   can be "touched" one point at a time.
2. Implement N small column models in numpy, each with its own sensor patch and
   location input, plus a voting step.
3. Baseline: one big model with the same total parameters that sees all sensor inputs.
4. Metric: touches needed to recognise an object, and accuracy with noise. Run at least
   5 seeds.

**Counts against it if:** the column-voting model shows no gain over one big model on
object recognition from touches.

**Why it matters for a brain-like learner.** It would favour many small, repeated
modules over one deep stack. It links to H049 (same group's neuron model) and to
grid-cell rows in section D.

## H049 - Dendrites predict sequences (HTM)
**Status:** open · **Tier:** T1 · **Source:** Hawkins & Ahmad 2016, *Front Neural Circuits*

**In simple words.** A pyramidal neuron has a long tree of input branches, the
**dendrites**. Some far-off (**distal**) branches can produce a local electrical spike
when enough nearby synapses fire together (established, see
[dendritic-computation](../../anatomy/dendritic-computation.md)). This hypothesis,
called **hierarchical temporal memory** (HTM), says such a spike does not make the cell
fire. It only "primes" it: the cell enters a **predicted state**. If the expected input
then arrives, the primed cell fires first and silences its neighbours. Like an actor who
hears their cue and gets ready to speak.

**How it would work in the brain (if true).**
1. At time t, some cells in a layer are active.
2. Distal segments on other cells recognise that pattern and depolarise those cells.
   They are now "predicted".
3. At time t+1, feedforward input arrives to a column of cells.
4. If a predicted cell is in that column, only it fires. If none was predicted, all
   cells in the column fire ("burst"), which signals surprise.
5. Synapses on segments that made a correct prediction get stronger. Wrong predictions
   weaken them. New segments grow to learn new transitions.

**How to test it here.**
Inside the standard test loop:
1. Generate noisy symbol sequences with shared sub-sequences (for example A-B-C-D and
   X-B-C-Y), so the model must use context.
2. Implement a minimal HTM-style sequence memory in numpy.
3. Baseline: a numpy LSTM (trained with backprop through time) with the same number of
   parameters.
4. Metric: next-symbol accuracy under input noise, and after sequences change. Run at
   least 5 seeds.

**Counts against it if:** the sequence-memory model is worse than an LSTM with equal
parameters on noisy sequences.

**Why it matters for a brain-like learner.** It gives a concrete use for dendrites and a
fully local way to learn sequences. It links to H048 and to dendrite rows in section H.

## H050 - Learning from one's own movements
**Status:** open · **Tier:** T1 · **Source:** O'Regan & Noë 2001, *Behav Brain Sci*

**In simple words.** Seeing is not just receiving pictures. It is knowing how the
picture will change when you move: turn your head and the scene shifts left; walk
forward and things grow. These rules are called **sensorimotor contingencies**. The
hypothesis says the brain learns mainly from these "if I do this, I sense that" links.
A classic picture: a kitten that walks around learns to see better than a kitten carried
along the same path.

**How it would work in the brain (if true).**
1. The motor system sends a command, and a copy of it (an **efference copy**) goes to
   sensory areas. Efference copies are established.
2. Sensory areas predict how input will change because of that movement.
3. The actual change arrives and is compared with the prediction.
4. Errors update a model that links actions to sensory changes.
5. Representations become organised by what you can do with things, not only by how
   they look.

**How to test it here.**
Inside the standard test loop:
1. In Brain World, let an active agent choose its own movements while learning a
   representation (for example by predicting the next observation from current
   observation and action).
2. Record its exact frame sequence. Train a passive learner on the same frames, with no
   access to the actions (a "yoked" control).
3. Compare the two representations: linear probes for position and object identity, and
   transfer in the H101 transfer setup.
4. Run at least 5 seeds per condition.

**Counts against it if:** the active and passive learners end up with the same
representation.

**Why it matters for a brain-like learner.** If action matters, an agent must learn while
acting, not from a fixed dataset. It links to H040 (action to reduce surprise) and H041.

## H051 - Two senses teach each other
**Status:** open · **Tier:** T1 · **Source:** de Sa 1994, NeurIPS

**In simple words.** When a cow moos, you see the cow and hear the moo at the same time.
Neither sense needs a teacher. Each one can use the other as the "label": "whatever I
heard, my visual category should agree with it". Agreement across senses (called
**modalities**) stands in for labels.

**How it would work in the brain (if true).**
1. A visual area and an auditory area each form their own guess of a category.
2. Each guess is sent to the other area, for example through multisensory regions.
   That such convergence exists in the brain is established.
3. Each area adjusts its synapses to move its guess toward the other area's guess.
4. Errors from the two senses are partly independent, so each sense can fix the other's
   mistakes.
5. Over time both areas form categories that match real objects, with no external labels.

**How to test it here.**
Inside the standard test loop:
1. Make synthetic data: hidden classes, each producing a "visual" vector and an
   "audio" vector with independent noise.
2. Implement de Sa's minimising-disagreement scheme in numpy: two networks, each trained
   to agree with the other.
3. Baseline: a single-modality clusterer (for example k-means or a competitive network)
   on one sense alone.
4. Metric: agreement between learned categories and true classes, as label noise
   rises. Run at least 5 seeds.

**Counts against it if:** two-modality self-supervision is no better than one modality.

**Why it matters for a brain-like learner.** It gives an agent with several senses a
free teaching signal. It is the cross-sense version of the contrastive idea in H043.

## H052 - Hebbian plus lateral inhibition is enough
**Status:** open · **Tier:** T1 · **Source:** Krotov & Hopfield 2019, *PNAS*; Journé et al. 2023, ICLR (SoftHebb)

**In simple words.** This is the strongest "no teacher" claim. It says you do not need
any feedback signal from higher layers at all. Each layer uses Hebbian learning, plus
**lateral inhibition**, where neighbours compete so only the best-matching units learn.
Stack such layers and you get good deep features. SoftHebb is a version where the
competition is soft (a **softmax**: the strongest unit wins most, others a little).

**How it would work in the brain (if true).**
1. An input pattern reaches a layer.
2. Inhibitory interneurons create competition among the layer's excitatory cells. That
   such inhibition exists is established.
3. The cells that respond most strongly fire most.
4. Their incoming synapses move toward the current input (Hebbian), with a term that
   keeps weights bounded.
5. The output then drives the next layer, which learns the same way. No signal flows
   down.

**How to test it here.**
Inside the standard test loop:
1. Implement SoftHebb layers in numpy (small convolutional or patch-based layers).
2. Train networks of depth 1, 2, 3 and 4 on CIFAR-10 (or a smaller subset to stay
   numpy-friendly) with no labels, then train only a linear classifier on top.
3. Baseline: the same architectures trained end-to-end with backprop.
4. Plot the accuracy gap against depth. Run at least 5 seeds per depth.

**Counts against it if:** the gap between SoftHebb and backprop on CIFAR-10 does not
close as depth grows.

**Why it matters for a brain-like learner.** If it holds, deep features need no credit
assignment at all, which would make much of section A unnecessary for perception. It
competes with H001-type rows and is the rate-based cousin of H053.

## H053 - Spiking STDP learns prototypes
**Status:** open · **Tier:** T1 · **Source:** Diehl & Cook 2015, *Front Comput Neurosci*

**In simple words.** **STDP** (spike-timing-dependent plasticity) strengthens a synapse
when the input spike comes just before the output spike, and weakens it in the other
order (established). Add **winner-take-all** (one neuron fires and blocks the rest) and
**homeostasis** (a neuron that fires too much becomes harder to excite, so no single
neuron hogs everything). Diehl & Cook showed that such a spiking network learns
"prototype" digits from MNIST without labels. The open question is whether this works
beyond MNIST.

**How it would work in the brain (if true).**
1. Input is turned into spike trains, with brighter pixels firing more.
2. Excitatory neurons receive these spikes and race to fire first.
3. The first to fire triggers inhibition that silences the others (winner-take-all).
4. STDP pulls the winner's synapses toward the current input, so it becomes a prototype
   of that pattern.
5. The winner's threshold rises a little, so other neurons get a turn on other patterns
   (homeostasis; that neurons adjust their own excitability is established).

**How to test it here.**
Inside the standard test loop:
1. Re-implement a small Diehl & Cook style network in numpy (spiking, leaky
   integrate-and-fire neurons).
2. Check it reproduces the published MNIST behaviour, as a sanity test.
3. Train it on Brain World observations from some layouts.
4. Use the H101 transfer setup: freeze the prototypes, train a small readout on new
   layouts, and compare with random prototypes and k-means prototypes. Run at least 5
   seeds.

**Counts against it if:** prototypes learned on Brain World observations do not transfer
to new layouts. (Learning prototypes on MNIST is already shown.)

**Why it matters for a brain-like learner.** It is the most biologically detailed
unsupervised learner in this group. See
[spiking-neural-networks](../../simulation/spiking-neural-networks.md). It links to H045
(sparse prototypes) and H052.

## H054 - Errors only where attention points
**Status:** open · **Tier:** T1 · **Source:** Friston 2010; Feldman & Friston 2010, *Front Hum Neurosci*

**In simple words.** Not all prediction errors are worth learning from. Some are just
noise. **Precision** is how reliable a signal is expected to be. This hypothesis says the
brain multiplies each error by its precision, and that attention is the act of setting
precision high where it matters. So most input causes little or no learning. It is like
a student who only rewrites notes on topics the teacher said will be on the exam.

**How it would work in the brain (if true).**
1. Prediction errors are computed as in H039.
2. Each error signal is scaled by a gain (its precision). The claim is that this gain is
   set by attention and by neuromodulators such as acetylcholine.
3. Attention raises the gain of error neurons for the attended location or feature.
   That attention raises neural gain is established; that this gain is precision is the
   claim.
4. Large weighted errors drive learning; tiny weighted errors drive almost none.
5. Over time, the brain also learns which sources are reliable, and updates precision.

**How to test it here.**
Inside the standard test loop:
1. Build a numpy PC network on inputs where some parts carry signal and other parts are
   pure noise (for example half the input dimensions random).
2. Version A: errors weighted by learned precision (inverse of the learned error
   variance per unit). Version B: unweighted PC.
3. Metric: number of samples needed to reach a fixed reconstruction or downstream
   accuracy on the signal part.
4. Run at least 5 seeds each.

**Counts against it if:** precision-weighted PC gives no saving in samples compared with
unweighted PC.

**Why it matters for a brain-like learner.** It would make learning efficient by
ignoring most input. It extends H039 and H040 and links to attention rows in section J.
