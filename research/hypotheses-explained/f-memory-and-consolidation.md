# F. Memory, consolidation and forgetting, explained

Part of [the 170 hypotheses, explained simply](README.md). Main table and status:
[learning-algorithm-hypotheses.md](../learning-algorithm-hypotheses.md). Every row is a
**hypothesis**, not an established fact.

## The big idea of this group

A learner that keeps learning new things tends to overwrite old ones. In artificial
networks this is called **catastrophic forgetting**: train on task B and task A is lost.
Brains seem to forget much less. Some background is **established**: the hippocampus
stores new episodes fast, the cortex learns slowly, and during sleep the hippocampus
replays recent experience (see [memory-systems](../../function/memory-systems.md) and
[sleep-and-memory-consolidation](../../function/sleep-and-memory-consolidation.md)). What
each row below **claims** is a specific trick that explains how memories are kept,
updated or forgotten on purpose. Some tricks act on the whole network (replay H093, H101,
H104, H105; sleep downscaling H094), some inside each synapse (tagging H095, hidden
timescales H096, importance H097, reconsolidation H098), and some on the code itself
(attention-like memory H099, fast weights H100, silent working memory H102, new neurons
H106, sparse expansion H107, context gating H108). They can combine, but they also
compete for the same job: if replay alone stops forgetting, the synapse-level tricks
matter less, and the reverse. H101 and H103 are this repo's main transfer tests and tie
the group to the [game/world](../../game/world/) creature.

## H093 - Generated replay prevents forgetting
**Status:** open · **Tier:** T1 · **Source:** van de Ven, Siegelmann & Tolias 2020, *Nat Commun*; Shin et al. 2017, NeurIPS

**In simple words.** To avoid forgetting, you could keep a diary of everything and reread
it. That takes a lot of storage. This idea says the brain does not keep the diary. It
keeps a model that can *make up* realistic past experiences, and it practises on those
made-up memories. A **generative model** is a network that has learned to produce new
examples that look like the ones it was trained on. **Replay** means re-presenting past
experience to the learner while it learns something new.

**How it would work in the brain (if true).**
1. The hippocampus replays recent experience during sleep and rest (established).
2. The claim: what is replayed is not an exact copy. It is a sample generated from a
   learned model of past experience, possibly at the level of internal features rather
   than raw senses.
3. The cortex learns the new task from real input during the day.
4. During offline periods it trains on the generated samples, mixed with new ones.
5. Old skills stay intact because the old input patterns keep being "seen", without
   storing them.

**How to test it here.**
Inside the standard test loop:
1. Build a small numpy classifier (Tiny MLP style) on a synthetic dataset of 10 Gaussian
   clusters, split into 5 tasks of 2 classes each, learned one task after another.
2. Add a simple generator: per-class Gaussian fitted to the hidden-layer activity
   (cheap stand-in for replay of internal features).
3. Compare three arms: generated replay, exact replay from a small stored buffer, and no
   replay. Keep the number of replay samples per step equal.
4. Metric: mean accuracy over all 10 classes after the last task, in the harder setting
   where the task identity is not given at test.
5. Run at least 5 seeds per arm.

**Counts against it if:** generated replay protects no better than no replay at all.

**Why it matters for a brain-like learner.** It would let a learner keep old skills
without a growing store of raw episodes. It links to H101, H104 and H164, which all
lean on replay, and competes with the synapse-level tricks H096 and H097.

## H094 - Sleep scales all synapses down
**Status:** open · **Tier:** T1 · **Source:** Tononi & Cirelli 2014, *Neuron*

**In simple words.** This is the **synaptic homeostasis hypothesis** (SHY). While awake,
learning mostly makes synapses stronger. That costs energy and leaves less room to learn.
During deep sleep, the idea says, every synapse is turned down a bit, like lowering the
volume on every instrument in a band. Weak, noisy synapses fall close to zero, while the
strong ones that carry real memories stay clearly above them. The memory becomes clearer
against the background ("signal-to-noise").

**How it would work in the brain (if true).**
1. Waking learning strengthens many synapses, some for real memories, some by chance.
2. Slow-wave sleep (deep, non-dreaming sleep) has large, slow oscillations in cortex
   (established).
3. The claim: during slow-wave sleep each neuron scales its synapses down, keeping their
   relative sizes.
4. Synapses that fall below a threshold are weakened further or removed.
5. The next day starts with headroom for new learning, and the strongest traces stand
   out more.

**How to test it here.**
Inside the standard test loop:
1. Use Tiny MLP trained on a sequence of 3-5 small tasks.
2. Between tasks, add an offline "sleep" step: multiply all weights by a factor below 1,
   then zero any weight under a small threshold. Pure multiplication alone does not
   change which unit wins, so the threshold (or a nonlinearity) is what can matter.
3. Baseline: identical training with no sleep step. A second control: random pruning of
   the same number of weights.
4. Metric: accuracy on all earlier tasks after the last task (forgetting), plus
   speed of learning each new task.
5. Sweep the factor and threshold coarsely, at least 5 seeds each. Link the result to
   issue #84.

**Counts against it if:** the downscaling step gives no less forgetting than no
downscaling (issue #84).

**Why it matters for a brain-like learner.** If true, a cheap global step between
learning sessions improves memory, with no replay needed. It may work with replay
(H093) rather than against it; the repo's sleep topic notes that some synapses grow
during sleep, which this rule does not explain.

## H095 - Only tagged synapses keep their changes
**Status:** open · **Tier:** T1 · **Source:** Frey & Morris 1997, *Nature*

**In simple words.** Most small things that happen in a day are forgotten. But if
something important happens soon before or after, ordinary details nearby can be
remembered too. **Synaptic tagging and capture** explains this at the level of one
synapse. A change at a synapse first leaves a temporary "sticky note" (the **tag**).
The change only becomes permanent if building materials (new proteins) arrive while the
note is still there. A strong or important event makes those proteins, and any tagged
synapse nearby can grab them.

**How it would work in the brain (if true).**
1. A weak input changes a synapse a little. This early change fades within hours
   unless it is stabilized.
2. The change also sets a local tag that lasts a limited time.
3. A strong or novel event, possibly signalled by dopamine or noradrenaline, makes the
   neuron produce plasticity proteins.
4. Tagged synapses capture those proteins and convert their early change into a
   lasting one. In hippocampal slices, this capture across synapses was shown by Frey &
   Morris (established as a slice result).
5. The claim: this rule decides which everyday memories last, based on what happened
   near them in time.

**How to test it here.**
Inside the standard test loop:
1. Build a numpy associative memory where each weight has two parts: a fast early part
   that decays, and a stable late part.
2. Any change larger than a threshold sets a decaying tag. A global "protein" signal
   fires only on rare "important" events (for example large reward).
3. While both tag and protein are present, move the early part into the late part.
4. Baseline: a plain rule where all changes decay at the same rate (and a second one
   where all changes are kept).
5. Present a stream of weak items, with a few important events. Metric: retention of
   items near an important event versus items far from one, after a long delay.
6. At least 5 seeds; vary the tag lifetime.

**Counts against it if:** the tag-and-capture model shows no selective retention compared
with a plain rule.

**Why it matters for a brain-like learner.** It gives a cheap way to decide *what* to
keep, using a third, global signal. It links to the three-factor rules of section B and
to H097, which also decides what to protect.

## H096 - Synapses with many hidden timescales
**Status:** open · **Tier:** T1 · **Source:** Fusi, Drew & Abbott 2005, *Neuron*; Benna & Fusi 2016, *Nat Neurosci*

**In simple words.** A synapse that changes easily learns fast but forgets fast. A
synapse that changes slowly keeps memories but learns slowly. This idea says each synapse
has several hidden internal states, each changing at a different speed. Picture a row of
connected water tanks: water poured into the first small tank slowly leaks into bigger,
slower tanks. New learning lands in the fast tank, and old learning lives on in the slow
ones. The visible weight is only the first tank.

**How it would work in the brain (if true).**
1. A synapse cannot grow without limit, and its biochemistry has many processes that
   run at different speeds (established).
2. The claim: these processes form a chain. A learning event changes the fastest one.
3. Each variable passes part of its change to the next, slower one.
4. Slow variables pull the fast ones back toward old values.
5. As a result, memories fade slowly, along a long tail, instead of being wiped out
   by a few new ones, so more memories can be kept with the same synapses.

**How to test it here.**
Inside the standard test loop:
1. Build a numpy network of N synapses (for example a single readout neuron) that stores
   a stream of random binary patterns, one per step.
2. Arm 1: simple synapse, one bounded variable. Arm 2: a cascade (Fusi 2005) or a chain
   of coupled variables (Benna & Fusi 2016), with the same N.
3. For each stored pattern, track the signal-to-noise ratio of its recall as more
   patterns arrive.
4. Metric: memory lifetime, the age at which a memory's signal-to-noise falls below a
   fixed level. Also the initial signal of a new memory.
5. Repeat for a few values of N and at least 5 seeds.

**Counts against it if:** the cascade synapse gives the same memory lifetime as the
simple synapse.

**Why it matters for a brain-like learner.** It would let each synapse solve the
learn-fast-but-keep-old problem by itself, with no replay. It competes with replay
(H093) and with importance weighting (H097) as the main defence against forgetting.

## H097 - Synapses estimate their own importance
**Status:** open · **Tier:** T1 · **Source:** Kirkpatrick et al. 2017, *PNAS*; Zenke, Poole & Ganguli 2017, ICML

**In simple words.** Some connections matter a lot for a skill you already have; others
hardly matter. If each synapse knew how important it was, the important ones could
become stiff and the rest stay free for new learning. **EWC** (elastic weight
consolidation, Kirkpatrick) computes importance with a global calculation (the **Fisher
matrix**, a measure of how much the output changes when a weight moves). **Synaptic
intelligence** (Zenke) lets each synapse add up, during learning, how much its own
changes helped. The question is whether the local version works nearly as well.

**How it would work in the brain (if true).**
1. While learning, each synapse changes and the error or reward changes.
2. The claim: a local variable at the synapse keeps a running sum of how much its
   own changes lowered the error.
3. At the end of a task (or during sleep) this sum becomes the synapse's importance.
4. Later changes are scaled down in proportion to that importance, so important
   synapses resist change.
5. Molecular "stiffness" (for example larger, more stable spines) would be the physical
   form of importance.

**How to test it here.**
Inside the standard test loop:
1. Use Tiny MLP on 5 tasks in a row (for example the same input with a different fixed
   random permutation per task).
2. Arms: plain training; EWC with a diagonal Fisher matrix; synaptic intelligence; and a
   fully local estimate such as a running average of |weight change|.
3. Tune the strength of the stiffness term on a held-out task for each arm.
4. Metric: mean accuracy over all tasks after the last one.
5. At least 5 seeds per arm, same compute.

**Counts against it if:** the local importance estimate is much worse than EWC with a
Fisher matrix.

**Why it matters for a brain-like learner.** If a local estimate is enough, a brain-like
learner can protect old skills with no global computation. It combines naturally with
context gating (H108, Masse et al. used both) and competes with H096 and replay.

## H098 - Retrieval makes memories changeable again
**Status:** open · **Tier:** T1 · **Source:** Nader, Schafe & LeDoux 2000, *Nature*

**In simple words.** We tend to think of a stored memory as fixed. **Reconsolidation**
says that when you recall a memory, it becomes soft again for a while, like clay taken
out of the kiln. During that time it can be changed, strengthened or even weakened, and
then it is stored again. The claim here is that this is useful: it lets you update old
knowledge in place, instead of keeping an old copy and a new copy that conflict.

**How it would work in the brain (if true).**
1. A memory is stored and consolidated.
2. A reminder makes you retrieve it.
3. In rats, blocking protein synthesis in the amygdala right after a fear memory was
   recalled weakened that memory later (Nader et al. 2000, an experimental result; how
   general it is remains debated).
4. The claim: retrieval makes the memory labile only when what happens next differs from
   what the memory predicts.
5. The memory is rewritten to include the new information, then stabilized again.
6. Later recall gives the updated version, not a mix of old and new.

**How to test it here.**
Inside the standard test loop:
1. Build a small numpy key-value memory (for example "object → location"), with a
   learned readout.
2. After learning, change the true value for some keys, keep others the same.
3. Arm A, retrieve-then-update: when a key is recalled and the outcome mismatches, its
   stored value is overwritten or blended. Arm B, append-only: a new entry is added and
   the old one stays.
4. Metrics: accuracy on changed keys after each change, accuracy on unchanged keys, and
   memory size.
5. Several rounds of change, at least 5 seeds.

**Counts against it if:** the retrieve-then-update model adapts no better than the
append-only model.

**Why it matters for a brain-like learner.** It would give a learner a way to keep its
knowledge current without its memory store growing forever. The risk it brings is
overwriting good memories, which H095 and H097 try to guard against.

## H099 - Hippocampus as attention over stored patterns
**Status:** open · **Tier:** T1 · **Source:** Ramsauer et al. 2021, ICLR; Whittington, Warren & Behrens 2022, ICLR

**In simple words.** A **Hopfield network** is a memory that rebuilds a whole stored
pattern from a part of it, like recognising a song from three notes. A **modern
Hopfield network** does this with a sharper rule: it compares the cue with every stored
pattern, gives most weight to the best match, and returns a weighted mix. That is the
same maths as **attention** in transformers (the networks behind chatbots). The claim is
that the hippocampus works this way.

**How it would work in the brain (if true).**
1. Area CA3 of the hippocampus has many recurrent connections and is the classic
   candidate for pattern completion (established as the standard model).
2. A partial cue arrives from the cortex.
3. The claim: the cue is compared with all stored memories at once (the "keys").
4. Strong competition, for example through inhibition, lets the best match win almost
   alone (like a softmax).
5. The winning memory's content (the "value") is sent back to the cortex.
6. In Whittington and colleagues' model, the stored items are tied to positions in a
   learned map, so the same machinery supports navigation.

**How to test it here.**
Inside the standard test loop:
1. Start simple: store K random patterns in a numpy classic Hopfield net (Hebbian outer
   products) and in a modern Hopfield memory (softmax over stored patterns).
2. Cue with noisy or partial patterns; metric: recall accuracy as K grows.
3. Then in Brain World: give the creature a memory that stores each new object-location
   pair once and recalls it by similarity.
4. Baseline: the same creature with only its slow learned weights.
5. Metric: success on the first repeat of a new layout (one-shot recall), at least 5
   seeds.

**Counts against it if:** the Hopfield-memory agent shows no one-shot recall advantage.

**Why it matters for a brain-like learner.** It would give a clean, buildable design for
the fast episodic store. It links to H100 (another fast memory) and to the
[memory-systems](../../function/memory-systems.md) Hopfield code.

## H100 - Fast weights store recent context
**Status:** open · **Tier:** T1 · **Source:** Ba et al. 2016, NeurIPS

**In simple words.** A network normally has one set of weights that changes slowly.
**Fast weights** add a second set that changes quickly and fades quickly, like writing on
a whiteboard that wipes itself after a few minutes. The fast set records what was just
seen together, so the network can link a name with a face it saw seconds ago. This is
called **binding**: holding together things that belong together, for now.

**How it would work in the brain (if true).**
1. Synapses change for a short time after use, through short-term facilitation and
   depression lasting up to seconds (established).
2. The claim: these short-term changes act as a second weight set laid on top of the
   long-term weights.
3. When two items are active together, the fast weight between them grows (a Hebbian
   step, "fire together, wire together").
4. The fast weights decay within seconds.
5. A later cue spreads through the fast weights and brings back what it was paired with.

**How to test it here.**
Inside the standard test loop:
1. Use the associative recall task: a sequence of key-value pairs, then a key, and the
   network must output its value.
2. Arm A: a small numpy RNN with fast weights, A ← λA + η·h·hᵀ, used inside each step.
3. Arm B: a plain RNN with the same number of slow parameters.
4. Train both the same way (backprop through time is fine here, sizes small).
5. Metric: recall accuracy as the number of pairs grows; at least 5 seeds.

**Counts against it if:** the fast-weight net gives no gain over a plain RNN on
associative recall.

**Why it matters for a brain-like learner.** It would give a cheap short-term binding
memory that uses synapses, not firing. It is closely linked to H102 (silent working
memory) and to H099, whose attention maths is related to fast weights.

## H101 - Main transfer experiment: local rule plus replay
**Status:** weakened (one setup: new object colours; see the results log) · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** **Transfer** means using what you learned in one place to learn
faster in a new place that has the same structure but looks different. Backprop (the
standard training method of deep networks, which needs a global error signal) is good at
this. A brain cannot easily run backprop. This row asks: with the same network size, can
a **local rule** (each synapse changes using only what is nearby, plus a reward signal)
combined with replay transfer as well?

**How it would work in the brain (if true).**
1. Dopamine carries a reward prediction error to many synapses (established).
2. Each synapse changes from its own activity and that error (a three-factor rule).
3. The hippocampus stores episodes and replays them offline (established that replay
   happens).
4. The claim: replay mixes episodes from different layouts, so the local rule sees the
   shared structure many times and the surface details average out.
5. The learned features then carry over to a new layout, which needs only a few
   episodes.

**How to test it here.**
Inside the standard test loop:
1. Use the **H101 transfer setup** in Brain World.
2. Arm A: the creature's existing local actor-critic rule (traces × dopamine, no
   backprop) with replay. Arm B: the same rule without replay. Arm C: the same network
   and parameter count trained with backprop.
3. Give all arms the same number of training episodes on the training layouts.
4. Metric: episodes to reach a fixed criterion on each new layout.
5. At least 5 seeds per arm. Report the gap between A and C.

**Counts against it if:** in episodes to criterion on a new layout, local plus replay
stays far behind backprop.

**Why it matters for a brain-like learner.** It is the repo's central test of whether
brain-like rules can reach deep-learning transfer. H164 and H170 build on it, H103 asks
whether priors matter more, and H001-type rows (section A) offer other rules to plug in.

## H102 - Silent working memory in synapses
**Status:** open · **Tier:** T1/T3 · **Source:** Mongillo, Barak & Tsodyks 2008, *Science*

**In simple words.** **Working memory** is holding something in mind for a few seconds,
like a phone number. The classic view is that neurons keep firing to hold it. This idea
says the item can be held *silently*: a short-lived change in the synapses keeps it,
while the neurons go quiet. It is like leaving a fingerprint on a glass instead of
holding the glass.

**How it would work in the brain (if true).**
1. An item is shown, and a group of prefrontal neurons fires.
2. Short-term **facilitation** boosts these neurons' synapses for about a second: the
   presynaptic terminal keeps extra calcium, so the next spike releases more
   transmitter (short-term facilitation is established).
3. The claim: firing can stop, and the item stays stored in this facilitation.
4. Brief, occasional bursts of the group refresh the trace before it fades.
5. A later cue, or any nonspecific input, reactivates the facilitated group and brings
   the item back, even after a distractor.

**How to test it here.**
Inside the standard test loop:
1. T1: build a small numpy rate or spiking network with Tsodyks-Markram short-term
   synapses (a facilitation variable and a depression variable per synapse).
2. Load one of several items, let firing return to baseline, present a distractor item,
   then give a nonspecific "ping".
3. Baseline: a persistent-activity attractor network with the same number of units.
4. Metric: recall accuracy after the delay, as distractor strength grows; at least 5
   seeds.
5. T3 part: a lab would need recordings showing the item is not decodable from firing
   during the delay, yet comes back after a ping, and that disrupting facilitation
   removes it.

**Counts against it if:** the silent-memory model cannot hold items across a distractor.

**Why it matters for a brain-like learner.** Silent storage would make working memory
cheaper in energy and harder to disrupt. It is the brain version of H100, and the repo's
[attention-and-working-memory](../../function/attention-and-working-memory.md) topic
discusses it as a hypothesis.

## H103 - Built-in priors beat better rules
**Status:** open · **Tier:** T1 · **Source:** **new** (links to Zador 2019 and issue #83)

**In simple words.** A **prior** is something the learner knows or assumes before
learning, built into its wiring. For example, a network that is built to treat an
object the same wherever it appears needs fewer examples. This row asks which helps
transfer more: a smarter learning rule, or a better built-in structure. Zador (2019)
argued that much of animal behaviour comes from wiring shaped by evolution, not from
learning.

**How it would work in the brain (if true).**
1. Genes specify wiring rules, not every synapse (established in broad terms).
2. The claim: these rules build in structure such as maps of space, objects as separate
   things, and repeated circuits across cortex.
3. Learning then only fills in details within that structure.
4. Because the structure already matches the world, a new layout that shares the
   structure needs little new learning, even with a simple local rule.

**How to test it here.**
Inside the standard test loop:
1. Use the **H101 transfer setup**.
2. Base learner: local rule, no extra prior. Arm "prior": same rule plus one built-in
   structure (for example an egocentric map or a shared detector per object slot).
   Arm "rule": no prior, but a better rule (backprop).
3. Match compute: same parameter count and number of training episodes.
4. Metric: episodes to criterion on new layouts; report how much of the gap between the
   base learner and the best arm each change closes.
5. At least 5 seeds; feed the result to issue #83.

**Counts against it if:** at equal compute, the better rule closes more of the gap than
the prior does.

**Why it matters for a brain-like learner.** It tells you where to spend design effort:
on the rule or on the architecture. It competes with section A's rule rows and links to
H084, H091 and H170.

## H104 - Overlapping replay builds schemas
**Status:** open · **Tier:** T1 · **Source:** Lewis & Durrant 2011, *Trends Cogn Sci*

**In simple words.** A **schema** is the common pattern behind many experiences, like
"restaurants: sit, order, eat, pay". You do not learn it from any one visit. This idea
says that during sleep, the brain replays several related memories together. The parts
they share get reinforced each time, the parts that differ do not, so the common pattern
stands out and becomes the schema.

**How it would work in the brain (if true).**
1. Several episodes are stored in the hippocampus, each with its own details.
2. Replay happens during sleep (established).
3. The claim: replay events often activate more than one episode at a time.
4. Neurons that code shared elements are active in many replay events, so their
   connections in cortex grow more than those for unique details.
5. The cortex ends up with a compact model of what the episodes share, which speeds
   learning of a new episode with the same structure.

**How to test it here.**
Inside the standard test loop:
1. Make episodes that share a hidden structure but differ in surface features (for
   example the same relative layout with different objects), in Brain World or a
   smaller numpy grid task.
2. Arm A: replay that mixes two or more stored episodes per replay event. Arm B: replay
   of one episode at a time. Arm C: no replay. Same number of replay steps in A and B.
3. Metric: episodes to criterion on a new episode with the same structure (schema
   transfer). Also check whether hidden units code the shared structure.
4. At least 5 seeds per arm.

**Counts against it if:** overlapping replay gives no more schema transfer than
single-episode replay.

**Why it matters for a brain-like learner.** It would turn replay from a defence against
forgetting into a tool for abstraction. It is the mechanism behind H164 and a likely part
of H101 and H105.

## H105 - Sleep produces insight
**Status:** open · **Tier:** T1 · **Source:** Wagner et al. 2004, *Nature*

**In simple words.** Sometimes you "sleep on" a problem and wake up seeing the answer.
Wagner and colleagues reported this with a number task that had a hidden shortcut: more
people found the shortcut after a night of sleep than after the same time awake. The
hypothesis is that sleep does more than store memories; offline replay can reorganise
them so that a hidden rule becomes visible.

**How it would work in the brain (if true).**
1. While awake, you practise a task step by step and store the episodes.
2. During sleep, the hippocampus replays them (established that replay happens).
3. The claim: replay is not an exact rerun. It mixes and reorders parts of episodes.
4. The mixing exposes a regularity that the step-by-step practice hid (for example,
   that one step always gives the final answer).
5. The cortex picks up that regularity, and after waking you use the shortcut.

**How to test it here.**
Inside the standard test loop:
1. Build a numpy version of a task with a hidden shortcut: a sequence of steps where
   the final answer always equals an early intermediate answer.
2. Train a small learner to do the steps. Then give arm A an offline phase of replay of
   stored episodes, possibly mixed (see H104).
3. Arm B (awake control): the same amount of time and compute, but no offline phase
   (either a pause or continued normal practice, run both).
4. Metric: fraction of seeds that switch to the shortcut, and how soon after the
   offline phase.
5. At least 10 seeds per arm, since the outcome is yes or no per run.

**Counts against it if:** the model with an offline replay phase shows no rule-discovery
advantage.

**Why it matters for a brain-like learner.** It suggests offline phases should be built
in on purpose, for discovery, not only for keeping memories. It builds on H104 and is
part of the replay family with H093 and H101.

## H106 - New neurons keep similar memories apart
**Status:** open · **Tier:** T1 · **Source:** Sahay et al. 2011, *Nature*

**In simple words.** Two very similar memories, like where you parked today and
yesterday, can blur together. **Pattern separation** means making similar inputs get
quite different codes, so they do not interfere. In some animals new neurons are born
in adulthood in the **dentate gyrus**, the entry stage of the hippocampus. Sahay and
colleagues increased the number of new neurons in mice and reported better separation of
similar contexts. The claim is that adding new units is a general way to reduce
interference.

**How it would work in the brain (if true).**
1. Adult neurogenesis in the dentate gyrus is established in rodents; in adult humans
   it is disputed (see
   [brain-development-and-critical-periods](../../function/brain-development-and-critical-periods.md)).
2. Young neurons are more excitable and more plastic than mature ones for a few weeks.
3. The claim: a new memory is mostly encoded by the young neurons available at that
   time.
4. Memories from different periods therefore use partly different neurons, so they
   overlap less.
5. Mature neurons become stable, protecting the older memories.

**How to test it here.**
Inside the standard test loop:
1. Build a numpy dentate-like layer: an expansion from input to a larger sparse layer,
   then a readout or a Hopfield store.
2. Arm A: start with fewer units and add new, highly plastic units before each new
   batch of memories; older units become less plastic.
3. Arm B: fixed units, the same final number from the start.
4. Store several batches of similar patterns. Metric: recall errors on old patterns
   after new similar ones are stored, and discrimination of near-identical pairs.
5. At least 5 seeds; vary how similar the batches are.

**Counts against it if:** the add-new-units model gives no less interference than fixed
units.

**Why it matters for a brain-like learner.** It suggests growing the network over time,
not only training a fixed one. It is a cousin of H107 (expansion) and H108 (different
units per task).

## H107 - Sparse random expansion for one-shot learning
**Status:** open · **Tier:** T1 · **Source:** Dasgupta, Stevens & Navlakha 2017, *Science*

**In simple words.** In the fly's smell system, a small number of input neurons connect
at random to a much larger number of **Kenyon cells** in the **mushroom body**. Only the
most active few Kenyon cells stay on. This turns each smell into a sparse "tag": a few
active cells out of many. Similar smells get similar tags, different smells get very
different ones. With such tags, learning a new smell from one exposure, or finding the
most similar stored smell, becomes easy.

**How it would work in the brain (if true).**
1. Olfactory input arrives from a small set of projection neurons (established).
2. Each Kenyon cell receives a few random inputs from them (established for the fly).
3. Inhibition lets only the most strongly driven Kenyon cells fire (established that
   activity is sparse).
4. The claim: this sparse, high-dimensional code is what makes one-shot learning and
   similarity search work.
5. A single reward or punishment changes the output synapses of the few active cells,
   which is enough to learn the smell's meaning.

**How to test it here.**
Inside the standard test loop:
1. Make a small synthetic dataset of classes with noisy examples.
2. Arm A: fixed sparse random expansion to a larger layer, keep the top few percent
   active. Arm B: dense random layer of the same size, no sparsity. Arm C: raw input.
3. One-shot test: store one example per class, classify new examples by the readout or
   by nearest stored code. Also measure nearest-neighbour search precision.
4. Metric: one-shot accuracy and search precision, at least 5 seeds.
5. Brain World already uses a fixed random expansion layer, so it can serve as a second
   check later.

**Counts against it if:** the random-expansion layer gives no one-shot gain over a dense
layer.

**Why it matters for a brain-like learner.** It is a cheap, learning-free front end that
makes fast learning easy. It links to H106 (pattern separation) and H108 (sparse codes
reduce overlap between tasks), and to the cerebellum-like circuits in
[comparative-and-evolutionary-neuroscience](../../anatomy/comparative-and-evolutionary-neuroscience.md).

## H108 - Context gating per task
**Status:** open · **Tier:** T1 · **Source:** Masse, Grant & Freedman 2018, *PNAS*; Iyer et al. 2022, *Front Neurorobot*

**In simple words.** If every task uses every neuron, learning a new task disturbs the
old ones. **Context gating** means a signal that says "now you are doing task 3" switches
off part of the network, so each task mostly uses its own subset of neurons. It is like
a shared office where each team has its own desks. Iyer and colleagues did a similar
thing with model **dendrites** (the input branches of a neuron), which respond to the
context and turn the neuron up or down.

**How it would work in the brain (if true).**
1. Prefrontal cortex holds the current task or rule (established in broad terms).
2. The claim: this context signal reaches other areas and inhibits a different subset
   of neurons for each task, or it acts through dendrites that gate a neuron's output.
3. Learning only changes synapses of neurons that are active, so each task changes
   mostly its own subset.
4. Shared neurons still allow some reuse between tasks.
5. Switching tasks switches the gate, and the old task's subset is found intact.

**How to test it here.**
Inside the standard test loop:
1. Use Tiny MLP on many tasks in a row (for example 10 or more input permutations).
2. Arm A: a fixed random gate per task that switches off a large share of hidden
   units. Arm B: no gating. Arm C: gating plus synaptic importance (H097), as in Masse
   et al.
3. Same network size and training per task.
4. Metric: mean accuracy over all tasks after the last one; at least 5 seeds.
5. Brain World already gates a random half of its expansion units per skill, so the
   same comparison can be repeated there with gating switched off.

**Counts against it if:** context gating gives the same forgetting as no gating across
many tasks.

**Why it matters for a brain-like learner.** It is a simple, local way to stop
interference, and it costs nothing if the task is known. Its weak point is that the
learner must know or infer the task. It combines with H097 and overlaps with H106 and
H107.
