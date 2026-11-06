"""Synthetic positive, negative and corrupt archive cases for replay analyzer."""
import copy
import unittest

from analyze_replay import analyze

SKILLS = ("grasp", "listen", "read", "write")


def experiment(seeds=range(1, 5)):
    seeds = list(seeds)
    arms = {"sleep-uniform": {"replay": 0.1, "sleepEvery": 20},
            "sleep-td-mix": {"replay": 0.1, "sleepEvery": 20, "sleepSampler": "td-mix"},
            "sleep-no-replay": {"replay": 0.1, "sleepEvery": 0}}
    runs = []
    for arm in arms:
        for seed in seeds:
            kept = {k: 0.5 + (0.06 if arm == "sleep-td-mix" else 0) for k in SKILLS}
            runs.append({"arm": arm, "seed": seed, "split": None, "status": "ok",
                         "reason": None, "seconds": 100 if arm != "sleep-td-mix" else 105,
                         "scores": {"total": 12000, "kept": kept}})
    return {"schema": "brain-result/1", "experiment": "brain-world/sweep",
            "commit": "synthetic", "created": "2026-11-06T00:00:00Z", "command": "synthetic",
            "environment": {}, "config": {"seeds": seeds, "arms": arms,
                "gains": {"memCap": 2048, "sleepSize": 200,
                          "sleepPriorityAlpha": 0.6, "sleepUniformMix": 0.2,
                          "sleepImportanceBeta": 1}},
            "budgets": {"episodes_per_stage": 20000, "scored_episodes": 4000},
            "metrics": {"total": "lower"}, "baseline": "sleep-uniform", "runs": runs}


class ReplayAnalysisTest(unittest.TestCase):
    def test_preregistered_success(self):
        out = analyze(experiment(range(1, 11)))
        row = out["by_arm"]["sleep-td-mix"]
        self.assertEqual(row["paired_n"], 10)
        self.assertEqual(row["graduated"], 10)
        self.assertAlmostEqual(row["mean_paired_retention_gain"], 0.06)
        self.assertGreater(row["paired_ci95"][0], 0)
        self.assertAlmostEqual(row["paired_wall_time_ratio"], 1.05)
        self.assertTrue(row["passes_preregistered_rule"])
        self.assertFalse(out["by_arm"]["sleep-no-replay"]["passes_preregistered_rule"])

    def test_exploratory_arm_cannot_be_promoted_by_look_elsewhere(self):
        data = experiment()
        # An exploratory arm can look equally promising but must not be
        # declared a confirmatory win without a separate registration.
        data["config"]["arms"]["sleep-td"] = {"replay": 0.1, "sleepEvery": 20}
        for seed in data["config"]["seeds"]:
            data["runs"].append({"arm": "sleep-td", "seed": seed, "split": None,
                                 "status": "ok", "reason": None, "seconds": 105,
                                 "scores": {"total": 12000,
                                            "kept": {k: 0.6 for k in SKILLS}}})
        out = analyze(data)
        self.assertFalse(out["by_arm"]["sleep-td"]["passes_preregistered_rule"])

    def test_insufficient_paired_seeds_cannot_be_promoted(self):
        data = experiment()
        data["config"]["seeds"] = [1, 2, 3, 4]
        # Even four perfectly consistent seeds are a pilot, not the
        # preregistered ten-seed confirmatory experiment.
        self.assertFalse(analyze(data)["by_arm"]["sleep-td-mix"]["passes_preregistered_rule"])

    def test_failure_not_dropped_or_called_success(self):
        data = experiment()
        for row in data["runs"]:
            if row["arm"] == "sleep-td-mix" and row["seed"] == 3:
                row.update(status="timeout", reason="read not learned", scores={})
        out = analyze(data)
        row = out["by_arm"]["sleep-td-mix"]
        self.assertEqual((row["started"], row["graduated"], row["timeouts"], row["paired_n"]), (4, 3, 1, 3))
        self.assertFalse(row["passes_preregistered_rule"])

    def test_missing_run_rejected(self):
        data = experiment()
        data["runs"].pop()
        with self.assertRaisesRegex(ValueError, "missing/unexpected"):
            analyze(data)

    def test_duplicate_run_rejected(self):
        data = experiment()
        data["runs"].append(copy.deepcopy(data["runs"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            analyze(data)

    def test_split_contamination_rejected(self):
        data = experiment()
        data["runs"][0]["split"] = "eval"
        with self.assertRaisesRegex(ValueError, "split"):
            analyze(data)

    def test_changed_budget_rejected(self):
        data = experiment()
        data["budgets"]["episodes_per_stage"] = 100
        with self.assertRaisesRegex(ValueError, "budget"):
            analyze(data)

    def test_non_finite_retention_rejected(self):
        data = experiment()
        data["runs"][1]["scores"]["kept"]["read"] = float("nan")
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            analyze(data)

    def test_mismatched_rehearsal_rejected(self):
        data = experiment()
        data["config"]["arms"]["sleep-td-mix"]["replay"] = 0.3
        with self.assertRaisesRegex(ValueError, "rehearsal"):
            analyze(data)


if __name__ == "__main__":
    unittest.main()
