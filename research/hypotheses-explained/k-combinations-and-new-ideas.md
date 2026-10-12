# K. Combinations and new ideas from this thread, explained

Part of [the 170 hypotheses, explained simply](README.md). Main table and status:
[learning-algorithm-hypotheses.md](../learning-algorithm-hypotheses.md). Every row is a
**hypothesis**, not an established fact.

## The big idea of this group
The earlier sections list single mechanisms. This section asks how they fit together to
give **abstraction**: learning the structure of a task so it transfers to new situations
that look different on the surface. Every row here is **new**: it came from this research
thread and has no published source, so it is a guess to test, not a finding. The
background they build on is established in parts: Hebbian and homeostatic plasticity
exist, dopamine signals reward-prediction errors, the hippocampus replays experience
during rest and sleep. The rows then make claims about which pieces are enough or
necessary. H162 and H164 say "few pieces are enough", while H170 says "all four main
pieces are needed". H163 and H168 are about where abstraction lives (fast activity vs slow
weights). H165, H166 and H167 each name one extra factor (sparsity, width, curiosity).
H169 is about how to judge rules at all. Most tests use the **H101 transfer setup**.

## H162 - Four rule types plus a switch suffice
**Status:** open · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** Think of a kitchen with only four tools: a knife, a pot, a pan and an
oven. The claim is that you can cook anything if a good cook decides which tool to use
when. Here the four tools are learning-rule types: **Hebbian** (strengthen synapses whose
two neurons fire together), **anti-Hebbian** (weaken them, which makes neurons more
different), **three-factor** (Hebbian change that only happens when a third signal, like
dopamine, arrives), and **homeostatic** (keep each neuron's activity in a healthy range).
The cook is the set of neuromodulators (chemicals like dopamine and acetylcholine that
change how neurons and synapses behave).

**How it would work in the brain (if true).**
1. Hebbian, three-factor and homeostatic plasticity have all been observed (established,
   see H021 and H146).
2. Each synapse can run any of the four rule types.
3. Neuromodulator levels, set by the current situation, choose which rule dominates
   (for example dopamine turns on three-factor learning, as in H021 and H026).
4. Different areas and moments thus get different learning, from one small rule set.
5. The claim: nothing else is needed for any task the brain learns.

**How to test it here.**
Inside the standard test loop:
1. Build a numpy network where each layer's update is a weighted mix of the four rule
   types, with the mix set by a few "modulator" signals.
2. Let the modulator mix be learned or meta-learned per task (an outer loop, as in H091).
3. Baseline: a backprop network of the same size.
4. Tasks: the Tiny MLP task, then harder ones (for example multi-layer tasks and the H101
   transfer setup).
5. Metric: the hardest task each can solve at equal size. Run 5 or more seeds.

**Counts against it if:** a model with these four rule types plus switching fails a task
that backprop solves at equal size.

**Why it matters for a brain-like learner.** If true, a learner needs a small rule
library and a good switching system, not a new algorithm. It competes with section A
(the brain approximates backprop) and links to H026 and H091.

## H163 - Fast and slow weights are needed for in-context abstraction
**Status:** open · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** **In-context** learning means picking up a new rule within one
episode without slow retraining, like getting the hang of a new board game in five
minutes. The claim is that this needs two kinds of weights: **slow weights** that change
over days and hold general knowledge, and **fast weights** that change in seconds and hold
"what is true in this game". One timescale alone is said not to be enough.

**How it would work in the brain (if true).**
1. Synapses can change on several timescales, from short-term facilitation over
   seconds to lasting change over days (established in general; see H096 and H102).
2. During an episode, fast synaptic changes store the current bindings (for example
   "red means food here"), as in H100.
3. Slow weights, trained over many episodes, learn how to use these fast bindings, a bit
   like H027's meta-RL.
4. Together they let the network apply an abstract rule to new items within an episode.
5. Fast weights fade after the episode, and only slow weights keep what was general.

**How to test it here.**
Inside the standard test loop:
1. Build small in-context tasks: each episode has a new random mapping (for example new
   colour-to-reward pairs) that the agent must use after a few trials.
2. Model: a small recurrent network with slow weights plus fast weights that decay.
3. Baseline: the same network with a single timescale, matched in parameters (including
   a version with plain recurrent activity as memory, as in H027).
4. Metric: accuracy on later trials of a new episode, with new items never seen in
   training. Run 5 or more seeds.

**Counts against it if:** a single-timescale network matches the two-timescale network on
in-context tasks.

**Why it matters for a brain-like learner.** If true, a learner needs at least two weight
speeds. It competes with H027 (abstraction lives in activity only) and links to H100 and
H168.

## H164 - Local rules plus recombining replay are enough
**Status:** open · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** The claim has two halves. First, simple local rules (each synapse
changes using only nearby information) are good enough to learn **features**, like edges,
colours or letter strokes. Second, to get **abstraction**, you need only one more piece:
**replay that recombines**, where the brain replays bits of past episodes in new orders.
It is like learning grammar by shuffling words you already know into new sentences.

**How it would work in the brain (if true).**
1. The hippocampus replays recent experience during rest and sleep (established).
2. Local plasticity in cortex learns features from waking input.
3. During replay, pieces of different episodes are stitched into new sequences (H065).
4. Cortex learns from these new combinations with the same local rules, so it sees the
   shared structure apart from any one episode's surface details.
5. The result is a reusable structure (a schema, as in H104) without any backprop-like
   signal.

**How to test it here.**
Inside the standard test loop:
1. Use the H101 transfer setup.
2. Model: a local-rule learner (for example a three-factor or Hebbian rule) plus a replay
   buffer that recombines segments from different episodes.
3. Baselines: the same learner with faithful (non-recombining) replay, with no replay,
   and a backprop learner at equal parameters.
4. Metric: episodes to criterion on new layouts (transfer). Run 5 or more seeds.

**Counts against it if:** a local rule with recombining replay still fails transfer in
the H101 setup.

**Why it matters for a brain-like learner.** If true, the hard part of abstraction is
replay, not the learning rule. It sharpens H101 by naming the kind of replay and
competes with H170 (which says more pieces are needed). Links H065 and H104.

## H165 - Sparse codes help abstraction, not just efficiency
**Status:** open · **Tier:** T1 · **Source:** **new** (links to issue #82)

**In simple words.** **k-WTA** ("k winners take all") means that in each layer only the k
most active neurons may fire, and the rest are set to zero. This saves energy and
compute. The claim is that it also helps **abstraction**: with fewer neurons active, each
one must stand for something more general, like a small team where everyone has a clear
job.

**How it would work in the brain (if true).**
1. Cortex fires sparsely: at any moment only a small part of neurons is active
   (established in broad terms).
2. Inhibitory neurons enforce this by suppressing all but the strongest responders.
3. With few active units per input, different inputs overlap less, so local rules
   change fewer shared synapses and interfere less.
4. The claim: units then come to code features that recur across many situations,
   which supports transfer to new layouts.

**How to test it here.**
Inside the standard test loop:
1. Use the H101 transfer setup, and Brain World's curriculum for the question in issue
   #82.
2. Model: a network with a k-WTA step in its hidden layer. Baseline: the same dense
   network at equal parameters.
3. Try a few values of k, chosen before running.
4. Metrics: transfer to new layouts, and separately compute or energy saved, so the two
   effects are not mixed up.
5. Run 5 or more seeds.

**Counts against it if:** sparse and dense networks at equal parameters give the same
transfer.

**Why it matters for a brain-like learner.** If true, sparsity is a learning tool, not
only a saving. It links to H073 (sparse concept cells) and H107 (sparse random
expansion). See [efficient-brain-like-learning](../../learning/efficient-brain-like-learning.md).

## H166 - Width hides a weak learning rule
**Status:** open · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** Local rules such as **feedback alignment** (FA, H002: errors are sent
back through fixed random weights) and **predictive coding** (PC, H001) usually learn
worse than backprop. The claim is that this gap gets smaller as the network gets wider
(more neurons per layer). So a huge brain might hide a weak rule, much like a big team
can make up for imperfect instructions.

**How it would work in the brain (if true).**
1. The human cortex has very many neurons per area (established in broad terms; see
   H131).
2. Each neuron uses a local, imperfect learning rule.
3. In a wide network, many directions in weight space reduce the error, so an imperfect
   update still often points downhill.
4. As width grows, the imperfect rule's results approach what an exact gradient would give.
5. So the brain would not need an exact algorithm, only enough neurons.

**How to test it here.**
Inside the standard test loop:
1. Use the Tiny MLP task and a slightly harder synthetic task.
2. Train FA, PC and backprop networks at several widths (for example from 8 to a few
   hundred hidden units), chosen before running.
3. Metric: the gap in final accuracy (and in learning speed) between each local rule and
   backprop, at each width.
4. Plot gap against width. Run 5 or more seeds per point.

**Counts against it if:** the FA/PC gap to backprop does not shrink as width grows.

**Why it matters for a brain-like learner.** If true, scaling up a local-rule learner is
a valid route. It links to H090 and H131 (scale over algorithm) and qualifies section A.

## H167 - Curiosity supplies the variety abstraction needs
**Status:** open · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** H079 says abstraction forms only when the structure stays the same
while surface details keep changing. H030 says the brain rewards itself for learning
progress, which is a form of **curiosity**. This row joins them: a curious agent, driven
by its world model's prediction errors, goes looking for new and surprising situations.
That gives it the varied data that abstraction needs, like a child who keeps trying the
same game with new toys.

**How it would work in the brain (if true).**
1. The cortex builds a world model that predicts what comes next (section C).
2. Prediction errors from this model act as an internal reward (links to H030).
3. The agent moves toward places and actions where its predictions are poor.
4. This makes it meet the same structure under many different surfaces.
5. With that variety, the structure is learned apart from the surface (H079), so transfer
   improves.

**How to test it here.**
Inside the standard test loop:
1. Use the H101 transfer setup.
2. Model: an agent with a curiosity bonus from its world model's prediction error (or
   learning progress, as in H030).
3. Baseline: a random explorer with the same number of steps.
4. Metrics: surface variety actually seen during training (for example the number of
   distinct colour and layout combinations) and transfer to new layouts.
5. Run 5 or more seeds.

**Counts against it if:** a curious and a random explorer see the same surface variety
and reach the same transfer.

**Why it matters for a brain-like learner.** If true, the learner must gather its own
data well, not only learn from it. Links H030 and H079, and relates to H156 (epistemic
value).

## H168 - Abstraction moves from activity into weights during sleep
**Status:** open · **Tier:** T1 · **Source:** **new** (links H027, H064)

**In simple words.** H027 says a new rule can first be learned in **activity** (the
pattern of firing in a recurrent network) without changing weights. H064 says cortex
slowly learns general structure from many replays. This row joins them: a new abstraction
first lives in activity during the day, like a note on a whiteboard, and sleep copies it
into the weights, like writing it into a notebook.

**How it would work in the brain (if true).**
1. During waking, prefrontal recurrent activity holds a new rule and applies it within
   the episode (H027).
2. This in-context abstraction is temporary and fades if not used.
3. During sleep, the hippocampus replays the day's episodes (established in rodents).
4. Replay drives the same activity patterns again, and slow plasticity in cortex stores
   them in synaptic weights (H064).
5. Next day, the rule is available without needing to be re-learned in activity.

**How to test it here.**
Inside the standard test loop:
1. Use the in-context tasks from H163 or Brain World layouts that share a rule.
2. Model: a recurrent agent that learns rules in activity, followed by an offline
   "sleep" phase that replays episodes and updates slow weights.
3. Ablation: the same agent with the sleep phase blocked (no replay or no weight update).
4. Metric: performance on the rule at the start of the next session, before any new
   in-context learning. Run 5 or more seeds.

**Counts against it if:** with consolidation blocked, the in-context abstraction still
becomes permanent.

**Why it matters for a brain-like learner.** If true, a learner needs both a fast
in-activity learner and an offline consolidation phase. Links H027, H064 and H163, and
relates to H105 (insight after sleep). See
[sleep-and-memory-consolidation](../../function/sleep-and-memory-consolidation.md).

## H169 - Judge learning rules by transfer, not accuracy
**Status:** open · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** Most papers rank learning rules by **accuracy**: how well a network
does on the task it was trained on. This row says we should also rank them by
**transfer**: how well they do on new situations that share structure. And it predicts
that the two rankings differ, like a student who tops the practice test but struggles on
a new kind of question.

**How it would work in the brain (if true).**
1. This is a claim about how to measure, not a brain mechanism.
2. Different rules shape different internal representations even at equal accuracy.
3. Some representations capture the shared structure; others memorise surface details.
4. So a rule that is weaker on training accuracy might still transfer better, which is
   what a brain-like learner needs.

**How to test it here.**
Inside the standard test loop:
1. Choose a fixed set of rules: backprop, FA (H002), DFA (H003), PC (H001), and a
   three-factor rule (H021).
2. Train each in the H101 transfer setup at equal parameters.
3. Record two scores per rule: accuracy on training layouts and transfer to new layouts.
4. Rank the rules by each score and compare the rankings (for example with a rank
   correlation). Run 5 or more seeds per rule.

**Counts against it if:** ranking the rules by accuracy and by transfer gives the same
order.

**Why it matters for a brain-like learner.** If true, the usual benchmarks pick the wrong
rule for abstraction, and every comparison in this repo should report transfer. It shapes
how H101, H164 and H166 are scored. See
[evaluating-brain-models](../../simulation/evaluating-brain-models.md).

## H170 - Abstraction needs all four main pieces
**Status:** open · **Tier:** T1 · **Source:** **new** (no published source)

**In simple words.** No single row explains abstraction alone. The claim is that four
pieces work together, like the legs of a table: **local credit assignment** (section A,
deciding which synapses caused an error using local signals), **replay** (section F),
**structural priors** (built-in starting structure, H103 and section E), and
**meta-learned neuromodulation** (neuromodulator settings tuned by an outer loop, H026 and
H091). Remove any leg and transfer falls sharply.

**How it would work in the brain (if true).**
1. Built-in structure (priors) gives the network a good starting shape (H103).
2. Local credit assignment learns features within that shape (section A).
3. Neuromodulators, whose settings were shaped by evolution or by slow learning, decide
   when and how strongly to learn (H026, H091).
4. Replay reuses and recombines episodes so cortex extracts what they share (H064, H065,
   H104).
5. Only all four together give strong transfer to new layouts.

**How to test it here.**
Inside the standard test loop:
1. Use the H101 transfer setup with a full model that has all four pieces.
2. Make four ablations, each removing one piece (for example replace local credit with a
   readout-only rule, remove replay, remove the prior, fix the modulators to constants).
3. Keep parameters and training steps equal across versions.
4. Metric: transfer to new layouts for the full model and each ablation, with a drop size
   that counts as "sharp" set before running.
5. Run 5 or more seeds for each version.

**Counts against it if:** in an ablation of each piece in the H101 setup, at least one
ablation has no effect on transfer.

**Why it matters for a brain-like learner.** If true, a brain-like learner must be built
as a system, and studying any piece alone will understate it. It competes with H164 and
H162 (fewer pieces suffice) and with H090 (scale alone). See
[build-a-brain-like-learner](../../guides/build-a-brain-like-learner.md).
