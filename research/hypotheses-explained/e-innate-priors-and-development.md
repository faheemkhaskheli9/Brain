# E. Innate priors and development, explained

Part of [the 170 hypotheses, explained simply](README.md). Main table and status:
[learning-algorithm-hypotheses.md](../learning-algorithm-hypotheses.md). Every row is a
**hypothesis**, not an established fact.

## The big idea of this group
A child learns to see, move and talk from far less data than a deep network needs. These
rows ask how much of that comes from what the brain brings *before* learning starts:
built-in wiring, self-made practice data, a growth schedule, and learning rules shaped by
evolution. Some background is established textbook science: retinal waves exist before
the eyes open, synapses are overproduced and then pruned, and critical periods exist
(see [brain-development-and-critical-periods](../../function/brain-development-and-critical-periods.md)
and [innate-priors-and-infant-learning](../../function/innate-priors-and-infant-learning.md)).
What is claimed here is that these facts are the *reason* learning is so efficient. Most
rows (H081-H089, H091, H092) say "the start state and the schedule matter". H090 says
the opposite: no special trick, just a big model and a lot of embodied data. A result for
one side weakens the other.

## H081 - The genomic bottleneck forces generalisation
**Status:** open · **Tier:** T1 · **Source:** Zador 2019, *Nat Commun*

**In simple words.** Your genes are a short instruction book. The human genome has about
3 billion base pairs, far too few to list every synapse (connection between neurons) one
by one. So evolution cannot pass on a finished brain. It passes on compact recipes:
"wire these areas like this, learn with this rule". The claim is that this squeeze is a
good thing. A recipe that must fit in a small book has to capture general patterns, not
details, so the brain it builds generalises better. It is like summarising a textbook in
one page: you keep the principles and drop the trivia.

**How it would work in the brain (if true).**
1. The genome cannot store individual synapse weights (established, by simple counting).
2. Instead it stores rules: which cell types connect, roughly where, with what strength
   bias, and which plasticity rule each synapse uses.
3. Development unfolds those rules into a wired brain with useful starting biases.
4. Because the rules are compact, they can only express regular, repeated structure. The
   odd, task-specific details of any one ancestor's brain are lost.
5. That regular structure is what transfers to new tasks in a new lifetime.

**How to test it here.**
Inside the standard test loop:
1. Train a net on a task family (Tiny MLP tasks, or a few Brain World layouts).
2. Build a "genome": a small network that takes a pair of neuron labels and outputs a
   weight. Fit it to reproduce the trained weights, with a few sizes from tiny to large.
3. Decode the genome into a fresh net and test it on new tasks (H101 transfer setup).
4. Compare transfer of the compressed nets with the original uncompressed net, at
   several compression sizes and at least 5 seeds each.

**Counts against it if:** compressing the trained net's wiring into rules gives no better
transfer than the uncompressed net.

**Why it matters for a brain-like learner.** If true, you should store and evolve
*rules* for building a network, not weights. It links to H087 (architecture as prior),
H091 (evolution as outer loop) and H103 (prior vs better rule).

## H082 - Retinal waves pre-train sensory maps
**Status:** open · **Tier:** T1 · **Source:** Katz & Shatz 1996, *Science*

**In simple words.** Before the eyes open, the retina makes its own activity. Waves of
firing roll across it, so nearby cells fire together (established, Meister et al. 1991).
The claim is that this is practice data. The visual system learns from these fake
"movies" to sort its wiring into neat maps before it ever sees the world. It is like a
band rehearsing with a metronome before the real concert.

**How it would work in the brain (if true).**
1. Retinal neurons fire in spontaneous, spreading waves before eye opening (established).
2. Neighbouring retinal cells are active together; cells from the two eyes are not
   active at the same time.
3. Downstream, in the thalamus and visual cortex, Hebbian plasticity ("cells that fire
   together wire together") strengthens synapses from co-active inputs.
4. This sorts connections into topographic maps (neighbours stay neighbours) and
   separates the two eyes' inputs.
5. When real vision starts, these maps are already in place, so learning from real images
   is faster.

**How to test it here.**
Inside the standard test loop:
1. Generate synthetic waves: blobs of activity drifting across a small 2D sheet of "retina"
   pixels.
2. Pre-train a small Hebbian or self-supervised layer (with weight normalisation) on the
   waves.
3. Compare with a baseline that gets no pre-training, and with one pre-trained on white
   noise (to check the wave structure matters, not just activity).
4. Then train all three on a small image or Brain World vision task. Measure episodes to
   reach a fixed score, over at least 5 seeds.

**Counts against it if:** pre-training on synthetic waves gives no speed-up on later
tasks.

**Why it matters for a brain-like learner.** It would mean a learner can make its own
cheap pre-training data from simple internal dynamics. It links to H087 (structure
before learning) and H089 (self-made curriculum).

## H083 - Starting small helps learning
**Status:** open · **Tier:** T1 · **Source:** Newport 1990, *Cogn Sci*; Elman 1993, *Cognition*

**In simple words.** Children have short memories and blurry, limited perception. Adults
have more of both. Yet children learn languages better. Newport proposed "less is more":
a child who can hold only a few words at once is forced to find the small, reusable
pieces of language. Elman showed a network that started with a short memory and grew it
could learn a grammar that a full-memory network struggled with. The idea is like
learning to juggle with one ball before three. Later work has questioned how general the
effect is, which is why this is still open.

**How it would work in the brain (if true).**
1. Early on, working memory span and perceptual detail are small, partly because the
   brain is still maturing (myelination and prefrontal development continue for years,
   established).
2. With a narrow window, the learner sees only short chunks of input.
3. Short chunks show simple, local regularities clearly (common sounds, word pieces).
4. Synapses lock in these simple building blocks first.
5. As capacity grows, longer structure is learned on top of the building blocks instead
   of being memorised whole.

**How to test it here.**
Inside the standard test loop:
1. Make a small grammar task: sequences from a tiny artificial grammar with nested
   structure.
2. Train a small numpy recurrent net whose memory window (or hidden size) grows over
   training.
3. Baseline: the same net at full capacity from the start, with the same total training.
4. Measure accuracy on held-out sentences, including longer ones, over at least 5 seeds.

**Counts against it if:** the growing-capacity learner ends up the same as or worse than
the full-capacity learner.

**Why it matters for a brain-like learner.** If true, a learner should be built to grow,
not start at full size. It links to H086 (blurry vision first) and H085 (plasticity
schedule).

## H084 - Core knowledge systems as a starting kit
**Status:** open · **Tier:** T1 · **Source:** Spelke & Kinzler 2007, *Dev Sci*

**In simple words.** Very young infants already seem to "expect" certain things. Objects
stay solid and keep existing when hidden. Agents (people, animals) act towards goals.
Small numbers and the shape of a room can be told apart. Spelke and Kinzler call these
core knowledge systems. The claim here is that learning builds on top of this starter
kit, which is why babies need so little data. It is like a new phone that comes with
basic apps installed, so you only add the extras.

**How it would work in the brain (if true).**
1. Infants show these expectations very early in looking-time studies (they look longer
   at "impossible" events), as described by the source.
2. Dedicated circuits are wired before or soon after birth for objects, agents, number,
   places and geometry.
3. These circuits turn raw input into useful variables: "an object here", "an agent
   wanting that".
4. Later learning (words, tools, social rules) attaches to these variables instead of to
   raw pixels.
5. Because the variables already fit the world's structure, far fewer examples are
   needed.

**How to test it here.**
Inside the standard test loop:
1. In Brain World, give one agent built-in modules: an object tracker (things persist
   when hidden) and an agent detector (things that move towards goals).
2. Give a baseline agent the same network size and learning rule, but no modules.
3. Train both on the five skills in order.
4. Measure episodes needed per skill and the H101 transfer score, over at least 5 seeds.

**Counts against it if:** the agent with object and agent priors shows no saving in
samples over the agent without them.

**Why it matters for a brain-like learner.** It says which priors are worth building in.
It links directly to H103 (prior vs better rule) and to H081 (how such priors could fit
in a genome); H090 predicts no need for them.

## H085 - Critical periods are a learning-rate schedule
**Status:** open · **Tier:** T1 · **Source:** Hensch 2005, *Nat Rev Neurosci*

**In simple words.** Some things are learned easily only in a window early in life.
Closing one eye of a young kitten rewires its visual cortex; the same in an adult cat
does little (established). The claim is that this is the brain's version of a
learning-rate schedule, as used in machine learning: learn fast early, then slow down
to protect what you learned. It is like wet concrete: easy to shape at first, then it
sets.

**How it would work in the brain (if true).**
1. Early in life, plasticity in a sensory area is high (established).
2. The window opens when fast-spiking inhibitory neurons (parvalbumin cells) mature, and
   closes when molecular "brakes" such as perineuronal nets form around them
   (established, Hensch 2005).
3. While the window is open, synapses change quickly and the area tunes to the input
   statistics.
4. After closing, synapse changes are small, so the learned map is protected from being
   overwritten by later, noisier input.
5. The claim: this schedule gives a better balance of fast learning and stable memory
   than constant plasticity.

**How to test it here.**
Inside the standard test loop:
1. Train a small local-rule network (for example Hebbian or Oja's rule) on an input
   distribution, then switch to a second distribution partway.
2. Condition A: learning rate decays over time. Condition B: constant learning rate,
   tuned for best final score.
3. Measure how well the first-phase representation survives (stability) and how well
   the second phase is learned.
4. Repeat for at least 5 seeds and a few decay speeds.

**Counts against it if:** decaying plasticity gives no stability gain over constant
plasticity.

**Why it matters for a brain-like learner.** A lifelong learner needs a rule for when to
stop changing. It links to H083 and H088 (other developmental schedules) and to section
F on forgetting.

## H086 - Blurry early vision is a feature
**Status:** open · **Tier:** T1 · **Source:** Vogelsang et al. 2018, *PNAS*

**In simple words.** Newborns see the world very blurry, and their sharpness improves
over months (established). The claim is that this blur helps. With fine details hidden,
the brain must learn from the big shapes and the layout of parts, such as how eyes,
nose and mouth sit in a face. The source paper linked this to children who got sight
late after cataract surgery and so started with sharper vision, and to networks trained
with a blur-then-sharp schedule. It is like learning the plot of a film before the
details.

**How it would work in the brain (if true).**
1. At birth, visual acuity is low because the eye and visual pathway are immature
   (established).
2. Early visual cortex learns from this low-detail input.
3. With only coarse input, neurons develop large receptive fields (the patch of the scene
   a neuron responds to) that combine information over wide areas.
4. These "configural" features (the arrangement of parts) are then kept as acuity rises.
5. Fine detail is learned later, on top of the large-scale features, so recognition stays
   robust when details are missing or noisy.

**How to test it here.**
Inside the standard test loop:
1. Use a small image classification set that numpy can handle (tiny faces or shapes).
2. Train a small net with a schedule: heavily blurred images first, slowly sharpening.
3. Baseline: the same net and steps, sharp images only.
4. Test on blurred, noisy and part-scrambled test images. Measure robustness (accuracy on
   degraded images) over at least 5 seeds.

**Counts against it if:** the blur-then-sharp schedule gives no robustness gain over
sharp-only training.

**Why it matters for a brain-like learner.** It suggests a free curriculum: start with
low-resolution input. It is a special case of H083 (starting small).

## H087 - Architecture alone carries strong priors
**Status:** open · **Tier:** T1 · **Source:** Ulyanov et al. 2018, CVPR; Gaier & Ha 2019, NeurIPS

**In simple words.** A prior is what a system "assumes" before it sees data. This row
claims that the wiring pattern itself is a strong prior, even with random or untrained
weights. Ulyanov et al. showed an untrained image network can clean up noisy photos just
because of its structure. Gaier and Ha found network shapes that do tasks with one shared
weight value. For the brain, the claim is that the connectome (the wiring diagram) does
much of the work before learning. It is like a riverbed: the shape alone decides where
the water goes.

**How it would work in the brain (if true).**
1. Development builds a wiring pattern: which areas connect, layers, local vs long-range
   links, convergence and divergence (established that these patterns exist).
2. Even with weak, unrefined synapses, this pattern already filters input in useful ways
   (for example, local connections favour local image features).
3. A simple readout, such as a downstream area learning which neurons matter, can then do
   useful tasks with little training.
4. Learning only fine-tunes a system that already works partly.

**How to test it here.**
Inside the standard test loop:
1. Build an untrained "connectome-like" net: local receptive fields, layered, sparse
   long-range links, with random weights.
2. Baseline: a random dense net with the same number of neurons and synapses.
3. Freeze both and train only a linear readout on a small task (images or Brain World
   observations).
4. Compare readout accuracy over at least 5 seeds and a few readout training sizes.

**Counts against it if:** the untrained connectome-like net shows no difference in readout
performance from the random net.

**Why it matters for a brain-like learner.** If true, designing the wiring is as
important as designing the rule. It feeds H081 (wiring rules in the genome) and H103.

## H088 - Early pruning at a falling rate
**Status:** open · **Tier:** T1 · **Source:** Navlakha, Barth & Bar-Joseph 2015, *PLoS Comput Biol*

**In simple words.** The young brain makes far more synapses than it keeps, then removes
many of them (established, "overproduce then prune"). The source argues the timing
matters: prune a lot early and less and less over time. That gives networks that are
both efficient (few wasted links) and robust (still work when some links fail). It is
like a gardener who cuts hard in spring and only trims later.

**How it would work in the brain (if true).**
1. Synapse density rises after birth, peaks, and then falls (established).
2. Pruning is activity-dependent: rarely used synapses are removed, partly by microglia
   (established).
3. The claim: the pruning rate is high at first and slows down.
4. Early heavy pruning removes clearly useless links while the network is still being
   shaped; later light pruning avoids cutting links that turned out to matter.
5. The result is a sparse network with the important routes kept and backed up.

**How to test it here.**
Inside the standard test loop:
1. Start a local-rule network (Hebbian or a three-factor rule) with dense connections.
2. Prune the weakest or least-used synapses during learning under three schedules:
   falling rate, constant rate, rising rate, all ending at the same final sparsity.
3. Measure task score, then robustness: delete a random fraction of the remaining
   synapses and measure the drop.
4. Use at least 5 seeds per schedule.

**Counts against it if:** prune schedules in a local-rule net show no robustness gain.

**Why it matters for a brain-like learner.** It gives a recipe for growing a sparse,
cheap network. It links to H085 (schedules) and H137 (synapses as the budget).

## H089 - Babies make their own curriculum
**Status:** open · **Tier:** T2 · **Source:** Smith & Gasser 2005, *Artif Life*; Orhan, Gupta & Lake 2020, NeurIPS

**In simple words.** Babies do not get random photos of the world. They get what is in
front of their own eyes, shaped by what they choose to look at and grab. A toddler holds
an object close, turns it, and sees it big and clear from many angles. The claim is that
this self-chosen, first-person (egocentric) data is a very good curriculum. It is like a
student who picks the exercises that teach them most.

**How it would work in the brain (if true).**
1. The infant's body limits and shapes the view: what is near, what is held, where the
   head points.
2. Attention and curiosity pick some objects for long, close looks.
3. Those views give clean, varied examples of single objects, a few at a time.
4. Self-supervised learning (learning from the data's own structure, with no labels) in
   visual cortex builds object categories from these views.
5. As motor skills grow, the data gets more complex, so the curriculum grows with the
   child.

**How to test it here.**
Inside the standard test loop:
1. Use open headcam video recorded from young children (the SAYCam kind of data, as in
   Orhan, Gupta & Lake 2020).
2. Train a small self-supervised model on the frames (a numpy one is enough for a pilot
   on downsized frames; larger runs are not run here).
3. Freeze it and train a linear readout on labelled object categories.
4. Compare with the same model trained on an equal number of non-egocentric frames, and
   with a random-weight model. Use at least 5 seeds.
5. A T1 side test: in Brain World, compare an agent that picks where to look with one that
   sees random views.

**Counts against it if:** self-supervised learning on a child's headcam gives no useful
categories.

**Why it matters for a brain-like learner.** If true, the learner should control its own
data stream, not be fed a fixed dataset. It is part of the H090 debate: it says the data
is special, not only large.

## H090 - No special algorithm, just direct fit
**Status:** open · **Tier:** T2 · **Source:** Hasson, Nastase & Goldstein 2020, *Neuron*

**In simple words.** This row is the "no trick" view. The brain is a huge model with many
more parameters than it strictly needs (over-parameterised). Hasson and colleagues argue
it simply fits itself to the dense stream of experience in a lifetime, just as deep
networks fit their data. Generalisation comes from the size of the model and the amount
of data, not from clever priors or a special rule. It is like a very big notebook filled
with very many examples.

**How it would work in the brain (if true).**
1. The cortex has a very large number of synapses, far more than a compact rule would
   need (established that the count is large).
2. A lifetime gives a constant flow of rich, multi-sense, embodied data.
3. Some ordinary learning rule adjusts the synapses to fit that data, with no special
   built-in structure needed.
4. New cases are handled by interpolating between the many stored examples.
5. Abilities that look like reasoning are what dense fitting looks like at this scale.

**How to test it here.**
Inside the standard test loop:
1. Use open data from a matched-data benchmark (BabyLM, which limits language models to
   roughly the amount of text a child hears).
2. Collect published BabyLM model scores and published child benchmarks on the same
   kinds of test (grammar judgements, word learning).
3. Compare how much data models need to reach child-level scores.
4. A T1 side check: in Brain World, compare a large plain model with a small model with
   priors (H084) at equal data.

**Counts against it if:** in a matched-data comparison like BabyLM, models still need far
more data than children.

**Why it matters for a brain-like learner.** If true, the best path is scale plus embodied
data, and the hunt for brain priors matters less. It competes with H001 (a special
gradient-like rule), H081, H084 and H103, and links to H131 (scale).

## H091 - Evolution meta-learned the plasticity rules
**Status:** open · **Tier:** T1 · **Source:** Confavreux et al. 2020, NeurIPS; Najarro & Risi 2020, NeurIPS

**In simple words.** Learning has two loops. The inner loop is a lifetime: synapses
change by some rule. The outer loop is evolution: over many generations, the rule itself
is tuned. "Meta-learning" means learning how to learn. The claim is that evolution was
this outer loop, and it found plasticity rules that work well for the kind of worlds
animals live in. The source papers searched for such rules with computers. It is like a
coach who does not play the game but trains the players' habits.

**How it would work in the brain (if true).**
1. Each synapse changes using local signals: pre- and post-synaptic activity, maybe a
   reward or neuromodulator signal (established that such local rules exist).
2. The exact form of the rule (how much each signal counts) is set by genes.
3. Animals whose rules learned faster or more safely survived better.
4. Over generations, rules were tuned to the statistics of typical tasks.
5. In each new animal, these tuned rules let a lifetime of learning succeed quickly.

**How to test it here.**
Inside the standard test loop:
1. Write a parameterised local rule: weight change = a·pre·post + b·pre + c·post + d,
   with the coefficients as the "genome".
2. Meta-learn the coefficients in an outer loop (simple evolution strategy in numpy) over
   many Brain World layouts.
3. Test the evolved rule on new layouts it never saw during evolution.
4. Compare with plain Hebb and Oja's rule on the same nets and layouts, at least 5 seeds.

**Counts against it if:** the evolved rules are no better than Hebb or Oja.

**Why it matters for a brain-like learner.** If true, we should search for rules, not
hand-design them. It links to H081 (rules in the genome) and H092 (rules that are
themselves learnable).

## H092 - Plasticity itself is plastic
**Status:** open · **Tier:** T1 · **Source:** Miconi, Clune & Stanley 2018, ICML; Miconi et al. 2019, ICLR

**In simple words.** Usually every synapse follows the same learning rule with the same
speed. This row says each synapse has its own "how much should I change?" dial, a
plasticity coefficient, and that dial is itself learned. Miconi and colleagues called
this differentiable plasticity: the dials are trained by gradient descent, while the
fast Hebbian changes happen during each task. It is like a team where each member knows
how open they should be to new ideas, and that openness was learned over time.

**How it would work in the brain (if true).**
1. Each synapse has a slow, fixed part of its strength and a fast, Hebbian part that
   changes within a task.
2. A per-synapse coefficient sets how big the fast part can grow.
3. Over many tasks, the coefficients are tuned: synapses that should store new facts
   become very plastic; synapses that hold stable knowledge become rigid.
4. Within a new task, only the plastic synapses change, so learning is fast and does not
   wreck old knowledge.
5. In the brain, the coefficient could be set by local molecules or by neuromodulators
   (a hypothesis, not established).

**How to test it here.**
Inside the standard test loop:
1. Build a small numpy recurrent net with Hebbian fast weights and per-synapse plasticity
   coefficients.
2. Train the slow weights and coefficients across many small tasks (for example pattern
   completion or Brain World layouts).
3. Baseline: the same net with one shared fixed plasticity rate.
4. Test on new tasks. Measure how fast each learns them and the final score, over at
   least 5 seeds.

**Counts against it if:** the plastic-plasticity net shows no gain over the fixed rule on
new tasks.

**Why it matters for a brain-like learner.** It gives each synapse its own learning rate,
which helps both fast learning and stability. It is a lighter version of H091 (learned
rules) and links to H085 (when plasticity should be high).
