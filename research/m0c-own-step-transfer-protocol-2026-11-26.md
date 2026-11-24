# M0c own-step and wide-goal transfer protocol: preregistration (2026-11-26)

**Status: preregistered before the full run. Advancement remains HOLD M1–M8.** This note implements steps 1–2 of the next falsification test in the [Round 29 results](m0c-matched-step-credit-results-2026-11-25.md). Results go in a separate dated note, and this file is not edited after the run.

**Inspected source:** `game/world/matched_step_credit_protocol.mjs`, `game/world/stateful_construct.mjs` (`observe`) and `game/world/brain.js` (`learn`).

**New code:**
- `game/world/own_step_transfer_protocol.mjs`
- `game/world/test_own_step_transfer_protocol.mjs`
- `research/analyze_m0c_own_step_transfer.py`
- `research/test_analyze_m0c_own_step_transfer.py`

`matched_step_credit_protocol.mjs` gains optional goal-map arguments, an exported `evalArm` and a `flag-only` sensing arm. With the defaults it reproduces Round 29 rows bit for bit (checked on seed 3, native and no-hidden). Brain source and its backprop-free rule are unchanged.

## Why (code-observed)

1. **Round 29 held every arm at native's step.** No-hidden peaked at η 0.064, the top of the grid, with 54.4% dev success, above native's best of 43.3%. The hidden-layer contrast is untested when each arm uses its own best step.
2. **Heldout transfer with 3 trained goals is close to impossible by construction.** `observe` codes the goal as a one-hot cell (inputs 50–74). A heldout goal's input unit is never active during training. Only the at-goal flag (input 81) and random hidden overlap carry goal information to untrained cells. With 3 trained goals a fixed route per goal suffices, so nothing forces the flag to be used.

## Part A: own step

- Same one-drop family, goal splits, dev seeds, budget (8,000 decisions) and 12 frozen trials per goal as Round 29.
- Grid extended to η ∈ {0.001, …, 0.064, 0.128, 0.256, 0.512}.
- **Rule:** each arm separately takes the η with the highest mean dev success on dev goals [0,0] [2,2] [3,1] and dev seeds 101–105. A diverged run scores 0, and ties go to the smaller η. The analyzer recomputes every choice from the raw rows.
- Each arm is evaluated frozen at its own η on seeds 1–20.
- Contrasts on trained-goal success: hidden-layer (native − no-hidden), eligibility (native − trace-one-step), goal-use (native − mask-goal). Each pairs two arms at their own steps.
- If either arm's η is the grid top (0.512), the contrast is reported **inconclusive (grid edge)**, whatever its p-value.

## Part B: wide-goal transfer

- One-drop family, 5×5, no walls, 12-step cap, start and item at [2,0].
- **Heldout:** 5 interior cells [1,1] [3,1] [2,2] [1,3] [3,3], never trained. Each is surrounded by trained cells.
- **Trained:** the other 19 non-start cells. The farthest goal needs 8 actions, within the cap.
- Goal-blind ceiling (common random numbers): 1/19 on trained goals, **1/5 on heldout goals**.
- **Budget:** 64,000 decisions. Chosen from a dev-seed pilot (seeds 101–102 only): at 8,000–32,000 decisions native stayed at or below 28% trained success.
- **Step selection:** native only, dev seeds 101–105, trained and scored on the 19 trained goals; grid 0.001–0.064; ties go to the smaller η. Heldout goals are never touched during selection.
- **Arms** at that η, matched per-weight step, seeds 1–20:
  - `native`.
  - `mask-goal`: goal plane and at-goal flag zeroed (goal-blind).
  - `flag-only`: goal plane zeroed, at-goal flag kept. Not goal-blind, so no ceiling applies.

## Preregistered analysis

Diverged rows are kept and score 0. Every test is an exact two-sided paired sign-flip over 20 seeds, with a 10,000-draw seed-bootstrap 95% CI. Holm correction is applied over all 5 tests (α = 0.05).

| # | Test | Comparison | Episode grid |
|---|---|---|---|
| A1 | hidden-layer | native − no-hidden, trained, own steps | 1/36 |
| A2 | eligibility | native − trace-one-step, trained, own steps | 1/36 |
| A3 | goal-use | native − mask-goal, trained, own steps | 1/36 |
| B1 | heldout above goal-blind | native heldout − 1/5 | 1/60 |
| B2 | heldout goal-use | native − mask-goal, heldout | 1/60 |

**Falsifiers:**

1. **"The hidden layer helps"** survives only if A1 is positive, Holm-significant and off the grid edge. A significant negative A1 is reported as reversed.
2. **The eligibility trace** gets the same rule (A2).
3. **Heldout transfer** is supported only if B1 is positive and Holm-significant and its CI excludes 0. Otherwise the reading "no transfer to untrained goal cells" stands for the wide family as well.
4. **Descriptive, no test:** native trained − 1/19; flag-only heldout − 1/5; native − flag-only heldout. If flag-only matches native on heldout, any transfer runs through the at-goal flag rather than the goal plane.

## Known limits

- This is one toy family, and the heldout goals share geometry, start and item position.
- Part B uses one η for all arms (matched per-weight step), not each arm's own.
- The wide budget was chosen on a dev-seed pilot. Evaluation seeds were not used.
- Independent heldout families (#112/#153/#154) are still untested.

Passing every falsifier would not justify advancing M1–M8 or changing claims.tsv.

## Reproduce

```
node game/world/test_own_step_transfer_protocol.mjs
python research/test_analyze_m0c_own_step_transfer.py
node game/world/own_step_transfer_protocol.mjs --out OUT.json
python research/result_schema.py --check OUT.json
python research/analyze_m0c_own_step_transfer.py OUT.json ANALYSIS.json
```
