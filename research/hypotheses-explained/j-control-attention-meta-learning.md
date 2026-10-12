# J. Control, attention and meta-learning, explained

Part of [the 170 hypotheses, explained simply](README.md). Main table and status:
[learning-algorithm-hypotheses.md](../learning-algorithm-hypotheses.md). Every row is a
**hypothesis**, not an established fact.

## The big idea of this group
A brain does not run one fixed program. It must decide what matters right now, which
rule applies, which skill to use, and how much to trust each sense. These rows ask how
that "control layer" works and how it shapes learning. Some background is established:
prefrontal cortex (PFC, the front part of the cortex) is needed for flexible rule use,
the thalamus and cortex are tightly connected, layer 5 neurons detect when top-down and
bottom-up input coincide, divisive normalisation is seen in visual cortex, and the
cerebellum has a climbing-fibre teaching input. What is claimed is that each of these is
a key part of *how the brain learns*, and that a model with it beats a model without it.
H152, H153 and H154 are three answers to the same question (who decides which inputs
count): PFC bias, thalamic switching, or dendritic gating. They can also work together.
H155 and H161 are about how tasks are organised (sub-skills, predictive maps). H156 and
H157 are about uncertainty. H158 and H159 propose canonical cortical computations, and
H160 a separate supervised learner in the cerebellum.

## H152 - PFC biases the brain toward the goal
**Status:** open · **Tier:** T1 · **Source:** Miller & Cohen 2001, *Annu Rev Neurosci*

**In simple words.** Think of PFC as a sticky note on your fridge that says "today: only
buy vegetables". It does not do the shopping itself. It keeps the current goal and rule
active and nudges every other brain area to favour what fits the goal. When the rule
changes, you rewrite the note, and the whole brain follows. The claim is that this
"top-down bias" (a signal from a higher area that tilts processing in lower areas) is how
flexible behaviour works.

**How it would work in the brain (if true).**
1. Patients with frontal damage keep using an old rule after it has changed, for example
   on the Wisconsin Card Sorting Test (established).
2. Many lateral PFC neurons fire according to the rule in force, whatever cue signalled
   it (established in monkeys, Wallis, Anderson & Miller 2001).
3. This rule activity is held as sustained firing while the task lasts.
4. PFC sends this pattern to sensory, memory and motor areas as an extra input, which
   boosts the pathways that fit the rule and weakens the others.
5. Because the right pathways are more active, local learning (for example Hebbian)
   strengthens them more, so the bias also steers what is learned.

**How to test it here.**
Inside the standard test loop:
1. Build a small rule-switching task in numpy: the same stimuli must be sorted by colour
   in one block and by shape in the next, with the rule changing without warning.
2. Model: a small network plus a "goal unit" vector that is held across trials and adds
   a bias to the hidden layer. The goal is updated when reward drops.
3. Baseline: the same network with the same number of parameters but no goal bias.
4. Metric: trials needed to recover accuracy after each switch, and errors that follow
   the old rule (perseveration).
5. Run 5 or more seeds of each and compare means and spread.

**Counts against it if:** an agent with a goal-bias module does no better at rule
switching than one without it.

**Why it matters for a brain-like learner.** If true, a learner needs a small, separate
store for "what am I doing now" that steers the rest. It overlaps with H153 and H154
(other ways to steer) and with H034 (learning *when* to update PFC). See
[prefrontal-cortex-and-abstraction](../../function/prefrontal-cortex-and-abstraction.md).

## H153 - Thalamus switches cortical wiring by context
**Status:** open · **Tier:** T1 · **Source:** Schmitt et al. 2017, *Nature*

**In simple words.** The thalamus is a relay station in the middle of the brain that is
connected in loops with the cortex (established). This hypothesis says it acts like a
railway switchboard: the tracks (cortical connections) stay the same, but the thalamus
sets which ones are in use for the current context. So the same cortex can run one task
in the morning and another in the afternoon without rewiring.

**How it would work in the brain (if true).**
1. Cortex and thalamus are linked in loops, and the mediodorsal thalamus is closely tied
   to PFC (established anatomy).
2. A cue tells the animal which rule applies (for example "attend to sound" vs "attend
   to light").
3. Thalamic neurons pick up the context and send input back to PFC.
4. This input strengthens the effective connections among the PFC neurons that hold the
   current rule, and leaves the others weak. The synapses themselves do not change; their
   effect does.
5. When the context changes, the thalamus switches to a different pattern, and a
   different set of cortical connections becomes active. Learning can then happen inside
   the active set only, which limits interference between tasks.

**How to test it here.**
Inside the standard test loop:
1. Use a context task: two tasks share inputs, and a context cue says which one applies.
2. Model: a small recurrent network whose recurrent weights are multiplied by a gain
   pattern chosen by a "thalamic" unit that reads the context.
3. Baseline: the same network that gets the context cue only as an extra input, at equal
   parameters.
4. Metrics: accuracy after a context switch, speed of switching, and forgetting of task A
   after training task B.
5. Run 5 or more seeds of each.

**Counts against it if:** a thalamic-gating model does no better than a model without it
on a context task.

**Why it matters for a brain-like learner.** If true, one network can hold many tasks
when a small controller switches its connections. It links to H108 (context gating
against forgetting) and competes with H152 as the main switch. See
[one-brain-many-tasks](../../function/one-brain-many-tasks.md).

## H154 - Top-down input gates learning in dendrites
**Status:** open · **Tier:** T1 · **Source:** Larkum 2013, *Trends Neurosci*

**In simple words.** A large cortical neuron has two "ears". One, near the cell body,
hears bottom-up input from the senses. The other, the apical dendrite (a long branch
reaching up to the top layer of cortex), hears top-down input from higher areas. The claim
is that a sensory input only gets to change its synapse when the top-down ear agrees that
it matters, like a teacher who says "this one counts".

**How it would work in the brain (if true).**
1. Bottom-up input arrives at the basal dendrites near the cell body of a layer 5
   pyramidal neuron.
2. Top-down input from higher areas and the thalamus arrives at the apical tuft in layer 1
   (established anatomy).
3. When both arrive together, the cell fires a calcium spike in the dendrite and a burst
   of spikes (BAC firing, established, Larkum et al. 1999).
4. The claim: the burst is the learning signal. Synapses that were active during a burst
   get stronger; those active during single spikes alone change little or weaken.
5. So top-down context decides which feedforward inputs drive learning, and different
   contexts train different inputs on the same neuron.

**How to test it here.**
Inside the standard test loop:
1. Build neurons with two input compartments in numpy: basal (sensory) and apical (task
   context). The output bursts only when both are active above a threshold.
2. Model: weight changes are gated by bursts. Baseline: the same neurons with plain
   Hebbian learning on all inputs.
3. Train on several tasks that share inputs but need different features, using the Tiny
   MLP input set or a small synthetic multitask set.
4. Metrics: mean accuracy over all tasks and forgetting of earlier tasks.
5. Run 5 or more seeds of each.

**Counts against it if:** an apically gated model shows no multitask gain over a plain
model.

**Why it matters for a brain-like learner.** If true, each neuron does its own gating,
which is cheaper than a central switch (H153). It links to H135 (branches as learning
units) and to dendritic credit-assignment ideas in section A. See
[dendritic-computation](../../anatomy/dendritic-computation.md).

## H155 - Behaviour is built from learned sub-skills
**Status:** open · **Tier:** T1 · **Source:** Botvinick, Niv & Barto 2009, *Cognition*

**In simple words.** Making tea is not hundreds of separate muscle twitches. It is "boil
water", "get cup", "pour". Each of those is an **option**: a sub-skill with its own start,
its own policy (what to do in each situation) and its own end. The claim is that the
brain learns such options by reinforcement learning (RL, learning from reward), and then
plans and learns with whole options instead of single actions.

**How it would work in the brain (if true).**
1. Dopamine neurons signal reward-prediction errors (established, see H022).
2. While a sub-skill runs, a separate "pseudo-reward" marks reaching the sub-goal (for
   example "cup in hand").
3. Prediction errors about this pseudo-reward train the sub-skill's own policy, likely in
   basal ganglia and motor areas.
4. A higher level, likely in PFC, learns which option to start, using the normal reward.
5. Because options are reused across tasks, a new task only needs a new choice of options,
   not new low-level learning.

**How to test it here.**
Inside the standard test loop:
1. Use Brain World, whose five skills (walk, grasp, listen, read, write) build on each
   other.
2. Model: an options agent that keeps learned sub-skills (for example "walk to object",
   "grasp") and a top-level policy that chooses among them.
3. Baseline: a flat agent that picks single actions at every step, with equal parameters.
4. Metric: episodes to reach each stage's pass rate, especially later stages.
5. Run 5 or more seeds of each.

**Counts against it if:** an options agent learns no faster than a flat agent in Brain
World.

**Why it matters for a brain-like learner.** If true, a curriculum like Brain World's
should reuse earlier skills as building blocks. It links to H067 (chunked action
sequences) and H068 (a hierarchy of rules in frontal cortex). See
[action-selection-and-motor-control](../../function/action-selection-and-motor-control.md).

## H156 - Acting to reduce uncertainty, not only for reward
**Status:** open · **Tier:** T1 · **Source:** Friston et al. 2015, *Cogn Neurosci*

**In simple words.** When you enter a dark room, you switch on the light before you look
for snacks. Seeing does not give reward, but it removes uncertainty. This hypothesis says
agents choose actions partly for their **epistemic value**: how much they expect to learn
about the world. This idea is part of active inference, a theory where the brain acts to
keep its predictions good.

**How it would work in the brain (if true).**
1. The brain keeps a model of the world with beliefs about hidden states (where things
   are, which rule holds).
2. For each possible action, it estimates two things: expected reward and how much the
   action would reduce its uncertainty.
3. It picks actions that score well on the sum, so early on it explores informative
   places and later it exploits.
4. The new observations update the world model.
5. Neuromodulators that report uncertainty may set the balance (links to H025).

**How to test it here.**
Inside the standard test loop:
1. Use a small gridworld or Brain World layouts with hidden structure (for example which
   colour is food).
2. Model: an agent that adds an information-gain bonus (expected drop in uncertainty of
   its beliefs) to reward.
3. Baseline: a reward-only agent with a matched exploration rate (for example epsilon-
   greedy).
4. Metrics: episodes until the agent's world model predicts the hidden structure, and
   reward over time.
5. Run 5 or more seeds of each.

**Counts against it if:** an epistemic agent learns the structure no faster than a
reward-only agent.

**Why it matters for a brain-like learner.** If true, curiosity is not an add-on: the
learner should seek information as a goal. It competes with H030 (learning progress as
the intrinsic reward) and links to H167. See [decision-making](../../function/decision-making.md).

## H157 - Combining cues by their reliability
**Status:** open · **Tier:** T1 · **Source:** Knill & Pouget 2004, *Trends Neurosci*

**In simple words.** If you hear a friend's voice from the left but see them on the right,
you trust your eyes more, because vision is more precise for location. A **Bayesian
observer** weights each cue by its reliability (how little it varies). The table marks
this as supported for perception: people combine senses close to the best possible way
in many experiments (Ernst & Banks 2002). The open part here is a learning question: can
a network with only local rules learn this weighting?

**How it would work in the brain (if true).**
1. Two senses report the same thing, for example the position of an object.
2. Each sensory population also carries how sure it is, for example in its overall
   activity level.
3. A downstream population combines the two, giving more weight to the more reliable one.
4. When one sense becomes noisy (fog, darkness), its weight falls, without new training.
5. The claim to test: local plasticity on these connections is enough to learn the right
   weights from experience.

**How to test it here.**
Inside the standard test loop:
1. Generate a synthetic task: two noisy cues of one hidden value, with noise levels that
   change from trial to trial.
2. Train a small network with a local rule (for example a delta rule on the output, or
   Hebbian with normalisation) to estimate the hidden value.
3. Compare its cue weights with the ideal weights (each proportional to one over that
   cue's noise variance). Also train a backprop net as a reference.
4. Metric: estimation error relative to the ideal observer, and how weights shift when
   noise changes.
5. Run 5 or more seeds.

**Counts against it if:** a local-rule network cannot learn reliability weighting.

**Why it matters for a brain-like learner.** If local rules can learn it, the learner gets
uncertainty handling for free. It links to H036 and H144 (uncertainty in synapses and in
variability). See [predictive-processing](../../function/predictive-processing.md).

## H158 - Divisive normalisation helps learning
**Status:** open · **Tier:** T1 · **Source:** Carandini & Heeger 2012, *Nat Rev Neurosci*

**In simple words.** **Divisive normalisation** means each neuron's response is divided
by the summed activity of its neighbours. It is like judging a voice relative to the noise
in the room, not by its raw volume. It is seen in visual cortex, for example in how
responses scale with contrast (established). The claim here is that it is a general
("canonical") step that also makes learning work the same at any input scale.

**How it would work in the brain (if true).**
1. A neuron receives its input drive.
2. A pool of nearby neurons, often through inhibition, computes the total activity.
3. The neuron's output is its drive divided by that total plus a constant.
4. Outputs now stay in a similar range whether the input is dim or bright, weak or strong.
5. The claim: because activity stays in range, Hebbian-style learning does not run away
   or stall when input strength changes, and learning rates need less tuning.

**How to test it here.**
Inside the standard test loop:
1. Use the Tiny MLP task, and a version where input scale changes between blocks (for
   example multiplied by 0.1 or 10).
2. Model: add a divisive normalisation step after the hidden layer. Baseline: the same
   network without it. Train both with the same local rule and with backprop.
3. Metrics: accuracy, speed of learning, and sensitivity to the learning rate across
   input scales.
4. Run 5 or more seeds of each.

**Counts against it if:** a network with normalisation learns no better than one without.

**Why it matters for a brain-like learner.** If true, normalisation is a cheap fix for
the stability problems of local rules. It overlaps with H146 (homeostatic scaling) and
H145 (balanced inhibition). See [neural-coding-and-computation](../../function/neural-coding-and-computation.md).

## H159 - Cortical layers do predictive coding
**Status:** open · **Tier:** T2 · **Source:** Bastos et al. 2012, *Neuron*

**In simple words.** **Predictive coding** is the idea that higher areas send predictions
down, and lower areas send up only the part that was not predicted: the **prediction
error**. The cortex has six layers. This hypothesis maps the idea onto them: some layers
hold predictions, others compute errors. It is like a map of which room in a house does
which job.

**How it would work in the brain (if true).**
1. Feedforward connections to higher areas start mostly in superficial layers (2/3), and
   feedback connections mostly in deep layers (5/6) (established anatomy).
2. Deep-layer neurons hold the area's current prediction and send it down to the lower
   area.
3. Superficial-layer neurons compare input with the prediction and fire for the
   difference: the prediction error.
4. Errors go up; predictions come down. The claim also links errors to faster (gamma) and
   predictions to slower (alpha/beta) rhythms.
5. Synapses change to make errors smaller over time.

**How to test it here.**
Inside the standard test loop:
1. T2: use open laminar recordings, such as the Allen Brain Observatory Neuropixels data
   of mouse visual cortex, where electrodes span the layers.
2. Find conditions that separate prediction from error, for example expected vs
   unexpected stimuli, if the dataset contains them; otherwise note the limit.
3. For each layer, measure responses to expected and unexpected input.
4. Test whether error-like responses sit mainly in superficial layers and prediction-like
   ones in deep layers. Use several sessions and mice as replicates.
5. A computer can still do a T1 check: a two-layer predictive coding model (see H001)
   gives the expected pattern to compare against.

**Counts against it if:** laminar recordings show prediction and error signals are not in
separate layers.

**Why it matters for a brain-like learner.** If true, a cortical column has a fixed job
split that a model can copy. It links to H001 (predictive coding approximates backprop).
See [predictive-processing](../../function/predictive-processing.md) and
[measuring-the-brain-and-open-datasets](../../simulation/measuring-the-brain-and-open-datasets.md).

## H160 - The cerebellum learns from an error signal
**Status:** open · **Tier:** T1 · **Source:** Marr 1969, *J Physiol*; Albus 1971, *Math Biosci*; Raymond & Medina 2018, *Annu Rev Neurosci*

**In simple words.** Most of the brain has no teacher that says "this was the right
answer". The cerebellum may be the exception. Each Purkinje cell (its main output neuron)
gets one special input, the climbing fibre, that fires when a movement goes wrong. This is
like a coach who only shouts when you miss. **Supervised learning** means learning from
such an explicit error.

**How it would work in the brain (if true).**
1. Mossy fibres bring context (senses, copies of motor commands) to granule cells, which
   expand it into a huge, sparse code on parallel fibres (established anatomy).
2. Each Purkinje cell sums many parallel-fibre inputs and gets a single climbing fibre
   from the inferior olive (established).
3. When a movement misses its target, the climbing fibre fires.
4. Parallel-fibre synapses active together with the climbing fibre weaken (long-term
   depression, found by Ito and colleagues).
5. The Purkinje output changes, and the next movement is corrected. In machine-learning
   terms: a fixed expansion followed by a readout trained with the delta rule.

**How to test it here.**
Inside the standard test loop:
1. Add a cerebellar module to the Brain World creature: a random sparse expansion of its
   senses and motor commands, and a readout that adds a correction to the motor output.
2. Train the readout with an error signal (for example the gap between intended and
   actual leg or pen movement).
3. Baseline: the same creature without the module, or with the module but no error
   learning.
4. Metrics: motor error over time after a perturbation (for example a changed leg
   strength) and episodes to pass the walk and write stages.
5. Run 5 or more seeds.

**Counts against it if:** a cerebellar model in Brain World does not correct motor errors.

**Why it matters for a brain-like learner.** If true, the brain mixes learning types:
reward learning (section B), self-supervised cortex (section C) and supervised
cerebellum. It links to H107 (random expansion). See
[action-selection-and-motor-control](../../function/action-selection-and-motor-control.md).

## H161 - People plan with a predictive map
**Status:** open · **Tier:** T2 · **Source:** Momennejad et al. 2017, *Nat Hum Behav*

**In simple words.** A **successor representation** (SR) is a map that stores, for each
place, where you will probably end up next and later. It sits between two known
strategies: habits (fast, but slow to adapt) and full planning (flexible, but slow). The
claim is that people use something like an SR, and that this shows in behaviour: they
adapt quickly when rewards change, but slowly when the paths between places change.

**How it would work in the brain (if true).**
1. While moving through a task, the brain learns how often each state leads to each other
   state in the future, likely by a TD-style rule (links to H029).
2. Separately, it learns how rewarding each state is.
3. Value is computed by combining the two: the predicted future states times their
   rewards.
4. If a reward changes, only the reward part needs updating, so behaviour adapts fast.
5. If the path structure changes, the whole map must be relearned, so behaviour adapts
   slowly. This asymmetry is the behavioural fingerprint.

**How to test it here.**
Inside the standard test loop:
1. T2: find open behavioural data from revaluation experiments (reward revaluation vs
   transition revaluation), if the authors or others have shared it.
2. Fit three models to each person's choices: model-free, SR, and full model-based.
3. Compare fits with a penalty for model size (for example cross-validated likelihood).
4. Check whether people show the SR asymmetry: better at reward revaluation than at
   transition revaluation.
5. A computer can still do T1 work: simulate the three agents on the same task to confirm
   the predicted asymmetry before fitting real data.

**Counts against it if:** in model comparison on open revaluation data, a model-based
account fits as well as the SR.

**Why it matters for a brain-like learner.** If true, a learner should store a predictive
map, which gives cheap transfer to new rewards. It links to H029 and H066 (successor
features). See [spatial-navigation](../../function/spatial-navigation.md) and
[decision-making](../../function/decision-making.md).
