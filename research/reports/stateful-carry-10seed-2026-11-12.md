# Stateful carry Gate B: ten-seed diagnostic — failed learning gate

**2026-11-12 · negative diagnostic · no AGI/reusable-option claim.**

Executed [GitHub Actions run 43152633806](https://github.com/faheemkhaskheli9/Brain/actions/runs/43152633806)
at commit `433e80c`. Raw `brain-result/1` audit:
`carry-gate-b-10seed.json` SHA-256
`91f58b117021abcab6cd7c29ccb3deba2f660366dcddda4417c4e77f2008434c`.
Paired analysis: `carry-gate-b-10seed-analysis.json` SHA-256
`40df4e06a594eb9ecd72c1afa1deaf8d03f024636fedaeb90ae75a178a2ad650`.
Both artifacts are retained in the Actions run. No failures or missing seeds.

## Preregistered setup

Paired seeds **1–10**. Each trained arm uses **exactly 10,000 primitive decisions**.
Training tasks: 40/seed, development: 12/seed, final held-out: 30/seed × 2 evaluation repeats.
Development includes wet-drop geometry/rule; frozen held-out uses turn-drop. Evaluation preserves
impossible goals, failed pickups, interruptions, timed forced drops and complete denominator.
`research/analyze_stateful_carry.py` chooses the reference controller *only from development*
scores, then computes seed-cluster paired intervals on held-out results.

## Results

| Controller | Development success | Held-out success | Note |
|---|---:|---:|---|
| Flat backprop-free Brain | 1.25% | 0.33% | Goal sensor visible; trained for 10k actions |
| Flat Brain, goal hidden | 0.83% | 0.50% | Ablation |
| Tabular Q, original tie-biased implementation | 0.00% | 0.00% | **Unfair tie-breaking; superseded by #187** |
| Legal random | 0.00% | 0.17% | Equal action mask, untrained |
| Fixed action macro | 0.00% | 0.00% | Deliberately observation-independent |
| Hand-coded BFS-style navigator | 91.67% | **90.00%** | Engineered navigation, 0 training actions |

The development-selected strongest eligible non-oracle comparator is the hand-coded
navigator. On 10 paired seeds, flat Brain vs navigator has held-out success difference
**-89.7 percentage points**, paired seed bootstrap 95% interval **[-90.0,-89.2]**;
two-sided exact sign-flip p=0.00195. Strong evidence that the present learning setup
does not solve this dependent-action task, **not** evidence that hierarchical learning
is impossible in general.

## Adversarial review and result validity

- **P0 — sparse learning signal:** rewards are mainly a small terminal placement success after acquiring, carrying and navigating. Flat learners almost never complete tasks and cannot credit the prerequisites. Add reward-shaping *ablations* shared across baselines and keep the original sparse protocol archived.
- **P0 — weak tabular comparator:** ties in unseen states always selected first legal action. Corrected by seeded random tie-breaking in [#187](https://github.com/faheemkhaskheli9/Brain/pull/187); tabular-zero here is **not** a credible strong-baseline result. Rerun this arm after correction before any relative-performance claim.
- **P0 — open-loop versus reactive controls:** the hand-coded heuristic uses public state each action and succeeds despite hidden transition rules. Fixed macro is weak as intended and cannot substantiate a learned option benefit by itself.
- **P0 — goal-use falsification:** the previous [ten-seed construction diagnostic](construction-diagnostics-10seed-2026-11-12.md) found goal-hidden policies scoring unusually well; this task distinguishes target positions, but goal-sensitive training itself is still unsuccessful.
- **P1 — sample accounting:** two repeats per task are nested within each seed; use ten seed pairs, not 600 episodes as independent evidence. Keep all timeouts and impossible goals.
- **P1 — teacher privilege and fairness:** the BFS controller uses graph search over visible walls, not an oracle future RNG. Label engineered advantage. Any future shaping, memory, action masks or option behavior must be disclosed and matched across arms.

## Decision

**Gate B does not pass. Gate C (learned initiation, intra-option policy and termination) remains blocked.**
Do not interpret adding an options API as solving these prerequisites. Next implement a separately
preregistered curriculum and symmetric potential-based reward-shaping ablation, with positive and
negative controls, development-only tuning, counterfactual target swaps and a corrected tabular-Q
baseline. Freeze fresh held-out seeds before evaluating a new mechanism. Do not retrofit this
original held-out set to claim a confirmed gain.
