# Stateful option frozen-evaluation audit (2026-11-12)

**Scope:** M0a evaluation isolation for [Brain World](../game/world/README.md), issues [#112](https://github.com/faheemkhaskheli9/Brain/issues/112) and [#154](https://github.com/faheemkhaskheli9/Brain/issues/154). This is an engineering correctness experiment, not evidence of new neural learning or AGI.

**Baseline reviewed:** main `49e2c6f1d7be3638c7ead724554e7acd1812d2ff`, before the change; existing v1.1 plan in [PR #194](https://github.com/faheemkhaskheli9/Brain/pull/194) (not on main when code work began). Initial code commit: `98544659bbc2f9c7fcf3a91d3b6e408f3d42e489`.

## Source-grounded issue

In [stateful_options.mjs](../game/world/stateful_options.mjs), the previous `frozenEpisode` temporarily replaced the live Brain random function, ran the live actor with `learning=false`, then restored a **selected** subset of state: rand, h, dopamine, pi, nActive, nEncode and flags. The old `modelDigest` covers only certain arrays. Meanwhile [brain.js](../game/world/brain.js) has additional state such as nested synaptic importance, surprise traces, eligibility, hidden activation, running normalization and optional lazy caches. The previous tests showed that the selected-state path worked for exercised configurations but did not establish general full-state isolation. This was an **integrity risk**, not an observed corrupted result.

## Intervention and falsifiable prediction

Use `cloneForEvaluation(model, seed)` to construct a new actor sharing its original Brain **prototype only**, with a `structuredClone` of its entire currently owned data state and a fresh evaluation RNG. Reject unexpected symbol fields, accessors, functions or other uncloneable state instead of silently aliasing it. `frozenEpisode` acts on the copy and never touches the source actor. Keep the old digest check as a redundant check, not a completeness proof.

**Prediction:** source actor field snapshots and the subsequent seeded training trajectories are identical whether evaluation occurs between two training phases or not; no trained array, nested synaptic array or RNG closure is shared with a scoring clone. Evaluating malformed tasks throws without touching the original actor.

**Regression controls added** in [test_stateful_options.mjs](../game/world/test_stateful_options.mjs):
- Paired flat, engineered-option and shuffled-gate models with identical initialization and training seeds.
- Score a trained learner repeatedly and in reverse task order; compare every owned data field rather than weights only, and verify unchanged source RNG closure identity.
- Deliberately modify clone actor weights, nested synaptic importance and policy buffer; prove originals are unchanged.
- Evaluate with greedy choice on a copy, then deliberately trigger an invalid task; source state must remain untouched.
- Train more steps after scoring and compare every result and field against a never-evaluated matched control.
- Add a future uncloneable field and require fail-closed behavior.

## Adversarial limitations and next work

1. `structuredClone` safely copies the currently owned data graph, but module-wide globals, environment objects and external tools are outside the actor's copy boundary. They require separate anti-leakage controls.
2. The evaluation RNG closure is freshly created, not serialized; equality of future training episodes tests its **noninterference**, not a general restorable RNG-state API. A named, serializable RNG is a future requirement for exact arbitrary mid-episode checkpoints.
3. `modelDigest` still hashes only selected arrays. M0d must implement a versioned exhaustive checkpoint integrity manifest that explicitly covers transient vs persistent state.
4. The present goal families remain small and options still use a supplied carrying flag. M0b exact primitive-decision caps and M0c structural-family benchmarks remain unimplemented in this change.
5. The model learns using the existing local three-factor policy. **No algorithmic improvement or held-out transfer gain is claimed.**

## Evidence / verification

- The reviewed change and tests were committed on a Git branch. GitHub Actions is the source of test verification for this connector-only run.
- Tests and scientific results were **not yet executed or reproduced at the time this note was drafted**; the PR check conclusion must be consulted for final status.
- No claimed score was added to `research/claims.tsv`; no `brain-result/1` performance artifact was created because this is a correctness change, not a new measured learning result.

## Research method and references

- Reuse [research/result_schema.py](result_schema.py) and [continual_guard.py](continual_guard.py), rather than adding reporting infrastructure.
- Reproducibility command once checked out: `node game/world/test_stateful_options.mjs`, plus `node game/world/test_stateful_construct.mjs`, `node game/world/test_continual_live.mjs`, and repository CI.
- Scientific question remains compositional skill learning under fair controls; the options formalism is from Sutton, Precup & Singh (1999), [DOI: 10.1016/S0004-3702(99)00052-1](https://doi.org/10.1016/S0004-3702(99)00052-1). That formalism does not verify any behavioral claim here.
