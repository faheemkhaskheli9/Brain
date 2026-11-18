"""Stream is single-lived, no resettable policy probes, with phase hidden."""
import unittest

from evaluate_online_context import ARMS, experiment, make_phases, run_seed, run_stream, seeded_phase_steps, train_checkpoints
from online_context import OnlineConfig
from result_schema import validate


class OnlineEvaluationTests(unittest.TestCase):
    def test_no_labels_or_boundaries_in_selector(self):
        selector = OnlineConfig()
        self.assertFalse(hasattr(selector, 'inverted_motor'))
        phase = make_phases(3, (25, 30, 27, 33))
        self.assertEqual(len(phase), 115)
        self.assertFalse(phase[0])
        self.assertTrue(phase[25])
        self.assertFalse(phase[55])
        with self.assertRaises(ValueError):
            make_phases(-1)
        schedule = seeded_phase_steps(7)
        self.assertEqual(schedule, seeded_phase_steps(7))
        self.assertNotEqual(schedule, seeded_phase_steps(8))
        self.assertTrue(all(sum(schedule[:k]) % 16 != 0 for k in (1, 2, 3)))

    def test_every_arm_same_real_action_budget_and_shared_frozen_memory(self):
        mem = train_checkpoints(0, train_episodes=8, adapt_episodes=6)
        before = mem.digest()
        rows = [run_stream(mem, name, 0, phase_steps=(29, 35, 39, 33), noise=0.15)
                for name in ARMS]
        self.assertEqual(mem.digest(), before)
        for d in rows:
            self.assertEqual(d['actions'], 136)
            self.assertEqual(d['rewardCalls'], 136)
            self.assertEqual(d['extraProbeActions'], 0)
            self.assertEqual(len(d['trace']['selected']), 136)
            self.assertEqual(d['trace']['phaseLengths'], [29, 35, 39, 33])
            self.assertGreaterEqual(d['contextAccuracy'], 0)
            self.assertLessEqual(d['contextAccuracy'], 1)
        self.assertEqual(rows[-1]['contextAccuracy'], 1)
        self.assertEqual(rows[-1]['meanPostSwitchDelay'], 0)

    def test_reproducible_seed_and_schema(self):
        a = experiment((0, 1), train_episodes=7, adapt_episodes=5,
                       phase_steps=(33, 41, 47, 39), noise=0.1, commit='test')
        b = experiment((0, 1), train_episodes=7, adapt_episodes=5,
                       phase_steps=(33, 41, 47, 39), noise=0.1, commit='test')
        self.assertEqual(validate(a), [])
        self.assertEqual([(r['scores'], r['trace'], r['checkpoint']) for r in a['runs']],
                         [(r['scores'], r['trace'], r['checkpoint']) for r in b['runs']])
        self.assertEqual(len(a['runs']), 2 * len(ARMS))
        self.assertEqual([row['arm'] for row in a['runs'][:len(ARMS)]], list(ARMS))

    def test_noise_budget_and_rejected_invalid_inputs(self):
        mem = train_checkpoints(0, train_episodes=6, adapt_episodes=4)
        with self.assertRaises(ValueError):
            run_stream(mem, 'online_reward', 0, noise=1.1)
        with self.assertRaises(ValueError):
            run_stream(mem, 'online_reward', 0, noise=float('nan'))
        with self.assertRaises(ValueError):
            run_stream(mem, 'broken', 0)
        with self.assertRaises(ValueError):
            run_stream(mem, 'online_reward', 0, phase_steps=(20, 30, 30, 30))
        with self.assertRaises(ValueError):
            run_seed(-1)
        with self.assertRaises(ValueError):
            experiment((1, 1))


if __name__ == '__main__':
    unittest.main()