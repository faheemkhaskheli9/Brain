# Brain Lab: a playable brain simulation

A desktop game in Python where you learn how the brain works by operating working
models of it. Each level is one idea from this knowledge base. You win a level by
making the simulated brain do something, not by answering a quiz.

## Run

```
pip install numpy
python game/play.py        # the game (tkinter ships with Python)
python game/test_sim.py    # headless checks for every model
python game/test_levels.py # a scripted play wins every level (needs a display; xvfb-run on CI)
```

Progress (stars per level) is saved in `~/.brain_lab/save.json`. Delete it to start over.
Each level opens once the one before it is won.

**In a browser (levels 1 to 7 so far).** `game/web/index.html` runs Spark (`#spark`),
Wire together (`#wire`), Lesion lab (`#lesion`), Be the dopamine (`#dopamine`), Remember me
(`#remember`), Sleep on it (`#sleep`) and Guess what's next (`#predict`) with the same `sim.py` under [Pyodide](https://pyodide.org), so nothing needs installing.
The level 5 and 7 debriefs have no sweep chart in the browser yet. The page
fetches `sim.py`, so serve the repo over HTTP: `python -m http.server` from the repo root,
then open `http://localhost:8000/game/web/`. The first load downloads Pyodide and numpy
from the jsDelivr CDN, so it takes a few seconds.

## Levels

| # | Level | You | Win when | Model in `sim.py` | Topic file |
|---|---|---|---|---|---|
| 1 | Spark | Click (or Space) to send 10 ms pulses of current into a neuron and watch its voltage | Exactly 5 spikes in 500 ms of model time | Leaky integrate-and-fire with a refractory period | [spiking-neural-networks](../simulation/spiking-neural-networks.md) |
| 2 | Wire together | Fire input A, input B (keys A, B) and the output neuron (Space) | Synapse A above 0.8 and B below 0.2 | STDP pair rule, ~20 ms window | [learning-and-plasticity](../function/learning-and-plasticity.md) |
| 3 | Lesion lab | Lesion one hidden region at a time, see which of 8 jobs breaks, name the region | All 8 named with at most 3 wrong names | Region and lesion tables from the topic file (H.M., Parkinson's, S.M., ...) | [brain-structure-overview](../anatomy/brain-structure-overview.md) |
| 4 | Be the dopamine | Run bell and juice trials for a TD learner and watch its dopamine | The burst moves to the bell, then a dip appears when juice is withheld | TD(0), `δ = r + γV(s') − V(s)` | [learning-and-plasticity](../function/learning-and-plasticity.md) |
| 5 | Remember me | Draw or generate 8 × 8 patterns, store them, recall from fragments | 3+ memories pass a recall test, then recall breaks as you add more | Hopfield network (64 neurons, capacity about 9) | [memory-systems](../function/memory-systems.md) |
| 6 | Sleep on it | Learn task B day by day, with or without sleep replay of task A | B at 90% while A stays at 80% or above | Linear associator, local delta rule, interleaved replay | [memory-systems](../function/memory-systems.md) |
| 7 | Guess what's next | Set how much a belief trusts noisy senses while a dot moves behind a screen | Tracking error under 0.05 for 12 s | Prediction plus gain × prediction error | [predictive-processing](../function/predictive-processing.md) |
| 8 | Tiny brain | Switch dopamine and the eligibility trace on or off, then run a forager | 10 meals within 400 steps | Actor-critic three-factor rule (trace × dopamine) | [build-a-brain-like-learner](../guides/build-a-brain-like-learner.md) |
| 9 | Find the pattern (bonus) | Feed 2-D inputs to one neuron, set its learning rate, switch Oja's forgetting term on or off | Weights line up with the inputs' first principal component at length ≈ 1, held for 100 inputs | Hebb vs Oja's rule, `Δw = ηy(x − yw)` | [brain-inspired-learning-algorithms](../learning/brain-inspired-learning-algorithms.md) |
| 10 | Neuron zoo (bonus) | Set current and the Izhikevich parameters a, c, d; an LIF neuron gets the same current | The Izhikevich neuron has fired regular, intrinsically bursting, chattering and fast spiking | Izhikevich 2003 vs LIF, patterns named from interspike intervals | [levels-of-brain-modeling](../simulation/levels-of-brain-modeling.md) |
| 11 | Find your way home (bonus) | Search the arena for food with the arrow keys, then press H to run straight home on the creature's own position estimate (at least 0.4 arena widths out); landmark place fields can reset your position estimate | Land within reach of the nest | Noisy path integration with landmark resets; one grid cell's hexagonal firing map | [spatial-navigation](../function/spatial-navigation.md) |

Every level has an intro card, the play screen and a debrief that explains what happened
and links its topic file. Levels that run on their own clock (1, 2, 7, 8, 9) have Pause (P)
and Step (N). A one-line hint appears after a failed attempt or 45 s without a win. The
debriefs for levels 5, 7 and 11 plot the model's what-if sweep: recall against memories stored,
tracking error against gain, and how far path integration misses home against steps walked.
Each intro is tagged **Established** or **Hypothesis**, as the
topic files are. Levels 6–9 and 11 are tagged Hypothesis, with a line saying which part is
settled and which is theory. Levels 9–11 come after the boss so existing save files
keep their level numbers.

Stars: 1 for a win; 2 and 3 for an efficient win or a bonus. The bonus is a debrief point
worth seeing, for example juice with no bell in level 4.

## How it is built

```
game/
  sim.py         numpy models, no UI imports
  levels.py      one class per level: text, canvas drawing, win check
  play.py        tkinter shell: menu, intro, level, debrief, save file
  test_sim.py    plain asserts on sim.py
  test_levels.py drives each level headlessly: a good play wins, a bad one does not
  eval.py        brain-match scorecard: models vs published recordings
```

- **Biological constants** (LIF time constant and thresholds, the ~20 ms STDP window,
  Hopfield storage) are copied from the topic files and keep their sources there.
- **Game gains** (learning rates, task sizes, step budgets) are tuning knobs. They make a
  level winnable in a minute or two and are marked "game gain" in `sim.py`. They are not
  measurements.
- `test_sim.py` checks that each level's lesson actually holds in its model:
  - the STDP sign flips with spike order;
  - dopamine moves from the juice to the bell;
  - recall breaks past capacity;
  - without replay task A is forgotten, and with replay it is kept;
  - the tracker has a gain sweet spot;
  - the forager needs both dopamine and the trace to win within 400 steps;
  - Oja's rule finds the first principal component at length 1, and pure Hebb blows up;
  - the four Izhikevich 2003 presets fire their named patterns, and the LIF never bursts;
  - the grid cell's map repeats along three directions 60° apart, path integration drifts
    more the farther it walks, and a landmark resets it.
- `eval.py` checks models against real brain data instead, one row per reference, and
  exits non-zero if a row fails. A `gap` row is a known mismatch, printed but not scored.
  It is a per-level table, not one "brain-likeness" score.
  Level 1 is scored against a recorded mouse L2/3 neuron from the Allen Cell Types
  Database: an LIF built from the cell's measured R, tau and threshold fits its f-I curve
  better than Allen's own GLIF1 fit, but every linear LIF overestimates its rheobase, and
  the game's 10 MOhm neuron needs about 20x the current (gap).
  Level 2 has rows against Bi & Poo 1998: sign of the timing window and its width pass,
  but the rule is symmetric while their potentiation is about 2.7x their depression (gap).
  Level 4 has rows for the dopamine signatures (burst moves to the cue, dip on omission,
  dip and late burst when reward is delayed). Level 5 has no human dataset that fits, so
  its row is an internal check against theory: capacity near 0.138 N (Amit et al. 1985).
  Level 6 has qualitative rows against the
  human savings curve (Murre & Dros 2015): forgetting is front-loaded, and replay mostly
  stops it. Level 7 is scored against human pursuit of a hidden target: the belief keeps
  moving while the dot is hidden, but it does not slow down the way eye velocity does (gap).
  Level 8 is scored against striatal dopamine ramps near a goal (Howe et al. 2013): value
  ramps, but plain TD error is flat once learned (gap).

## Brain World

`game/world/` is a separate browser simulation. Brain Lab has you operate one mechanism
at a time; Brain World puts them together in one 3D creature that learns to walk, grasp,
listen, read and write from reward alone. Save and Load keep a trained brain as a JSON file.

```
python -m http.server 8000        # from the repo root, then open http://localhost:8000/game/world/
node game/world/test_brain.mjs    # headless check, about 90 s
```

See [world/README.md](world/README.md) for the curriculum, the brain and its limits.

## Not done yet

- Playtest with two people new to neuroscience and tune difficulty (issue #6).
- Out of scope for now: sound, a web version (`sim.py` has no UI imports, so one could
  reuse it), larger spiking networks.
