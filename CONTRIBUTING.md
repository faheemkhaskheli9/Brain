# Contributing

Corrections are the most useful contribution: a number that does not match its
source, a hypothesis labelled as established, or a broken code block. Open a
**Science correction** issue, or send a pull request with the fix and the source.

## Adding or editing a topic

The rules are the same for people and AI agents and live in [AGENTS.md](AGENTS.md):
one topic per file from `_template.md`, a source for every number, **established**
vs **hypothesis** kept visible, runnable numpy-only code, LF line endings.

## Reviewing a draft

A topic moves from `status: draft` to `stable` once someone other than its author
has reviewed it. Pick an unticked topic in issue #21, check every number against its
cited source, check the established/hypothesis labels, and run its code. Send the
status change as a pull request and list what you checked.

## Before you open a pull request

```
pip install . ruff
ruff check .
python build_index.py          # regenerates INDEX.md, fails on a broken [[link]]
python run_code_blocks.py      # runs every python block in the topics
python game/test_sim.py        # if you touched game/
python game/eval.py            # if you touched a model in game/sim.py
```

CI runs the same checks, plus `game/test_levels.py` under xvfb.

By contributing you agree that code is licensed Apache-2.0 and prose CC BY 4.0
(see the README).
