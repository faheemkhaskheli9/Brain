"""Mutation checks for paired source-trajectory identity and scientific controls."""
import copy
import json
import unittest
from pathlib import Path

from analyze_m0d_credit_replay import analyze, paired_interval

EVIDENCE = (Path(__file__).parent / "results" /
            "m0d-matched-credit-replay-10seed-2026-11-18.json")


class ReplayIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_valid_evidence(self):
        summary = analyze(self.sample)
        self.assertEqual(summary["records"], 70)
        self.assertEqual(summary["seedCount"], 10)
        self.assertGreater(summary["perArmMean"]["native"]["actorDeltaL1"], 0)
        self.assertEqual(summary["perArmMean"]["zero-feedback"]["actorDeltaL1"], 0)
        self.assertEqual(analyze(self.sample), summary)

    def test_missing_arm_rejected(self):
        changed = copy.deepcopy(self.sample)
        changed["runs"].pop()
        with self.assertRaisesRegex(ValueError, "missing arm"):
            analyze(changed)

    def test_mismatched_stream_rejected(self):
        changed = copy.deepcopy(self.sample)
        changed["runs"][1]["scores"]["streamHash"] = "different"
        with self.assertRaisesRegex(ValueError, "mismatched logged experience"):
            analyze(changed)

    def test_hidden_policy_interaction_rejected(self):
        changed = copy.deepcopy(self.sample)
        changed["runs"][1]["scores"]["policyEnvironmentInteractions"] = 1
        with self.assertRaisesRegex(ValueError, "uncounted"):
            analyze(changed)

    def test_negative_control_mutation_rejected(self):
        changed = copy.deepcopy(self.sample)
        row = next(r for r in changed["runs"] if r["arm"] == "actor-frozen")
        row["scores"]["actorDeltaL1"] = 1
        with self.assertRaisesRegex(ValueError, "negative controls"):
            analyze(changed)

    def test_unpaired_rejected(self):
        with self.assertRaisesRegex(ValueError, "unpaired"):
            paired_interval([1, 2], [3])


if __name__ == "__main__":
    unittest.main()
