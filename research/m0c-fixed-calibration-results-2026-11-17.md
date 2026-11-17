# M0c ten-seed fixed-task calibration results (2026-11-17)

**Executed exploratory experiment; advanced M1–M8 remain HOLD.** This task repeats one public-observation 5x5 pickup–east–drop configuration, not a genuinely novel heldout environment. [Registered protocol](m0c-fixed-calibration-protocol-2026-11-17.md).

**Provenance:** [PR #205](https://github.com/faheemkhaskheli9/Brain/pull/205); tested source branch [a03f5ddb](https://github.com/faheemkhaskheli9/Brain/commit/a03f5ddb748e248005339c9fb7d31b1b9e692576), successful [GitHub Actions run 44100531505](https://github.com/faheemkhaskheli9/Brain/actions/runs/44100531505); brain-result/1 checkout field commit a053179 is the PR test-merge SHA, not main. Ten seeds (1–10), seven arms, **70 complete records**, no errors. Exactly 4,000 training environment decisions per trained policy and zero online oracle calls; random trains zero. Checkpoints at 0/250/1000/4000 decisions, with 12 frozen repeated-task episodes plus 12 trials of each of two nearby, unsealed variants per checkpoint.

## Physical item-delivery success

| Policy | Before training | After 4,000 decisions | After on nearby diagnostic variants |
|---|---:|---:|---:|
| Backprop-free Brain | 5.00% | 9.17% | 5.42% |
| Tabular Q, public absolute state | 0.83% | 100.00% | 2.92% |
| Tabular Q, engineered relative state | 0.83% | 100.00% | 55.00% |
| Relative Q, higher exploration (epsilon 0.5) | 0.83% | 100.00% | 53.33% |
| Relative Q, engineered potential reward | 0.83% | 100.00% | 58.75% |
| Relative Q, zero learning reward | 0.83% | 0.83% | 2.92% |
| Uniform random (untrained) | 0.83% | 0.83% | 2.92% |

**Statistical caution:** Brain's before-to-after mean paired gain was **+4.17 percentage points**, paired seed-bootstrap 95% interval **[-0.83, +10.83] pp** (includes zero). Its post-training success had 95% CI **[2.50%, 15.83%]**. The after-training Brain-minus-relative-Q difference was **-90.83 pp**, paired 95% CI **[-97.50, -84.17] pp**. These descriptive intervals do not isolate learning-rule superiority: Q uses different network capacity and supplied state encodings. Source analysis uses 10,000 seeded resamples across ten independent random seeds.

**Causal/negative controls:** the simulator's public state and physical reward are sufficient for strong in-sample tabular learning. The same-table zero-reward control remained at the untrained accidental-success rate, indicating reward dependence for that tabular training configuration. The relative-state table's strong nearby variation performance comes with **handcoded target-relative geometry**; potential-based feedback additionally supplies distance/carrying expertise. Neither demonstrates that Brain learned a world model or transfer. The 4,000-step budget is matched in physical decisions, not model size or number of completed episodes.

## Complete evidence and reproduction

- [Raw per-seed brain-result/1](results/m0c-fixed-calibration-10seed-2026-11-17.json): 70 full rows with checkpoint curves, physical actions, pickups, invalid actions, successes and native-versus-training feedback.
- [Paired bootstrap analysis](results/m0c-fixed-calibration-analysis-2026-11-17.json), reproducible with [analyze_m0c_calibration.py](analyze_m0c_calibration.py).
- Integrity and mutation controls: [check_m0c_calibration.py](check_m0c_calibration.py) and [test_check_m0c_calibration.py](test_check_m0c_calibration.py).

Run from the repository root:

    python research/result_schema.py --check research/results/m0c-fixed-calibration-10seed-2026-11-17.json
    python research/check_m0c_calibration.py research/results/m0c-fixed-calibration-10seed-2026-11-17.json
    python research/analyze_m0c_calibration.py research/results/m0c-fixed-calibration-10seed-2026-11-17.json

## Adversarial decision

**Do not promote M1 or claim AGI.** A repeated easy task is not independent transfer; nearby variants were exposed diagnostic probes, not sealed evaluation. Brain's small gain is not statistically resolved. Supplied Q relative coordinates and reward potential do not count as autonomously discovered planning. Before adding more network regions, test input accessibility of item/goal/carrying channels, action entropy and one-step/two-step TD/eligibility-trace calculations with matched feedback and negative controls, then evaluate on independent structural families. Keep all negative results. No new neuroscience claim is justified in claims.tsv.

Background only: [Ng, Harada & Russell 1999](https://dl.acm.org/doi/10.5555/645528.657613) formalizes potential-based reward shaping under assumptions; it does not demonstrate biological validity for this model.
