# Brain Ecosystem: insects, foxes and humans, each with its own brain

A 3D browser world where three species live together and every individual learns from its own
experience. Insects sip nectar, foxes hunt insects and are chased off by humans, humans pick berries.
Nothing they do is scripted: each one gets a dopamine signal (a reward prediction error), and its
synapses change only where an eligibility trace meets that signal. [Brain World](../world/README.md)
shows one learner mastering a curriculum. This shows many learners, with different brains, sharing a
world.

![Brain Ecosystem after about 1900 steps: a human selected, with its learned liking for berry bushes and the place it remembers](../../docs/screenshots/brain-ecosystem.png)

## Run

```
python -m http.server 8000                     # from the repo root
# open http://localhost:8000/game/ecosystem/   (?seed=N for a fixed world)
node game/ecosystem/test_ecosystem.mjs         # headless check, seeds 1-3, about 80 s
node game/ecosystem/test_ecosystem.mjs 4 5 6   # other seeds
```

Three.js loads from the jsDelivr CDN. Everything else is in `ecosystem.js` (simulation, no DOM) and
`index.html` (3D view, panels).

**On the page:** Watch or Fast forward; switch Learning, Memory and Telling on or off for the whole
world; click any creature to see its age, energy, dopamine trace, inborn and learned likes, and the
odds of its next move, with a caption saying in plain words what it is doing and whether that comes
from instinct or learning. The pink marker shows the place a selected fox or human remembers. Follow
keeps the camera on it.

## The species

| | Insect | Fox | Human |
|---|---|---|---|
| Eats | Nectar. Each season (4000 steps) only one flower colour has any | Insects | Berries, which grow in clumps and regrow |
| Threat | Foxes (death) | Humans (lose energy nearby) | None |
| Brain (game sizes, not neuron counts) | 60 hidden units | 200 | 400 |
| Born with | Strong pulls: to flowers, away from foxes and walls | A pull toward insects | Almost nothing: a weak pull toward bushes |
| Memory | None | Where it last saw prey, fading in about 20 steps | A map of where it found berries |
| Social | None | None | Tells nearby humans where food grows (hypothesis) |
| Lifespan | 3000 steps | 6000 | 10000 |

A creature with enough energy and age has a child. The child gets the parent's genome (its inborn
pulls), slightly mutated, and **none** of what the parent learned. If a species falls below a minimum,
newcomers with the default genome arrive, so no species dies out.

These differences follow the knowledge base, in direction only: small, short-lived brains lean on
inherited structure; long-lived, large-brained animals learn more and keep maps
([innate-priors-and-infant-learning](../../function/innate-priors-and-infant-learning.md),
[comparative-and-evolutionary-neuroscience](../../anatomy/comparative-and-evolutionary-neuroscience.md),
[spatial-navigation](../../function/spatial-navigation.md)). Every number in `ecosystem.js` is a game
gain chosen so the world runs in minutes, not a measurement.

## The brain

Every creature has the same kind of brain, in three sizes:

- **Senses.** Six 60° sectors around the head. In each, how close the nearest red flower, blue flower,
  ripe bush, insect, fox, human and wall is, plus one remembered place. Empty flowers and bare bushes
  are not sensed. Plus its own energy.
- **Expansion.** A fixed random sparse expansion of the senses with exactly k winners (like the insect
  mushroom body or cerebellar granule cells). It never learns.
- **Actor-critic.** A critic predicts future reward from the senses and the expansion; dopamine is the
  TD error `δ = r + γV(s') − V(s)`. An actor picks forward, turn left or turn right. Both learn by
  `Δw = lr · δ · trace`, the three-factor rule. No backprop.
- **Instinct plus learned likes.** On top of the actor, each cue has an inborn pull (the genome) and a
  learned valence. On contact with something (nectar, an empty flower, a berry, prey, a bite, being
  chased off), dopamine moves the valence of that one kind, as dopamine neurons change mushroom-body
  output synapses for the odour present at reward
  ([brain-inspired-learning-algorithms](../../learning/brain-inspired-learning-algorithms.md)). Learned
  valence fades slowly, so a food that went sour is tried again later.
- **Memory.** The remembered place is sensed like a thing in its direction. A fox's is the last insect it
  saw. A human's is the best cell of an 8 × 8 map that rises where it eats and decays where it finds
  nothing.

## What the test shows

`test_ecosystem.mjs` checks three things:

1. **Alone, learning pays.** Each species is run alone with energy and age held (so nothing dies), with
   learning on and off. Learning off freezes synapses and valence; memory still works.
2. **In the shared world, grown beats newborn.** After 6000 steps, the three oldest foxes and humans are
   copied into an empty world with the same layout, learning off, and compared with the same brains
   with everything learned wiped (same genome, same fixed wiring), standing in for a newborn. What
   separates them was learned, not inherited or lucky wiring.
3. **Same seed, same world.**

Means over the seeds named:

| Measure | Seeds 1-3 | Seeds 4-6 | Seeds 7-9 |
|---|---|---|---|
| Human alone, food per 1000 steps, learning on / off | 40.3 / 16.0 | 62.3 / 25.2 | 50.8 / 20.4 |
| Fox alone, on / off | 28.0 / 10.5 | 28.7 / 11.1 | 27.1 / 10.8 |
| Insect alone, share of flower visits on the colour with nectar, on / off | 0.73 / 0.51 | 0.75 / 0.48 | 0.76 / 0.52 |
| Grown human vs newborn, from the shared world | 38.4 / 15.9 | 48.5 / 21.9 | 42.2 / 18.1 |
| Grown fox vs newborn | 24.1 / 10.8 | 23.6 / 11.3 | 24.4 / 12.1 |

The test asserts learning-on above 1.4 × learning-off for humans and foxes, an insect rich-colour share
above 0.65 with learning (and below 0.6 without), and grown above 1.2 × newborn.

## Limits and open questions

- **Not "just like" real animals.** They share mechanisms the knowledge base describes (dopamine
  prediction errors, eligibility traces, sparse expansion, inborn priors, a place map). Real insect,
  fox and human brains do far more, and the sizes here say nothing about real neuron counts.
- **Insects learn, but it barely shows in the world.** Foxes keep insects near their minimum
  population, so most insects die young, a few hundred steps in. Their learning shows alone, as colour
  choice, and their survival in the world rests on instinct, which is the point of a short-lived brain.
- **Telling does not help, so far.** Humans that pass on where food grows did not make a newcomer eat
  more in our runs (six seeds, 42.8 vs 43.7 meals in 2000 steps), perhaps because shared knowledge sends
  everyone to the same bushes. An earlier version that also imitated the actions of a human who had just
  eaten made newcomers eat less (33.3). Telling is on by default so it can be watched, not because it
  pays.
- **What failed while building it,** in case it helps the next change: a rest action (cheaper than
  moving) became a trap the learner fell into and never left; crediting every cue in view at a meal made
  everything attractive and the creature spun; letting dips between meals move valence (prey that got
  away) taught foxes to avoid insects; with no wall sense, creatures got stuck against walls.
- **Evolution is slow here.** Genomes mutate at each birth, but runs on a page are too short for
  selection to move them much.
