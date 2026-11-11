# Continual-learning archive integrity gate (partial #154)

This is a **fast, deterministic archive check**, not a live performance regression benchmark
and not evidence that the creature improved. It validates the actual committed `brain-result/1` held-out,
reversal, replay-sampler (#152) and shared-network RL (#153) artifacts, pins their exact Git blob IDs, and checks experiment splits, seed
coverage, failure/timeout rows, forgetting arithmetic, reversal retention recomputation,
and optional checkpoint file SHA-256 references. It includes mutation tests so corrupt
results cannot silently pass. No new model training is performed by this gate.

Run `python research/test_continual_guard.py` or `python research/continual_guard.py`.
Original, much slower scientific runs:
`node game/world/heldout.mjs 1 2 3 4 5 6 7 8 9 10 --out research/results/heldout-new.json`
and `node game/world/reversal.mjs 1 2 3 4 5 6 7 8 9 10 --out research/results/reversal-new.json`.
Validate with `python research/result_schema.py --check FILE.json` and compare
in `python research/dashboard.py`.

**Known weaknesses are preserved:** held-out pretrained seed 5 failed read; seed 7
timed out during copy. Scratch seed 5 was not started. These are not counted as
successful transfer. In the replay comparison `sleep-no-replay` seed 9, `sleep-td` seed 8 and
`sleep-failure` seed 5 timed out and stay pinned as timeouts; the gate also fixes its budgets,
and for the shared-network runs the no-task-ID input, the creature-matched step budget and
full skill coverage. The archive guard does not optimize on the evaluation split.

Still open in #154: cheap **live** behavioral gates from a versioned checkpoint,
pre/post held-out and reversal scores for every mechanism change (the replay samplers
have curriculum retention only), and multi-seed uncertainty. The pinned
historical numbers must not be mistaken for tests of the current working tree.
