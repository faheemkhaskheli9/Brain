"""Scientific check: reward-only policy retrieval cannot alter frozen checkpoints."""

import json
import unittest

from evaluate_context_memory import ARMS, experiment, run_seed, summarize
from result_schema import validate


class ContextEvaluationTests(unittest.TestCase):
    def test_all_arms_use_shared_training_and_frozen_source(self):
        rows = run_seed(0, train_episodes=8, adapt_episodes=5,
                        eval_episodes=5, probe_trials=3, probe_steps=3)
        self.assertEqual([r['arm'] for r in rows], list(ARMS))
        self.assertTrue(all(r['status'] == 'ok' for r in rows), rows)
        self.assertEqual(len({r['sourceCheckpoint'] for r in rows}), 1)
        self.assertEqual(len({r['checkpoint'] for r in rows}), 1)
        self.assertEqual(len({r['scores']['sourceBefore'] for r in rows}), 1)
        for row in rows:
            stats = row['scores']
            self.assertEqual(stats['probeActions'], 0 if row['arm'] == 'single' else 36)
            self.assertGreaterEqual(stats['returnSuccess'], 0)
            self.assertLessEqual(stats['returnSuccess'], 1)
        self.assertEqual(rows[-1]['selected'], [1, 0])  # privileged only

    def test_deterministic_checkpoint_selection_and_result_schema(self):
        a = experiment((1, 2), train_episodes=8, adapt_episodes=5,
                       eval_episodes=6, probe_trials=3, probe_steps=2, commit='test')
        b = experiment((1, 2), train_episodes=8, adapt_episodes=5,
                       eval_episodes=6, probe_trials=3, probe_steps=2, commit='test')
        self.assertEqual([(x['arm'], x['scores'], x['checkpoint'], x['selected']) for x in a['runs']],
                         [(x['arm'], x['scores'], x['checkpoint'], x['selected']) for x in b['runs']])
        self.assertEqual(validate(a), [])
        self.assertTrue(summarize(a)['complete'])
        self.assertTrue(json.dumps(a))

    def test_invalid_configuration_rejected(self):
        with self.assertRaises(ValueError):
            run_seed(-1)
        with self.assertRaises(ValueError):
            run_seed(0, probe_trials=33)
        with self.assertRaises(ValueError):
            experiment((1, 1))


if __name__ == '__main__':
    unittest.main()