# M0c fixed-geometry feedback and exploration calibration (2026-11-17)

**Status:** implementation protocol; numeric evidence to be appended only after a verified scientific run. Existing ten-seed M0c evidence on main reports 0% physical delivery for the flat Brain learner in legacy and two structural stress directions. This study asks whether it can learn *one repeated, simple action sequence*.

**Parent reviewed:** [3ebc3c0](https://github.com/faheemkhaskheli9/Brain/commit/3ebc3c0abbd81ea132920e66ce5610a188d773b6), 2026-11-17. Inspected source: game/world/stateful_construct.mjs, stateful_options.mjs, stateful_construct_controls.mjs, brain.js and prior [M0c evidence](m0c-ten-seed-evidence-2026-11-17.md). Backlog [#112](https://github.com/faheemkhaskheli9/Brain/issues/112), [#120](https://github.com/faheemkhaskheli9/Brain/issues/120), [#136](https://github.com/faheemkhaskheli9/Brain/issues/136), [#153](https://github.com/faheemkhaskheli9/Brain/issues/153).

## Falsifiable question

If a public-observation learner cannot solve a repeatedly presented, fully visible three-primitive pickup–east–drop task after fixed, matched training decisions, it is premature to attribute failure on novel obstacle families to missing higher brain regions or learned world-model planning. Positive results here demonstrate *same-structure learning* only—not transfer, autonomous abstraction, or biological fidelity.

Three possible bottlenecks are kept separate: (H0) sparse delayed goal feedback, (H1) engineered public-state representation, and (H2) action exploration. This suite can prioritize subsequent single-variable experiments; it does not prove a single cause.

## Task and controls

Single **training task**: 5×5 grid; agent and item at (2,0); target at (3,0); no walls; horizon 12; shortest solution pickup–east–drop. Two clearly nonsealed *diagnostic variants* move the target one cell west or require approaching the item first. No policy receives task ID or oracle path.

| Arm | Information and feedback | Confound disclosed |
|---|---|---|
| flat-brain | Existing backprop-free Brain three-factor actor/critic and native simulator feedback | Neural policy architecture differs from Q |
| q-absolute | Public absolute-state tabular Q; epsilon 0.2 | Authored discrete key |
| q-relative | Public goal-relative tabular Q; epsilon 0.2 | Supplied spatial representation |
| q-relative-explore50 | Same relative Q and native reward; epsilon 0.5 | Exploration-only tabular comparison |
| q-relative-potential | Same relative Q; native reward plus potential-based shaped training signal | **Engineered** Manhattan target/carry prior, never score shaping |
| q-relative-no-reward | Same relative Q with zero learning feedback | Negative reward/credit control |
| uniform-random | Uniform among all six primitives; no training | Unlearned accidental-success rate |

All task transitions and scoring use the original stateful_construct.observe/transition and six primitives. Invalid moves and drops cost one physical environment step and are recorded. All trainable arms consume exactly the same total **0 / 250 / 1000 / 4000** cumulative primitive decisions across **10 fixed seeds** (1–10); random trains zero. Frozen evaluation uses 12 repeated trials on the same calibration structure and 12 trials on each nearby variant at every checkpoint, with cloned parameters. Score **actual delivered objects**; report training pickups, invalid actions, blocked moves, negative outcomes, and exactly counted env steps.

**Feedback caveat:** shaped reward uses public Manhattan/carry potential with gamma=0.95 and a zero terminal potential. Its goal geometry is supplied by code; this is a deliberately engineered upper-support comparison, not evidence of an autonomous learned world model. It is a separate *feedback* intervention rather than a change to simulator rewards. For theoretical background only: [Ng, Harada & Russell (1999)](https://dl.acm.org/doi/10.5555/645528.657613). A potential can affect finite-horizon, truncated training and exploration behavior, so policy invariance cannot be assumed here.

## Reproduction

```bash
node game/world/test_stateful_calibration.mjs
python research/test_check_m0c_calibration.py
node game/world/stateful_calibration.mjs 1 2 3 4 5 6 7 8 9 10 --checkpoints 0,250,1000,4000 --repeats 12 --out /tmp/m0c-fixed-calibration.json
python research/result_schema.py --check /tmp/m0c-fixed-calibration.json
python research/check_m0c_calibration.py /tmp/m0c-fixed-calibration.json
```

[GitHub Actions evidence workflow](../.github/workflows/m0c-fixed-calibration.yml) uploads the entire brain-result/1 file and prints its raw contents for source/seed-preserving Git archival. The cheap standard CI smoke test checks exact budgets, negative runs, frozen evaluation and task validity, **not** learning superiority.

## Decision criteria and adversarial checks

- **Primary outcome:** before vs 4,000-step *physical same-task delivery success*, by paired seed. Secondary: variant success and how often the policy successfully picks up, invalid rates and relative-Q exploration/feedback ablations.
- If flat Brain remains at or near zero while a public Q baseline learns, investigate its action entropy, synaptic feature accessibility, temporal-difference targets and traces—do **not** grow the architecture without causal evidence.
- A positive training-structure result is not heldout generalization. Neither the best relative tabular key nor engineered potential is autonomously discovered. Different actor/Q capacities prevent a learning-rule superiority claim.
- The visible state contains position, goal, carrying flag and local collision sensors; persistent episodic history is not necessary to *represent* this Markov toy. Avoid attributing poor performance to missing history without evidence.
- The whole scientific program remains **HOLD M1–M8** regardless of same-task performance; require independent structural-transfer and retention evidence with sealed controls before any promotion.

**Provenance:** prior 0% result is repository-reproduced evidence. The bottleneck hypotheses and this protocol are engineering hypotheses, not established neuroscientific findings. No claims.tsv change is justified by this implementation.
