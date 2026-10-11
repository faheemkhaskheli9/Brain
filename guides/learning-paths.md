---
title: Learning paths for different readers
category: guides
tags: [reading-order, learning-path, curriculum, ml-engineers, students, games]
use_cases:
  - I am an ML engineer, what should I read first about the brain
  - I study neuroscience and want the computational side
  - I came from Brain Lab or Brain World and want the science behind it
  - give me an ordered reading list for this knowledge base
status: draft
last_verified: 2026-10-11
sources:
  - https://neuronaldynamics.epfl.ch/
---

# Learning paths for different readers

## Summary
Three ordered reading lists through this knowledge base, one per kind of reader.
Each step names what to take away. [[start-here]] has the same files grouped by
subject, and a question table for jumping straight to one file.

## How it works

### ML engineers: from deep learning to the brain
You know backprop, transformers and RL. Start from what you know and work out.
1. [[brain-vs-deep-learning]] - where networks and brains differ, and the backprop problem.
2. [[neurons-and-synapses]] - what a real unit is, beyond a weighted sum.
3. [[learning-and-plasticity]] - Hebb, STDP and dopamine as TD error.
4. [[brain-inspired-learning-algorithms]] - the runnable versions of those rules.
5. [[memory-systems]] - complementary learning systems and catastrophic forgetting.
6. [[sensory-systems-and-vision]] - CNNs and the ventral stream.
7. [[language-and-llms]] - LLM activations compared with brain recordings.
8. [[predictive-processing]] - prediction as the brain's training signal (hypothesis).
9. [[evaluating-brain-models]] - how to tell whether a model is actually brain-like.
10. [[build-a-brain-like-learner]] - the staged project that ties it together.

### Neuroscience students: from biology to models
You know the anatomy. Learn to write it as code and test it against data.
1. [[levels-of-brain-modeling]] - pick the level of detail for a question.
2. [[neural-coding-and-computation]] - rate, timing and population codes.
3. [[spiking-neural-networks]] - LIF neurons, STDP and simulators, in Python.
4. [[dendritic-computation]] - single neurons as small networks.
5. [[brain-rhythms-and-oscillations]] - where oscillations come from in a model.
6. [[neuromodulators]] - modulators as learning-rate and exploration dials.
7. [[spatial-navigation]] - place and grid cells, the best-modelled cognitive map.
8. [[measuring-the-brain-and-open-datasets]] - recording methods and data to test models on.
9. [[evaluating-brain-models]] - RSA, encoding models and Brain-Score.
10. [[brain-inspired-learning-algorithms]] - what the models contribute back to AI.

### Players: from the games to the science
You have played Brain Lab (`python game/play.py`) or Brain World. Each step is
the topic behind a level, in level order, then the parts the games skip.
1. [[spiking-neural-networks]] - Spark (level 1): the leaky integrate-and-fire neuron.
2. [[learning-and-plasticity]] - Wire together and Be the dopamine (levels 2, 4).
3. [[brain-structure-overview]] - Lesion lab (level 3): what each region does.
4. [[memory-systems]] - Remember me and Sleep on it (levels 5, 6).
5. [[sleep-and-memory-consolidation]] - what the sleep replay in level 6 stands for.
6. [[predictive-processing]] - Guess what's next (level 7).
7. [[build-a-brain-like-learner]] - Tiny brain (level 8) and Brain World's dopamine-only creature.
8. [[brain-inspired-learning-algorithms]] - Find the pattern (level 9).
9. [[levels-of-brain-modeling]] - Neuron zoo (level 10).
10. [[spatial-navigation]] - Find your way home (level 11).
11. [[neurons-and-synapses]], then [[start-here]] path A for the rest of the brain.

### Everyone: the open frontier
After any path, these are the hypothesis-heavy topics, read with the
established/hypothesis line in mind: [[predictive-processing]],
[[theories-of-consciousness]], [[whole-brain-emulation-projects]].

## Relevance to building brain-like AI
All three paths end at [[build-a-brain-like-learner]] or
[[evaluating-brain-models]]: building something, and testing it against the brain.

## Related
- [[start-here]] - the same files by subject, and a question-to-file table.
- [[glossary]] - terms used along the way.
- [[key-papers]] - the evidence behind each step.

## References
- Gerstner, Kistler, Naud & Paninski (2014) *Neuronal Dynamics*, Cambridge University Press; free online at https://neuronaldynamics.epfl.ch/ - a companion text for the student path.
