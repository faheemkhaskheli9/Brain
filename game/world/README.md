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
original.

All learning rates, costs and sizes in `GAINS` are game gains: tuning knobs, not measurements. The
claims the page marks as established are that dopamine signals reward prediction error, that
plasticity needs a trace plus a neuromodulator, and that replay protects old memories. That this stack
is enough for a real brain's version of these skills is a hypothesis.

## Not done yet

- Real vision from rendered pixels. The retina is ray-cast, so it runs headless and fast.
- Speech or spoken words instead of pure tones. Multi-letter words.
- Physics-based limbs (joint torques) instead of discrete leg states.
- Inferring the task context from the senses instead of being told it.

## References

- Masse, Grant and Freedman (2018) "Alleviating catastrophic forgetting using context-dependent
  gating and synaptic stabilization", *PNAS* 115:E10467. doi:10.1073/pnas.1803839115
