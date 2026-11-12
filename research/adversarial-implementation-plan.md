# Brain: adversarial implementation plan and evidence gates (2026-11-12)

This is the **execution specification**, not a new roadmap or claim of intelligence.
Work through the existing [roadmap #120](https://github.com/faheemkhaskheli9/Brain/issues/120)
and [ordered backlog #136](https://github.com/faheemkhaskheli9/Brain/issues/136).
Do not reopen completed infrastructure work. Keep the backprop-free Brain World
learner separate from conventional-RL and LLM-agent comparators. Preserve
`brain-result/1`, the claims register, and frozen evaluation splits.

## Target and non-goals

**Target:** a single learned policy that uses past mistakes and learned skills to
complete genuinely unseen compositions, while retaining previously learned tasks.
After that, test short-horizon model-based planning and useful novelty.

**Not evidence of the target:** graduating the familiar curriculum; a fixed gait
reflex; a hard-coded action/goal grammar; retrieving an exact answer; a search
algorithm with an engineered validator; a conventional backprop or LLM system
solving the task on the creature's behalf.

**Constraints:** JS for Brain World/Ecosystem, Python/NumPy for experiments, no
new heavy dependencies, deterministic seeds, bounded work, no model access to
hidden target labels or reward rules, no tuning on a frozen held-out split.

## 0. Repair the reliability of the measurements (P0; #111, #153, #154)

1. **Novelty benchmark fairness (#111).** Preserve the October/November legacy
   artifact as *historical, not a fair comparison*. Its random arm generates
   illegal stroke indices and duplicates; its engineered search consults a graded
   constraint penalty outside the charged validator budget. Introduce a separate
   benchmark with valid-stroke random, unmodified retrieval, blind mutation,
   binary-feedback mutation and a **clearly labelled privileged graded-feedback**
   upper bound. Same seed, task instances, candidate count, and eight verifier
   calls/task. Report graded-feedback calls separately; compare blind mutation to
   feedback mutation to isolate the value of feedback. Count all calls inside
   the candidate-generation loop and fail if the allowance is exceeded.
2. **RL comparator (#153).** Run matched total environment steps and action masks,
   with a reasonably tuned shared recurrent/working-memory comparator and
   appropriate context-aware conventional baseline; report all tuning trials,
   network size, optimizer bytes, inference compute and wall clock. Existing
   five-seed 64-unit shared run is a **single weak baseline**, not a general verdict
   on backprop. Never select hyperparameters on the frozen eval split.
3. **Research gates (#154).** Keep cheap deterministic CI smoke tests separate
   from full multi-seed science. Any learning-mechanism PR must report source-skill
   retention, reversed-rule adaptation, held-out glyph/composition success, failure
   counts and costs **before and after**, with immutable raw runs.

**Gate:** a matched-control benchmark can detect validity/novelty exploitation,
all attempts are recorded, reruns reproduce deterministic scores, and CI cannot
silently accept changed saved checkpoints.

## 1. Learn a reusable skill/composition representation (P0; #110, #112)

- Extend `construct.mjs` only as needed for a **learned** policy to observe a
  goal and output an action sequence. Explicitly tag supplied primitives, goal
  encoder, reward, oracle and any teacher demonstration.
- Implement initiation, termination, failure and parameter binding for reusable
  approach/grasp/carry/place and draw-stroke skills; start with one minimal
  2–3-step goal, not every possible behavior.
- Compare: random legal policy, hard-coded task solver (separate oracle upper
  bound), flat backprop-free policy, learned option library with options disabled,
  and scratch/no-pretrain matched to both *adaptation-only* and *total*
  experience. Also compare retrieval-only with a shuffled solution store.
- Freeze **combinations** and goals absent from training, not only input order.
  Add changed affordances, distractions, interruption/retry, and impossible goals.

**Preregister for the first mechanism experiment:** 10 matched seeds (1–10);
train/dev/eval family-disjoint; at most 20,000 learner episodes per skill and
2,000 adaptation episodes per unseen task; same eval episodes and validator
queries. Primary metric: **novel held-out task success after 2,000 episodes**,
with frozen zero-shot as a separate metric. Secondary: attempts, old-task
retention, repeated errors, memory bytes, operations, wall clock. Require at
least **+0.10 absolute success** versus the strongest budget-matched non-oracle
control, a paired 95% interval excluding zero, and **no more than -0.05**
loss on prior skills. A CI smoke test cannot substitute for this run. Do not
retune to meet the criterion.

**Gate:** retain or reject the option mechanism based on held-out evidence;
failed seeds count as failures. No claim of creativity follows merely from
compositional-task validity.

## 2. Correct mistakes and consolidate memory (P1; #150, #114, #152, #106)

- Store a bounded **verified outcome** record: context/goal, action or skill,
  predicted result, observed result, validity source, revision, schema version.
  Distinguish a failed attempt from a verified corrective experience.
- Retrieve by goal and contextual features; compare scoped retrieval, memory
  disabled, randomized retrieval, stale feedback, contradictory feedback, exact
  repeats and semantically novel cases with equal memory/cost budgets.
- Use confidence/surprise to choose when to retrieve, revise, retry or abstain,
  never to read the hidden correct action. Prevent memory from learning eval
  answers. Test ring eviction, overwrite, save/load and corrupt-input recovery.
- Track **same error repeated after corrective experience** and backward transfer,
  not just reward or memory hit rate. Keep negative replay-sampler results.

**Gate:** fewer repeated errors on a held-out rule family with stable old-skill
retention. A correction stored externally is retrieval, not parameter learning.

## 3. Model-based planning and uncertainty (P1; #113, #115)

- Train a compact next-observation/reward model on the learner's own transitions,
  with no access to simulator state or the hidden target.
- Evaluate one-step calibration, 2/4/8-step rollout error, changed dynamics,
  exploratory surprise, and whether the resulting plans actually improve
  decisions. Include model-free search at equal **environment and model-call**
  budgets and an *explicit oracle-model* upper bound.
- Bound depth, number of expansions, compute and fallback behavior on uncertain
  predictions. Ablate curiosity, search, reward prediction and model updates.

**Gate:** improve unseen long-horizon goal success per environment interaction,
without disproportionate simulated-rollout cost or old-skill regression.

## 4. Useful novelty and creative generalization (P1; #111, #110, #112)

- Move beyond the 63 nonempty combinations of the six-stroke toy.
  Hold out new primitives, spatial relations and functional goals, while keeping
  a tiny enumerated benchmark as a validator regression suite.
- Score **valid + task-relevant + distinct** solutions; measure coverage and
  solution diversity against random-valid, retrieving old solutions, blind
  mutation, binary-feedback search and a clearly privileged engineered oracle.
- Evaluate unseen instructions and environment rearrangements, not only
  symmetry variants. Test noise/reordering/mirroring/degenerate outputs.
  Audit all search, judge, retrieval and verifier calls; distinguish a
  learned creator from a supplied search routine.

**Gate:** a learned creature generates useful held-out solutions above a valid
random and equal-budget non-learning search; gains survive increased task-space
size and independent seed splits.

## 5. Ecosystem, independent replication and communication (P2; #116, #95, #94)

- Change resources and social conditions after training; measure collective
  utility, individual survival, congestion, message latency and stale-message
  harm, with communication on/off/shuffled and matched opportunity cost.
- Benchmark morphology/vision modifications with *matched learning-rate,
  observation/parameter count and steps*; do not credit step-size confounders
  as visual-feature discoveries. Include at least one genuinely new environment.
- Rerun the strongest mechanism independently with fixed frozen tests, separate
  author review, and negative results.

**Gate:** credible transfer and retention in both Brain World and at least one
changed ecosystem task; no biological inference from game simulation alone.

## 6. LLM/agent mistake-learning track (separate; #149, #156, #151, #155)

- Run an actual model with external executable feedback, not only toy fixtures.
  Same model/version, temperature, token/retry/tool budget across no-memory,
  reflection, verified memory, stale/shuffled memory, reviewed skills/RAG and
  optional offline fine-tuning/adapter arms.
- Exclude near-duplicates and goal templates from train/eval across sessions;
  test whether improvements persist with memory physically removed.
- Log verified accuracy, repeated errors, tool correctness, hallucination,
  tokens, latency, storage, weight/version provenance and cost. Do not self-certify
  corrections or auto-escalate tool permissions.
- Keep LLMs as interfaces or separate baselines, never relabel external
  generation as a backprop-free creature's learned intelligence.

## Research protocol for every change

1. Register **question, falsifier, fixed split, seeds, baseline, tuning budget,
   acceptance threshold, stops, compute and memory** before confirmatory runs.
2. Run cheap deterministic unit/mutation/smoke checks; record protocol and
   code SHA. Then run the preregistered full experiment once.
3. Save *every* seed/arm, including timeouts, via `brain-result/1`; compare
   paired estimates with bootstrap intervals and an explicit effect size.
4. Investigate leakage, engineered shortcuts, evaluation tuning, cost mismatch,
   lucky seeds, weak baselines and prior-skill forgetting.
5. Promote only verified claims to `research/claims.tsv` and reports; retain
   negative findings and the old frozen checkpoints.

Applicable checks:
`ruff check .`, `python build_index.py`,
`python run_code_blocks.py`, `python research/check_claims.py`,
`node game/world/test_brain.mjs 1`, relevant world/benchmark tests,
`node game/ecosystem/test_ecosystem.mjs 1 2 3`,
and `node game/test_browser.mjs`.

## Adversarial review of this implementation plan

| Attack / failure mode | Why the plan could still fail | Mitigation and stop condition |
|---|---|---|
| Tiny task grammar encodes solutions | Six strokes admit exhaustive search | Keep tiny suite for software tests only; freeze larger, held-out compositional families before scientific claims |
| Privileged feedback masquerades as intelligence | Graded penalty is equivalent to a designed solver hint | Count feedback separately; isolate binary-verifier learning from graded-feedback oracle |
| Pretraining budget mismatch | Learning skills before evaluation gives free experience | Report both total and incremental budgets; enforce budget-matched controls |
| Invalid random baseline | Random fails through malformed actions, inflating search advantage | Sample legal unique stroke sets within stated budget |
| Curriculum or gait supplies the answer | Designed gating and reflexes drive success | Report supplied representation/action grammar and include ablations |
| Leaked held-out answers | Solution memory stores an eval equivalent | Split by goal family and semantic equivalence; hash/check memory provenance |
| A tuned baseline is intentionally weak | A single 64-unit model cannot rebut backprop | Tune each comparator on development tasks, report tuning cost, reserve eval |
| Simulator-specific tricks | A fixed reward or map structure is exploited | Shift environments, rewards and layouts, and compare task families |
| Multiple-hypothesis selection | Many tweaks eventually find a lucky seed | Preregister one primary metric/criterion and archive negative runs |
| Forgetting hidden by new-task success | Improvement overwrites earlier skills | Pair source-skill retention with every improvement claim |
| Expensive planning appears sample-efficient | Model rollouts are uncharged | Count simulated steps, wall time, compute and real interactions |
| Corrective memory becomes stale or malicious | Retrieved hints worsen policy | Test conflicting/stale data, provenance, expiry and abstention |
| CI is green but science regresses | Smoke tests are not statistical evidence | Keep frozen CI gates AND full multi-seed evidence; require actual status check on main (#164) |
| Project scope explodes | Architecture grows before a falsifiable gain | Do not start the next mechanism until the previous gate is measured or explicitly rejected |

## Implementation state

- **Already implemented:** world/environment interfaces, episodic replay, held-out
  and reversal suites, baseline runners, construction task generator, engineered
  novelty search, result schema/dashboard, CI tests and claims tracking.
- **First code change in this plan:** a new fairness-controlled novelty benchmark
  and regression tests; keep the legacy artifact for audit, but do not compare its
  invalid-random baseline as if search had matched information.
- **Now prototyped (pilot, not confirmed):** a goal-conditioned backprop-free
  construction policy using the existing Brain actor/critic, with goal-mask,
  learning-off and valid-random controls plus frozen held-out evaluation (#112).
  No measured advantage is claimed; no transferable option/skill hierarchy yet.
- **Not yet implemented:** learned reusable skill compositions by the creature,
  generalizing error memory, learned world-model planning, real-LLM benchmark or
  independent replication. These remain under existing issues.

Update this state only after code and results are verified, not from an issue
closure or a proposed design.

## Next execution batch: falsify the construction pilot before adding options (2026-11-12)

**Reason for this batch:** #173 delivered a fairer *engineered* novelty evaluator and #174 delivered a backprop-free construction **pilot**, but neither has a recorded confirmatory multi-seed transfer advantage. This batch narrows the existing #110–#112 work; it does not create a parallel roadmap. Preserve the frozen split, existing negative results and prior research gates.

### A. P0 — audit measurements and publish the pilot baseline (#111, #112, #154)

1. **Legal-action parity:** In `construct_learner.mjs`, the policy can choose the same pen stroke twice, while `random-valid` samples unique strokes. Add two controls: raw/unmasked random and syntactically masked learner/random. Distinguish this from a forbidden *goal-aware* action mask; it may exclude already-used strokes but may not reveal which stroke satisfies a goal. Record illegal-action frequency, chosen actions and decision cost.
2. **Frozen means no adaptation or evaluation-order effects:** `frozenScore` currently hashes `P` and `v`, but `Brain.act` consumes RNG even when `learning=false`. Verify whether train-set scoring changes the later test result. Evaluate from identical copied checkpoints and isolated deterministic evaluation RNG streams; test reversed evaluation order, no weight/state updates, and sampled-policy versus greedy-policy performance. Do not count a passed weight hash as proof of fully isolated evaluation.
3. **Novelty opportunity ceiling:** The six-stroke toy admits only 63 nonempty subsets. The pilot builds the known set by enumerating *every* valid train-task solution, not just observed experience. Calculate per-task reachable novel classes and report conditional novelty among tasks with at least one novel valid solution, alongside the unconditional score. Keep the strict historical metric, but do not equate it with useful open-ended creativity.
4. **Complete the missing artifact:** run `novelty_fair.mjs` on preregistered seeds 1–10, 30 eval tasks/seed, eight verifier calls/task and all five existing arms. Save candidate audits and a validated `brain-result/1` artifact. Compare legal random, retrieval, blind mutation, binary feedback and *separately priced privileged graded feedback*. Do not recycle the legacy 0.49 versus 0.27 claim.
5. **Pilot comparison:** run `construct_learner.mjs` on seeds 1–10 with 10,000 training decisions, 64 training tasks, 30 frozen eval tasks and five evaluation attempts per task. Include goal-conditioned, goal-masked, learning-off, legal random and raw random; add legal-mask parity arms only after a dev-only, declared amendment. Record every run and failure, total and adaptation-only experience, training and test success, infeasible/invalid action frequency, old-task retention, bytes, calls and wall time. Treat this as a **diagnostic** protocol, not a post-hoc winner selection.

**Gate A:** All arms use comparable action/feedback budgets or are clearly labeled unequal. Frozen test results do not depend on scoring order; results and costs are reproducible, integrity-checked and archived. If the learned policy cannot beat a legal nonlearning control, diagnose representation/credit assignment **before** introducing more mechanisms.

### B. P0 — make composition require real temporal dependencies (#110, #112)

The current drawing validator tests an unordered subset of up to six supplied strokes; its task is not evidence of multi-step skill execution. Retain it as a unit-level construction benchmark, then introduce **one** tiny stateful environment: acquire object → carry past an obstacle → place at a requested destination, with possible failed pickup, drop and retry. Each action changes the next observation and has observable consequences. Do not expose the simulator's hidden state, task identifier, oracle route or solution enumeration to the learner.

Freeze train, development and evaluation families *before* training. Hold out destination/obstacle combinations and perturb one transition rule. Include impossible goals, distractors and interrupted episodes. Supply an engineered oracle **only** as a labeled feasibility ceiling. Add tests for episode-state transitions, mask legality, reward provenance, evaluator independence and impossible-goal handling.

**Gate B:** A flat backprop-free policy and valid nonlearning baselines can be run on the same environment and fail/succeed for observable reasons. If the task is solved by one fixed action macro independent of observation, redesign it rather than presenting macro execution as intelligence.

### C. P1 — learn and test one reusable option hierarchy (#112)

Implement *one* minimal option with an initiation condition, a learned intra-option policy and a termination decision. The manager selects options using only available observations and goals; interrupted/failed execution must return control for recovery. Distinguish designed primitive actions, designed option interfaces, learned option parameters and optional hand-scripted upper bounds. Use the existing three-factor learner; backprop and LLM baselines remain separate.

Pre-register 10 paired seeds (1–10), train/dev/frozen-test splits and an equal primitive-decision **total** training budget. Compare flat trained policy, option-enabled policy, option-disabled ablation, fixed-script macro, shuffled option/termination, scratch learning and a task-specific oracle ceiling. Report zero-shot and up-to-2,000-decision adaptation separately, plus source-task retention, repeated failure, valid goal completion, compute, and training history. Match the tuning allowance on **development data**, not test. Use a paired 95% interval and the pre-existing decision rule: at least +0.10 absolute held-out success over the strongest non-oracle, budget-matched arm, interval excluding zero, and no more than -0.05 loss on source skills.

**Gate C:** Keep the mechanism only if it meets the frozen evaluation rule without a disproportionate compute/cost increase. Otherwise save a negative result and audit the failed seed/task families before trying #150's corrective memory or #113's planner.

### Adversarial review: code-level attacks to test in this batch

| Priority | Potential failure | Evidence / adversarial test |
|---|---|---|
| P0 | **Unequal legal action spaces** favor the random-valid baseline or hide how often the learner wastes strokes. | `playEpisode` accepts any action in `ALLOWED`, including a prior stroke; `randomLegal` samples a set without repetitions. Compare unmasked/masked versions of **both** arms. |
| P0 | **Evaluation RNG contamination** produces a lucky or order-dependent held-out score. | `Brain.act` samples `this.rand()` with learning disabled, while `frozenScore` checks only weight arrays; restore matched RNG and state for each eval arm and reverse scoring order. |
| P0 | **Artificial novelty ceiling** causes apparent creativity or failure for the wrong reason. | `construct.mjs` has 2^6-1 candidates; `runSeed` excludes all enumerated train solutions. Report feasible novel classes and a nontrivial larger task before any creativity claim. |
| P0 | **Unordered subset mistaken for learned option composition.** | The current validator ignores stroke order; require stateful dependent actions and interruption handling before accepting #112 as a reusable-skill result. |
| P1 | **Training/test family leakage** hides in task-template variants. | Test semantic-equivalence groups and duplicate solution classes, and validate that a changed rule or new affordance is truly absent from training. |
| P1 | **Unequal adaptation and verifier information** inflate gains. | Match primitive steps, total pretraining, repeat attempts, validator queries and memory. Keep privileged graded feedback as an explicitly unequal-information upper bound. |
| P1 | **Winner selection and weak comparator** overstate significance. | Declare the primary effect before confirmation, publish all seeds including failures, and retain legal random, flat, fixed macro and tuned development-only comparators. |
| P1 | **Positive new-skill metric masks forgetting.** | Score old skills before and after, and run the existing held-out/reversal guards before promoting any learned-option claim. |

### Delivery order, checks and stop conditions

- **PR 1 (measurement repair):** evaluation-state and legal-action controls, stronger tests, fair-novelty full artifact, diagnostic construction pilot report. No new learning architecture.
- **PR 2 (stateful task):** minimal dependent-action environment, split generator, independent verifier, oracle upper bound, frozen tests and baseline runner.
- **PR 3 (learned option):** one learned option plus ablations, ten-seed confirmatory artifact and honest negative/positive claim update.
- Defer #113–#115 and #150 until Gate C is measured or rejected; #164 remains an independent repository-governance requirement.
- For code PRs, run the applicable JS tests, `ruff check .`, `python build_index.py`, `python run_code_blocks.py`, `python research/check_claims.py` and CI's integration suites. If local execution is unavailable, report tests as **not run**; do not substitute a green smoke check for scientific evidence.
- Reference foundations: Sutton, Precup & Singh, *Artificial Intelligence* (1999), DOI 10.1016/S0004-3702(99)00052-1 (options); Bacon, Harb & Precup, AAAI (2017), DOI 10.1609/aaai.v31i1.10916 (learned termination). These are methods to test, not proof that the Brain implementation works.

**Status on 2026-11-12:** plan and adversarial review only; Gates A–C are *not* implemented or satisfied.
