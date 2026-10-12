# G. Language and reasoning, explained

Part of [the 170 hypotheses, explained simply](README.md). Main table and status:
[learning-algorithm-hypotheses.md](../learning-algorithm-hypotheses.md). Every row is a
**hypothesis**, not an established fact.

## The big idea of this group
Humans learn language from far less data than a large language model (LLM) needs, and
they reason about things they have never seen. This group asks how. Some background is
established: the brain has a left-sided language network in frontal and temporal cortex,
and that network responds weakly to maths, logic and music (Fedorenko, Behr & Kanwisher
2011). It is also established that the brain anticipates upcoming words, and that LLM
activations predict brain responses to the same sentences (see
[language-and-llms](../../function/language-and-llms.md)). What is *claimed* in the rows
below is the mechanism. The rows fall into three camps that compete. One camp says
general learning from rich statistics is enough (H109, H110, H111, H129, H130). One says
humans have special built-in machinery: an innate structure-building operation, a
"language of thought", program-like concepts or explicit relation binding (H114-H117,
H121, H122). The third says much of it comes from other people: social gating, teaching,
shared symbols and culture (H113, H126-H128). A result for one camp usually weakens
another.

## H109 - Infants segment words using syllable statistics
**Status:** open · **Tier:** T1 · **Source:** Saffran, Aslin & Newport 1996, *Science*

**In simple words.** Speech has no spaces between words. So how does a baby know where
one word ends? This idea says babies count which syllable tends to follow which. Inside a
word, the next syllable is very predictable ("pre-" is often followed by "-tty"). Across a
word boundary it is not ("pretty" can be followed by almost anything). A dip in
predictability marks a likely word edge. This is called a **transition probability**: how
likely syllable B is, given that you just heard syllable A.

**How it would work in the brain (if true).**
1. A continuous stream of syllables reaches auditory cortex (established that infants hear
   and discriminate syllables).
2. Neurons tuned to each syllable fire in turn.
3. A Hebbian rule ("fire together, wire together") strengthens the synapse from the
   syllable-A population to the syllable-B population each time B follows A.
4. Strong links come to mean "high transition probability"; weak links mean "boundary".
5. A downstream group groups syllables joined by strong links into a word-like chunk.
6. These chunks become candidate words that meanings can later attach to.

**How to test it here.**
Inside the standard test loop:
1. Build an artificial language like Saffran's: a few three-syllable nonsense words
   strung together with no pauses, in random order.
2. Train a local Hebbian sequence learner (one unit per syllable, a weight matrix updated
   only by pre-then-post activity) on the stream.
3. Read out a boundary wherever the learned link strength drops below a threshold.
4. Score segmentation with precision and recall against the true word edges. Compare
   with a baseline that places boundaries at random with the same rate.
5. Also run the infant-style test: does the model "prefer" (give higher summed link
   strength to) real words over part-words that span a boundary?

**Counts against it if:** the local Hebbian sequence learner cannot segment the syllable
stream.

**Why it matters for a brain-like learner.** If a purely local rule finds words, the first
step of language needs no special machinery, which supports the "statistics is enough"
camp against H114. See also [timing-and-sequence-learning](../../function/timing-and-sequence-learning.md).

## H110 - The language network predicts the next word
**Status:** open · **Tier:** T2 · **Source:** Schrimpf et al. 2021, *PNAS*; Goldstein et al. 2022, *Nat Neurosci*

**In simple words.** An LLM is trained to guess the next word. This idea says the brain's
language network does the same job. The evidence so far is a match: LLM activations,
mapped linearly onto brain recordings, predict how the brain responds to sentences, and
better next-word models predict the brain better (established result, per the sources).
The open question is *why* they match. Maybe both predict the next word. Or maybe both
just encode which words and meanings are present, and prediction is not the shared part.

**How it would work in the brain (if true).**
1. Words arrive one at a time through hearing or reading.
2. The language network keeps a running summary of the context so far.
3. Before the next word arrives, it activates a guess about that word (Goldstein et al.
   2022 report such pre-onset signals in ECoG, electrodes on the brain surface).
4. When the word arrives, the mismatch between guess and word is a surprise signal
   (the N400 EEG wave tracks surprise; established).
5. That surprise signal drives learning, so the network gets better at guessing.

**How to test it here.**
Inside the standard test loop:
1. Use the open Narratives fMRI dataset (people listening to stories), tracked as issue #89.
2. Build an **encoding model**: a linear map from word features to each brain voxel,
   scored by correlation on held-out stories (see
   [evaluating-brain-models](../../simulation/evaluating-brain-models.md)).
3. Compare feature sets: LLM activations; next-word surprisal; and prediction-free
   features such as static word embeddings, part of speech and word rate.
4. Use the same regularisation and cross-validation for each. Test the difference across
   subjects, not across voxels.

**Counts against it if:** prediction-free features fit the brain as well as the
prediction-based ones.

**Why it matters for a brain-like learner.** If it holds, next-word prediction is a fair
objective for a brain-like language module. H111 is a stronger version of the same claim.

## H111 - The brain predicts at many timescales
**Status:** open · **Tier:** T2 · **Source:** Caucheteux, Gramfort & King 2023, *Nat Hum Behav*

**In simple words.** An LLM guesses one word ahead. This idea says the brain guesses
further: the next word, the rest of the phrase, and where the whole idea is going. It is
like a weather forecast for the next hour, the next day and the next week, made at once.
The source reports that adding information about words further ahead improves the fit of
LLM features to fMRI. The claim that this reflects a hierarchy of predictions is the
hypothesis.

**How it would work in the brain (if true).**
1. Sensory areas near auditory cortex hold short-range context (a few syllables).
2. Higher temporal areas hold phrase-level context; frontal and parietal areas hold
   longer, idea-level context. (That higher areas integrate over longer windows is
   reported in fMRI work; the predictive role is the claim.)
3. Each level predicts the upcoming input at its own timescale.
4. Each level compares its forecast with what actually arrives and learns from its own
   error.
5. Long-range forecasts feed down to bias the short-range guesses.

**How to test it here.**
Inside the standard test loop:
1. Reuse the H110 encoding pipeline on Narratives fMRI.
2. Build two feature sets: next-word model features alone, and the same features plus
   representations of words several steps ahead (a "forecast window").
3. Vary the window length and record which window best fits each brain region.
4. Check whether the best window grows from auditory to frontal regions.
5. Control for the extra number of features (compare with random features of equal size).

**Counts against it if:** multi-horizon features give no better brain fit than next-word
features.

**Why it matters for a brain-like learner.** If true, a brain-like learner should be
trained to forecast at several horizons, not only one step. It refines H110 and links to
[predictive-processing](../../function/predictive-processing.md).

## H112 - Language is for communication, not thought
**Status:** open · **Tier:** T1/T3 · **Source:** Fedorenko, Piantadosi & Gibson 2024, *Nature*

**In simple words.** We often feel we think in words. This idea says that is mostly an
illusion: language is a tool for passing thoughts between people, and reasoning runs in
other brain networks. The background is established: the language network barely responds
to maths or logic, and some people who lose nearly all language (global aphasia) can still
do arithmetic and logic puzzles. The broader claim, that thought does not need language,
is a position, not a settled result.

**How it would work in the brain (if true).**
1. The language network turns sound or text into meaning, and meaning into words
   (established that it is language-selective).
2. Reasoning (planning, logic, maths) runs in other networks, such as the
   **multiple-demand network**, a set of frontal and parietal areas active in many hard
   tasks.
3. The two networks exchange content when you explain a thought or follow an argument.
4. Damage to the language network leaves reasoning largely intact.

**How to test it here.**
Inside the standard test loop:
1. The claim about human brains is T3 (patient and imaging studies). A computer can test
   the design claim.
2. Build a small agent with a reasoning module (for example a planner over states) and no
   language module. Compare it with the same agent plus a language module.
3. Use multi-step tasks that need no words, such as Brain World navigation with a
   detour, or a small arithmetic puzzle on numbers given as vectors.
4. Metric: success rate and steps to solve, over at least 5 seeds.

**Counts against it if:** the agent with reasoning but no language module fails the
reasoning tasks.

**Why it matters for a brain-like learner.** If true, language can be bolted on as an
interface, and reasoning must be learned elsewhere. It competes with H119 (inner speech
scaffolds reasoning).

## H113 - Social interaction gates speech learning
**Status:** open · **Tier:** T1/T3 · **Source:** Kuhl, Tsao & Liu 2003, *PNAS*

**In simple words.** Babies learn the speech sounds of a language better from a live
person than from a video of the same person. The source reports that infants exposed to a
foreign language through live play kept the ability to hear its sounds, while infants
given the same input by video or audio did not. The hypothesis is that social contact
acts like a switch that turns learning on. Without it, the same sounds pass by without
being learned.

**How it would work in the brain (if true).**
1. Speech sounds reach auditory cortex in all cases.
2. A live, responsive partner raises the infant's attention and arousal (for example via
   shared gaze).
3. That social signal acts as a **gate**: a third factor, beyond the two neurons at a
   synapse, that decides whether a synapse may change.
4. Only gated sound input updates the phonetic categories.
5. Ungated input (video, audio) is heard but leaves weak or no traces.

**How to test it here.**
Inside the standard test loop:
1. The human claim is T3 (infant studies). A computer can test whether a gate helps.
2. Build a learner of sound categories (for example competitive learning over vectors
   standing in for syllables).
3. Give it a stream where useful sounds come with a "social" cue and distracting sounds
   come without it.
4. Compare: a learner whose learning rate is multiplied by the social cue, versus one
   that learns from everything.
5. Metric: category accuracy on held-out sounds.

**Counts against it if:** the agent with a social-attention gate learns no differently
from the agent without one.

**Why it matters for a brain-like learner.** A gate would tell a learner *what* to learn
from, saving data. It links to H126 and H127 (learning from others).

## H114 - An innate Merge operation builds hierarchy
**Status:** open · **Tier:** T1 · **Source:** Berwick & Chomsky 2016, *Why Only Us*

**In simple words.** Sentences are not flat strings. "The man who is tall is happy" has a
part ("who is tall") nested inside another. This idea says humans are born with one simple
operation, **Merge**, that takes two pieces and joins them into a new unit, which can be
joined again and again. That gives tree-shaped structure for free. The strong claim is that
learning from examples cannot replace it.

**How it would work in the brain (if true).**
1. Words are recognised and kept in working memory.
2. A built-in operation combines two items into a labelled unit.
3. The unit can itself be merged with another item, giving nested structure.
4. Grammar rules refer to this structure, not to word order. For example, a question
   moves the main verb, not simply the first verb.
5. Learning sets the details of each language, but the Merge operation itself is not
   learned.

**How to test it here.**
Inside the standard test loop:
1. Make a tiny artificial language where the right rule depends on hierarchy, not on
   position (for example forming a question from a sentence with an embedded clause).
2. Train only on sentences where a simple "first verb" rule and the hierarchical rule
   give the same answer.
3. Test on sentences where they differ.
4. Train a local learner (Hebbian sequence learner or a small recurrent net with a local
   rule) with no built-in tree prior. Compare with a model that has a Merge-like
   tree-building step.
5. Metric: share of test sentences answered by the hierarchical rule.

**Counts against it if:** the local learner with no Merge prior learns the hierarchical
generalisation anyway.

**Why it matters for a brain-like learner.** If Merge is needed, a brain-like learner
needs a built-in structure builder. It competes with H109, H129 and H130 (learning from
statistics) and is close to H115.

## H115 - Humans compress sequences into nested patterns
**Status:** open · **Tier:** T2 · **Source:** Dehaene et al. 2015, *Neuron*; Dehaene et al. 2022, *Trends Cogn Sci*

**In simple words.** Remember "ABABABAB" as "AB, four times". This idea says humans store
sequences as short nested programs like that: repeat, mirror, then repeat the whole. It
calls this a "language of thought" for sequences. A sequence with a short description is
easy to remember; one with only a long description is hard. The claim is that other
primates can track simpler sequence statistics but not these nested codes.

**How it would work in the brain (if true).**
1. Items in a sequence (sounds, locations) arrive one by one.
2. Lower levels track which item follows which (transition statistics).
3. Higher levels, possibly in frontal cortex, search for a short rule that generates the
   sequence: repeat, alternate, mirror, nested inside each other.
4. The sequence is stored as that rule, not as a list.
5. Memory errors and surprise depend on rule length, the **minimal description length**
   (the size of the shortest program that makes the sequence).

**How to test it here.**
Inside the standard test loop:
1. Find open behavioural data from human sequence-learning studies (error rates or
   surprise per sequence).
2. Write a small compressor that gives each sequence a length in a simple rule language
   (repeat, alternate, mirror, nest).
3. Compare its fit to the human data with a transition-probability model and a chunking
   model.
4. Use cross-validated correlation across sequences.

**Counts against it if:** the sequence-compression model fits human sequence-learning
data no better than the alternatives.

**Why it matters for a brain-like learner.** If true, a learner needs a bias towards short
nested programs, close to H114 and H116. It competes with H109 for how sequences are
stored.

## H116 - Concepts are small programs learned from few examples
**Status:** open · **Tier:** T1 · **Source:** Lake, Salakhutdinov & Tenenbaum 2015, *Science*

**In simple words.** Show a child one new letter and they can write it and spot it again.
This idea says the child does not store a picture. It stores a small "program": the
strokes and how they join. With a program you can redraw the concept, vary it, and
recognise new versions. **Bayesian program learning (BPL)** means picking the program that
best explains the example, weighed against how likely that program is to begin with.

**How it would work in the brain (if true).**
1. One example of a new concept arrives (for example a written character).
2. The learner already has reusable parts from past experience (strokes, how they join).
3. It searches for a short combination of parts that would produce the example.
4. It keeps the few best programs, weighted by how well and how simply they explain it.
5. A new item is judged by how likely those programs are to produce it.

**How to test it here.**
Inside the standard test loop:
1. Use Omniglot, the open set of handwritten characters from many alphabets, at small
   image size.
2. Build a cut-down BPL-like learner: characters as short sequences of stroke parts,
   scored by fit plus a simplicity prior.
3. Compare with a neural learner (a small numpy net with nearest-neighbour on its
   features) on one-shot classification: one example per class, then classify new ones.
4. Metric: one-shot accuracy across many episodes and at least 5 seeds.

**Counts against it if:** the BPL-like learner shows no gain over the neural learner on
Omniglot one-shot.

**Why it matters for a brain-like learner.** If programs win, a brain-like learner needs
reusable parts and a search over combinations. It is a special case of H117 and close
to H115.

## H117 - Learning is Bayesian inference over structured hypotheses
**Status:** open · **Tier:** T1 · **Source:** Tenenbaum et al. 2011, *Science*

**In simple words.** A child hears "dog" for three different dogs and guesses the word
means "dog", not "animal". Why? This idea says the learner keeps many structured guesses
(trees, rules, groups) and weighs each by how well it fits the examples and how likely it
was before. If "animal" were the meaning, seeing only dogs would be a big coincidence. So a
few examples are enough. **Bayesian inference** means updating how much you believe each
guess as evidence comes in.

**How it would work in the brain (if true).**
1. The learner has a space of possible structures (for example categories arranged in a
   tree).
2. Each structure has a prior belief, higher for simple ones.
3. Each example raises the belief in structures that predict it, and lowers the rest.
4. Narrow hypotheses gain fast when examples cluster tightly (the **size principle**).
5. Generalisation to a new item averages over all hypotheses, weighted by belief.

**How to test it here.**
Inside the standard test loop:
1. Make a small concept task: objects as feature vectors with a hidden tree of
   categories.
2. Build a Bayesian concept learner over that tree, with a simplicity prior.
3. Compare with a neural learner (the Tiny MLP style net, trained on the same few
   examples).
4. Give 1, 2, 4 and 8 examples. Measure generalisation to held-out objects, and how
   closely it matches the right level of the tree.

**Counts against it if:** the Bayesian concept learner and the neural learner generalise
the same from few examples.

**Why it matters for a brain-like learner.** If true, few-shot learning comes from a
structured hypothesis space, not a better local rule. It competes with H130 and H129,
which put few-shot ability in learned statistics.

## H118 - Physical reasoning is mental simulation
**Status:** open · **Tier:** T1 · **Source:** Battaglia, Hamrick & Tenenbaum 2013, *PNAS*

**In simple words.** Look at a stack of blocks: will it fall? This idea says you answer by
running a rough physics simulation in your head, a bit like a video-game engine. The
simulation is noisy, so you run it a few times and see how often the tower falls. The
alternative is that you just recognise patterns you have seen before ("that looks
wobbly").

**How it would work in the brain (if true).**
1. Vision builds a 3D estimate of the scene: objects, positions, rough masses.
2. An internal model rolls the scene forward in time using physics-like rules.
3. Noise in the perceived positions is included, so each run differs.
4. Several runs are summarised ("in most runs it fell").
5. The answer and the confidence come from that summary.

**How to test it here.**
Inside the standard test loop:
1. Build simple 2D scenes (stacks of boxes) with a tiny numpy physics step.
2. Simulation agent: estimate the scene with noise, roll it forward a few times, answer
   by the fraction that fall.
3. Pattern-match agent: a small classifier trained on images or features of past scenes
   with the answer.
4. Test both on new scene types not seen in training (taller stacks, new shapes).
5. Metric: accuracy on the new scenes.

**Counts against it if:** the simulation agent shows no gain over the pattern-match agent
on new physical scenes.

**Why it matters for a brain-like learner.** If true, a learner needs a world model it can
run forward, which links to the world-model rows in section C and to H125.

## H119 - Inner speech chains reasoning steps
**Status:** open · **Tier:** T1 · **Source:** Alderson-Day & Fernyhough 2015, *Psychol Bull*

**In simple words.** When a task is hard, many people talk to themselves: "first this,
then that". This idea says inner speech is not just a side effect. It holds each step in
words, so you can pass the result of one step to the next. It is like writing notes on a
scrap of paper while doing long division, except the paper is in your head.

**How it would work in the brain (if true).**
1. A task needs several steps, each depending on the last.
2. The speech-production system creates a word or short phrase for the current step,
   without saying it aloud.
3. The speech-perception system "hears" it, which puts it back into working memory.
4. That loop keeps the intermediate result active and lets it cue the next step.
5. Blocking inner speech (for example by repeating a word aloud) should hurt multi-step
   tasks more than single-step ones.

**How to test it here.**
Inside the standard test loop:
1. Build an agent with an internal symbol loop: at each step it emits a discrete symbol
   that is fed back as input on the next step.
2. Baseline: the same agent without the loop (it keeps only its hidden state).
3. Tasks: multi-step problems with a growing number of steps (for example chained
   lookups or Brain World tasks with several sub-goals).
4. Metric: success rate as a function of step count, at least 5 seeds.

**Counts against it if:** the agent with an internal symbol loop shows no gain over the
one without on multi-step tasks.

**Why it matters for a brain-like learner.** If true, a reasoning loop through a discrete
code helps, much like step-by-step reasoning in LLMs. It competes with H112.

## H120 - Shared words pull examples together
**Status:** open · **Tier:** T1 · **Source:** Lupyan 2012, *Front Psychol*

**In simple words.** A chihuahua and a great dane look very different. Calling both "dog"
may help your brain treat them as the same kind of thing. This is the
**label-feedback** idea: hearing a word sends a signal back down to perception that
highlights the features members of the category share. So words do not just name
categories; they help build them.

**How it would work in the brain (if true).**
1. An object is seen and processed by visual cortex.
2. A word for it is heard or recalled, and activates the language network.
3. Feedback from the word's representation reaches visual areas.
4. That feedback boosts features shared by the category and dampens features that
   differ.
5. Learning in the visual areas then groups category members more tightly.

**How to test it here.**
Inside the standard test loop:
1. Build a category task with feature vectors where the members of a category share a
   few features and differ a lot on others.
2. Learner with labels: during training, a label vector is fed back and added to the
   hidden layer.
3. Learner without labels: the same network, no label feedback.
4. Test on new categories built the same way (category transfer), with few examples.
5. Metric: accuracy on the new categories and how tightly their members cluster.

**Counts against it if:** the learner with labels shows no gain over the one without on
category transfer.

**Why it matters for a brain-like learner.** If true, words are a tool for learning
abstraction, which links to H126 (learning from others) and competes in part with H112.

## H121 - Analogy needs role-filler binding by timing
**Status:** open · **Tier:** T1 · **Source:** Hummel & Holyoak 1997, *Psychol Rev*; Doumas, Hummel & Sandhofer 2008, *Psychol Rev*

**In simple words.** "The sun is to the planets as the nucleus is to the electrons." To
see this, you must keep *roles* (thing at the centre, things orbiting) separate from the
*fillers* (sun, nucleus). This idea says the brain marks which filler goes with which role
by timing: units for "sun" and "centre" fire together, and units for "planets" and
"orbiter" fire together at a different moment. The models are called LISA and DORA (DORA
can also learn new relations).

**How it would work in the brain (if true).**
1. A situation is coded by units for objects and units for roles.
2. A role and its filler fire in synchrony; different pairs fire out of phase. (Brain
   rhythms exist; whether they bind roles is the claim.)
3. The pattern of firing for one situation activates matching role units in memory.
4. Matching roles across two situations gives a mapping: sun to nucleus, planets to
   electrons.
5. Learning strengthens links between mapped items and can store the shared structure
   as a new relation.

**How to test it here.**
Inside the standard test loop:
1. Make small analogy problems: pairs of situations with objects in roles, where the
   surface features of the objects do not help.
2. Build a cut-down LISA/DORA-like model with role and filler units and phase-based
   binding.
3. Compare with a plain network that sees the same situations as flat vectors.
4. Test on new fillers and new relations.
5. Metric: share of correct mappings.

**Counts against it if:** the LISA/DORA-like model and the plain network do the same on
analogy.

**Why it matters for a brain-like learner.** If true, a learner needs a way to bind roles
and fillers, not just bigger networks. It is the mechanism behind H122, and H123 proposes
where it may happen. See [brain-rhythms-and-oscillations](../../function/brain-rhythms-and-oscillations.md).

## H122 - Relations between relations set humans apart
**Status:** open · **Tier:** T1/T3 · **Source:** Penn, Holyoak & Povinelli 2008, *Behav Brain Sci*

**In simple words.** Seeing that two apples are "the same" is a relation. Seeing that
"two apples are the same" is like "two pens are the same" is a relation *between*
relations. This idea says humans are special because they can reason at that second
level, and other animals mostly cannot. The classic test is **relational match-to-sample**:
given the pair AA, choose BB rather than CD, because both pairs are "same".

**How it would work in the brain (if true).**
1. Perception codes objects and their features (established).
2. A first stage computes simple relations between objects (same, bigger, left of).
3. A second stage treats those relations as objects in their own right.
4. It compares relations with each other and finds matches at the second level.
5. This second stage, possibly in front parts of the prefrontal cortex, is the part
   that is claimed to be missing or weak in other species.

**How to test it here.**
Inside the standard test loop:
1. The species claim is mostly T3 (comparative studies). A computer can test whether
   higher-order relations are needed.
2. Build relational match-to-sample trials from random feature vectors, with new
   objects at test time.
3. Model A has only first-order relation units. Model B adds a stage that compares
   relations.
4. Metric: accuracy on trials with new objects.

**Counts against it if:** a model without higher-order relations still solves relational
match-to-sample.

**Why it matters for a brain-like learner.** If true, abstraction needs a separate level
that treats relations as things. It builds on H121 and links to H123 and to
[prefrontal-cortex-and-abstraction](../../function/prefrontal-cortex-and-abstraction.md).

## H123 - Rostrolateral PFC integrates relations
**Status:** open · **Tier:** T2 · **Source:** Bunge et al. 2005, *Cereb Cortex*

**In simple words.** The very front of the brain, at the side, is called the
**rostrolateral prefrontal cortex (RLPFC)**. This idea says it is the place that combines
two relations into one, as in an analogy ("is A to B the same relation as C to D?").
Thinking about one relation would not need it much; comparing two relations would.

**How it would work in the brain (if true).**
1. Temporal and parietal areas represent the items and their meanings.
2. Other parts of the prefrontal cortex hold single relations in working memory.
3. RLPFC takes two relations and compares or merges them.
4. Its activity rises with the number of relations that must be combined.
5. Its output tells the rest of the system whether the analogy holds.

**How to test it here.**
Inside the standard test loop:
1. Search open repositories (OpenNeuro, NeuroVault) for fMRI data from analogy or
   relational reasoning tasks (see
   [measuring-the-brain-and-open-datasets](../../simulation/measuring-the-brain-and-open-datasets.md)).
2. Define RLPFC with a standard atlas, chosen before looking at the data.
3. Contrast trials that need two relations combined with trials that need one, with
   difficulty and reaction time matched or added as covariates.
4. Test the effect across subjects.

**Counts against it if:** reanalysis of open analogy fMRI shows no relational-integration
effect in RLPFC.

**Why it matters for a brain-like learner.** If true, it gives a place to look for the
second-level relation stage of H122. A null result would not refute H121 or H122, which
could be done elsewhere.

## H124 - A global workspace broadcasts one content
**Status:** open · **Tier:** T1 · **Source:** Dehaene, Kerszberg & Changeux 1998, *PNAS*

**In simple words.** The brain has many specialist modules: vision, language, memory,
movement. This idea says there is also a shared "stage". When one piece of content wins the
stage, it is broadcast to all modules at once, so they can work on it together. That lets
the brain combine skills in new ways, like a group of experts who all read the same
whiteboard. It builds on Baars 1988.

**How it would work in the brain (if true).**
1. Specialist modules process input in parallel.
2. Long-range neurons in frontal and parietal cortex link the modules.
3. Contents compete; one wins and is amplified, a sudden spread of activity sometimes
   called **ignition**.
4. While it holds the stage, every module can read it and add to it.
5. Learning links modules that often work on the same broadcast content.

**How to test it here.**
Inside the standard test loop:
1. Build an agent with a few small modules (for example a perception module, a memory
   module and an action module).
2. Workspace version: the modules write to a shared vector through a competition and all
   read from it.
3. Modular version: fixed links between specific modules only.
4. Train both on some combinations of skills; test on new combinations never trained
   together (for example a Brain World skill paired with a new cue).
5. Metric: success on the new combinations.

**Counts against it if:** the workspace architecture shows no gain over the fully modular
one on new combinations.

**Why it matters for a brain-like learner.** If true, flexible reuse needs a shared
broadcast channel. It links to H119 and H112 and to
[theories-of-consciousness](../../function/theories-of-consciousness.md).

## H125 - The cerebellum automates familiar thoughts
**Status:** open · **Tier:** T1 · **Source:** Ito 2008, *Nat Rev Neurosci*

**In simple words.** When you learn to ride a bike, it starts slow and effortful and ends
up automatic. The cerebellum is known to help with that for movements. This idea says it
does the same for thinking: it learns to predict where a familiar chain of thought will go,
so you can skip the slow steps. Doing mental arithmetic you have done a hundred times feels
automatic for this reason, if the idea is right.

**How it would work in the brain (if true).**
1. The cerebellum learns **forward models** of movements: predictions of what a motor
   command will do (established; Wolpert, Miall & Kawato 1998).
2. Its learning uses an error signal from climbing fibres that changes the synapses from
   parallel fibres onto Purkinje cells (established; Marr 1969, Albus 1971, Ito).
3. Prefrontal cortex sends copies of its "thought commands" to the cerebellum through
   loops via the pons and thalamus (cortico-cerebellar loops are established).
4. The cerebellum learns to predict the result of each familiar mental step.
5. Once its prediction is good, prefrontal cortex can use it and skip the slow step.

**How to test it here.**
Inside the standard test loop:
1. Build an agent that solves a multi-step task by slow, step-by-step search.
2. Add a cerebellum-like forward model: a simple supervised learner, trained by the error
   between its prediction and the outcome of each search step.
3. Once the forward model is accurate, let the agent use its prediction instead of the
   search.
4. Compare with the same agent without the forward model on repeated, familiar problems.
5. Metric: steps or time to solve, and accuracy, over practice.

**Counts against it if:** the agent with a cerebellum-like forward model of its own
reasoning shows no speed-up.

**Why it matters for a brain-like learner.** If true, a learner can turn slow reasoning
into fast habit with a cheap local learner. It links to H118 (internal simulation) and to
[action-selection-and-motor-control](../../function/action-selection-and-motor-control.md).

## H126 - Abstraction is mostly learned from others
**Status:** open · **Tier:** T1 · **Source:** Tomasello 1999, *The Cultural Origins of Human Cognition*

**In simple words.** Nobody invents maths, writing or the calendar alone. This idea says
most human abstraction is passed on: children learn ideas others already found, then add a
little. Each generation starts higher, like a ratchet that only turns one way. The special
human skill, on this view, is learning from others, not inventing alone.

**How it would work in the brain (if true).**
1. A child pays attention to what another person attends to (joint attention).
2. The child copies not just actions but the goal behind them.
3. Words and demonstrations point to the parts of a situation that matter.
4. The child's ordinary learning systems then fit the abstraction from these well-chosen
   cues.
5. The new abstraction is passed on again, perhaps improved.

**How to test it here.**
Inside the standard test loop:
1. Train a teacher agent in Brain World until it masters a skill with a reusable
   structure.
2. Student A learns alone. Student B learns while the teacher shows it what to do (for
   example demonstrations or highlighted cues).
3. Test both with the H101 transfer setup: new layouts that share structure.
4. Metric: transfer performance, and how much training each student needed.

**Counts against it if:** agents taught by another agent reach the same abstraction as
agents that learn alone.

**Why it matters for a brain-like learner.** If true, a brain-like learner needs a teacher
and a way to learn from one. It links to H113, H127 and H128 and to
[social-cognition-and-theory-of-mind](../../function/social-cognition-and-theory-of-mind.md).

## H127 - Learners assume a helpful teacher
**Status:** open · **Tier:** T1 · **Source:** Shafto, Goodman & Griffiths 2014, *Cogn Psychol*

**In simple words.** If a teacher shows you one example, you assume they picked it on
purpose. So you learn more from it than from a random example. For instance, if a teacher
shows the two corners of a rectangle on a board, you guess they marked the exact edges.
This idea, **pedagogical reasoning**, says learners reason about why the teacher chose
each example.

**How it would work in the brain (if true).**
1. The learner sees an example and knows a teacher chose it.
2. The learner models the teacher: "which example would I pick to teach this concept?"
3. Hypotheses that the teacher would have shown this example for gain belief; the others
   lose belief.
4. The teacher in turn picks examples that will lead the learner to the right answer.
5. Both sides end up with fewer examples needed than with random sampling.

**How to test it here.**
Inside the standard test loop:
1. Make a simple concept game (for example rectangles on a grid, or a hidden rule over
   feature vectors).
2. Teacher: chooses examples that most raise the learner's belief in the true concept.
   Random: examples drawn at random.
3. Learner: a Bayesian learner that knows whether examples are chosen by a teacher.
4. Metric: examples needed to reach a target accuracy, in each condition.

**Counts against it if:** pedagogical examples give no saving in data over random ones.

**Why it matters for a brain-like learner.** If true, data efficiency depends on who chose
the data. It links to H126 and to H117 (Bayesian learning).

## H128 - Shared symbols emerge from cooperation
**Status:** open · **Tier:** T1 · **Source:** Lazaridou & Baroni 2020, arXiv:2006.02419

**In simple words.** Imagine two people who share no language and must work together by
sending only a few beeps. Over time they invent a code. This idea says shared symbols
appear naturally when two learners must cooperate through a narrow channel. The
interesting question is whether the code is **compositional**: built from parts that mean
the same thing in new combinations, like "red" + "box".

**How it would work in the brain (if true).**
1. A speaker sees something the listener needs to know.
2. The speaker sends a short signal from a small set.
3. The listener acts on it; both get a shared reward if the action is right.
4. Each side updates its mapping with a local rule driven by that reward (for example a
   dopamine-like third factor).
5. Over many rounds, a stable code forms; pressure for a small channel and new
   situations may push it to be compositional.

**How to test it here.**
Inside the standard test loop:
1. Put two Brain World agents in a task where one sees the goal and the other must reach
   it. Only a short message channel links them.
2. Both learn with local reward-driven rules.
3. Measure stability: does the code stay the same across rounds?
4. Measure compositionality: for example, does a message for a new combination of
   features follow from the messages for each part? Test on held-out combinations.
5. Compare with a channel of random messages.

**Counts against it if:** the two agents form no stable, compositional code.

**Why it matters for a brain-like learner.** If true, symbols can grow from local
learning plus cooperation, with no built-in grammar. It links to H126 and competes with
H114.

## H129 - Meta-learning gives systematic generalisation
**Status:** open · **Tier:** T1 · **Source:** Lake & Baroni 2023, *Nature*

**In simple words.** If you learn "jump" and "twice", you can understand "jump twice"
without seeing it. This is **systematic generalisation**: combining known parts in new
ways. Standard neural networks are often poor at it. This idea says the skill can be
learned by practising on many small tasks, each with a new set of made-up words. That is
**meta-learning**, learning how to learn. The source reports that a network trained this
way reached human-like systematic generalisation on its task.

**How it would work in the brain (if true).**
1. A child meets many small "games" where new words must be combined with known ones.
2. Each game is solved from a few examples in context.
3. Across games, a slow learning process tunes the network to solve such games well.
4. What is learned is a general habit: treat a new word as a part that combines by
   rules.
5. New combinations then work on the first try.

**How to test it here.**
Inside the standard test loop:
1. Build a small command-to-action task (like "jump twice" giving "JUMP JUMP") with
   word meanings shuffled in every episode.
2. Train a network whose weights change only by a local rule, across many episodes
   (meta-learning).
3. Baseline: the same network trained on one fixed task, and a backprop-trained version.
4. Test on new combinations in new episodes.
5. Metric: exact-match accuracy on held-out combinations.

**Counts against it if:** the meta-learned local-rule net fails systematic
generalisation.

**Why it matters for a brain-like learner.** If true, compositional skill can be learned,
not built in, which competes with H114. The question here is whether it also works with a
local rule. It links to H130.

## H130 - Bursty input statistics create in-context learning
**Status:** open · **Tier:** T1 · **Source:** Chan et al. 2022, NeurIPS

**In simple words.** **In-context learning** means picking up a new pattern from a few
examples given just now, without changing your long-term weights. This idea says it comes
from the shape of the data, not only from the model. Natural input is **bursty**: a rare
word or face shows up several times close together, then disappears for a long time. It
is also **Zipf-like**: a few items are very common and most are rare. The source reports
that training a transformer on data like this made in-context learning appear.

**How it would work in the brain (if true).**
1. Real-world input comes in bursts: a new person's name is used many times in one
   conversation.
2. Long-term weights cannot keep up with so many rare items.
3. So the system benefits from a fast mechanism that uses recent examples, such as
   fast-changing synapses or persistent activity in working memory.
4. Over development, this fast mechanism gets tuned because the input keeps rewarding
   it.
5. The result is the ability to learn from a few examples on the spot.

**How to test it here.**
Inside the standard test loop:
1. Build a small sequence task: sequences contain a few item-label pairs, then a query
   item.
2. Make two training sets: bursty (the query item appears earlier in the same sequence,
   with a Zipf-like spread of item frequencies) and uniform (items drawn evenly, rarely
   repeated within a sequence).
3. Train the same small numpy model with an attention-like or fast-weight readout on
   each set.
4. Test on sequences with brand-new items, where only the in-context examples can help.
5. Metric: accuracy on new items.

**Counts against it if:** training on bursty and uniform input gives the same in-context
learning.

**Why it matters for a brain-like learner.** If true, the data a learner sees matters as
much as its rule, which argues for natural, bursty curricula. It competes with H117 as an
account of few-shot learning, and links to H129.
