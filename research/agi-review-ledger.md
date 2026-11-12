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
