"""Continuous-body invariants and strictly causal delayed feedback."""
from __future__ import annotations

import unittest

from closed_loop_reach import HORIZON, ReachTrial, reach_trials
from continuous_motor import ContinuousReachBody, DelayedRewardSelector
from online_context import OnlineConfig, OnlineRewardSelector


class ContinuousBodyTests(unittest.TestCase):
    def test_target_updates_never_reset_joint_positions_or_velocities(self):
        a, b = reach_trials('eval', 2, 2)
        body = ContinuousReachBody(a)
        initial_id = id(body.loop.body)
        for index in range(HORIZON):
            body.act(1 if index % 4 else 0)
        positions, velocities = body.loop.body.positions.copy(), body.loop.body.velocities.copy()
        self.assertNotEqual(positions['L_hip'], 0.0)
        self.assertEqual(body.physical_steps, HORIZON)
        body.set_target(b)
        self.assertEqual(id(body.loop.body), initial_id)
        self.assertEqual(body.loop.body.positions, positions)
        self.assertEqual(body.loop.body.velocities, velocities)
        self.assertEqual(body.steps, 0)  # target budget resets; physics does not.
        self.assertEqual(body.physical_steps, HORIZON)
        self.assertEqual(body.targets_seen, 2)
        body.act(0, inverted_motor=True)
        self.assertEqual(body.physical_steps, HORIZON + 1)

    def test_target_validation_and_natural_budget(self):
        a, b = reach_trials('train', 4, 2)
        body = ContinuousReachBody(a)
        with self.assertRaises(RuntimeError):
            body.set_target(b)
        for _ in range(HORIZON):
            body.act(0)
        with self.assertRaises(RuntimeError):
            body.act(1)
        with self.assertRaises(ValueError):
            body.set_target(ReachTrial(float('nan'), (0.0, 0.0), 'eval', 'nan'))
        self.assertEqual(body.targets_seen, 1)
        body.set_target(b)
        self.assertEqual(body.targets_seen, 2)


class DelayedFeedbackTests(unittest.TestCase):
    def test_exact_history_policy_equivalence_at_one_action_delay(self):
        cfg = OnlineConfig(window=3, low_mean=-0.5, min_dwell=4, max_switches=6)
        original = OnlineRewardSelector(cfg)
        delayed = DelayedRewardSelector(cfg, delay=1)
        outcomes = [-1, -1, 1, -1, -1, -1, -1, 1, 1, 1, -1, -1, -1, -1]
        for reward in outcomes:
            self.assertEqual(delayed.choose(), original.select())
            original.feedback(reward)
            delayed.feedback(reward)
        self.assertEqual(delayed.stats().actions, len(outcomes))
        self.assertEqual(delayed.stats().pending_rewards, 1)
        self.assertEqual(delayed.stats().rewards_delivered, len(outcomes) - 1)

    def test_delayed_negative_outcomes_cannot_switch_before_arrival(self):
        cfg = OnlineConfig(window=2, low_mean=-0.5, min_dwell=1, max_switches=2)
        delay = DelayedRewardSelector(cfg, delay=3)
        chosen = []
        for _ in range(5):
            chosen.append(delay.choose())
            delay.feedback(-1.0)
        # The first negative reward arrives at action t=3; the second at t=4.
        # Switching only becomes possible when both are observed at t=4.
        self.assertEqual(chosen[:5], [0, 0, 0, 0, 1])
        self.assertEqual(delay.stats().rewards_delivered, 2)
        self.assertEqual(delay.stats().pending_rewards, 3)
        self.assertEqual(delay.stats().switches, 1)

    def test_no_fake_outcomes_and_bounded_delay(self):
        d = DelayedRewardSelector(OnlineConfig(), delay=3)
        with self.assertRaises(RuntimeError):
            d.feedback(1)
        d.choose()
        with self.assertRaises(RuntimeError):
            d.choose()
        with self.assertRaises(RuntimeError):
            d.stats()
        for value in (float('nan'), float('inf'), 2.0, True, None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                d.feedback(value)
        d.feedback(-1)
        self.assertEqual(d.stats().actions, 1)
        with self.assertRaises(ValueError):
            DelayedRewardSelector(OnlineConfig(), delay=0)
        with self.assertRaises(ValueError):
            DelayedRewardSelector(OnlineConfig(), delay=True)
        with self.assertRaises(ValueError):
            DelayedRewardSelector(OnlineConfig(), initial=3)


if __name__ == '__main__':
    unittest.main()