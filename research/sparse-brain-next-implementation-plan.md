# Brain: evidence-gated sparse neural learning implementation plan
Date: 2026-11-12
Status: proposed; planning document, NOT implemented results
Scope: the separate research scaffold under research/, then optional Brain World integration.
Owners and backlog: roadmap #120; execution order #136; reuse #65, #94, #112-#115, #152-#154, #164.

## Decision

Prioritize measurable learning over more anatomical labels or speculative AGI features.
The present 78-node, 142-edge hand-designed regional graph has separate unassigned
learning weights, an active-source sparse scalar router, bounded body control,
and image/video/text/audio I/O adapters. There is no learned neural
propagation or learned decoder from cortex to motor or media output.
The ratio 154/6006 (2.56%) is *synthetic regional sparsity*, not human
neuron-to-neuron connectivity. No output codec should be scored as learned
generative behavior. Do not modify or relax the Brain World backprop-free
learner constraint to make research results look stronger.

Main CI was green when this plan was authored. The 10-seed stateful options
pilot (research/stateful-options-negative-2026-11-12.md) recorded 0.000
held-out success for both flat and two-option learners; the BFS oracle
scored 1.000. This is a **negative learning result** and a reason to first
solve verified lower-complexity tasks. Reuse experiments and controls;
do not relabel the oracle or engineered features as learned.

## Reference architecture (target, not current behavior)

    Vision/image/video/audio/text/touch/proprioception
                    |
    bounded per-modality encoder; no hidden task/answer leakage
                    |
    sparse feature-preserving projections (not global mean abs)
                    |
    E/I recurrent neuronal populations + activity state
                    |
    local learning / eligibility traces + modulatory feedback
                    |
    memory/replay + bounded planner + uncertainty gate
                    |
    learned motor and symbolic output selection
                    |
    simulated body and constrained media renderers
                    |
    observable outcome and error -> learning and retest

Every source-to-target pathway should have explicit provenance, sign policy,
fixed edge budget, spatial/temporal shape contracts, and a learning scope.
Macro-anatomical edges and microcircuit synapses are different units of
analysis. Empirical connectome structure is not a synaptic weight.

## Preregistered baseline protocol for new mechanisms

- Seeds: 1–10, fixed in advance; report every successful or failed run.
- Dataset: train, development, and untouched frozen evaluation families;
  create and fingerprint a **new** holdout for the next experiment, since
  earlier #112 holdout tasks have already informed interpretation.
- Trial budget: one small diagnostic first (20k primitive environment
  interactions per learned arm, 10 seeds), scale to 100k only if
  learnability is established. Report decisions separately from actions,
  reward calls and verifier queries. No tuning on frozen test.
- Baselines: learning-off, fixed heuristic, legal random, existing flat
  backprop-free learner, matched-size dense and randomly rewired sparse
  graphs; separately labeled conventional DL or oracle references.
- Matching: environment transitions, decisions, observations,
  initialization data, trainable parameters, and feedback availability;
  additionally report wall time, peak memory, weighted products, active
  neurons and emitted events. A budget mismatch must be flagged, never
  silently normalized away.
- Primary metric for the first task: unseen-goal success rate after an
  identical train budget. Secondary: error reduction over repeated attempts,
  reversal adaptation, retention of the old skill, wall time/memory,
  connectivity density, and useful novelty where applicable.
- Proposed advancement gate, not a claimed result: >= +0.10 absolute
  paired held-out success versus the strongest matched non-oracle control,
  positive seed-paired 95% CI, lower 95% retention change >= -0.05,
  and no severe compute regression at equal task success. Report failures
  even if this criterion is not met. Freeze the gate before the run.
- Output format: brain-result/1, raw per-seed trajectories (including
  failures), checkpoint hashes, exact source revision, CPU/RAM, config,
  objective leakage checks, and an updated claims register when needed.

## P0 — reliability, contracts and simpler diagnostics (first)

Deliverables:
1. Characterize behavior and bottlenecks in existing modules. The current
   sparse router compresses each high-dimensional sensory packet to one
   mean-absolute value, losing direction, position, timing, and sign.
2. Define typed, versioned input/region/output contracts and explicit
   conversion boundaries. Validate modality timestamps, short/long clips,
   reset behavior, missing channels, NaN/Inf, and movement safety.
3. Add two deterministic tiny diagnostic environments with independent
   oracle solvability and train/dev/test splits:
   (A) reversible two-cue association with distractors and delayed reward;
   (B) 2D reaching with two joints, target, obstacles and proprioception.
   Do not reuse the impossible-at-current-budget option task as the first
   learning acceptance test.
4. Add a zero-learning and hand-assigned-weights control. Snapshot raw
   input packets, intermediate activation, motor command and outcome
   without exposing hidden goals or validator state.
Files: research/test_sparse_connectivity.py; research/test_multimodal_io.py;
research/test_audio_io.py; research/sensorimotor_bridge.py; new
research/sparse_brain_tasks.py and research/test_sparse_brain_tasks.py.
Gate: reproducible runs, no leakage, bounded memory, source and held-out
task families provably disjoint, no unearned capability claims.

## P1 — preserve features inside the sparse anatomical framework

Do NOT feed RGB/video/audio/text through an absolute-value scalar bottleneck.
Keep separate, bounded vectors and sparse **per-feature** projection edges;
only active features should contribute. Start with 8–32 channels per
population; avoid applying 192 pixel features to every downstream node.
Use 10-seed matched studies of learned embeddings vs nonlearned
spatial/temporal features. Preserve negative signs and output ordering;
hold back timing/video temporal facts needed by the task.

Files: new research/sparse_populations.py and tests; opt-in adapter in
research/sparse_connectivity.py, preserving scalar API and legacy tests.
Gate: simple two-pattern discrimination succeeds after routing, retains
frame or audio ordering, and does not regress resource/invalid-input guards.
Measure downstream information discrimination, not only exact codec roundtrip.

## P1 — event-driven neurons, synapses and stable dynamics

Start with a rate-neuron implementation and then a configurable leaky
integrate-and-fire (LIF) variant. For only the active task-relevant
regions, create small populations (suggested 64–256 units initially),
configurable E/I ratios, Dale-consistent outgoing signs, local recurrence,
delays and homeostatic controls; do **not** claim those chosen sizes are
biological measurements. Sparse CSR/COO or adjacency arrays, no NxN dense
allocation at runtime. Ensure isolated/inactive populations do not incur
synaptic multiply operations, no runaway activity, no dead-network
collapse, deterministic seeded replay, and stable serialization.

Files: new research/neural_populations.py and tests; experiment metadata
in research/results/ through brain-result/1.
Gate: robust bounded dynamics across seeds, CPU memory target <= 512 MB
for the *small pilot*, and equal-output reference agreement between
sparse and dense oracle mathematics with all gates disabled.
No claim of GPU superiority based solely on edge counts.

## P1 — make connection values learn from mistakes

Introduce explicit per-experiment seeded initialization (separate from
anatomical observations): None until the training experiment calls
initialize(). Compare local Oja/Hebb, reward-modulated eligibility traces,
and (for LIF) STDP plus stabilizing homeostasis. Update *only existing*
trainable synapses; add no global dense backward pass to Brain World.
Use three-factor local changes as the primary action-learning candidate;
pre/post eligibility and an external verified reward/error signal.
Disclose engineered reward, sensor preprocessing, action primitives,
and modulatory delivery. Trainable local signs and bounds must be validated.

Files: new research/local_plasticity.py, research/test_local_plasticity.py,
research/learn_sparse_brain.py, research/test_learn_sparse_brain.py.
Gate: ten-seed improvement on unseen cues/targets versus random,
frozen and shuffled-reward controls; demonstrate fewer repeated errors,
not merely retrieval of seen samples. Track updates/edge, synaptic cost,
forgetting and saturation. If source success remains near zero,
**stop** before hierarchical options.

## P1 — first real closed-loop body learning

Connect neural motor-pool activity into MotorDecoder and SimpleJointBody
through an explicit saturating actuator policy, preserving emergency
bounds and command validation. The learner sees target-relative sensory
features/proprioception and receives external reward only **after**
actions. Evaluate a progressively harder curriculum: single joint ->
two joints -> delayed sensory cue -> obstacle/reversal -> held-out targets.
Never include the exact target coordinates as a privileged observation
unless all compared agents receive the same public sensory measurement.

Files: research/sensorimotor_bridge.py (opt-in policy hook),
research/sparse_brain_tasks.py, learned policy experiment and tests.
Gate: positive held-out motor improvement and recovery from wrong moves,
with 10-seed intervals and retention; actor generated commands recorded.
Externally injected motor commands may be used only in integration tests.

## P2 — working memory, continual learning and reusable skills

Reuse Brain World's replay/context/continual gates rather than create a
second incompatible memory framework (#65, #112, #114, #152, #154).
Only add a stateful neuronal memory mechanism after the low-level task
learns. Compare no memory, short fading trace, gated state and replay
with equal memory bytes. Stage a newly preregistered acquire/carry/place
curriculum with observable subskill successes, learned option termination,
explicit control transfer, and fresh held-out compositions.

Gate: old-task retention and success on withheld sequences over the
best matched flat learner; compare against engineered option selectors.
The previous option pilot's 0.000 scores remain a negative result;
do not silently reuse its frozen task family as a fresh test.

## P2 — actual multimodal understanding and constrained output actions

Do not mistake PNG/WAV/MP4/UTF-8 encoding for learned perception or
generation. Begin with small paired inputs: image<->symbol, tone<->symbol,
short audiovisual sequence->outcome, and delayed instruction->body
action, all with disjoint concepts/combinations and no answer leakage.
First prove recognition/grounding and contrast against vector-only
fixed features; then add learned symbolic action outputs for short text
and simple image strokes or tone sequences. Convert **learned output
actions** with existing encoders into media artifacts. Label any external
ASR, TTS, VLM, diffusion, or LLM component as an independent hybrid
interface/baseline, never as skill learned by Brain's creature.

Files: research/multimodal_io.py, research/audio_io.py, new
research/multimodal_tasks.py and tests. Video soundtrack sync and
microphone are separate opt-in engineering work, not prerequisites.

## P2 — prediction, planning, curiosity and transfer

Reuse #113 forward-model planning criteria, #115 uncertainty and #112
option baselines. Start with a model that predicts one-step sensory
changes from observed state and action. Test multiple-step error growth
before planning; cap rollout depth and action candidates. Require
ablation of the predictive model and correct accounting for model
updates, environment interactions, simulated rollouts and reward calls.
Keep a reactive fall-back under uncertainty. Only then test
recombination and useful novelty against fair candidate generators.

Gate: statistically supported held-out sample-efficiency/goal gain
over compute-matched reactive policies, plus old-skill retention.
Record failures and confidence intervals; terminate unpromising arms.

## P3 — empirical wiring, dynamic sparsity and efficient scaling

Before claiming anatomical fidelity, add a **small, provenance-tagged**
empirical-subgraph loader; validate one subset of FlyWire (adult fly)
or MICrONS (mouse visual cortex) *without pretending it is a human
whole-brain map*. Record species, specimen, reconstruction confidence,
ROI, neuron/cell type, transmitter predictions, missing synapses and
license. Compare its topology against degree-preserving rewires, synthetic
motifs and matched random graphs under the same learning budget.
Investigate dynamic prune/regrow only after fixed-topology gains and
negative controls. Profile CPU/GPU sparsity and vectorized dense
baselines before claiming speed, power or memory gains.

Sources:
- Dorkenwald et al., Nature 2024, adult Drosophila connectome:
  https://doi.org/10.1038/s41586-024-07558-y
- MICrONS Consortium, Nature 2025, functional/connectomic mouse visual areas:
  https://doi.org/10.1038/s41586-025-08790-w
- Diehl & Cook 2015, unsupervised STDP and homeostatic stabilization:
  https://doi.org/10.3389/fncom.2015.00099
- Bellec et al. 2020, online eligibility-trace learning (e-prop):
  https://doi.org/10.1038/s41467-020-17236-y
- Evci et al. 2020, dynamic sparse training comparator (RigL):
  https://proceedings.mlr.press/v119/evci20a.html

## Adversarial failure gates and non-goals

1. **No biological inference from a toy simulation.** Species/subgraph,
   statistical analogue and speculative circuit priors must be labeled.
2. **Task leaks:** prohibit engineered goal labels and hidden simulator
   state from a policy input; separate verifier/oracle budget.
3. **Fake learning:** check actual changed synaptic parameters; compare
   against lookup, frozen, random-policy and shuffled-feedback controls.
4. **Sparse != fast:** measure wall time, operations, memory and resource
   overhead at matched quality and hardware. Tiny sparse Python graphs
   may run slower than vectorized dense NumPy.
5. **Dead or unstable neurons:** monitor silent-rate, saturation,
   sign constraint violations, and learning divergence across seeds.
6. **Overfitting holdout:** never adjust to #112's already reported
   frozen evaluation family; use truly unseen final evaluation.
7. **Complexity without competence:** if 20k-step subskill baseline
   cannot learn, stop and debug credit assignment/observation first,
   not add memory, consciousness, extra anatomy or media generation.
8. **Integrations:** do not replace Brain World's learner with a
   conventional gradient-trained model in the name of neuroscience;
   include such models only as labeled fair comparators.

## Ordered deliverables and issue mapping

1. P0 tests, diagnostic tasks, frozen experiment manifest
   (reuse #120, #136, #154).
2. Vector information preservation and sparse neural populations
   (reuse #65 and #94, extend separate research scaffold).
3. Backprop-free eligibility plasticity and a verified learnable
   sensory->motor task (#65, #112).
4. Retention, episodic replay, manager/skill hierarchy (#112, #114, #152).
5. Multimodal grounding and learned outputs (#94, #115) then
   bounded action planning (#113).
6. Empirical topology validation and fair performance benchmarking
   before any scaling or "brain-like intelligence" claims.

Each stage: small tested implementation, deterministic regression tests,
preregistered baselines, raw reproducible brain-result/1, negative
result retention, claim updates, and a single logical commit/PR.
Suggested checks on every phase: ruff check ., python build_index.py,
python run_code_blocks.py, python research/check_claims.py, relevant
Python and Node tests. For actual knowledge-base topic edits, also
update proper frontmatter and index per AGENTS.md.

## First commit-sized engineering task (next, not yet implemented)

Create research/sparse_brain_tasks.py with a two-cue delayed-response
task and explicit public sensor/target separation, plus tests for
deterministic splits, seed invariance, leakage, a trivial oracle,
and fair no-learning/random baselines. Implement no neural plasticity
in that commit. This gives a falsifiable testbed for the subsequent
vector-population and local-learning milestones.
