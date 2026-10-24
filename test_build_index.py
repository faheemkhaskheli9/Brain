"""Checks for build_index.py and run_code_blocks.py. Stdlib only.

Run: python test_build_index.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import build_index as b

ROOT = Path(__file__).parent


def test_frontmatter_lists_and_comments():
    meta = b.frontmatter("---\ntitle: T\ntags: [a, b]\nstatus: draft   # note\nsources:\n  - x\n---\n")
    assert meta == {"title": "T", "tags": ["a", "b"], "status": "draft", "sources": ["x"]}, meta


def test_check_meta_accepts_a_good_topic_and_names_each_problem():
    good = {"title": "T", "category": "anatomy", "status": "draft", "last_verified": "2026-10-17",
            "tags": ["a"], "use_cases": ["q"], "sources": ["s"]}
    assert b.check_meta("anatomy/t.md", good) == []
    bad = dict(good, category="function", status="done", last_verified="17/10/2026", sources=[])
    errs = " | ".join(b.check_meta("anatomy/t.md", bad))
    for part in ("category", "status", "last_verified", "empty sources"):
        assert part in errs, (part, errs)


def test_stale_warns_only_past_the_age_limit():
    from datetime import date
    today = date(2026, 10, 24)
    assert b.stale("a/t.md", {"last_verified": "2026-01-01"}, today) is not None
    assert b.stale("a/t.md", {"last_verified": "2026-10-24"}, today) is None
    assert b.stale("a/t.md", {"last_verified": "2026-10-01"}, today, max_age=10) is not None
    assert b.stale("a/t.md", {"last_verified": "bad"}, today) is None   # check_meta reports it


def test_slug_matches_github():
    assert b.slug("Jointed legs (?legs=joints)") == "jointed-legs-legsjoints"
    assert b.slug("Watch, Fast forward, Pause, Sound") == "watch-fast-forward-pause-sound"
    assert b.slug("Watch / Pause") == "watch--pause"
    assert b.anchors("# A\n## A\n```\n# not a heading\n```\n### `x` y\n") == {"a", "a-1", "x-y"}


def test_relative_links_files_anchors_and_code():
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        d = Path(tmp)
        (d / "a.md").write_text("# Top\n## Second part\n", encoding="utf-8")
        page = d / "b.md"
        page.write_text(
            "[ok](a.md) [ok](a.md#second-part) [ok](#here) [web](https://x.org/y.md)\n"
            "[gone](missing.md) [bad](a.md#nope)\n`[code](nothing.md)`\n```\n[fenced](nothing.md)\n```\n"
            "## Here\n", encoding="utf-8")
        errs = b.check_relative_links(page, page.read_text(encoding="utf-8"), {})
    assert len(errs) == 2, errs
    assert "broken link missing.md" in errs[0] and "broken anchor a.md#nope" in errs[1], errs


def test_downloaded_pdfs_are_not_required():
    page = ROOT / "research" / "papers.md"
    assert not any("pdfs/" in e for e in b.check_relative_links(page, "[p](pdfs/x.pdf)", {}))


def test_repo_builds_without_errors():
    r = subprocess.run([sys.executable, str(ROOT / "build_index.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_run_code_blocks_runs_only_named_files_and_reports_failures():
    with tempfile.TemporaryDirectory(dir=ROOT / "guides") as tmp:
        md = Path(tmp) / "t.md"
        md.write_text("```python\nprint('hi')\n```\n\n```python\nraise SystemExit('boom')\n```\n\n"
                      "```python\n# not run here: needs torch\nimport torch\n```\n", encoding="utf-8")
        r = subprocess.run([sys.executable, str(ROOT / "run_code_blocks.py"), str(md)],
                           capture_output=True, text=True)
    assert r.returncode == 1, r.stdout
    assert "block 1" in r.stdout and "FAIL" in r.stdout and "boom" in r.stdout, r.stdout
    assert "skip" in r.stdout and "1 of 2 blocks ran" in r.stdout, r.stdout


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
