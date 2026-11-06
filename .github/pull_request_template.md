## What changed and why

Related issue: #

## Verification

Commands run and results (or explain why a check does not apply):

- `ruff check .`
- `python build_index.py` (commit any updated `INDEX.md`)
- `python run_code_blocks.py`
- `python research/check_claims.py`
- Relevant Python/Node/browser tests for affected components:

## Research evidence (for learning, simulation, or scientific changes)

- **Hypothesis and prior baseline:**
- **Controls and ablations:**
- **Seeds, matched steps/compute budget, and fixed train/dev/test splits:**
- **Results:** link `brain-result/1` artifacts, run command and commit; include failed runs.
- **Retention, held-out generalization, and uncertainty:**
- **Limitations / negative results:**

For LLM-agent work, explicitly distinguish context/memory retrieval from model-weight
updates and use an independent verifier. Do not attribute LLM or plugin capabilities
to the backprop-free Brain World creature.

## Checklist

- [ ] Scoped change; checked the existing backlog and related PRs to avoid duplication.
- [ ] Scientific claims cite evidence; updated `research/claims.tsv` where applicable.
- [ ] No training/test leakage, unverifiable model self-grading, or hidden handcoded advantages.
- [ ] Updated or added regression tests and documented any skipped checks.
- [ ] Preserved Brain World save/load compatibility and backprop-free learning constraints (if applicable).
