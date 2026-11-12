"""Safety, strict causal updates and deterministic context switching tests."""
import copy
import unittest

from online_context import OnlineConfig, OnlineRewardSelector


class SelectorTests(unittest.TestCase):
    def test_negative_reward_switches_only_after_live_actions(self):
        selector = OnlineRewardSelector(OnlineConfig(window=3, low_mean=-0.5, min_dwell=5))
        indices = []
        for reward in [-1, -1, -1, -1, -1, 1, 1, 1, -1, -1, -1, -1, -1]:
            indices.append(selector.select())
            selector.feedback(reward)
        self.assertEqual(indices[:5], [0] * 5)
        self.assertEqual(indices[5:10], [1] * 5)
        self.assertEqual(indices[-3:], [1, 0, 0])
        self.assertEqual(selector.switches, 2)
        self.assertEqual(selector.actions, 13)

    def test_no_phase_leak_and_no_uncharged_feedback(self):
        detector = OnlineRewardSelector()
        with self.assertRaises(RuntimeError):
            detector.feedback(-1)
        first = detector.select()
        self.assertEqual(first, 0)
        with self.assertRaises(RuntimeError):
            detector.select()
        with self.assertRaises(ValueError):
            detector.feedback(float('nan'))
        with self.assertRaises(ValueError):
            detector.feedback(2)
        with self.assertRaises(RuntimeError):
            detector.snapshot()
        self.assertEqual(detector.active, 0)
        detector.feedback(-1)

    def test_state_persistence_no_reward_fabrication(self):
        cfg = OnlineConfig(window=3, min_dwell=4, low_mean=-0.4, max_switches=1)
        source = OnlineRewardSelector(cfg)
        for reward in (-1, 1, -1, -1):
            source.select()
            source.feedback(reward)
        encoded = source.snapshot()
        restored = OnlineRewardSelector.from_state(copy.deepcopy(encoded))
        self.assertEqual(restored.snapshot(), encoded)
        for reward in (1, -1, -1, -1, -1, -1, -1):
            self.assertEqual(restored.select(), source.select())
            self.assertEqual(restored.feedback(reward), source.feedback(reward))
        self.assertEqual(restored.snapshot(), source.snapshot())
        self.assertLessEqual(restored.switches, 1)

    def test_reject_corrupt_state_and_invalid_initial(self):
        base = OnlineRewardSelector().snapshot()
        for key, value in [('active', 2), ('actions', -1), ('switches', 1000),
                           ('last_switch', 1), ('history', [float('nan')]),
                           ('history', [0] * 100), ('config', {'window': 0})]:
            bad = copy.deepcopy(base)
            bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                OnlineRewardSelector.from_state(bad)
        with self.assertRaises(ValueError):
            OnlineRewardSelector(initial=True)
        with self.assertRaises(ValueError):
            OnlineConfig(low_mean=float('inf'))
        with self.assertRaises(ValueError):
            OnlineConfig(min_dwell=0)


if __name__ == '__main__':
    unittest.main()