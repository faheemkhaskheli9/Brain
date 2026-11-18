# Stateful option transfer: failed preregistered pilot (2026-11-12)

**Question:** Does separating a local three-factor actor-critic into
observable-state-gated option policies improve unseen acquire/carry/place
success beyond the flat policy at equal interaction-decision budgets?

**Design:** 5×5 room with one visible object, goal, obstacles, pickup/drop
and recoverable wrong placement; supplied primitive actions and task reward.
Train, development adaptation, and frozen evaluation use **disjoint
item-to-goal pair families**; random seed, wall configurations and initial
sensory encoding are explicitly fixed. Option initiation and the gate
using the carrying flag are **engineered**, not learned. The actor within
each option and its voluntary exit probabilities are learned via Brain
World's existing backprop-free rule.

**Protocol:** 10 paired seeds (1–10), per-learned-arm 10,000 training
decisions on train pairs, 2,000 development adaptation decisions, 32
training tasks, 16 frozen held-out tasks, two scoring attempts each
(32 attempts/seed/arm). Both option exits and primitive acts count toward
decision budgets; environment transitions are separately logged.
All 70 arm/seed entries completed with `status=ok`.

Run (from repository root):

```bash
node game/world/stateful_options.mjs 1 2 3 4 5 6 7 8 9 10 --train-steps 10000 --adapt-steps 2000 --train-tasks 32 --eval-tasks 16 --repeats 2 --out /tmp/stateful-options.json
python research/result_schema.py --check /tmp/stateful-options.json
python research/analyze_stateful_options.py /tmp/stateful-options.json
```

The analyzer exits nonzero when the scientific criterion fails.
**A failed criterion is a valid negative finding**, not an experiment
execution error. Primary effect must be at least +0.10 absolute frozen
success versus every preregistered matched learned control, paired
95% intervals must exclude zero in the desired direction, and the lower
95% source-retention delta must not be below −0.05.

The run was validated on
[GitHub Actions 43130661102](https://github.com/faheemkhaskheli9/Brain/actions/runs/43130661102).
The complete, validated 70-run `brain-result/1` JSON and `gate.json`
are available in `stateful-options-10seed` (90-day retention). Exact
scientific run metadata inside the artifact: short checkout SHA
`9443e8e`, Node v22.23.4, 2026-11-12T00:54:48Z.

## Results: frozen held-out goal pairs

| Arm | Held-out success | Source success before/after dev adaptation | Parameters/bytes |
|---|---:|---:|---:|
| flat local learner | 0.000 | 0.000 / 0.000 | 0.150 MB |
| flat, goal masked | 0.000 | 0.000 / 0.000 | 0.150 MB |
| two-option learner | 0.000 | 0.003 / 0.000 | 0.301 MB |
| option gate shuffled | 0.000 | 0.000 / 0.006 | 0.301 MB |
| option exit disabled | 0.000 | 0.000 / 0.000 | 0.301 MB |
| uniform random policy | 0.000 | 0.000 / 0.000 | no trained parameters |
| engineered BFS oracle (upper bound) | 1.000 | 1.000 / 1.000 | no trained parameters |

*The source success values are per-scored-episode rates, not evidence
of robust skill acquisition.* The two-option arm had **zero-shot and
post-adaptation held-out success 0.000**. Difference against the primary
flat learner = 0.000 (paired bootstrap 95% CI [0, 0], exact sign-flip
p = 1.000). Mean old-skill change = −0.0031
(95% CI [−0.0094, 0]). The preregistered decision rule **failed**.

## Adversarial diagnosis

1. **Task solvable does not mean task learnable.** The oracle succeeds
   in every held-out episode, but flat and random both score 0.000.
   Without a non-oracle learner solving simpler components, the target
   task is too difficult to use as evidence of beneficial option design.
2. **The voluntary exit is effectively a no-op.** The manager re-selects
   the *same* option whenever the public carrying flag is unchanged.
   That permits the option to waste an entire episode on repeated exit
   actions rather than changing a plan.
3. **Collapse in action selection:** the two-option arm averages
   2,082.5 voluntary exits per 32 held-out episodes, out of the fixed
   2,560 decision allowance (≈81.3%). It executes only about 477.5
   primitive interactions across those 32 episodes. Exit-disabled
   options also fail, so eliminating exit alone is **not** sufficient.
4. **Two models cost twice the memory:** 0.301 vs 0.150 MB of recorded
   model arrays, yet neither arm transfers. Fairness therefore requires
   a same-capacity flat alternative before a strong future claim.
5. **Near-zero source performance makes forgetting uninformative.**
   The small source-retention delta cannot be called 'good retention':
   no source competence was demonstrated.
6. **Selection on the frozen test is forbidden.** These 10 seeds and
   goal pairs are now used for the reported negative result. Do not tune
   exit penalties, curriculum, or shaping to improve this frozen
   score and then reuse the same tasks as confirmatory evidence.

## Decision and next falsifier

**Reject the present option design as an effective transfer mechanism
under this preregistered setup; preserve the negative result.** Do not
promote it as a learned skill hierarchy or a human-like learning claim.

Next work stays under existing #112 (not a duplicate issue):
establish a curriculum of independently verified pickup, navigation
and delivery subskills on *development tasks*; compare flat and
hierarchical local learners under matched decisions/parameters;
make option termination actually transfer control to a learned manager
rather than re-entering an identical option; publish new data and
preregister a *new, untouched holdout* before any further
confirmatory claim. No architectural gain is assumed.
