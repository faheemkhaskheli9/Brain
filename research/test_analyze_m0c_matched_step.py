"""Mutation tests on a tiny real run (not a Brain performance result)."""
import copy
import itertools
import json
import os
import subprocess
import tempfile
import unittest

from analyze_m0c_matched_step import holm, sign_flip_p, summarize, validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fixture():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "smoke.json")
        subprocess.run(["node", "game/world/matched_step_credit_protocol.mjs", "--budget", "15",
                        "--repeats", "1", "--dev-seeds", "101", "--etas", "0.004,0.016",
                        "--out", out, "1", "2"],
                       cwd=ROOT, check=True, capture_output=True)
        with open(out, encoding="utf-8") as stream:
            return json.load(stream)


def brute(diffs):
    observed = abs(sum(diffs))
    flips = list(itertools.product((1, -1), repeat=len(diffs)))
    return sum(abs(sum(s * d for s, d in zip(f, diffs))) >= observed - 1e-12
               for f in flips) / len(flips)


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = fixture()

    def mutated(self):
        return copy.deepcopy(self.record)

    def test_valid_and_two_step_sizes(self):
        validate(self.record)
        report = summarize(self.record)
        self.assertEqual(len(report["contrasts"]), 6)
        self.assertEqual(len(set(self.record["config"]["evalEtas"])), 2)

    def test_exact_sign_flip_matches_brute_force(self):
        for diffs in ([3, -1, 2, 0, 5], [1] * 10, [0, 0, 0], [2, -2, 4, 1, -3, 6, 1]):
            self.assertAlmostEqual(sign_flip_p([d / 36 for d in diffs], 36), brute(diffs))
        self.assertAlmostEqual(sign_flip_p([1 / 36] * 20, 36), 2 / 2 ** 20)
        with self.assertRaises(ValueError):
            sign_flip_p([0.5 / 36], 36)
        self.assertEqual(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])

    def test_rejects_tampered_selection(self):
        r = self.mutated()
        r["config"]["evalEtas"] = r["config"]["evalEtas"][::-1]
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
                                                 x["arm"].startswith("no-hidden@"))]
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_unmatched_step(self):
        r = self.mutated()
        row = next(x for x in r["runs"] if x["split"] == "eval" and
                   x["arm"].startswith("no-hidden@"))
        row["scores"]["training"]["meanActorStep"] *= 9
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_goal_blind_ceiling_breach(self):
        r = self.mutated()
        row = next(x for x in r["runs"] if x["split"] == "eval" and
                   x["arm"].startswith("mask-goal@"))
        row["scores"]["after"]["train"]["maxGoalsPerRepeat"] = 2
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_goal_mask_bypass(self):
        r = self.mutated()
        row = next(x for x in r["runs"] if x["split"] == "eval" and
                   x["arm"].startswith("mask-goal@"))
        row["scores"]["goalSensitivity"]["carryingL1"] = 0.1
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_oracle_use(self):
        r = self.mutated()
        next(x for x in r["runs"] if x["split"] == "eval")["scores"]["onlineOracleQueries"] = 1
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
