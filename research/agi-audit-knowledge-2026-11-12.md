# Brain: M0 code audit and external benchmark knowledge (2026-11-12)

Status: **source inspection and reviewed design only**. Reviewed main commit 49e2c6f1 and PR #194 head eefd33e3, not an executed scientific result. These findings are captured before implementation to prevent them being lost between tasks. The action plan is [blueprint v1.1](agi-execution-blueprint-v1.1-2026-11-12.md) and history is [review ledger](agi-review-ledger.md).

## Source-backed observations

| Source | Direct observation | Consequence |
| --- | --- | --- |
| [stateful_options.mjs](../game/world/stateful_options.mjs) trainPhase/episode | Full episodes are added to a decision budget without a remaining-budget parameter. EXIT consumes a decision without a physical transition, and metadata explicitly admits episode-boundary overshoot. | Exact learner interaction budgets and termination accounting are M0b, not a future optimization. |
| [stateful_options.mjs](../game/world/stateful_options.mjs) frozenEpisode/modelDigest | Snapshots select rand function pointer, h, dopamine, pi, nActive/nEncode and two flags; digest uses P/v/wIn/bias/gate/ev/eP/proto/uses. | Exhaustive isolation and adversarial mutation tests are needed, even if existing isolated tests pass. This is a *risk*, not proof of a demonstrated frozen-eval bug. |
| [brain.js](../game/world/brain.js) Brain constructor/act/learn | Additional mutable or persistent state includes idx, fast/slow, active, epS/epN, hh, synaptic importance, eligibility, hidden h and optional caches. act samples a random number even when greedy chooses argmax. | Distinguish full actor state, saving, and scoring state; evaluate on independently seeded clone. |
| [brain.js](../game/world/brain.js) World.toJSON/fromJSON | The World save is designed to resume by replaying the current episode, not to serialize an exact arbitrary in-episode Brain execution state. | Do not treat normal World save/load as a bit-exact mid-episode actor clone. |
| [stateful_construct.mjs](../game/world/stateful_construct.mjs) FAMILIES/OBSTACLES/generate | Each train/dev/eval partition draws four corner relations and four fixed obstacle arrays, START=[2,0], maxSteps=40. Thus at most 16 goal-layout patterns exist per split (IDs can differ). | A held-out pair is not evidence of independence from the simulator family; create new structural/dynamics holdouts. |
| [stateful_construct.mjs](../game/world/stateful_construct.mjs) observe/transition | Agent, item, goal and adjacent blockage are public; whole obstacle map is not; invalid actions receive penalties and still consume transitions. | Controls must use the same partial information; keep invalid actions available to measure error correction. |
| [stateful_options.mjs](../game/world/stateful_options.mjs) oracle/selectOption | BFS oracle reports path length as success; it is not stepped as a policy. Option selection reads carrying state (engineered), while action/EXIT policies are learned. | Oracle only supplies feasibility upper bounds; distinguish engineered initiation from discovered temporally extended skills. |

## External primary-source research used for protocol design

- Sutton, Precup, Singh (1999), *Between MDPs and semi-MDPs*, [DOI 10.1016/S0004-3702(99)00052-1](https://doi.org/10.1016/S0004-3702(99)00052-1): formalizes an option using initiation set, policy and termination. This supports terminology and the separate discovery gate; it does **not** demonstrate that current Brain options are autonomously discovered.
- Chollet et al. (2025), [ARC-AGI-2 technical report](https://arxiv.org/abs/2505.11831), and [ARC Prize benchmark documentation](https://arcprize.org/arc-agi/2): independent public and held-out evaluation partitions target generalization on novel symbolic tasks. The transfer-testing principle motivates sealed evaluation; ARC-AGI-2 scores are **not** evidence about Brain's embodied learner and do not establish AGI.
- Chollet et al. (2026), [ARC Prize 2025 technical report](https://arxiv.org/abs/2601.10904): explicitly discusses evaluation contamination and iterative task refinement. Design response is separation of diagnostic tuning from sealed confirmation. This is a literature-derived motivation, not a repository measurement.

## Claim taxonomy and open checks

- **Established from inspected code:** current budget logic can overshoot; fixed 4×4 generator families; partial snapshot/digest implementation; externally engineered option routing; codec and connectome are not end-to-end learned competence.
- **Hypotheses, unverified:** the existing frozenEpisode actually changes later learning under particular flags; stronger tabular/gradient controls will learn; larger generator-family holdouts will expose a drop; new sparse learning improves competence.
- **No tests or experiments run in this review.** The next code PR must add the deterministic reproduction and record the actual result. Do not mark a behaviour claim as measured or update claims.tsv from this note alone.

## Reuse / no duplication

Follow issues #120 and #136, with implementation checks owned by #110–#115, #131, #153 and #154. Reuse brain-result/1, continual_guard.py, the existing result dashboard and the repository's research notes. Preserve the older negative outcomes on replay, transfer, context and reaching rather than replacing them with unsupported positive statements.
