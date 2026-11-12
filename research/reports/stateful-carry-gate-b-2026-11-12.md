# Gate B — stateful dependent-action environment and baselines

Status: **code committed; empirical Gate B not yet confirmed**. This is a research diagnostic, not a learned-option result. Related: [complete Gates A–C plan](https://github.com/faheemkhaskheli9/Brain/pull/176), issue #112.

## Task and observation contract

- **Goal:** acquire an object, transport it through a 5×5 grid, and explicitly place it at a target. Each action changes the next public observation. Pickup may fail. Wet surfaces, turns, or a timed interruption may drop the object; policies must observe and recover.
- **Training:** vertical barrier with one opening and normal carry rule.
- **Development (future tuning only):** horizontal barrier with an opening and wet-tile forced drops.
- **Frozen evaluation:** held-out obstacle geometry and turn-induced drops. The future transition rule, solver, task ID and hidden RNG are never passed to policies.
- Include unreachable goals (target inside wall), random starts/object/goal, variable gaps, visible walls and last observed events. Only the independent `feasible()` evaluator knows whether a goal is reachable; an agent sees the physical layout and may infer impossibility.
- Legal action mask is derived solely from *currently public* position, object presence and obstacles; `drop` is allowed anywhere while carrying. All learning and random-legal arms receive the same mask.
- Scripts and goals are supplied by engineers. No evidence of an independently discovered planning language, symbol system, or conscious representation.

## Baselines and accounting

Arms: flat backprop-free Brain actor-critic, Brain with goal withheld, public-observation tabular Q-learning, stepwise legal random, observation-independent fixed script and hand-coded BFS navigation.

Each trained arm receives **exactly 10,000 primitive environment decisions** by default, including unfinished last episodes; untuned nonlearning baselines use zero training steps and must be labeled separately. Eval consists of 30 frozen tasks × 2 repeats per seed. Individual attempts are nested within the seed, not independent samples. Both Q and Brain are deep-copied for scoring. No training updates or test-set tuning may occur during eval.

**Run after code checks:**

```bash
node game/world/test_stateful_carry.mjs
node game/world/test_stateful_baselines.mjs
node game/world/stateful_baselines.mjs 1 2 3 4 5 6 7 8 9 10 --train-steps 10000 --train-tasks 40 --eval-tasks 30 --repeats 2 --out /tmp/carry-gate-b.json
python research/result_schema.py --check /tmp/carry-gate-b.json
```

Archive the per-seed JSON, split hashes, commit, environment and all failure cases. Publish zero-shot success, infeasible-goal errors, invalid action rate, forced drops, recovery events, source-task retention, decisions and wall time. The hand-coded heuristic is an engineered control, not an independent learning achievement.

## Adversarial threats and stop rules

1. **Trivial macro:** compare fixed script and goal-ablated learner. If these solve held-out destinations reliably, increase task diversity before claiming composition.
2. **Transition leakage:** assert rule/split/task ID/feasibility are absent from public observations. Split hashes and generation seeds must be published; rule families must be disjoint.
3. **Unfair baseline:** tabular Q sees the same public state and action mask as Brain. Disclose different architectures and compute costs; do not handicap Q through an artificially truncated state or tuning budget.
4. **Hidden shortcuts:** scripted BFS can use the full public grid but cannot see future pickup failures. Report it separately from any privileged oracle upper bound.
5. **Impossible goals and interruptions:** failures must remain in denominators. A success on a blocked destination indicates a validator bug. Count reacquisition after forced drops.
6. **Evaluation RNG/state leakage:** frozen copies and task-scoped episode seeds; verify reversal of scoring order cannot change source parameters or per-task outcomes.
7. **Sample size and selection:** paired seeds 1–10 are experimental units. A high average with wide seed-cluster confidence interval is inconclusive.

**Remaining Gate C:** one learned intra-option policy, initiation and termination, interruption recovery, option-disabled/shuffled/fixed-macro ablations, development-selected strongest comparator and a frozen paired 95% interval. Do not claim a generalization or AGI advance until Gate A and B pass, then run the confirmatory Gate C protocol without post-hoc changing seeds or thresholds.
