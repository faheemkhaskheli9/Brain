# M0c independent goal-pair fixtures

**Registered engineering audit, 2026-11-25.** Supports #112, #153 and #154. The fixture
audit evaluates the environment and public observation interface. Learner confirmation
requires a separate registered experiment.

## Provenance and design

- Inspected [main at af40c8d](https://github.com/faheemkhaskheli9/Brain/commit/af40c8d2371f1db157e09f916d9eccd2913a5833),
  specifically [construction transitions](../game/world/stateful_construct.mjs),
  the [structural generator](../game/world/stateful_structural.mjs) and the
  [public maze baseline](../game/world/stateful_construct_controls.mjs).
- [Round 28](m0c-frozen-step-credit-results-2026-11-24.md) motivates a test with fewer
  memorization shortcuts. The proposed [branching plan](https://github.com/faheemkhaskheli9/Brain/pull/215)
  and the unmerged [matched-step results](https://github.com/faheemkhaskheli9/Brain/pull/214)
  were reviewed at f11de9c and e271ab8, respectively. This implements the independent-layout
  fixture work on main's existing interfaces.
- A group holds start, item, walls, action set and horizon fixed, and varies between two equally
  distant goals. The horizon equals the shortest start–pickup–carry–drop route. All shortest
  first directions after pickup are computed for each goal. The generator rejects pairs
  whose sets overlap. Local collision sensors provide partial wall information.
- Any drop while carrying ends the episode. For a blind policy, paired goals receive the
  same observation history and random stream through its first carrying drop. One route can
  complete at most one of two goals. The evaluator checks the action trace matches for both
  blind episodes and rejects any blind pair above 50%. A fixed feasible route demonstrates
  attainability with known geometry. An uninformed policy on new geometry may score lower.
- Open layouts are partitioned by physical-layout hash across training and development seeds.
  Scattered holdouts use two or three walls. Barrier holdouts use at least four and retain
  the original generator's goal across the divider. The manifest records separate split hashes
  and counts offline oracle calls. Policies receive observations and paired random seeds.
- The relational adapter encodes two signed goal-offset axes in the original goal channels.
  It uses observed coordinates, keeps the at-goal flag and leaves the rest of the public
  input unchanged. This is an engineered representation.

## Audit budget and interpretation

Use seeds 1–10, six goal pairs per split and three frozen repeats per pair. Compare the existing
goal-aware public maze heuristic with goal-blind uniform random. Count actual deliveries,
decisions, failed rows and offline oracle checks. Require every fixture to pass the
simulator's feasibility check and the blinded traces to agree. Flag any held-out topology
where heuristic completion is at or below 50% for fixture review before learner tuning.
The deterministic heuristic repeats are a scoring integration check and have the same
information as one run per goal. Aggregate rates are descriptive.

```sh
node game/world/test_stateful_goal_pairs.mjs
node game/world/stateful_goal_pairs.mjs OUT.json 1 2 3 4 5 6 7 8 9 10
python research/result_schema.py --check OUT.json
```

The tight horizon filters out layouts that require a probe or recovery beyond an optimal route.
Evaluation layouts are public exploratory fixtures. For confirmation, freeze externally held
manifests, register dev-only rate selection and interaction budgets, and pair absolute,
relative and blinded learner arms against public-history comparators. Test delayed reward and
retention as separate endpoints. M1–M8 remain HOLD.
