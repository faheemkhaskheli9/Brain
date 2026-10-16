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
# open http://localhost:8000/game/world/?body=cpg   # jointed legs and a pattern generator (see "Jointed legs")
node game/world/test_brain.mjs    # headless check, seed 1, about 90 s
node game/world/test_brain.mjs 1 2 3   # several seeds, as CI runs it
node game/world/perform.mjs brain.json # score a saved brain per skill, learning off
node game/world/sweep.mjs --arms rehearse30,rehearse10+sleep,rehearse0+sleep,rehearse10+sleepActor,rehearse0+sleepActor --jobs 2   # rehearsal vs sleep replay, seeds 1-10 (see "Sleep")
node game/world/sweep.mjs --arms rehearse30,kwta20,kwta35,kwta50 --jobs 2   # k-WTA sparsity (see "Sparsity")
node game/world/sweep.mjs --arms rehearse30,timeoutSense,timeoutBootstrap --jobs 2   # time-limit bootstrapping (see "Timeouts")
node game/world/sweep.mjs --arms copy,copy+si,copy15,copy15+si --jobs 2   # synaptic intelligence and a sixth skill (see "Synaptic intelligence")
node game/world/sweep.mjs --arms transfer --jobs 4   # new letters: does what it learned transfer? (see "New letters")
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

**Teach** in the skill picker makes you the teacher (see "Teach mode" below). Drop cubes and balls
by clicking the floor, play a tone, and watch it fetch. **Give reward** (key R) works in every mode.

## The curriculum

| # | Stage | What it must discover | Pass |
|---|---|---|---|
| 1 | Learn to walk | Push a forward leg, lift it again, alternate. Reward: distance covered. | 80% of 50 episodes |
| 2 | Find food and grasp it | Walk to the one object and grasp it within reach | 75% |
| 3 | Listen | Three coloured objects. A tone (262, 392 or 587 Hz) names the colour that is food | 70% |
| 4 | Read | Three white cubes with the letters T, L, X. The tone names the letter, so it must read it with the fovea | 60% |
| 5 | Write | At a board, the tone names a letter. Draw it with two of six pen strokes | 80% |
| 6 (optional) | New letters | At the board, no tone. One of three new letters (Γ, ⊥, 7) is shown on the fovea. Each is two strokes it already writes, from two different old letters. Draw it | 80% |

The letters it reads and the letters it writes are the same 5×5 stroke shapes. Stage 6 is off by
default, like copy (#56): `STAGES.push(NEW)` adds it, and a graduated save loads into it and
resumes there. See "New letters" below.

## The brain

- **Senses:** a 15-ray retina (RGB times nearness), a 5×5 fovea that resolves the letter on the
  object in a ±0.2 rad central cone, three cochlea bands, leg position (hip angles on the jointed
  body) and the pen pad. On the page, that cone turns dark violet while a letter is in it.
- **Two bodies:** `GAINS.body = "legs"` (the default, and the one CI trains) has two legs, each
  forward or back. A push of a forward leg moves the creature 0.22 and turns it 0.3 rad.
  `GAINS.body = "cpg"` (page: `?body=cpg`) has jointed legs. Each hip angle follows a damped spring
  toward a target set by a central pattern generator: two phase oscillators coupled in antiphase
  (Ijspeert 2008). The actor never sets a joint. Its five actions set how hard each side swings for
  one step: step turning left, step turning right, step straight, stand, and grasp (which pauses the
  rhythm). A foot is down during the back-swing half of its cycle, and the body moves as far as the
  planted foot goes back, so forward motion comes from the stance phase. Each foot pushes its own
  side, so unequal swings turn the body. A world is born with `GAINS.body`, the save records it, and
  a save from before #38 loads as `"legs"`. See "Jointed legs" below.
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
original. The new-letter stage (#37) is checked on `fixtures/v3-seed1.json`, which resumes at it: it
must learn Γ, ⊥ and 7 within 8,000 episodes (it takes 4,669), a save made 500 episodes in must take
the same 2,000 actions, and a drawn letter must be graded against the new letters, not T, L and X. A second part tests the episodic store with sleep on. A spy records which episode and
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

So `GAINS.performGreedy` is walk and write (and the optional board skills copy and new letters), the default for `perform`. Grasp, listen and read are
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

## Teach mode: the viewer as teacher (#36)

`world.teach({objects: [{pos: [x, y], letter: 0-2} or {pos, color: 0-2}], tone: 0-2 or -1}, learn)`
replays the viewer's room every episode, with the creature dropped somewhere clear of the
objects. The target is the first object the tone names. A cube's letter or a ball's colour counts,
and grading follows the listen and read rules. It runs on the perform-mode machinery: the
curriculum, success windows and episodic store are untouched, and actions are sampled. With
`learn = true` (the page's default, "It learns from this") the weights do change. `world.reward(r)`
adds `r` to the next step's reward, so it reaches the brain only through the TD error, as food
does. It works in every mode. On the page, picking **Teach** shows a row to choose what a floor
click drops (a click on an object takes it away, six at most), to play a tone, and to clear the
room.

`test_brain.mjs` checks the mechanics on each graduated seed: the room and target are the viewer's,
the creature never starts on an object, `reward(1)` makes that step's dopamine exactly 1 higher,
and with learning on the weights change but the curriculum does not. It prints the fetch rates
and holds them to no bar. Here is why. A single fixed room depends on its layout far more than the
random rooms the brain trained in. Learning off, 300 tries per room, on graduated seeds 1 / 2 / 3
(2026-10-13):

| Room | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|
| Lone T cube at (2, 6), low tone | 0.98 | 0.96 | 0.31 |
| Lone T cube in a corner (1, 1) | 0.93 | 0.83 | 0.14 |
| T, L, X spread out, tone names L | 0.34 | 0.92 | 0.92 |
| Same room, tone names T | 0.91 | 0.79 | 0.13 |
| T, L, X in a row at y = 6, tone names X | 0.45 | 0.72 | 0.46 |
| Red, green, blue balls, tone names green | 0.66 | 0.82 | 0.51 |
| Read in random rooms (perform) | 0.56 | 0.75 | 0.49 |

Averaged over these rooms, the rate is close to the random-room read rate. A single room swings
from 0.13 to 0.98, though, even for one cube with nothing to confuse it with. Each room is one fixed
set of views, so a policy that turns the same way at the same view either always reaches the cube
or never does. Random rooms average that out. So the issue's check ("drop a T cube, play its tone,
watch it fetch") holds on seeds 1 and 2 and fails on seed 3 in these rooms, until it is taught.
With learning on in that room, the seed 3 lone-T-cube rate (scored with learning off, 300 tries)
went from 0.31 to 0.70 after 100 taught tries, 0.90 after 400 and 0.93 after 1,400. Read in random
rooms stayed close to where it was: 0.48, 0.39 and 0.45 after those three, against 0.49 before.
That is one seed and one room, so the size of the cost to other rooms is not established.

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

## Surprise: telling look-alike contexts apart (#65)

Slots are picked by the scene, so two rules that share a scene share a slot and overwrite each
other. Issue #65 item 1 asked whether the brain can split them by surprise instead, as multiple
model RL (Doya, Samejima, Katagiri and Kawato 2002) and COIN (Heald, Lengyel and Wolpert 2021) infer
context from prediction error.

**How it works.** Each training episode adds up its squared TD errors (`epErr`). At `commit`, the
slot the episode played in keeps a fast (about 5 episodes) and a slow (about 50) running mean of
it. When `fast > GAINS.surprise × slow` on a slot past `minUses` episodes, the scene's slot gets an
`alias`. It points to the calm sibling with the lowest normal error that has not failed since the
last calm episode. If there is none, a free slot is founded as a new sibling (`parent` = the scene
slot). Siblings never match scenes themselves, so `infer` reaches them only through the alias.
`alias`, `parent`, `fast`, `slow` and `seen` are saved as `brain.ctx`. A save without them loads
with none, and `GAINS.surprise = 0` (the default) never calls the detector. So nothing else changed:
`test_brain.mjs` passes as before, and its new check drives the detector with made-up errors. It
must switch to a new sibling, back to the original, back to the sibling, and found a third.

**The task.** `world.reversed = true` remaps listen's tones (low = blue, middle = red, high =
green). The scene is identical, so only the outcomes say the rule changed. `sweep.mjs --arms
reversal` trains each seed to graduation and saves. From that same save it runs six blocks of 1,000
listen episodes, alternating normal (N) and reversed (R), with no rehearsal and no stage passes.
It does this twice, with surprise 0 and with surprise 3.

Seeds 1-10, 2026-10-13, `--jobs 10` (seed 8 did not learn read, so n = 9). Success in each block's
first / last 50 episodes:

| Surprise | N | R | N | R | N | R | Switches (mean) |
|---|---|---|---|---|---|---|---|
| off | 0.71 / 0.83 | 0.02 / 0.06 | 0.11 / 0.78 | 0.02 / 0.09 | 0.20 / 0.79 | 0.02 / 0.09 | 0 |
| on (3) | 0.71 / 0.83 | 0.07 / 0.14 | 0.21 / 0.60 | 0.04 / 0.08 | 0.15 / 0.50 | 0.04 / 0.10 | 7.1 |

**What it shows:**
- **No savings.** On the return blocks (3-6), surprise raised first-50 success by +0.026, which is
  not significant (p = 0.25, paired sign-flip, n = 9). On one seed (7) the first return to N started
  at 0.66, against 0.12 without surprise. That is the hoped-for effect, but only once.
- **It cost the normal rule.** Last-50 success on N fell to 0.60 and 0.50 (off: 0.78, 0.79).
  Binary outcomes make the 5-episode mean noisy, so the detector also fires inside N blocks (seed 6:
  29 switches), and each false switch lands on a slot that does not know the rule.
- **The reversed rule was rarely relearned in either arm.** On 6 of 9 seeds R stayed near 0, below
  the 0.33 that grasping at random would score. The creature keeps grasping the colour the old rule
  named, and an unrewarded block gives the actor no positive TD error to learn from. A pilot with
  blocks of 400 and surprise 2 (seeds 1-2) was worse: 10 switches and lower N.
- **The hypothesis is not supported at this setting**, so `GAINS.surprise` stays 0. Inference was
  not the bottleneck; relearning in a fresh slot was. Untested next steps: a detector that needs
  more evidence (a Bayesian belief over siblings, as COIN keeps), and siblings that do not share
  the raw senses and the old rule's actor weights (the 25% of units the masks share, plus `x`).

That the brain infers which memory to express from prediction error has behavioural support (COIN
explains savings and spontaneous recovery in motor adaptation). This detector is a toy version.

## Jointed legs: a pattern generator body (#38)

Issue #38 asked for limbs with joints instead of two leg states. Its research notes ruled out
learning raw joint torques with the linear actor-critic. Instead, the discrete actions modulate a
central pattern generator (CPG), as spinal circuits do in animals
(established; Ijspeert 2008 reviews CPGs in animals and robots). The discrete body stays the CI body.

**The body** (`GAINS.body = "cpg"`, page `?body=cpg`, constants in `CPG`). A world step is 0.25 s,
integrated in ten 25 ms substeps, and the rhythm runs at 1 Hz, so each leg takes one stride every
four steps. Each hip angle θ follows `θ'' = k(target − θ) − cθ'` (k 160, c 18). The target is
`amp × drive × cos φ`, where the phases φ of the two legs are oscillators coupled toward antiphase.
A foot is down while `sin φ > 0`, the back-swing half. Then the body moves forward by as much as the
foot goes back (`leg × Δ sin θ`), and turns by `yaw` (2.4 rad per unit) times that push, the left
foot turning it right. The hip lags its target, so early in each stance the foot still swings
forward and pulls the body back a little. The five actions set the drive on each side for one step:
step turning left (left −0.5, right 1, so the left leg walks backward), step turning right, step
straight (1, 1), stand (0, 0), and grasp, which pauses the rhythm. The two hip angles, scaled to
[0, 1], take the inputs that hold leg position on the discrete body, so the brain's size and wiring
are unchanged. After walk, the habit drops "stand" and keeps the other four (`ACT_SETS[3]`). The
discrete habit set has no straight step, and on this body alternating the two turns walks at
only 0.031 per step. Reward and pass rule are unchanged: 2 × forward progress, and an episode passes
above 0.08 per step. As on the discrete body, sliding along a wall counts as distance.

**Fixed policies,** 300 walk episodes each (2026-10-16): uniform random over the five actions passes
0.00 of episodes (0.039 per step). Always stepping straight passes 0.78 (0.089 per step), because it
stalls at walls. Stepping straight and turning left whenever a wall is within 1.5 ahead passes 1.00
(0.117). In open floor, a straight step covers 0.137 per step, and a turn covers 0.033 while turning
0.249 rad. So walking has to be learned: keep the rhythm on, and turn away from walls.

**Learned walk** (0.8 over a 50-episode window): seeds 1-5 pass in 104, 67, 164, 330 and 65
episodes. Seed 1 on the discrete body takes 99. To reproduce (about 10 s):

```
node --input-type=module -e 'import { World, GAINS } from "./game/world/brain.js"; GAINS.body = "cpg"; for (const s of [1, 2, 3, 4, 5]) { const w = new World(s); while (w.stage === 0) w.step(); console.log(s, w.episode); }'
```

`test_brain.mjs` checks seed 1 within 1,000 episodes, that an untrained brain passes 0 of 100 walk
episodes, that a CPG save reloads with its body and takes the same actions for 300 steps, and that
`fixtures/v3-seed1.json` loads as `"legs"`. The page learns walk on seed 1 in 104 episodes too, so the
browser and Node compute the same gait.

**What it does not do yet.** On seed 1 (one seed only), the full curriculum on this body is much
slower. Grasp takes 9,284 episodes (discrete: 437), listen 14,826 (discrete: 1,561), and read is
not learned within 20,000. Two other settings were tried on seed 1. Yaw 1.5 with a turn drive of
−0.6 learned walk in 676 episodes but not grasp within 20,000. Yaw 1.2 turning in place (drive −1)
learned walk in 1,249 but not grasp. Two causes are likely, though neither is tested. The straight gait swings the
heading by about ±0.6 rad per stride, so a target leaves the fovea's ±0.2 rad cone. And the brain
senses hip angles but not hip velocity or phase, so a reactive policy cannot tell which leg is about
to push. An earlier version measured progress along the heading, so sliding along a wall did not
count. None of five settings then learned walk within 3,000 episodes on seeds 1-3: success stayed at
0.3-0.5, the level of walking straight into walls. The body is kinematic: no masses, no slip, no
torques. That this body says anything about how animals learn to walk is not claimed.

## New letters: does what it learned transfer? (#37)

Issue #37 asked whether a new letter built from strokes it already knows is learned faster than
its first letters were, as a measure of learning to learn. Monkeys that solve hundreds of
discrimination problems solve each new one faster (learning sets, Harlow 1949), and Lake, Ullman,
Tenenbaum and Gershman (2017) list learning to learn among what a human-like learner needs.

**The stage.** `NEW` (stage 6, optional) shows one of three new letters on the fovea at the board,
with no tone, and grades the two strokes drawn against it:
- Γ is T's top bar plus L's left bar;
- ⊥ is T's middle bar plus L's bottom bar;
- 7 is T's top bar plus X's /.

So no new letter is an old one, and every stroke is one it has drawn. A tone cannot name them. The
cochlea has three bands and they already name T, L and X, so a tone for a new letter would overwrite
an old one in write's slot. The stage works like copy (#56), with the same scene code
`[0,0,0,1,1]`, and nothing in `Brain` changed. `World.reset` sets the board's alphabet
(`world.letters`); cubes always carry T, L and X.

**The run.** `sweep.mjs --arms transfer` trains each seed to graduation and saves, as the default
arm does. Each learner below then trains one stage until it passes (80% of 50) or has played 20,000
episodes of that stage. Only episodes of that stage count, not rehearsal:
- the graduated brain, with rehearsal 0.3 (the default) and with none;
- the control that cannot reuse what it learned: the same save with its learned weights (actor and
  critic) set to zero, also with and without rehearsal. It keeps the wiring, gate masks, context
  slots and random stream, so only what it learned differs;
- the same seed untrained (a new `World`, no rehearsal, since it has nothing to rehearse);
- copy of T, L and X, then the new letters: one task, first on letters it knows, then on new ones;
- its own write stage (its first letters), from the graduation run.

Zero-shot is sampled perform-mode success before any training on the stage, over 300 episodes.
Random strokes score 1/18 = 0.056.

How the design changed: the plan was to compare the graduated brain with the untrained one. A
probe on the fixture and three untrained seeds ran first. During the first sweep, a check found
that rehearsal changes the step size (below). So the zeroed control and the arms without rehearsal
were added, and the sweep was re-run from the start. Three seeds of the first run had been seen by
then.

Seeds 1-10, 2026-10-16, `--jobs 4`, 16 minutes. Seed 8 does not learn read, as in "Inferred
context", so n = 9. Graduation matched that row exactly: 9/10, 16,515 episodes, kept
0.87 / 0.70 / 0.59 / 0.65.

| Learner (new letters unless named) | Rehearsal | Learned | Episodes, mean | Median |
|---|---|---|---|---|
| Its first letters: write T, L, X by tone | 0.3 | 9/9 | 7,037 | 7,171 |
| Graduated | 0.3 | 9/9 | 5,314 | 5,175 |
| Weights zeroed | 0.3 | 9/9 | 4,498 | 3,075 |
| Graduated | none | 9/9 | 9,591 | 8,269 |
| Weights zeroed | none | 9/9 | 7,503 | 7,047 |
| Untrained | none | 8/9 | 6,054 | 5,986 |
| Copy T, L, X, graduated | 0.3 | 9/9 | 7,883 | 6,075 |
| New letters after copy T, L, X | 0.3 | 9/9 | 6,858 | 5,819 |

Paired over the seeds that learned both (positive = the second is faster), with a 95% bootstrap
interval of the mean and the exact sign-flip p:

| Comparison | Difference | 95% interval | p | n |
|---|---|---|---|---|
| Untrained − graduated (the plan) | +1,286 | 594 to 2,083 | 0.023 | 8 |
| Its first letters − graduated | +1,723 | 298 to 3,205 | 0.063 | 9 |
| Zeroed − graduated, rehearsal | −816 | −1,995 to 530 | 0.25 | 9 |
| Zeroed − graduated, no rehearsal | −2,088 | −5,695 to 1,443 | 0.31 | 9 |
| No rehearsal − rehearsal, graduated | +4,278 | 2,134 to 7,197 | 0.004 | 9 |
| No rehearsal − rehearsal, zeroed | +3,005 | −223 to 6,170 | 0.11 | 9 |
| Copy T, L, X − new letters after it | +1,025 | −1,056 to 3,865 | 0.63 | 9 |
| New letters − new letters after copy | −1,544 | −4,529 to 1,195 | 0.32 | 9 |

Zero-shot: new letters 0.049, copy of T, L and X 0.088, new letters after learning copy 0.049.

**What it shows:**
- **The planned test looks like transfer.** The graduated brain learns the new letters in 1,286
  fewer episodes than the untrained one (p = 0.023), and 1,723 fewer than its first letters took
  (p = 0.063).
- **What it learned is not the reason.** With its learned weights zeroed it was not slower. On
  average it was faster, by 816 episodes with rehearsal (p = 0.25) and 2,088 without (p = 0.31).
  Neither is significant: the data fit no effect or a small cost of the old weights, not a benefit.
- **Rehearsal is.** Without rehearsal, the graduated brain needed 4,278 more episodes (p = 0.004).
  The step size is `lr / (1 + mean |h|²)`, a running mean over every step. Rehearsal fills that
  mean with room steps, whose |h|² is smaller than the board's, so each board update moves the
  policy further. On the fixture (a one-off probe), `|h|² / (1 + mean |h|²)` on board steps was 1.50
  for the graduated brain with rehearsal and 2.44 for the zeroed one, whose untrained rehearsal
  episodes run to the 150-step limit. It was 0.99 for both without rehearsal.
- **A larger step alone covers the gain.** Untrained brains on seeds 1-10, with no rehearsal and
  both learning rates scaled up, took 5,872 episodes on average at x1 (seed 10 not within 20,000),
  4,525 at x1.5 and 3,335 at x2.5. At x1.5 they were 700 episodes faster than the graduated brain
  with rehearsal (p = 0.10, n = 9).
- **No learning set.** Learning to copy T, L and X first did not speed up the new letters (1,544
  episodes slower on average, p = 0.32). Copying the letters it already writes was not faster than
  copying new ones (7,883 against 5,314 on average). Zero-shot it copies T, L and X at 0.088, and
  the new letters at chance, before and after learning copy.
- **The hypothesis is not supported.** A likely reason, untested: each old letter's two strokes
  always came together, and the actor is linear over its features, so it learned whole letters (a
  tone or a glyph to a stroke pair). Nothing in training separates one stroke's features from its
  partner's, and a new pair needs exactly that.

To reproduce the step-size check (about 1 minute):

```
node --input-type=module -e 'import { World, STAGES, GAINS, NEW } from "./game/world/brain.js"; STAGES.push(NEW); GAINS.replay = 0; for (const k of [1, 1.5, 2.5]) { GAINS.lrP = GAINS.lrV = 0.05 * k; const n = []; for (let s = 1; s <= 10; s++) { const w = new World(s); w.setStage(5); while (!w.graduated && w.episode < 20000) w.step(); n.push(w.graduated ? w.episode : "-"); } console.log(k, n.join(" ")); }'
```

Limits:
- One set of three new letters, and nine seeds. Single seeds swing widely: seed 2's graduated brain
  took 18,065 episodes without rehearsal and 3,754 with it.
- The runs from one save share the random stream, which pairs them tightly. Two runs can then pass
  at the same episode though they act differently: on seed 1 the kept and zeroed brains without
  rehearsal both passed at 7,584, and 1,224 of their episodes differ.
- The step-size rule is a game choice (it stopped the critic diverging), not a model of the brain.
  The lesson is about measuring: compare episode counts only at matched step sizes.
- Reading new letters is not tested. Three tones can name only three letters.

That learning sets exist is established (Harlow 1949). This learner's lack of them says nothing
about brains. It shows only that this linear three-factor learner, over a fixed random expansion,
did not transfer from these three letters to new ones.

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
| New letters: learning to learn, and why it does not transfer | [prefrontal-cortex-and-abstraction](../../function/prefrontal-cortex-and-abstraction.md) |

## Not done yet

- Real vision from rendered pixels. The retina is ray-cast, so it runs headless and fast.
- Speech or spoken words instead of pure tones. Multi-letter words.
- Physics-based limbs: joint torques in a deterministic physics engine such as Rapier. The jointed
  CPG body (#38, "Jointed legs" above) is done, but it is kinematic: no masses, no slip, no torques.

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
- Doya, Samejima, Katagiri and Kawato (2002) "Multiple model-based reinforcement learning",
  *Neural Computation* 14:1347. doi:10.1162/089976602753712972
- Heald, Lengyel and Wolpert (2021) "Contextual inference underlies the learning of sensorimotor
  repertoires", *Nature* 600:489. doi:10.1038/s41586-021-04129-3
- Singh, Jaakkola and Jordan (1994) "Learning without state-estimation in partially observable
  Markovian decision processes", *Proceedings of ICML 1994*, 284-292.
- Ijspeert (2008) "Central pattern generators for locomotion control in animals and robots: a
  review", *Neural Networks* 21:642. doi:10.1016/j.neunet.2008.03.014
- Harlow (1949) "The formation of learning sets", *Psychol Rev* 56:51. doi:10.1037/h0062474
- Lake, Ullman, Tenenbaum and Gershman (2017) "Building machines that learn and think like people",
  *Behav Brain Sci* 40:e253. doi:10.1017/S0140525X16001837
