"""Synthetic analysis gate regression tests: do not confuse with model evidence."""
import unittest

from analyze_m0c_controls import ARMS, analyze, paired_ci


def fixture():
    seeds = list(range(1, 11))
    cfg = {"seeds": seeds, "arms": list(ARMS), "trainSteps": 17,
           "trainTasks": 3, "devTasks": 2, "evalTasks": 2, "repeats": 1,
           "protocol": "legacy",
           "manifests": {str(seed): {"counts": {
               split: {"tasks": count, "uniqueStructures": count, "duplicates": 0}
               for split, count in [("train", 3), ("dev", 2), ("heldout", 2)]}}
               for seed in seeds},
           "generatorAudits": {str(seed): {"totalOfflineOracleQueries": 0}
                               for seed in seeds}}
    runs = []
    for arm in ARMS:
        for seed in seeds:
            e = 17 if arm in ARMS[:4] else 0
            x = {"success": 0.5, "decisions": 18, "envSteps": 18, "episodes": 2}
            runs.append({"arm": arm, "seed": seed, "status": "ok",
                         "scores": {"trainDecisions": e, "trainEnvSteps": e,
                                    "oracleQueries": 0, "source": x,
                                    "development": x, "heldout": x}})
    return {"schema": "brain-result/1", "config": cfg, "runs": runs}


class AnalyzerTest(unittest.TestCase):
    def test_deterministic_no_promotion(self):
        result = analyze(fixture())
        self.assertEqual(result["flatMinusBestHeldoutDelta"], 0)
        self.assertEqual(result["flatMinusBestHeldoutCi95"], [0, 0])
        self.assertIn("HOLD", result["promotion"])
        self.assertEqual(paired_ci([1] * 10), [1, 1])

    def test_missing_and_duplicate(self):
        o = fixture()
        o["runs"].pop()
        with self.assertRaisesRegex(ValueError, "missing"):
            analyze(o)
        o = fixture()
        o["runs"].append(o["runs"][-1])
        with self.assertRaisesRegex(ValueError, "repeated"):
            analyze(o)

    def test_failed_arm_and_budget(self):
        o = fixture()
        o["runs"][0]["status"] = "failed"
        with self.assertRaisesRegex(ValueError, "failed"):
            analyze(o)
        o = fixture()
        o["runs"][0]["scores"]["trainDecisions"] = 20
        with self.assertRaisesRegex(ValueError, "budget"):
            analyze(o)

    def test_unpaid_step_and_oracle(self):
        o = fixture()
        o["runs"][0]["scores"]["heldout"]["envSteps"] = 1
        with self.assertRaisesRegex(ValueError, "environment"):
            analyze(o)
        o = fixture()
        o["runs"][0]["scores"]["oracleQueries"] = 1
        with self.assertRaisesRegex(ValueError, "privileged"):
            analyze(o)

    def test_structural_duplicate_and_missing_feasibility(self):
        o = fixture()
        o["config"]["protocol"] = "scattered-to-barrier"
        o["config"]["manifests"]["1"]["counts"]["heldout"]["duplicates"] = 1
        with self.assertRaisesRegex(ValueError, "duplication"):
            analyze(o)
        o["config"]["manifests"]["1"]["counts"]["heldout"]["duplicates"] = 0
        with self.assertRaisesRegex(ValueError, "feasibility"):
            analyze(o)


if __name__ == "__main__":
    unittest.main()
