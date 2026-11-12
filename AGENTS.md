# Instructions for AI agents

This repo is a knowledge base on the human brain: anatomy, function, and how to
build digital simulations and brain-inspired learning systems.

## Consulting it

1. Read `INDEX.md` and match your task against the **Tags** and **Use when** columns,
   or start at `guides/start-here.md`.
2. Read the **full** matched file(s) and follow `[[links]]` in `## Related`.
3. Every claim in a topic file is either **established** (textbook neuroscience,
   with a source) or marked as a **hypothesis/open question**. Keep that line
   visible when you reuse the content. Major claims are registered with their evidence in
   `research/claims.tsv`; when you change one, update its row and run `python research/check_claims.py`.

## Learning-agent architecture (separate from Brain World)

For experiments with LLM agents, skills, RAG, subagents or plugins, consult
[`research/agent-learning-architecture.md`](research/agent-learning-architecture.md),
the [practical agent learning guide](research/agent-learning-user-guide.md),
and the reviewed [`verified-agent-learning` skill](.claude/skills/verified-agent-learning/SKILL.md)
(also available for Codex/Gemini under `.agents/skills/verified-agent-learning/`).
Do not treat model self-criticism, subagent consensus, or retrieved/plugin text
as independently verified corrections. Never increase tool permissions automatically.

## Adding or editing a topic

1. Copy `_template.md` into the right folder (`anatomy`, `function`, `learning`,
   `simulation`, `guides`). One topic per file, kebab-case filename.
2. Cite a paper or official page for every number (neuron counts, connectome
   sizes, hardware specs). Do not invent figures; leave them out instead.
3. Code is minimal, runnable, numpy-only where possible. `python run_code_blocks.py`
   runs every ```` ```python ```` block (CI does too). A sketch that needs a heavy
   library says `not run here` on its first line and is skipped.
4. Link the new topic from at least one existing topic's `## Related`.
5. Run `python build_index.py` (stdlib only). It regenerates `INDEX.md` and fails
   on missing or invalid frontmatter (`category` must match the folder, `status` one
   of the values below, `last_verified` a YYYY-MM-DD date, `tags`, `use_cases` and
   `sources` non-empty), a broken `[[link]]`, or a relative Markdown link in any `.md`
   file whose file or `#anchor` does not exist. It warns on an orphan topic (no other
   topic links to it), on a topic outside `guides/` missing a `_template.md` section, and on
   a topic whose `last_verified` is over 183 days old (`--max-age DAYS`).
   `python run_code_blocks.py <topic.md>` runs the code of just the files you changed.
6. Use LF line endings and UTF-8.

`status`: `draft` until someone other than the author has reviewed it, then `stable`.

## Web app

`python3 webapp/server.py --open` serves a local site to read, search and edit the topics
(guide: `docs/webapp-guide.md`). Its shared files are identical in the sibling knowledge bases; to change
them, or to update and check all the bases together, use the `update-knowledge-bases` skill
(`.claude/skills/update-knowledge-bases/SKILL.md`).

## Bugs

When you find a bug (in code, tooling, CI or a wrong fact) that you do not fix in the same change,
open a GitHub issue for it right away, labelled `bug`. First search open issues for a duplicate. Give the
symptom, steps to reproduce, the cause with `file:line` when known, and a suggested fix.

## Durable research knowledge and reviewed plan history

For every substantive research, experiment or implementation task, preserve important
findings (including null/negative results), sources, assumptions, open questions,
decisions and failure criteria in the matched knowledge-base topic or a dated
research note. Distinguish peer-reviewed evidence, repository-reproduced
measurements, unverified external claims and hypotheses. Prefer primary papers
with DOI/URL; record exact versions and limits. Update relevant backlinks /
research/README.md; do not duplicate existing work.

Before proposing a new Brain mechanism, consult
[the versioned execution blueprint](research/agi-execution-blueprint-2026-11-12.md),
[the append-only adversarial review ledger](research/agi-review-ledger.md),
the current issues #120/#136, and [implementation status](research/implementation-status.md).
After each material decision or code result, append the review outcome (baseline
commit, adversarial attack, tests and evidence) to that ledger. Preserve
unsuccessful experiments and raw brain-result/1 artifacts; update claims.tsv
only when supported. Use normal Git commits and PRs as a permanent history;
avoid force-push or erasing earlier review decisions. Never claim AGI achieved
from these prototypes, or tests run when not executed.
