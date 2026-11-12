# Context-dependent sparse checkpoint memory: precommitted motor-reversal experiment

**Research status:** implementation and exploratory tests; confirmatory run is reserved and not yet executed when this protocol is committed. This is a bounded **engineering-memory mechanism**, not a mammalian hippocampus, autonomous context-change detection, or brain-equivalent synaptogenesis. The structural 78-region graph and Brain World's backprop-free learner are unchanged. Reuses #65 (surprise and context), #112 (reusable skills), #114 (episodic retrieval), #152 (replay), and #154 (retention gates). H149 remains unproven.

## Exact gap

The earlier frozen one-joint reversal study (`closed-loop-reaching-results-2026-11-12.md`) reported evidence-guided learning success 0.930 on standard held-out reaching, but later motor reversal caused source-task retention to drop by about -0.521. It is possible to avoid overwriting an old policy by preserving a separate snapshot, but selecting the appropriate snapshot without privileged labels is the actual challenge.

## Mechanism

`context_memory.py` is a capacity-two **bank of separately learned `SparsePlasticPolicy` checkpoints**. Each has at most four local learned functional synapses and its own serialized RNG, candidate cache and error state. Each slot comes from ordinary post-action reward training, and uses the same sparse local plasticity / growth code as the previous pilot. No extra dense learned gate or hidden simulator-context flag is added. It saves JSON with a strict version and restores independent copies; changed-context training cannot modify the original.

A fixed-size **development-only probe** evaluates every saved candidate on identical fresh toy-body episodes, using its deterministic actions and the resulting **public post-movement reward**. The system chooses the highest mean reward. It does not know the hidden inversion sign; only the environment applies the sign. The experimenter still explicitly defines the training→reversal adaptation boundary and requests a new context selection at each evaluation block. This is *not automatic change-point discovery*. Every candidate probe resets the simulated joint body and receives charged physical actions/reward signals; this is not a zero-cost passive lookup. It also doubles checkpoint storage relative to one policy. No source or evaluation trials may be used as selector probes.

```
old task -> learn sparse controller A -> save A
motor rule inverted by environment -> adapt detached clone B -> save B
new context requested -> run fixed charged DEV probes through A and B
choose by real progress reward -> freeze selected weights -> held-out body actions
same for return of original motor rule -> retrieval should choose A
```

## Scientific protocol (reserve before evaluating new seeds)

| Design choice | Fixed value |
|---|---|
| Seeds | 401–410 inclusive (10 paired seeds, never tune on these) |
| Exploratory seeds | 0–2 only, excluded from confirmatory comparisons |
| Shared policy pretraining | 120 train episodes × 16 body actions = 1,920 actions |
| Reversed motor adaptation | 40 development episodes × 16 = 640 actions in independent policy B |
| Frozen normal task | 80 distinct source-family episodes × 16 = 1,280 actions |
| Frozen reversed task | 80 distinct held-out eval-family episodes × 16 = 1,280 actions |
| Context probes per regime | 6 development episodes × 3 actions × 2 checkpoints = 36 actual probe actions |
| Total probes per bank arm | 72 actions: reversed and normal-return contexts; **not** included in learning interactions |
| Saved checkpoints | Up to 2 independent sparse models, 4 trainable synapses per model |
| Arms | `single`, `bank_latest`, `bank_random`, `bank_probe`, `bank_oracle` |

The five arms share the **exact same pretrained A** and **exact same reversed-trained B** checkpoint per seed, so differences in selection are not due to lucky training. `single` carries only B, pays 0 probes and is a cheaper baseline; `bank_latest` stores A and B but always selects B, `bank_random` samples a checkpoint independently (both bank controls still pay all 72 probes), `bank_probe` selects using reward evidence, and `bank_oracle` picks known correct A/B labels as an explicitly **privileged upper bound** (also pays probes). In all cases scoring runs on restored checkpoints with learning off. `sourceBefore` is the original saved A evaluated on the same normal test family as `returnSuccess`, so the retention delta is paired within each seed. A probe may touch the goal and receive reward; the binary goal is an **engineered task**, not real visual perception or understanding.

### Preregistered decision rule

**Primary:** paired `bank_probe.returnSuccess - bank_random.returnSuccess` ≥ +0.15 absolute held-out success, paired 95% bootstrap lower bound > 0 and exact two-sided sign-flip p ≤ 0.05, with all 50 arm-seed rows present and status `ok`. **Additional required controls:** beat `bank_latest` on mean return success by ≥ +0.15, keep mean `retentionDelta` ≥ -0.05, and mean reversed success within -0.05 of `bank_latest`. If any criterion fails, the planned hypothesis is not supported, even if memory protects a checkpoint by construction. Secondary: correct source/reversal selections, probe efficiency, saved bytes, total synaptic and candidate products, return final error and per-seed failures. Both positive and negative outcomes will be kept; the previous failed evidence-growth advantage remains unchanged.

Comparison against `single` alone is **not compute/memory matched**, and cannot establish better sample efficiency. Bank arms have the same saved models, probes, and training data, and form the meaningful selection comparison. All selector decisions are based on *development* reward probes and only then frozen on untouched eval tasks. We expect context labels to be weak or ambiguous in more realistic environments; a failure to distinguish contexts should be recorded, not hidden.

### Validation and adversarial checks

- Reject non-development selector probes, oversized lists, wrong body factory, nonfinite/corrupt weights, invalid memory format, invalid slot capacity, and pending feedback. Restore JSON without pickle.
- Mutation tests: modifying a retrieved copy or adapting B must never change stored A. Repeated evaluation produces identical selections, checkpoints and scores, excluding timing.
- A shuffled/random bank that ignores probe outcomes shares bank memory and probe cost; report the gap. Privileged oracle must not be used to tune learning.
- The environment transition timing is provided externally; the selector does not detect it autonomously. **Context-specific storage is not synaptic consolidation in a single network.** The bank can also fail if contexts cannot be distinguished by rewards, memory slots fill, or rewards are delayed/noisy.
- Relative-target observations and progress reward are engineered; bodies reset for probes. There is no transfer from natural images/audio, no recurrent neural populations, and no proof of biological circuit mechanisms.
- The two saved policies require about twice the model checkpoint bytes; account for extra reward queries, not just four live synapses. No compute or energy efficiency claim from sparse active weights.

### Run

```bash
python research/test_context_memory.py
python research/test_evaluate_context_memory.py
python research/evaluate_context_memory.py --seeds 0 1 --train-episodes 6 --adapt-episodes 4 --eval-episodes 3 --probe-trials 2 --probe-steps 2 --out /tmp/context-memory-smoke.json
python research/result_schema.py --check /tmp/context-memory-smoke.json
```

**Confirmatory run only after committed protocol and source hash:**

```bash
python research/evaluate_context_memory.py --seeds 401 402 403 404 405 406 407 408 409 410 --train-episodes 120 --adapt-episodes 40 --eval-episodes 80 --probe-trials 6 --probe-steps 3 --commit SOURCE_COMMIT --out /tmp/brain-context-memory-confirm.json
python research/result_schema.py --check /tmp/brain-context-memory-confirm.json
```

Artifact: `brain-result/1` with 50 complete arm/seed records, exact policy checkpoint hashes, probe counts, config, budgets, conditional result and negative finding, source revision. Results will be documented separately after the run; neither the proposed method nor exploratory seed performance is confirmatory evidence.