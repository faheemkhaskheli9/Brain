"""Claim-to-evidence register (#117): checks research/claims.tsv.

Each row is one major claim the repository makes, with where it is stated and what backs it:

    id        short unique name
    status    established   textbook or published finding: evidence is a source (DOI or URL)
              measured      a result of this repository: evidence is a brain-result/1 file
              hypothesis    proposed, not shown: evidence optional
              unsupported   stated somewhere but nothing in the repository backs it
    kind      biology       a fact about brains
              behaviour     what a model or agent was measured to do
              analogy       a model mechanism likened to a brain mechanism
              aspiration    a goal (e.g. human-level intelligence), never a result
    claim     the claim, one sentence
    where     the file that states it, and quote: text that must still appear in that file
              (whitespace and line breaks are ignored)
    evidence  DOI / URL, or a repository path to a result file
    commit    for measured: the commit the result file records
    check     for measured, optional: "arm=A [split=S] metric=M mean=V" -> the mean of M over the
              ok runs of A (in S) must round to V, at V's decimals
    reviewed  YYYY-MM-DD of the last check against the evidence

Errors (exit 1): a malformed row; established without a source; measured without a valid result
file, with another commit, or with a check that does not reproduce; analogy or aspiration marked
established or measured; a quote no longer in its file. Warnings: reviewed over --max-age days
ago (default 183), unsupported claims (listed so they get fixed or removed).
A cited source is only a pointer: the summary counts established claims as "cited", and only
measured claims whose numbers recompute from a result file as "reproduced".

    python research/check_claims.py [--max-age DAYS]
Stdlib only.
"""
import csv
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import result_schema as rs  # noqa: E402

CLAIMS = os.path.join(HERE, "claims.tsv")
COLUMNS = ["id", "status", "kind", "claim", "where", "quote", "evidence", "commit", "check", "reviewed"]
STATUSES = ("established", "measured", "hypothesis", "unsupported")
KINDS = ("biology", "behaviour", "analogy", "aspiration")
MAX_AGE = 183
SOURCE = re.compile(r"^(10\.\d{4,9}/\S+|https?://\S+)$")
CHECK = re.compile(r"^arm=(\S+)(?: split=(\S+))? metric=(\S+) mean=(-?\d+(?:\.(\d+))?)$")


def read(path=CLAIMS):
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    return rows


def recompute(record, arm, split, name):
    xs = [rs.metric(r["scores"], name) for r in record["runs"]
          if r["arm"] == arm and r.get("split") == split and r["status"] == "ok"]
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def check_row(row, today, max_age=MAX_AGE, root=ROOT):
    """Return (errors, warnings) for one row."""
    errs, warns = [], []
    if set(row) != set(COLUMNS) or None in row.values():
        return [f"columns must be exactly {', '.join(COLUMNS)}"], warns
    s, k = row["status"], row["kind"]
    if s not in STATUSES:
        errs.append(f"status {s!r}, expected one of {', '.join(STATUSES)}")
    if k not in KINDS:
        errs.append(f"kind {k!r}, expected one of {', '.join(KINDS)}")
    if not row["claim"].strip():
        errs.append("claim is empty")
    if k in ("analogy", "aspiration") and s in ("established", "measured"):
        errs.append(f"a {k} cannot be {s}: mark it hypothesis or unsupported")
    path = os.path.join(root, row["where"])
    if not row["where"] or not os.path.isfile(path):
        errs.append(f"where: {row['where']!r} is not a file")
    else:
        with open(path, encoding="utf-8") as fh:
            if not row["quote"] or " ".join(row["quote"].split()) not in " ".join(fh.read().split()):
                errs.append(f"quote not found in {row['where']}: {row['quote']!r}")
    ev = row["evidence"]
    if s == "established" and not SOURCE.match(ev):
        errs.append("established needs a source (DOI or URL) as evidence")
    if s == "measured":
        file = os.path.join(root, ev)
        if not ev.endswith(".json") or not os.path.isfile(file):
            errs.append(f"measured needs a result file as evidence, got {ev!r}")
        else:
            with open(file, encoding="utf-8") as fh:
                record = json.load(fh)
            bad = rs.validate(record)
            if bad:
                errs.append(f"{ev} is not a valid {rs.SCHEMA} file: {bad[0]}")
            elif row["commit"] != record["commit"]:
                errs.append(f"commit {row['commit']!r}, but {ev} records {record['commit']!r}")
            elif row["check"]:
                m = CHECK.match(row["check"])
                if not m:
                    errs.append(f"check {row['check']!r}: expected 'arm=A [split=S] metric=M mean=V'")
                else:
                    arm, split, name, want, dec = m.groups()
                    got = recompute(record, arm, split, name)
                    if got is None or abs(got - float(want)) > 0.5 * 10 ** -len(dec or "") + 1e-9:
                        errs.append(f"check: mean {name} of {arm}{' in ' + split if split else ''} is {got}, claim says {want}")
    if s != "measured" and row["check"]:
        errs.append("check is only for measured claims")
    try:
        age = (today - date.fromisoformat(row["reviewed"])).days
        if age > max_age:
            warns.append(f"last reviewed {row['reviewed']}, {age} days ago")
    except ValueError:
        errs.append(f"reviewed {row['reviewed']!r} is not a YYYY-MM-DD date")
    if s == "unsupported":
        warns.append(f"unsupported: no evidence in the repository yet (stated in {row['where']})")
    return errs, warns


def main(argv=()):
    argv = list(argv)
    max_age = int(argv[argv.index("--max-age") + 1]) if "--max-age" in argv else MAX_AGE
    rows, today, bad, seen = read(), date.today(), 0, set()
    counts = {}
    for i, row in enumerate(rows, start=2):
        errs, warns = check_row(row, today, max_age)
        if row.get("id") in seen:
            errs.append("duplicate id")
        seen.add(row.get("id"))
        for e in errs:
            print(f"claims.tsv:{i} {row.get('id')}: error: {e}")
        for w in warns:
            print(f"claims.tsv:{i} {row.get('id')}: warning: {w}")
        bad += bool(errs)
        if not errs:
            label = {"established": "cited", "measured": "reproduced" if row["check"] else "measured"}.get(row["status"], row["status"])
            counts[label] = counts.get(label, 0) + 1
    print(f"{len(rows)} claims: " + ", ".join(f"{n} {k}" for k, n in sorted(counts.items())) + (f", {bad} with errors" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
