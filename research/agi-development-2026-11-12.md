# Brain: adversarial implementation and experiment plan (2026-11-12)

**Status:** preregistration / working plan; no claim of AGI. **Scope:** [Brain World](../game/world/README.md) and [Brain Ecosystem](../game/ecosystem/README.md). **Existing backlog:** [#120](https://github.com/faheemkhaskheli9/Brain/issues/120), [#136](https://github.com/faheemkhaskheli9/Brain/issues/136), [#153](https://github.com/faheemkhaskheli9/Brain/issues/153), [#154](https://github.com/faheemkhaskheli9/Brain/issues/154). Existing artifacts and gates take precedence over new parallel infrastructure.

## Objective and scientific constraints

Build a **single continually adapting learner** that acquires useful reusable structure from experience, survives task changes, corrects repeated errors, transfers parts/skills to novel goals and eventually plans with learned dynamics. These are operational milestones, not a definition or demonstrated achievement of AGI.

Brain World's policy/representation learning remains **backprop-free**. Conventional RL and language-model agents are independently labelled controls or interfaces. Do not count their knowledge or external decisions as creature-acquired capability. The architecture is not a literal model of hippocampus/PFC/dopamine simply because software components use those names.

Every proposed mechanism must pass the same decision rule: a preregistered prediction, a minimal implementation, explicit leakage audit, matched environment-interaction budget, ablation, paired seeds, held-out evaluation, failure rows and resource cost. The [hypotheses register](learning-algorithm-hypotheses.md), [claims register](claims.tsv), and [brain-result/1 schema](result_schema.py) own the durable scientific record; [implementation-status](implementation-status.md) owns what is actually on main. This plan does **not** replace them.

## Adversarial assessment: strongest counter-explanations

| Risk | Code/evidence | Severity | Controlled experiment / disconfirmation |
|---|---|---|---|
| **Curriculum leakage / automatic motor competence.** After stage 0, the world restores legs and narrows actions. This is **environment scaffolding**, not discovered habit. | \`World.step()\` in [brain.js](../game/world/brain.js); older source-string test in [test_brain.mjs](../game/world/test_brain.mjs) did not reject stage-derived control | P0 | Freeze the same graduated checkpoint; compare legacy vs opt-out body scaffold on exactly paired scene seeds and unchanged weights. Then retrain the unscaffolded arm with equal interaction budgets and report timeouts. |
| **Weak abstract transfer and rule reversals.** Held-out new letters, reversed tone rules and no-rehearsal retention previously failed or were weak. | [heldout.mjs](../game/world/heldout.mjs), [reversal.mjs](../game/world/reversal.mjs), [implementation-status](implementation-status.md) | P0 | Pretrain on primitives, withhold combinations, measure zero-shot and post-adaptation performance against scratch and goal-masked policy; old skill retention must survive. |
| **False novelty from a tiny authored grammar.** Counting a new drawing can amount to enumeration or class-specific shortcut. | [construct.mjs](../game/world/construct.mjs), [construct_learner.mjs](../game/world/construct_learner.mjs), #110-#112 | P0 | Hold out *combinations* and independently generated task families; exclude exact and symmetry-equivalent training solutions; report valid novelty and oracle-free action count. |
| **Unfair baselines.** Per-skill conventional RL has a different task burden from a single-network creature. | [rl.mjs](../game/world/rl.mjs), [rl_multitask.mjs](../game/world/rl_multitask.mjs), #153 | P0 | Keep the existing shared-network control (added in #170); extend it to frozen transfer/reversal/retention. Publish parameters, replay, compute and cumulative **pretraining plus adaptation** steps. |
| **Continual-learning gains are hidden rehearsal.** Removing live rehearsal hurts retained skill. | [sweep.mjs](../game/world/sweep.mjs), #152, #154 | P1 | Equal-cost uniform replay versus schema consolidation, online rehearsal, and no replay; quantify performance before and after each skill. |
| **Frozen evaluation and result contamination.** A passed seed, truncated results, evaluation tuning, checkpoint mutation or subtle RNG drift can make spurious gains. | [continual_guard.py](continual_guard.py), [result_schema.py](result_schema.py), #154 | P0 | Run synthetic mutations (missing failures, altered source data, leaking evaluation, changed checkpoints); reject altered hashes and frozen weight updates. Report all outcomes including non-graduation. |
| **Fixed, task-shaped representation.** Sparse random features do not establish learning perceptual abstractions. | \`Brain\` and \`World.sense()\` in [brain.js](../game/world/brain.js), #65, #94 | P1 | Compare locally learned predictive features to frozen random expansion, equal-size Hebbian and shuffled-time controls on unseen tasks, not just training graduation. |
| **World model/planner not demonstrated.** A withdrawn local forward-model result must remain withdrawn. | [implementation-status](implementation-status.md), #113 | P1 | Implement a local action-conditioned transition predictor and 2–5-step search; require gain over model-free and shuffled-model controls with identical online steps. |
| **Engineering priors are confused with biology.** Dopamine, replay, scene slots and gait have hand-authored choices. | [brain.js](../game/world/brain.js), [ecosystem README](../game/ecosystem/README.md) | P1 | Lesion individual mechanisms; report functional changes. Label computational analogy versus experimental neuroscience evidence. |
| **Finite seeds / adaptive benchmarking.** Tuning repeatedly on the same small held-out set converts it into development data. | [heldout.mjs](../game/world/heldout.mjs), [result schema](result_schema.py) | P0 | Keep distinct development, sealed evaluation and independent stress generators. Record hashes before running. Never change criteria after seeing sealed results. |

### Findings that should not be overclaimed

- A trained five-stage policy is evidence of **local RL in a highly designed world**, not general intelligence.
- The merged [construction pilot #174](https://github.com/faheemkhaskheli9/Brain/pull/174) demonstrates an executable policy and frozen controls; it does **not** establish compositional transfer.
- [Issue #136](https://github.com/faheemkhaskheli9/Brain/issues/136) records that a shared multi-task conventional comparator and archival transfer/retention gates **already exist**. Extend these rather than building duplicate systems.
- Prioritized replay and several architectural sweeps have negative/ambiguous measurements; do not silently promote them to defaults.
- Frozen scaffold ablation asks a narrow causal question about *dependency at evaluation*. It cannot show whether a new learner would acquire locomotion and later skills **without** the scaffold. That requires separate training arms.

## Work packages and dependencies

| Order | Task / owning backlog | Implementation deliverable | Acceptance / stop condition |
|---|---|---|---|
| 0 — validity | #120, #136, #154 | Opt-in scaffold parameter, paired frozen-world evaluator, save/load and CI smoke tests; no change in default behaviour. | Same checkpoint/scene hashes across arms; unchanged actor/predictor weights; old saves default to legacy scaffold; baseline curriculum tests remain green. |
| 1 — evidence | #153, #154 | Shared-control comparison extended to reversal + retention, versioned split manifests, source/lock/host provenance, 20-seed paired report. | No privileged task ID; every attempted run including failure/timeout retained; null effects and uncertainty published. |
| 2 — composition | #110–#112, #120 | Construction transfer runner: preregister train/development/sealed/stress grammars; pretrained vs scratch vs masked vs frozen vs legal-random vs memory lookup, plus shared RL. | See composition decision rule below. Do not count identical drawing recall as compositional transfer. |
| 3 — representation | #65, #94 | Local predictive / competitive feature learner as independent opt-in arm. | Outperforms fixed random and time-shuffled controls on novel combinations and adaptive learning under matched compute. |
| 4 — dynamics | #113, #115 | Action-conditioned, backprop-free latent transition prediction and bounded lookahead; uncertainty diagnostic. | Held-out multi-step outcome improvement over model-free and shuffled-model controls; calibrated error bars and inference cost. |
| 5 — memory/skills | #114, #150, #152 | Episodic failure retrieval and verified corrective update, schema consolidation, skill primitives. | Reduced repeat errors, stronger retention/novel transfer; no verifier/oracle leaking through observations. |
| 6 — development | #116, #95, #119 | Procedural task-family generator, persistent lifelong evaluation, optional ecosystem private-information communication. | Positive transfer across unseen families and reproducible repeated trials; otherwise publish negative result. |

### Package 0: implemented diagnostic protocol

\`new World(seed, retina, "unscaffolded")\` keeps the five-action non-board body interface even after the curriculum stage changes, and never performs the post-stage automatic gait reset. \`"curriculum"\` preserves original behavior; both modes retain the explicit pen/board action set. The opt-in setting round-trips in save v5 without breaking old v3–v5 saves.

Run cheap invariants:

\`\`\`bash
node game/world/test_scaffold.mjs
node game/world/test_brain.mjs 1
\`\`\`

Train a **legacy graduated checkpoint separately**. Compare its frozen policy on the same scene draws, for example:

\`\`\`bash
node game/world/scaffold_eval.mjs --checkpoint trained.json --out scaffold.json --episodes 100 1 2 3
python research/result_schema.py --check scaffold.json
\`\`\`

The evaluator resets the RNG before each scene; the starting state and goal are hashed in the result for each seed. It resets the evaluator from the same checkpoint per skill, leaves weights frozen and records success **and decision count**. Scene matching is a deterministic control, not a promise of identical action trajectories. The saved file **must** be a trained graduated checkpoint; no untrained control may be presented as evidence of learning. The current evaluator measures performance dependence **only**. Follow with 20 paired seeds of *from-scratch training* under both regimes; abort with a truthful negative result if budgets are exceeded.

## Primary next experiment: compositional transfer, not more brain labels

**Preregistered hypothesis H-composition-01:** Pretraining a single backprop-free policy on disjoint combinations of supplied construction primitives reduces subsequent experience required to solve unseen combinations, *without* erasing old abilities.

**Freeze before testing:** generator code hash; train/dev/eval/stress task-family predicates and their seeds; 20 paired model seeds (minimum); observation/action/reward interface; adaptation criterion (e.g. 70% success on an unseen adaptation validation set); budgets (10k pretrain, 2k adaptation environmental decisions), model capacity, hyperparameters and stop/timeout rules. Development tuning is allowed only against dev seeds. The sealed split cannot be checked during model selection.

**Arms:** pretrained goal-conditioned Brain; same-architecture scratch; goal-masked; no-update/frozen; legal random; exact-memory-only lookup; single shared conventional actor–critic comparator (backprop permitted **only** in this comparator); optional context/replay ablations. Do not equip one arm with a task-ID oracle or a privileged solution verifier. Keep the number of environment transitions, terminal feedback events and adaptation episodes visible for each arm. Report preprocessing/pretraining separately from adaptation, and wall-clock/RSS/parameter count.

**Endpoints:** frozen zero-shot success; unseen-combination success after adaptation; decisions to 70% validation success (right-censor if not achieved); pre/post old-task success, exact-and-equivalence-class novelty, failed actions, calibration and compute. Analyse paired seed differences with bootstrap 95% CIs, show individual seeds and failure rates (do not average only successful learners). Preregister effect sizes and use an independent stress generator.

**Go only if all conditions pass on sealed eval:** at least +0.10 absolute success versus goal-masked and legal random; *positive lower* 95% paired CI for pretrained minus scratch adapted success; at least 2× fewer adaptation decisions to criterion than scratch; no more than 0.03 loss on previously learned tasks; gains survive the independent stress generator, removal of goal cues removes most improvement, and leakage/shortcut controls pass. **No-go:** report that the current architecture failed to demonstrate reusable composition and prioritize package 3. Do not retune thresholds after evaluation.

## Timeline and resource gates

**Next 48 hours — validity and trust:** merge/test package 0 after reviewing default-behavior invariants; annotate all existing research claims that confuse authored scaffolds with learned skills; rerun fast integrity checks and at least the seed-1 learner; preserve unmerged experimental work separately.

**Next two weeks — decisive comparison:** extend #153/#154 into 20-seed matched shared-network reversal/transfer evaluation; run frozen paired scaffold dependence on graduated checkpoints; implement package 2 adaptation runner with pre-registered splits. Review result data before any mechanistic proposal. Failures are first-class result rows.

**Next six weeks — controlled mechanism selection:** if composition fails, isolate *locally learned predictive features* (package 3). If composition passes, start the *action-conditioned world model* (package 4) and schema replay (package 5) as separate arms. Publish direct negative results and mechanism lesions; never stack unproven interventions and attribute gains to all of them.

**Next three months — lifelong/generalization scope:** procedural families with held-out rule transformations, increasing horizons and delayed rewards; reusable options and uncertainty-aware planning; Ecosystem communication with private-information and shuffled-message controls. Evaluate lifelong learning-curve area, zero-shot transfer, re-learning savings, forgetting and useful novelty. A research release (#119) is allowed with null findings and cannot claim human-level intelligence.

### Testing / implementation gates

- Node: \`test_scaffold.mjs\`, \`test_brain.mjs\`, \`test_construct_learner.mjs\`, \`test_heldout.mjs\`, \`test_reversal.mjs\` where present, \`test_continual_live.mjs\`, \`test_rl_multitask.mjs\`.
- Python: \`ruff check .\`, \`python build_index.py\`, \`python run_code_blocks.py\`, \`python research/check_claims.py\`, \`python research/test_continual_guard.py\`, \`python research/test_result_schema.py\`.
- Regression mutations: tampered checkpoint, action-mask swap, leaked held-out label, different scene generator, removed failure row, duplicate model seeds, false frozen update.
- For a scientific run record the exact base commit, tree/working-state hash, runtime/dependency versions, generator hash, seed list, training/evaluation budgets, memory/CPU and every failed attempt. Add only **measured** claims supported by linked raw \`brain-result/1\` artifacts.
- On disagreement between the original headline metric and a valid held-out control, prefer the held-out control. Do **not** merge a positive claim until controls pass.

## Neuroscience inspirations (hypotheses, not established algorithm identities)

- Local eligibility traces interacting with dopamine are biologically observed; see [Shindou et al., 2018](https://pubmed.ncbi.nlm.nih.gov/29603470/) and [Frémaux & Gerstner, 2016](https://pubmed.ncbi.nlm.nih.gov/26834568/). A global TD error is **one model**, not the biological mechanism in full.
- Hippocampal sharp-wave ripples and replay influence memory selection ([Yang et al., 2024](https://pubmed.ncbi.nlm.nih.gov/38547293/)); this motivates a test of **structured consolidation**, not an automatic claim about FIFO transition buffers.
- [DreamerV3](https://www.nature.com/articles/s41586-025-08744-2) and [MuZero](https://www.nature.com/articles/s41586-020-03051-4) motivate controlled predictive planning experiments, but their backprop-trained neural machinery must stay outside Brain World's constrained learner.
- [Self-supervised predictive visual learning](https://www.nature.com/articles/s41467-025-61399-5) motivates checking predictive features; matching a cortical phenomenon in simulation is not proof of biological implementation.
- [DeepSeek-R1](https://www.nature.com/articles/s41586-025-09422-z) shows benefits of RL over large pretrained representations, but its prior language knowledge and scale do not transfer to Brain World for free.
- The general aim is a falsifiable search for *which minimal mechanisms yield reusable structure*, not a claim to have reconstructed human cognition.
