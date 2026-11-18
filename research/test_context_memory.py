"""No hidden-context leakage, bounded memory, independent policy snapshots."""

import copy
import json
import unittest

from closed_loop_reach import ReachBody, reach_trials, run_episodes
from context_memory import SparseContextMemory
from learn_reach import policy_for
from structural_plasticity import SparsePlasticPolicy


class ContextMemoryTests(unittest.TestCase):
    def policies(self):
        old = policy_for('evidence', 0)
        run_episodes(old, reach_trials('train', 0, 100), learn=True)
        reversed_policy = SparsePlasticPolicy.from_state(old.export_state())
        run_episodes(reversed_policy, reach_trials('dev', 6001, 40), learn=True, inverted_motor=True)
        return old, reversed_policy

    def test_memory_snapshots_detached_and_exactly_saved(self):
        old, new = self.policies()
        memory = SparseContextMemory(capacity=2)
        memory.add(old)
        memory.add(new)
        saved = memory.digest()
        self.assertNotEqual(old.fingerprint(), new.fingerprint())
        cloned = memory.policy(0)
        run_episodes(cloned, reach_trials('train', 222, 2), learn=True)
        self.assertEqual(saved, memory.digest())
        self.assertEqual(memory.size, 2)
        self.assertLess(memory.checkpoint_bytes, 20000)
        state = json.loads(json.dumps(memory.export_state()))
        self.assertEqual(memory.digest(), SparseContextMemory.from_state(state).digest())
        state['slots'][0]['edges'] = []
        self.assertEqual(saved, memory.digest())

    def test_selects_context_by_observed_outcome_not_motor_inversion(self):
        old, new = self.policies()
        memory = SparseContextMemory()
        memory.add(old)
        memory.add(new)
        probes = reach_trials('dev', 90123, 6)
        initial = memory.digest()
        normal = memory.retrieve(probes, lambda t: ReachBody(t), steps=3)
        flipped = memory.retrieve(probes, lambda t: InvertedBody(t), steps=3)
        self.assertEqual(normal.index, 0)
        self.assertEqual(flipped.index, 1)
        self.assertEqual(normal.probe_actions, 36)
        self.assertEqual(flipped.probe_rewards, 36)
        self.assertEqual(initial, memory.digest())

    def test_rejects_eval_leakage_and_corrupt_memory(self):
        old, _ = self.policies()
        memory = SparseContextMemory()
        memory.add(old)
        with self.assertRaises(ValueError):
            memory.retrieve(reach_trials('eval', 22, 2), ReachBody)
        with self.assertRaises(ValueError):
            memory.retrieve(reach_trials('train', 22, 2), ReachBody)
        with self.assertRaises(ValueError):
            memory.retrieve(tuple(), ReachBody)
        with self.assertRaises(ValueError):
            memory.retrieve(reach_trials('dev', 22, 1), ReachBody, steps=9)
        with self.assertRaises(RuntimeError):
            memory.add(old)
            memory.add(old)
        valid = SparseContextMemory()
        valid.add(old)
        checkpoint = valid.export_state()
        bad = copy.deepcopy(checkpoint)
        bad['slots'][0]['edges'][0][0] = 1000
        with self.assertRaises(ValueError):
            SparseContextMemory.from_state(bad)
        bad = copy.deepcopy(checkpoint)
        bad['slots'].append(bad['slots'][0]); bad['slots'].append(bad['slots'][0])
        with self.assertRaises(ValueError):
            SparseContextMemory.from_state(bad)
        with self.assertRaises(ValueError):
            SparseContextMemory(capacity=True)


class InvertedBody(ReachBody):
    def act(self, action: int, *, inverted_motor: bool = False) -> float:
        return super().act(action, inverted_motor=True)


if __name__ == '__main__':
    unittest.main()