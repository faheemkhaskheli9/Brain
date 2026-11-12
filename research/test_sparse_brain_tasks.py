"""Privacy of verifier labels, deterministic split separation and task solvability."""

import unittest

import numpy as np

from sparse_brain_tasks import trials


class ToyTasksTests(unittest.TestCase):
    def test_reproducible_split_and_label_is_not_in_observation_contract(self):
        a = trials('train', 5, 200)
        self.assertEqual(a, trials('train', 5, 200))
        self.assertTrue(all(len(trial.features) == 24 for trial in a))
        self.assertTrue(all(trial.observe().shape == (24,) for trial in a))
        self.assertTrue(all(trial.observe().dtype == np.float32 for trial in a))
        # Independent verifier's answer must not be passed to a learning model.
        self.assertIsInstance(a[0].observe(), np.ndarray)

    def test_task_families_are_disjoint_and_rule_generalizes(self):
        a, b, c = (trials(split, 7, 200) for split in ('train', 'dev', 'eval'))
        ids = [set(t.key for t in block) for block in (a, b, c)]
        self.assertFalse((ids[0] & ids[1]) or (ids[0] & ids[2]) or (ids[1] & ids[2]))
        self.assertEqual({round(abs(t.features[0]), 1) for t in a}, {1.0})
        self.assertEqual({round(abs(t.features[0]), 1) for t in b}, {0.7})
        self.assertEqual({round(abs(t.features[0]), 1) for t in c}, {0.5})
        for task in a + b + c:
            # Oracle for feasibility/upper bound only, never fed to the model.
            action = 0 if task.observe()[0] > 0 else 1
            self.assertEqual(task.reward(action), 1)
            self.assertEqual(task.reward(1-action), -1)

    def test_invalid_inputs_fail(self):
        for split, seed, count in [('bad', 0, 1), ('train', True, 1), ('train', 0, 0)]:
            with self.assertRaises(ValueError):
                trials(split, seed, count)
        with self.assertRaises(ValueError):
            trials('eval', 3, 1)[0].reward(2)
        with self.assertRaises(ValueError):
            trials('eval', 3, 1)[0].reward(True)


if __name__ == '__main__':
    unittest.main()