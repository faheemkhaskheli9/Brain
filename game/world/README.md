# Brain World: a creature that learns on its own

A 3D browser simulation. A creature with a colour retina, a fovea, a cochlea, two legs, an arm and a
pen learns five skills in a row from reward alone: **walk, grasp, listen, read, write**. Nothing is
scripted. It gets a dopamine signal (a reward prediction error), and its synapses change where an
eligibility trace meets that signal. Brain Lab (`game/play.py`) has you operate one mechanism at a time.
Here you watch the mechanisms work together in one learner.

## Run

```
python -m http.server 8000        # from the repo root
# open http://localhost:8000/game/world/
node game/world/test_brain.mjs    # headless check, seed 1, about 90 s
node game/world/test_brain.mjs 1 2 3   # several seeds, as CI runs it
node game/world/perform.mjs brain.json # score a saved brain per skill, learning off
node game/world/sweep.mjs --arms rehearse30,rehearse10+sleep,rehearse0+sleep,rehearse10+sleepActor,rehearse0+sleepActor --jobs 2   # rehearsal vs sleep replay, seeds 1-10 (see "Sleep")
node game/world/sweep.mjs --arms rehearse30,kwta20,kwta35,kwta50 --jobs 2   # k-WTA sparsity (see "Sparsity")
node game/world/sweep.mjs --arms rehearse30,timeoutSense,timeoutBootstrap --jobs 2   # time-limit bootstrapping (see "Timeouts")
node game/world/sweep.mjs --arms copy,copy+si,copy15,copy15+si --jobs 2   # synaptic intelligence and a sixth skill (see "Synaptic intelligence")
```

Three.js loads from the jsDelivr CDN. Everything else is in `brain.js` (simulation, no DOM) and
`index.html` (3D view, panels, sound). Press **Fast forward** to reach graduation in about two minutes.
Then **Watch** shows it practising each skill, with the tones played aloud. **Save brain**
downloads its weights and progress as JSON, and **Load brain** picks up from such a file, so a
graduated creature does not need training again. A loaded brain restarts the episode it was saved in.
Each save carries a `meta` model card (#55): seed, creation time and `GAINS` from birth, plus one
row per save with the perform-mode score of every learned skill. When a skill passes, the
**Checkpoints** list next to Save offers that moment's brain for download.

A first visit opens a three-line intro (reopen it with **What is this?**). A caption under the room
says in plain words what the creature is doing and why dopamine rose or dipped, and every panel label
has a hover explanation.

## The curriculum

| # | Stage | What it must discover | Pass |
|---|---|---|---|
| 1 | Learn to walk | Push a forward leg, lift it again, alternate. Reward: distance covered. | 80% of 50 episodes |
| 2 | Find food and grasp it | Walk to the one object and grasp it within reach | 75% |
| 3 | Listen | Three coloured objects. A tone (262, 392 or 587 Hz) names the colour that is food | 70% |
| 4 | Read | Three white cubes with the letters T, L, X. The tone names the letter, so it must read it with the fovea | 60% |
| 5 | Write | At a board, the tone names a letter. Draw it with two of six pen strokes | 80% |

The letters it reads and the letters it writes are the same 5×5 stroke shapes.

## The brain

- **Senses:** a 15-ray retina (RGB times nearness), a 5×5 fovea that resolves the letter on the
  object in a ±0.2 rad central cone, three cochlea bands, leg position and the pen pad. On the page,
  that cone turns dark violet while a letter is in it.
- **Fovea memory:** a decaying trace of the fovea (×0.9 per step), so the last letter seen stays
  in its senses for a few steps after the gaze moves on. Each leg push turns 0.3 rad, wider than
  the fovea, so a letter is in view for only a step or two. This is a crude stand-in for working
  memory (persistent activity in prefrontal cortex). It is a model choice, not a claim about how
  reading works.
- **Expansion:** 1,000 fixed random units, as in cerebellar granule cells or the mushroom body. Each
  one is driven by one local patch of a sense, and sound scales that drive by a random gain (gain
  modulation). An additive mix learned the tone tasks far too slowly.
- **Context gating, with the context inferred:** each of 8 context slots switches off a fixed random
  half of the expansion units, so each skill mostly trains its own units while the raw senses stay
  shared (context-dependent gating, Masse, Grant and Freedman 2018). The creature is never told the
  task. It pools what it has sensed this episode into 5 bits (something white, something coloured,
  a tone, a letter on the fovea, the board) and picks the slot whose prototype matches; at the end
  of an episode that summary joins its slot or founds a new one (adaptive resonance, Carpenter and
  Grossberg 1987). See "Inferred context" below. That prefrontal cortex gates hidden units this way
  is a hypothesis, not established; that it picks the context by clustering scene summaries is
  also a hypothesis.
- **Actor-critic with traces:** dopamine is `δ = r + γV(s') − V(s)`. Weight change = trace × δ. There
  is no backprop.
- **Habit:** after stage 1 the gait is automatic, so a pushed leg swings forward by reflex. Later
  stages choose which leg to push, or grasp.
- **Replay:** 30% of later episodes rehearse an earlier skill. Without replay, grasp, listen and read
  fell to chance once it learned to write (catastrophic forgetting). Walking is not replayed, because
  its distance reward fought against stopping to grasp. After graduation it cycles grasp, listen,
  read and write.
- **Episodic store and sleep (off by default):** a hippocampus-like ring buffer keeps the last 2,048
  training steps, each written once as it happens. Every `GAINS.sleepEvery` episodes, a sleep phase
  replays 200 of them offline to the critic, with TD(0) and the live traces untouched. It replays a
  step only if the step ended its episode or its true next step is still stored, and it never
  replays a time-limit cut. `GAINS.sleepActor` replays the actor too, with a truncated importance
  weight. The store is saved with the brain. See "Sleep" below.

## What the test shows, and its limits

`test_brain.mjs` asserts every stage is learned within 20,000 episodes. It then asserts that after
graduation each skill stays well above chance: grasp ≥ 0.7, listen ≥ 0.5, read ≥ 0.4, write ≥ 0.5.
Chance is about 0.33 for listen and read, and 1/18 for write. Seed 1 (the page's first brain) passes:
grasp 0.80, listen 0.67, read 0.85, write 0.69. CI runs seeds 1–3.

Across seeds 1–10, 9 pass everything. The tenth (seed 5) keeps read at 0.37, just under the mark.
The fovea memory mainly speeds up reading. On seed 1, read passes in 2,951 episodes instead of
5,699, and it keeps 0.85 instead of 0.52. Over seeds 1–10, read takes 5,400 episodes on average
instead of 6,300, and keeps 0.55 instead of 0.51 (seed 9's 0.38 becomes 0.51, seed 5's 0.53
drops to 0.37). The effect varies a lot between seeds, so the read mark stays at 0.4. A "look"
saccade action that turned the gaze to the next object was tried with it. It sped reading up on
some seeds, but one or two of ten never learned to read, so it was dropped.

With the earlier 600 units and no gating, only 5 of 10 passed: the rest stalled on listen or read,
or kept them too weakly. Most of the gain came from the larger layer: 1,000 units without gating pass
8 of 10. Gating adds a little on top, mostly to listening (mean kept listen 0.70 against 0.62 without
it). Interleaving one network across four tasks still keeps some interference, and reading is
still the weakest skill.

Gating did not let replay drop. With replay at 0.15 instead of 0.3, over seeds 1–10, 9 still pass,
and the write stage passes sooner (7,200 episodes on average instead of 8,800). Mean kept scores
barely move: grasp 0.78 (was 0.82), listen 0.66 (0.69), read 0.55 (0.55), write 0.69 (0.66). But
seed 8 never learns to read within 20,000 episodes, and seed 1 keeps read at 0.52 instead of 0.85.
So replay stays at 0.3.

Last, it saves and reloads the brain and checks that the copy takes the same 2,000 actions as the
original. A second part tests the episodic store with sleep on. A spy records which episode and
step wrote each slot. Then 10,000 replay draws must each have their true next step after:
- the buffer wraps;
- perform mode is switched on and off mid-episode;
- the stage changes mid-episode;
- a save is loaded 40 steps into an episode, which must also store no step twice.

## Sleep: can offline replay replace live rehearsal? (#64)

`node game/world/sweep.mjs [seeds] [--arms ...] [--jobs N]` trains every arm × seed in its own
process and scores the kept skills over 4,000 graduated episodes. Each job needs about 100 MB, so
pass `--jobs 2` on a busy machine. Seeds 1-10, 2026-10-12. The decision rule, fixed in the issue
before the run, was: sleep may take over only if 10% rehearsal plus sleep learns every stage on
at least as many seeds as 30% rehearsal.

| Arm | All stages learned | Kept every skill above the test's bars | Episodes to graduate (mean) | Write stage | Kept grasp / listen / read / write |
|---|---|---|---|---|---|
| 30% rehearsal, no sleep (default) | 10/10 | 9/10 | 18,202 | 8,773 | 0.82 / 0.69 / 0.55 / 0.66 |
| 10% rehearsal + sleep (critic) | 10/10 | 10/10 | 15,058 | 8,665 | 0.76 / 0.66 / 0.54 / 0.67 |
| 0% rehearsal + sleep (critic) | 9/10 | 5/10 | 11,224 | 6,281 | 0.71 / 0.61 / 0.48 / 0.66 |
| 10% rehearsal + sleep (actor too) | 10/10 | 6/10 | 12,347 | 4,639 | 0.72 / 0.62 / 0.47 / 0.67 |
| 0% rehearsal + sleep (actor too) | 9/10 | 6/10 | 8,992 | 2,557 | 0.73 / 0.63 / 0.47 / 0.73 |

Episode means cover the seeds that passed. The comparisons with 30% rehearsal use an exact paired
sign-flip test on per-seed differences, over the seeds that passed in both arms. `sweep.mjs`
prints this table and the p values, and `--from <log>` reprints them from a saved run.
- **10% + critic sleep** passes the decision rule. It saves 3,144 episodes, which is not
  significant (p = 0.21).
- **Replaying the actor** saves 5,854 episodes (p = 0.029) and 4,134 on write (p = 0.002), but
  forgets more.
- **With no rehearsal**, the store holds only recent steps, so old skills fade. Seed 8 (critic
  only) and seed 7 (actor) never learned to read.

Sleep is still off by default, for one reason the rule did not measure. With 10% rehearsal plus
critic sleep, greedy write in perform mode scores 0.67, 0.63 and 0.66 on seeds 1-3 (900 episodes
each), where it was 1.00. Sampling is unchanged at 0.61, 0.58 and 0.62. About 2/3 suggests one of
the three letters now has the wrong most-likely stroke pair; why is not yet known. To try sleep,
set `GAINS.replay = 0.1` and `GAINS.sleepEvery = 20`.

That a brain replays during sleep is established (Wilson and McNaughton 1994). That this ring
buffer works the way the hippocampus selects what to replay is not claimed. Which steps to replay
is open, issue #84.

## Sparsity: k-winners-take-all (#82)

`GAINS.kwta = k` keeps only the k strongest hidden units each step (0, the default, keeps
all). Seeds 1-10, 2026-10-12, 30% rehearsal, no sleep:

| Arm | All stages learned | Kept every skill above the test's bars | Hidden units on per step | Episodes to graduate (mean) | vs default (paired) |
|---|---|---|---|---|---|
| Default (no k-WTA) | 10/10 | 9/10 | 79 | 18,202 | - |
| k = 20 | 10/10 | 10/10 | 20 | 13,642 | -4,560 (p = 0.066) |
| k = 35 | 10/10 | 9/10 | 35 | 16,809 | -1,392 (p = 0.57) |
| k = 50 | 10/10 | 9/10 | 49 | 17,189 | -1,013 (p = 0.64) |

None of the k values slowed learning. k = 20 was faster on 7 of 10 seeds, but not
significantly. The code still updates every trace and weight densely each step, so fewer
active units does not yet mean less work. That would need event-driven updates. The
working is in `learning/efficient-brain-like-learning.md`. k-WTA stays off.

## Timeouts: end the task or bootstrap? (#54)

Grasp, listen and read stop after `GAINS.maxSteps` = 150 steps. The critic treats that cut-off
as the end of the task (`learn(r, null)`): nothing comes after. Pardo et al. (2018) show that
when the time limit is not part of the task, the agent should instead bootstrap from the value of
the state it was cut off in, which is why Gymnasium splits `terminated` from `truncated`. Walk's
60-step limit *is* part of its task (it is scored on distance over time), and write never times
out, so both keep the old rule.

`GAINS.timeoutBootstrap`: 0 (default) ends the task; 1 also senses the cut-off state and throws
it away, which shifts the random stream exactly as bootstrapping does (the control); 2 bootstraps
from it and then clears the traces. Seeds 1-10, 2026-10-12, 30% rehearsal, no sleep:

| Arm | All stages learned | Kept every skill above the test's bars | Episodes to graduate (mean) | Kept grasp / listen / read / write (mean) |
|---|---|---|---|---|
| Default (end the task) | 10/10 | 9/10 | 18,202 | 0.82 / 0.69 / 0.55 / 0.66 |
| RNG control (sense, discard) | 9/10 | 9/10 | 17,802 | 0.82 / 0.68 / 0.61 / 0.66 |
| Bootstrap | 10/10 | 9/10 | 17,130 | 0.81 / 0.70 / 0.52 / 0.66 |

Bootstrap against the control, paired over the 9 seeds both passed: 517 fewer episodes
(p = 0.77), write 980 fewer (p = 0.56). The control's failure is seed 4, which never learned to
read in 20,000 episodes: the random stream alone moves a seed across the line, as it did in the
first, uncontrolled try (7 of 10 seeds, walk bootstrapped too). The rule set before the run was
to switch only if bootstrap passes at least as many seeds as the control **and** lowers no
skill's kept score. It passes more seeds but keeps read lower (0.52 vs 0.61) and grasp slightly
lower, so the default stays 0. With ten seeds, no difference here is distinguishable from seed
noise; the theory says bootstrapping is right, and this agent is too noisy to show it.

## Innate prior: an orienting reflex (#83)

`GAINS.orient = g` adds a fixed bias that is never learned to the two leg-push logits:
`g × (left − right object salience)`, where salience per ray is `max(r, g, b) − 0.2`,
clipped at 0, so walls do not count. It turns the agent toward the brighter side. 0 (the
default) is off. Issue #83 crossed it (gain 1, untuned) with a better learning rule, actor
sleep replay, at 30% rehearsal. Seeds 1-10, 2026-10-12, passed / mean episodes:

| Arm | Grasp | Listen | All five |
|---|---|---|---|
| Default | 10/10, 840 | 10/10, 3,042 | 10/10, 18,202 |
| Reflex | 10/10, 53 | 3/10, 13,492 | 3/10, 34,047 |
| Actor sleep | 10/10, 808 | 10/10, 2,369 | 9/10, 16,322 |
| Reflex + actor sleep | 10/10, 77 | 6/10, 13,806 | 3/10, 29,160 |

The reflex makes grasp almost free (759 episodes saved, p = 0.002), then blocks listen: the
right object is the one that matches the tone, and the weights have to outweigh a bias that
always points at the brightest one. It stays off. The full table and the per-stage effects are
in `learning/efficient-brain-like-learning.md`. Running 16 jobs at once crashed one child out
of memory; it was re-run alone with `--jobs 1`.

## Synaptic intelligence and a sixth skill (#56)

Rehearsal protects the five skills only because they keep being practised. Issue #56 asked
whether a loaded brain forgets them when it learns a sixth, and whether synaptic intelligence
(SI; Zenke, Poole and Ganguli 2017) would let rehearsal drop from 0.3 to 0.15. SI is on top of the
gating, the pairing used by Masse, Grant and Freedman (2018).

**How SI works here.** Each actor and critic synapse keeps three numbers:
- `omega`, this stage's path integral of its learning (`dw² / lr`);
- `Omega`, its importance, summed over the passed stages;
- `anchor`, its value at the last stage pass.

Every update adds a pull back to the anchor of `min(1, si · lr · Omega)` of the way. At each
stage pass, `Omega += omega / ((w − anchor)² + 1e-3)`, the anchor moves to the current weights and
`omega` resets. `GAINS.si = 0` (the default) tracks nothing and only re-anchors at each pass, so
the CI output did not change line for line. Saves are now version 5 and hold `syn`, all three
numbers per synapse; a version-4 save migrates with `Omega = 0`.

**The sixth skill is copy** (`COPY`, added to `STAGES` only by the sweep). The creature is at the
board, there is no tone, and the target letter is shown on the fovea, so it must draw what it
sees. Its scene code `[0,0,0,1,1]` is new, and nothing in `Brain` changed for it.

**The run.** Each seed trains the five stages and saves. The save is loaded into six-stage code
(`growStages` resumes it at copy), and the old skills are scored in perform mode (300 episodes
each). The brain then learns copy for up to 20,000 episodes, and the old skills are scored again.

**Choosing the SI strength.** A pilot on seeds 1-2 settled it. With `si` = 0.1, 1 or 10, neither
seed learned listen. With 1e-2, neither seed learned it. With 1e-3, one of the two did not. Only
1e-4 let both learn every stage. Reward-driven updates are mostly noise, so for most synapses
`omega ≈ Δ²/lr` and `lr · Omega ≈ 1`: `si` is close to the share of the way pulled back on every
step. So the run uses `si` = 1e-4.

Seeds 1-10, 2026-10-13, `--jobs 6`:

| Arm | Five stages learned | Kept every skill above the bars | Copy learned | Copy episodes (mean) | Own slot for copy | Old grasp / listen / read / write, before → after copy | Mean drop |
|---|---|---|---|---|---|---|---|
| Rehearsal 0.3 (default) | 9/10 | 9/10 | 7/9 | 7,845 | 9/9 | 0.88→0.89 / 0.73→0.73 / 0.61→0.64 / 0.86→0.85 | −0.009 |
| Rehearsal 0.3 + SI | 7/10 | 6/10 | 7/7 | 10,999 | 7/7 | 0.83→0.83 / 0.56→0.56 / 0.48→0.47 / 0.95→0.96 | −0.003 |
| Rehearsal 0.15 | 9/10 | 9/10 | 9/9 | 12,170 | 9/9 | 0.83→0.85 / 0.70→0.69 / 0.60→0.60 / 0.75→0.78 | −0.007 |
| Rehearsal 0.15 + SI | 6/10 | 5/10 | 5/6 | 9,278 | 6/6 | 0.80→0.78 / 0.58→0.57 / 0.52→0.52 / 0.92→0.89 | +0.014 |

The default arm reproduces the "Inferred context" row exactly (9/10, 16,515 episodes), so saving,
loading and the new code changed nothing.

**What it shows:**
- **Learning copy made the brain forget nothing**, in any arm. The mean drop over the four old
  skills is within ±0.015, inside perform-mode noise at 300 episodes. Copy founded its own
  context slot on every one of the 31 runs that reached it, with 100% of its episodes there. So it
  trains its own half of the hidden units, and rehearsal covers the ~25% the masks share.
- **SI only cost.** It lost 2-3 seeds in the first five stages (listen on seeds 3 and 6, read on
  seed 5) and lowered kept listen and read. Against rehearsal 0.3, SI with rehearsal 0.15 dropped
  0.018 more (p = 0.094, n = 6, paired sign-flip).
- **The hypothesis is not supported**, and its premise did not hold: there was no forgetting
  for SI to prevent. Rehearsal 0.15 without SI also forgot nothing. SI stays off.
- **Copy is the slow stage.** At rehearsal 0.3 it missed the 80% mark within 20,000 episodes on
  seeds 4 and 7; at 0.15, all 9 learned it. More episodes of the new skill helped more than
  protecting the old ones.

That synapses are tagged and later captured for long-term change is established (synaptic tagging
and capture, Frey and Morris 1997). That real synapses keep an SI-like importance is a hypothesis.

## Perform mode: using a trained brain

`world.perform(key)` locks every episode to one skill and turns learning off: the brain acts and
still computes dopamine, but no weight, success window, log entry or stage changes. `perform(null)`
goes back to training. A save made while performing resumes training on its own stage.
`perform.mjs` scores a save this way (`--seed N` trains that seed to graduation in memory instead).
On the page, the skill picker next to Load does the same: pick a skill to watch the loaded brain use
it (the banner counts its successes and the learning curve stays still), or "Train" to resume.
With learning on, every action and random draw is the same as before, so training episode counts
did not change.

With learning off, exploring is no longer needed for learning, so a skill can take its most likely
action (greedy) instead of sampling. That only helps some skills. `node game/world/perform.mjs
--seed N --greedy ""` (all sampling) against `--greedy walk,grasp,listen,read,write` (all greedy),
500 episodes per skill on each seed's graduation brain:

| Skill | Sampling (seeds 1, 2, 3) | Greedy (seeds 1, 2, 3) |
|---|---|---|
| walk | 0.99, 0.99, 0.79 | 1.00, 1.00, 1.00 |
| grasp | 0.81, 0.75, 0.83 | 0.67, 0.58, 0.72 |
| listen | 0.66, 0.72, 0.59 | 0.29, 0.77, 0.40 |
| read | 0.85, 0.61, 0.50 | 0.62, 0.36, 0.14 |
| write | 0.67, 0.52, 0.64 | 1.00, 1.00, 1.00 |

So `GAINS.performGreedy` is walk and write, the default for `perform`. Grasp, listen and read are
searches: a fixed policy turns the same way from the same view forever, and in a partially
observed task the best memoryless policy can be stochastic (Singh, Jaakkola and Jordan 1994). A
temperature between 0 and 1 for the search skills is the next knob to try (untested).
`test_brain.mjs` performs each kept skill for 200 episodes on the trained brain, asserts it stays
at the kept bar, and asserts the weights, slot prototypes and stage are unchanged.

**Free play (#62).** `perform("any")` (page: "Use: any scene") draws a random scene each episode
and never says which. Since the brain infers its context slot (#60), it has to find the skill
itself; greedy follows the scene's entry in `performGreedy`. `perform.mjs --seed N any` prints the
success rate per scene and the share of steps on its most used slot. Seed 1, 1,000 episodes: walk
1.00 (slot 0 on 100% of steps), grasp 0.79 (86%), listen 0.61 (93%), read 0.55 (86%), write 1.00
(100%). `test_brain.mjs` runs 1,000 free-play episodes per seed and holds each kept scene to the
kept bar. On seeds 1-3, free play scored grasp 0.85 / 0.85 / 0.80, listen 0.70 / 0.77 / 0.67,
read 0.59 / 0.83 / 0.53 and write 1.00 on all three, against the one-skill runs' grasp
0.84 / 0.86 / 0.86, listen 0.69 / 0.78 / 0.56, read 0.61 / 0.85 / 0.51. A task-blind greedy
rule (greedy wherever `max pi > 0.5`) instead of the per-skill list is an untested hypothesis.

## Inferred context: one model, no task index (#60)

Until 2026-10-13 the brain was handed the stage index, which picked its gate row. Now nothing in
`Brain` is sized or indexed by task. `World.context()` returns `brain.infer(z)`, where `z` is the
running max over the episode of `scene(x)`, five thresholded channels. `infer` picks the used slot
whose prototype is within `GAINS.vigilance` (0.35) of `z` on every channel, the nearest if several
are, otherwise a free slot. `commit(z)` runs once per training episode: `z` joins that prototype
(rate 0.05) or founds a new one. With every slot used it first reclaims one used fewer than
`GAINS.minUses` (20) times, and only then merges into the nearest. Perform mode commits nothing.

`test_brain.mjs` checks the design statically (no `STAGES` in `Brain`, no `encode` call is passed
the task, `context()` reads no task field) and with a spy: every live `encode` gets the slot `infer`
just returned. Over the 4,000 graduated episodes, each kept skill must end at least 95% of its
episodes in one slot and spend at least 70% of its steps there, and the four skills must use four
different slots. Perform mode must leave the prototypes and use counts unchanged.

`node game/world/sweep.mjs --arms rehearse30 --jobs 6`, seeds 1-10, 2026-10-13:

| | All stages learned | Kept every skill above the test's bars | Episodes to graduate (mean) | Write stage | Kept grasp / listen / read / write |
|---|---|---|---|---|---|
| Told the task (before, 2026-10-12) | 10/10 | 9/10 | 18,202 | 8,773 | 0.82 / 0.69 / 0.55 / 0.66 |
| Infers the task | 9/10 | 9/10 | 16,515 | 10,089 | 0.87 / 0.70 / 0.59 / 0.65 |

Slot use over the 9 that graduated: the share of episodes ending in the skill's own slot is 1.000
for grasp, listen and write and 0.999 for read. The share of steps there is 0.82 (grasp), 0.95
(listen), 0.90 (read) and 1.00 (write); the opening steps run under another slot until the cue
arrives (grasp starts out looking like walk). All 9 use four distinct slots, and 5 to 7 of the 8
slots end up used: one per skill plus walk, and on 5 seeds one or two strays holding 1 to 124
episodes whose summary missed a channel (a read episode that never fixated a letter). Seed 8 never learns to read within 20,000 episodes. Its inference is right
(99.6% of read episodes land in the read slot); read stays at 0.34, so it is the random gate
mask, as the arena run found for its seed 10. The two rows differ in their random draws (8 gate
rows instead of 5), so the 9 vs 10 is within seed variance, not a measured cost.

Honest limits:
- The thresholds (white > 0.3, colour > 0.1, tone > 0.5, fovea > 0.1) were picked knowing the five
  scenes. A continuous `z`, and thresholds x0.5 and x1.5, are the A/B still to run.
- The board bit still means "task is write" until a second board task exists.
- The action set comes from the body and development, not the mode (#61): pen at the board
  (`world.board`, set by the world when it puts the creature there), otherwise the gait habit
  (legs reset by reflex, push or grasp) once the brain is past stage 0, otherwise the full body set.
  Reward and time limit still branch on the mode: they are the world's rules, not the brain.
  Training never replays walk, so the habit is off exactly on walk episodes: `test_brain.mjs 1 2 3`
  prints the same output as before, line for line (2026-10-13). Walk on a graduated brain
  (perform, free play) now runs under the habit: `perform.mjs --seed N walk` scores 1.00 on seeds
  1-3 both sampling and greedy (was 0.99 / 0.99 / 0.79 sampling, 1.00 greedy).
- Saves were version 4 here (they hold `proto` and `uses`; version 5 adds the SI record, #56). `World.migrate` (#63) loads older and
  smaller ones: a version 3 save's five told gate rows become five slots whose prototypes are the
  scene codes of their stages, with 50 uses each; a save with fewer slots than `GAINS.slots` gets
  free rows appended; a save with fewer stages gets empty windows, and a graduated one resumes at
  the first new stage. `fixtures/v3-seed1.json` (seed 1, trained to graduation by the told-gate
  code, saved without its episodic store) still reads at 0.80 after migrating, with 80% of its
  read steps in slot 3. A save at 8 slots performs identically at 12. `sweep.mjs` now prints, per
  seed, the slots in use with their counts, each skill's step share, and its reclaims and merges
  (seeds 1-2: none).
- Saves carry a `meta` model card (#55), and every graduated seed in `sweep.mjs` now goes
  through a real save and load: each row holds the save's perform-mode scores and git commit.
  Re-run 2026-10-13 (`--arms rehearse30 --jobs 6`): the same 9/10 passed, 9/10 kept, 16,515
  episodes, kept 0.87 / 0.70 / 0.59 / 0.65 as above, so saving changes nothing. Perform mode
  (100 episodes per skill, mean over the 9 seeds): walk 1.00, grasp 0.90, listen 0.72, read 0.60,
  write 0.86. Write is 1.00 on five seeds and 0.67-0.72 on four. A save with its store is about
  0.64 MB, and scoring adds about 0.7 s to each save.

All learning rates, costs and sizes in `GAINS` are game gains: tuning knobs, not measurements. The
claims the page marks as established are that dopamine signals reward prediction error, that
plasticity needs a trace plus a neuromodulator, and that replay protects old memories. That this stack
is enough for a real brain's version of these skills is a hypothesis.

## The science behind it

| Mechanism here | Topic file |
|---|---|
| Dopamine as TD error, eligibility traces, three-factor rule | [learning-and-plasticity](../../function/learning-and-plasticity.md) |
| Replay of earlier skills against forgetting | [memory-systems](../../function/memory-systems.md), [sleep-and-memory-consolidation](../../function/sleep-and-memory-consolidation.md) |
| Sound scaling visual drive (gain modulation) | [neural-coding-and-computation](../../function/neural-coding-and-computation.md) |
| Task-context gating, fovea memory as working memory | [attention-and-working-memory](../../function/attention-and-working-memory.md) |
| Actor-critic plus replay as one learner | [build-a-brain-like-learner](../../guides/build-a-brain-like-learner.md) |
| Save brain and Load brain: what the file holds and why | [saving-and-reusing-a-trained-brain](../../simulation/saving-and-reusing-a-trained-brain.md) |

## Not done yet

- Real vision from rendered pixels. The retina is ray-cast, so it runs headless and fast.
- Speech or spoken words instead of pure tones. Multi-letter words.
- Physics-based limbs (joint torques) instead of discrete leg states.

## References

- McClelland, McNaughton and O'Reilly (1995) "Why there are complementary learning systems in the
  hippocampus and neocortex", *Psychol Rev* 102:419. doi:10.1037/0033-295X.102.3.419
- Munos, Stepleton, Harutyunyan and Bellemare (2016) "Safe and efficient off-policy reinforcement
  learning" (Retrace), NeurIPS. arXiv:1606.02647
- Wilson and McNaughton (1994) "Reactivation of hippocampal ensemble memories during sleep",
  *Science* 265:676. doi:10.1126/science.8036517
- Masse, Grant and Freedman (2018) "Alleviating catastrophic forgetting using context-dependent
  gating and synaptic stabilization", *PNAS* 115:E10467. doi:10.1073/pnas.1803839115
- Carpenter and Grossberg (1987) "A massively parallel architecture for a self-organizing neural
  pattern recognition machine", *Computer Vision, Graphics, and Image Processing* 37:54.
  doi:10.1016/S0734-189X(87)80014-2
- Pardo, Tavakoli, Levdik and Kormushev (2018) "Time limits in reinforcement learning", ICML.
  arXiv:1712.00378
- Zenke, Poole and Ganguli (2017) "Continual learning through synaptic intelligence", ICML.
  arXiv:1703.04200
- Frey and Morris (1997) "Synaptic tagging and long-term potentiation", *Nature* 385:533.
  doi:10.1038/385533a0
- Singh, Jaakkola and Jordan (1994) "Learning without state-estimation in partially observable
  Markovian decision processes", *Proceedings of ICML 1994*, 284-292.
