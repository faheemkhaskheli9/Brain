---
title: Doing research with an AI assistant (filling gaps in brain knowledge)
category: guides
tags: [research, method, open-questions, preregistration, reproducibility, seeds, statistics, literature-search, ai-assistant, hallucination]
use_cases:
  - how can I use Claude or another AI to do research and fill gaps in what is known about the brain
  - turn an open question from this knowledge base into an experiment I can run on a computer
  - check whether my simulation result is real or just one lucky seed
  - which research gaps can be closed with open data or simulation and which need a lab
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1073/pnas.1708274114
  - https://doi.org/10.1177/0956797611417632
  - https://arxiv.org/abs/2108.13264
  - https://doi.org/10.1038/s41598-023-41032-5
---

# Doing research with an AI assistant

## Summary
An AI assistant such as Claude can do most of the computer side of research. It can
search the literature, download open data, write and run the analysis and simulations,
and draft the write-up. It cannot record from a brain, and its unchecked claims are not
evidence. A gap counts as filled only when other people can check the result:
the question was really open, the test could have failed, it held up across seeds and
datasets, and the write-up links every source. This guide gives the workflow. The open
questions it feeds on are ranked in [[open-questions-register]].

## How it works

### Three kinds of gap
| Kind | Example | Can a computer close it? |
|---|---|---|
| **This repo's gap** | Does k-WTA help Brain World's curriculum? | Yes, fully. The answer is new to this repo, not to science. |
| **Field gap, computable** | Does spike timing add information beyond counts, per visual area? | Yes, with open data (Allen, MICrONS, OpenNeuro) or a simulation. |
| **Field gap, needs a lab** | How much adult neurogenesis do humans have? | No. Claude can only summarise the evidence and design the experiment. |

A simulation answers "which mechanism works better *computationally*". It does not show
what the brain does. Keep that line visible, as AGENTS.md asks for hypotheses.

### The workflow
1. **Pick** a question from [[open-questions-register]] (tier 1 or 2), or from any topic's
   `## Open questions`.
2. **Check it is open.** Have the assistant search the literature for the exact question,
   with results from the last few years, and list what it found *with links*. Open the
   links yourself. A question that turns out answered becomes a KB update, which is still
   useful. Language models fabricate plausible references (Walters & Wilder 2023), so a
   citation you have not opened does not count.
3. **Pre-register.** Before running anything, write down the hypothesis, the prediction,
   the data or simulation, the analysis, the number of seeds, and the result that would
   count against you. Put it in the GitHub issue. Deciding these after seeing the data
   inflates false positives (Simmons, Nelson & Simonsohn 2011; Nosek et al. 2018).
4. **Build and run.** The assistant writes the data loader, model and analysis, runs them
   across seeds or subjects, and adds baselines and controls (a shuffled-label null, an
   untrained model, a simpler model).
5. **Attack the result.** Ask a second reviewer (another model, or a person) to find the
   flaw: leakage between train and test, a missing baseline, a result from one seed, a
   number in the text that the code does not produce. Single-seed results have reversed
   in this repo before ([[efficient-brain-like-learning]]).
6. **Record it.** Write the outcome into the topic file that raised the question, marked as
   a measured result or still open, with the code in the repo. Update the register row and
   close the issue. A negative result is a result.
7. **Share it.** If it is a field gap and it holds up, write a preprint and send it to people
   who work on that question. Peer checking is what turns a result into knowledge.

### What the assistant is good and bad at
| Good at | Bad at |
|---|---|
| Searching and summarising many papers fast | Knowing a paper exists without a link (it may invent one) |
| Writing loaders, models, statistics, plots | Noticing its analysis answers a slightly different question |
| Running many seeds and conditions | Judging whether a result is surprising to the field |
| Connecting findings across subfields | Original lab experiments of any kind |

## Relevance to building brain-like AI
Most tier-1 questions in [[open-questions-register]] are about brain-like learners: sparsity,
priors, replay, dendrites. Answering them with the workflow above both improves the
learner and adds measured results to this KB, rather than more summaries.

## Code: is the effect real across seeds?
Compare two conditions over several seeds with a permutation test. It makes no
distribution assumption and needs only numpy. Agarwal et al. (2021) show how often RL
conclusions drawn from a few runs do not hold.

```python
import numpy as np

def perm_test(a, b, n=10000, seed=0):
    """Mean(a) - mean(b), and a two-sided p-value from shuffling which seed got which condition."""
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a, float), np.asarray(b, float)
    obs = a.mean() - b.mean()
    pool = np.concatenate([a, b])
    diffs = np.empty(n)
    for i in range(n):
        rng.shuffle(pool)
        diffs[i] = pool[:len(a)].mean() - pool[len(a):].mean()
    return obs, (np.sum(np.abs(diffs) >= abs(obs)) + 1) / (n + 1)

rng = np.random.default_rng(1)
base = rng.normal(100, 15, 10)     # e.g. episodes to learn a skill, 10 seeds
noop = rng.normal(100, 15, 10)     # a change that does nothing
better = rng.normal(75, 15, 10)    # a change that really helps

d0, p0 = perm_test(noop, base)
d1, p1 = perm_test(better, base)
print(f"no-op change: mean diff {d0:+.1f} episodes, p = {p0:.3f}")
print(f"real change:  mean diff {d1:+.1f} episodes, p = {p1:.4f}")
print(f"one seed each would have shown a difference of {noop[0] - base[0]:+.1f} for the no-op")
assert p1 < 0.01 and p0 > 0.05
```

It prints a mean difference of -5.6 episodes at p = 0.16 for the no-op change and -32.5
at p = 0.0001 for the real one. With one seed per condition the no-op would have looked
like a 4.8-episode win.

Report the mean difference with its spread, not just the p-value. With several
comparisons, correct for them, or pre-register one primary comparison.

## Open questions
- How well AI-generated research holds up under expert review is itself being studied
  (Lu et al. 2024, "The AI Scientist"). There is no settled answer yet.
- Which parts of the workflow can be safely automated end to end, and which need a person
  every time, is open. Step 2 (is it really open?) and step 5 (attack it) need a person
  in this repo.

## Related
- [[open-questions-register]] - the ranked list of gaps this workflow runs on.
- [[measuring-the-brain-and-open-datasets]] - the open data that tier-2 questions use.
- [[evaluating-brain-models]] - how to compare a model with brain data.
- [[key-papers]] - the papers already read, before searching for new ones.
- [[build-a-brain-like-learner]] - the learner most tier-1 questions improve.

## References
- Nosek, Ebersole, DeHaven & Mellor (2018) "The preregistration revolution", *PNAS* 115:2600. doi:10.1073/pnas.1708274114
- Simmons, Nelson & Simonsohn (2011) "False-positive psychology", *Psychol Sci* 22:1359. doi:10.1177/0956797611417632
- Agarwal, Schwarzer, Castro, Courville & Bellemare (2021) "Deep reinforcement learning at the edge of the statistical precipice", NeurIPS. arXiv:2108.13264
- Walters & Wilder (2023) "Fabrication and errors in the bibliographic citations generated by ChatGPT", *Sci Rep* 13:14045. doi:10.1038/s41598-023-41032-5
- Lu et al. (2024) "The AI Scientist: towards fully automated open-ended scientific discovery", arXiv:2408.06292
