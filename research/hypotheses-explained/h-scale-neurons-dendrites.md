# H. Scale, neurons and dendrites, explained

Part of [the 170 hypotheses, explained simply](README.md). Main table and status:
[learning-algorithm-hypotheses.md](../learning-algorithm-hypotheses.md). Every row is a
**hypothesis**, not an established fact.

## The big idea of this group
What makes a human brain more capable than a monkey's or a mouse's: more parts, or
better parts? These rows look at the size of the system (neurons, synapses) and at the
power of each single neuron. Some background is established: the human brain has about
86 billion neurons and fits the scaling rule of other primates (Azevedo et al. 2009;
Herculano-Houzel 2009), and dendrites (the branching input trees of a neuron) can make
their own local electrical spikes (see
[dendritic-computation](../../anatomy/dendritic-computation.md) and
[comparative-and-evolutionary-neuroscience](../../anatomy/comparative-and-evolutionary-neuroscience.md)).
What is claimed is how much each factor matters for learning. H131 and H137 are about
scale (more neurons vs more synapses). H132-H135 say single neurons are much more
powerful than the "point neurons" of deep learning, which just add up inputs. H136 is
about a limit: learning may be stuck inside the patterns of activity the network
already has.

## H131 - More neurons, not a different algorithm
**Status:** open · **Tier:** T1/T2 · **Source:** Herculano-Houzel 2009, *Front Hum Neurosci*

**In simple words.** Herculano-Houzel counted neurons across species and found that the
human brain looks like a scaled-up primate brain, not a special design (established
for the counts). This row goes further: it claims humans are smarter mainly because we
have more cortical neurons, and that the learning algorithm is the same as in other
primates. It is like two factories using the same machines, one with many more of them.

**How it would work in the brain (if true).**
1. Primate brains add neurons at a roughly constant size per neuron, so a bigger
   primate brain holds many more neurons (established, Herculano-Houzel et al. 2007).
2. The human cortex therefore has many more neurons than other primates' (established).
3. Each cortical area uses the same local circuits and the same plasticity rules as in
   other primates.
4. More neurons give more room for features, more areas and longer chains of processing.
5. Abilities like abstraction and language emerge from that extra capacity, not from a
   new rule.

**How to test it here.**
Inside the standard test loop:
1. T1: take one local-rule model (for example a Hebbian or three-factor network) and
   train it at several sizes on the same task, such as Brain World.
2. Keep the rule and all settings fixed; change only the number of neurons.
3. Measure abstraction with the H101 transfer setup (score on new layouts with shared
   structure) at each size, over at least 5 seeds.
4. Plot transfer against size and look for a rising trend.
5. T2: compare open cross-species neuron counts with behavioural measures, keeping in mind
   that a correlation alone cannot settle it.

**Counts against it if:** scaling the local-rule model does not make abstraction appear
with size.

**Why it matters for a brain-like learner.** If true, the fastest route is a simple rule
at large scale. It sits close to H090 (direct fit) and competes with rows that need a
special algorithm (section A) or special priors (section E). H137 asks which kind of
scale counts.

## H132 - Compartmentalised human dendrites
**Status:** weakened (#85: with random branch inputs, dendritic neurons were no better than point neurons at equal parameters, and worse under feedback alignment) · **Tier:** T1 · **Source:** Beaulieu-Laroche et al. 2018, *Cell*

**In simple words.** A dendrite is a neuron's input tree. If its branches are electrically
well connected, inputs all blend into one total. If the branches are more separated
("compartmentalised"), each part can work on its own. Beaulieu-Laroche and colleagues
recorded from human cortical neurons and found their dendrites are more electrically
separated than rat dendrites. The claim is that this gives each human neuron more
independent computing units. It is like an office with separate rooms instead of one
open hall: several conversations can happen at once.

**How it would work in the brain (if true).**
1. Human cortical neurons are larger, with long dendrites (established).
2. The source reported weaker electrical coupling between distant dendrites and the cell
   body in human neurons.
3. Because of this, a branch far from the cell body can process its inputs without being
   swamped by the rest of the cell.
4. Each such zone works like a small separate unit that applies its own nonlinearity (a
   threshold or curve, not just a sum).
5. A human neuron thus does the work of several simpler units.

**How to test it here.**
Inside the standard test loop:
1. Build two numpy neuron models (this is issue #85): a lumped neuron that sums all inputs
   once, and a compartmentalised one with several branch units, each with its own
   nonlinearity, feeding the cell body.
2. Keep the number of synapses and parameters equal.
3. Measure capacity: how many random input-label patterns each can store, and accuracy on
   a small task in the Tiny MLP setting.
4. Repeat for several numbers of compartments and at least 5 seeds.

**Counts against it if:** the compartmentalised model and the lumped model reach the same
capacity.

**Why it matters for a brain-like learner.** If true, a brain-like model should use
richer neurons, not only more neurons. It links to H133-H135 and to H131 (another
explanation for human ability besides neuron count).

## H133 - Single dendrites compute XOR
**Status:** open · **Tier:** T1 · **Source:** Gidon et al. 2020, *Science*

**In simple words.** XOR means "one or the other, but not both". A classic point neuron
(sum the inputs, then threshold) cannot compute it; you need at least two layers.
Gidon and colleagues found a new kind of dendritic spike in human layer 2/3 neurons: it
is strongest for medium input and weaker for strong input. That lets a single dendrite
compute XOR (established for the recordings and model in the paper). This row claims
this ability matters for what human cortex can learn. It is like a light that turns on
for one switch but goes off when both are flipped.

**How it would work in the brain (if true).**
1. Human layer 2/3 dendrites produce calcium-based dendritic action potentials
   (reported by the source).
2. Their size peaks at a medium input level and falls for stronger input (reported by the
   source).
3. So input A alone, or B alone, triggers the spike, but A and B together give too much
   input and the spike shrinks.
4. The neuron fires for "A or B, not both": XOR in one cell.
5. Networks of such neurons need fewer cells for tasks that a point-neuron net solves
   only with an extra layer.

**How to test it here.**
Inside the standard test loop:
1. Write a numpy neuron whose dendritic unit has a bump-shaped (rise then fall) response
   instead of a monotonic one.
2. Build a small network of these neurons and a point-neuron network with the same
   number of neurons and parameters.
3. Train both on XOR-like and parity-like tasks (the Tiny MLP tasks) with the same
   learning rule.
4. Measure accuracy and how many neurons each needs to solve the task, over at least 5
   seeds.

**Counts against it if:** the dendritic-XOR network shows no capacity gain over the
point-neuron network.

**Why it matters for a brain-like learner.** It suggests a cheap extra nonlinearity per
neuron. It is a specific case of H132 and H134.

## H134 - One neuron equals a deep net
**Status:** open · **Tier:** T1 · **Source:** Beniaguev, Segev & London 2021, *Neuron*

**In simple words.** How powerful is one real neuron? Beniaguev and colleagues took a
detailed computer model of a layer 5 cortical neuron and trained deep networks to copy
its output, spike for spike. They needed a network with 5 to 8 layers. Without NMDA
receptors (a type of synapse channel that makes dendrites nonlinear) one hidden layer was
enough (established modelling result, see
[dendritic-computation](../../anatomy/dendritic-computation.md)). The row claims that a
real cortical neuron really is that powerful. It is like finding that one worker does
the job of a whole small team.

**How it would work in the brain (if true).**
1. A layer 5 pyramidal neuron gets thousands of inputs across a large dendritic tree
   (established).
2. NMDA channels make clustered inputs on a branch combine nonlinearly (established).
3. Branch outputs then interact with each other and with the cell body over time.
4. The result is an input-output mapping that only a 5-8 layer net can copy.
5. A cortical network is then a network of deep networks, with far more computing power
   than its neuron count suggests.

**How to test it here.**
Inside the standard test loop:
1. Build a small numpy multi-compartment neuron with NMDA-like nonlinear branches
   (simplified, not a full biophysical model).
2. Generate random input spike trains and record the model's output.
3. Fit networks of depth 1, 2, 4 and more to predict the output, with equal parameter
   counts where possible.
4. Report prediction quality against depth, with and without the NMDA nonlinearity, over
   at least 5 seeds.

**Counts against it if:** in a fit-a-neuron replication, a shallow net does as well as a
deep one.

**Why it matters for a brain-like learner.** If true, counting neurons badly
underestimates brain capacity, and comparing brains to deep nets by unit count is
misleading. It links to H135 (a simpler two-layer version) and H131.

## H135 - Each branch is a learning unit
**Status:** open · **Tier:** T1 · **Source:** Poirazi, Brannon & Mel 2003, *Neuron*

**In simple words.** Poirazi and colleagues showed that a detailed hippocampal neuron
model behaves like a two-layer network. Each dendritic branch applies its own threshold
to its summed input, and the cell body adds up the branch outputs (established
modelling result). This row goes a step further: each branch also *learns* on its own,
with its own local plasticity. It is like a choir where each section practises its part
separately, and the conductor only blends them.

**How it would work in the brain (if true).**
1. Inputs that land together on one branch can trigger a local branch spike
   (established).
2. That local spike is a signal only that branch sees.
3. Synapses on the branch strengthen when they helped cause the branch spike, so learning
   depends on the branch, not on the whole cell's output.
4. Different branches come to store different input patterns.
5. One neuron thus stores many patterns, one or more per branch, instead of one.

**How to test it here.**
Inside the standard test loop:
1. Build a numpy two-layer neuron: branches with a sigmoid each, summed at the cell body.
2. Rule A: branch-local plasticity (update a synapse when its own branch is active and
   a global reward or target says "good").
3. Rule B: neuron-global plasticity (update all synapses based on the cell's output only).
4. Measure storage: the number of random patterns stored before errors rise, over at
   least 5 seeds and a few branch counts.

**Counts against it if:** branch-local plasticity gives no storage gain over
neuron-global plasticity.

**Why it matters for a brain-like learner.** It moves part of learning below the neuron
level and gives a cheap way to raise memory per cell. It links to H132-H134 and to
dendrite-based credit assignment ideas in section A.

## H136 - Learning stays on the existing manifold
**Status:** open · **Tier:** T1/T2 · **Source:** Sadtler et al. 2014, *Nature*

**In simple words.** A group of neurons can in principle fire in countless combinations,
but in practice it uses only a few main patterns. Those patterns form a
"low-dimensional manifold", a small surface inside the space of all possible activity.
Sadtler and colleagues had monkeys control a cursor with a brain-computer interface.
When the new mapping could be done with existing patterns, monkeys learned it; when it
needed new patterns, they did not learn it within a session (reported by the source; see
[population-dynamics-and-neural-manifolds](../../function/population-dynamics-and-neural-manifolds.md)).
The claim is that this is a general limit on fast learning. It is like a pianist who can
quickly learn new songs with familiar hand shapes but needs much longer for a new
technique.

**How it would work in the brain (if true).**
1. Recurrent connections in a circuit make some activity patterns easy and others hard.
2. So population activity lies on a low-dimensional manifold.
3. Fast learning changes which existing patterns are used, or how they are read out.
4. Reaching patterns off the manifold needs rewiring of the recurrent connections
   themselves, which is slow.
5. New skills that fit the old manifold are learned quickly; others take long practice.

**How to test it here.**
Inside the standard test loop:
1. Train a small numpy recurrent network on a task so it settles into a manifold; find it
   with principal component analysis (PCA, a way to find the main patterns of activity).
2. Add a readout "decoder" like a brain-computer interface. Then perturb it in two ways:
   within the manifold, and needing new directions outside it.
3. Let the network relearn with a local rule. Measure how fast performance recovers for
   each kind, over at least 5 seeds.
4. T2: reanalyse open brain-computer interface data for the same contrast.

**Counts against it if:** the model learns on- and off-manifold perturbations equally
fast.

**Why it matters for a brain-like learner.** If true, a learner's early wiring limits
what it can learn quickly later. It links to H080 (expand then compress) and to section E
on development.

## H137 - Synapses are the real budget
**Status:** open · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** When you make a brain-like model bigger, you can add more neurons or
give each neuron more synapses (connections). This row claims synapses are the
resource that counts: with a fixed total number of synapses, more synapses per neuron
helps more than more neurons. It is like a phone network: more phones help less than
more lines between them.

**How it would work in the brain (if true).**
1. Each synapse stores information in its strength; memory capacity grows with the
   number of synapses.
2. A neuron with many synapses can combine many inputs, and with dendrites (H132-H135)
   can combine them in complex ways.
3. Energy and space limit the total amount of wiring.
4. Within that limit, evolution would favour neurons with many synapses over many
   neurons with few synapses.
5. Learning rules use those synapses to store patterns and build features.

**How to test it here.**
Inside the standard test loop:
1. Choose a local-rule network (Hebbian or three-factor) and a task (pattern storage, or
   Brain World).
2. Equal-synapse scaling: fix the total synapse count; vary neurons vs synapses per
   neuron (many neurons with few inputs, or few neurons with many).
3. Equal-neuron scaling: fix neurons, add synapses per neuron; compare with adding
   neurons at fixed synapses per neuron.
4. Measure score and transfer (H101 transfer setup) against neurons and synapses, over at
   least 5 seeds.

**Counts against it if:** in equal-synapse vs equal-neuron scaling in a local-rule net,
neurons matter more.

**Why it matters for a brain-like learner.** It tells you how to spend a fixed hardware
budget. It competes with H131 (neurons are what count) and links to H088 (pruning sets
the synapse count).
