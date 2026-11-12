"""Microcircuit structural growth, reward-local plasticity and resource safety tests."""

import json
import math
import unittest
from dataclasses import replace

import numpy as np

from structural_plasticity import PlasticityConfig, SparsePlasticPolicy


class StructuralPlasticityTests(unittest.TestCase):
    def setUp(self):
        self.cfg = PlasticityConfig(inputs=4, max_edges=2, grow_every=2, warmup=2,
                                    candidate_min_score=0.001, min_prune_age=0,
                                    min_error_rate=0)

    def test_zero_edges_no_dense_parameter_allocation(self):
        brain = SparsePlasticPolicy(self.cfg, 1)
        self.assertEqual(brain.edges, {})
        self.assertEqual(brain.density, 0)
        self.assertEqual(brain.act(np.zeros(4, np.float32), explore=False), 0)
        self.assertEqual(brain.synaptic_products, 0)
        self.assertEqual(brain.candidates, {})

    def test_weight_changes_only_when_eligible_and_rewarded(self):
        b = SparsePlasticPolicy(self.cfg, 1, growth_mode='off', initial_edges=((0, 0), (2, 1)))
        before = b.edges[0, 0].weight
        unchanged = b.edges[2, 1].weight
        a = b.act(np.array([1, 0, 0, 0], np.float32))
        with self.assertRaises(RuntimeError):
            b.act(np.zeros(4, np.float32), explore=False)
        b.feedback(1)
        self.assertNotEqual(b.edges[0, 0].weight, before)
        self.assertEqual(b.edges[2, 1].weight, unchanged)
        self.assertEqual(b.edges[0, 0].updates, 1)
        self.assertEqual(b.edges[2, 1].updates, 0)
        self.assertIn(a, (0, 1))

    def test_absent_edge_grows_after_reward_correlated_activity(self):
        b = SparsePlasticPolicy(self.cfg, 1, initial_edges=((1, 0), (1, 1)))
        # Use public signals and externally supplied feedback, no target in policy.
        for _ in range(2):
            b.act(np.array([1, 0, 0, 0], np.float32))
            b.feedback(-1)
        self.assertTrue(any(i == 0 for i, _ in b.edges))
        self.assertEqual(len(b.edges), 2)
        self.assertGreaterEqual(b.new_edges, 1)
        self.assertGreaterEqual(b.removed_edges, 1)
        self.assertLessEqual(b.density, 0.25)

    def test_growth_only_if_needed_and_evidence(self):
        b = SparsePlasticPolicy(replace(self.cfg, min_error_rate=0.8), 3)
        for _ in range(4):
            b.act(np.array([1, 0, 0, 0], np.float32))
            b.feedback(1)
        self.assertEqual(b.new_edges, 0)
        self.assertEqual(b.edges, {})
        self.assertFalse(b.rewire())
        fixed = SparsePlasticPolicy(self.cfg, 3, growth_mode='off')
        for _ in range(4):
            fixed.act(np.array([1, 0, 0, 0], np.float32))
            fixed.feedback(-1)
        self.assertEqual(fixed.edges, {})

    def test_mature_edge_protection_and_budget(self):
        cfg = replace(self.cfg, min_prune_age=100, max_edges=1)
        b = SparsePlasticPolicy(cfg, 4, initial_edges=((1, 0),))
        for _ in range(4):
            b.act(np.array([1, 1, 0, 0], np.float32))
            b.feedback(-1)
        self.assertEqual(b.new_edges, 0)
        self.assertEqual(set(b.edges), {(1, 0)})
        self.assertLessEqual(len(b.candidates), cfg.max_candidates)

    def test_bounded_candidate_cache_with_more_features_than_budget(self):
        cfg = PlasticityConfig(inputs=60, max_edges=1, max_candidates=2, warmup=10000)
        b = SparsePlasticPolicy(cfg, 9)
        for n in range(10):
            data = np.zeros(cfg.inputs, np.float32)
            data[n:n+4] = 1
            b.act(data)
            b.feedback(-1)
            self.assertLessEqual(len(b.candidates), 2)
        self.assertGreater(b.candidate_evictions, 0)
        self.assertLessEqual(len(b.edges), 1)

    def test_delayed_reward_accumulates_decayed_eligibility(self):
        cfg = replace(self.cfg, max_delayed_steps=2)
        b = SparsePlasticPolicy(cfg, 5, initial_edges=((0, 0),))
        b.act(np.array([1, 0, 0, 0], np.float32))
        x = b.edges[0, 0].eligibility
        b.act(np.array([0, 1, 0, 0], np.float32))
        self.assertAlmostEqual(b.edges[0, 0].eligibility, cfg.eligibility_decay * x)
        with self.assertRaises(RuntimeError):
            b.act(np.ones(4, np.float32))
        b.feedback(-1)
        self.assertEqual(b.edges[0, 0].eligibility, 0)
        self.assertEqual(b._pending, 0)

    def test_state_round_trip_resumes_same_action_and_synapses(self):
        b = SparsePlasticPolicy(self.cfg, 13)
        for t in range(8):
            b.act(np.array([1, (-1)**t, 0, 0], np.float32))
            b.feedback(-1 if t % 2 else 1)
        restored = SparsePlasticPolicy.from_state(json.loads(json.dumps(b.export_state())))
        self.assertEqual(b.fingerprint(), restored.fingerprint())
        x = np.array([1, 0.2, -1, 0], np.float32)
        self.assertEqual(b.act(x), restored.act(x))
        b.feedback(-1)
        restored.feedback(-1)
        self.assertEqual(b.fingerprint(), restored.fingerprint())

    def test_invalid_checkpoint_fails_closed(self):
        net = SparsePlasticPolicy(self.cfg, 1)
        base = net.export_state()
        tests = [
            {'format': 'bad'},
            {**base, 'edges': [[0, 0, math.nan, 0, 0]]},
            {**base, 'edges': [[0, 0, 0.2, 0, 0], [0, 0, 0.2, 0, 0]]},
            {**base, 'edges': [[10, 0, 0.2, 0, 0]]},
            {**base, 'rng': ['bad']},
            {**base, 'recent_errors': [3]},
        ]
        for item in tests:
            with self.subTest(item=str(item)[:80]), self.assertRaises(ValueError):
                SparsePlasticPolicy.from_state(item)

    def test_validation_and_invalid_feedback_does_not_change_learning_state(self):
        for options in ({'inputs': 0}, {'max_edges': 100},
                        {'learning_rate': float('nan')}, {'max_candidates': 0}):
            with self.assertRaises(ValueError):
                PlasticityConfig(**options)
        b = SparsePlasticPolicy(self.cfg, 2)
        for bad in (np.array([1, 2], np.float32), np.array([math.nan, 0, 0, 0], np.float32),
                    np.array([2, 0, 0, 0], np.float32), np.array([1, 0, 0, 0], np.int64)):
            with self.assertRaises(ValueError):
                b.act(bad)
        with self.assertRaises(RuntimeError):
            b.feedback(-1)
        b.act(np.ones(4, np.float32))
        for invalid in (math.nan, float('inf'), 2, True):
            with self.assertRaises(ValueError):
                b.feedback(invalid)
        self.assertEqual(b.feedback_steps, 0)
        b.reset()
        self.assertEqual(b._pending, 0)

    def test_no_anatomical_long_range_edges_are_created(self):
        # Microcircuit only, structural graph is a distinct immutable object.
        from structural_connectome import make_schematic_graph
        g = make_schematic_graph()
        old = g.to_dict()
        b = SparsePlasticPolicy(self.cfg, 1)
        for _ in range(4):
            b.act(np.array([1, 0, 0, 0], np.float32))
            b.feedback(-1)
        self.assertEqual(g.to_dict(), old)


if __name__ == '__main__':
    unittest.main()