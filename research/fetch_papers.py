"""Collect every paper the knowledge base cites into research/papers.md.

Two separate steps:
1. Extraction (offline, deterministic): read the `sources:` frontmatter and `## References`
   bullets of every topic and key each reference by its cited DOI, arXiv id, title or URL.
2. Enrichment (online, only when asked): look references up in OpenAlex (and Semantic Scholar
   for PDFs) and store what was found in research/papers.json, keyed by reference. The catalog
   is built from the extraction plus that file, so it never depends on the network.

    python research/fetch_papers.py            # rebuild papers.md offline from papers.json
    python research/fetch_papers.py --check    # offline: exit 1 if papers.md is out of date (CI)
    python research/fetch_papers.py --enrich   # online: look up references not in papers.json yet
    python research/fetch_papers.py --enrich --refresh   # online: look every reference up again
    python research/fetch_papers.py --enrich --pdf       # also download open-access PDFs

Every row says whether its reference was resolved, looked up and not found, or not looked up
yet. Stdlib only.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research"
PDFS = OUT / "pdfs"
CACHE = OUT / "papers.json"   # enrichment results, keyed by reference key; written only by --enrich
FOLDERS = ["anatomy", "function", "learning", "simulation", "guides"]
UA = {"User-Agent": "Mozilla/5.0 (Brain KB reference fetcher)"}

# DOIs may contain parentheses (Elsevier/SICI: 10.1016/0166-2236(89)90074-X); clean_doi drops an
# unbalanced closing one, as from a Markdown link around the URL.
DOI_RE = re.compile(r"(?:doi:\s*|doi\.org/)(10\.\d{4,9}/[^\s,;]+)", re.I)
ARXIV_RE = re.compile(r"arxiv(?:\.org/abs/|:)\s*(\d{4}\.\d{4,5})", re.I)
BIORXIV_RE = re.compile(r"bioRxiv\s+(\d{6,})", re.I)
URL_RE = re.compile(r"https?://[^\s)>\]]+")
TITLE_RE = re.compile(r'"([^"]{8,})"')
CITE_RE = re.compile(r"^(.+?)\s*\((\d{4})\)")


def clean_doi(d):
    d = d.rstrip(".]")
    while d.endswith(")") and d.count(")") > d.count("("):
        d = d[:-1].rstrip(".")
    return d.lower()


def looks_pdf(u):
    """A direct PDF link, not a DOI resolver or a repository landing page."""
    return "doi.org/" not in u and bool(re.search(r"\.pdf($|[?#])|/pdf(/|$|[?#])", u, re.I))


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def openalex(path):
    try:
        return json.loads(get("https://api.openalex.org/" + path))
    except Exception:
        return None


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def parse_refs():
    """Yield (topic_stem, text) for every reference line and source URL."""
    for folder in FOLDERS:
        for f in sorted((ROOT / folder).glob("*.md")):
            text = f.read_text(encoding="utf-8")
            fm = text.split("---", 2)[1] if text.startswith("---") else ""
            in_src = False
            for line in fm.splitlines():
                if line.startswith("sources:"):
                    in_src = True
                elif in_src and line.strip().startswith("- "):
                    yield f.stem, line.strip()[2:]
                elif in_src and line and not line.startswith(" "):
                    in_src = False
            m = re.search(r"^## References\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
            if m:
                for line in m.group(1).splitlines():
                    if line.strip().startswith("- "):
                        yield f.stem, line.strip()[2:]


def key_of(text):
    if m := DOI_RE.search(text):
        return "doi:" + clean_doi(m.group(1))
    if m := ARXIV_RE.search(text):
        return "arxiv:" + m.group(1)
    if m := BIORXIV_RE.search(text):
        return "doi:10.1101/" + m.group(1)
    if m := TITLE_RE.search(text):
        return "title:" + norm(m.group(1))
    if m := URL_RE.search(text):
        return "url:" + m.group(0).rstrip(".")
    if not CITE_RE.match(text) and (m := re.search(r"\*([^*]{4,})\*", text)):
        return "book:" + norm(m.group(1))
    return "book:" + norm(text)[:60]


def collect():
    refs = {}
    for topic, text in parse_refs():
        k = key_of(text)
        r = refs.setdefault(k, {"key": k, "cite": text, "topics": []})
        # prefer the full bibliographic line over a bare frontmatter URL
        if text.startswith("http") is False and r["cite"].startswith("http"):
            r["cite"] = text
        if topic not in r["topics"]:
            r["topics"].append(topic)
    # a bare doi.org URL in frontmatter and a full citation share a key. A bare URL that a
    # fuller citation elsewhere also gives is the same source: fold it into that citation.
    by_url = {}
    for r in refs.values():
        if not r["key"].startswith("url:"):
            for u in URL_RE.findall(r["cite"]):
                by_url.setdefault(u.rstrip(".)"), r)
    out = []
    for r in refs.values():
        twin = by_url.get(r["key"][4:].rstrip(".)")) if r["key"].startswith("url:") else None
        if twin is not None:
            twin["topics"] += [t for t in r["topics"] if t not in twin["topics"]]
            continue
        out.append(r)
    return out


def resolvable(r):
    """Whether enrichment looks this reference up. Books, bare URLs and cited web pages (a
    citation with its own URL) are taken as cited."""
    k = r["key"]
    return k.startswith(("doi:", "arxiv:")) or (k.startswith("title:") and not URL_RE.search(r["cite"]))


def lookup(r):
    """Online: what OpenAlex (and Semantic Scholar) know about r, as a cache entry."""
    tmp = {"key": r["key"], "cite": r["cite"]}
    resolve(tmp)
    if "pdf_urls" not in tmp:   # resolve sets it only when OpenAlex matched a work
        return {"found": False}
    return {"found": True, **{f: tmp.get(f) for f in ("title", "year", "doi", "oa_status")},
            "pdf_urls": tmp["pdf_urls"]}


def apply(r, entry):
    """Offline: copy a cache entry onto r and record its status."""
    if not resolvable(r):
        r["status"] = "-"
    elif entry is None:
        r["status"] = "not looked up"
    elif not entry.get("found"):
        r["status"] = "not found"
    else:
        r["status"] = "resolved"
        for f in ("title", "year", "doi", "oa_status", "pdf_urls"):
            if entry.get(f) is not None:
                r[f] = entry[f]


def resolve(r):
    k = r["key"]
    w = None
    if k.startswith("doi:"):
        w = openalex("works/doi:" + urllib.parse.quote(k[4:], safe="/"))
    elif k.startswith("arxiv:"):
        w = openalex("works/doi:10.48550/arxiv." + k[6:])
    elif k.startswith("title:") and not URL_RE.search(r["cite"]):
        # a cited web page (fact sheet, project site) names its own URL: a title search would
        # only find some other work with a similar title
        title = TITLE_RE.search(r["cite"]).group(1)
        res = openalex("works?per-page=5&search=" + urllib.parse.quote(title))
        for cand in (res or {}).get("results", []):
            ct = norm(cand.get("title") or "")
            if ct and (ct == k[6:] or ct.startswith(k[6:]) or k[6:].startswith(ct)):
                w = cand
                break
    if not w:
        return
    r["title"] = w.get("title")
    r["year"] = w.get("publication_year")
    if w.get("doi"):
        r["doi"] = w["doi"]
    r["oa_status"] = (w.get("open_access") or {}).get("oa_status")
    urls = [f"https://arxiv.org/pdf/{k[6:]}"] if k.startswith("arxiv:") else []   # the cited version first
    for loc in [w.get("best_oa_location")] + (w.get("locations") or []):
        if loc and loc.get("pdf_url") and looks_pdf(loc["pdf_url"]) and loc["pdf_url"] not in urls:
            urls.append(loc["pdf_url"])
    oa = (w.get("open_access") or {}).get("oa_url")
    if oa and looks_pdf(oa) and oa not in urls:
        urls.append(oa)
    # many publisher/PMC/bioRxiv URLs answer scripts with a bot challenge
    # (HTML, not PDF); those stay as links in the catalog.
    if r.get("doi"):
        try:
            s2 = json.loads(get("https://api.semanticscholar.org/graph/v1/paper/DOI:"
                                + r["doi"].split("doi.org/")[-1] + "?fields=openAccessPdf"))
            u = (s2.get("openAccessPdf") or {}).get("url")
            if u and looks_pdf(u) and u not in urls:
                urls.append(u)
        except Exception:
            pass
    r["pdf_urls"] = urls


def merge(refs):
    """Fold rows that turn out to be the same paper (same resolved DOI, or a
    short 'Author (year)' citation of a paper cited in full elsewhere)."""
    by_doi, out = {}, []
    for r in refs:
        d = r.get("doi")
        if d and d in by_doi:
            keep = by_doi[d]
            keep["topics"] += [t for t in r["topics"] if t not in keep["topics"]]
            if len(r["cite"]) > len(keep["cite"]) and not r["cite"].startswith("http"):
                keep["cite"] = r["cite"]
            continue
        if d:
            by_doi[d] = r
        out.append(r)
    full = {}
    for r in out:
        if m := CITE_RE.match(r["cite"]):
            full.setdefault((m.group(1).split()[0], m.group(2)), r)
    final = []
    for r in out:
        m = CITE_RE.match(r["cite"])
        twin = full.get((m.group(1).split()[0], m.group(2))) if m else None
        if twin is not None and twin is not r and not r.get("doi"):
            twin["topics"] += [t for t in r["topics"] if t not in twin["topics"]]
            continue
        final.append(r)
    return final


def slug(r):
    m = CITE_RE.match(r["cite"])
    author = norm(m.group(1).split()[0]) if m else "ref"
    year = (m.group(2) if m else r.get("year")) or ""
    words = norm(" ".join((r.get("title") or "").split()[:4]))[:30]
    return f"{author}-{year}-{words}".strip("-")


def download(r):
    urls = list(r.get("pdf_urls", []))
    if r["key"].startswith("arxiv:"):
        urls.insert(0, f"https://arxiv.org/pdf/{r['key'][6:]}")
    if r["key"].startswith("url:") and r["key"].endswith(".pdf"):
        urls.insert(0, r["key"][4:])
    dest = PDFS / (slug(r) + ".pdf")
    if dest.exists():
        r["pdf"] = dest
        return
    for u in urls:
        try:
            data = get(u, timeout=60)
        except Exception:
            continue
        if data[:5] == b"%PDF-":
            PDFS.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            r["pdf"] = dest
            r["pdf_src"] = u
            return
        time.sleep(0.5)


def link(r):
    # What the topic cites wins: its DOI, arXiv id or URL. OpenAlex's DOI is only a fallback
    # for a citation found by title, since OpenAlex may normalise a DOI into another one or
    # file an arXiv paper under a later copy's DOI.
    # Returns (url, cited): cited is False when the URL came from OpenAlex, not the topic.
    k = r["key"]
    if k.startswith("doi:"):
        return "https://doi.org/" + k[4:], True
    if k.startswith("arxiv:"):
        return "https://arxiv.org/abs/" + k[6:], True
    if k.startswith("url:"):
        return k[4:], True
    if m := URL_RE.search(r["cite"]):
        return m.group(0).rstrip(".)"), True
    return r.get("doi") or "", False


def md_url(u):
    return u.replace("(", "%28").replace(")", "%29")   # a bare ) would end the Markdown link


def catalog(refs):
    """The text of papers.md: a function of the topics and papers.json only, so a rebuild with no
    network gives the same file, and --check can compare it with the committed one."""
    refs = sorted(refs, key=lambda r: (r["cite"].lower(), r["key"]))
    count = {s: sum(1 for r in refs if r["status"] == s) for s in ("resolved", "not found", "not looked up")}
    n_pdf = sum(1 for r in refs if r.get("pdf_urls"))
    lines = [
        "# Papers cited by the knowledge base",
        "",
        "Generated by `python research/fetch_papers.py` from the topics and `research/papers.json` -",
        "do not edit by hand. `python research/fetch_papers.py --enrich` looks new references up online.",
        f"{len(refs)} references: {count['resolved']} resolved, {count['not found']} not found, "
        f"{count['not looked up']} not looked up yet, and {len(refs) - sum(count.values())} books, pages or",
        f"bare URLs taken as cited. {n_pdf} have a direct open-access PDF link.",
        "Annotated takeaways live in [guides/key-papers.md](../guides/key-papers.md).",
        "",
        "Link: the DOI, arXiv id or URL the topic cites; \"(OpenAlex)\" marks a DOI OpenAlex found for a",
        "citation that gave none.",
        "",
        "| Reference | Cited in | Link | Status | Open access | PDF |",
        "|---|---|---|---|---|---|",
    ]
    for r in refs:
        cite = r["cite"].replace("|", "/")
        topics = ", ".join(f"[{t}](../{find(t)})" for t in sorted(r["topics"]))
        url, cited = link(r)
        lk = (f"[link]({md_url(url)})" + ("" if cited else " (OpenAlex)")) if url else "book / no link"
        oa = r.get("oa_status") or "-"
        pdf = f"[pdf]({md_url(r['pdf_urls'][0])})" if r.get("pdf_urls") else ""
        lines.append(f"| {cite} | {topics} | {lk} | {r['status']} | {oa} | {pdf} |")
    return "\n".join(lines) + "\n"


def find(stem):
    for folder in FOLDERS:
        if (ROOT / folder / f"{stem}.md").exists():
            return f"{folder}/{stem}.md"
    return stem


def load_cache():
    return json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}


def build(cache):
    refs = collect()
    for r in refs:
        apply(r, cache.get(r["key"]))
    return merge(refs)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = set(sys.argv[1:])
    cache = load_cache()
    if "--check" in args:   # offline: is papers.md what the topics and papers.json give?
        want = catalog(build(cache))
        have = (OUT / "papers.md").read_text(encoding="utf-8") if (OUT / "papers.md").exists() else ""
        if want != have:
            new = sum(1 for r in collect() if resolvable(r) and r["key"] not in cache)
            print("research/papers.md is out of date: run python research/fetch_papers.py"
                  + (f" (and --enrich: {new} references are not in papers.json)" if new else ""))
            sys.exit(1)
        print("research/papers.md is current")
        return
    if "--enrich" in args:   # online
        todo = [r for r in collect() if resolvable(r) and ("--refresh" in args or r["key"] not in cache)]
        for i, r in enumerate(todo, 1):
            cache[r["key"]] = lookup(r)
            print(f"[{i}/{len(todo)}] {'found    ' if cache[r['key']]['found'] else 'not found'} {r['cite'][:70]}")
            time.sleep(0.2)  # polite to OpenAlex
        live = {r["key"] for r in collect()}
        cache = {k: v for k, v in sorted(cache.items()) if k in live}   # drop references no topic cites
        CACHE.write_text(json.dumps(cache, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
                         encoding="utf-8", newline="\n")
    refs = build(cache)
    if "--pdf" in args:
        for r in refs:
            download(r)
    (OUT / "papers.md").write_text(catalog(refs), encoding="utf-8", newline="\n")
    st = {s: sum(1 for r in refs if r["status"] == s) for s in ("resolved", "not found", "not looked up")}
    print(f"{len(refs)} references ({st['resolved']} resolved, {st['not found']} not found, "
          f"{st['not looked up']} not looked up) -> research/papers.md")


if __name__ == "__main__":
    main()
