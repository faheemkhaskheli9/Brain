# Exact-budget stateful options: frozen 10-seed negative evidence (2026-11-12)

**Evidence status:** repository workflow executed and result validated. Scientific advancement gate **FAILED**. Do not infer AGI, autonomous options, task-general intelligence, or biological learning from these toy results.

## Provenance and full raw artifact (retained in Git)

- Executed GitHub Actions [run 43250847229](https://github.com/faheemkhaskheli9/Brain/actions/runs/43250847229), job `131295897015`, completed successfully on PR [#196](https://github.com/faheemkhaskheli9/Brain/pull/196) head commit `bda1db3d8dbeac4167be6f69c3310d0e0decf19a`. **Success of CI means the experiment was executed and archived, not that the hypothesis passed.**
- Original CI artifact ID `13958414726`: `stateful-options-10seed.zip`, SHA-256 `77d996ba93a67ddd236f751b0d9158666b901bcc314d9aa2c6027a79717d2c60`, temporary workflow download. The two original contained files are retained losslessly in permanent Git archive [stateful-options-exact-2026-11-12.tar.br](results/stateful-options-exact-2026-11-12.tar.br): SHA-256 `eb2b6641702f499c50cfb3f114d0aeb39b5bc0ba3263a3780fc71a5c8da1c79f`, Git blob `6405e123e2cba7d46077656ec587a0c075ff1d69`.
- Archive uses Brotli-compressed USTAR with two original unchanged members: `stateful-options-10seed.json` (90,537 bytes, SHA-256 `6694fe237bd4fe72648dbe0cb83d181137afdc9983dc067e89e9530718c1afd4`) and `gate.json` (1,121 bytes, SHA-256 `e7a5f1e46b5d7ea24fb78ebb5f25903abae6acf2105b6a376d57a59e1394ac17`). Decode: `brotli -d research/results/stateful-options-exact-2026-11-12.tar.br -o /tmp/stateful-options-exact.tar && mkdir -p /tmp/stateful-options-exact && tar -xf /tmp/stateful-options-exact.tar -C /tmp/stateful-options-exact`. The `brotli` CLI is needed only to unpack archived results, not by the Brain learner.
- The raw JSON's `commit` is GitHub's ephemeral PR synthetic merge short SHA `9dd250b`; the actual PR **head** verified against Actions API is `bda1db3d8dbeac4167be6f69c3310d0e0decf19a`. These must not be conflated.
- Runtime recorded: Node `v22.23.4`, brain.js save `v5`. Seeds exactly 1–10; 7 arms × 10 seeds = **70 attempted runs**, all `status=ok` (no crashed arms). Each learned arm used **10,000 actual training + 2,000 actual development adaptation primitive decisions**; random and privileged BFS oracle do not train. Frozen held-out evaluation: 16 tasks × 2 repeats per seed, with the engineered goal-pair split.

## Primary results (observed, not guessed)

| Arm | Mean held-out goal completion | Pretraining + adaptation policy decisions |
| --- | ---: | ---: |
| Flat backprop-free | 0.000 | 10,000 + 2,000 |
| Flat, goal masked | 0.000 | 10,000 + 2,000 |
| Engineered two-option | 0.000 | 10,000 + 2,000 |
| Options, no gate | 0.000 | 10,000 + 2,000 |
| Options, no termination | 0.000 | 10,000 + 2,000 |
| Legal-stepwise random (untrained) | 0.000 | 0 |
| Privileged BFS feasibility oracle (untrained ceiling) | 1.000 | 0 (not a matched policy) |

- Preregistered comparison `options - flat`: **0.000** held-out success delta, paired 95% bootstrap CI **[0.000, 0.000]**, exact paired sign-flip **p = 1.000**. Other learned controls all have the same zero held-out success. Primary gate: **FAIL**, with `budget_protocol = exact`.
- Engineered-options source retention change (after dev adaptation − before): **−0.003125** average, 95% paired CI [−0.009375, 0]. This does not compensate for lack of held-out successes.
- The trained options arm made fewer invalid actions than several baselines (mean frozen invalid actions per episode 6.86875 versus flat 12.928125), but its actual held-out completion was still zero. **Do not switch endpoints from success to invalid-action count** after seeing a failed primary.
- Options final training-budget truncation occurred on 9/10 seeds; no-gate on 10/10; flat on 0/10. A future comparison must evaluate sensitivity to budget boundary and policy-specific rollout length.

## Mechanism-level and comparator audit from the raw runs

The engineered option learner averaged **2,559.6 policy decisions** per 32 frozen held-out episodes, but only **480.2 physical transitions**; its mean **2,079.4 EXIT decisions** were **81.24%** of its decisions. A flat learner executed 1,280.0 decisions/transitions. The option manager immediately reselects the same option after EXIT whenever the carrying state has not changed; hence EXIT is often a costly no-op, not a discovered skill-switch decision. The separate [older negative pilot](stateful-options-negative-2026-11-12.md) had independently reported a similar EXIT collapse, so this is **confirmation of an existing failure mode**, not a novel discovery.

**Additional fairness warning:** the policies are matched in **training decisions** but not in frozen **evaluation decision counts or physical transitions**. The flat arm naturally exhausts its 40-step physical episode earlier, whereas the two-option arm can spend the 80-decision cap on EXIT. Report success together with actual decisions, environment steps, model bytes and option exits; the next diagnostic should compare EXIT-disabled/matched-evaluation-allowance controls and track step efficiency. The `options-no-terminate` arm also had **0.000 held-out completion**, so simply forbidding EXIT is not evidence that the underlying learner solves the task.

There is already a different public-observation [tabular-Q, legal random and heuristic baseline](../game/world/stateful_baselines.mjs) for the **separate** [stateful_carry.mjs](../game/world/stateful_carry.mjs) environment. Reuse its tested tabular code/design for an identical-observation baseline on `stateful_construct.mjs` rather than building a duplicate framework. Its performance on the other environment is **not a matched control** for this 5×5 construction pilot.

## Adversarial interpretation and next experiment

This negative finding cannot tell whether (a) the task horizon, reward, observation/hidden layout, or partial observability makes learning implausible; (b) the existing backprop-free actor lacks memory, exploration, credit assignment or training capacity; or (c) the engineered manager harms behavior. The tiny 4×4 per-split authored grammar means this is not independent transfer evidence. The privileged BFS oracle proves only task feasibility with full transition access, not policy learnability from public observations.

**Gate decision: HOLD M1 and later AGI architecture work.** Proceed with [M0c handoff in reviewed blueprint v1.1](https://github.com/faheemkhaskheli9/Brain/blob/docs/agi-v1-reviewed-blueprint-20261112/research/agi-execution-blueprint-v1.1-2026-11-12.md): first implement a public-observation tabular/history policy and legal heuristic with equal experience; test whether *any* unprivileged learner beats random on a deliberately learnable diagnostic. Add independently generated obstacle/start/dynamics families only after the diagnostic. Do not call the engineered option policy a discovered compositional skill. Keep exact budget and full-state scoring tests green.

## Reproduce and check

After extracting the raw archive, run `python research/result_schema.py --check /tmp/stateful-options-exact/stateful-options-10seed.json` and `python research/analyze_stateful_options.py /tmp/stateful-options-exact/stateful-options-10seed.json`; the analyzer intentionally exits nonzero because the scientific gate failed. To rerun, use the exact 10-seed command in [stateful-options-evidence workflow](../.github/workflows/stateful-options-evidence.yml) at head commit `bda1db3d`; **do not overwrite** this result with a subsequent run or compare old overshoot-era outcomes as if budgets matched.

Source: executable repository experiment and independent outcome verification in the GitHub workflow, not a biology paper. See [budget audit](stateful-decision-budget-audit-2026-11-12.md), [implementation status](implementation-status.md), [ledger on the plan PR](https://github.com/faheemkhaskheli9/Brain/pull/194), and issues #112/#153/#154. Preserve future positive and negative findings with the same provenance.
