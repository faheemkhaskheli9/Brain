# research/

| Path | What |
|---|---|
| [papers.md](papers.md) | Every reference cited by the topic files: citation, which topics cite it, DOI/link, open-access status, PDF link. Generated. |
| [fetch_papers.py](fetch_papers.py) | Regenerates `papers.md` and downloads open-access PDFs. Stdlib only. |
| `pdfs/` | Downloaded open-access PDFs. Git-ignored (publisher copyright); run the script to fetch them. |

```
python research/fetch_papers.py            # resolve all references + download PDFs
python research/fetch_papers.py --no-pdf   # refresh the catalog only
```

Re-run after adding references to a topic. It resolves each reference through
OpenAlex (DOI, arXiv id, or exact title) and tries the open-access PDF URLs
OpenAlex and Semantic Scholar report. Publishers that answer scripts with a bot
check (eLife, bioRxiv, PMC, J Neurosci) stay as `oa` links: open them in a
browser. Closed-access papers are listed with their DOI only.

The per-paper findings, grouped by theme, are in
[guides/key-papers.md](../guides/key-papers.md).

## Audit (2026-10-11) in brief
An external audit of the repo recommended, before adding more topics: CI, a
license, `pyproject.toml`, community files, headless level-winnability tests,
read-only CI permissions, unique topic names in `build_index.py`, atomic save
files, independent review of the `draft` topics, and a per-model scorecard
against published data. All of these have landed except two: splitting
`game/levels.py` into a pure level engine plus Tk UI, and the topic review
(issue #21). Its evaluation advice now lives in
[simulation/evaluating-brain-models.md](../simulation/evaluating-brain-models.md).
The full report is in git history (`git show 033e79a:research/deep-research-report.md`).
