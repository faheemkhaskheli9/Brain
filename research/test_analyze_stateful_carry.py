"""Diagnostic analysis never selects the comparator from the frozen test split."""
import copy
import unittest

from analyze_stateful_carry import ARMS, EXPERIMENT, analyze


def fixture():
    rows = []
    for arm in ARMS:
        for seed in (1, 2, 3):
            dev = 0.8 if arm == "tabular-q" else 0.7 if arm == "hand-coded-heuristic" else 0.1
            heldout = 0.2 if arm == "tabular-q" else 0.9 if arm == "flat-brain" else 0.3
            rows.append({"arm": arm, "seed": seed, "split": "heldout-transition", "status": "ok",
                         "scores": {"development": {"success": dev},
                                    "heldout": {"success": heldout}}})
    return {"schema": "brain-result/1", "experiment": EXPERIMENT,
            "commit": "fixture", "created": "2026-11-12T00:00:00Z",
            "command": "fixture", "environment": {}, "config": {"seeds": [1, 2, 3]},
            "budgets": {"primitiveTrainingDecisionsPerTrainedArm": 17},
            "metrics": {"development.success": "higher", "heldout.success": "higher"},
            "baseline": "tabular-q", "runs": rows}


class CarryAnalysisTests(unittest.TestCase):
    def test_development_only_selection(self):
        record = fixture()
        result = analyze(record)
        self.assertEqual(result["development_selected_comparator"], "tabular-q")
        self.assertFalse(result["confirmatory"])
        self.assertEqual(result["comparisons"]["flat-brain"]["paired_seeds"], [1, 2, 3])
        self.assertAlmostEqual(result["comparisons"]["flat-brain"]["heldout_delta_mean"], 0.7)
        self.assertEqual(result["run_failures"], [])

    def test_frozen_test_mutation_does_not_select_winner(self):
        record = fixture()
        for r in record["runs"]:
            r["scores"]["heldout"]["success"] = float(r["arm"] == "fixed-script")
        self.assertEqual(analyze(record)["development_selected_comparator"], "tabular-q")

    def test_missing_seed_is_error(self):
        record = fixture()
        record["runs"].pop()
        with self.assertRaises(ValueError):
            analyze(record)

    def test_duplicate_cohort_is_error(self):
        record = fixture()
        record["runs"].append(copy.deepcopy(record["runs"][0]))
        with self.assertRaises(ValueError):
            analyze(record)

    def test_invalid_experiment_is_error(self):
        record = fixture()
        record["experiment"] = "unrelated"
        with self.assertRaises(ValueError):
            analyze(record)

    def test_missing_development_metric_is_error(self):
        record = fixture()
        record["runs"][0]["scores"].pop("development")
        with self.assertRaises(ValueError):
            analyze(record)


if __name__ == "__main__":
    unittest.main()
