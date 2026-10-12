# The 170 learning hypotheses, explained simply

This folder explains every hypothesis (H001-H170) in
[learning-algorithm-hypotheses.md](../learning-algorithm-hypotheses.md) in plain
language. For each one you get:

1. **In simple words**: the idea with no jargon, usually with an everyday comparison.
2. **How it would work in the brain**: a step-by-step workflow, from input arriving to
   a synapse changing, *if the hypothesis is true*.
3. **How to test it here**: a step-by-step experiment workflow you can run on a
   computer (or, for T2/T3 rows, what data or lab work it needs).
4. **Counts against it if**: the result that would weaken it, copied from the table.
5. **Why it matters for a brain-like learner**: what changes in the design if it holds.

## Read this first

- **Every hypothesis here is a hypothesis.** The "how it would work in the brain"
  workflow describes what the idea *claims*, not what has been shown. Where part of a
  workflow is textbook neuroscience (for example "dopamine neurons fire to unexpected
  reward"), it says so; everything else is the claim being tested.
- **Sources are the same as in the main table and were written from memory.** Check
  authors, year and venue before citing anything (step 0 of
  [research-with-ai](../../guides/research-with-ai.md)). Rows marked **new** have no
  published source.
- **Status** is copied from the main table. The main table is the source of truth:
  when a status changes there, update it here too.
- Competing rows are pointed out ("competes with H090"). A result for one weakens the
  other.

## The standard test loop (used by every "How to test it here")

Each test workflow below lists only the steps specific to that hypothesis. All of them
sit inside this loop:

1. **Step 0, literature check.** Search for the hypothesis and the test. If it is
   already answered, set the status to `answered elsewhere` and log it.
2. **Pre-register** in a GitHub issue labelled `research-gap`: the hypothesis, the
   metric, the baseline, and the result that would count against it.
3. **Build the smallest numpy version** that can show the effect.
4. **Run several seeds** (at least 5) for both the model and the baseline, and report
   mean and spread, not the best run.
5. **Record** the result in the main table's Status column and its Log, and in the
   topic file it belongs to. Close the issue.

Tiers: **T1** = a simulation in this repo, **T2** = open data, **T3** = needs a lab, new
instruments or theory. Several tests reuse three shared setups:

| Setup | What it is |
|---|---|
| **Tiny MLP** | A 2-layer numpy network on XOR or a small synthetic classification task, with a backprop baseline. |
| **Brain World** | The 3D creature in [game/world](../../game/world/) that learns five skills in a row. |
| **H101 transfer setup** | Train on some Brain World layouts, test on new layouts that share structure but not surface features. Transfer = performance on the new layouts. |

## Files

| File | Section | Rows |
|---|---|---|
| [a-credit-assignment.md](a-credit-assignment.md) | A. Credit assignment: local approximations of backprop | H001-H020 |
| [b-reward-and-neuromodulators.md](b-reward-and-neuromodulators.md) | B. Reward, neuromodulators and three-factor rules | H021-H038 |
| [c-self-supervised-world-model.md](c-self-supervised-world-model.md) | C. Self-supervised objectives: cortex learns a world model | H039-H054 |
| [d-structure-maps-abstraction.md](d-structure-maps-abstraction.md) | D. Structure, maps and abstraction | H055-H080 |
| [e-innate-priors-and-development.md](e-innate-priors-and-development.md) | E. Innate priors and development | H081-H092 |
| [f-memory-and-consolidation.md](f-memory-and-consolidation.md) | F. Memory, consolidation and forgetting | H093-H108 |
| [g-language-and-reasoning.md](g-language-and-reasoning.md) | G. Language and reasoning | H109-H130 |
| [h-scale-neurons-dendrites.md](h-scale-neurons-dendrites.md) | H. Scale, neurons and dendrites | H131-H137 |
| [i-dynamics-and-computing-primitives.md](i-dynamics-and-computing-primitives.md) | I. Dynamics and alternative computing primitives | H138-H151 |
| [j-control-attention-meta-learning.md](j-control-attention-meta-learning.md) | J. Control, attention and meta-learning | H152-H161 |
| [k-combinations-and-new-ideas.md](k-combinations-and-new-ideas.md) | K. Combinations and new ideas from this thread | H162-H170 |

## Background for the simple explanations

If a word is unfamiliar, these topic files explain the established science behind it:
[learning-and-plasticity](../../function/learning-and-plasticity.md) (Hebbian, STDP,
dopamine, three-factor rules), [brain-vs-deep-learning](../../learning/brain-vs-deep-learning.md)
(why backprop is hard for a brain), [memory-systems](../../function/memory-systems.md)
(hippocampus and cortex), [neuromodulators](../../function/neuromodulators.md), and the
[glossary](../../guides/glossary.md).
