# M0c frozen-step credit protocol: preregistration (2026-11-24)

**Status: preregistered before the full run. Advancement remains HOLD M1–M8.** Implements the four next steps from the [Round 27 step-size review](m0c-credit-step-size-review-2026-11-23.md). Results go in a separate dated note. This file is not edited after the run.

**Inspected source:** main `761ca92d046b27300be40b637c07f6d9e86bfc6a`; `game/world/brain.js` (constructor wiring, `encode`, `act`, `learn`), `game/world/stateful_construct.mjs`, `game/world/stateful_credit_probe.mjs`.
**New code:** `game/world/stateful_credit_protocol.mjs`, `game/world/test_stateful_credit_protocol.mjs`, `research/analyze_m0c_credit_protocol.py`, `research/test_analyze_m0c_credit_protocol.py`. Brain source and its backprop-free rule are unchanged.

## Design

- **Task family (code-observed):** a 5×5 grid with no walls and a 12-step cap. The agent starts on the item at [2,0]. It must pick the item up, carry it and drop it on the goal, with every goal 3–4 primitives away. The goal splits are disjoint:
  - development [0,0] [2,2] [3,1]
  - train [1,1] [4,0] [2,1]
  - heldout [1,0] [3,0], never trained
- **Seeds:** development seeds 101–105; evaluation seeds 1–10. The code rejects any overlap between the two sets.
- **Step-size selection (plan step 1):**
  - Grid: `lrP` and `lrV` both scaled by ×1, ×2, ×4 or ×8.
  - Selection uses the native arm only, on development goals and development seeds only, with 8,000 training decisions and 12 frozen trials per goal.
  - Rule: highest mean development success wins; a diverged run counts as 0; ties go to the smaller scale.
  - Evaluation runs at ×1 and at the selected scale. If ×1 is selected, the best other scale is used instead.
  - The selected scale is computed in code, and the analyzer recomputes it from the raw rows.
- **Arms:** each arm trains for 8,000 decisions on train goals, with the same goal order per seed. Each is scored frozen on train goals and on heldout goals, 12 trials per goal, before and after training.
  - `native`: the unchanged Brain rule.
  - `aligned` (plan step 3): moves the three item cells that land on Brain's multiplicative cochlea gain inputs (indices 47–49) to unused drive inputs 84–86. Nothing else changes.
  - `mask-goal`: goal plane and at-goal flag zeroed; the goal-blind control.
  - `yoked-reward` (plan step 2): replaces the tautological zero-feedback arm. It receives native's reward sequence from the same seed and scale, decision by decision, so its TD error is nonzero but its reward is not contingent on its own actions.
  - `trace-one-step`: previous-step eligibility cleared.
  - `no-bootstrap`: next-state value removed from the TD target.
  - `no-hidden`: all hidden units gated off, leaving the direct actor and critic only. This also lowers the running |h|² normaliser, so its effective step size differs; it is logged as `meanActorStep`.
- **Telemetry:**
  - mean effective actor step `lrP/(1+hh)`
  - pairwise goal-counterfactual policy L1 at the start and after pickup
  - share of hidden fan-in reading inputs that can be nonzero (`fanIn`)

## Preregistered analysis

The primary metric is frozen trained-goal success per seed. Diverged rows are kept and score 0.

At each evaluation scale there are six paired contrasts:

| Contrast | Comparison |
|---|---|
| goal-use | native − mask-goal |
| reward-contingency | native − yoked-reward |
| eligibility | native − trace-one-step |
| bootstrap | native − no-bootstrap |
| gain-layout | aligned − native |
| hidden-layer | native − no-hidden |

Each contrast gets an exact two-sided paired sign-flip test over the 10 seeds, with Holm correction across all 12 tests (α = 0.05), and a 10,000-draw seed-bootstrap 95% CI.

**Falsifiers:**

1. Goal-conditional learning at the frozen step size is supported only if goal-use at the selected scale is positive and Holm-significant. Otherwise the 2026-11-23 "goal-insensitive memorisation" reading stands.
2. Heldout goal use is supported only if the bootstrap CI of native − mask-goal heldout success, at the selected scale, excludes 0.
3. A mechanism claim (eligibility, bootstrap, hidden layer, reward contingency) is made only if its contrast is Holm-significant at **both** step sizes. A contrast significant at one scale only is reported as step-size dependent.

## Known limits

- This is one toy family. The heldout goals share geometry, start cell and item position with the training goals.
- Ten seeds give low power.
- Trajectories diverge between arms, so equal decision budgets do not mean equal experience.
- The two scale factors (`lrP`, `lrV`) are tied.
- About 11% of hidden fan-in still reads always-zero inputs 87–106 in both layouts.

Passing every falsifier would not justify advancing M1–M8 or changing claims.tsv.

## Reproduce

```
node game/world/test_stateful_credit_protocol.mjs
python research/test_analyze_m0c_credit_protocol.py
node game/world/stateful_credit_protocol.mjs --out OUT.json 1 2 3 4 5 6 7 8 9 10
python research/result_schema.py --check OUT.json
python research/analyze_m0c_credit_protocol.py OUT.json ANALYSIS.json
```

## Amendment 1 (2026-11-24, after run 1; appended, design above unchanged otherwise)

**Defect found in run 1 (code-observed):** in the preregistered `yoked-reward` arm, the tape came from native on the *same* seed. Yoked shares native's initial weights and action RNG, so it replays native's actions, its tape reward equals its own reward at every step, and it learns exactly as native does. Every one of the 20 seed × scale rows was identical to native. The control tested nothing.

**Fix:** the tape now comes from a separate donor native learner on the same seed, goal order, budget and scale, but with a different initialisation and RNG (`DONOR_SALT` 503). Each row logs `tapeMatchesOwnRewards`. The analyzer rejects any row where this is 1. All other arms, the selection and the analysis are unchanged. Run 1's raw output is preserved as `results/m0c-frozen-step-run1-degenerate-yoke-2026-11-24.json`; the current analyzer rejects it because the field is missing.
