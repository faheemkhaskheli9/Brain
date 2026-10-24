"""Tests for the shared result format (#104). Stdlib only; the end-to-end part needs node 22+.

    python research/test_result_schema.py
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import result_schema as rs  # noqa: E402

FIXTURE = os.path.join(HERE, "results", "fixtures", "sweep.log")


def sample():
    runs = [{"arm": "a", "seed": 1, "status": "ok", "scores": {"x": 1.0, "k": {"y": 2}}},
            {"arm": "a", "seed": 2, "status": "ok", "scores": {"x": 3.0, "k": {"y": 4}}},
            {"arm": "a", "seed": 3, "status": "timeout", "reason": "budget", "scores": {}},
            {"arm": "b", "seed": 1, "status": "ok", "scores": {"x": 2.0, "k": {"y": 2}}},
            {"arm": "b", "seed": 2, "status": "ok", "scores": {"x": 5.0, "k": {"y": 5}}},
            {"arm": "b", "seed": 3, "status": "ok", "scores": {"x": 9.0, "k": {"y": 9}}}]
    return rs.make_result("test", "python test", {"lr": 0.1}, {"steps": 10}, {"x": "higher", "k.y": "higher"},
                          runs, baseline="a", commit="abc1234")


def test_valid_and_summary():
    r = sample()
    assert rs.validate(r) == [], rs.validate(r)
    rows = {row["arm"]: row for row in rs.summary(r)}
    # The timeout stays in the denominator; the mean is over ok runs and says how many.
    assert rows["a"]["started"] == 3 and rows["a"]["statuses"] == {"ok": 2, "timeout": 1}
    assert rows["a"]["metrics"]["x"] == {"n": 2, "mean": 2.0, "ci95": rows["a"]["metrics"]["x"]["ci95"]}
    v = rows["b"]["metrics"]["x"]["vs_baseline"]
    assert v["n"] == 2 and v["diff"] == 1.5 and v["p"] == 0.5   # seeds 1, 2: +1, +2; seed 3 not paired
    assert "a: 2/3 ok" in rs.format_summary(r, rs.summary(r))


def test_invalid():
    def bad(mutate, expect):
        r = sample()
        mutate(r)
        errs = rs.validate(r)
        assert any(expect in e for e in errs), (expect, errs)
    bad(lambda r: r.pop("commit"), "commit")
    bad(lambda r: r.update(schema="brain-result/0"), "schema")
    bad(lambda r: r["metrics"].update(x="up"), "metrics.x")
    bad(lambda r: r["runs"][2].pop("reason"), "needs a reason")
    bad(lambda r: r["runs"][0].update(status="passed"), "status")
    bad(lambda r: r["runs"][0]["scores"].pop("x"), "lacks metric")
    bad(lambda r: r["runs"].append(copy.deepcopy(r["runs"][0])), "duplicate")
    bad(lambda r: r.update(baseline="z"), "baseline")
    bad(lambda r: r["runs"][0].update(seed=True), "seed")


def test_sign_flip():
    assert rs.sign_flip([1, 1, 1]) == 0.25            # only all-+ and all-- reach |3|
    assert rs.sign_flip([1, -1]) == 1.0
    assert rs.sign_flip([0.5] * 20) < 0.01            # sampled branch


def test_sweep_end_to_end():
    """sweep.mjs --from the fixture log writes a valid file that keeps the timeout and the crash."""
    if not shutil.which("node"):
        print("  skipped: node not installed")
        return
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "sweep.json")
        subprocess.run(["node", os.path.join(HERE, "..", "game", "world", "sweep.mjs"), "--from", FIXTURE,
                        "--arms", "rehearse30,kwta35", "--out", out], check=True, capture_output=True)
        with open(out, encoding="utf-8") as fh:
            r = json.load(fh)
    assert rs.validate(r) == [], rs.validate(r)
    st = {(x["arm"], x["seed"]): x["status"] for x in r["runs"]}
    assert st == {("rehearse30", 1): "ok", ("rehearse30", 2): "ok", ("rehearse30", 3): "timeout",
                  ("kwta35", 1): "ok", ("kwta35", 2): "ok", ("kwta35", 3): "error"}, st
    assert r["baseline"] == "rehearse30" and r["budgets"]["episodes_per_stage"] == 20000
    assert r["config"]["arms"]["kwta35"]["kwta"] == 35
    rows = {row["arm"]: row for row in rs.summary(r)}
    assert rows["kwta35"]["metrics"]["total"]["vs_baseline"]["diff"] == -410


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"{name}: ok")
