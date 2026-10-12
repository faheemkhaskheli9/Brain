"""Verify the sources of learning-algorithm-hypotheses.md and fetch the papers.

Reads research/learning-algorithm-sources.tsv (ids, first author, year, title,
and an optional url for sources checked by hand), looks each title up in
Crossref (Semantic Scholar as fallback), checks that title, first author and
year match, downloads an open-access PDF when one exists, and writes:

- research/learning-algorithm-sources.md   catalog with verdict + official link
- research/pdfs/learning-algorithm/        PDFs and sources.json (abstracts), git-ignored
- links in the Source column of learning-algorithm-hypotheses.md

    python research/verify_sources.py            # verify + download
    python research/verify_sources.py --no-pdf   # verify only

Stdlib only. Results are cached in sources.json; verified rows and existing
PDFs are skipped on re-runs (delete the json to re-check everything).
"""
import csv
import difflib
import html
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_papers import get, norm  # noqa: E402

OUT = Path(__file__).resolve().parent
PDFS = OUT / "pdfs" / "learning-algorithm"
CACHE = PDFS / "sources.json"
HYP = OUT / "learning-algorithm-hypotheses.md"
S2 = "https://api.semanticscholar.org/graph/v1/paper/"
LINK_RE = re.compile(r"(\[[^\]]*\]\([^)\s]*\))")
S2_FIELDS ="title,authors,year,venue,externalIds,openAccessPdf,abstract,url"


def fetch_json(url):
    """GET with backoff: a 429 must not read as 'not found'. None on 404."""
    for wait in (0, 3, 10, 30, 60):
        time.sleep(wait)
        try:
            return json.loads(get(url))
        except Exception as e:
            if getattr(e, "code", None) == 404:
                return None
            err = e
    print(f"  giving up on {url[:90]}: {err}")
    return None


def title_sim(a, b):
    a, b = norm(a), norm(b)
    if a and b and (a.startswith(b) or b.startswith(a)):
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def from_crossref(it):
    doi = it.get("DOI", "")
    return {"title": html.unescape((it.get("title") or [""])[0]),
            "authors": [" ".join(filter(None, (a.get("given"), a.get("family") or a.get("name"))))
                        for a in it.get("author") or []],
            "year": ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0],
            "venue": html.unescape((it.get("container-title") or [""])[0]),
            "link": f"https://doi.org/{doi}" if doi else it.get("URL", ""),
            "doi": doi,
            "abstract": re.sub(r"<[^>]+>", "", it.get("abstract") or "").strip()}


def from_s2(p):
    ext = p.get("externalIds") or {}
    doi = ext.get("DOI", "")
    link = (f"https://doi.org/{doi}" if doi else
            f"https://arxiv.org/abs/{ext['ArXiv']}" if ext.get("ArXiv") else p.get("url", ""))
    return {"title": p.get("title") or "", "authors": [a["name"] for a in p.get("authors") or []],
            "year": p.get("year"), "venue": p.get("venue") or "", "link": link, "doi": doi,
            "abstract": p.get("abstract") or ""}


def score(row, rec):
    s = title_sim(row["title"], rec["title"])
    if norm(row["author"]) in norm(" ".join(rec["authors"])):
        s += 0.5
    if rec["year"] and abs(rec["year"] - int(row["year"])) <= 1:
        s += 0.25
    return s


def lookup(row):
    q = urllib.parse.quote(f"{row['title']} {row['author']} {row['year']}")
    cands = [from_crossref(it) for it in ((fetch_json(
        f"https://api.crossref.org/works?rows=5&query.bibliographic={q}") or {})
        .get("message") or {}).get("items", [])]
    best = max(cands, key=lambda c: score(row, c), default=None)
    if not best or score(row, best) < 1.6:  # arXiv/NeurIPS papers often lack a DOI
        res = fetch_json(f"{S2}search?limit=5&fields={S2_FIELDS}&query="
                         + urllib.parse.quote(row["title"])) or {}
        cands += [from_s2(p) for p in res.get("data") or []]
        best = max(cands, key=lambda c: score(row, c), default=None)
    return best


def check(row, rec):
    if not rec:
        return "not found", ""
    notes = []
    if title_sim(row["title"], rec["title"]) < 0.9:
        notes.append(f"title differs: {rec['title']}")
    names = rec["authors"]
    if not names or norm(row["author"]) not in norm(names[0]):
        notes.append("first author: " + (names[0] if names else "none"))
    if rec["year"] != int(row["year"]):
        notes.append(f"year {rec['year']}")
    if any(n.startswith(("title", "first")) for n in notes) or (
            rec["year"] and abs(rec["year"] - int(row["year"])) > 1):
        return "check", "; ".join(notes)
    return "verified", "; ".join(notes)


def oa_info(rec):
    """Open-access PDF URLs (+ abstract if missing) from Semantic Scholar."""
    lk = rec.get("link", "")
    urls = []
    if m := re.search(r"proceedings\.mlr\.press/(v\d+)/(\w+)\.html$", lk):
        urls.append(f"https://proceedings.mlr.press/{m[1]}/{m[2]}/{m[2]}.pdf")
    if "openaccess.thecvf.com" in lk:
        urls.append(lk.replace("/html/", "/papers/").replace(".html", ".pdf"))
    doi = rec.get("doi") or lk.split("doi.org/")[-1]
    arx = re.search(r"arxiv\.org/abs/(.+)$", lk)
    if arx:
        urls.append(f"https://arxiv.org/pdf/{arx.group(1)}")
    key = f"DOI:{doi}" if "/" in doi else f"ARXIV:{arx.group(1)}" if arx else ""
    if not key:
        return urls, ""
    p = fetch_json(f"{S2}{key}?fields=openAccessPdf,externalIds,abstract") or {}
    u = (p.get("openAccessPdf") or {}).get("url")
    a = (p.get("externalIds") or {}).get("ArXiv")
    for v in (a and f"https://arxiv.org/pdf/{a}", u):
        if v and v not in urls:
            urls.append(v)
    return urls, p.get("abstract") or ""


def slug(row):
    words = norm(" ".join(row["title"].split()[:4]))[:30]
    return f"{norm(row['author'])}-{row['year']}-{words}"


def download(row, urls):
    dest = PDFS / (slug(row) + ".pdf")
    if dest.exists():
        return dest
    for u in urls:
        try:
            data = get(u, timeout=60)
        except Exception:
            continue
        if data[:5] == b"%PDF-":
            dest.write_bytes(data)
            return dest
        time.sleep(0.5)
    return None


def write_catalog(rows, cache):
    recs = [cache[slug(r)] for r in rows]
    n_ok = sum(c["verdict"] == "verified" for c in recs)
    n_pdf = sum(bool(c.get("pdf")) for c in recs)
    lines = [
        "# Sources of the learning-algorithm hypotheses",
        "",
        "Generated by `python research/verify_sources.py` from",
        "[learning-algorithm-sources.tsv](learning-algorithm-sources.tsv). Do not edit by hand:",
        "fix the TSV and re-run.",
        "",
        f"{len(rows)} sources: {n_ok} verified (title, first author and year within one",
        f"matched a Crossref, Semantic Scholar or OpenAlex record, or checked by hand),",
        f"{len(rows) - n_ok} still to check. {n_pdf} open-access PDFs saved under",
        "`research/pdfs/learning-algorithm/` (git-ignored; re-run to fetch).",
        "Methods, experiments and results per paper are in",
        "[learning-algorithm-notes/](learning-algorithm-notes/README.md).",
        "",
        "| Hypotheses | Source | Venue | Verdict | Link | PDF |",
        "|---|---|---|---|---|---|",
    ]
    for r, c in zip(rows, recs):
        cite = f"{r['author']} {r['year']}, *{c['title'] or r['title']}*".replace("|", "/")
        verdict = c["verdict"] + (f" ({c['note']})" if c["note"] else "")
        lk = f"[link]({urllib.parse.quote(c['link'], safe=':/?=&%#~-_.')})" if c["link"] else ""
        pdf = f"[pdf](pdfs/learning-algorithm/{c['pdf']})" if c.get("pdf") else (
            f"[oa]({c['pdf_urls'][0]})" if c.get("pdf_urls") else "")
        lines.append(f"| {r['ids'].replace(',', ', ')} | {cite} | {c['venue']} | "
                     f"{verdict.replace('|', '/')} | {lk} | {pdf} |")
    (OUT / "learning-algorithm-sources.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return n_ok, n_pdf


def link_hypotheses(rows, cache):
    """Wrap each 'Author ... year' citation in the Source column in its link."""
    text = HYP.read_bytes().decode("utf-8")
    out = []
    for line in text.split("\n"):
        m = re.match(r"\| (H\d{3}) \| (.*?) \| (.*?) \| (.*)$", line)
        if m:
            hid, src = m.group(1), m.group(3)
            for r in rows:
                c = cache[slug(r)]
                if hid not in r["ids"].split(",") or c["verdict"] != "verified":
                    continue
                pat = re.compile(r"(?<!\w)(" + re.escape(r["author"]) + r"[^;|\[\]]*?"
                                 + r["year"] + r")(?!\d)")
                url = urllib.parse.quote(c["link"], safe=":/?=&%#~-_.")  # DOIs with ();<>
                parts = LINK_RE.split(src)  # odd parts are existing links: leave alone
                for j in range(0, len(parts), 2):
                    new = pat.sub(lambda mm: f"[{mm.group(1)}]({url})", parts[j], count=1)
                    if new != parts[j]:
                        parts[j] = new
                        break
                src = "".join(parts)
            line = f"| {hid} | {m.group(2)} | {src} | {m.group(4)}"
        out.append(line)
    HYP.write_bytes("\n".join(out).encode("utf-8"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    with open(OUT / "learning-algorithm-sources.tsv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    PDFS.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    for i, r in enumerate(rows, 1):
        k = slug(r)
        c = cache.get(k)
        if not r.get("url") and (not c or c["verdict"] != "verified"):
            rec = lookup(r) or {}
            verdict, note = check(r, rec or None)
            c = {"title": rec.get("title", ""), "authors": rec.get("authors", []),
                 "venue": rec.get("venue", ""), "link": rec.get("link", ""),
                 "verdict": verdict, "note": note, "abstract": rec.get("abstract", "")}
            time.sleep(1)  # Semantic Scholar's shared pool is ~1 request/s
        if r.get("url"):  # not indexed (or matched wrongly): checked by hand
            if not c or title_sim(c["title"], r["title"]) < 0.9:  # drop a wrong match
                c = {"title": r["title"], "authors": [], "venue": "", "abstract": ""}
            c.update(verdict="verified", note="checked by hand", link=r["url"])
        c.update(ids=r["ids"], author=r["author"], year=r["year"])
        if "--no-pdf" not in sys.argv and c["verdict"] == "verified" and not c.get("pdf"):
            if not c.get("pdf_urls"):  # empty also when Semantic Scholar throttled
                c["pdf_urls"], abs2 = oa_info(c)
                c["abstract"] = c["abstract"] or abs2
                time.sleep(1)
            p = download(r, c["pdf_urls"])
            c["pdf"] = p.name if p else ""
        cache[k] = c
        CACHE.write_text(json.dumps(cache, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"[{i}/{len(rows)}] {c['verdict']:9} {'PDF' if c.get('pdf') else '   '} "
              f"{r['author']} {r['year']} {c['note']}", flush=True)
    n_ok, n_pdf = write_catalog(rows, cache)
    link_hypotheses(rows, cache)
    print(f"{len(rows)} sources, {n_ok} verified, {n_pdf} PDFs")


if __name__ == "__main__":
    main()
