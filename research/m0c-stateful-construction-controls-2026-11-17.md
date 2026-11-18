# M0c: matched public-observation construction baseline handoff (2026-11-17)

**Evidence status:** code and tests implemented in the branch; executable CI and scientific performance remain separate. This document reports **protocol and source inspection**, not a 10-seed positive finding. Parent source commit reviewed: [69e4fb1a](https://github.com/faheemkhaskheli9/Brain/commit/69e4fb1a586530e67a87a1e7c29e013fe5706644) (2026-11-17). Reuse existing issues [#112](https://github.com/faheemkhaskheli9/Brain/issues/112), [#153](https://github.com/faheemkhaskheli9/Brain/issues/153) and [#154](https://github.com/faheemkhaskheli9/Brain/issues/154).

## Gap and prior negative evidence

- Previous [10-seed exact-budget option experiment](stateful-options-exact-negative-2026-11-12.md) reported **0** held-out goal completions across all six non-oracle arms; the privileged BFS ceiling was **1.0**. It did not show task learnability from public observations.
- Existing tabular-Q and heuristic baselines in [stateful_baselines.mjs](../game/world/stateful_baselines.mjs) target `stateful_carry.mjs`, *not* [stateful_construct.mjs](../game/world/stateful_construct.mjs). Transferring the results across environments would be invalid.
- `stateful_construct.mjs` uses a fixed start and only four goal pairs × four obstacle patterns per named split. New seeds can repeat physical structures. Comparing these splits measures limited, engineered pair-family generalization, not new task mechanics.

## Implementation and falsifiable questions

[New runner](../game/world/stateful_construct_controls.mjs) compares six arms in exactly **one** environment, with the same six selectable primitives, identical `observe`/`transition` and reward functions, and no online oracle calls.

| Arm | Access | Learns? | Intended control |
| --- | --- | --- | --- |
| `flat` | unchanged public observation | local, backprop-free Brain actor/critic | existing learner |
| `flat-goal-masked` | goal channels removed | same learner | goal-use ablation |
| `tabular-absolute` | publicly observed absolute positions, local obstacle flags and last failure | tabular Q(0.2, 0.95, ε=0.2), randomized ties | public-state learnability |
| `tabular-relative` | the same public observation, with **authored target-relative coordinates** | same Q rule | inductive-bias comparator, not acquired abstraction |
| `uniform-random` | fixed six-action set | none | random primitive baseline; can attempt invalid moves |
| `public-maze-heuristic` | observed agent, item, goal, carrying flag and **adjacent** blocked flags | no parameter learning; stores only encountered walls | engineered, nonprivileged online pathfinding ceiling |

The heuristic is allowed to know the grid geometry and plan through *unobserved* cells optimistically; it is **not** allowed to inspect `task.walls`, transitions, feasibility oracle or hidden state to select actions. Discovered blocked neighbors update its local wall memory. Tabular-Q reuses the existing seeded `TabularQ` implementation, parameterized for six instead of seven actions; all learned arms have an exact primitive-decision training cap and charge both invalid attempts and failed placements as physical transitions.

### Deterministic audit and boundaries

- Record **actual** `trainDecisions`, `trainEnvSteps`, truncated episodes, evaluated decisions, false actions, table states, stored parameter bytes estimates and zero online oracle calls. An estimate of Q string/map payload is **not** a comparable measured RSS or compute cost.
- Each task structural fingerprint includes start, item, goal, sorted walls, horizon and dynamics version; excludes seed, task ID and split. Reject identical full physical structures across named train/dev/heldout splits; report unique structures and duplicates **within** each split and SHA-256 of ordered manifests.
- Source and evaluation both operate on frozen copies (the existing Brain clone and a copied Q table). Q updates on explicit training truncation bootstrap the observable next state instead of manufacturing a terminal penalty.
- On the existing 5×5 generator, the protocol **cannot** establish transfer to independently sampled layouts, unseen starts or new dynamics. Confidence intervals and independent family stress tests remain future work under M0c/M0d.

**Primary falsifier:** if neither public-Q variant learns a deliberately simple fixed-geometry pickup/delivery diagnostic better than random after a matched decision budget, the next task is to inspect state observability, reward and action horizon—not increase biological architecture complexity. A successful heuristic proves only that an engineered public-observation method can solve such cases, **not** that a learnable policy can.

## Reproduction

From the repository root, first run deterministic test and schema-checked smoke:

```bash
node game/world/test_stateful_construct_controls.mjs
node game/world/stateful_construct_controls.mjs 1 --train-steps 17 --train-tasks 4 --dev-tasks 3 --eval-tasks 3 --repeats 1 --out /tmp/m0c-smoke.json
python research/result_schema.py --check /tmp/m0c-smoke.json
```

Exploratory (do **not** interpret as sealed transfer until new generator families are implemented):

```bash
node game/world/stateful_construct_controls.mjs 1 2 3 4 5 6 7 8 9 10 --train-steps 10000 --train-tasks 32 --dev-tasks 16 --eval-tasks 16 --repeats 2 --out /tmp/m0c-exploratory.json
python research/result_schema.py --check /tmp/m0c-exploratory.json
```

Record the exact run commit, environment/runtime, code/manifest hashes, all statuses and raw result as `brain-result/1`. **No new scientific score is asserted here.** CI's small deterministic run guards implementation, not model performance.

## Adversarial limitations and next experiment

1. **Representation fairness:** relative-tabular hardcodes a spatial prior. Strong performance would demonstrate learnability with that prior, not automatic abstraction acquired by Brain. Flat uses the current original public observation.
2. **Data family leakage:** at most 16 different pair-layout configurations per legacy split. Distinct IDs can alias; exact structural overlap is rejected, but all obstacle styles and starts are still authored.
3. **Budget fairness is not compute fairness:** neural and Q models have different parameter allocation and cost; compare runtime and memory separately before claiming efficiency.
4. **Generator feasibility:** this pilot does not perform private BFS checks. Record feasible/impossible tasks in a later separate, fully charged *offline* audit before a sealed new-family test.
5. **Learning proof versus architecture:** source-task training success, goal-completion learning curves and a within-distribution simple calibration must be measured independently. Do not promote M1 based solely on a positive heuristic result or on a higher shaped reward.
6. **Next M0c/d implementation:** build two genuinely new obstacle/start/dynamics generators, add audit mutations for hidden oracle access and action counts, and investigate nonterminal option-boundary bootstrap as a separate single-variable intervention.

**Research basis:** [Sutton, Precup & Singh (1999)](https://doi.org/10.1016/S0004-3702(99)00052-1) formalizes temporal abstraction and semi-MDP options, but does not validate this toy algorithm. The precise executed negative results are repository evidence, not claims about neuroscience. Preserve the original experiment rather than rewriting it.
