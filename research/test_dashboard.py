"""Tests for the results dashboard (#107): bad files are reported, not dropped or fatal; exports
hold exactly the run values; incomparable files are flagged; text is escaped. Stdlib only.

    python research/test_dashboard.py
"""
import csv
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dashboard as db  # noqa: E402
import result_schema as rs  # noqa: E402


def record(budget=10, arm_b="<b>b</b>"):
    runs = [{"arm": "a", "seed": 1, "status": "ok", "scores": {"x": 1.0}},
            {"arm": "a", "seed": 2, "status": "ok", "scores": {"x": 3.0}},
            {"arm": arm_b, "seed": 1, "status": "ok", "scores": {"x": 2.0}},
            {"arm": arm_b, "seed": 2, "status": "failed", "reason": "not learned", "scores": {}}]
    return rs.make_result("exp", "python test", {"lr": 0.1, "seeds": [1, 2]}, {"steps": budget}, {"x": "higher"},
                          runs, baseline="a", commit="abc1234")


def main():
    with tempfile.TemporaryDirectory() as d:
        def put(name, obj):
            p = os.path.join(d, name)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(obj if isinstance(obj, str) else json.dumps(obj))
            return p
        good, other = put("good.json", record()), put("other.json", record(budget=20))
        broken, invalid = put("broken.json", "{not json"), put("invalid.json", {"schema": "brain-result/1"})
        missing = os.path.join(d, "missing.json")
        loaded = db.load([good, broken, invalid, missing, other])
        assert [r is not None for _, r, _ in loaded] == [True, False, False, False, True]
        assert loaded[3][2] == ["missing"] and loaded[1][2][0].startswith("unreadable")

        fl = db.flags(loaded)
        assert sum("budgets differ" in f for f in fl) == 1, fl
        assert any("broken.json" in f for f in fl) and any("missing" in f for f in fl) and any("invalid.json" in f for f in fl)
        assert not any("config (seeds aside)" in f for f in fl), "seeds alone must not flag the config"

        data = db.rows(loaded)
        assert len(data) == 8   # two valid files x four runs x one metric
        assert [x["value"] for x in data[:4]] == [1.0, 3.0, 2.0, None]
        out = os.path.join(d, "out.csv")
        db.write_csv(out, data)
        with open(out, encoding="utf-8") as fh:
            back = list(csv.DictReader(fh))
        assert len(back) == 8 and back[3]["status"] == "failed" and back[3]["reason"] == "not learned" and back[3]["value"] == ""

        exp = db.export_json(loaded)
        assert exp["files"][0]["record"] == record() | {"created": exp["files"][0]["record"]["created"]}
        assert exp["files"][1]["record"] is None and exp["files"][1]["problems"]

        page = db.page(loaded)
        assert "<b>b</b>" not in page and "&lt;b&gt;b&lt;/b&gt;" in page, "arm names must be escaped"
        assert "not learned" in page and "budgets differ" in page

        assert db.main([good, missing, "--html", os.path.join(d, "p.html")]) == 1   # a bad file fails the run
        assert db.main([good, "--csv", os.path.join(d, "c.csv")]) == 0
    print("ok")


if __name__ == "__main__":
    main()
