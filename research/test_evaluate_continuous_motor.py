"""Scientific controls: same actions/target instances; no hidden reset or future reward."""
from __future__ import annotations

import base64
import struct
import unittest

from evaluate_continuous_motor import ARMS, experiment, run_stream
from evaluate_online_context import train_checkpoints
from result_schema import validate


class ContinuousEvaluationTests(unittest.TestCase):
    def test_same_stream_actions_and_persistent_physics(self):
        mem = train_checkpoints(0, train_episodes=8, adapt_episodes=5)
        before = mem.digest()
        stats = {arm: run_stream(mem, arm, 0, phase_steps=(33, 41, 47, 39)) for arm in ARMS}
        self.assertEqual(mem.digest(), before)
        self.assertEqual(set(stats), set(ARMS))
        target_hashes = {v['trace']['targetKeysSha256'] for v in stats.values()}
        self.assertEqual(len(target_hashes), 1)
        for result in stats.values():
            self.assertEqual(result['bodyResets'], 0)
            self.assertEqual(result['physicalActions'], 160)
            self.assertEqual(result['generatedRewards'], 160)
            self.assertEqual(result['targetChanges'], 9)
            self.assertEqual(result['extraProbeActions'], 0)
            self.assertEqual(len(result['trace']['motorActions']), 160)
            self.assertEqual(len(result['trace']['selected']), 160)
            packed = base64.b64decode(result['trace']['positionsInt16Base64'])
            positions = struct.unpack('<160h', packed)
            # A bounded physical step can never teleport the body to a new
            # target at the 16-action target-change boundary.
            self.assertLess(max(abs(b-a) for a, b in zip(positions[:-1], positions[1:])), 1001)
            self.assertTrue(all(abs(p) <= 10000 for p in positions))
            self.assertGreaterEqual(result['contextAccuracy'], 0)
            self.assertLessEqual(result['contextAccuracy'], 1)
        self.assertEqual(stats['online_delay3']['deliveredRewards'], 157)
        self.assertEqual(stats['online_delay3']['pendingRewards'], 3)
        self.assertEqual(stats['online_immediate']['deliveredRewards'], 159)
        self.assertEqual(stats['online_immediate']['pendingRewards'], 1)
        self.assertEqual(stats['privileged_oracle']['contextAccuracy'], 1.0)

    def test_deterministic_and_all_seed_arm_runs_reported(self):
        config = dict(train_episodes=8, adapt_episodes=5, phase_steps=(33, 41, 47, 39), commit='test')
        a = experiment((0, 1), **config)
        b = experiment((0, 1), **config)
        self.assertEqual(validate(a), [])
        self.assertEqual(len(a['runs']), len(ARMS) * 2)
        for x, y in zip(a['runs'], b['runs']):
            self.assertEqual((x['arm'], x['seed'], x['status'], x['scores'], x.get('trace')),
                             (y['arm'], y['seed'], y['status'], y['scores'], y.get('trace')))
        self.assertTrue(all(r['status'] == 'ok' for r in a['runs']))

    def test_invalid_budgets_and_reward_corruption_rejected(self):
        mem = train_checkpoints(0, train_episodes=6, adapt_episodes=4)
        for value in (float('nan'), float('inf'), -0.1, 1, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                run_stream(mem, 'online_delay3', 0, noise=value)
        with self.assertRaises(ValueError):
            run_stream(mem, 'unknown', 0)
        with self.assertRaises(ValueError):
            experiment((0, 0))
        with self.assertRaises(ValueError):
            experiment((0,), phase_steps=(33, 41, 47))


if __name__ == '__main__':
    unittest.main()