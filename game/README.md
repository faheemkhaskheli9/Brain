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

Every level has an intro card, the play screen and a debrief that explains what happened
and links its topic file. Each intro is tagged **Established** or **Hypothesis**, as the
topic files are. Levels 6–9 are tagged Hypothesis, with a line saying which part is
settled and which is theory. Levels 9 and 10 come after the boss so existing save files
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
  - the four Izhikevich 2003 presets fire their named patterns, and the LIF never bursts.
- `eval.py` checks models against real brain data instead, one row per reference, and
  exits non-zero if a row fails. It is a per-level table, not one "brain-likeness" score.
  Level 4 has rows for the dopamine signatures (burst moves to the cue, dip on omission,
  dip and late burst when reward is delayed). Level 6 has qualitative rows against the
  human savings curve (Murre & Dros 2015): forgetting is front-loaded, and replay mostly
  stops it. Levels 1 and 2 wait on digitized data (issues #24, #25).

## Not done yet

- Playtest with two people new to neuroscience and tune difficulty (issue #6).
- Out of scope for now: sound, a web version (`sim.py` has no UI imports, so one could
  reuse it), larger spiking networks.
