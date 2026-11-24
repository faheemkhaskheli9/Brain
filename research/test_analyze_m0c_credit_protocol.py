"""Mutation tests on a tiny real run (not a Brain performance result)."""
import copy
import json
import os
import subprocess
import tempfile
import unittest

from analyze_m0c_credit_protocol import holm, sign_flip_p, summarize, validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fixture():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "smoke.json")
        subprocess.run(["node", "game/world/stateful_credit_protocol.mjs", "--budget", "15",
                        "--repeats", "1", "--dev-seeds", "101", "--out", out, "1", "2"],
                       cwd=ROOT, check=True, capture_output=True)
        with open(out, encoding="utf-8") as stream:
            return json.load(stream)


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = fixture()

    def mutated(self):
        return copy.deepcopy(self.record)

    def test_valid_and_two_step_sizes(self):
        validate(self.record)
        report = summarize(self.record)
        self.assertEqual(len(report["contrasts"]), 12)
        self.assertEqual(len(self.record["config"]["evalScales"]), 2)

    def test_stats_helpers(self):
        self.assertEqual(sign_flip_p([0, 0, 0]), 1.0)
        self.assertAlmostEqual(sign_flip_p([1] * 10), 2 / 1024)
        self.assertEqual(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])

    def test_rejects_tampered_selection(self):
        r = self.mutated()
        r["config"]["selection"]["selected"] = 8
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_dev_eval_seed_overlap(self):
        r = self.mutated()
        r["config"]["devSeeds"] = [1]
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_missing_eval_row(self):
        r = self.mutated()
        r["runs"] = [x for x in r["runs"] if not (x["split"] == "eval" and x["seed"] == 2 and
                                                 x["arm"].startswith("aligned@"))]
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_budget_or_oracle_mismatch(self):
        r = self.mutated()
        row = next(x for x in r["runs"] if x["split"] == "eval")
        row["scores"]["onlineOracleQueries"] = 1
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_goal_mask_bypass(self):
        r = self.mutated()
        row = next(x for x in r["runs"] if x["arm"].startswith("mask-goal@"))
        row["scores"]["goalSensitivity"]["carryingL1"] = 0.1
        with self.assertRaises(ValueError):
            validate(r)

    def test_error_rows_score_zero_not_dropped(self):
        r = self.mutated()
        row = next(x for x in r["runs"] if x["split"] == "eval" and
                   x["arm"].startswith("native@"))
        row["status"], row["scores"] = "error", {}
        arm = summarize(r)["arms"][row["arm"]]
        self.assertEqual(arm["errors"], 1)
        self.assertEqual(len(arm["perSeedTrain"]), 2)


if __name__ == "__main__":
    unittest.main()
