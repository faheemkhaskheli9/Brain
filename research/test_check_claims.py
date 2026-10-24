"""Tests for the claim-to-evidence register (#117). Stdlib only.

    python research/test_check_claims.py
"""
import json
import os
import sys
import tempfile
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_claims as cc  # noqa: E402
import result_schema as rs  # noqa: E402

TODAY = date(2026, 10, 24)


def setup(root):
    with open(os.path.join(root, "topic.md"), "w", encoding="utf-8") as fh:
        fh.write("The arm scores\n0.75 on average.\n")
    runs = [{"arm": "a", "seed": s, "status": "ok", "scores": {"x": x}} for s, x in ((1, 0.5), (2, 1.0))]
    runs.append({"arm": "a", "seed": 3, "status": "error", "reason": "crash", "scores": {}})
    with open(os.path.join(root, "r.json"), "w", encoding="utf-8") as fh:
        json.dump(rs.make_result("t", "t", {}, {}, {"x": "higher"}, runs, commit="abc1234"), fh)


def row(**kw):
    r = {"id": "c", "status": "measured", "kind": "behaviour", "claim": "The arm scores 0.75.", "where": "topic.md",
         "quote": "scores 0.75", "evidence": "r.json", "commit": "abc1234", "check": "arm=a metric=x mean=0.75",
         "reviewed": "2026-10-01"}
    return {**r, **kw}


def errors(root, **kw):
    return cc.check_row(row(**kw), TODAY, root=root)[0]


def main():
    with tempfile.TemporaryDirectory() as root:
        setup(root)
        # A measured claim whose number recomputes from the ok runs (the crashed run is excluded),
        # with a quote that wraps across lines in the topic.
        assert errors(root) == [], errors(root)
        assert errors(root, check="arm=a metric=x mean=0.8") == []    # 0.75 rounds to 0.8 (or 0.7) at one decimal
        assert errors(root, check="arm=a metric=x mean=0.6")          # does not reproduce
        assert errors(root, check="arm=a metric=x mean=0.76")
        assert errors(root, check="arm=b metric=x mean=0.75")         # no such arm
        assert errors(root, check="mean of x is 0.75")                # malformed check
        assert errors(root, commit="def5678")                         # result file is from another commit
        assert errors(root, evidence="topic.md")                      # not a result file
        assert errors(root, quote="scores 0.9")                       # the topic no longer says it
        assert errors(root, where="missing.md")
        # An established claim needs a source; a source is enough for "cited", not "reproduced".
        assert errors(root, status="established", evidence="", commit="", check="")
        assert errors(root, status="established", evidence="10.1002/cne.21974", commit="", check="") == []
        assert errors(root, status="established", evidence="https://doi.org/10.1002/cne.21974", commit="", check="") == []
        assert errors(root, status="hypothesis", evidence="", commit="", check="arm=a metric=x mean=0.75")  # check only for measured
        # Analogies and aspirations are never established or measured.
        assert errors(root, kind="analogy")
        assert errors(root, kind="aspiration", status="established", evidence="https://example.org", check="")
        assert errors(root, kind="aspiration", status="hypothesis", evidence="", commit="", check="") == []
        assert errors(root, status="proven")
        assert errors(root, reviewed="24/10/2026")
        # Stale reviews and unsupported claims warn, they do not fail.
        errs, warns = cc.check_row(row(reviewed="2025-01-01"), TODAY, root=root)
        assert errs == [] and any("days ago" in w for w in warns)
        errs, warns = cc.check_row(row(status="unsupported", evidence="", commit="", check=""), TODAY, root=root)
        assert errs == [] and any("unsupported" in w for w in warns)
    # The repository's own register is valid.
    assert cc.main([]) == 0
    print("check_claims: ok")


if __name__ == "__main__":
    main()
