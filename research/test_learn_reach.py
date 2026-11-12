"""Bounded deterministic closed-loop learning and audit-protocol regression."""

import json
import unittest

from closed_loop_reach import reach_trials, run_episodes
from learn_reach import ARMS, experiment, policy_for, run_seed, summary
from result_schema import validate
from structural_plasticity import SparsePlasticPolicy


class LearningReachTests(unittest.TestCase):
    def test_all_arms_share_initial_budget_and_delayed_feedback_is_charged(self):
        rows = run_seed(0, train_episodes=4, eval_episodes=3, reverse_episodes=2)
        self.assertEqual([r["arm"] for r in rows], list(ARMS))
        self.assertTrue(all(r["status"] == "ok" for r in rows), rows)
        for row in rows:
            s = row["scores"]
            self.assertGreaterEqual(s["heldoutSuccess"], 0)
            self.assertLessEqual(s["heldoutSuccess"], 1)
            self.assertLessEqual(s["connections"], 4)
            self.assertEqual(s["feedbackCalls"], 0 if row["arm"] == "frozen" else
                             32 if row["arm"] == "evidence_delay2" else 64)

    def test_experiment_record_is_valid_and_exactly_reproducible_except_timing(self):
        a = experiment((2, 3), train_episodes=4, eval_episodes=3, reverse_episodes=2, commit="test")
        b = experiment((2, 3), train_episodes=4, eval_episodes=3, reverse_episodes=2, commit="test")
        self.assertFalse(validate(a))
        self.assertFalse(validate(b))
        scores = lambda x: [(r["arm"], r["seed"], r["scores"], r["checkpoint"], r["connectionTopology"])
                            for r in x["runs"]]
        self.assertEqual(scores(a), scores(b))
        self.assertEqual(summary(a)["status"], "complete")

    def test_frozen_scoring_is_unchanged_after_checkpoint_load(self):
        p = policy_for("evidence", 3)
        run_episodes(p, reach_trials("train", 3, 5), learn=True)
        checkpoint = json.loads(json.dumps(p.export_state()))
        restored = SparsePlasticPolicy.from_state(checkpoint)
        data = reach_trials("eval", 1023, 3)
        self.assertEqual(run_episodes(p, data), run_episodes(restored, data))
        self.assertEqual(p.fingerprint(), restored.fingerprint())

    def test_known_diagnostic_growth_reaches_body_not_a_hardcoded_answer(self):
        # Exploratory fixture: the pretrained handwired path is deliberately absent.
        policy = policy_for("evidence", 0)
        self.assertFalse(any(i == 0 for i, _ in policy.edges))
        run_episodes(policy, reach_trials("train", 0, 120), learn=True)
        self.assertTrue(any(i == 0 for i, _ in policy.edges))
        self.assertLessEqual(len(policy.edges), policy.cfg.max_edges)
        score = run_episodes(policy, reach_trials("dev", 1000, 40))
        self.assertGreaterEqual(score.success, 0.75)

    def test_invalid_budgets_rejected(self):
        with self.assertRaises(ValueError):
            run_seed(-1, 4, 4, 4)
        with self.assertRaises(ValueError):
            experiment((1, 1), train_episodes=4, eval_episodes=4)


if __name__ == "__main__":
    unittest.main()