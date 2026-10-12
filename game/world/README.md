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
node game/world/sweep.mjs --jobs 2     # rehearsal vs sleep replay, seeds 1-10 (see "Sleep")
```

Three.js loads from the jsDelivr CDN. Everything else is in `brain.js` (simulation, no DOM) and
`index.html` (3D view, panels, sound). Press **Fast forward** to reach graduation in about two minutes.
Then **Watch** shows it practising each skill, with the tones played aloud. **Save brain**
downloads its weights and progress as JSON, and **Load brain** picks up from such a file, so a
graduated creature does not need training again. A loaded brain restarts the episode it was saved in.

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
- **Task-context gating:** each stage switches off a fixed random half of the expansion units, so
  each skill mostly trains its own units while the raw senses stay shared (context-dependent gating,
  Masse, Grant and Freedman 2018). The creature is told which task it is on, like an instruction
  cue; inferring the task from what it sees is not modelled. That prefrontal cortex gates hidden
  units this way is a hypothesis, not established.
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

## Perform mode: using a trained brain

`world.perform(key)` locks every episode to one skill and turns learning off: the brain acts and
still computes dopamine, but no weight, success window, log entry or stage changes. `perform(null)`
goes back to training. A save made while performing resumes training on its own stage.
`perform.mjs` scores a save this way (`--seed N` trains that seed to graduation in memory instead).
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
at the kept bar, and asserts the weights and stage are unchanged.

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
- Inferring the task context from the senses instead of being told it.

## References

- McClelland, McNaughton and O'Reilly (1995) "Why there are complementary learning systems in the
  hippocampus and neocortex", *Psychol Rev* 102:419. doi:10.1037/0033-295X.102.3.419
- Munos, Stepleton, Harutyunyan and Bellemare (2016) "Safe and efficient off-policy reinforcement
  learning" (Retrace), NeurIPS. arXiv:1606.02647
- Wilson and McNaughton (1994) "Reactivation of hippocampal ensemble memories during sleep",
  *Science* 265:676. doi:10.1126/science.8036517
- Masse, Grant and Freedman (2018) "Alleviating catastrophic forgetting using context-dependent
  gating and synaptic stabilization", *PNAS* 115:E10467. doi:10.1073/pnas.1803839115
- Singh, Jaakkola and Jordan (1994) "Learning without state-estimation in partially observable
  Markovian decision processes", *Proceedings of ICML 1994*, 284-292.
