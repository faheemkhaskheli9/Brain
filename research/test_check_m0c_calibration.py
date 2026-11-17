"""Synthetic fault injections guard reporting; scores are NOT empirical evidence."""
import copy
import unittest

from check_m0c_calibration import ARMS, check


def fixture():
    config = {
        "seeds": [1, 2],
        "arms": list(ARMS),
        "checkpoints": [0, 5],
        "repeats": 2,
        "diagnosticVariants": [{"id": "left"}, {"id": "approach"}],
    }
    def evaluation(n):
        return {
            "success": 0.5,
            "episodes": n,
            "deliveries": n // 2,
            "failed": n // 2,
            "decisions": n * 3,
            "envSteps": n * 3,
        }
    rows = []
    for seed in config["seeds"]:
        for arm in ARMS:
            before = {"decisions": 0, "calibration": evaluation(2),
                      "diagnosticVariants": evaluation(4)}
            after = copy.deepcopy(before)
            after["decisions"] = 5
            rows.append({"arm": arm, "seed": seed, "status": "ok",
                         "scores": {"trainDecisions": 0 if arm == "uniform-random" else 5,
                                    "trainEnvSteps": 0 if arm == "uniform-random" else 5,
                                    "oracleQueries": 0,
                                    "training": {"pickups": 0, "successes": 0},
                                    "curve": [before, after]}})
    return {"schema": "brain-result/1", "config": config, "runs": rows}


class GateTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(len(check(fixture())), 14)

    def test_no_missing_or_duplicates(self):
        a = fixture()
        a["runs"].pop()
        with self.assertRaisesRegex(ValueError, "missing"):
            check(a)
        a = fixture()
        a["runs"].append(a["runs"][0])
        with self.assertRaisesRegex(ValueError, "repeated"):
            check(a)

    def test_failed_budget_and_oracle(self):
        for key, value in [("trainDecisions", 2), ("trainEnvSteps", 2),
                           ("oracleQueries", 1)]:
            a = fixture()
            a["runs"][0]["scores"][key] = value
            with self.assertRaisesRegex(ValueError, "budget|privileged"):
                check(a)
        a = fixture()
        a["runs"][0]["status"] = "error"
        with self.assertRaisesRegex(ValueError, "failed"):
            check(a)

    def test_mutated_frozen_result_and_checkpoints(self):
        a = fixture()
        a["runs"][0]["scores"]["curve"][1]["decisions"] = 6
        with self.assertRaisesRegex(ValueError, "checkpoint"):
            check(a)
        a = fixture()
        a["runs"][0]["scores"]["curve"][1]["calibration"]["envSteps"] += 1
        with self.assertRaisesRegex(ValueError, "unpaid"):
            check(a)
        a = fixture()
        a["runs"][0]["scores"]["curve"][1]["calibration"]["success"] = 1
        with self.assertRaisesRegex(ValueError, "outcome"):
            check(a)


if __name__ == "__main__":
    unittest.main()
