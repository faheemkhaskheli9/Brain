"""Synthetic mutation tests are not Brain performance results."""
import copy
import unittest

from analyze_m0c_credit_probe import ARMS, bootstrap, summarize, validate


def fixture():
    seeds = [1, 2]
    budgets = [0, 5]
    def metrics(episodes):
        return {"success": 0.5, "deliveries": episodes // 2,
                "failed": episodes // 2, "episodes": episodes,
                "decisions": episodes * 2, "envSteps": episodes * 2,
                "entropy": 0.9}
    obs = {"directActorInputWidth": 100, "rawInputWidth": 100,
           "goalCounterfactualL1": 0, "carryingGoalCounterfactualL1": 0}
    rows = []
    for seed in seeds:
        for arm in ARMS:
            stages = [{"decisions": budget,
                       "calibration": metrics(2),
                       "diagnosticVariants": metrics(4),
                       "sensory": copy.deepcopy(obs)}
                      for budget in budgets]
            rows.append({"seed": seed, "arm": arm, "status": "ok",
                         "scores": {"trainDecisions": 5, "trainEnvSteps": 5,
                                    "learningUpdates": 5, "onlineOracleQueries": 0,
                                    "modelBytes": 20, "trainMeanAbsTD": 0.1,
                                    "trainDeliveries": 2, "curve": stages}})
    return {"schema": "brain-result/1", "commit": "synthetic",
            "config": {"arms": list(ARMS), "seeds": seeds,
                       "checkpoints": budgets, "repeats": 2},
            "runs": rows}


class AuditTests(unittest.TestCase):
    def test_valid_and_paired_ci(self):
        self.assertEqual(len(validate(fixture())), 12)
        report = summarize(fixture())
        self.assertEqual(report["arms"]["native-three"]["finalSuccess"], 0.5)
        self.assertEqual(report["arms"]["native-three"]["gainCi95"], [0.0, 0.0])
        self.assertEqual(bootstrap([1, 1]), [1.0, 1.0])
        self.assertIn("HOLD", report["advancement"])

    def test_missing_or_duplicate(self):
        r = fixture()
        r["runs"].pop()
        with self.assertRaisesRegex(ValueError, "missing"):
            validate(r)
        r = fixture()
        r["runs"].append(r["runs"][-1])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate(r)

    def test_oracle_and_physical_step(self):
        for key, value in (("onlineOracleQueries", 1),
                           ("trainEnvSteps", 4),
                           ("learningUpdates", 4)):
            r = fixture()
            r["runs"][0]["scores"][key] = value
            with self.assertRaisesRegex(ValueError, "budget|oracle"):
                validate(r)

    def test_goal_mask_and_frozen_scoring(self):
        r = fixture()
        row = next(x for x in r["runs"] if x["arm"] == "mask-goal")
        row["scores"]["curve"][0]["sensory"]["goalCounterfactualL1"] = 0.3
        with self.assertRaisesRegex(ValueError, "mask"):
            validate(r)
        r = fixture()
        r["runs"][0]["scores"]["curve"][-1]["calibration"]["envSteps"] += 1
        with self.assertRaisesRegex(ValueError, "charge"):
            validate(r)

    def test_failed_seed_retained(self):
        r = fixture()
        r["runs"][0]["status"] = "error"
        with self.assertRaisesRegex(ValueError, "failed"):
            validate(r)


if __name__ == "__main__":
    unittest.main()
