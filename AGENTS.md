# Instructions for AI agents

This repo is a knowledge base on the human brain: anatomy, function, and how to
build digital simulations and brain-inspired learning systems.

## Consulting it

1. Read `INDEX.md` and match your task against the **Tags** and **Use when** columns,
   or start at `guides/start-here.md`.
2. Read the **full** matched file(s) and follow `[[links]]` in `## Related`.
3. Every claim in a topic file is either **established** (textbook neuroscience,
   with a source) or marked as a **hypothesis/open question**. Keep that line
   visible when you reuse the content.

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
   on missing frontmatter or a broken `[[link]]`.
6. Use LF line endings and UTF-8.

`status`: `draft` until someone other than the author has reviewed it, then `stable`.
