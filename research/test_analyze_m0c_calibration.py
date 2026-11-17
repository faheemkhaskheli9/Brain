"""Synthetic statistical/integrity tests; numbers are not research measurements."""
import unittest

from analyze_m0c_calibration import summarize
from test_check_m0c_calibration import fixture


class AnalysisTests(unittest.TestCase):
    def test_paired_zero_control_and_hold(self):
        report = summarize(fixture())
        self.assertEqual(report["arms"]["flat-brain"]["beforeSuccess"], 0.5)
        self.assertEqual(report["arms"]["flat-brain"]["pairedGain"], 0)
        self.assertEqual(report["arms"]["q-relative"]["afterCi95"], [0.5, 0.5])
        self.assertEqual(report["brainMinusRelativeQ"], 0)
        self.assertEqual(report["brainMinusRelativeQCi95"], [0, 0])
        self.assertIn("HOLD", report["promotionDecision"])

    def test_missing_run_fails(self):
        record = fixture()
        record["runs"].pop()
        with self.assertRaisesRegex(ValueError, "missing"):
            summarize(record)

    def test_violating_budget_fails(self):
        record = fixture()
        record["runs"][0]["scores"]["trainEnvSteps"] += 1
        with self.assertRaisesRegex(ValueError, "budget"):
            summarize(record)


if __name__ == "__main__":
    unittest.main()
