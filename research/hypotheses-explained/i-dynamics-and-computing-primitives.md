# I. Dynamics and alternative computing primitives, explained

Part of [the 170 hypotheses, explained simply](README.md). Main table and status:
[learning-algorithm-hypotheses.md](../learning-algorithm-hypotheses.md). Every row is a
**hypothesis**, not an established fact.

## The big idea of this group

Most of this research looks for a learning *rule*: which synapse changes, and by how much.
This group asks a different question. Maybe a lot of the work is done by the *dynamics*:
how activity flows, settles, oscillates and stays in a safe range, and by parts of the
brain that are not ordinary synapses at all. It is established that recurrent circuits
have rich ongoing activity, that the hippocampus has a theta rhythm, that firing rates
are kept roughly stable by homeostasis, that synapses often fail to release transmitter,
and that astrocytes, myelin and new synapses all change with experience (see
[learning-and-plasticity](../../function/learning-and-plasticity.md),
[brain-rhythms-and-oscillations](../../function/brain-rhythms-and-oscillations.md) and
[glia-and-energy-budget](../../anatomy/glia-and-energy-budget.md)). What is claimed is
that each of these does a specific job *for learning*. Some rows are tools to compute with
(reservoirs, FORCE, attractors, sampling: H138-H140, H144). Some are about timing (theta:
H141-H142, myelin: H150). Some are about keeping learning stable (criticality, inhibitory
plasticity, scaling, BCM: H143, H145-H147). The rest add new storage or regularisation
(astrocytes, rewiring, transmission failure: H148, H149, H151). The stability rows overlap
and partly compete: if one of them is enough, the others may be redundant.

## H138 - Fixed random reservoirs, learned readouts

**Status:** open · **Tier:** T1 · **Source:** Jaeger 2001 (GMD report 148); Maass, Natschläger & Markram 2002, *Neural Comput*

**In simple words.** A *reservoir* is a big recurrent network (neurons that feed back to
each other) whose connections are random and never change. When input arrives, it makes
a complicated echo of ripples inside, like stones dropped in a pond. A *readout* is a
simple layer that learns to read the answer off those ripples. The claim is that most
brain circuits are like the pond: fixed and random. Only the readouts learn. That would
make learning cheap, because only one layer of weights has to change.

**How it would work in the brain (if true).**
1. Sensory input drives a recurrent local circuit, for example a patch of cortex.
2. The circuit's recurrent connections, set up during development, stay mostly fixed.
3. The circuit turns the input into a high-dimensional, time-smeared pattern. Recent
   inputs still leave a trace in it, so it holds a short memory for free.
4. Downstream neurons (the readout) receive this pattern.
5. Only the synapses onto the readout change, using a local rule such as a delta rule
   or reward-modulated Hebbian learning.

**How to test it here.**
Inside the standard test loop:
1. Build two learners for Brain World: (a) a fixed random recurrent reservoir with a
   local, reward-modulated readout; (b) the same network with every weight plastic.
2. Note that Brain World already uses 1,000 fixed random expansion units with learned
   readouts. Use that as a third reference point, since it is a feed-forward reservoir.
3. Match unit counts and learning budgets. Train on the five-skill curriculum.
4. Metrics: episodes to pass each stage, final success rate, and transfer in the H101
   transfer setup.
5. Run at least 5 seeds per learner and compare means and spread.

**Counts against it if:** the reservoir with a local readout falls clearly short of the
fully plastic network in Brain World.

**Why it matters for a brain-like learner.** If fixed reservoirs suffice, a learner only
needs one cheap plastic layer, as in [reservoir-computing](../../simulation/reservoir-computing.md).
It is the opposite bet to the credit-assignment rows in section A, which assume deep
weights must learn.

## H139 - FORCE tames chaos into tasks

**Status:** open · **Tier:** T1 · **Source:** Sussillo & Abbott 2009, *Neuron*

**In simple words.** Some recurrent networks are *chaotic*: their activity never repeats
and is very sensitive to small pushes. FORCE learning takes such a network and feeds its
own output back into it. A fast learning rule changes the readout so quickly that the
output error stays tiny from the start. The feedback then pulls the chaos into a steady,
useful pattern, like a dancer locked onto a beat. The claim is that the brain uses
output feedback plus fast local learning in this way to produce patterns such as
movements.

**How it would work in the brain (if true).**
1. A recurrent circuit, for example in motor cortex, runs with rich, irregular activity.
2. A readout population produces the output, for example a motor command.
3. The output is fed back into the circuit through feedback connections.
4. A fast, local rule adjusts the readout weights to cut the error at every moment. The
   original FORCE uses a recursive least-squares rule that is not local; the claim needs
   a local version.
5. With the error kept small, the feedback stabilises the circuit into a repeating
   trajectory that produces the target pattern.

**How to test it here.**
Inside the standard test loop:
1. Build a small chaotic rate network in numpy (a few hundred units, random weights with
   gain above the chaos threshold).
2. Target: a periodic motor-like signal, for example a sum of sines, or a leg-pattern
   from the Brain World walking stage.
3. Train with three rules: original FORCE (recursive least squares), a local FORCE-like
   rule (for example a delta rule on the readout using only local error), and a plain
   readout without feedback as the baseline.
4. Metric: output error after training with learning switched off, and whether the
   pattern holds over long runs.
5. Run at least 5 seeds per rule.

**Counts against it if:** the local FORCE-like rule cannot learn the motor pattern.

**Why it matters for a brain-like learner.** FORCE shows how a fixed chaotic network can
be made useful, which makes it a stronger version of H138. If only the non-local rule
works, it does not help explain the brain.

## H140 - Memories and categories as attractors

**Status:** open · **Tier:** T1 · **Source:** Hopfield 1982, *PNAS*

**In simple words.** An *attractor* is a state a network falls into and stays in, like a
marble rolling into the bottom of a bowl. A Hopfield network stores memories as the
bottoms of many bowls. Start it near a memory, even with a noisy or partial cue, and it
rolls into the full memory. The claim is that memories and categories in the brain are
attractors: many similar inputs all roll into the same bowl, and that bowl *is* the
category.

**How it would work in the brain (if true).**
1. A recurrent network, for example hippocampal area CA3 or a cortical area, receives an
   input pattern.
2. Hebbian learning (neurons that fire together strengthen their link) makes the active
   neurons support each other. This carves a bowl around the pattern.
3. Many similar experiences carve one shared bowl.
4. Later, a partial or noisy cue starts activity inside the bowl.
5. Recurrent activity settles to the bowl's bottom: the stored memory, or the category
   prototype.

**How to test it here.**
Inside the standard test loop:
1. Record Brain World sensory states (retina, fovea, cochlea) over many episodes.
2. Train a Hopfield-style network on these states with a Hebbian rule. A modern variant
   with higher capacity can be a second model.
3. Present new states and let the network settle. Group states by which attractor they
   end in.
4. Metric: do the attractors line up with real categories (object colour, letter, tone)?
   Compare against k-means on the raw states as the baseline.
5. Run at least 5 seeds and several network sizes.

**Counts against it if:** the attractor net on Brain World states forms no categories.

**Why it matters for a brain-like learner.** Attractors give pattern completion and
categories almost for free. They link to memory rows in section F and to the
[memory-systems](../../function/memory-systems.md) account of CA3 as an auto-associator.

## H141 - Theta splits encoding from retrieval

**Status:** open · **Tier:** T1 · **Source:** Hasselmo, Bodelón & Wyble 2002, *Neural Comput*

**In simple words.** The hippocampus has a *theta rhythm*: a slow wave of activity, a few
cycles per second, seen when an animal explores (established). Learning something new
and recalling something old can get in each other's way. If recall runs while you learn,
you may store the old memory again instead of the new one. The claim is that each theta
cycle has two halves. One half is for taking in new input and storing it. The other half
is for recalling. It is like a two-way street with a traffic light, so traffic never
collides.

**How it would work in the brain (if true).**
1. The theta rhythm runs in the hippocampus during exploration (established).
2. In one phase, input from entorhinal cortex is strong and recurrent connections in CA3
   are weak. Synapses are in a state where they strengthen easily. New input is stored.
3. In the opposite phase, input is weaker and recurrent connections are strong. The
   network recalls stored patterns, and plasticity is low.
4. Because storage and recall alternate, recall does not overwrite or blur new memories.

**How to test it here.**
Inside the standard test loop:
1. Build a small associative memory (for example a Hopfield-style CA3 model) that learns
   a stream of patterns, some of them overlapping with older ones.
2. Model A: alternate phases with input-strong/plastic and recurrent-strong/non-plastic.
   Model B: same network with no phases (input, recall and learning all at once).
3. Metric: interference, measured as recall accuracy for new and old patterns after
   learning, and how many spurious mixed memories form.
4. Vary pattern overlap. Run at least 5 seeds per model.

**Counts against it if:** the phase-split model shows the same interference as the
unsplit one.

**Why it matters for a brain-like learner.** A clock that switches between "learn" and
"recall" is cheap to build. It links to H142, which uses the same rhythm for a
different job.

## H142 - Theta sequences compress behaviour for STDP

**Status:** open · **Tier:** T1 · **Source:** Skaggs et al. 1996, *Hippocampus*

**In simple words.** Place cells fire when an animal is in one spot. As the animal walks
through a cell's spot, the cell fires at an earlier and earlier point in each theta wave.
This is called *phase precession* (established). As a result, within one theta wave,
cells for places just behind, here, and just ahead fire in order, squeezed into a fraction
of a second. *STDP* (spike-timing-dependent plasticity) strengthens a link from cell A to
cell B when A fires just before B, within tens of milliseconds. Walking past a few places
takes seconds, too slow for STDP. The claim is that theta squeezes the sequence into the
time window STDP can use, like playing a slow film on fast-forward so it fits.

**How it would work in the brain (if true).**
1. The animal moves through places A, B, C over a few seconds.
2. Place cells for A, B, C fire with phase precession against theta (established).
3. Within each theta wave, A, B and C fire in order a few milliseconds apart.
4. STDP strengthens A to B and B to C, because each fires just before the next.
5. The learned chain lets the network replay or predict the path later.

**How to test it here.**
Inside the standard test loop:
1. Simulate an agent on a track or in Brain World with a population of place-like units.
2. Model A: units fire with phase precession against a theta oscillation. Model B: same
   firing rates without phase precession.
3. Apply the same STDP rule to recurrent weights in both.
4. Metric: how well the learned weights encode the order of places (for example, accuracy
   of predicting the next place from the weights, or replay order).
5. Run at least 5 seeds and several walking speeds.

**Counts against it if:** the model with phase precession gives no sequence-learning gain
over the one without.

**Why it matters for a brain-like learner.** It shows how a rhythm can bridge the gap
between the speed of behaviour and the speed of a learning rule. See
[timing-and-sequence-learning](../../function/timing-and-sequence-learning.md).

## H143 - Learning is best near criticality

**Status:** open · **Tier:** T1 · **Source:** Beggs & Plenz 2003, *J Neurosci*

**In simple words.** Think of a network where each active neuron triggers, on average,
some number of others. If it triggers less than one, activity dies out fast. If more than
one, activity explodes. Right at one, the network is *critical*: activity spreads in
cascades of all sizes, called neuronal avalanches. Beggs and Plenz reported such
avalanches in slices of cortex. The claim is that the brain sits near this critical
point on purpose, because there information travels furthest and learning works best.
It is like a pile of sand on the edge of sliding: small pushes can travel far.

**How it would work in the brain (if true).**
1. Each neuron's activity spreads to others through excitatory synapses.
2. Homeostatic processes (see H145, H146) tune the network's overall gain.
3. The gain settles near the critical point, where one spike causes about one more on
   average.
4. Signals then neither fade nor blow up, so input can affect activity far away.
5. Learning rules that depend on activity get the most useful signal in this regime.

**How to test it here.**
Inside the standard test loop:
1. Build a recurrent rate or spiking network in numpy with a global gain knob.
2. Measure how critical it is at each gain, for example from the branching ratio or the
   avalanche size distribution.
3. At each gain, train a readout (or a local learning rule) on a small task: a memory
   task, or a Brain World skill.
4. Metric: learning speed and final performance as a function of gain. Find the gain
   with the best learning.
5. Run at least 5 seeds per gain value.

**Counts against it if:** learning is not best near the critical point.

**Why it matters for a brain-like learner.** If true, a learner should be tuned to the
edge of chaos, which also matters for reservoirs (H138, H139). Whether real brains are
critical is still debated.

## H144 - Variability is sampling

**Status:** open · **Tier:** T1 · **Source:** Fiser et al. 2010, *Trends Cogn Sci*; Kappel et al. 2015, *PLoS Comput Biol*

**In simple words.** Neurons respond differently each time to the same input
(established). Usually this is seen as noise. The claim is that the variation is useful:
each moment of activity is a *sample*, one guess drawn from the brain's beliefs about
what is out there. Over time the samples show not only the best guess but also how
unsure the brain is. That is the core of *Bayesian* reasoning: keep track of
uncertainty and update it with evidence. Kappel et al. go further: synapses also wander,
sampling from a distribution of good weights.

**How it would work in the brain (if true).**
1. An input arrives that is ambiguous, for example a dim object.
2. Neural activity wanders over several possible interpretations from moment to moment.
3. How often each interpretation appears matches how likely the brain thinks it is.
4. Downstream areas and learning rules read the spread, not only the average.
5. Synapses learn in proportion to the uncertainty, and their own noise keeps them
   exploring good weight settings.

**How to test it here.**
Inside the standard test loop:
1. Build two small networks on the same task: a stochastic sampling network (for example
   a Boltzmann-machine-like net or Langevin-noise weights) and a matched deterministic net.
2. Use a task where uncertainty matters: noisy or ambiguous Brain World inputs, or a
   Tiny MLP task with label noise.
3. Metrics: calibration (do confidence levels match how often it is right?), learning
   speed, and performance on new data.
4. Run at least 5 seeds per network.

**Counts against it if:** the sampling net gives no better uncertainty estimates or
learning than the deterministic net.

**Why it matters for a brain-like learner.** A learner that knows how unsure it is can
explore and ask for more evidence. It links to H151, which also treats noise as useful.

## H145 - Inhibitory plasticity keeps E/I balance

**Status:** open · **Tier:** T1 · **Source:** Vogels et al. 2011, *Science*

**In simple words.** Neurons get two kinds of input: excitatory (push to fire) and
inhibitory (push to stay quiet). In cortex these are roughly balanced (established
background). When excitatory synapses learn, they can upset that balance, and the
network may run wild or fall silent. The claim is that inhibitory synapses learn too,
with their own rule, and keep tracking the excitation. It is like a thermostat that
follows the heater: whatever the heater does, the room stays at the right temperature.

**How it would work in the brain (if true).**
1. Excitatory synapses onto a neuron change through Hebbian learning, for example when it
   learns a new pattern.
2. The neuron's firing rate rises above a target value.
3. Inhibitory synapses onto that neuron strengthen when pre- and postsynaptic activity
   are high, and weaken when the neuron fires below its target.
4. Inhibition comes to match excitation for each input, so the neuron returns to its
   target rate.
5. With balance restored, excitatory learning can continue without runaway activity.

**How to test it here.**
Inside the standard test loop:
1. Build a small recurrent network in numpy with separate excitatory and inhibitory
   units. Excitatory synapses learn with a Hebbian rule.
2. Model A: inhibitory synapses learn with a Vogels-style rule. Model B: inhibitory
   synapses fixed.
3. Train on a stream of patterns, or on Brain World inputs.
4. Metrics: stability (firing rates stay in range over long runs) and learning
   (selectivity or task performance).
5. Run at least 5 seeds per model.

**Counts against it if:** the model without inhibitory plasticity learns as well and
stays stable.

**Why it matters for a brain-like learner.** Stability is a basic need for any learner
that never stops learning. H145, H146 and H147 are three stabilisers; this test helps
show which ones are needed.

## H146 - Synaptic scaling stops runaway Hebbian learning

**Status:** open · **Tier:** T1 · **Source:** Turrigiano et al. 1998, *Nature*

**In simple words.** Pure Hebbian learning has a known problem: stronger links make
neurons fire more, which makes links stronger still, and the weights run away
(established for the plain rule). Turrigiano and colleagues found that when activity
in cultured neurons goes up or down for a long time, all of a neuron's synapses scale
down or up together, by the same factor. This is *synaptic scaling*. The claim is
that this slow scaling is what keeps Hebbian learning in the brain from running away.
It is like turning down the overall volume while keeping the balance between
instruments.

**How it would work in the brain (if true).**
1. Hebbian learning strengthens some synapses on a neuron.
2. The neuron's average firing rate drifts above its set point over hours.
3. The neuron senses its own long-term activity.
4. It scales all its excitatory synapses down by the same factor. The relative pattern,
   which holds what was learned, stays the same.
5. Firing returns to the set point, and further Hebbian learning stays within bounds.

**How to test it here.**
Inside the standard test loop:
1. Build a small Hebbian network in numpy (for example one layer learning from Brain
   World sensory input or from synthetic patterns).
2. Model A: Hebbian learning plus slow multiplicative scaling toward a target rate.
   Model B: Hebbian learning alone. Optionally model C: Oja's rule, which normalises
   weights in a different way.
3. Run for a long time.
4. Metrics: do weights and rates stay bounded? Does the network still learn useful
   features (selectivity, readout accuracy)?
5. Run at least 5 seeds per model.

**Counts against it if:** the Hebbian net without scaling stays stable.

**Why it matters for a brain-like learner.** It is a cheap, local fix for a basic flaw of
Hebbian learning. It overlaps with H145 and H147; Oja's rule (in
[brain-inspired-learning-algorithms](../../learning/brain-inspired-learning-algorithms.md))
solves the same problem another way.

## H147 - BCM sliding threshold

**Status:** open · **Tier:** T1 · **Source:** Bienenstock, Cooper & Munro 1982, *J Neurosci*

**In simple words.** The BCM rule says a synapse gets stronger when the postsynaptic
neuron fires above a threshold, and weaker when it fires below it. The key part is that
the threshold slides: if the neuron has been very active lately, the threshold goes up, so
strengthening gets harder. If it has been quiet, the threshold goes down. It is like a
teacher who grades harder for a student who has been getting easy A's. The claim is that
this sliding threshold decides when activity strengthens or weakens a synapse in the
brain, and that it makes neurons become *selective*: each responds strongly to only some
inputs.

**How it would work in the brain (if true).**
1. A presynaptic input fires and the postsynaptic neuron responds.
2. If the response is above the neuron's current threshold, the synapse strengthens. If
   it is below but above zero, the synapse weakens.
3. The threshold tracks the neuron's recent average activity, rising when activity is
   high.
4. Inputs that drive the neuron hardest win, and the others fade.
5. The neuron ends up selective to a subset of input patterns, and activity stays bounded.

**How to test it here.**
Inside the standard test loop:
1. Collect Brain World sensory inputs (retina and fovea patterns).
2. Train a small layer of neurons with BCM, and a matched layer with Oja's rule.
3. Metric: selectivity of each neuron (for example, how sharply it responds to one class
   of input versus others), plus how useful the features are for a linear readout.
4. Run at least 5 seeds per rule.

**Counts against it if:** BCM and Oja give no difference in selectivity on Brain World
input.

**Why it matters for a brain-like learner.** BCM combines learning and stability in one
rule. If it adds selectivity that Oja lacks, it is the better default for unsupervised
feature learning; otherwise the simpler rule wins. Competes with H145 and H146 as the main
stabiliser.

## H148 - Astrocytes as slow, many-synapse memory

**Status:** open · **Tier:** T1 · **Source:** Kozachkov et al. 2023, *PNAS*

**In simple words.** Astrocytes are star-shaped glial cells. A single astrocyte touches
many synapses at once (established background, see
[glia-and-energy-budget](../../anatomy/glia-and-energy-budget.md)). Their internal
calcium signals are slower than spikes. The claim is that astrocytes add an extra,
slow memory layer that links many synapses together. Kozachkov et al. argue that a
network of neurons plus astrocytes can compute something like the *attention* used in
transformer AI models, and store more memories than neurons alone. Think of an
astrocyte as a manager who watches many conversations at once and can quietly change
how loud each one is.

**How it would work in the brain (if true).**
1. Many synapses fire, and the astrocyte that wraps them senses their activity.
2. The astrocyte's calcium level integrates this activity slowly, across many synapses.
3. The astrocyte releases signals that change the strength of those synapses together.
4. This creates interactions between synapses, not only between neurons. That adds
   memory capacity and can compute weighted mixtures similar to attention.

**How to test it here.**
Inside the standard test loop:
1. Build a small associative memory network in numpy, with a neuron-only version as
   baseline.
2. Add astrocyte units that each connect to many synapses and modulate them with a slow
   variable, following the Kozachkov et al. model.
3. Store more and more patterns and test recall from partial cues.
4. Metric: memory capacity (patterns stored before recall fails), at matched numbers of
   neurons and parameters.
5. Run at least 5 seeds and several network sizes.

**Counts against it if:** the neuron-astrocyte model shows no memory capacity gain.

**Why it matters for a brain-like learner.** If glia compute, a brain model with only
neurons misses part of the machine. It links to H140 (attractor memory capacity).

## H149 - Rewiring stores long-term memories

**Status:** open · **Tier:** T1 · **Source:** Holtmaat & Svoboda 2009, *Nat Rev Neurosci*

**In simple words.** Learning is usually modelled as turning the strength of existing
synapses up or down. But in the brain, small bumps called *dendritic spines* that carry
synapses also appear and disappear, and some new ones last a long time (established,
seen by imaging living animals). The claim is that adding and removing synapses, called
*structural plasticity*, is a key way to store long-term memories. It is like the
difference between turning knobs on a fixed mixing board and building new wires between
devices.

**How it would work in the brain (if true).**
1. An experience drives Hebbian activity between pairs of neurons.
2. Where an axon and a dendrite are close and active together, new spines and synapses
   form.
3. Synapses that are used are kept and stabilised; unused ones are removed.
4. The pattern of which neurons connect, not only how strongly, now holds the memory.
5. Because rewiring is slow and the kept synapses are stable, the memory lasts.

**How to test it here.**
Inside the standard test loop:
1. Build two associative memory networks in numpy with the same number of synapses
   allowed at any time.
2. Model A: weight-only learning on a fixed connection graph. Model B: rewiring, where
   weak synapses are removed and new ones are formed between co-active neurons, plus
   weight learning.
3. Store patterns one after another and test recall of old and new ones.
4. Metrics: capacity (patterns stored before recall fails) and retention of old patterns
   over time.
5. Run at least 5 seeds per model.

**Counts against it if:** the rewiring model gives no capacity gain over the weight-only
model.

**Why it matters for a brain-like learner.** Sparse, rewiring networks could store more
per synapse and keep old memories safe. It links to memory rows in section F and to
pruning during development (section E).

## H150 - Myelination learns timing

**Status:** open · **Tier:** T1 · **Source:** Fields 2015, *Nat Rev Neurosci*

**In simple words.** Myelin is a fatty wrapping on axons that makes signals travel faster
(established). How much myelin an axon has can change with activity and experience.
Changing myelin changes how long a signal takes to get from one area to another. The
claim is that the brain uses this to tune timing, so signals from different areas
arrive together when they need to. That would be a kind of learning that changes delays,
not synapse strengths. It is like adjusting the length of pipes so water from several
taps reaches a bucket at the same moment.

**How it would work in the brain (if true).**
1. Two areas send signals to a third that must combine them, for example to detect
   coincidences.
2. The signals arrive out of step, so the combination works poorly.
3. Activity in the axons signals glial cells (oligodendrocytes) to add or adjust myelin.
4. Conduction speed changes, so the delays shift.
5. Signals now arrive in step, and the downstream computation improves.

**How to test it here.**
Inside the standard test loop:
1. Build a small spiking or rate model in numpy where several inputs travel with delays
   to a coincidence-detecting neuron.
2. Task: a timing task, for example detect a specific interval or synchronise two input
   streams.
3. Model A: delays learn by an activity-dependent rule. Model B: fixed random delays,
   with weights learning in both.
4. Metric: task accuracy and learning speed.
5. Run at least 5 seeds per model.

**Counts against it if:** the delay-learning model gives no gain over fixed delays on the
timing task.

**Why it matters for a brain-like learner.** Delays are a parameter almost no AI model
learns. If they matter, spiking learners (see
[spiking-neural-networks](../../simulation/spiking-neural-networks.md)) should learn them
too. It links to H142 (timing for STDP).

## H151 - Transmission failures act like dropout

**Status:** open · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** When a spike reaches a synapse, the synapse often fails to release
any transmitter at all (established: release is probabilistic). In machine learning,
*dropout* is a trick where random units are switched off during training. It stops the
network from leaning too hard on a few units, so it generalises better to new data
instead of memorising the training set (*overfitting*). The claim is that random
synaptic failures do the same job in the brain. It is like a team that practises with
random players missing, so no one player becomes a single point of failure.

**How it would work in the brain (if true).**
1. A presynaptic neuron fires a spike.
2. Each of its synapses releases transmitter only with some probability; often it fails
   (established).
3. Over many trials, a downstream neuron sees a different random subset of its inputs
   each time.
4. Learning rules adjust weights based on these noisy inputs, so no single input becomes
   essential.
5. The learned representation is more robust and generalises better to new situations.

**How to test it here.**
Inside the standard test loop:
1. Use the Tiny MLP on a small task with limited training data, so overfitting is
   possible. Optionally repeat in Brain World with the H101 transfer setup.
2. Model A: each synapse transmits with a fixed probability below one during training.
   Model B: all synapses always transmit. Also compare with standard unit dropout.
3. Rescale so expected input matches across models.
4. Metric: generalisation gap (train minus test performance) and test performance.
5. Run at least 5 seeds and a few failure probabilities.

**Counts against it if:** the net with random transmission failure shows no
generalisation gain over the net without.

**Why it matters for a brain-like learner.** If failures regularise, a brain-like learner
gets a regulariser for free. It links to
H144, which also treats variability as useful rather than as noise.
