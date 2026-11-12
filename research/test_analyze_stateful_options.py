"""Synthetic pass/fail adversarial fixtures for the option evidence gate."""
from __future__ import annotations

import copy

from analyze_stateful_options import ARMS, audit


def fixture(treatment: float = 0.7, baseline: float = 0.4,
            retained: float = -0.01) -> dict:
    runs = []
    for seed in range(1, 11):
        for arm in ARMS:
            score = treatment if arm == "options" else (
                1.0 if arm == "oracle" else baseline
            )
            source = 0.8
            scores = {
                "heldout": {"success": score},
                "zeroShot": {"success": score},
                "sourceBefore": {"success": source},
                "sourceAfter": {
                    "success": source + retained if arm == "options" else source
                },
                "training": {"decisions": 106},
                "adaptation": {"decisions": 105},
            }
            runs.append({
                "seed": seed, "arm": arm, "split": "eval", "status": "ok",
                "scores": scores,
            })
    return {
        "schema": "brain-result/1",
        "experiment": "brain-world/stateful-options-pilot",
        "config": {"seeds": list(range(1, 11))},
        "budgets": {"trainingDecisionsPerArm": 100,
                    "adaptationDecisionsPerArm": 100},
        "runs": runs,
    }


def must_fail(record: dict, reason: str) -> None:
    try:
        audit(record)
    except ValueError as exc:
        assert reason in str(exc), (reason, str(exc))
    else:
        raise AssertionError(f"failed to reject {reason}")


passing = audit(fixture())
assert passing["gate"] == "pass"
assert abs(passing["delta"] - 0.3) < 1e-9
assert passing["delta_ci95"][0] > 0
assert passing["n_seeds"] == 10
assert audit(fixture(treatment=0.3))["gate"] == "fail"
assert audit(fixture(retained=-0.2))["gate"] == "fail"
missing = fixture()
missing["runs"].pop()
must_fail(missing, "incomplete")
duplicated = fixture()
duplicated["runs"].append(copy.deepcopy(duplicated["runs"][0]))
must_fail(duplicated, "duplicate")
leaked = fixture()
leaked["config"]["seeds"] = [1, 2, 3]
must_fail(leaked, "fixed seeds")
underbudget = fixture()
underbudget["runs"][0]["scores"]["training"]["decisions"] = 1
must_fail(underbudget, "unmatched")
failed = fixture()
failed["runs"][0]["status"] = "timeout"
must_fail(failed, "failed run")
bad_score = fixture()
bad_score["runs"][0]["scores"]["zeroShot"]["success"] = 1.2
must_fail(bad_score, "invalid success")
print("stateful options evidence gate: ok")
