"""Regression tests: only signed public sensory inputs and after-action reward."""

import json
import unittest

import numpy as np

from closed_loop_reach import HORIZON, ReachBody, reach_trials, run_episodes
from structural_plasticity import PlasticityConfig, SparsePlasticPolicy


class ClosedLoopReachTests(unittest.TestCase):
    def test_splits_are_reproducible_and_disjoint(self):
        a = reach_trials("train", 11, 100)
        self.assertEqual(a, reach_trials("train", 11, 100))
        b = reach_trials("eval", 11, 100)
        self.assertTrue(set(x.key for x in a).isdisjoint(x.key for x in b))
        self.assertTrue(all(0.37 <= abs(t.target) <= 0.52 for t in b))
        for bad in (("unknown", 1, 3), ("train", -1, 3), ("eval", 1, 0)):
            with self.assertRaises(ValueError):
                reach_trials(*bad)

    def test_sensor_features_are_signed_and_track_state(self):
        sample = reach_trials("train", 0, 1)[0]
        body = ReachBody(sample)
        start = body.observe()
        self.assertEqual(start.shape, (24,))
        self.assertEqual(start.dtype, np.float32)
        self.assertAlmostEqual(float(start[0]), sample.target, places=6)
        self.assertEqual(list(start[1:3]), list(sample.distractors))
        self.assertTrue(np.array_equal(start[3:], np.zeros(21, np.float32)))
        body.act(1)
        after = body.observe()
        self.assertNotEqual(float(start[0]), float(after[0]))
        self.assertGreater(float(after[3]), 0)  # signed proprioception, no abs pooling
        self.assertGreater(float(after[5]), 0)  # hip velocity
        self.assertTrue(np.all(np.isfinite(after)))

    def test_opposite_actions_move_left_hip_in_opposite_directions(self):
        task = reach_trials("eval", 4, 1)[0]
        left, right = ReachBody(task), ReachBody(task)
        left.act(0)
        right.act(1)
        self.assertLess(left.loop.body.positions["L_hip"], 0)
        self.assertGreater(right.loop.body.positions["L_hip"], 0)
        self.assertEqual(left.loop.body.positions["R_hip"], 0)
        self.assertEqual(right.loop.body.positions["R_knee"], 0)
        flipped = ReachBody(task)
        flipped.act(1, inverted_motor=True)
        self.assertLess(flipped.loop.body.positions["L_hip"], 0)

    def test_reward_is_verified_after_motion_and_has_no_action_oracle(self):
        target = next(t for t in reach_trials("train", 1, 4) if t.target > 0)
        better, worse = ReachBody(target), ReachBody(target)
        self.assertEqual(better.act(1), 1)
        self.assertEqual(worse.act(0), -1)
        self.assertEqual(better.steps, 1)
        with self.assertRaises(ValueError):
            better.act(2)
        for _ in range(HORIZON - 1):
            better.act(0)
        with self.assertRaises(RuntimeError):
            better.act(0)

    def test_frozen_evaluation_does_not_change_checkpoint_and_respects_budget(self):
        policy = SparsePlasticPolicy(PlasticityConfig(), 10)
        tasks = reach_trials("eval", 34, 5)
        before = policy.fingerprint()
        x = run_episodes(policy, tasks)
        self.assertEqual(before, policy.fingerprint())
        self.assertEqual(x.episodes, 5)
        self.assertGreaterEqual(x.success, 0)
        self.assertLessEqual(x.success, 1)
        self.assertEqual(x, run_episodes(policy, tasks))
        with self.assertRaises(ValueError):
            run_episodes(policy, tasks, delay=0)
        with self.assertRaises(ValueError):
            run_episodes(policy, tasks, delay=17)

    def test_delay_two_receives_one_reward_per_two_actions(self):
        model = SparsePlasticPolicy(PlasticityConfig(), 12)
        tasks = reach_trials("train", 12, 4)
        run_episodes(model, tasks, learn=True, delay=2)
        self.assertEqual(model.feedback_steps, 4 * (HORIZON // 2))
        self.assertLessEqual(len(model.edges), model.cfg.max_edges)
        state = json.loads(json.dumps(model.export_state()))
        copy = SparsePlasticPolicy.from_state(state)
        self.assertEqual(model.fingerprint(), copy.fingerprint())

    def test_frozen_training_is_rejected(self):
        model = SparsePlasticPolicy(PlasticityConfig(), 5, learn=False)
        with self.assertRaises(ValueError):
            run_episodes(model, reach_trials("train", 5, 1), learn=True)


if __name__ == "__main__":
    unittest.main()