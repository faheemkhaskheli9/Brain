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
node game/world/test_brain.mjs    # headless check, about 20 s
```

Three.js loads from the jsDelivr CDN. Everything else is in `brain.js` (simulation, no DOM) and
`index.html` (3D view, panels, sound). Press **Fast forward** to reach graduation in under a minute.
Then **Watch** shows it practising each skill, with the tones played aloud.

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
  object in a ±0.2 rad central cone, three cochlea bands, leg position and the pen pad.
- **Expansion:** 600 fixed random units, as in cerebellar granule cells or the mushroom body. Each one
  is driven by one local patch of a sense, and sound scales that drive by a random gain (gain
  modulation). An additive mix learned the tone tasks far too slowly.
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
grasp 0.87, listen 0.68, read 0.53, write 0.60. Across seeds 1–7, three pass everything. The others
stall on listen or read within the episode budget, or keep listen just below 0.5. Interleaving one
small network across four tasks keeps some interference, and reading is the weakest skill.

All learning rates, costs and sizes in `GAINS` are game gains: tuning knobs, not measurements. The
claims the page marks as established are that dopamine signals reward prediction error, that
plasticity needs a trace plus a neuromodulator, and that replay protects old memories. That this stack
is enough for a real brain's version of these skills is a hypothesis.

## Not done yet

- Real vision from rendered pixels. The retina is ray-cast, so it runs headless and fast.
- Speech or spoken words instead of pure tones. Multi-letter words.
- Physics-based limbs (joint torques) instead of discrete leg states.
- A larger or growing network to cut interference between skills.
