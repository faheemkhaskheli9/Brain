"""Benchmark acceptance, reproducibility and frozen held-out evaluation checks."""

import unittest

from learn_sparse_brain import ARMS, experiment, paired_summary, run_seed


class LearningBenchmarkTests(unittest.TestCase):
    def test_short_run_is_complete_schema_and_budget_matched(self):
        data = experiment((2, 5), train_steps=140, eval_trials=25, commit='test-code')
        self.assertEqual(data['schema'], 'brain-result/1')
        self.assertEqual(len(data['runs']), len(ARMS)*2)
        for row in data['runs']:
            self.assertEqual(row['status'], 'ok')
            self.assertIn('checkpoint', row)
            self.assertEqual(row['scores']['synapses'], 4)
            self.assertLessEqual(row['scores']['candidateProducts'], 140*24*2)
        self.assertEqual(paired_summary(data)['status'], 'complete')

    def test_repeat_seed_identical_other_than_timing(self):
        def stable():
            return [{k:v for k,v in row.items() if k!='seconds'}
                    for row in run_seed(3, 180, 50)]
        self.assertEqual(stable(), stable())

    def test_genuinely_learned_missing_feature_on_exploratory_seed(self):
        out = {r['arm']:r for r in run_seed(2, 600, 100)}
        self.assertEqual(out['evidence']['status'], 'ok')
        self.assertGreater(out['evidence']['scores']['heldoutSuccess'], 0.85)
        self.assertGreater(out['evidence']['scores']['newSynapses'], 0)
        self.assertEqual(out['fixed']['scores']['newSynapses'], 0)
        self.assertEqual(out['frozen']['scores']['newSynapses'], 0)
        self.assertIn([0, 0], out['evidence']['connectionTopology'])

    def test_bad_seeds_rejected_without_running(self):
        for args in ((), (1, 1), (-1,), (True,)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                experiment(args, train_steps=100, eval_trials=50)


if __name__ == '__main__':
    unittest.main()