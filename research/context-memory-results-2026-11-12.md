# Context memory and motor reversal: ten-seed confirmatory result

**Question:** Can a bounded bank of separately trained sparse policies select an earlier learned policy from **public post-action reward probes**, protecting it against later motor reversal without a privileged context label? The result is specific to the engineered one-joint reaching simulator, not a human brain or autonomous experience replay.

**Precommitted source:** `2341f7014c68260993e128279c8317559779bddc`. The design, seeds and primary gate were fixed before confirmatory evaluation in [the protocol](context-memory-pilot.md). Exploratory seeds 0–2 were not counted. The [machine-readable evidence](results/context-memory-2026-11-12.json) includes all **50 arm/seed records**, checkpoint hashes, probe choices, resource budgets and per-arm scores under `brain-result/1`; no failures or missing rows. Reserved seeds **401–410**.

## Reproduction

```bash
python research/evaluate_context_memory.py --seeds 401 402 403 404 405 406 407 408 409 410 --train-episodes 120 --adapt-episodes 40 --eval-episodes 80 --probe-trials 6 --probe-steps 3 --commit 2341f7014c68260993e128279c8317559779bddc --out /tmp/brain-context-memory-confirm.json
python research/result_schema.py --check /tmp/brain-context-memory-confirm.json
```

Both learned snapshots are shared by all arms *per seed* for an isolated, controlled selector comparison. A is trained on the original motor mapping with **1,920** actions; a detached clone B adapts to inverted motor dynamics using **640** additional actions. Frozen held-out and source-return scoring use **1,280** actions each per arm. A reward probe tries both checkpoints on six **separate development trials** for three actions each: 36 body interactions per regime, **72 charged extra actions** per bank arm for reverse selection plus normal return. Probe trials are not held-out scoring trials. No memory selector receives the environment's inversion flag.

## Confirmatory measurements

| Arm | Return to original motor rules | Frozen reversed success | Change in source success | Probe actions | Mean checkpoint storage |
|---|---:|---:|---:|---:|---:|
| `single` (original overwritten) | 0.3725 | 0.58875 | −0.5750 | 0 | 7,790 bytes |
| `bank_latest` (always B) | 0.3725 | 0.58875 | −0.5750 | 72 | 15,577 bytes |
| `bank_random` (equal-memory control) | 0.7700 | 0.33625 | −0.1775 | 72 | 15,577 bytes |
| **`bank_probe` (public reward selection)** | **0.9475** | **0.58875** | **0.0000** | 72 | **15,577 bytes** |
| `bank_oracle` (**privileged** context label) | 0.9475 | 0.58875 | 0.0000 | 72 | 15,577 bytes |

The `sourceBefore` mean across seeds was 0.9475. A saved original model has **exactly zero model-parameter forgetting** by construction; this is storage and retrieval, not consolidation of both skills in one set of synapses. Crucially, the 0.9475 returned-task success reflects *using the saved earlier checkpoint*, not new learning during evaluation.

**Primary pre-registered comparison: `bank_probe − bank_random`**: +0.1775 absolute return success, seed-paired 95% percentile bootstrap interval **[+0.0450,+0.32375]**, two-sided exact paired sign-flip **p=0.125**. Although the mean exceeds +0.15 and the bootstrap lower bound is positive, **the p≤0.05 component fails**. **Do not promote the preregistered superiority hypothesis.** The available 10 paired seeds do not establish a robust advantage over the equal-memory random selector under the prespecified rule. This negative gate is retained.

Secondary `bank_probe − bank_latest`: +0.5750, paired 95% interval **[+0.41375,+0.74750]**, sign-flip **p=0.001953125**. All 10 seeds selected the earlier checkpoint for the normal-motor return and the newer one for inversion, matching the privileged selector on this *highly separable deterministic two-context setup*. Frozen reversal success was identical to `bank_latest` (0.58875), satisfying the corresponding retention and reversed-performance secondary gates. The protocol requires every primary and secondary criterion, so the **overall gate fails**.

Averaged over paired seeds, building both controllers cost approximately **10,167 actual sparse synaptic products** and **14,036 additional candidate-link evaluations** (not included in the plain synapse count); each bank additionally expends 72 charged probe actions. The 15.6 KB stores *two full trained contexts*, not four global synapses total. These counts do **not** establish lower wall-clock, energy, or memory cost than a well-wired conventional policy.

## Adversarial interpretation

1. **Experimenter-specified boundary.** The procedure explicitly knows *when* to adapt B and *when* to request a context selection. It never observes the actual motor sign in its selector, but this is not automatic context discovery or lifelong learning.
2. **Two separately trained policies rather than a unified cortical model.** Saving the old policy prevents overwriting by definition; the scientific question is whether reward evidence can retrieve it. The prior remains accessible as extra storage, not as synaptic memory in one network.
3. **Counterfactual simulator resets.** The selector probes both candidate policies from the same fresh development starting states. This is possible in the simulated body, costly in real environments, and unavailable without a reset or a predictive world model.
4. **Hand-designed sensory and reward channels.** The agent directly observes signed target-relative distance and receives progress reward. Neither is learned from pixels/audio; most natural tasks do not reveal similarly diagnostic rewards.
5. **Simple context discrimination.** Forward versus inverted motor direction is an easy binary contrast, especially with six trials and three action steps each. Contexts that are similar, noisy, delayed, novel, or more than two may defeat the selector.
6. **Fairness:** The bank controls `bank_random` and `bank_latest` have the same memory bytes, candidate checkpoints, probe tasks and charged probes. `single` uses only one checkpoint and 0 probes, so raw performance against `single` cannot support a compute- or memory-efficiency claim. `bank_oracle` knows the regime and is only a labeled upper bound.
7. **Negative primary finding.** A positive bootstrap interval can coexist with a non-significant exact paired sign-flip because many seeds have zero improvement against the lucky random selection. Do not select one favorable test after seeing the random outcomes.
8. **Neuroscience boundaries:** This implementation is neither recurrent spiking neurons nor hippocampal pattern separation, synaptic consolidation, autonomous change detection, or evidence for a biological learning algorithm. The existing macroscopic connectome remains unchanged.

## Decision and next falsifier

Keep the code as a clearly labeled experimental memory-retrieval **baseline**, with its negative primary criterion. For #65 and #114, remove externally signaled context boundaries and test a bounded online surprise/change detector; compare to a latest-policy, random-switching and fixed-two-slot baseline at **identical real environment-action budgets**. Use noisy, delayed, and overlapping contexts with no per-candidate simulator resets. For structural learning, address sparse-population feature preservation before making multimodal cognition claims. Future confirmatory evaluations require fresh holdout seeds and should not tune on seeds 401–410.