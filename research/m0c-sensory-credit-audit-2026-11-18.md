# M0c direct sensory access and temporal credit audit (2026-11-18)

**Status at registration: implementation proposed; experiment not yet executed.** This is a falsification study of the existing backprop-free Brain actor/critic, **not a new neuroscience result or evidence of AGI**. The previous [executed fixed-task study](m0c-fixed-calibration-results-2026-11-17.md) reported 5.00% to 9.17% delivery after 4,000 decisions by flat Brain (paired improvement CI includes zero), while a public tabular control reached 100% on the same repeatedly trained structure.

**Inspected parent:** [bb8a07de9be226c9d8fdd04c3de2c6bdd45dfa0f](https://github.com/faheemkhaskheli9/Brain/commit/bb8a07de9be226c9d8fdd04c3de2c6bdd45dfa0f). Checked code in game/world/brain.js (Brain.encode/act/learn, GAINS), stateful_construct.mjs, stateful_options.mjs, stateful_calibration.mjs, test_stateful_calibration.mjs, research/agi-execution-blueprint-v1.1-2026-11-12.md, AGENTS.md and issue [#112](https://github.com/faheemkhaskheli9/Brain/issues/112) / [#153](https://github.com/faheemkhaskheli9/Brain/issues/153) / [#154](https://github.com/faheemkhaskheli9/Brain/issues/154).

## Code-observed mechanisms and the adversarial review

1. **Observation access is not absent.** Brain.encode sets the *complete public input vector* directly into the first nIn encoded units using h.set(x). The sparse random hidden wiring does not remove direct 5x5 agent/item/goal, carrying or collision features. It remains possible that actor weights and exploration fail to exploit those channels. A claim of missing sensory connectivity would contradict the inspected source.
2. **Learning is genuinely local but can fail.** Brain.act samples a masked softmax across six primitives and creates critic and policy-gradient eligibility traces; Brain.learn applies TD error to those traces with gamma and a bootstrap critic. The policy starts with zero actor weights, hence an initially uniform distribution. Matching initial random seeds does not imply identical trajectories after arm-specific learning begins.
3. **Previously confounded interventions:** zero rewards, no goal observation, no cross-time trace, and no next-state value are different changes. This audit isolates one switch per arm without changing Brain.js or the simulator. It does not swap to tabular Q or introduce hand-authored action sequences.
4. **Fixed-goal masking is a weak dependency test.** A learner can memorize pickup–east–drop even when the goal map is blank. Success after goal masking cannot demonstrate goal reasoning; the frozen counterfactual target-switch sensitivity and nearby unsealed variants must be interpreted separately.
5. **A shorter task changes the problem.** The two-action pickup–drop configuration differs from pickup–move–drop in action count and geometry. Compare it only as a *difficulty calibration*; it does not isolate a trace mechanism.
6. **Temporal boundary ambiguity:** setting next value to zero while preserving eligibility (no-bootstrap arm) differs from removing past-action traces (one-step trace arm). A cutoff at a physical step budget still clears traces; we preserve the original treatment on all arms to avoid hidden extra updates.

## Hypotheses and falsifiers

- **H-sensory:** actor sensitivity to a visible goal change is not guaranteed merely because the raw channel is present. Report directly readable input width and a **frozen counterfactual action-distribution L1 difference** before and after training, alongside direct actor weight magnitudes for agent/item/goal/carrying channels. Goal-masked policy must show zero change for both target variations; any nonzero reading is a leakage failure.
- **H-traces:** with identical initial seed and same fixed three-step simulator, deleting previous-step eligibility may affect heldout diagnostic success and native delivery compared with the unchanged local learner. No performance direction is assumed; null or worse results are archived.
- **H-critic:** removing next-state TD bootstrap may change the learning trajectory; a deterministic one-step counterexample must yield different model updates when initial critic values are nonzero.
- **H-reward:** if reward is zero throughout training and critic weights start at zero, the actor should not update. Any learned goal-dependent improvement from that arm is a failure of the intended negative-control isolation.
- **H-depth:** repeated two-step pickup/drop may be easier than three-step pickup/move/drop; a success difference is a task-depth observation, not isolated evidence for temporal credit.

## Preregistered pilot, before looking at numeric output

- **Seeds:** 1–10; **six arms:** native-three, native-two, mask-goal, zero-feedback, trace-one-step, no-bootstrap. Same Brain architecture and identical initial seed per arm. No online oracle, backpropagation, gradient surrogate or engineered reward shaping. Environment uses existing six actions, native transitions and native reward except zero-feedback *to the learner*.
- **Training cost:** each arm exactly **4,000 charged primitive/environment steps** with cumulative checkpoints 0 / 250 / 1,000 / 4,000. Physical steps, number of critic/actor updates and evaluation episodes separately counted. Each cap truncation bootstraps the same actor's next value except for explicitly no-bootstrap arm.
- **Frozen scoring:** 12 repeats on each arm's own repeatedly trained physical task plus two nearby exploratory diagnostic task variants, 12 repeats each. A policy can succeed on a fixed task by memorizing; no heldout/generalization promotion. Goal-counterfactual probe uses the *same source agent/item state* and switches only the **public target** between [3,0] and [1,0].
- **Primary outcome:** physical same-task delivery completion at each checkpoint, with ten-seed paired 95% bootstrap CIs on change relative to native-three and before/after. **Secondary:** frozen action entropy, goal-sensitivity L1, actor direct sensor magnitude, native rewards, valid pickup rates, TD magnitude and erroneous action costs. No cherry-picked seeds, omitted statuses or significance claims based on unsealed variants.
- **Failure/stop:** if the unmodified learner still fails on the simple repeatedly presented task, do not add anatomical modules or claim transfer. If its goal sensitivity remains near zero while channels exist, examine its trained actor direct sensor weights and stochastic gradient signal. Keep M1–M8 HOLD under every possible outcome here.

## Reproducibility

```bash
node game/world/test_stateful_credit_probe.mjs
python research/test_analyze_m0c_credit_probe.py
node game/world/stateful_credit_probe.mjs 1 2 3 4 5 6 7 8 9 10 --checkpoints 0,250,1000,4000 --repeats 12 --out /tmp/m0c-credit.json
python research/result_schema.py --check /tmp/m0c-credit.json
python research/analyze_m0c_credit_probe.py /tmp/m0c-credit.json /tmp/m0c-credit-analysis.json
```

The [GitHub Actions evidence workflow](../.github/workflows/m0c-credit-audit.yml) preserves complete brain-result/1 JSON, failed as well as successful runs, experiment configuration, seed/checkpoint budgets, and deterministic descriptive uncertainty. All results must be committed to research/results and appended to agi-review-ledger.md, not inferred from a passing CI smoke test.

## Constraints, prior art and interpretation

This is an engineered five-by-five simulator, not a measured human brain. The actor-critic and eligibility-trace principles are related to policy-gradient RL and temporal-difference learning; see the repository's [original learning algorithm hypotheses](learning-algorithm-hypotheses.md) and [annotated research sources](learning-algorithm-sources.md). Such theoretical prior art does not validate any new neuroscience claim. A positive two-step or in-sample three-step result is **not** evidence of independent transfer, genuine general-purpose planning, creativity or AGI. All negative and failed outcomes count.
