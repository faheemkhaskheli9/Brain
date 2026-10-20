"""Regenerate INDEX.md from topic frontmatter and check the links between files.

Run after adding or editing a topic:  python build_index.py
Stdlib only. Exits 1 on:
  - missing or invalid frontmatter (title; category matching the folder; status draft,
    stable or needs-review; last_verified as YYYY-MM-DD; non-empty tags, use_cases, sources),
  - a broken [[link]] in a topic,
  - a relative Markdown link ([text](../path.md#anchor)) in any .md file whose file or
    heading anchor does not exist.
Warns (exit 0) on an orphan topic (no other topic [[links]] to it) and on a topic outside
guides/ that lacks a _template.md section.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
ORDER = ("guides", "anatomy", "function", "learning", "simulation")
SKIP = {"README.md", "AGENTS.md", "INDEX.md", "_template.md", "LICENSE-CONTENT.md",
        "CONTRIBUTING.md", "SECURITY.md"}
STATUSES = {"draft", "stable", "needs-review"}
REQUIRED_LISTS = ("tags", "use_cases", "sources")
# Sections every topic outside guides/ has (from _template.md). "Code" is optional.
SECTIONS = ("Summary", "How it works", "Relevance to building brain-like AI",
            "Open questions", "Related", "References")
# Relative links into these folders point at files that scripts download and git ignores.
GENERATED = ("research/pdfs/",)


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---", text.replace("\r\n", "\n"), re.S)
    if not m:
        return None
    meta, key = {}, None
    for line in m.group(1).splitlines():
        if line.startswith("  - ") and key:
            meta.setdefault(key, []).append(line[4:].strip())
        elif ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            key, val = key.strip(), val.split("#")[0].strip()
            if val.startswith("["):
                meta[key] = [v.strip() for v in val.strip("[]").split(",") if v.strip()]
            elif val:
                meta[key] = val
    return meta


def check_meta(rel, meta):
    """Frontmatter problems in one topic, as error strings."""
    errors, folder = [], rel.split("/")[0]
    if meta.get("category") != folder:
        errors.append(f"category {meta.get('category')!r} is not the folder {folder!r}: {rel}")
    if meta.get("status") not in STATUSES:
        errors.append(f"status {meta.get('status')!r} is not one of {sorted(STATUSES)}: {rel}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(meta.get("last_verified", ""))):
        errors.append(f"last_verified {meta.get('last_verified')!r} is not YYYY-MM-DD: {rel}")
    errors += [f"empty {k}: {rel}" for k in REQUIRED_LISTS if not isinstance(meta.get(k), list) or not meta[k]]
    return errors


def strip_fences(text):
    return re.sub(r"^(```|~~~).*?^\1", "", text, flags=re.S | re.M)


def strip_code(text):
    """Text with fenced code blocks and inline code removed, so examples are not checked as links."""
    return re.sub(r"`[^`\n]*`", "", strip_fences(text))


def slug(heading):
    """GitHub's heading anchor: lowercase, punctuation dropped, spaces to hyphens."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def anchors(text):
    seen, out = {}, set()
    for h in re.findall(r"^#{1,6} +(.+?) *#*$", strip_fences(text), re.M):
        s = slug(h.replace("`", ""))
        n = seen.get(s, 0)
        seen[s] = n + 1
        out.add(s if n == 0 else f"{s}-{n}")
    return out


def check_relative_links(path, text, cache):
    """Broken relative Markdown links in one file, as error strings."""
    errors, rel = [], path.relative_to(ROOT).as_posix()
    for url in re.findall(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)", strip_code(text)):
        if re.match(r"[a-zA-Z][\w+.-]*:", url) or url.startswith("//"):
            continue  # http:, mailto:, ...
        target, _, anchor = url.partition("#")
        dest = (path.parent / target).resolve() if target else path.resolve()
        try:
            dest_rel = dest.relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            errors.append(f"link outside the repo {url} in {rel}")
            continue
        if dest_rel.startswith(GENERATED):
            continue
        if not dest.exists():
            errors.append(f"broken link {url} in {rel}")
        elif anchor and dest.suffix == ".md":
            if dest not in cache:
                cache[dest] = anchors(dest.read_text(encoding="utf-8"))
            if anchor.lower() not in cache[dest]:
                errors.append(f"broken anchor {url} in {rel}")
    return errors


def main():
    topics, errors, warnings = {}, [], []
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("."):
            continue
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        errors += check_relative_links(path, text, {})
        if path.name in SKIP or rel.startswith(("research/", "docs/", "game/", "webapp/")):
            continue
        meta = frontmatter(text)
        if not meta or "title" not in meta:
            errors.append(f"missing frontmatter: {rel}")
            continue
        errors += check_meta(rel, meta)
        prose = strip_code(text)
        if path.stem in topics:  # [[links]] resolve by filename, so stems must be unique
            errors.append(f"duplicate topic name {path.stem}: {topics[path.stem][0]} and {rel}")
        topics[path.stem] = (rel, meta, re.findall(r"\[\[([^\]|#]+)", prose))
        if not rel.startswith("guides/"):
            heads = set(re.findall(r"^## +(.+?) *$", prose, re.M))
            missing = [s for s in SECTIONS if s not in heads]
            if missing:
                warnings.append(f"missing section(s) {', '.join(missing)}: {rel}")

    linked = set()
    for name, (rel, _, links) in topics.items():
        errors += [f"broken link [[{l}]] in {rel}" for l in links if l.strip() not in topics]
        linked |= {l.strip() for l in links if l.strip() != name}
    warnings += [f"orphan topic (no other topic links to it): {rel}"
                 for name, (rel, _, _) in topics.items() if name not in linked and name != "start-here"]

    lines = ["# Index", "", "Generated by `python build_index.py` - do not edit by hand.",
             f"{len(topics)} topics. Start at [guides/start-here.md](guides/start-here.md).", ""]
    for folder in ORDER:
        rows = [t for t in topics.values() if t[0].startswith(folder + "/")]
        if not rows:
            continue
        lines += [f"## {folder}", "", "| Topic | Tags | Use when | Status |", "|---|---|---|---|"]
        for rel, meta, _ in sorted(rows, key=lambda t: t[1]["title"]):
            lines.append(f"| [{meta['title']}]({rel}) | {', '.join(meta.get('tags', []))} "
                         f"| {'; '.join(meta.get('use_cases', []))} | {meta.get('status', '')} |")
        lines.append("")
    (ROOT / "INDEX.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")

    for e in errors:
        print(e)
    for w in warnings:
        print(f"warning: {w}")
    print(f"INDEX.md: {len(topics)} topics, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
