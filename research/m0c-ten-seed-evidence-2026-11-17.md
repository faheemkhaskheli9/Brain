# M0c exploratory ten-seed results (2026-11-17)

**Status: executed, archived, scientific gate HOLD.** This is an experiment on a hand-authored 5×5 pickup/carry/place simulator, not a finding about brains or achieved general intelligence.

- Source branch head tested: [`38ecbad5`](https://github.com/faheemkhaskheli9/Brain/commit/38ecbad5ef41c1aa00beb2a02e95b74c727d91a5). GitHub Actions [run 44087806775](https://github.com/faheemkhaskheli9/Brain/actions/runs/44087806775) ran checkout of PR test merge commit recorded by `brain-result/1` as `511f6c6`. The authored protocol is [here](m0c-structural-transfer-protocol-2026-11-17.md).
- All three protocol jobs finished successfully; 10 fixed seeds (`1`–`10`) × six arms × three protocols = **180 arm/seed rows**. Every arm scored 16 heldout tasks × two frozen repeats × 10 seeds = **320 evaluated episodes per protocol**. Per-arm counts, exact budgets, unique structure manifests, offline BFS feasibility costs, runtimes, missing/failed rows and CIs are retained in the machine-readable artifacts linked below.

## Physical heldout delivery success (% of episodes)

| Policy | Legacy (10,000 train decisions) | Scattered → barrier (2,500) | Barrier → scattered (2,500) |
|---|---:|---:|---:|
| Backprop-free flat Brain | 0.00% | 0.00% | 0.00% |
| Brain, goal hidden | 0.31% | 0.31% | 0.00% |
| Public absolute-state tabular Q | 0.94% | 0.00% | 0.00% |
| Engineered relative-state tabular Q | 25.00% | 0.94% | 2.50% |
| Uniform random primitives | 0.00% | 0.00% | 0.00% |
| Engineered online maze heuristic | 100.00% | 100.00% | 100.00% |

**Interpretation:** the unmasked backprop-free Brain learner delivered **zero** heldout objects in all three exploratory protocols despite completing its specified training decisions. The goal-masked ablation had isolated successes but is not reliable evidence of goal-directed transfer. Relative-coordinate Q, with a **hand-engineered target-relative representation**, achieved **25.00%** legacy heldout success and **0.94–2.50%** on the two structural transfer directions; it does not demonstrate that Brain learned spatial abstractions. The engineered public sensor-based heuristic reached **100%** on all these *feasibility-filtered* tasks, showing that the authored observation/action interface can support completion **when given pathfinding code**.

### Source-preserved effect estimates and limitations

- **legacy**: Brain success 0.00%, 95% resampled CI [0.00%, 0.00%]; relative Q 25.00%, CI [13.13%, 38.13%]. Comparator selected by development outcome: `public-maze-heuristic`; Brain minus comparator paired heldout delta -100.00 percentage points (95% CI [-100.00, -100.00 pp]).
- **scattered-to-barrier**: Brain success 0.00%, 95% resampled CI [0.00%, 0.00%]; relative Q 0.94%, CI [0.00%, 2.50%]. Comparator selected by development outcome: `public-maze-heuristic`; Brain minus comparator paired heldout delta -100.00 percentage points (95% CI [-100.00, -100.00 pp]).
- **barrier-to-scattered**: Brain success 0.00%, 95% resampled CI [0.00%, 0.00%]; relative Q 2.50%, CI [0.63%, 4.69%]. Comparator selected by development outcome: `public-maze-heuristic`; Brain minus comparator paired heldout delta -100.00 percentage points (95% CI [-100.00, -100.00 pp]).

- These are **paired exploratory bootstrap intervals**, not a preregistered 20-seed sealed confirmatory study. Algorithms differ in representational priors and storage; comparisons do not isolate learning rule superiority. The stress directions use **2,500** train decisions vs legacy **10,000**; rates are not comparable as a fixed-budget architecture ablation across protocols.
- The generator calls BFS privately for task **feasibility filtering**, not online learning. Feasibility rejection creates selection bias. Code-observed provenance and query counts are inside `config.generatorAudits`/`budgets.offlineGeneratorOracleQueries`; policy-level `oracleQueries=0`. Task IDs are omitted from structural fingerprints.
- Frozen source scoring measures **post-training** success on old training tasks, not pre/post retention across adaptation. There is no independent gradient RL comparator and no unprogrammed option-initiation policy. Avoid inferring general intelligence, cortical plasticity, or lifelong learning.

## Raw records (per-seed, with negative runs preserved)

- **legacy** — [complete `brain-result/1` records](results/m0c-legacy-10seed-2026-11-17.json), [paired analysis](results/m0c-legacy-analysis-2026-11-17.json).
- **scattered-to-barrier** — [complete `brain-result/1` records](results/m0c-scattered-to-barrier-10seed-2026-11-17.json), [paired analysis](results/m0c-scattered-to-barrier-analysis-2026-11-17.json).
- **barrier-to-scattered** — [complete `brain-result/1` records](results/m0c-barrier-to-scattered-10seed-2026-11-17.json), [paired analysis](results/m0c-barrier-to-scattered-analysis-2026-11-17.json).

Run `python research/result_schema.py --check research/results/m0c-legacy-10seed-2026-11-17.json` and `python research/analyze_m0c_controls.py research/results/m0c-legacy-10seed-2026-11-17.json` (analogously for both stress protocols). The three GitHub Actions artifact bundles are attached to the source [workflow run](https://github.com/faheemkhaskheli9/Brain/actions/runs/44087806775).

## Decision and next falsification

**REJECT M1 promotion / HOLD advanced architecture.** The critical gap is demonstrated: flat Brain fails physical heldout success while a relative-coordinate learner improves only the repeated-template family and fails to transfer reliably across authored obstacle topologies. Next isolate whether the error is **partial observability/history, sparse credit assignment, action exploration or untrained representation** using a simpler single-family calibration and matched-step interventions. Follow issues [#112](https://github.com/faheemkhaskheli9/Brain/issues/112), [#153](https://github.com/faheemkhaskheli9/Brain/issues/153), and the [review ledger](agi-review-ledger.md). Preserve these negative results rather than tuning against heldout scores.

**Scientific background:** options are a theoretical framework for temporally extended actions (Sutton, Precup & Singh, 1999, [DOI 10.1016/S0004-3702(99)00052-1](https://doi.org/10.1016/S0004-3702(99)00052-1)); that paper does not validate these toy results.
