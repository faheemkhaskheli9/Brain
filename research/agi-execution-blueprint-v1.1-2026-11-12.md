# Brain research execution blueprint v1.1 — adversarially revised handoff

Date: 2026-11-12. Status: **implementation-ready for M0; later milestones are conditional research protocols**. Baseline reviewed: main 49e2c6f1 and unmerged PR #194 at eefd33e3. This document supersedes the operational order of [v1.0](agi-execution-blueprint-2026-11-12.md), which remains intact for audit. Additional findings: [knowledge note](agi-audit-knowledge-2026-11-12.md); review history: [append-only ledger](agi-review-ledger.md). Canonical backlog: [#120](https://github.com/faheemkhaskheli9/Brain/issues/120), [#136](https://github.com/faheemkhaskheli9/Brain/issues/136).

## A. Objective and limits

Build a single backprop-free embodied learner that can acquire skills from its own sensor-action-reward stream, correct recurring errors, preserve old skills, generalize to unseen tasks and eventually plan using learned models. **No known implementation path guarantees AGI.** Evidence from a toy simulator cannot establish human-level intelligence. Do not count preprogrammed actions, prompted foundation models, external search, media codecs or stored answers as skills learned by the creature. Conventional gradient RL and LLM agents are separate, explicitly attributed comparisons.

**Do not implement M1 before M0 succeeds.** No extra anatomical regions, new AGI framework or unfunded compute program should be added to bypass a failed learning gate. Prioritize measured learning and independent task generalization over demonstration polish.

## B. Red-team audit: blocking findings and corrections

| ID | Code-backed finding (inspected, not executed) | Failure mechanism | Mandatory correction / rejection test |
| --- | --- | --- | --- |
| F01 | game/world/stateful_options.mjs trainPhase increments decisions by whole episodes; episode has no remaining-budget input; result metadata discloses trainingOvershoot. | Claimed equal training budgets can differ substantially across arms. | Add maxDecisions to episode and enforce exact remaining primitive decisions; tests with budgets 1, 39, 80, 81 and mixed exits. |
| F02 | frozenEpisode saves a small field subset and modelDigest hashes selected arrays; Brain in game/world/brain.js has additional idx, syn, fast/slow, epS/epN, hh, active, h and optional cached pools. | Fingerprint equality alone is not complete noninterference or an auditable checkpoint. | Separate complete serialization of learnable/persistent state from transient state; evaluate on isolated clone; deterministic train-eval-train vs train-train tests, alias mutation tests and full-state fingerprints. |
| F03 | stateful_construct.mjs has four item-goal pairs and four obstacle layouts per split, with fixed start and horizon (at most 16 structural combinations per split). | New task IDs and random seeds can repeat the same tiny templates; the held-out label is not independent environment-family transfer. | Keep legacy suite as regression only; introduce a structurally disjoint generator with new starts, nonisomorphic obstacle maps, affordances, interruptions and perturbations. Fingerprint structure without task.id. |
| F04 | episode() returns a BFS oracle solution length without stepping the environment, while learned/random arms take real transitions. | Oracle can be silently mistaken for a comparable policy and lacks equivalent cost. | Classify oracle as privileged feasibility ceiling only; exclude it from the ranking/control for claims; log all oracle calls/time. |
| F05 | options use a directly supplied carrying-state switch; input observe() also encodes carrying. | An engineered option manager can masquerade as autonomous skill discovery. | Label supplied initiation/termination; add manager-off and observation-derived-manager tests; learned option boundaries are a later independent hypothesis. |
| F06 | observe() exposes the goal and immediate blocked directions, but not the full obstacle map. | A supposedly Markov tabular control may receive privileged global map state or be unfairly memoryless. | Define public-observation-history baselines; compare full-map privileged oracle separately. Test hard partial-observation tasks with and without history. |
| F07 | Primitive action set includes blocked moves and invalid pickup/drop; the options arm additionally has EXIT. | Context-valid filtering can remove the errors the learner must discover, while EXIT changes decision opportunities. | Distinguish syntactically allowed from physically valid actions; preserve failure transitions; count EXIT as a decision and report different action-set capacity. |
| F08 | Same small generated families under 20 new seeds are not independent domain replications. | Confidence intervals may be numerically narrow while external validity stays poor. | Pair by seed **and** generator family; use new independent layout families and an external task generator, report family-wise breakdown and no broad AGI inference. |
| F09 | M0/M1 plans propose strong conventional controls, but existing five-seed shared-RL arm is weak. | A victory against an undertuned control could be a baseline-selection artifact. | Tune each control using only development tasks with documented search budget; preselect strongest non-oracle control before opening the sealed suite. |
| F10 | A positive shaped-reward change can coexist with reduced physical goal hits (continuous motor result). | Reward shaping may optimize a surrogate rather than task competence. | Primary outcome is real held-out successful goal completion; progress reward is secondary; report both and reject endpoint switching. |
| F11 | No automatic Git/knowledge-base promotion can validate an author’s own model-derived claims. | History can look complete while containing unreviewed or unsupported assertions. | Every PR updates dated KB note, ledger, tests and source/provenance status; claims.tsv changes only from validated artifacts. External replication is a separate gate. |

These are **inspection-based concerns**, not reports of newly executed failures. The old pilot, negative results and v1.0 remain unchanged.

## C. Frozen experiment contract to implement before any neural feature

### C1. Run boundary and state machine

Use one versioned task-independent execution record for each attempted arm / seed / generator family / split:

- Observation (public): sensory values and masks, goal cue only when deliberately presented, task-relative step clock, action opportunities. No task ID, split, feasible path, oracle output, hidden obstacle map or future reward.
- Decision: policy action, optional EXIT, option ID, action probability/uncertainty, inferred context and model version. EXIT consumes one **primitive decision** and zero physical transitions; count it in the same budget as all other decisions.
- Transition: only environment calls change physical state. Invalid actions still consume one decision plus one transition and produce observed failure feedback. Timeouts, interruptions and partial episodes have explicit reasons.
- Feedback: observed post-action reward, error class, latency and verification origin. Reward components are logged separately from real completion.
- State: actor weights, indices/topology, eligibilities, SI synaptic importance, surprise traces, hidden activity, recurrent/working memory, counters, RNG state, codecs and saved episodic stores; declare what is persistent versus transient. Include array shape/dtype and schema version.
- Accounting: decisions, environment transitions, episode attempts, policy/model calls, verifier queries, oracle queries, training/adaptation/eval interactions, CPU/wall time, memory bytes, structural operations, failures and reason codes.

Suggested API evolution, subject to existing callers:
- episode(model, task, { learn, seed, greedy, maxDecisions }): returns a reason-coded result, decisions <= maxDecisions, and whether the episode was truncated.
- trainPhase(..., budget): passes remaining decisions to each episode; asserts decisions === budget or an explicit impossible-to-progress terminal reason; never silently rounds up.
- scoreTasks(...) operates on isolated actors plus evaluation-only RNG; training-model snapshot must be bitwise equivalent before and after. Repeated frozen scoring must neither progress learning nor alter subsequent training trajectories.
- Export an exhaustive, versioned modelStateDigest for audits; keep modelDigest's old meaning only if existing consumers demand compatibility. A byte digest of current P/v/wIn alone is **not** a freeze guarantee.

### C2. Determinism and RNG independence

Do not try to clone an opaque JavaScript RNG closure by copying a function reference. Prefer a documented restorable RNG state or deterministic reconstruction from an evaluation seed with a fully copied actor. Maintain separate named streams for initialization, train task sampling, action exploration, evaluation tasks, evaluation actions and baseline tuning. Verify the original actor's next 100 decisions and complete digest are unchanged after isolated evaluation. For greedy tests, note Brain.act currently consumes a random draw even when it later chooses argmax.

State audit must enumerate current Brain members (idx, wIn, bias, gate, proto, uses, fast, slow, active, epS, epN, v, P, ev, eP, syn.P/v with omega/Omega/anchor, dopamine, pi, h, hh, nEncode, nActive, learning, greedy, rand and any lazy caches). Test serialization/restore with ordinary and surprise/SI/learned-feature configurations. Do not use World.toJSON as proof of a mid-episode Brain snapshot: it intentionally replays the episode after load.

### C3. Structured task split contract

Keep original train/dev/eval goal pairs for regression; create a new **family holdout** whose generator parameters are frozen before training. Factor item-goal relation, start location, obstacles, distractors, horizon, sensory availability and dynamics; hold out combinations and entire structural families. Reject duplicate canonical environment fingerprints across disjoint partitions, where the fingerprint excludes ID and random seed but includes all dynamics-relevant structure. Explicitly report overlap by feature family, not only by full-instance hash. Use a second implementation or hand-authored adversarial perturbations for stress, with no tuned access to the final heldout tasks.

A feasibility oracle may label a task set before freezing for stratification, with every call accounted for; it must never supply policy observations, online reward shaping or search hints. Preserve infeasible and impossible-goal stress tasks as a separate endpoint; do not exclude failed model attempts from the denominator.

### C4. Matched controls and fairness

For M0/M1 implement: legal **stepwise** random, open-loop fixed script, reactive heuristic using only permitted observations, goal-masked learner, no-observation learner, tabular history/state-aggregation Q-learning or SARSA, the existing flat backprop-free learner, supplied-option learner and its no-gate/no-termination variants; separately tuned shared gradient RL. Keep privileged full-state BFS as upper bound, not a comparable training arm. Equalize primitive decisions and public information first; disclose pretraining+adaptation counts, parameter bytes, model calls and wall time separately. Do not give a tabular control a global obstacle map or a policy a special runtime transition call.

Ablation arms must not inherit a trained checkpoint unavailable to their comparator. Any external ASR, LLM or solution-memory baseline must be labelled a hybrid and excluded from creature-acquired learning claims.

### C5. Versioned evidence and statistical decision

All evaluation reports use research/result_schema.py's brain-result/1. Each attempted arm × seed × family has one status row, including crashes, nonconvergence, infeasible tasks and timeouts. Store code/tree SHA, exact command and versions, manifests/generator digests, budgets, costs, checkpoint hashes, sealed-suite access log, and raw trace references. Never retroactively delete failed trials.

Development: 10 paired seeds, up to 20,000 **exact** train decisions/arm/seed on a diagnostic suite. Confirmation: after code and hyperparameters are frozen, 20 newly selected sealed seeds **plus at least two genuinely distinct unseen generator families**, with predeclared analysis of family interactions; 100,000 decisions is a ceiling only if diagnostics justify expansion, not an entitlement. Task repetitions are clustered within family/seed, not treated as independent samples. Use paired differences, family-stratified intervals, raw failure counts and a prespecified primary comparison. CI smoke checks measure integrity, not statistical discovery.

Promotion requires (i) real held-out task success improvement >= +0.10 absolute over strongest development-selected non-oracle control; (ii) paired 95% CI lower endpoint > 0; (iii) old-task retention non-inferiority with 95% lower bound > -0.05; (iv) no reproducibility, leakage or budget violation. These are proposed project thresholds, **not empirical results**. If power or a family interaction makes the decision uncertain, status is HOLD, not PASS. Explicitly correct for multiple primary claims when more than one is pursued; exploratory secondary outcomes never override a failed primary. Never tune on opened sealed results.

## D. Ordered implementation PRs: one falsifiable change and review per PR

### M0 — Evidence reliability (MUST complete first)

**M0a: Isolated frozen-state evaluation** (#112, #154)
1. Read Brain constructor/act/learn, stateful_options episode/frozenEpisode and existing tests; document all mutating state and RNG ownership.
2. Add a state snapshot/isolated evaluation actor with explicit type-safe copies, no shared typed-array aliasing and separate evaluation RNG.
3. Replace partial save/restore in frozenEpisode while retaining scoreTasks' public API and old default results where valid.
4. Add tests for eval-before-train, mid-train eval, repeated eval, greediness, save/load, surprise/SI toggles, random stream and mutation attempts.
5. Exit: all post-eval state and next-trajectory invariants hold across 10 deterministic test seeds; regressions green. NO learning-benefit claim.

**M0b: Exact budget and terminal accounting** (#112, #153)
1. Add maxDecisions / truncation handling inside episode, including EXIT, terminal and exception paths.
2. Make trainPhase enforce its exact budget, without post-hoc adjustment of recorded decisions.
3. Emit separate actual decisions, environment steps and optional oracle/model/validator calls; retain earlier metric names as compatibility aliases where possible.
4. Tests: 1, 39, 80, 81, 137 decision ceilings; EXIT-only bursts, malformed tasks, terminal-at-boundary, timeout and training-randomized episodes.
5. Exit: no overshoot, no uncharged action, all started arms and errors present; default sim unaffected.

**M0c: Truly fair diagnostic baseline and data generators** (#110, #112, #153)
1. Factor public history observation into a side-effect-free adapter; use same transition and reward as existing learning arms.
2. Implement legal stepwise random and tabular public-history RL first, with deterministic replay of seed and budget; tune optional stronger shared RL only on development.
3. Add structural fingerprinting and generator-level split manifests; preserve 5×5 legacy cases as regression and create at least two new structurally distinct stress families.
4. Test split overlap rejection, task serialization, path feasibility audit, baseline legal-action parity and zero calls to oracle from any learned arm.
5. Exit: signed manifest hashes and an interpretable learning-vs-random diagnostic exist; no claimed transfer based on repeated templates.

**M0d: Evidence-gate mutation and audit harness** (#154, #131)
1. Extend existing research/continual_guard.py and test_continual_live.mjs; do not invent another result format.
2. Inject corrupted synaptic state, cloned-array alias, evaluation RNG drift, changed split ID/fingerprint, omitted failed run, extra action/EXIT, free oracle call and changed checkpoint.
3. Verify each mutation is rejected and honest empty/null results remain valid; freeze tests separate from expensive science.
4. Save diagnostic brain-result/1, scripts, source hash, limitations, results link in a dated note; update status and claims only with executed evidence.
5. Exit: full immutable audit trail and all synthetic mutations fail closed.

### M1 — Prove learnability, then composition (#110–#112)

**M1a:** Train public-observation tabular/history control on 5×5 tasks at equal budgets, report sample-efficiency curve and actual success. If no control learns over random, repair the task/reward protocol, not the brain architecture. **M1b:** Compare flat vs engineered two-option, no-gate, no-termination, goal-masked, history-free, scratch, no-replay and privileged oracle on unseen structural families. **M1c:** Learn initiation/termination from public transitions instead of carrying-flag rules; remove supplied manager to test causal dependence. Include interruption and incorrect-place recovery. Only claim learned hierarchical control if M1c passes independent checks; otherwise keep supplied options labelled engineered.

### M2 — Sparse sensory-to-motor learning (#65, #94, #95)

**M2a:** Define typed population/edge/action/feedback contracts and golden, deterministic Python→JS fixtures, preserving signed spatial and temporal information. **M2b:** Run manual-weight end-to-end joint control, then local eligibility vs random rewiring, fixed sparse, shuffled feedback and matched dense. Count candidate search, memory, active edges, total operations and wall time; limit growth/pruning per step. **M2c:** Retain one continuous physical body during delayed reward, hidden motor reversal and sensor loss; require goal-hit improvement AND retention bounds, not shaped-reward improvement alone. **M2d:** Optional JS integration only if the independent Python research pilot passes; default Brain World unchanged.

### M3 — Causal mistake correction and memory (#114, #150, #152)

**M3a:** Append observed attempt/prediction/outcome/error and provenance to bounded episodes; verify consequences externally without feeding answer to actor. **M3b:** Compare parameter update, episodic retrieval only, replay, stale/shuffled memory and memory-off at equal steps/bytes; test persistence/eviction/corrupt records. **M3c:** Measure repeated *error type* on structurally unseen tasks after verified corrective experience plus delayed retention; no exact-answer lookup credited as generalization. Reuse old negative prioritized-replay evidence as a control.

### M4 — Learned representations and reusable skills (#65, #110–#112)

**M4a:** Learn local predictive/competitive features from observation history; compare same-capacity frozen random and time-shuffled features. **M4b:** Compositional tasks with withheld affordance relations and sequences, skill interruption and retry; log options' learned initiation, termination and policy changes. **M4c:** Compare flat, authored options, discovered options, retrieval-only, no-sense and separate gradient RL with identical acquisition+adaptation budgets. Hold if results depend on the supplied grammar or features.

### M5 — Predictions, reasoning and bounded planning (#113, #115)

**M5a:** Learn action-conditioned next-observation and reward prediction from actual traces only. Report calibration, changed-rule prediction and rollout errors at 1/2/4/8 steps. **M5b:** Add capped 2–5-step planning with compute and model-call accounting and uncertainty-triggered reactive fallback. **M5c:** Compare with reactive, model-free extra search at matched compute, shuffled/fixed model, oracle upper bound and curiosity-off. Score real environment goals, irreversible failures and model exploitation, not imagined reward.

### M6 — Grounded multimodal learning and output (#94)

**M6a:** Validate image/video/audio/text/touch input contracts, timing, missing modalities, anti-leakage and stored input provenance; codecs are transport only. **M6b:** Train cross-modal causal association in minimal tasks (e.g., sound+object+body action, time-dependent video event, grounded symbol command), with cue-shuffle and single-modality controls. **M6c:** Test learner-produced bounded action symbols/audio/text; do not label re-encoding or foundation-model generation as creature-generated output. Defer open-domain media generation without independent learned capability.

### M7 — Lifelong, social, independently replicated learning (#116, #119)

**M7a:** Evaluate continuous no-reset streams with rule switches, delayed reward, acquisition cost, backwards/forwards transfer and retention across long distractor tasks. **M7b:** Communication with private observations in Ecosystem: on/off/shuffled/costly messages, score individual and group success under changing resources. **M7c:** Reproduce primary results on a second generator and ideally independent implementation, publish scripts, failed runs, compute and citation ledger; archive a signed release. Reject broad intelligence claims if effects disappear.

### M8 — Open-ended hypotheses; not a promised feature release

Only after replicated M0–M7 gains should separate proposals test causal abstraction, compositional tool use, language grounding, open-world planning, safety and external benchmark generality. An ARC-AGI-style independent private evaluation may inform a separate symbolic reasoning track but is not itself proof of AGI or an embodiment benchmark. Consciousness and human-neuron emulation are not declared outcomes.

## E. Mandatory integration/quality and stop rules

- Each code PR includes one owning issue, exact changed files, minimal runnable implementation, tests first, deterministic seeds, before/after metrics, invalid-example safeguards, memory/CPU accounting, full failed-run rows, and explicit PASS/HOLD/REJECT.
- Do not change the default Brain World backprop-free learner by introducing gradient-trained/LLM modules. JS for World/Ecosystem, Python/NumPy for standalone pilots; no heavy dependencies without a measured justification.
- CI: ruff check .; python build_index.py; python run_code_blocks.py; python research/check_claims.py; Python research unit discovery; relevant Node tests (especially test_stateful_options.mjs, test_stateful_construct.mjs, test_continual_live.mjs, test_brain.mjs). Never imply CI smoke is 20-seed scientific evidence.
- Before touching M1, the M0 PRs must establish a clean checkout, reproducible command, sealed-generator manifest and no budget/state leak. Before promotion, commit raw brain-result/1 to research/results plus the manifest and claim/status changes; never overwrite a prior negative.
- Safety: treat agent/environment outputs and retrieved knowledge as untrusted; no automatic tool permission increases or external actions by the research creature. Data licensing, privacy and hardware control limits become explicit gates when real sensor/media inputs or physical bodies are introduced.
- Resource stop: cap environment decisions, validator calls, file sizes, RAM, CPU minutes and test runtime per protocol; stop rather than silently scale a failed arm. Record exact costs and why a run was stopped.
- KB gate on EVERY substantive task: read AGENTS.md/INDEX.md/issue #120/#136/implementation-status and latest ledger; capture verified sources, methods, decisions, failed/null findings, version/time, affected code and unresolved questions in matched topic or dated note; update research/README.md links; append a new numbered ledger entry rather than rewriting old entries; use one logical Git commit per distinct change. Claims.tsv requires a reproducible result, not plausibility.
- Version control: preserve v1.0, this v1.1, append-only review ledger, original benchmark outputs and normal PR/commit history. If a sealed protocol changes after access, fork a new version and new sealed set; do not rewrite v1.1 as if prespecified.

## F. First engineering handoff: M0a exact sequence

1. Branch from latest main after PR #194 is merged, or work on a dedicated child branch; keep dependency to this blueprint explicit. Review live main and open PRs for overlap.
2. Reproduce current game/world/test_stateful_options.mjs; record the actual command and output before any code change.
3. Add a failing test: train A for K decisions; score without learning; continue for J decisions. Train B (identical seed) for K+J without scoring. Compare full persistent state, action trace and resulting checkpoints; cover greedy and stochastic scoring.
4. Enumerate all Brain fields and RNG snapshots in a table; implement evaluation actor cloning with typed arrays and nested SI state copied by value; do not share a closure RNG or refer to mutable model arrays.
5. Test independent clone mutation, exact train-eval-train equivalence, multiple scores, no-learner updates, stable success and restoration after intentional exception.
6. Keep API backwards compatible; run test_stateful_construct.mjs, test_stateful_options.mjs, test_continual_live.mjs and related Brain World tests.
7. Run relevant Python checks, index, claims and lint where the checkout permits; update dated source audit note with tests and limitations; append ledger; commit and open/update the owning PR.
8. If any old score changes, diagnose model-state/seed change and preserve both before and after artifacts. Do not quietly adjust results or say that M0 is complete.

### Version history

- v1.0: initial M0–M8 structure and adversarial rounds 0–4; immutable predecessor.
- v1.1 (this review): rounds 5–8; explicit code-backed blockers F01–F11, exact caps and snapshot contract, structural family holdouts, non-inferiority intervals, ordered PRs, standalone knowledge capture and first test-first implementation handoff. **No new learning algorithm or experimental result is claimed.**
