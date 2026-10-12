# D. Structure, maps and abstraction, explained

Part of [the 170 hypotheses, explained simply](README.md). Main table and status:
[learning-algorithm-hypotheses.md](../learning-algorithm-hypotheses.md). Every row is a
**hypothesis**, not an established fact.

## The big idea of this group

People can learn a rule in one setting and use it in a very different one. A child who
learns how a family tree works can reason about a new family at once. These rows try to
explain how a brain gets that kind of **abstraction**: knowledge about structure that is
free of the surface details it was learnt from. Some background is established: the
hippocampus has place cells (O'Keefe & Dostrovsky 1971), the entorhinal cortex has grid
cells (Hafting et al. 2005), the hippocampus replays past experience during rest and sleep
(Wilson & McNaughton 1994), and the prefrontal cortex is needed for flexible rules (see
[prefrontal-cortex-and-abstraction](../../function/prefrontal-cortex-and-abstraction.md)).
What these rows claim is *how* those parts produce abstraction. Several rows are about
maps (H055-H057, H074, H076), several about the geometry of codes (H058, H059, H062, H069,
H077, H080), several about symbols and binding (H060, H061, H072, H073, H078), and several
about learning over time (H063-H065, H067, H075, H079). They often combine, and some
compete: for example H071 (simplest description) and H080 (expand, then compress) can both
be true, while H060 (vector binding) and H061 (binding by synchrony) offer rival answers
to the same problem.

## H055 - Structure and content stored separately
**Status:** open · **Tier:** T1 · **Source:** Whittington et al. 2020, *Cell* (Tolman-Eichenbaum Machine)

**In simple words.** Think of a chess board. The 8x8 grid is the *structure*. The pieces
on it are the *content*. If you know the grid, you can play with new pieces at once. This
hypothesis says the brain's memory system keeps these two apart. The entorhinal cortex
(a cortex area next to the hippocampus) holds the "grid", and sensory areas hold what you
see. The hippocampus ties the two together. Because the grid is kept apart, it can be
reused on a new problem with the same shape.

**How it would work in the brain (if true).**
1. Grid cells in medial entorhinal cortex fire at points that form a hexagonal pattern as
   an animal moves (established, Hafting et al. 2005).
2. Lateral entorhinal cortex carries sensory content: what objects are where.
3. The hippocampus combines the two. A place cell fires for "this content at this point in
   the structure" (place cells are established; this role is the claim).
4. Synapses between the structure code and hippocampus learn the rules of moving, for
   example "a step north then a step south returns you". These are shared across worlds.
5. In a new environment only the content-to-hippocampus links need new learning. The
   structure code predicts where things will be before they are seen.

**How to test it here.**
Inside the standard test loop:
1. Build a small TEM-like model in numpy: a structure module (a recurrent code updated by
   actions) and a content memory (a Hebbian associative store, meaning links strengthened
   when two units are active together).
2. Train it on several Brain World layouts that share the same graph of moves but have
   different objects.
3. Test zero-shot inference (correct answer with no training on that layout): after
   visiting A then B in a new layout, can it predict what is at a place reached by a new
   path, the first time?
4. Baseline: a single recurrent network of the same size that does not split structure
   from content.
5. Metric: prediction accuracy on first visits to new layouts, over at least 5 seeds.

**Counts against it if:** the TEM-like model in Brain World shows no zero-shot inference on
new layouts.

**Why it matters for a brain-like learner.** If true, a learner should keep a reusable
"shape of the problem" module apart from its sensory memory. This is the core mechanism
behind the transfer test in H101, and it links to H056 and H066.

## H056 - Cognitive maps for any knowledge
**Status:** open · **Tier:** T1/T2 · **Source:** Behrens et al. 2018, *Neuron*

**In simple words.** A **cognitive map** is an inner model of how things relate, like a
mental street map. We know the hippocampus builds maps of space. This hypothesis says the
same machinery maps anything with relations: who is friends with whom, which ideas are
close to which, which step comes after which. Space would then be just one example of a
general format. A brain that learns maps for space would get maps for ideas for free.

**How it would work in the brain (if true).**
1. Place and grid cells code position in space (established).
2. The same hippocampal-entorhinal circuit receives inputs that are not spatial, such as
   social rank or features of an object.
3. It learns which items follow or neighbour which, and builds a graph (a set of nodes
   joined by links).
4. Grid-like and place-like codes then form over that graph, as they do over a room.
5. Planning in ideas then reuses the same tools as planning a route: shortcuts, distances,
   and inference about links never seen.

**How to test it here.**
Inside the standard test loop:
1. Take the map model from H055 (or a successor-representation map, Stachenfeld et al.
   2017) trained on spatial layouts.
2. Build a non-spatial graph task of the same size, for example a family tree or a
   ranked list, where items are abstract symbols.
3. Compare: the same model with its structure part reused, vs a fresh model trained from
   scratch.
4. Metric: accuracy on inferring unseen relations (for example "A > B and B > C, so
   A > C?") after a fixed small number of examples. Use at least 5 seeds.
5. T2 option: look for open fMRI or neural data recorded during a non-spatial relational
   task and check for map-like codes.

**Counts against it if:** the same map model on a non-spatial graph task shows no transfer.

**Why it matters for a brain-like learner.** If maps are a general format, one module
could serve navigation, social reasoning and concepts. It builds on H055 and is tested in
people by H057.

## H057 - Grid codes for abstract concept spaces
**Status:** open · **Tier:** T2 · **Source:** Constantinescu, O'Reilly & Behrens 2016, *Science*

**In simple words.** Imagine a set of cartoon birds whose neck length and leg length can
change. Each bird is a point on a 2D "bird space". This hypothesis says that when you think
about changing a bird, your brain moves through that space with the same grid code it uses
to walk through a room. The sign of a grid code in brain scans is a **hexagonal
modulation**: the signal goes up and down six times as you turn through 360 degrees of
direction.

**How it would work in the brain (if true).**
1. In rodents, grid cells fire in a hexagonal pattern over space (established).
2. In humans, fMRI (a scan that measures blood flow linked to activity) of virtual
   navigation shows a signal that varies with direction with six-fold symmetry (reported
   in earlier human navigation studies).
3. A person learns a 2D concept space, such as bird neck and leg length.
4. When they imagine morphing a bird, entorhinal and prefrontal areas treat the change as
   a direction of movement.
5. The fMRI signal then shows the same six-fold pattern across "directions" in concept
   space.

**How to test it here.**
Inside the standard test loop:
1. Find open fMRI data from a task where people move through a 2D abstract space (T2).
2. Estimate each participant's grid orientation from half of the runs.
3. In the other half, test whether the signal is higher for directions aligned with that
   orientation (in steps of 60 degrees) than for misaligned ones.
4. Control: test 4-fold, 5-fold and 7-fold symmetries too. Only 6-fold should show an
   effect.
5. What a computer can still do: simulate grid cells over a 2D concept space, generate fake
   fMRI with noise, and check the analysis recovers a known effect.

**Counts against it if:** a reanalysis of open fMRI shows no hexagonal modulation.

**Why it matters for a brain-like learner.** It is direct human evidence for H056: that
map machinery is reused for ideas. A learner could then use one navigation module for
reasoning in feature spaces.

## H058 - Abstraction as shared geometry
**Status:** open · **Tier:** T1 · **Source:** Bernardi et al. 2020, *Cell*

**In simple words.** Picture a cloud of points, one for each situation the brain is in.
If "good vs bad outcome" always points along the same direction in that cloud, no matter
which task you are doing, then a simple reader (a **decoder**, a line that separates two
groups) learnt in one task also works in another. This hypothesis says that is what
abstraction *is*: a shape of the code, not a special symbol. The test for it is called
**cross-condition generalisation**: train the decoder in some conditions, test it in
others.

**How it would work in the brain (if true).**
1. Neurons in prefrontal cortex and hippocampus respond to many task variables at once.
2. During learning, the code for one variable (for example "context A vs context B") lines
   up along one direction in neural activity space.
3. That direction stays the same when other variables change (such as which stimulus is
   shown).
4. A downstream area that learnt to read the variable in one condition can read it in
   new conditions without retraining.
5. More abstract variables show better cross-condition generalisation.

**How to test it here.**
Inside the standard test loop:
1. Train several Brain World agents (or a small numpy agent) with different rules or
   seeds so that some transfer well (H101 transfer setup) and some do not.
2. Record hidden-layer activity across many conditions.
3. For each task variable, train a linear decoder on half the conditions and test on the
   other half. That accuracy is the cross-condition generalisation score.
4. Correlate the score with each agent's transfer to new layouts.
5. Baseline: the same correlation with a plain decoding score (train and test in the same
   conditions).

**Counts against it if:** cross-condition generalisation in trained Brain World agents
shows no link to transfer.

**Why it matters for a brain-like learner.** It gives a cheap measure of abstraction you can
read from any network. It is the geometry side of H055 and H077, and it trades off
against H059 (high-dimensional codes).

## H059 - Mixed selectivity for easy readout
**Status:** open · **Tier:** T1 · **Source:** Rigotti et al. 2013, *Nature*

**In simple words.** Some neurons respond to one thing, like "red". This is **pure
selectivity**. Others respond to combinations, like "red *and* on the left *and* in task
2". This is **mixed selectivity**. Mixing makes the code high-dimensional (it spreads the
data over many independent directions). In a high-dimensional code almost any split of
the situations can be drawn with one straight line, so a very simple learning rule can
read out whatever it needs.

**How it would work in the brain (if true).**
1. Many prefrontal neurons respond to mixtures of task variables (reported in the source
   paper's recordings).
2. These mixtures arise from random or partly random connections from many inputs.
3. The population then spans many dimensions.
4. A downstream neuron learns a readout with a simple local rule, such as a delta rule
   (change each weight by input times error).
5. Because the code is high-dimensional, that simple rule can learn hard combinations,
   such as XOR (true when exactly one of two inputs is on).

**How to test it here.**
Inside the standard test loop:
1. Build two hidden layers of the same size: one with random mixed units (random weights
   from all inputs plus a nonlinearity), one with pure units (each tied to a single
   input).
2. Fix the hidden layer, and train only a linear readout with the delta rule.
3. Tasks: XOR and a few random binary labellings of the input combinations (the Tiny MLP
   tasks).
4. Metric: readout accuracy and the dimension of the hidden code. At least 5 seeds.
5. Vary layer size to see when the gain appears.

**Counts against it if:** a random mixed layer vs a pure-selectivity layer gives no readout
gain.

**Why it matters for a brain-like learner.** It suggests a cheap trick: a fixed random
expansion layer lets simple local rules do the rest (compare
[reservoir-computing](../../simulation/reservoir-computing.md)). It pulls the other way
from H058, which favours low-dimensional shared directions; H080 says both may happen at
different times.

## H060 - Binding by vector operations
**Status:** open · **Tier:** T1 · **Source:** Plate 1995, *IEEE Trans Neural Netw*; Kanerva 2009, *Cogn Comput*

**In simple words.** To think "the dog chased the cat", the brain must keep track of who did
what. The roles ("chaser", "chased") have to be bound to fillers ("dog", "cat"). In
**hyperdimensional computing**, each idea is a long random vector. You bind a role to a
filler with a simple operation, such as circular convolution or XOR, and get a new vector.
You can add several bound pairs into one vector and later unbind to ask "who was the
chaser?". This gives symbols that combine like words in a sentence.

**How it would work in the brain (if true).**
1. Each concept is a large, roughly random activity pattern across many neurons.
2. A circuit computes a binding operation between a role pattern and a filler pattern.
3. Several bound pairs are summed into one pattern that stands for a whole structure.
4. To answer a question, the circuit applies the inverse of the role and gets a noisy copy
   of the filler.
5. A clean-up memory (an associative store of known patterns) snaps the noisy copy to the
   nearest known concept.

**How to test it here.**
Inside the standard test loop:
1. Start from the numpy setup in
   [hyperdimensional-computing](../../learning/hyperdimensional-computing.md) with fixed
   binding.
2. Replace the fixed binding with one learnt by local rules (for example Hebbian learning
   of a binding matrix from examples).
3. Train on some role-filler pairs, then test on new pairs that use known roles and known
   fillers in combinations never seen.
4. Baseline: the exact algebraic binding (an upper bound) and an unstructured associative
   memory.
5. Metric: unbinding accuracy on new pairs vs vector size. At least 5 seeds.

**Counts against it if:** HDC binding learnt by local rules cannot represent new role-filler
pairs.

**Why it matters for a brain-like learner.** It would give a learner compositional symbols
from plain vectors. It competes with H061 (binding by timing) and H078 (binding by
assemblies), and links to language rows in section G.

## H061 - Binding by synchrony
**Status:** open · **Tier:** T1/T3 · **Source:** Singer 1999, *Neuron*

**In simple words.** You see a red square and a blue circle. Some neurons code "red", some
"blue", some "square", some "circle". How does the brain know red goes with square? This
hypothesis says neurons for features of the same object fire at the same moments, in step.
Red and square fire together; blue and circle fire together, at a different moment.
Timing, not extra neurons, carries the "belongs together" label.

**How it would work in the brain (if true).**
1. Visual cortex neurons often fire in rhythm in the gamma band, around 30-80 times per
   second (gamma oscillations are established; see
   [brain-rhythms-and-oscillations](../../function/brain-rhythms-and-oscillations.md)).
2. Neurons that code features of one object are linked by connections that pull them into
   the same phase.
3. Features of different objects settle into different phases.
4. A downstream neuron that sums inputs over a short time window responds most to inputs
   that arrive together, so it reads out one object at a time.
5. Learning strengthens links between features that often appear on the same object.

**How to test it here.**
Inside the standard test loop:
1. Build a small network of phase oscillators (each unit has a phase and an amplitude) in
   numpy.
2. Task: scenes with two objects, each with a colour and a shape; answer "what colour is
   the square?".
3. Compare against a rate-code network (no timing) of the same size and training.
4. Metric: accuracy on scenes with new colour-shape pairs. At least 5 seeds.
5. T3 part: whether real cortex uses synchrony for binding needs recordings during a
   binding task; that cannot be settled on a computer.

**Counts against it if:** a synchrony-binding model shows no gain on a binding task over a
rate code.

**Why it matters for a brain-like learner.** If timing carries binding, a brain-like learner
needs spiking or phase dynamics, not only rates. It competes with H060 and H078.

## H062 - Biological constraints give disentangled codes
**Status:** open · **Tier:** T1 · **Source:** Whittington et al. 2023, ICLR

**In simple words.** A **disentangled** code gives each hidden cause its own units: one set
for "size", another for "colour", with no mixing. This hypothesis says two simple facts of
biology push a network toward such codes. Firing rates cannot go below zero, and firing
costs energy. Under these limits, the cheapest way to describe the world is to give each
independent factor its own neurons.

**How it would work in the brain (if true).**
1. Firing rates are non-negative and spikes cost metabolic energy (established; see
   [glia-and-energy-budget](../../anatomy/glia-and-energy-budget.md)).
2. A learning circuit tries to represent its inputs well while keeping activity low.
3. Because rates cannot be negative, one unit cannot cheaply code both "more" and "less"
   of two mixed factors.
4. The solution that is both accurate and cheap puts each independent factor on its own
   units.
5. Downstream areas can then read each factor alone, which helps generalisation.

**How to test it here.**
Inside the standard test loop:
1. Make a synthetic dataset where inputs are generated from a few independent factors
   (for example position x, position y, colour) through a fixed random mixing.
2. Train a small autoencoder (a network that learns to reproduce its input through a
   narrow hidden layer) in numpy, with and without non-negativity and an activity
   penalty.
3. Measure disentanglement: how much each hidden unit depends on only one factor (for
   example mutual-information based scores).
4. Also measure transfer: train a readout on some factor combinations and test on new
   ones.
5. Use at least 5 seeds and a few penalty strengths.

**Counts against it if:** a net with these constraints shows no more disentanglement than a
net without them.

**Why it matters for a brain-like learner.** It would mean the cheap, brain-like constraints
are a feature: they give cleaner factors for free. It links to H058 and H080.

## H063 - Schemas speed up consolidation
**Status:** open · **Tier:** T1 · **Source:** Tse et al. 2007, *Science*

**In simple words.** **Consolidation** is the slow process by which a new memory, first held
by the hippocampus, becomes stored in cortex. It usually takes weeks. A **schema** is an
existing framework of knowledge, like knowing how a kitchen is laid out. This hypothesis
says that if a new fact fits a schema stored in medial prefrontal cortex, cortex can
absorb it within a day. You learn a new recipe fast if you already know cooking.

**How it would work in the brain (if true).**
1. A new episode is first stored quickly in the hippocampus (established, see
   [memory-systems](../../function/memory-systems.md)).
2. Medial prefrontal cortex holds a schema built from many earlier related experiences.
3. During replay or soon after learning, the new episode is compared with the schema.
4. If it fits, cortical synapses need only small, local changes to add the new item, so
   they change fast.
5. The memory soon no longer depends on the hippocampus. If there is no fitting schema,
   cortex must learn slowly to avoid overwriting old knowledge (H064).

**How to test it here.**
Inside the standard test loop:
1. Build a fast hippocampal store (one-shot associative memory) and a slow cortical
   network that learns from replayed items.
2. Condition A: pre-train cortex on many items from one structured set (the schema).
   Condition B: no pre-training, or pre-training on an unrelated set.
3. Add a few new items consistent with the structure and replay them.
4. Metric: number of replay steps until cortex recalls the new items with the hippocampus
   removed, and damage to old items. At least 5 seeds.

**Counts against it if:** a model with a schema and one without reach the same
consolidation speed.

**Why it matters for a brain-like learner.** It tells a learner when it is safe to learn fast:
when new data fits what it already knows. It refines H064 and links to H104 in section F.

## H064 - Slow cortex extracts abstraction from replay
**Status:** open · **Tier:** T1 · **Source:** McClelland, McNaughton & O'Reilly 1995, *Psychol Rev*; Kumaran et al. 2016, *Trends Cogn Sci*

**In simple words.** This is the idea of **complementary learning systems**. The
hippocampus learns fast and stores each event as it was. The cortex learns slowly. During
rest and sleep, the hippocampus replays many events, mixed together, and cortex slowly
picks out what they have in common. Like reading many recipes and slowly working out the
rules of baking. Fast-only learning would overwrite old knowledge; slow-only learning
could not keep single events.

**How it would work in the brain (if true).**
1. The hippocampus encodes each episode quickly with sparse, separate codes (established).
2. During rest and sleep, hippocampal cells replay recent sequences (established, Wilson &
   McNaughton 1994).
3. Replay sends episodes to cortex again and again, interleaved with older memories.
4. Cortical synapses change by small steps each time, so they learn the regularities
   across episodes rather than single events.
5. Over time cortex holds a general model and the hippocampus is no longer needed for it.

**How to test it here.**
Inside the standard test loop:
1. Build a fast store (one-shot memory) plus a slow numpy network trained on interleaved
   replay from the store.
2. Baseline: one network trained on each episode once, in order, with a learning rate
   tuned for it.
3. Data: episodes generated from a hidden structure (for example a small graph or a
   family tree).
4. Metric: performance on new items drawn from the same structure (generalisation) and on
   old items (forgetting). At least 5 seeds.

**Counts against it if:** a fast+slow system shows no better generalisation than one
system.

**Why it matters for a brain-like learner.** It is the classic reason a learner should have
two memories and replay. H063 adds schemas; H065 says replay also recombines; section F
covers the memory side in depth.

## H065 - Replay recombines episode pieces
**Status:** open · **Tier:** T1 · **Source:** Kurth-Nelson et al. 2023, *Neuron*

**In simple words.** Replay is not a faithful video of the past. This hypothesis says the
brain cuts episodes into pieces and joins them in new orders, the way you can imagine a
route you never walked by joining two streets you know. That is **compositional**
computation: building new wholes from known parts. It lets you plan and infer things you
never experienced directly.

**How it would work in the brain (if true).**
1. The hippocampus stores sequences from past episodes (established).
2. During rest, replay can produce paths never actually taken (reported in rodent
   studies cited by the source).
3. Pieces from different episodes that share a state (a place or an object) are joined at
   that shared point.
4. These new sequences train cortex or the value system as if they had been lived.
5. The animal can then use a new combination, such as a shortcut, without trying it first.

**How to test it here.**
Inside the standard test loop:
1. Build a small grid or graph world in numpy. Give the agent episodes that each cover only
   part of it.
2. Replay model A: faithful replay of stored episodes. Model B: replay that joins episode
   fragments at shared states.
3. Train a value function or a predictor on each kind of replay.
4. Test on start-goal pairs whose route needs pieces from different episodes.
5. Metric: success or steps to goal on those new combinations. At least 5 seeds.

**Counts against it if:** recombining replay vs faithful replay gives no gain on new
combinations.

**Why it matters for a brain-like learner.** It turns replay from a memory aid into a
reasoning tool. It extends H064 and links to H055 (structure) and H072 (analogy).

## H066 - Successor features split dynamics from goals
**Status:** open · **Tier:** T1 · **Source:** Barreto et al. 2017, NeurIPS

**In simple words.** A **successor representation** stores, for each place, which places you
tend to visit afterwards. It captures "what the world does" when you act. Goals ("what I
want") are kept separately as a reward for each feature. To get the value of a place you
multiply the two. If you suddenly want something new, you change only the goal part and
the plan updates at once. Like knowing a city well: a new errand needs a new destination,
not a new map.

**How it would work in the brain (if true).**
1. The hippocampus holds a predictive map of future states (proposed by Stachenfeld et al.
   2017; still a hypothesis).
2. This map is learnt with a prediction-error rule like temporal-difference learning, but
   about states, not reward.
3. A separate set of weights, perhaps in orbitofrontal cortex or striatum, links features to
   reward.
4. Value is the map times the reward weights.
5. When goals change, only the reward weights change. Several stored policies can be
   checked for the new goal at once (Barreto's "generalised policy improvement").

**How to test it here.**
Inside the standard test loop:
1. Build a successor-feature (SF) agent in a small numpy gridworld or in Brain World.
2. Baseline: a model-free agent (Q-learning) of matched size.
3. Train both on a set of reward functions over the same layout.
4. Switch to a new reward that is a new mix of the same features.
5. Metric: return in the first episodes after the switch (zero-shot) and episodes to
   recover. At least 5 seeds.

**Counts against it if:** an SF agent vs a model-free agent on new rewards in Brain World
shows no zero-shot gain.

**Why it matters for a brain-like learner.** It is a cheap middle ground between model-free
and full planning. It links to H055 (structure kept apart) and to section B on reward.

## H067 - Basal ganglia chunk actions
**Status:** open · **Tier:** T1 · **Source:** Graybiel 1998, *Neurobiol Learn Mem*

**In simple words.** When you learn to tie a shoelace, it starts as many separate moves.
With practice it becomes one smooth unit. That unit is a **chunk**. This hypothesis says
the basal ganglia (deep brain nuclei that help pick actions) build such chunks and store
them so they can be used inside bigger plans, the way words are used inside sentences.

**How it would work in the brain (if true).**
1. The basal ganglia take part in action selection and habit learning (established, see
   [action-selection-and-motor-control](../../function/action-selection-and-motor-control.md)).
2. With practice, striatal neurons fire more at the start and end of a learnt sequence
   and less in the middle (a pattern reported in Graybiel's lab).
3. A whole sequence comes to be triggered by one start signal.
4. Dopamine-driven learning treats the chunk as one action and assigns value to it.
5. New tasks that contain the same subsequence can call the chunk directly.

**How to test it here.**
Inside the standard test loop:
1. Build a set of tasks in a small numpy environment where solutions share subsequences
   (for example the same 4-step move pattern appears in several tasks).
2. Chunking agent: detects frequent action subsequences and adds them as new options
   (macro-actions).
3. Flat agent: only primitive actions, same learning rule.
4. Train on early tasks, test learning speed on later tasks that reuse subsequences.
5. Metric: episodes to criterion on later tasks. At least 5 seeds.

**Counts against it if:** a chunking agent vs a flat agent on tasks sharing subsequences
gives no speed-up.

**Why it matters for a brain-like learner.** Reusable action units would make Brain World's
later skills cheaper (for example walking inside grasping). It links to H068
(hierarchy of rules) and H070 (reused motifs).

## H068 - Frontal cortex as a hierarchy of rules
**Status:** open · **Tier:** T1/T2 · **Source:** Badre & D'Esposito 2009, *Nat Rev Neurosci*

**In simple words.** Some rules are concrete: "press left for red". Others are about rules:
"in this context, use the colour rule". This hypothesis says the frontal cortex is laid
out from back to front by how abstract its rules are. Back areas link stimuli to actions.
Front areas pick which set of rules to use. Like a company where workers do tasks,
managers choose tasks, and directors choose goals.

**How it would work in the brain (if true).**
1. Damage to prefrontal cortex hurts flexible rule use (established, see
   [prefrontal-cortex-and-abstraction](../../function/prefrontal-cortex-and-abstraction.md)).
2. Premotor areas link a stimulus to a response.
3. More anterior areas hold a context that selects which stimulus-response mapping is
   active.
4. The most anterior areas hold higher contexts that select among those contexts.
5. Each level sends top-down signals to the level behind it, and learning at a level only
   needs to change its own small mapping.

**How to test it here.**
Inside the standard test loop:
1. Make a nested-rule task: a top cue picks a rule set, a second cue picks a rule, and the
   stimulus picks the action.
2. Hierarchical model: separate layers or modules for each level, each gating the one
   below.
3. Flat model: one network of the same total size receiving all cues at once.
4. Metric: learning curve (trials to criterion) and transfer when one level's rules
   change. At least 5 seeds.
5. T2 option: check open fMRI from a hierarchical rule task for a front-to-back gradient.

**Counts against it if:** a hierarchical-rule model and a flat model have the same learning
curve on nested rules.

**Why it matters for a brain-like learner.** It suggests building control in layers, so a
change of goal touches only one layer. It links to H067 and to section J (control).

## H069 - Tasks as low-rank parts of recurrent weights
**Status:** open · **Tier:** T1 · **Source:** Mastrogiuseppe & Ostojic 2018, *Neuron*

**In simple words.** A recurrent network has a big weight matrix that links every neuron to
every other. A **low-rank** matrix is one that can be built from just a few patterns, like
a picture made of a few stripes. This hypothesis says each task uses only a few such
patterns in the weights. Abstraction would then mean that different tasks share some of
the same patterns, so learning a new task reuses old parts.

**How it would work in the brain (if true).**
1. Cortical circuits are recurrent: neurons excite and inhibit each other in loops
   (established).
2. The part of the connectivity that matters for a task is made of a few input-output
   pattern pairs.
3. These patterns define a small subspace where activity moves during the task (compare
   [population-dynamics-and-neural-manifolds](../../function/population-dynamics-and-neural-manifolds.md)).
4. Related tasks share some patterns, for example one for "hold a value in memory".
5. Learning a new related task adds or tunes a few patterns instead of rewriting the whole
   matrix.

**How to test it here.**
Inside the standard test loop:
1. Build a small rate RNN in numpy. Make a family of related tasks (for example memory,
   comparison and their combinations).
2. Low-rank model: recurrent weights forced to be a sum of a few outer products. Full-rank
   model: no constraint.
3. Train on some tasks; then on a new task allow only new rank-one parts or fine-tuning.
4. Measure reuse: how much the learnt patterns for different tasks overlap, and how fast
   the new task is learnt. At least 5 seeds.

**Counts against it if:** a low-rank RNN vs a full-rank RNN on task families shows no reuse.

**Why it matters for a brain-like learner.** Low-rank parts are small and could be stored or
transferred cheaply. It is closely tied to H070 and H077.

## H070 - Shared dynamical motifs across tasks
**Status:** open · **Tier:** T1 · **Source:** Yang et al. 2019, *Nat Neurosci*; Driscoll, Shenoy & Sussillo 2024, *Nat Neurosci*

**In simple words.** A **dynamical motif** is a recurring pattern of how activity moves in a
network, such as "settle on one of two points" (a decision) or "hold still" (memory). This
hypothesis says a network trained on many tasks builds a small toolbox of these motifs and
reuses them across tasks, like a cook who reuses "chop", "fry" and "stir" in many dishes.
Tasks become combinations of motifs.

**How it would work in the brain (if true).**
1. Population activity in cortex follows low-dimensional paths during tasks (established
   as a description; see
   [population-dynamics-and-neural-manifolds](../../function/population-dynamics-and-neural-manifolds.md)).
2. During learning, groups of units come to support specific motifs such as fixed points,
   rotations or decision boundaries.
3. A task cue selects which motifs are active.
4. A new task made of known parts is learnt by selecting the right motifs.
5. The source papers report this in networks trained with backprop; whether local rules do
   the same is the open part.

**How to test it here.**
Inside the standard test loop:
1. Train a small multitask RNN in numpy with a local learning rule (for example a three-
   factor or e-prop-like rule) on a few tasks that share parts.
2. Train the same network with backprop as a reference.
3. Motif analysis: find fixed points and slow regions for each task, and check whether the
   same units and the same structures serve several tasks.
4. Test learning speed on a new task made of known parts.
5. At least 5 seeds per rule.

**Counts against it if:** motif analysis of a local-rule multitask net finds no shared
motifs.

**Why it matters for a brain-like learner.** If local rules also produce shared motifs,
reuse does not need backprop. It links to H069, H077 and
[one-brain-many-tasks](../../function/one-brain-many-tasks.md).

## H071 - Abstraction as compression
**Status:** open · **Tier:** T1 · **Source:** Chater & Vitányi 2003, *Trends Cogn Sci*

**In simple words.** If you can describe a long list of numbers as "the even numbers up to
100", you have compressed it and found its rule. This hypothesis says the brain looks for
the shortest description of what it sees, and that this short description is the
abstraction. The formal version is **minimum description length (MDL)**: pick the model
that makes model size plus the cost of the leftover errors smallest.

**How it would work in the brain (if true).**
1. Sensory input is redundant, and early sensory codes reduce redundancy (efficient coding
   is a well-studied idea; how far it explains the brain is debated).
2. Learning favours models that predict the input with few parameters or little activity.
3. Short models capture the shared rule and drop the details unique to each example.
4. Those short models then apply to new examples that follow the same rule.
5. Plasticity is held back by a cost (for example energy or synapse count) that acts like a
   description-length penalty.

**How to test it here.**
Inside the standard test loop:
1. Take a small numpy learner (the Tiny MLP or a small agent on the H101 transfer setup).
2. Add an MDL-like penalty: for example a sparsity or weight-precision penalty that
   approximates the number of bits needed to store the model.
3. Baseline: the same learner without the penalty, with ordinary tuning.
4. Metric: transfer to held-out structure-sharing tasks, and the size of the learnt model.
   Sweep the penalty weight. At least 5 seeds.

**Counts against it if:** an MDL-penalised learner shows no better transfer than a plain
learner.

**Why it matters for a brain-like learner.** It gives a single objective for abstraction.
It overlaps with H062 (energy cost) and H080 (compression phase), and with H081 in
section E (the genome bottleneck).

## H072 - Analogy as matching relations
**Status:** open · **Tier:** T1 · **Source:** Gentner 1983, *Cogn Sci*

**In simple words.** "An atom is like the solar system." The two look nothing alike. The
analogy works because the *relations* match: small things go round a big central thing.
This hypothesis says analogy is mapping one structure onto another by lining up relations,
and ignoring surface features like colour or size. It is called **structure mapping**.

**How it would work in the brain (if true).**
1. The brain stores situations as items plus relations between them.
2. When facing a new situation, it searches memory for a stored one whose relations match,
   even if the items look different.
3. It pairs items one-to-one so that matching relations line up (systematic, consistent
   mapping).
4. Knowledge about the stored situation is then carried over to the new one.
5. Prefrontal cortex is often linked to holding and comparing relations (see
   [prefrontal-cortex-and-abstraction](../../function/prefrontal-cortex-and-abstraction.md));
   the exact mechanism is the claim.

**How to test it here.**
Inside the standard test loop:
1. Represent each Brain World layout as a small graph of objects and relations (left of,
   near, food-for).
2. Structure-mapping model: find the mapping between a known layout and a new one that
   matches the most relations, then reuse the known policy through that mapping.
3. Baseline: a feature-matching model that maps by similar looks, and an agent that learns
   from scratch.
4. Use the H101 transfer setup with layouts that are surface-different but share relations.
5. Metric: performance on new layouts in the first episodes. At least 5 seeds.

**Counts against it if:** a structure-mapping model in Brain World shows no transfer on
surface-different layouts.

**Why it matters for a brain-like learner.** It names a clear mechanism for transfer. It
competes with learnt-geometry accounts (H058) and builds on H055 and H060.

## H073 - Concept cells are learnt
**Status:** open · **Tier:** T1/T3 · **Source:** Quian Quiroga et al. 2005, *Nature*

**In simple words.** Recordings in the human medial temporal lobe (the area around the
hippocampus) found neurons that fire to one person or place, whether shown as a photo, a
drawing, or the written name. These are **concept cells**. They are **sparse** (few cells
fire for any one concept) and **invariant** (the same cell fires across very different
views). This hypothesis says such cells are built by learning, not wired in from birth.

**How it would work in the brain (if true).**
1. Concept-like neurons exist in human medial temporal lobe (reported by the source,
   recorded in epilepsy patients).
2. Visual and other sensory streams send increasingly invariant codes to the medial
   temporal lobe.
3. When different views or names of the same thing appear close in time or together, a
   Hebbian rule strengthens their links onto the same cells.
4. Competition between cells (for example by inhibition) keeps the code sparse.
5. Over time a few cells come to respond to the concept across all its forms.

**How to test it here.**
Inside the standard test loop:
1. Build a two-layer numpy net with Hebbian learning and winner-take-most inhibition.
2. Input: several "concepts", each shown in several very different forms (different input
   patterns), with forms of one concept appearing close in time.
3. After learning, check each hidden unit: does it fire for all forms of one concept and
   little else?
4. Baseline: the same net without temporal grouping, or with random weights.
5. Metric: fraction of units that are sparse and invariant. At least 5 seeds.
6. T3 part: whether real concept cells are learnt needs recordings during learning of new
   concepts in people.

**Counts against it if:** a sparse local-rule net produces no invariant "concept units".

**Why it matters for a brain-like learner.** It suggests symbols can grow from plain local
rules. It links to H060 (symbols as vectors) and H078 (assemblies).

## H074 - Time cells as a reusable time axis
**Status:** open · **Tier:** T1 · **Source:** Eichenbaum 2014, *Nat Rev Neurosci*; Howard & Kahana 2002, *J Math Psychol*

**In simple words.** **Time cells** are hippocampal neurons that fire one after another at
particular moments during a delay, like the hands of a clock. This hypothesis says they
give an abstract time line that any sequence can be pinned to. The **temporal context
model** adds that the brain keeps a slowly drifting "context" signal, so events close in
time get similar context and become linked.

**How it would work in the brain (if true).**
1. Hippocampal time cells fire in sequence across a delay (reported, MacDonald et al. 2011;
   see [timing-and-sequence-learning](../../function/timing-and-sequence-learning.md)).
2. A context signal drifts slowly, mixing in each new event.
3. Each event is linked to the context present when it happened.
4. Recalling one event brings back its context, which then cues nearby events.
5. The same time code is reused for very different sequences, so learning the timing of
   one task helps with another.

**How to test it here.**
Inside the standard test loop:
1. Build a temporal-context model in numpy: a context vector updated as
   context = rho * context + (1 - rho) * input, with events linked to context.
2. Baseline: fixed delay lines (a set of units, each a copy of the input delayed by a set
   number of steps).
3. Train both on one set of sequences, then test on new sequences with new items but the
   same timing structure.
4. Metric: next-item prediction and timing error on the new sequences. At least 5 seeds.

**Counts against it if:** a temporal-context model vs fixed delay lines shows no sequence
transfer.

**Why it matters for a brain-like learner.** A shared time axis would let a learner reuse
timing across skills. It is the time version of H055 (a structure code reused for new
content).

## H075 - Latent causes and reusable task clusters
**Status:** open · **Tier:** T1 · **Source:** Collins & Frank 2013, *Psychol Rev*; Gershman & Niv 2010, *Curr Opin Neurobiol*

**In simple words.** When the rules suddenly change, a smart learner does not just slowly
unlearn. It asks "is this a new situation, or one I have seen before?". A **latent cause**
is a hidden reason behind what you observe, like "I am now in my grandmother's kitchen".
This hypothesis says people group experiences into such hidden causes, store a policy for
each group, and when an old group comes back, reuse its whole policy at once.

**How it would work in the brain (if true).**
1. The learner keeps a set of hidden contexts, each with its own policy.
2. Each new observation is checked: does it fit an existing context well, or is it
   surprising enough to start a new one?
3. Only the policy of the active context is updated, so other contexts are protected.
4. When a familiar context returns, its stored policy is selected at once.
5. Prefrontal cortex and basal ganglia loops are proposed to do this selection; the details
   are the claim.

**How to test it here.**
Inside the standard test loop:
1. Build a latent-cause agent in numpy: a small set of context slots, a rule for creating
   a new slot (for example a Chinese restaurant process prior, which makes new contexts
   less likely the more contexts already exist), and one policy per slot.
2. Baseline: a single-policy agent with the same learning rule.
3. In Brain World or a gridworld, alternate layouts A, B, A, C, B.
4. Metric: episodes to relearn a returning layout, and damage to other layouts. At least
   5 seeds.

**Counts against it if:** a latent-cause agent in Brain World shows no faster relearning of
returning layouts (links to #57/#60).

**Why it matters for a brain-like learner.** It protects old skills and gives instant reuse.
It is a mechanism for H077 (separate contexts) and links to the forgetting rows in
section F.

## H076 - Choosing among structural forms
**Status:** open · **Tier:** T1 · **Source:** Kemp & Tenenbaum 2008, *PNAS*

**In simple words.** Different knowledge has different shapes. Animals fit a tree
(mammals, then dogs, then breeds). Colours fit a ring. Cities fit a 2D map. Political views
may fit a line. This hypothesis says the brain does not assume one shape. It tries several
**structural forms** and picks the one that fits the data best, then uses that shape to
reason about new items.

**How it would work in the brain (if true).**
1. The learner holds a small set of candidate forms: chain, ring, tree, grid, clusters.
2. For a new domain, it fits each form to the observed similarities or relations.
3. It scores each fit, trading off how well it explains the data against how complex the
   form is.
4. The best form is kept and new items are placed into it.
5. Predictions about unseen items follow from their place in that form.

**How to test it here.**
Inside the standard test loop:
1. Make synthetic category data generated from known forms (a tree, a ring, a grid), with
   noise.
2. Form-discovery model: fit each candidate form and choose by a score that penalises
   complexity.
3. Baseline: a model that always uses one fixed form (for example always a tree, or
   always a flat space).
4. Metric: held-out prediction of features or similarities, and whether the right form is
   recovered. At least 5 seeds.
5. Optionally use a small open dataset of animal features as a check.

**Counts against it if:** a form-discovery model vs a fixed-form model gives the same fit to
category data.

**Why it matters for a brain-like learner.** It suggests the learner should test the shape of
a problem before learning its details. It generalises H055 and H056 beyond grids and links
to H071 (simplicity).

## H077 - Orthogonal subspaces prevent interference
**Status:** open · **Tier:** T1 · **Source:** Flesch et al. 2022, *Neuron*; Zeng et al. 2019, *Nat Mach Intell*

**In simple words.** Learning task B often damages task A. This is **interference**, and in
the worst case **catastrophic forgetting**. This hypothesis says the brain avoids it by
putting each context in its own **orthogonal subspace**: directions in activity space that
do not overlap, like two streets crossing at right angles. Changes made along one street
do not move you along the other.

**How it would work in the brain (if true).**
1. A context signal (for example from prefrontal cortex) tells the network which task is
   active.
2. The context gates or shifts activity so each task uses a different set of directions.
3. Learning for task B changes weights mainly along task B's directions.
4. Because task A's directions are orthogonal, its readout is barely changed.
5. Shared parts can still be reused where tasks truly overlap.

**How to test it here.**
Inside the standard test loop:
1. Build a small numpy network and two or more tasks learnt one after the other.
2. Orthogonalising rule: project each weight update away from the input directions used
   by earlier tasks (as in orthogonal weight modification, Zeng et al. 2019).
3. Baseline: the plain rule, and optionally elastic weight consolidation
   (Kirkpatrick et al. 2017).
4. Metric: accuracy on earlier tasks after learning later ones (forgetting), and new-task
   accuracy. At least 5 seeds.

**Counts against it if:** an orthogonalising rule vs a plain rule gives the same forgetting.

**Why it matters for a brain-like learner.** It is a direct fix for the forgetting Brain World
must avoid across its five skills. It links to H075 (contexts), H069/H070 (reuse), and
[one-brain-many-tasks](../../function/one-brain-many-tasks.md).

## H078 - Assembly calculus
**Status:** open · **Tier:** T1 · **Source:** Papadimitriou et al. 2020, *PNAS*; Buzsáki 2010, *Neuron*

**In simple words.** A **cell assembly** is a group of neurons that fire together and stand
for one item (an idea going back to Hebb 1949). **Assembly calculus** says assemblies are
the brain's basic unit of computation. A few operations on them, such as **project** (copy
an assembly into another area), **associate** and **merge** (make one assembly for two
combined), are enough to compute things like parsing a sentence.

**How it would work in the brain (if true).**
1. An input activates neurons in an area; only the most strongly driven ones fire (a cap
   set by inhibition).
2. Hebbian plasticity strengthens links among the neurons that fire together, so a stable
   assembly forms.
3. Project: firing an assembly in area A creates a linked assembly in area B.
4. Merge: two assemblies projected into the same area form a new assembly that stands for
   their combination.
5. Chains of these operations, gated by which areas are active, build structures like
   phrases.

**How to test it here.**
Inside the standard test loop:
1. Build the assembly model in numpy: a few areas of random sparse neurons, a top-k firing
   cap, Hebbian learning.
2. Implement project and merge, and a small controller that turns areas on and off.
3. Task: parse sentences from a tiny grammar (for example subject-verb-object with a few
   words) into a structure that can be read back.
4. Baseline: the same model with plasticity turned off, so assemblies do not stabilise.
5. Metric: parse accuracy on sentences not used to tune the model, vs number of neurons
   and cap size. At least 5 seeds.

**Counts against it if:** the assembly-calculus model cannot parse a small grammar.

**Why it matters for a brain-like learner.** It offers symbols built from plain Hebbian
learning and inhibition. It competes with H060 and H061 as the answer to binding, and links
to language rows in section G.

## H079 - Abstraction needs surface variety
**Status:** open · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** If you always see the same red ball in the same room, you might learn
"red ball in this room", not "ball". This hypothesis says abstraction forms only when the
structure stays the same while surface details keep changing. Variety forces the learner
to rely on what stays fixed. Like learning a song: if you hear it on many instruments, you
learn the melody, not the instrument.

**How it would work in the brain (if true).**
1. A learner sees many episodes that share a hidden structure.
2. If surface features (colours, textures, positions) also stay the same, both structure
   and surface predict reward, and the learner may latch onto the surface.
3. If the surface changes from episode to episode, only the structure keeps predicting
   reward.
4. Plasticity then strengthens the synapses that track the structure and weakens the ones
   tied to surface features.
5. The resulting code transfers to new surfaces.

**How to test it here.**
Inside the standard test loop:
1. Use the H101 transfer setup in Brain World.
2. Low-variety condition: train on layouts with fixed colours, textures and object
   positions. High-variety condition: same structure, surface details changed each
   episode.
3. Keep the total amount of training equal.
4. Test both on new layouts that share structure but have new surface features.
5. Metric: transfer score, plus a probe of whether hidden units encode surface or
   structure. At least 5 seeds.

**Counts against it if:** Brain World with low vs high surface variety shows no difference in
transfer.

**Why it matters for a brain-like learner.** It is about the data, not the rule: it says
training worlds must vary. It links to H101 and H058, and to development rows in section
E.

## H080 - Expand, then compress
**Status:** open · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** Early in learning, the brain may spread a problem over many
dimensions so it is easy to separate the cases (expand). Later, once it knows what
matters, it squeezes the code down to a few dimensions that capture the rule (compress).
Like brainstorming many options first, then boiling them down. A common measure of how
many dimensions a code uses is the **participation ratio**: computed from the variance
along each principal direction, it is high when activity is spread over many directions
and low when it sits in a few.

**How it would work in the brain (if true).**
1. A new task arrives. Mixed-selective units respond in many combinations, so dimension
   rises (H059).
2. A readout learns quickly in this high-dimensional code.
3. With more experience, plasticity (perhaps aided by energy cost, H062, or replay, H064)
   removes directions that do not help prediction.
4. The code shrinks to the few directions that matter for the task.
5. This low-dimensional code then transfers better to new cases (H058).

**How to test it here.**
Inside the standard test loop:
1. Train the Tiny MLP and a small Brain World or gridworld agent, with backprop and with
   a local rule.
2. At regular points during training, record hidden activity on a fixed set of inputs.
3. Compute the participation ratio: (sum of eigenvalues)^2 / sum of squared eigenvalues of
   the activity covariance.
4. Plot it against training time, and against test transfer at the same points.
5. Use at least 5 seeds and a few network sizes and initial weight scales (these are known
   to change learning dynamics).

**Counts against it if:** tracking participation ratio during training shows no
expand-then-compress pattern.

**Why it matters for a brain-like learner.** It would reconcile H059 (high dimension helps
learning) and H058/H071 (low dimension helps generalisation) as two phases of one process.
