# M0c matched-step, one-drop credit protocol: preregistration (2026-11-25)

**Status: preregistered before the full run. Advancement remains HOLD M1–M8.** This note implements steps 1–3 of the next falsification test in the [Round 28 results](m0c-frozen-step-credit-results-2026-11-24.md). Results go in a separate dated note, and this file is not edited after the run.

**Inspected source:** main `af40c8d2371f1db157e09f916d9eccd2913a5833`, specifically `game/world/brain.js` (`learn`, running |h|² normaliser), `game/world/stateful_construct.mjs` (`transition`, `observe`) and `game/world/stateful_credit_protocol.mjs`.

**New code:**
- `game/world/matched_step_credit_protocol.mjs`
- `game/world/test_matched_step_credit_protocol.mjs`
- `research/analyze_m0c_matched_step.py`
- `research/test_analyze_m0c_matched_step.py`

Brain source and its backprop-free rule are unchanged.

## Defects in Round 28 that this design removes (code-observed)

1. **The step size depends on hidden width.**
   - `learn` applies `lrP/(1 + running |h|²)`.
   - With the hidden gates off, `no-hidden` has a ~9× smaller |h|², so it ran at a ~9× larger per-weight step.
   - Its 72.5% therefore cannot be attributed to the missing layer.
2. **A goal-blind policy could exceed 1/k.**
   - In `stateful_construct.mjs`, a misplaced drop is not terminal, and the item can be picked up again.
   - With 12 steps, a goal-blind sweep (drop at [2,1], then [1,1], then [4,0]) fits exactly.
   - Goal-masked success (31.7%) was therefore not bounded by 1/3.
   - Scoring also drew different random numbers per goal, so even a single-route policy's realised success was not bounded either.
3. **Low power.**
   - There were 10 seeds and 12 Holm-corrected contrasts.

## Design

- **Matched effective step (step 1).**
  - Immediately before each `learn` call, the protocol computes the running |h|² that `learn` is about to compute, using the same terms in the same order.
  - It then sets `lrP = lrV = η·(1 + that value)`, so `learn` applies exactly η per weight on every decision, in every arm. `GAINS` is restored afterwards.
  - Each training row logs `meanActorStep` and `maxStepRelDev`. The analyzer rejects any row whose step differs from η by more than 1e-9 relative.
- **Step-size selection.**
  - Grid η ∈ {0.001, 0.002, 0.004, 0.008, 0.016, 0.032, 0.064}. Round 28's native ×8 ran at 0.0081 and no-hidden at 0.074.
  - Selection uses dev goals [0,0], [2,2] and [3,1] only, dev seeds 101–105 only, 8,000 decisions and 12 frozen trials per goal.
  - Rule: the highest mean **native** dev success wins. A diverged run scores 0, and ties go to the smaller η.
  - The ablations run at the selected η and at the second-best η under the same rule. The analyzer recomputes both from the raw rows.
  - Every arm is also run on the full dev grid. This is descriptive only (per-arm best η): it shows whether a conclusion depends on matching the step.
- **One-drop family (step 3).**
  - Same 5×5 map, no walls, 12-step cap, start and item at [2,0].
  - Goal splits are unchanged: train [1,1] [4,0] [2,1]; heldout [1,0] [3,0], never trained.
  - A misplaced drop now **ends the episode**, and its −0.2 reward is kept.
  - Frozen scoring uses common random numbers: repeat *r* uses the same evaluation seed for every goal. A goal-blind policy then sees identical inputs for every goal up to its first carrying drop, so it delivers on at most one goal per repeat.
  - Its success is therefore **at most 1/k exactly**: 1/3 on trained goals, 1/2 on heldout.
  - The analyzer rejects a goal-masked row with `maxGoalsPerRepeat > 1` or success above 1/k (that would be a goal leak), and rejects nonzero goal-masked policy L1.
- **Arms.** Each arm trains for 8,000 decisions on the train goals, with the same seed-only goal order, and is scored frozen before and after training (12 trials per goal).
  - `native`: the unchanged rule.
  - `mask-goal`: goal plane and at-goal flag zeroed.
  - `trace-one-step`: previous-step eligibility cleared.
  - `no-hidden`: all hidden gates off.
- **Power (step 2).** 20 evaluation seeds (1–20), disjoint from the dev seeds. Only 3 contrasts are tested at each of the 2 step sizes.

## Preregistered analysis

The primary metric is frozen trained-goal success per seed. Diverged rows are kept and score 0.

| Contrast | Comparison |
|---|---|
| goal-use | native − mask-goal |
| eligibility | native − trace-one-step |
| hidden-layer | native − no-hidden |

Each of the 6 tests (3 contrasts × 2 η) gets an exact two-sided paired sign-flip test over 20 seeds and a 10,000-draw seed-bootstrap 95% CI. The sign-flip test is computed exactly by an integer dynamic programme on the 1/36 episode grid, and Holm correction is applied over all 6 tests (α = 0.05).

**Falsifiers:**

1. **Goal-conditional learning** is supported only if both hold at the selected η:
   - goal-use is positive and Holm-significant, and
   - the bootstrap CI of native trained success minus 1/3 excludes 0. No goal-blind policy can exceed 1/3.

   Otherwise the "goal-insensitive memorisation" reading stands.
2. **Heldout goal use** is supported descriptively only if the CI of native − mask-goal heldout success at the selected η excludes 0. Native minus 1/2 is reported alongside.
3. **A mechanism claim** (eligibility, hidden layer) is made only if the contrast is Holm-significant with the same sign at **both** η values. A contrast that is significant at one η only is reported as step-size dependent.

## Known limits

- This is one toy family, and the heldout goals share geometry, start and item position.
- Trajectories still diverge between arms.
- Matching the per-weight step does not match the function-space step. Native's |h|² is larger, so the same η moves its outputs more. The descriptive per-arm dev curves are the check on this.
- The terminal drop changes the reward structure relative to Round 28, so the results are not directly comparable.
- Independent heldout families (#112/#153/#154, step 4) are not tested here.

Passing every falsifier would not justify advancing M1–M8 or changing claims.tsv.

## Reproduce

```
node game/world/test_matched_step_credit_protocol.mjs
python research/test_analyze_m0c_matched_step.py
node game/world/matched_step_credit_protocol.mjs --out OUT.json
python research/result_schema.py --check OUT.json
python research/analyze_m0c_matched_step.py OUT.json ANALYSIS.json
```
