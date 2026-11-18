# M0d — identical-public-transition credit assignment audit

Date: 2026-11-18. Status: **implemented on a research branch; 10-seed evidence pending review**. This is an off-policy mechanistic diagnostic, **not** an autonomous-learning, neural-fidelity, or generalization result.

## Source and exact unresolved gap

Inspected `main` [bcd3c87e561c8e9dbc59b178286b4b22edf604c7](https://github.com/faheemkhaskheli9/Brain/commit/bcd3c87e561c8e9dbc59b178286b4b22edf604c7), including `game/world/brain.js::Brain.act/learn/update`, `game/world/stateful_construct.mjs`, `game/world/stateful_credit_probe.mjs`, `game/world/stateful_options.mjs`, `research/m0c-sensory-credit-results-2026-11-18.md`, and the [adversarial ledger](agi-review-ledger.md). Backlog: [#112](https://github.com/faheemkhaskheli9/Brain/issues/112), [#120](https://github.com/faheemkhaskheli9/Brain/issues/120), [#136](https://github.com/faheemkhaskheli9/Brain/issues/136), [#153](https://github.com/faheemkhaskheli9/Brain/issues/153) and [#154](https://github.com/faheemkhaskheli9/Brain/issues/154).

**Negative evidence motivating this audit:** the [prior 10-seed study](m0c-sensory-credit-results-2026-11-18.md) measured 10.0% three-action same-task delivery, 0% after clearing prior eligibility traces, and 2.5% after removing next-value bootstrap. **Those arms experienced different action/state/reward trajectories**, so their performance gaps cannot isolate credit-rule causality.

## Frozen hypothesis and permitted inference

H0: changing temporal traces or TD bootstrap while holding *every public observation, chosen action, reward, termination and total update* fixed does not measurably alter learned parameters or probe policy.

H1 (mechanistic only): update trajectories differ despite identical source transitions; the amount and direction may depend on initial seed. This demonstrates a computational contribution of the update rule to parameter changes **on a supplied log**. It does not demonstrate that the change improves actual task success.

### Experimental protocol

- Fixed before full evidence execution: seeds **1–10**, **12 logged episodes per seed**, one offline replay pass, seven arms: `native`, `trace-one-step`, `no-bootstrap`, `actor-frozen`, `critic-frozen`, `reward-shifted`, `zero-feedback`.
- Log uses the existing public 5×5 construction observations, same six legal action IDs, actual `transition()` reward/done, three existing calibration task layouts and goals. Tasks cycle; even-numbered episodes begin with **explicit, task-specific supplied demonstration sequences**, odd episodes sample uniform primitives from a seeded RNG. This is engineered data, not a learned skill.
- Each stream is generated **once** for a seed, hashed with SHA-256, and applied unchanged to all seven arms. Logs include public pre/post observations, primitive action and outcome; task index is provenance only and is **not** passed to the actor or critic.
- Use exactly the existing `Brain.encode()`, `Brain.act()` eligibility computation and `Brain.learn()` updates. Force a logged action by substituting only the random draw with the midpoint of its current policy interval; verify the sampled action matches. No `Brain` source or global GAINS changes. No backpropagation.
- `trace-one-step` clears eligibility before the current action. `no-bootstrap` passes a null next feature to `learn`; explicit episode end and observed reward remain unchanged. `actor-frozen` / `critic-frozen` suppress only the corresponding `Brain.update()` parameter-group call. `reward-shifted` cyclically moves the logged rewards seven events while preserving their multiset. `zero-feedback` sets every learner reward to zero.
- Report source stream hash, replay updates, physical log steps, rewards, actor/critic L1 movement, mean absolute TD error, start/carry policy probe changes, supplied demonstration counts, and per-arm model bytes.
- Each arm gets **zero new physical interactions or policy oracle queries** during replay. The logging phase itself interacts with the physical simulator; those source transitions are **shared**, not seven independent training budgets. The test never equates this off-policy update with a true on-policy training run.
- Every row is written to `brain-result/1`, including explicit errors; exact configuration and unpaired/sampled caveats are kept. The PR evidence workflow captures all ten seed streams and seven rows per seed as a downloadable JSON artifact.

### Predeclared integrity and falsification checks

1. Seven arms per seed, 70 records total; all `ok`. For each seed all hashes, public environment-step counts, original reward sums and initial policy probes must agree.
2. All arms replay exactly the same number of updates and zero extra environment or oracle calls.
3. `zero-feedback` produces zero TD and unchanged P/v from zero initialization. `actor-frozen` leaves P unchanged; `critic-frozen` leaves v unchanged.
4. On the regression fixture, removing bootstrap and clearing old eligibility must change the native parameter result. If they do not, the implementation is not isolating those mechanisms or the fixture is uninformative.
5. The reward-shift control keeps total feedback while disturbing temporal assignment. No improvement criterion is inferred from the size of a weight or policy L1 difference.
6. Record failed seeds without dropping them. No `claims.tsv` change without independently checked empirical support.

### Adversarial limitations and next step

**Major confound intentionally retained:** forcing an action without importance correction creates an off-policy learning stream; high reward can come from the supplied demonstration rather than the learner. Tests prove update-level reproducibility, **not** policy competence. The three authored layouts and target probes are neither sealed heldout tasks nor an independent environment family. Ten seeds on one task generator cannot establish generality. Changing the critic update necessarily changes subsequent TD values despite the fixed public transitions; this is the mechanism being tested, not an experimental leak.

If the mechanistic tests pass, the next independent work is a *closed-loop* varying-goal/carry-state training experiment with fresh heldout structural generators, a matched tuned public-state comparator and source-task retention after adaptation. Do not advance M1–M8 or add anatomical complexity based on L1 parameter changes.

## Commands

```bash
node game/world/test_stateful_credit_replay.mjs
node game/world/stateful_credit_replay.mjs 1 2 --episodes 6 --out /tmp/m0d-smoke.json
python research/result_schema.py --check /tmp/m0d-smoke.json
# Predeclared full run:
node game/world/stateful_credit_replay.mjs 1 2 3 4 5 6 7 8 9 10 --episodes 12 --out /tmp/m0d-ten-seed.json
```

**Interpretation boundary:** delayed TD credit and three-factor synaptic plasticity have established theoretical motivations (see [hypothesis register](learning-algorithm-hypotheses.md) H021–H022 and [primary source ledger](learning-algorithm-sources.md)); the effect of this replay intervention on Brain's weights is a repository software test, not biological evidence. Run-dependent conclusions, including negative findings, must be appended to [review history](agi-review-ledger.md) after the full evidence is inspected.
