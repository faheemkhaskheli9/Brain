# Brain AGI research program: versioned execution blueprint v1.0

Date: 2026-11-12. Status: implementation-ready **research protocol**, not an AGI claim.
Scope: Brain World (backprop-free creature), Brain Ecosystem, and the separate sparse-connectome laboratory. Existing roadmap: [#120](https://github.com/faheemkhaskheli9/Brain/issues/120); ordered execution: [#136](https://github.com/faheemkhaskheli9/Brain/issues/136). Review history: [agi-review-ledger.md](agi-review-ledger.md).

## 1. Decision: pursue measurable generality, not another feature inventory

An AGI system is not guaranteed or known to follow from these experiments. The near-term objective is a **single embodied learner** that improves from its own feedback, transfers reusable structure to previously unseen goals, retains old skills, and plans using learned dynamics. Passing staged tests establishes only the tested abilities. Human-level generality would require extensive **independent, unpredictable, cross-domain** assessment beyond this repository.

**Non-negotiable separations:**
- Brain World remains backprop-free. A conventional gradient learner is a comparator; an LLM teacher, ASR, vision foundation model or text generator is an explicitly labeled interface or independent hybrid, never evidence of what the creature learned.
- Designed anatomy is only an inductive bias. The schematic 78-region, 142-edge scaffold is neither a measured human connectome nor a learned controller. Audio/image/video/text codecs currently convert supplied inputs/outputs; they do not understand or generate them.
- The toy sparse policy has evidence for rewiring and motor improvement under engineered cues. Neither proves open-world competence. Anatomical labels, connection count, reward increases, or a successful curriculum do not establish intelligence.
- Reuse existing experiments, issue ownership, schema and test infrastructure. No new meta-framework, dashboard, benchmark format or duplicate backlog.

## 2. Evidence snapshot and blocking gaps (as of main on 2026-11-12)

| Existing substrate | Measured or runnable evidence | What remains unproved |
| --- | --- | --- |
| game/world/brain.js, heldout.mjs, reversal.mjs, continual_guard.py | A backprop-free creature, frozen scoring and archived integrity tests. | Robust unseen compositions, reversals and no-rehearsal retention; remove stage-derived gait assistance as an independent causal test. |
| game/world/stateful_construct.mjs + stateful_options.mjs | Stateful pick/carry/drop and runnable flat/two-option arms; option routing reads a supplied carrying flag. | Learned option initiation, discovery and strong transfer. Do not call this autonomous hierarchy. |
| game/world/rl_multitask.mjs | Shared gradient-based comparator exists, but reported five-seed results are weak. | Appropriately tuned comparable control on independent transfer, reversal and retention. |
| research/structural_connectome.py + sensorimotor_bridge.py + media/audio adapters | Structural ports and bounded joint body; routing initially has no learned weights. | Feature-preserving signal propagation and learned end-to-end sensor-to-action output. |
| research/structural_plasticity.py + learn_reach.py | Sparse reward-modulated local learning and target-error reaching; reversed dynamics damage old-skill retention. | Scaling past engineered sensory vectors; integration with structural regions and natural perception. |
| research/context_memory.py, online_context.py, continuous_motor.py | Reward-based retrieval/switching of **pretrained** controllers in synthetic regimes; some positive control comparisons, one retention criterion failed. | Discovering new contexts/skills independently while preserving body state and handling longer feedback delays. |
| research/result_schema.py, claims.tsv, dashboard.py | Versioned brain-result/1, claims checking and comparative views exist. | Sealed confirmation with honest failures, inference cost, checkpoint provenance and independent replication on every new mechanism. |

The existing [implementation-status.md](implementation-status.md) and dated raw artifacts are the source of truth. Past negative or inconclusive results are never silently superseded by this plan.

## 3. Architecture contracts: one learning loop, many sensors, bounded actions

All learned modules share a single task-independent clock, episode/history identity and provenance. Define versioned typed contracts before integrating implementations:

1. **ObservationFrame**: timestamp, modality (vision pixels, frame sequence, audio spectrum/waveform, Unicode text, touch, proprioception), shape, value range, missing-sensor mask, and source. Preserve sign, spatial arrangement and time; never collapse a full modality into a single absolute scalar.
2. **PopulationState**: sparse active neuron IDs, activations and prior state; explicit mapping to a region and local circuit. Do not encode task, answer, reward oracle or phase in hidden fields.
3. **SynapseState**: source, target, signed local weight, eligibility, utility/age, delay, connectivity version and budget. Only permissible observed events and reward prediction error modify the learned part.
4. **ActionPacket**: bounded motor-pool commands or constrained output-symbol/audio/image actions; legal mask derives from public affordances. Output media must be learner-produced to be scored as generation.
5. **Outcome**: post-action observation, independently computed reward, terminal condition, feedback delay, error type, and provenance. The actor cannot read verifier-only fields.
6. **Experience**: append-only transition and event stream with source checkpoint digest, sensor codec version, seed streams, context estimate, option ID (if any), and independent split ID stored **outside actor observation**.
7. **Checkpoint**: includes weights, topology, encoder states, memory stores, working state, RNG streams, schema, and environment-independent restore tests. Frozen evaluation must use a deep copy or full-state restore, not a weight digest alone.

Control loop: observe -> encode -> recurrent local dynamics -> retrieve/plan if justified -> choose action -> bounded body step -> observe result -> compute error/reward -> update weights and/or memory -> retry -> later test frozen. Diagram labels are **software roles**, not proven homology with cortex/hippocampus/basal ganglia.

Separate research adapters (Python/NumPy) from the production Brain World JavaScript learner until a matched experiment establishes benefit. Make shared contracts and portable deterministic fixtures rather than rewriting one engine in the other language.

### Dynamic sparse plasticity hypothesis H-SP-1

Under the same edge budget B and primitive-action budget T, utility-guided local connection growth plus mature-edge pruning improves held-out sensorimotor success and repeated-error correction over randomly rewired and fixed sparse controls **without worse old-skill retention**.

Initial rule to *test*, not predeclare as biology: reward-modulated local eligibility adjusts occupied edges; grow at most one edge each growth interval from a bounded candidate reservoir scored using only past observable co-activity and signed feedback; prune only low-utility mature edges; enforce per-neuron fan-in/out, no self loops if prohibited, edge-count B, weight clamp, stabilization and a growth cooldown. Compare against uniform growth, static sparse, dense equal-memory/equal-multiplies, privileged topology and feedback-shuffled arms. Log candidate-scoring operations: hidden dense searches do not count as sparse efficiency.

**Fail closed** if utility depends on hidden labels, learning degrades source retention, activity saturates, behavior is scripted, or sparse wall time/memory at equivalent accuracy is not competitive. A successful local rule on toy cues is not an inference about human plasticity.

## 4. Implement in this exact dependency order

Every package ends in a mergeable code PR with deterministic tests, full science artifacts when feasible, review ledger entry, KB update, and an explicit advance/reject/hold decision. Following packages are conditional; a failed gate triggers diagnosis or a smaller alternative, never automatic scaling.

### M0 — Reproducibility and anti-leakage repair (P0, next; #111, #112, #153, #154)

**PR 1: freeze evaluation and expose costs.**
1. Inspect exact existing stateful_options.mjs and brain.js mutable actor state and RNG fields; enumerate all values modified by encoding, acting, scoring and learning.
2. Factor an evaluation clone or complete snapshot/restore. Test train -> eval -> train, eval -> train, repeated eval and greedy/sampled eval all yield identical later training/checkpoint outcomes.
3. Replace ambiguous episode caps with a single **primitive-decision** budget (including exits, failures and overshoot) and separately log true environment actions, model calls, verifier calls and wall time.
4. Add paired public-observation tabular SARSA/Q-learning where state aliasing permits, valid stepwise random, fixed macro, goal-masked, no-observation, and privileged oracle arms. Keep common legal action masks.
5. Generate disjoint training/development/sealed/stress manifests, fingerprint generators and instances, separate RNG streams, and save all raw attempts/errors, including timeouts.
6. Add mutation tests: deliberately corrupt checkpoint, swap task split, duplicate seed, leak answer field, remove failure row, increase query budget, and alter source state during scoring. Each must fail.
7. Run the cheap Node regression suite and Python schema/claim checks; archive a 10-seed **diagnostic** artifact without using it as a confirmatory effect claim.

**Exit:** no known leakage or history mutation, all budget/arm/seed coverage accounted for, archived negatives remain intact. No new learned-options claim before this passes.

**Exact first PR files:** game/world/stateful_options.mjs, game/world/test_stateful_options.mjs, and a small additive evaluation/baseline module if justified; research/results/* only after a reproducible run; reference the amended [adversarial plan](adversarial-implementation-plan.md). Do not rename existing public APIs casually. Keep default Brain World behavior unchanged.

### M1 — Establish a genuinely learnable temporal dependency (P0; #110, #112)

1. Retain the existing stateful pick-carry-place simulator, but vary item/goal/walls/start, failed pickup/drop, distracting objects and interruptions; avoid impossible goals in the primary learnability arm.
2. Supply only observable goal/contacts; use identical public affordance masks for all policies. Test both fully observable and partially observable variants.
3. First show that a trainable tabular agent beats legal stepwise random and a fixed open-loop script under one frozen diagnostic budget. If not, debug observation/reward/horizon; **do not introduce hierarchical learning**.
4. Test flat backprop-free policy, learned two-option policy, options without gate/termination, no-observation, scratch, pretraining, retrieval-only, and privileged BFS.
5. Report zero-shot unseen pair success, adaptation success, repetitions of an error after correction, source-task retention and actual primitive decisions; evaluate on a new generator family, not mere reorderings.
6. If two supplied options beat stronger controls, explicitly keep initiation as engineered. Only later test discovery from transition/bottleneck statistics against fixed options.

**Exit:** precommitted held-out advantage over the strongest non-oracle control, source retention acceptable, and no fixed action script passes the stress suite. If absent, **record a negative result**, keep the flat learner and revisit credit assignment.

### M2 — Close the sparse sensor-to-body loop (P1; #65, #94, #95, #112)

1. Reuse research/sparse_brain_tasks.py, structural_plasticity.py, closed_loop_reach.py, sensorimotor_bridge.py; do not create a second miniature environment.
2. Introduce vector-preserving sparse populations for V1-like visual errors and S1 proprioception; test actual propagation with **manually fixed** weights before learning.
3. Use one SimpleJointBody with no reset between context windows. Restrict actor to observations and post-action reward; test delay 1 and 3, reversal, dropped sensors and drift.
4. Introduce locally adjusted weight/eligibility with bounded growth/pruning. Verify learning-off freezes all learned state; weight topology is absent from actor observations.
5. Compare fixed/random/evidence-growth sparse, equal-size dense, privileged wiring and feedback-shuffled arms at matched interaction/compute budgets. Profile ops, memory, wall time and stability.
6. Only after positive toy closed-loop evidence, build a **thin optional** JS integration adapter behind a feature flag. Brain World default remains unchanged.

**Exit:** more goal hits on truly new target/dynamics pairs (not only shaped progress reward) and no unacceptable retention loss. Else preserve as a research-only module.

### M3 — Make mistakes cause reusable updates (P1; #114, #150, #152)

1. Store immutable attempt -> prediction -> observed error -> verifier source -> corrected attempt sequences; distinguish synaptic change, episodic retrieval and externally supplied correction.
2. Implement bounded goal/context-keyed retrieval with eviction, conflicting-feedback, stale-memory, poisoned-memory and save/restore tests.
3. Compare memory off, raw replay, uniform replay, verified-error replay, shuffled/stale retrieval, new parameter updates and frozen weights under equal bytes, compute and interactions.
4. Measure same-*type* error recurrence on semantically new tasks, improvement after one correction, delayed recall and forgetting after distractor learning. Do not call exact answer replay generalization.
5. Gate consolidation only if it adds transfer/retention; existing prioritized-replay negative runs remain the baseline.

**Exit:** fewer repeated verified failures on unseen instances, stable prior ability and auditable distinction between memory retrieval and learning new parameters.

### M4 — Learn reusable abstractions and skills (P1; #65, #110-#112)

1. Test locally learned temporal/predictive representations against frozen random features and shuffled-time controls with equal neuron/edge/compute budgets.
2. Train primitive policies on distinct source families, then hold out *new combinations* and goal relations, changed affordances and interruptions.
3. Learn (rather than hand-select) option initiation/termination from public transitions; compare engineered-option and flat controls with identical pretrain plus adaptation action counts.
4. Pre-register a compositional transfer criterion: success on generator-disjoint goals, adaptation learning curve, total acquisition cost, retention, and skill reuse with option/module interventions.
5. If a learned abstraction does not aid held-out control, delete or quarantine it. Do not expand hidden layers solely to graduate old tasks.

**Exit:** evidence for a reusable, learned (not authored) representation and greater held-out success than strongest non-oracle control.

### M5 — Learn predictive dynamics and plan (P1; #113, #115)

1. Fit action-conditioned local next-state/reward predictions from the creature's own logged transitions; explicitly prevent access to simulator dynamics or future samples.
2. Report one-step calibration, 2/4/8-step compounding rollout error and changed-rule degradation.
3. Allow 2-5-step bounded candidate simulation, with uncertainty-triggered fallbacks and independent model-call budgets.
4. Controls: reactive policy, model-free action search with equal real actions/compute, shuffled model, fixed model, oracle model upper bound and no-curiosity.
5. Test irreversible actions, deceptive predicted rewards and negative surprises; reward is scored from the *real* environment, never from the agent's imagined score.

**Exit:** improved real held-out task success after charging all planning and learning costs; otherwise retain reactive control.

### M6 — Ground multimodal representations and outputs (P2; #94, #115)

1. Use existing image/video/text/audio input and output codecs solely as transport; time-align real video frames and audio segments, retain masks and latencies.
2. Begin with **small** synthetic causal tasks requiring a joint audio+visual cue to choose a body action, then object persistence across video, and grounded text-command following.
3. Train local features/decoders under explicit per-channel budgets; compare missing/shuffled/noisy modality and single-modality controls. Prevent transcripts, metadata or cached frames from leaking the answer.
4. Outputs progress from learned discrete symbols/commands to bounded audio/text trajectories; scored media generation requires action/content produced by learned components, not re-encoding caller data.
5. Compare external ASR/LLM encoders only as clearly labeled hybrid baselines. Report whether any claimed progress survives removing them.

**Exit:** transfer of learned sensorimotor concepts across **withheld modality combinations**; no claim of open-domain language, speech or image generation from codec round-trips.

### M7 — Lifelong curriculum, social transfer and scale (P2; #116, #119)

1. Continuous task-stream without convenient resets; record re-learning, backward/forward transfer, adaptation regret, stable error recurrence, catastrophic forgetting and resource cost.
2. Test environment changes independently generated from the initial simulation, then Ecosystem private-information communication with messages on/off/shuffled and a transmission cost.
3. Add novel task families and delayed rewards only when previously demonstrated modules pass their controls. Repeat across ≥20 sealed paired seeds and a second evaluator/environment implementation where feasible.
4. Explore homeostatic regulation, structured replay, selective plasticity and network growth **one mechanism at a time**; include capacity/energy/latency scaling curves.
5. Publish reproducible release with failures, hashes, negative findings, scripts, raw brain-result/1 and fully qualified claims. Make no AGI declaration based on toy tasks.

**Exit:** evidence for sustained across-task competence in a lifelong stream, rather than a sequence of separately optimized demonstrations.

### M8 — Open-ended research directions, NOT scheduled feature promises

If M0-M7 replicate externally, evaluate object-centric causal models, long-horizon self-supervision, language grounding, social reasoning, tool use, uncertainty-aware planning and safe autonomy in new environments. These are research hypotheses requiring new public benchmarks and independent raters. Consciousness, real human connectome emulation and human-level AGI are not deliverables inferred from this roadmap.

## 5. Confirmatory protocol and promotion rules

- **Protocol unit:** matched independent seed; task repeats within seed are dependent. Development seeds 0-9 for engineering; *new sealed* seeds 301-320 for final confirmation where practical. A sealed suite is read once after a design freeze; if modified, call subsequent results exploratory and mint a new independent final suite.
- **Budget:** M1/M2 diagnostic ceiling 20,000 primitive decisions/arm/seed and 10 paired seeds; exact budget truncation mandatory. A separate **pre-registered confirmatory** program can use up to 100,000 decisions/arm/seed and 20 sealed seeds only if diagnostic learnability is established. Options exits, retry, verifier calls, lookahead, pretraining and adaptation are separately charged. These are project-design budgets, not published biological parameters.
- **Primary metric:** held-out solved goals per sampled task with frozen evaluation, including failure/timeouts. Secondary: paired transfer lift, repeated error after feedback, backward transfer, old-task retention, sample efficiency (learning-curve AUC), new edge count, memory bytes, synaptic products, total CPU time, latency, and failure-to-train fraction.
- **Decision rule (pre-registered separately for each mechanism):** aim for at least +0.10 absolute held-out success over the development-selected strongest non-oracle control, paired 95% seed-cluster CI excluding zero, and no more than -0.05 absolute loss in old-task success. This threshold is a **proposed design criterion**, not a current finding. Also show limits when multiplicity or power makes evidence inconclusive.
- **Integrity:** record code commit, runtime versions, exact CLI, dataset/split hashes, observation provenance, policy parameter and topology digests, seeds, all attempted runs, crash/timeouts, budgets and evaluation query counts. Include a counterfactual ablation table. File schema is brain-result/1 and claims live in claims.tsv. Never trim failed seeds.
- **Performance fairness:** matched observations/legal masks, environment decisions, source+adaptation budgets, opportunity to tune on development only, and disclosed computational differences. Equal decision count alone is not equal compute; show both.
- **Full stop:** abort any arm that reads hidden fields, mutates sealed checkpoints, violates safety bounds, exceeds budget, corrupts result provenance or relies on oracle decisions. Report the stop as a result.

## 6. Coding/verification commands and acceptance checklist

From a clean checkout, run:
    
    ruff check .
    python build_index.py
    python run_code_blocks.py
    python research/check_claims.py
    python -m unittest discover -s research -p 'test_*.py'
    node game/world/test_stateful_options.mjs
    node game/world/test_stateful_construct.mjs
    node game/world/test_construct_transfer.mjs
    node game/world/test_rl_multitask.mjs
    node game/world/test_continual_live.mjs
    node game/world/test_brain.mjs 1
    node game/ecosystem/test_ecosystem.mjs 1 2 3

Use the repository's actual existing test filenames; if one of the above is absent, document that fact and use its present equivalent rather than inventing a passing check. CI smoke is for regression; full science requires separately run paired experiments.

For every code PR: (a) falsifiable hypothesis and baseline; (b) minimal implementation behind an opt-in flag; (c) deterministic unit, regression and mutation tests; (d) frozen heldout + no-leakage + learning-off tests; (e) memory/compute accounting; (f) brain-result/1 with failures; (g) claims register and KB update; (h) clear merge/hold decision. One logical change per commit.

## 7. Research knowledge-base and Git-history contract

All future substantive Brain tasks must keep durable project knowledge current:
1. **Before work:** read AGENTS.md, INDEX.md, the matched topic(s), implementation-status.md, hypotheses, issue #120/#136, and the latest review ledger. Search for existing work/issue rather than create a duplicate.
2. **During research:** store source URL/DOI, published vs observed date, methods, task assumptions, exact result, uncertainty and applicability. Label statements: established neuroscience; supported primary-source model result; repo-reproduced result; independent verification pending; hypothesis; speculation; invalidated.
3. **When learning something important:** update an existing relevant topic or a dated research note; link it from research/README.md or the matched topic; record negative and null findings. Do not turn unsourced anecdotes into general facts.
4. **On change:** append a row to [agi-review-ledger.md](agi-review-ledger.md) with date, reviewed commit, reviewer attack, evidence, changed decision, and new falsification test. Preserve previous rows; revise a past mistake by adding a correction, not silently deleting history.
5. **On experiment:** retain immutable raw runs and manifests under research/results/, a brain-result/1 artifact with all failures, the source commit/tree hashes, and a reproducibility command. Update claims.tsv and implementation-status.md only when evidence actually changes.
6. **Git:** one logical change per commit; descriptive message; branch/PR tied to existing issues; no force-push that destroys reviewed history; use normal merge controls; never assert unrun tests. Git history plus the append-only ledger is the audit trail.
7. **External AI tools:** their literature summaries and self-criticism are not independent verification. Require primary-source checks and executable external tests before updating the knowledge base as established.

The [research README](README.md) links the authoritative plan; this document does not replace the existing hypothesis register or [adversarial-implementation-plan.md](adversarial-implementation-plan.md).

## 8. Source-grounded mechanism map (not guarantees)

- Local eligibility learning: Bellec et al. (2020), https://doi.org/10.1038/s41467-020-17236-y. Supports a tested spiking learning approximation, **not** an established recipe for general intelligence.
- Dynamic sparsity comparator: Evci et al. (2020), https://proceedings.mlr.press/v119/evci20a.html. RigL uses gradients; it is an external algorithmic comparison, **not** a backprop-free mechanism.
- Complementary memory systems: McClelland, McNaughton & O'Reilly (1995), https://doi.org/10.1037/0033-295X.102.3.419. Motivates fast/slow memory distinctions, not an identity between software buffers and hippocampus.
- Temporally extended options: Sutton, Precup & Singh (1999), https://doi.org/10.1016/S0004-3702(99)00052-1. Formal basis for skills, does not solve learning useful option boundaries automatically.
- Learned-model planning comparators: MuZero (2020), https://doi.org/10.1038/s41586-020-03051-4, and DreamerV3 (2025), https://doi.org/10.1038/s41586-025-08744-2. Both employ gradient-trained neural networks and cannot be quietly imported as evidence for Brain World's local learner.

## 9. First implementation handoff (ready now)

**Branch/PR target:** a narrowly scoped M0 fix; issue owners #112/#153/#154. No new learning algorithm in this PR.

- Read game/world/stateful_options.mjs and test_stateful_options.mjs; enumerate mutating fields (including RNG, per-step eligibility, actor encode buffers and option termination state). Add a test that **currently fails** when a supposedly frozen score changes subsequent deterministic training.
- Fix scoring by cloning the full model state into evaluation-specific instances (or prove complete restore). Use identical task seeds, action decisions and model digests for train/evaluate order invariance.
- Add an exact primitive-decision cap at the transition loop boundary and record both decision and environment interaction counts, including options exit and error paths; assert no overshoot.
- Add legal stepwise random and a goal-conditioned tabular control in a standalone module sharing the public observation/transition API, with no hidden target; compare against current flat/options/oracle in diagnostic (not confirmatory) runs.
- Add state-tamper, split-leak, action-mask, checkpoint and budget mutation tests. Extend existing brain-result/1 data, never invent a passing result.
- Verify relevant Node tests, result_schema.py, ruff, index, code blocks and claims. Commit code, test changes, dated result/KB entry as separate logical commits or PRs when their evidence scope differs. PR merge must be blocked if a safety/integrity test fails.

**After M0 passes:** run the M1 tabular-learnability and option-ablation protocol. Do not spend effort on natural-language generation or an elaborate brain anatomy simulator until the embodied learner demonstrably transfers on unseen tasks.

### Change history

- v1.0 / 2026-11-12: reconciled #120/#136, existing sparse and Brain World branches, current documented failures, and four adversarial rounds. Frozen first PR and promotion criteria. Further reviews append to the [review ledger](agi-review-ledger.md); any protocol change after sealed evaluation requires a new version and new sealed split.
