---
title: Open questions register (ranked research gaps)
category: guides
tags: [research, open-questions, backlog, research-gap, testability, open-data, simulation]
use_cases:
  - which open questions about the brain can I test myself with a computer
  - list every open question in this knowledge base in one place
  - pick a research project that could add something new
status: draft
last_verified: 2026-10-11
sources:
  - https://github.com/faheemkhaskheli9/Brain/issues?q=label%3Aresearch-gap
---

# Open questions register

## Summary
Every `## Open questions` item in this KB, collected in one place and ranked by whether a
computer can answer it. **Tier 1** needs only a simulation in this repo. **Tier 2** needs
open data. **Tier 3** needs a lab, new instruments or philosophy. Questions with an
issue (label `research-gap`) are ready to run with the workflow in [[research-with-ai]].
"Open" here means listed as open by the topic file. Whether each one is still open in the
literature is **unchecked** until its issue's step 0 is done.

## How it works

### Ranking rule
Rank = can a computer answer it, then data or code available today, then effort, then
payoff for brain-like AI. Within a tier, earlier rows come first.

### Tier 1: simulation in this repo (days to weeks)
| # | Question | Raised in | Issue | Status |
|---|---|---|---|---|
| 1 | Does k-WTA sparsity help or hurt Brain World's curriculum, and how much work does it save? | [[efficient-brain-like-learning]] | #82 | answered: no learning cost (k = 20 trended faster, p = 0.066), but under 2x less work per step without event-driven updates |
| 2 | How many episodes does a built-in prior save, compared with a better learning rule? | [[efficient-brain-like-learning]], [[brain-development-and-critical-periods]] | #83 | answered (Brain World, 10 seeds): a fixed orienting reflex cut grasp from 840 to 53 episodes but blocked listen on 7/10 seeds, so it cost far more than it saved; actor sleep replay changed little; a prior the learner cannot override is the problem |
| 3 | Which replay selection rule protects old tasks best, and does SHY downscaling coexist with replay? | [[sleep-and-memory-consolidation]], [[memory-systems]] | #84 | answered (toy network): high-error replay beats random in every cell, most when replay is scarce; recency and least-replayed are no better; downscaling x0.8 slightly hurt and left the ranking unchanged |
| 4 | How much dendritic detail does a useful model need, at equal parameters and operations? | [[dendritic-computation]], [[levels-of-brain-modeling]] | #85 | answered (toy networks): with random branch inputs, dendritic neurons gave no gain over dense one- or two-layer nets at equal parameters under backprop, and were worse under feedback alignment; whether local receptive fields per branch change that is still open |
| 5 | Can place, grid and successor-representation accounts run as one model? | [[spatial-navigation]] | - | candidate |
| 6 | Do grid cells compute path integration or inherit it? (which model fits recorded properties) | [[spatial-navigation]] | - | candidate |
| 7 | Does adding neuron-like noise make a CNN less adversarially fragile, at equal accuracy? | [[sensory-systems-and-vision]] | - | candidate |
| 8 | Which set points and drives does an agent need for useful emotion-like behaviour? | [[emotion-amygdala-and-interoception]] | - | candidate |
| 9 | How can an agent infer its task with no task index? | [[saving-and-reusing-a-trained-brain]] | #57, #60, #65 | in Brain World backlog |
| 22 | Can local learning rules learn reusable abstract structure, or what does the brain add? 170 hypotheses (H001-H170), each with a test, in [research/learning-algorithm-hypotheses.md](../research/learning-algorithm-hypotheses.md), explained simply in [research/hypotheses-explained](../research/hypotheses-explained/README.md) | [[build-a-brain-like-learner]] | #92 | in progress: H001-H003 replicated (PC matches backprop when the output variance is large; FA and DFA train hidden layers on digits) |
| 23 | Can a local rule (STDP, three-factor, e-prop) train a multi-layer spiking network close to surrogate-gradient accuracy, and does spike timing add anything over rates? | [[spiking-neural-networks]], [[brain-inspired-learning-algorithms]] | - | candidate |

### Tier 2: open-data analysis (weeks)
| # | Question | Raised in | Data | Issue | Status |
|---|---|---|---|---|---|
| 10 | Spike timing vs count, per mouse visual area | [[neural-coding-and-computation]] | Allen Neuropixels | #86 | open |
| 11 | Do co-tuned inputs cluster on the same dendritic branch? | [[dendritic-computation]] | MICrONS | #87 | open |
| 12 | Has the accuracy-to-Brain-Score link saturated? | [[sensory-systems-and-vision]], [[evaluating-brain-models]] | Brain-Score leaderboard | #88 | answered (snapshot 2026-10-12): not saturated, the slope above 70% top-1 is steeper (mostly behaviour); parameter count does not predict neural match; accuracy and pretraining-data scale cannot be separated |
| 13 | LLM-brain match: shared computation or word statistics? | [[language-and-llms]] | Narratives (OpenNeuro) | #89 | open |
| 14 | Working-memory capacity: slots or resource? | [[attention-and-working-memory]] | public delayed-estimation sets | #90 | open |
| 15 | Goal-directed vs habitual arbitration: is model-based vs model-free the right split? | [[action-selection-and-motor-control]] | public two-step task data | - | candidate |
| 16 | Is gamma synchrony linked to binding or to routing? | [[brain-rhythms-and-oscillations]], [[neural-coding-and-computation]] | Allen Neuropixels LFP | - | candidate |
| 17 | Do tonic and phasic firing of one nucleus carry different signals? | [[neuromodulators]] | IBL, DANDI | - | candidate |
| 18 | How well do mouse findings transfer to primates? | [[measuring-the-brain-and-open-datasets]] | Allen + Brain-Score macaque | - | candidate |
| 19 | Which metric wins when RSA, predictivity and behaviour disagree? | [[evaluating-brain-models]] | Brain-Score | - | candidate |
| 20 | Benchmarks for learning dynamics (model errors over training vs children) | [[evaluating-brain-models]] | BabyLM, developmental sets | - | candidate |
| 21 | How much of model-brain alignment comes from mechanism vs scale and data? | [[evaluating-brain-models]] | Brain-Score | - | candidate |

### Tier 3: needs a lab, new instruments or theory
| Topic | Questions |
|---|---|
| [[brain-structure-overview]] | What the canonical microcircuit computes; how subsystems coordinate into general intelligence. |
| [[dendritic-computation]] | How often dendritic spikes occur in natural behaviour; which credit-assignment hypothesis the cortex uses (also [[key-papers]]). |
| [[glia-and-energy-budget]] | Astrocyte computation in behaving animals; adult myelin plasticity; the lactate-shuttle debate; how close codes are to the energy optimum. |
| [[cortical-layers-and-columns]] | What the canonical microcircuit computes; whether columns are computational units; what layer 1 feedback does in behaviour. |
| [[neurons-and-synapses]] | Whether synaptic noise and Dale's principle help learning; what most cell types compute; how much one synapse stores. |
| [[learning-and-plasticity]] | Cortical credit assignment; how general eligibility traces are; stable memories on turning-over synapses; how plasticity rules combine. |
| [[predictive-processing]] | Dedicated prediction-error neurons; how precision is set; testable predictions of the free-energy principle. |
| [[brain-vs-deep-learning]] | Which credit-assignment scheme cortex uses; rules vs priors as the source of sample efficiency. |
| [[neuromorphic-hardware]] | Fair energy comparisons with GPUs; on-chip learning accuracy; reliable analog devices at scale. |
| [[action-selection-and-motor-control]] | Cerebellum in cognition and language; what climbing fibres carry; parameters vs dynamics in motor cortex. |
| [[attention-and-working-memory]] | Persistent vs silent storage; routing of top-down attention; all-pairs attention in the hippocampus. |
| [[brain-development-and-critical-periods]] | Adult human neurogenesis; safely reopening critical periods; how genomic rules unfold; language-learning decline. |
| [[brain-rhythms-and-oscillations]] | Which rhythms compute; how theta sequences arise; why bands sit where they do. |
| [[emotion-amygdala-and-interoception]] | Dedicated circuits for emotions; insula and feeling; the fast subcortical route in humans. |
| [[language-and-llms]] | How children learn from little data; how syntax is built; why language is left-lateralised. |
| [[memory-systems]] | How memories are indexed; how the hippocampus decides what to store. |
| [[neural-coding-and-computation]] | Whether oscillations are causal for computation. |
| [[neuromodulators]] | One or several roles for serotonin; how global modulation really is. |
| [[sensory-systems-and-vision]] | What visual feedback computes; learned vs innate ventral-stream organisation. |
| [[sleep-and-memory-consolidation]] | What REM contributes; full copy vs gist in cortex. |
| [[spatial-navigation]] | How many maps avoid interference; whether the map is used for abstract thought. |
| [[theories-of-consciousness]] | Prefrontal role; report vs experience; computing Φ; machine consciousness. |
| [[efficient-brain-like-learning]] | The episode-count gap between Brain World and a person (needs matched human data). |
| [[levels-of-brain-modeling]] | Which biological details are necessary; feasibility of human emulation. |
| [[measuring-the-brain-and-open-datasets]] | BOLD vs spiking per region; cellular-resolution non-invasive methods. |
| [[saving-and-reusing-a-trained-brain]] | How the brain marks important synapses; sleep vs awake consolidation. |
| [[whole-brain-emulation-projects]] | Scan resolution needed; identity of an emulation; ethics. |

For tier 3, an assistant can still summarise the evidence and draft the experiment, but
the answer has to come from new data.

## Relevance to building brain-like AI
Tier 1 rows 1-4 each change a design choice in [[build-a-brain-like-learner]]: how sparse,
how much is innate, how to replay, how detailed a neuron. Start there.

## Keeping this file current
- When a topic gains or loses an open question, add or remove its row here.
- When an issue closes, set its status to `answered` (with a one-line result),
  `answered elsewhere` (step 0 found it), or `negative` and link the topic that holds the result.
- Promote a candidate to an issue only after writing its pre-registration
  ([[research-with-ai]], step 3).

## Open questions
- The tier assignments are judgement calls. Some tier-3 questions may have open data that
  this KB has not found yet.

## Related
- [[research-with-ai]] - the workflow that turns a row into a result.
- [[measuring-the-brain-and-open-datasets]] - where tier-2 data come from.
- [[build-a-brain-like-learner]] - the learner tier-1 results feed into.
- [[start-here]] - map of the whole KB.

## References
- Issues labelled `research-gap`: https://github.com/faheemkhaskheli9/Brain/issues?q=label%3Aresearch-gap
