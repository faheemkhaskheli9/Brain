# research/

| Path | What |
|---|---|
| [papers.md](papers.md) | Every reference cited by the topic files: citation, which topics cite it, DOI/link, open-access status, PDF link. Generated. |
| [fetch_papers.py](fetch_papers.py) | Regenerates `papers.md` and downloads open-access PDFs. Stdlib only. |
| `pdfs/` | Downloaded open-access PDFs. Git-ignored (publisher copyright); run the script to fetch them. |
| [deep-research-report.md](deep-research-report.md) | External audit of this repo (2026-10-11): engineering gaps and a prioritised roadmap. |

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

## Audit report in brief
`deep-research-report.md` recommends, before adding more topics: CI (ruff,
pytest, index check), a license (Apache-2.0 code + CC BY 4.0 prose suggested),
`pyproject.toml`, headless level-winnability tests, splitting `game/levels.py`
into a pure level engine plus Tk UI, independent review of the `draft` topics,
and a per-model brain-match scorecard scored against published data
(e.g. Bi & Poo 1998 for STDP, Schultz 1997 for TD). Check the repo and issues
for what has since landed before acting on it.
