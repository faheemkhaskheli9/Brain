# Brain adversarial plan review ledger (append-only)

Date opened: 2026-11-12. Linked plan: [AGI execution blueprint](agi-execution-blueprint-2026-11-12.md).
This ledger preserves review decisions and corrections. It is an engineering/scientific audit, not an account of independently run experiments. Future entries must include exact source commit, change, rationale, adversarial counterexample and verification status. Keep old entries visible; Git adds chronological provenance.

## Round 0 — inventory and claim separation (2026-11-12)
Reviewed baseline: main at 49e2c6f1; checked AGENTS.md, INDEX.md, #120/#136, implementation-status.md, current adversarial and sparse-brain plans, Brain World stateful options, research sensorimotor bridge, sparse reaching, source docs and primary literature.
- Challenge: the project has multiple sophisticated components but **no integrated general learner**; a 78-region structural graph and media encoders could falsely be presented as a working brain.
- Evidence: structural-connectome.md explicitly says weights start unassigned; sensorimotor_bridge.py requires external motor activation; audio-io.md/multimodal-io.md describe caller-supplied codecs.
- Resolution: explicitly split architectural interfaces, local learned control, agent/tool baselines and speculative future capabilities. Document input/output and checkpoint contracts, M0-to-M8 dependencies.
- Verification: source audit only; no algorithmic run made in this review. Re-check live main before each code PR.

## Round 1 — scientific adversary: 'Are we measuring intelligence or scaffolding?'
- Attack A: current creature's prior curriculum automates parts of body control; a success can be a fixed gait or authored feature. A constructed goal can be solved by an invariant macro script or an oracle that uses simulator transitions.
- Attack B: pretraining, memory lookup and two engineered option banks can look like transfer/learning even when no new reusable policy is acquired.
- Attack C: reward increases in delayed-feedback body experiments need not correspond to goal-contact increases; a positive mean can coexist with worse retention.
- Correction: primary endpoints use **actual held-out goal success** and old-skill retention; count trained weights vs retrieval vs externally supplied knowledge; test unscaffolded evaluation, fixed macros, observable-only state, goal masks and independent task generators. Require real errors to be corrected under frozen tests.
- Rejection test: if a no-observation script, oracle-assisted verifier, lookup-only, or stage-specific body rule explains the effect, withdraw the intelligence/transfer interpretation.

## Round 2 — experimental adversary: 'Could the effect be data leakage or a weak control?'
- Attack A: frozen evaluation can change RNG, temporary activations, eligibility or policy state even when weight hashes stay identical.
- Attack B: counting episodes instead of primitive actions masks longer option searches; hardcoded search may use free verifier calls.
- Attack C: a five-seed weak multi-task RL implementation or a legal random that does not interact with the environment is not a meaningful comparator.
- Attack D: repeated tuning on the same sealed 'held-out' task set turns it into development data; nested task repeats are not independent seed pairs.
- Correction: M0 first; full clone tests; one precise decision cap; budget wall time, model calls and verifier; legal stepwise random, small-state tabular learning, tuned shared RL; independent development and genuinely new sealed seeds/generators; seed-paired uncertainty and documented power limits.
- Rejection test: perturb each leak, checkpoint or budget invariant; fail CI on mutation. After any sealed feedback used for tuning, mint a new sealed suite and call the previous result exploratory.

## Round 3 — architectural adversary: 'Can the proposed brain learn without a hidden shortcut?'
- Attack A: a scalar/signed-insensitive sparse router loses spatial/time information needed for image, sound, text and video, so many 'multimodal' successes would be codec demonstrations.
- Attack B: candidate growth could scan every possible dense edge off the books and claim sparse efficiency; global hidden-label rewards could be mistaken for local plasticity.
- Attack C: a bank of pretrained checkpoint controllers plus reward switch is retrieval, not online discovery and re-learning under a continuous body.
- Attack D: a learned world model can be exploited for high imagined reward while making real actions worse.
- Correction: typed signed/time-preserving population contracts; full operation accounting; explicit provenance; separate closed-loop one-body test with post-action feedback; freeze model-call budgets; compare live environment outcomes and planning-off controls.
- Rejection test: shuffled modality/time, no sensory channels, fixed controls, motor reversal, model-shuffled planning, and growing candidate-budget profiling must eliminate unexplained success.

## Round 4 — project and safety adversary: 'Will this produce evidence or an endless AGI feature backlog?'
- Attack A: adding memory, curiosity, connectivity, media and language at once cannot attribute causality, and 10-seed toy gains can disappear in new environments.
- Attack B: architecture may become dependent on pre-trained LLM assistance while still being advertised as from-scratch learning.
- Attack C: no cost/stop rule can burn compute while returning impressive demos and little durable information.
- Attack D: research claims, citations and negative results can be lost between chats or replaced by unverified paraphrases.
- Correction: gated one-mechanism PRs, no AGI guarantee, opt-in flags, matched cumulative budgets, explicit non-goals, provenance, independent evaluation, claim-to-result linkage, immutable run artifacts, append-only ledger and required KB maintenance in AGENTS.md.
- Rejection test: no mechanism promoted without independent held-out benefit and valid integrity gates; when evidence is null, preserve the negative and pivot to a smaller falsifiable hypothesis.

## Final adversarial verdict (2026-11-12)

**Ready for implementation:** M0 evaluation/measurement repairs. **Not yet validated:** M1-M8. The program is research-ready, not AGI-ready. The dominant early uncertainty is whether the local learner can discover transferable action structure under fair stateful tasks. The next code PR must address frozen-state equivalence and fair budget/controls; this review made no experimental performance claim.


## Round 5 — implementation adversary: a budget that is not actually bounded (2026-11-12)

- Baseline: main 49e2c6f1; PR #194 eefd33e3, unmerged. Inspected stateful_options.mjs, stateful_construct.mjs, brain.js, tests; no test run or code change.
- Attack: trainPhase can overshoot its declared training decision cap because it scores an entire episode then increments decisions. The BFS oracle claims success without taking the same actual environment actions; EXIT is a decision but not a transition.
- Decision: split M0 into M0a–M0d. Enforce exact remaining-budget caps inside episode; classify oracle as privileged ceiling; report decisions, transitions and all optional calls separately.
- Falsification: budgets 1/39/80/81/137, EXIT bursts, timeouts, failure paths and replay must never overshoot. Until tested, this is a code-backed risk, not a verified regression fix.
- Claim status: source-observed behavior and proposed correction; untested.

## Round 6 — representation adversary: can source state survive an evaluation exactly?

- Baseline: same. Model digest hashes selected arrays, frozenEpisode explicitly restores a subset, whereas Brain has nested syn, RNG closure and further state. World.toJSON intentionally resumes by replay.
- Attack: a previously passed weight-only freeze assertion might miss a future change in synaptic importance, RNG, surprise, hidden eligibility or learned features. A shallow clone would alias typed-array memory.
- Decision: add complete-state inventory and isolated actor snapshot protocol; do not reuse arbitrary World save as a mid-episode snapshot. Inspect the next training action trace, not just the immediate weight hash.
- Falsification: train/eval/train equals train/train in full state and future action trace, across greedy/stochastic/surprise/SI cases; intentional alias mutation is detected.
- Claim status: potential evaluation integrity risk, not an observed changed training trace; untested.

## Round 7 — generalization adversary: a new seed is not a new environment

- Baseline: same. Four item-goal relations × four obstacle templates per split, fixed start and horizon; there are at most 16 structural patterns/split.
- Attack: random new IDs and seeds produce repeated task structures; a significant 20-seed improvement can still be overfitting to tiny same-family layouts. A full-map baseline would be privileged over observe().
- Decision: retain tiny split as regression, add nonisomorphic structural generators, history-aware controls, family-level split fingerprint, and family-stratified independent confirmation. Strongest tuned non-oracle control fixed before sealed scoring; retention must pass confidence-bound non-inferiority, not only a point estimate.
- Falsification: unseen families, new starts/obstacles/interruptions, masked-sensor tests and independent evaluator should preserve the claimed benefit. Otherwise remove the transfer/generalization interpretation.
- Claim status: source-backed narrow task breadth; proposed new evaluation untested.

## Round 8 — scientific governance adversary: does the roadmap permit a false AGI declaration?

- Baseline: v1.0 and this inspection; primary options formalism checked against Sutton et al. 1999; ARC-AGI-2 primary benchmark documentation checked for independent evaluation practice.
- Attack: a single shaped reward or tiny controlled benchmark can be promoted as AGI; new knowledge can be filed as established without a run; document edits could erase earlier failed decisions.
- Decision: publish v1.1 **as a new file** leaving v1.0 and all old ledger entries in place. Link a separate source-grounded knowledge note; gate M1 on M0 and prohibit model/AGI claims without independent replication. Add capture rules to AGENTS.md.
- Falsification: any missing failure, changed sealed suite, hidden oracle, unverified source or erased negative invalidates promotion; create a new version rather than rewriting history.
- Claim status: implementation-ready M0 specification; no experiment, AGI outcome or independent validation claim.

## Entry template for subsequent reviews (append; do not overwrite)

- Date and baseline commit:
- Hypothesis/feature and owning issue:
- Sources checked (DOI/URL; primary vs secondary):
- Strongest falsification attack:
- Existing and new baselines:
- Change in decision and its cost:
- Tests run, failed/skipped and raw result links:
- Claim status (confirmed / weakened / refuted / inconclusive / untested):
- Next minimal experiment:

## Round 9 — isolated-evaluation intervention (2026-11-12)

- Baseline main `49e2c6f1`, preceding v1.1 `b74396f6`. [PR #195](https://github.com/faheemkhaskheli9/Brain/pull/195): code `98544659` and source-grounded KB note `0be775b6`.
- Attack: frozen scoring temporarily used the live learner and restored selected fields; future new state could bypass a parameter-only digest. RNG closures also cannot be deep-cloned as ordinary data.
- Change: evaluate on an independently seeded deep copy of every owned Brain field, preserving methods but not data aliases. Fail closed for unknown noncloneable fields; test training before/after scoring, greedy performance and invalid tasks.
- Verification: PR #195 CI and separate 10-seed stateful option workflow **passed**. They test integrity and historical pilot behavior, not new learning or AGI.
- Counterattack: global/module state, task-object side effects, arbitrary mid-episode RNG restoration and independent test-generator leakage remain open.

## Round 10 — exact interaction budget intervention (2026-11-12)

- [PR #196](https://github.com/faheemkhaskheli9/Brain/pull/196), stacked on #195: code `aab50b1d`, KB `c44cd932`; both full CI and 10-seed stateful option workflow **passed**.
- Attack: trainPhase's whole episodes could overshoot the declared budget, with EXIT counted as a decision but not a physical action. Requested steps were not necessarily actual steps.
- Change: cap exact primitive decisions, use remaining allowance in every trainPhase episode, reject cap errors, record truncated episodes and distinguish experiment cutoff from natural timeout.
- Counterattack: the cutoff's TD bootstrap and partial-episode schedule can still change outcomes; compare boundary policies on development tasks and disclose truncation fraction. No performance advantage claimed.
- Next: M0c fair public-observation controls and genuinely different structural task families. Do not reuse historical budget-confounded rows as confirmatory evidence.

## Round 11 — external benchmark skepticism (2026-11-12)

- Sources: [ARC Prize ARC-AGI-3 competition](https://arcprize.org/competitions/2026/arc-agi-3) and [official testing policy](https://arcprize.org/policy), contrasted with independent [Epoch AI ARC-AGI-3 review](https://epoch.ai/benchmarks/arc-agi-3/review) (review date 2026-10-30; verdict **Flawed**).
- Attack: high scores on a named AGI benchmark could mask differences in action-efficiency incentives, harness elicitation, versioning or evaluation setup. A publicly available test manifest is not secret from an agent that can read it.
- Decision: ARC-AGI-3 is a useful **optional interactive generalization stress test**, not the sole AGI gate. Report real completion separately from action efficiency, harness/version, learning interactions, planning calls, hidden information and test contamination. Independent benchmark critique is an external report, not a result reproduced by Brain.
- Falsification: claimed transfer must survive a second unexposed task generator and matched evaluation protocol. [Execution addendum](agi-execution-addendum-2026-11-12.md) contains the M0c implementation sequence.

## Round 12 — can a 'strict' science gate still pass over-budget trials? (2026-11-12)

- Baseline: M0b [PR #196](https://github.com/faheemkhaskheli9/Brain/pull/196), before analyzer commits `01c95ff2` and `bda1db3d`; historical `research/analyze_stateful_options.py` accepted `limit <= spent < limit + 81`.
- Attack: even after an exact-limit implementation, its science checker could have accepted an 80-decision overrun and declared the run comparable. A source-model fix without validating the downstream verifier is insufficient.
- Decision: identify versioned protocols in the result metadata. Explicit `trainingOvershoot: "none (exact cap)"` requires `spent == requested`; historical missing/episode-boundary metadata may still be analysed for reproducibility but is labelled `legacy-overshoot` and cannot produce a new confirmatory pass.
- Synthetic counterexamples: one extra training decision, malformed string count, unknown protocol, and an apparently high-performing legacy run must be rejected or receive a nonconfirmatory verdict. Check both status and actual per-run spent counts.
- Verification at entry: code/test commits pushed; updated GitHub Actions checks for `bda1db3d` in progress. Earlier M0b code `c44cd932` had passed CI and 10-seed workflows; **do not conflate that earlier pass with this later gate change**.
- Claim status: method-level bug found by source inspection, corrective test patch awaiting CI. No result establishes AGI, transfer or memory performance.

## Round 13 — failed learning gate after fixing measurement integrity (2026-11-12)

- Baseline: actual GitHub Actions run [43250847229](https://github.com/faheemkhaskheli9/Brain/actions/runs/43250847229), head `bda1db3d8dbeac4167be6f69c3310d0e0decf19a`, Node 22.23.4, PR [#196](https://github.com/faheemkhaskheli9/Brain/pull/196). The 10-seed workflow and CI completed successfully; test success **is not** hypothesis success.
- Attack: a code-only improvement could be falsely called transfer if the stronger benchmark produces zero goal completions but reduced invalid actions or apparently positive shaped reward. The archived pilot includes four-goal-pair/obstacle templates and an engineered manager, so generalization claims also risk template confounding.
- New reproducible evidence: 70 arm×seed `brain-result/1` rows, all executable runs `status=ok`; exactly 10,000 training and 2,000 adaptation decisions for each learned arm. All six non-oracle policies had **0.000 mean frozen held-out goal completion**. Privileged BFS feasibility oracle 1.000, explicitly not a comparable policy. `options-flat` paired delta 0.000 (95% CI [0,0], p=1), source-retention delta −0.003125 (CI [−0.009375,0]). Preregistered advancement gate **FAIL**.
- Full source-grounded [negative report](https://github.com/faheemkhaskheli9/Brain/blob/fix/options-exact-decision-budget-20261112/research/stateful-options-exact-negative-2026-11-12.md) and lossless [raw archive](https://github.com/faheemkhaskheli9/Brain/blob/fix/options-exact-decision-budget-20261112/research/results/stateful-options-exact-2026-11-12.tar.br), archive Git blob `6405e123e2cba7d46077656ec587a0c075ff1d69`, are permanently committed on the code branch. The original CI artifact is also linked in that note; Git is the durable copy.
- Decision: **HOLD** M1–M8 capability promotions. M0c begins by testing basic task learnability using an observation-parity tabular/history policy and legal stepwise heuristic under exact budgets. If no public-observation control learns, fix task observability, reward and horizon before attempting a more elaborate neural architecture. Then introduce independent structural families and stronger RL baselines.
- Evidence status: repo-reproduced negative result for this toy protocol; no proof that brain-inspired learning is impossible generally, nor that engineered options can transfer. These are scientific failure findings, not permission to tune against the frozen test.

## Round 14 — failed option policy is trapped by a non-switching EXIT (2026-11-12)

- Baseline: [exact-budget raw experiment](https://github.com/faheemkhaskheli9/Brain/blob/fix/options-exact-decision-budget-20261112/research/results/stateful-options-exact-2026-11-12.tar.br) and [negative report](https://github.com/faheemkhaskheli9/Brain/blob/fix/options-exact-decision-budget-20261112/research/stateful-options-exact-negative-2026-11-12.md), generated in 10-seed workflow run 43250847229; existing `stateful_options.mjs` and original [negative pilot](stateful-options-negative-2026-11-12.md) inspected.
- Attack: "learned two options" are assumed to perform useful temporal abstraction, but the engineered manager reselects the **same** option after voluntary EXIT if `carrying` did not change. EXIT permits spending evaluation decisions without physical action; the two-option arm is allocated more total evaluation decisions than a flat actor that reaches the environment step limit.
- Evidence: exact-budget options arm averaged **2,079.4 exits / 2,559.6 decisions** (81.24%) and only **480.2 physical transitions** per 32 frozen evaluation episodes, compared to flat's 1,280 decisions/transitions. Yet disabling EXIT also did not solve a single held-out task. Original older pilot already showed a similar ~81% EXIT collapse: this confirms a known negative limitation rather than discovering new compositional competence.
- Decision: next M0c diagnostic must report equal *training* budgets and evaluation primitive/environment-action accounting; add exit-disabled and matched-eval-boundary controls, and reject any interpretation based on invalid-action reductions alone.
- Reuse audit: a tested tabular-Q/legal-random/heuristic public-observation comparator already exists in [stateful_baselines.mjs](../game/world/stateful_baselines.mjs), but it operates over [stateful_carry.mjs](../game/world/stateful_carry.mjs), **not** this `stateful_construct.mjs` task. Port/reuse appropriate logic against identical observations rather than counting performance from different simulators as matched controls.
- Falsifier: with EXIT suppressed and a learnable public-observation baseline, does any learned policy achieve new-goal completion under comparable real actions? If not, do not build larger options, world models or multimodal interfaces to evade a failed elementary control.
- Claim status: measured no-op EXIT problem and continued held-out failure in this toy; AGI/general transfer unestablished.

## Round 15 — current-main evidence audit (2026-11-17)

- **Baseline:** \`main\` commit \`c4f41771e9d29188d2cfd6e845e97e88ff85de46\` (2026-11-16 22:43:59 UTC), after exact-budget PR #201. Latest main [CI run 43972854480](https://github.com/faheemkhaskheli9/Brain/actions/runs/43972854480) completed successfully. This round reviewed live source, archived experiment notes, backlog #120/#136, and M0 blueprint; **it did not re-run experiments**. CI demonstrates regression/test integrity under covered cases, **not** scientific success.
- **Observed result:** [10-seed exact-budget stateful options archive](stateful-options-exact-negative-2026-11-12.md) reports all nonprivileged arms at **0.000** frozen held-out goal completion, with a privileged feasibility oracle at **1.000**. Options-minus-flat paired mean **0.000**, CI [0, 0]; official promotion rule failed. The options arm used **81.24%** EXIT decisions with no corresponding physical transition; disabling termination also failed. This is a **measured negative** for that specific 5×5 toy, not a proof that hierarchical or local learning cannot work generally.
- **Challenge:** subsequent successful microcircuit/context studies could distract from the unchanged missing core result. The current repo contains useful independently scoped positive *synthetic* results, but no integrated single general learner showing reliable constructive transfer, long-horizon planning, retention, novel modalities and autonomous option discovery together.
- **Decision:** retain the existing **HOLD M1–M8** advancement policy. Do not permit an M1 success label from CI, shaped reward, invalid-action reduction, selection among two pretrained controllers, or a privileged feasibility oracle. Existing issue [#112](https://github.com/faheemkhaskheli9/Brain/issues/112) owns compositional learning; [#153](https://github.com/faheemkhaskheli9/Brain/issues/153) owns fair controls; [#154](https://github.com/faheemkhaskheli9/Brain/issues/154) owns integrity. No duplicate plan or new issue is warranted.

## Round 16 — temporal-credit adversary: are option switches being treated as task terminals?

- **Inspected path:** \`game/world/stateful_options.mjs::episode\` computes \`last = result.done || atCap || next !== option\`, then passes \`hNext = null\` to \`Brain.learn\` on an option change. In \`game/world/brain.js::Brain.learn\`, null \`hNext\` yields one-step TD target \`r\` instead of \`r + gamma * V(next)\`. Thus a **nonterminal physical transition that changes the engineered carrying-based option** receives a terminal-style target in the outgoing critic, including the first successful pickup. This behavior is source-confirmed; **its causal contribution to the zero-success result is untested**.
- **Adversarial alternative:** an option-specific critic may intentionally estimate *only the return until option termination*, so terminal-at-option updates can be valid under a different subgoal objective. The limitation is that this architecture currently lacks a demonstrated task-return bootstrap/across-options critic or manager-level value update. Do not call it a proven software bug or imply that cross-option bootstrap is universally correct.
- **Falsifier within #112:** add a minimal local TD-target unit fixture for a nonterminal pickup/switch, a true environment terminal and a budget truncation. Compare (A) current option-termination critic, (B) continuation bootstrap using next-option value or a separate task-level critic, and (C) shuffled-next-value control, with identical action/feedback access, network-capacity disclosure, exact environment-action and policy-decision budgets. Test 10 development seeds then freeze a structurally distinct evaluation family. Report actual goal delivery, not only TD target magnitude. Preserve the backprop-free update rule. The literature on semi-Markov options [Sutton, Precup & Singh (1999)](https://doi.org/10.1016/S0004-3702(99)00052-1) and learned termination [Bacon, Harb & Precup (2017)](https://doi.org/10.1609/aaai.v31i1.10916) is *prior art for a test*, not evidence that a change will help.

## Round 17 — split-design adversary: are held-out labels genuinely novel structures?

- **Source observation:** \`game/world/stateful_construct.mjs\` fixes \`START=[2,0]\`, four source-target corner-pairs per split, and exactly four obstacle templates. Therefore each split can generate at most **16 distinct (goal pair, wall template) configurations** despite arbitrary task IDs and seeds. Its \`generate\` samples with replacement; different task IDs are not evidence of independent spatial problems.
- **Consequence:** pairing many seeds with many trials on this generator estimates stochastic robustness on a tiny authored task family, not transfer across structural families. Goal-pair disjointness is useful but insufficient for new obstacle topology, start positions, goal affordances, dynamics or horizon. The available \`stateful_baselines.mjs\` tabular Q and heuristic apply to **another environment** (\`stateful_carry.mjs\`), so their published scores cannot be used as matched controls on \`stateful_construct.mjs\`.
- **M0c resolution, reusing #110/#112/#153:** first hold out full canonical \`(start, item, goal, obstacle map, dynamics, horizon)\` fingerprints, excluding generated IDs. Add a public-observation tabular/history policy, legal stepwise random and a legal reactive heuristic **inside the same \`stateful_construct\` transition interface**, with exact policy decisions, *physical transitions* and charged reward/verifier calls. Introduce two separately generated stress families only after the simple diagnostic shows some nonprivileged learning. Freeze hashes and seed assignments before sealed evaluation. Track effective unique configurations and failures, not raw sample count. Do not silently relabel the old 10-seed evidence.

## Round 18 — endpoint and biological-analogy adversary (2026-11-17)

- **Confirmed limitation in independent synthetic results:** [continuous motor delayed-feedback evaluation](continuous-motor-results-2026-11-12.md) passed its *progress-reward* gate (+0.28993 vs periodic), but goal contact was **0.2266** against periodic **0.2529** (difference −0.0264; paired CI spans zero). This is **not evidence of improved reaching success**. The separate [online-context study](online-context-results-2026-11-12.md) had a positive goal-hit difference versus blind random (+0.24844), but selected between two previously trained microcircuits using a designed reward; it did not show de novo lifelong representation learning.
- **Positive result with a deliberately weak control:** [structural-plasticity pilot](sparse-plasticity-results-2026-11-12.md) reached 1.000 held-out success on a one-cue binary task after the fixed-topology control was deliberately denied access to the predictive cue. A privileged correctly wired topology also scored 1.000 without growth. The supported claim is **repair of an engineered missing-edge defect**, not general neural wiring superiority or human-like cortical development.
- **Misleading interface claim:** the opening of [Brain World README](../game/world/README.md) said “Nothing is scripted,” while \`World.step()\` uses an engineered stage-dependent gait reset/action set in the default curriculum and \`stateful_construct.mjs\` provides authored reward, sensory mappings, task grammar and legal primitives. Clarify **engineered environment and innate control** versus **policy parameters learned from reward**. Existing issue [#34](https://github.com/faheemkhaskheli9/Brain/issues/34) owns broader user-facing claim accuracy.
- **Decision:** keep the wording and metrics faithful to *measured goal completion*, use reward as secondary mechanism evidence, require real transfer beyond a fixed family before any general-intelligence claim, and label cortex/hippocampus/basal ganglia references as analogies unless directly supported by biological experiments. No change to \`research/claims.tsv\` is justified by this inspection-only round.

## Round 19 — audited handoff and stop/go gates (2026-11-17)

1. **P0, #112/#153 — M0c same-environment learnability:** public-observation tabular/history, legal reactive heuristic, random, flat policy; identical legal primitive set/reward and transition code. Preregister 10 paired dev seeds, exact decision budgets, counts of *environment* actions, tabular states/memory bytes, oracle calls and physical goal success. **STOP** architecture work if no public-observation control beats random on a deliberately simplified case; repair observability, horizon/reward or task learnability instead. This step is **not completed as of audited main**.
2. **P0, #112 — two-level credit diagnostic:** compare current terminal-on-switch update against an explicit task-return bootstrap and shuffled control. Log each pickup, option switch, EXIT, critic target and delivered item. Report any effect as exploratory until the new families are frozen. This step is **not executed**.
3. **P0, #110/#154 — M0d mutation controls:** fail closed on duplicated structural fingerprints under different IDs, swapped nonterminal-vs-terminal flags, hidden oracle observation, uncharged option exit or physical action, shared train/evaluation state and omitted failures. Extend existing gates; avoid a second result format. This step is **not completed in full**.
4. **Only after successful M0c/M0d:** compare flat, engineered options and genuinely learned initiation/termination on 20 sealed seeds across at least two new generator families. Require actual held-out goal success >= +0.10 over strongest dev-selected **non-oracle** baseline, paired 95% CI lower bound > 0, retention lower bound > −0.05, and valid accounting (existing v1.1 proposal). Otherwise preserve a **HOLD/REJECT** negative result. Do not alter frozen criteria post hoc.

**Source/evidence boundary:** main source code, GitHub Actions CI state and previously archived numeric experiment reports were inspected; **no new scientific run, independent reproduction, human-brain experiment or AGI breakthrough was performed in this review**. Prior historical failures and all 15 earlier ledger rounds remain intact.

## Round 20 — M0c matched same-environment controls implemented (2026-11-17)

- **Source baseline and purpose:** main `69e4fb1a586530e67a87a1e7c29e013fe5706644`, existing open #112/#153; code implementation in `game/world/stateful_construct_controls.mjs` and regression tests in `test_stateful_construct_controls.mjs`. Follow the [M0c dated knowledge note](m0c-stateful-construction-controls-2026-11-17.md) rather than adding another plan.
- **Attack corrected:** controls from `stateful_carry.mjs` previously could not be treated as matched evidence on `stateful_construct.mjs`. The new runner uses the latter's exact observation, transition, reward and six-action interface for flat, goal-masked, public-state Q, target-relative Q, uniform random and locally discovered-wall heuristic. The existing `TabularQ` storage is reused with parameterized action count.
- **Integrity:** all trained arms have exact primitive/environment transition caps; invalid moves and failed pickups/drops are charged; no oracle is accessed by a policy; complete physical task fingerprints omit IDs, detect split collisions and expose duplicate within-split structures. Frozen Q scores use deep-copied tables. Legacy fixed geometry remains **only a regression/development suite**, not a new structural holdout.
- **Adversarial counterexample:** a highly successful reactive online maze heuristic or target-relative-Q does **not** prove the Brain actor learned internal representations or novel options: both have prior knowledge embedded in code. A tabular learner failing after 10k steps does not prove local plasticity impossible; it could expose sparse reward or state representation difficulty. Do not claim transfer until independent structural families are tested.
- **Verification boundary:** this note was authored alongside code **before CI completion**. CI smoke must pass schema and deterministic tests, but cannot satisfy M1 scientific improvement thresholds. A later full scientific run must archive per-seed evidence, compared physical goal completion, matched costs and failures; do not edit historical negative results.

## Round 21 — structural holdout and independent ten-seed research protocol (2026-11-17)

- **Inspected base and reviewed mechanisms:** main [`2f714b7`](https://github.com/faheemkhaskheli9/Brain/commit/2f714b714d80574c4d66697f55bfbf3c3d61d250), `stateful_construct.mjs`, `stateful_construct_controls.mjs`, `stateful_options.mjs`, and issue #112/#120/#136/#153/#154. Prior baseline stress: the so-called heldout set used 4 goal pairs × 4 obstacle templates, fixed starting position, and task IDs varied independently of physical geometry.
- **Attack and intervention:** add independently drawn scattered-obstacle and single-gate barrier topologies, variable starts and both train→heldout directions; fingerprint the real task structure, reject collisions, count offline BFS feasibility filters, and use physical fingerprint instead of arbitrary ID for Brain evaluation RNG on new tasks. Never pass an oracle path into a learning policy.
- **Scientific gate:** six matched same-environment arms; precommit legacy 10,000 and stress 2,500 decisions per trained arm, 10 seeds each, 16 dev and 16 heldout tasks ×2 repeats. Bootstrap paired physical-delivery success across seeds and choose the strongest comparator **using development only**. Raw `brain-result/1`, exact-budgets and negative outcomes must survive. The two authored topology families do **not** yet constitute independent 20-seed confirmatory transfer.
- **Adversarial caveat:** BFS filtering selects reachable tasks, relative-state Q injects a human-defined coordinate prior, maze heuristic supplies planning code, and environment physics/reward remain hand-authored. A positive score on any of these cannot establish autonomous planning/AGI. Preserve HOLD M1–M8 regardless of CI green or shaped reward. Existing [dated protocol](m0c-structural-transfer-protocol-2026-11-17.md) separates implementation and scientific results.
- **Verification status at authoring:** code, deterministic tests, Python mutation-style integrity checks and a PR-triggered raw artifact workflow are proposed and pushed; CI and numeric ten-seed results were **not yet complete when this entry was written**. Add an evidence addendum after running, without rewriting past rounds.

## Round 22 — 180 arm/seed exploratory evidence rows archived; M1 promotion rejected (2026-11-17)

- **Reproduced CI source:** [source branch commit `38ecbad5`](https://github.com/faheemkhaskheli9/Brain/commit/38ecbad5ef41c1aa00beb2a02e95b74c727d91a5); [GitHub Actions #44087806775](https://github.com/faheemkhaskheli9/Brain/actions/runs/44087806775), all 3 matrix jobs succeeded. `brain-result/1` `commit=511f6c6` is the PR test-merge checkout, not an independently verified mainline run. Full per-seed JSON and paired CI are archived in [dated M0c results](m0c-ten-seed-evidence-2026-11-17.md).
- **Observed:** fixed ten seeds 1–10, 60 arm/seed rows per protocol. The flat backprop-free learner had **0.000** heldout physical delivery on all three protocols at exact 10,000 legacy and 2,500 per stress-direction training decisions. The authored relative-Q comparator was **0.250** legacy, **0.009375** scattered→barrier and **0.025** barrier→scattered; an engineered public-sensor BFS-style maze policy was **1.000** on the feasible-filtered task sets. Frozen goal-mask successes were sparse and unreliable.
- **Adversarial rebuttal:** the heuristic's successful outcome is not learned path planning, and relative-Q's supplied coordinate prior cannot be credited to Brain. The two stress directions use fewer training decisions than legacy; their numerical gap is *not* a controlled test of effect of topology alone. Because feasibility is oracle-filtered offline, the task distribution is conditional on reachability. All seed outcomes are exploratory, not sealed confirmation.
- **Decision:** explicit **HOLD M1–M8 / reject AGI or integrated skill-transfer claim**. Existing backlog #110/#112/#153/#154 remains. Next use a fixed-geometry public learnability task, add a history/TD-credit diagnostic with matched budgets, and re-test on independent sealed families without tuning on evaluation. No claims.tsv change: no biological claim established.

## Round 23 — fixed-task feedback and exploration diagnosis proposed (2026-11-17)

- **Source baseline:** main [3ebc3c0](https://github.com/faheemkhaskheli9/Brain/commit/3ebc3c0abbd81ea132920e66ce5610a188d773b6). The archived ten-seed same-environment evaluation recorded flat Brain 0% delivery across its legacy and independent structural stress protocols. Code review of stateful_construct.mjs, stateful_options.mjs, stateful_construct_controls.mjs and brain.js exposed ambiguity between sparse delayed reward, exploration and engineered feature accessibility.
- **Intervention:** a deliberately repeated three-action task with flat Brain, public absolute/relative Q, higher epsilon exploration, engineered potential shaping, zero-feedback and uniform-random controls. Exact 0/250/1000/4000 decisions for each trained arm over fixed seeds 1–10; frozen physical success at every checkpoint; native simulator primitives/rewards intact. See [dated protocol](m0c-fixed-calibration-protocol-2026-11-17.md).
- **Adversarial boundaries:** an authored goal-distance reward or relative spatial key is *supplied knowledge*, not a discovered representation. Repeated-task learning is memorization/adaptation, not novel transfer. Zero-feedback tests whether Q can succeed without causal goal feedback, not whether an LLM can learn. No hidden oracle access; charge invalid actions and verify budget/training-state noninterference.
- **Verification status at authoring:** code, tests, and artifact workflow pushed to a PR branch; 10-seed numeric results not yet read. Archive all negative/raw results with exact source commit and append findings; never relabel this as AGI. **HOLD M1–M8**.

## Round 24 — executed repeated-task learnability calibration, limited Brain improvement (2026-11-17)

- **Evidence:** [dated ten-seed outcome](m0c-fixed-calibration-results-2026-11-17.md) with 70 archived brain-result/1 arm/seed rows, source head a03f5ddb748e248005339c9fb7d31b1b9e692576 and [Actions 44100531505](https://github.com/faheemkhaskheli9/Brain/actions/runs/44100531505). Ten fixed seeds, 4,000 exact physical decisions per trained arm, complete valid statuses and zero policy oracle calls.
- **Observed:** flat backprop-free Brain 5.00% to 9.17% repeated-task delivery (paired gain +4.17 pp; 95% seed bootstrap CI [-0.83, +10.83] spans zero). Absolute and relative tabular Q both 100% on that same trained structure after equal training steps; no-feedback Q and random 0.83%. The supplied target-relative Q key improves nearby-variant performance relative to absolute keys, but is hand-authored structure, not learned spatial abstraction.
- **Adversarial interpretation:** reliable learning *can* occur with the public simulator sensors using an engineered tabular policy. Brain's learning rule/access/exploration remains bottlenecked; its paired improvement is not statistically resolved. Neither repeated-task acquisition nor supplied potential feedback justifies claims of transfer, cortex simulation or AGI; Q/neural model capacity differs.
- **Decision:** preserve HOLD M1–M8. Next isolate Brain action entropy, item/goal feature access and single-step TD/eligibility targets before architecture changes; then test on independent heldout families. Keep all raw negative runs. No claims.tsv update.

## Round 25 — explicit native Brain sensor accessibility and temporal-credit falsifiers (2026-11-18)

- **Inspected baseline:** main [bb8a07de](https://github.com/faheemkhaskheli9/Brain/commit/bb8a07de9be226c9d8fdd04c3de2c6bdd45dfa0f), primary code `brain.js::Brain.encode/act/learn`, `stateful_construct.mjs`, `stateful_options.mjs`, `stateful_calibration.mjs`, previous measured M0c ten-seed negative. Existing issues #112/#120/#136/#153/#154 reused.
- **Adversarial attack:** Brain.encode copies the full public observation vector directly into its input block (`h.set(x)`), falsifying an unsupported claim that sparse hidden wiring alone hides goal/item/carry channels. Failure might instead arise from learned actor/critic features, action entropy, exploration and credit.
- **Falsifiable prototype:** six matched backprop-free Brain arms with identical initialized models and six physical primitives: native three-step, native two-step difficulty calibration, target-goal masking, zero feedback, current-step-only eligibility, no TD bootstrap. Instrument input/actor weights, frozen counterfactual goal sensitivity, entropy, TD error, physical completion and step counts. Each arm has exactly 0/250/1000/4000 decision checkpoints over predeclared seeds 1–10. Preserve failed-run rows.
- **Red-team controls:** same goal on training makes goal masking intrinsically underpowered; the two-step arm has a changed objective; arms are identical at initialization but cannot have identical data trajectories after reward changes; fixed geometry is in-sample; a counterfactual L1 response does not establish *correct* goal use. No engine or Brain core modifications, no oracle paths for learning, no learned memory/planning claim.
- **Status at entry:** changes and unit gates proposed, full ten-seed run unverified. [Registered protocol](m0c-sensory-credit-audit-2026-11-18.md). After running append observations and negative findings. M1–M8 HOLD.
