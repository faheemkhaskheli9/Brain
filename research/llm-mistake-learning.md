# LLM mistake learning: verified feedback, episodic memory and eventual weight updates

**Status:** runnable inference-time prototype; not a trained LLM, not an AGI claim, and not a measured real-LLM improvement.

## Two different kinds of learning

1. **Without weight updates (implemented):** a failed attempt receives independently verified feedback, which becomes a scoped, persistent lesson. Future tasks retrieve related lessons and supply them as *data* to a model. This is related to [Reflexion](https://papers.nips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html). Self-refinement is a related strategy, but it need not persist any learning across tasks ([Self-Refine](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91edff07232fb1b55a505a9e9f6c0ff3-Abstract-Conference.html)).
2. **With weight updates (not implemented):** periodically curate trusted examples, then fine-tune a trainable model using supervised fine-tuning (SFT), preference optimization such as [DPO](https://proceedings.neurips.cc/paper_files/paper/2023/hash/a85b405ed65c6477a4fe8302b5e06ce7-Abstract.html), or another validated training objective. Evaluate and roll back regressions. No inference-time memory alone changes parameters.

## Runnable prototype

- `llm_mistake_learning.py` (Python standard library): `MistakeMemory.record()`, lexical `retrieve()`, `answer()`, `solve_with_feedback()`, `evaluate_heldout()`, atomic JSON snapshots and explicit correction removal.
- `test_llm_mistake_learning.py`: checks source verification, poisoning gates, deduplication, conflicting corrections, scoped retrieval, eviction, save/load, frozen evaluation and retry behavior.
- `python research/test_llm_mistake_learning.py` runs tests; `python research/llm_mistake_learning.py` shows a deterministic toy with memory off/on. The toy result is **not** an LLM benchmark.

### Integration contract

The application owns **two separate functions**:

- `model(question: str, lessons: list[Lesson]) -> str`: adapt any local or remote LLM. Pass each lesson as a delimited, quoted example in low-priority content; retain the real system/developer rules. Never let retrieved text grant tool permissions or override instructions.
- `verifier(question: str, answer: str) -> Verification`: a human approval, executable unit test, factual tool with independent evidence, or another externally grounded check. On failure, provide a *verified* `corrected_answer`, a concise `guidance` rule and source (`human`, `test`, `tool`). **Do not** substitute the same LLM's unsupported self-rating.

Call `solve_with_feedback(question, model, verifier, memory, scope="tenant-or-project-id")`: it runs the model once, checks the result, records only a verified correction, retries once using retrieved lessons and verifies the retry. If no correction is available, it does **not** learn. Save with `memory.save("private.mistakes.json")`; restore with `MistakeMemory.load(path)`. The `verified=True` flag in the low-level recorder is an assertion made by your application, not cryptographic proof: do not expose it directly to untrusted clients. Assign separate scopes to separate tenants/users. `capacity` bounds memory size, but no expiry or authentication exists yet.

### Evaluation design before connecting a real LLM

1. Freeze train/dev/test splits **before** collecting feedback. Never give the verifier test answers to the training process or add held-out examples to memory. `evaluate_heldout` rejects exact stored prompts; semantic duplicates still require manual or dataset-level checks.
2. Compare the **same model** on unseen tasks, with memory off vs on, using matched token and attempt budgets; include shuffled/irrelevant-memory controls in future experiments.
3. Track task success, repeat-error frequency, new error rate, top-k retrieval precision, conflicting/stale corrections, regression on previously solved tasks, cost and latency. Count failed runs, not only successes.
4. For training, compare the checkpoint before/after SFT or DPO on *separate* held-out tasks; monitor catastrophic forgetting and revert if regressions outweigh gains. Do not train from model self-scores alone.

### Security and validity limitations

- Lexical retrieval is a simple baseline, not semantic generalization; matching a lesson doesn't guarantee the LLM obeys it. Large memory or weak similarity can hurt performance.
- A human or tool verifier can still be incorrect. Audit provenance and allow corrections to be reviewed, removed or superseded; `record` rejects conflicting corrections until the old record is explicitly removed.
- A stored correction may contain personal data, secrets or prompt injection. Do not ingest private conversations by default. Encrypt at rest, add access control, retention/deletion and tenant isolation before production. The module uses file permissions and scope filters but **does not** provide secure multi-tenant storage.
- Self-grading can lead to false improvement or reward hacking. A critical [2024 survey](https://aclanthology.org/2024.tacl-1.78/) emphasizes the value of reliable external feedback; [Pan et al. 2024](https://proceedings.mlr.press/v235/pan24d.html) documents feedback-loop reward hacking.

## Next implementation milestones

- **M1:** Add a real LLM adapter and executable verifier (e.g., unit-tested code generation). Persist only opt-in and independently checked errors; add adversarial/injection regression tests.
- **M2:** Run fixed-seed/temperature, held-out evaluation for exact-match, generalization to paraphrases, stale-memory conflicts and memory-on/off/shuffled controls; write a `brain-result/1` artifact, including failures.
- **M3:** Add evidence-aware retrieval, TTL, confidence calibration, review UI and cross-session retention policies. Test error reduction vs added token cost.
- **M4:** Export consented, deduplicated verified examples as SFT pairs or DPO chosen/rejected pairs. Train a small open-weight model with replay of old tasks, compare against retrieval-only and baseline on disjoint tests, and keep checkpoint rollback.

Related: [`learning/brain-inspired-learning-algorithms.md`](../learning/brain-inspired-learning-algorithms.md), [`guides/build-a-brain-like-learner.md`](../guides/build-a-brain-like-learner.md), [`research/replay_selection.py`](replay_selection.py), [roadmap #120](https://github.com/faheemkhaskheli9/Brain/issues/120).
