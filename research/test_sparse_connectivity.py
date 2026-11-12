"""Sparse regional connectivity regression and adversarial tests (no neuroscience claims)."""

import math
import random
import unittest

from sparse_connectivity import SparseConnectivity, make_sparse_schematic
from structural_connectome import Connection, LearningWeights, Region, StructuralGraph, make_schematic_graph
from sensorimotor_bridge import SensoryPacket, SensorimotorLoop


class SparseConnectivityTests(unittest.TestCase):
    def setUp(self):
        self.graph = make_schematic_graph()
        self.weights = LearningWeights(self.graph)
        self.network = SparseConnectivity(self.graph, self.weights)

    def weight(self, src, dst, value, *, pathway=None):
        edges = [edge for edge in self.graph.connections if edge.source == src and edge.target == dst
                 and (pathway is None or edge.pathway == pathway)]
        self.assertEqual(len(edges), 1)
        self.weights.set(edges[0].id, value)
        return edges[0].id

    def test_topology_is_genuinely_sparse_without_dense_matrix(self):
        s = self.network.topology
        self.assertEqual((s.regions, s.structural_edges, s.directed_arcs), (78, 142, 154))
        self.assertEqual(s.possible_directed_arcs, 78 * 77)
        self.assertLess(s.density, 0.03)
        self.assertEqual(sum(len(a) for a in self.network.adjacency.values()), 154)
        self.assertTrue(all(not isinstance(a, dict) for a in self.network.adjacency.values()))
        self.assertTrue(all(v is None for v in self.weights.values.values()))

    def test_unassigned_and_zero_weights_do_not_propagate(self):
        result = self.network.step({'L_v1': 0.8})
        self.assertEqual(result.activity, {})
        self.assertGreater(result.stats.examined_arcs, 0)
        self.assertEqual(result.stats.weighted_products, 0)
        eid = self.weight('L_v1', 'L_visual_assoc', 0)
        self.assertEqual(self.network.step({'L_v1': 0.8}).activity, {})
        self.weights.set(eid, 0.8)
        self.assertAlmostEqual(self.network.step({'L_v1': 0.8}).activity['L_visual_assoc'], 0.64)

    def test_no_activity_scans_no_connections(self):
        self.weight('L_v1', 'L_visual_assoc', 0.8)
        for input_activity in ({}, {'L_v1': 0}, {'L_v1': 0.01}):
            r = self.network.step(input_activity)
            self.assertEqual(r.activity, {})
            self.assertEqual((r.stats.examined_arcs, r.stats.weighted_products), (0, 0))

    def test_unrelated_sensory_modules_are_not_visited(self):
        self.weight('L_v1', 'L_visual_assoc', 0.5)
        self.weight('R_a1', 'R_auditory_assoc', 0.5)
        r = self.network.step({'L_v1': 1})
        self.assertEqual(r.activity, {'L_visual_assoc': 0.5})
        self.assertEqual(r.stats.examined_arcs, len(self.network.adjacency['L_v1']))
        self.assertLess(r.stats.examined_arcs, self.network.topology.directed_arcs)

    def test_undirected_uses_one_weight_slot_for_both_directions(self):
        edge = next(edge for edge in self.graph.connections if edge.pathway == 'corpus_callosum_schematic')
        self.weights.set(edge.id, 0.4)
        self.assertEqual(self.network.step({edge.source: 1}).activity.get(edge.target), 0.4)
        self.assertEqual(self.network.step({edge.target: 1}).activity.get(edge.source), 0.4)

    def test_directed_does_not_implicitly_reverse(self):
        self.weight('L_lgn', 'L_v1', 0.5)
        self.assertEqual(self.network.step({'L_lgn': 1}).activity, {'L_v1': 0.5})
        self.assertEqual(self.network.step({'L_v1': 1}).activity, {})

    def test_dynamic_enable_and_disable_does_not_delete_topology(self):
        edge_id = self.weight('L_lgn', 'L_v1', 0.5)
        self.network.set_enabled(edge_id, False)
        self.assertEqual(self.network.step({'L_lgn': 1}).activity, {})
        self.assertEqual(len(self.graph.connections), 142)
        self.network.set_enabled(edge_id, True)
        self.assertEqual(self.network.step({'L_lgn': 1}).activity, {'L_v1': 0.5})

    def test_multihop_requires_each_intermediate_weight(self):
        self.weight('L_v1', 'L_visual_assoc', 0.8)
        trace = self.network.propagate({'L_v1': 1}, hops=3)
        self.assertEqual(len(trace), 2)
        self.assertEqual(trace[0].activity, {'L_visual_assoc': 0.8})
        self.assertEqual(trace[1].activity, {})
        self.weight('L_visual_assoc', 'L_temporal_assoc', 0.5)
        trace = self.network.propagate({'L_v1': 1}, hops=2)
        self.assertEqual(trace[1].activity, {'L_temporal_assoc': 0.4})

    def test_fanout_chooses_largest_magnitudes_and_is_reproducible(self):
        # Use a synthetic star to ensure multiple candidate outgoing synapses.
        regions = [Region(x, x, 'L', 'test') for x in ('A', 'B', 'C')]
        edges = [Connection('A', 'B', 'AB', 'test', True), Connection('A', 'C', 'AC', 'test', True)]
        graph = StructuralGraph(regions, edges, 'none', 'unit test', 'synthetic')
        w = LearningWeights(graph)
        w.set(edges[0].id, 0.3)
        w.set(edges[1].id, -0.9)
        star = SparseConnectivity(graph, w, max_fanout=1, contribution_threshold=0)
        self.assertEqual(star.step({'A': 1}).activity, {'C': -0.9})
        self.assertEqual(star.step({'A': 1}).stats.delivered_events, 1)
        # Tie-breaking picks lexicographically smaller edge ID consistently.
        w.set(edges[1].id, -0.3)
        self.assertEqual(star.step({'A': 1}).activity, {'B': 0.3})

    def test_negative_canceling_and_saturation(self):
        regs = [Region(x, x, 'L', 'test') for x in ('A', 'B', 'C')]
        edges = [Connection('A', 'C', 'AC', 'test', True), Connection('B', 'C', 'BC', 'test', True)]
        graph = StructuralGraph(regs, edges, 'none', 'test', 'test')
        w = LearningWeights(graph)
        net = SparseConnectivity(graph, w, contribution_threshold=0)
        for e in edges:
            w.set(e.id, 0.8)
        self.assertEqual(net.step({'A': 1, 'B': 1}).activity, {'C': 1.0})
        w.set(edges[1].id, -0.8)
        self.assertEqual(net.step({'A': 1, 'B': 1}).activity, {})

    def test_input_validation_and_weight_guard(self):
        for invalid in ({'unknown': 0.5}, {'L_v1': math.nan}, {'L_v1': 3}, {'L_v1': True}):
            with self.subTest(input=invalid), self.assertRaises((ValueError, KeyError)):
                self.network.step(invalid)
        for invalid in (-1, 2, math.inf, math.nan, True):
            with self.assertRaises(ValueError):
                SparseConnectivity(self.graph, self.weights, activation_threshold=invalid)
        with self.assertRaises(ValueError):
            SparseConnectivity(self.graph, LearningWeights(StructuralGraph(
                [Region('x', 'x', 'L', 'test')], [], 'none', 'test', 'test')))
        with self.assertRaises(ValueError):
            SparseConnectivity(self.graph, self.weights, max_fanout=0)
        with self.assertRaises(ValueError):
            self.network.set_enabled(self.graph.connections[0].id, 'yes')
        with self.assertRaises(KeyError):
            self.network.set_enabled('nonexistent', False)
        with self.assertRaises(ValueError):
            self.network.propagate({}, hops=0)
        e = self.graph.connections[0]
        self.weights.values[e.id] = math.nan
        with self.assertRaises(ValueError):
            self.network.step({e.source: 1})

    def test_sensory_packets_vision_text_and_silent_change(self):
        router = SensorimotorLoop(self.graph)
        packets = router.sensors.route({'vision_pixels': {'L': [0.25] * 192},
                                        'text_symbols': {'L': [0.5] * 33},
                                        'visual_change': {'R': [0] * 192}})
        activity = self.network.input_packets(packets)
        self.assertEqual(activity, {'L_v1': 0.25, 'L_language_temporal': 0.5, 'R_visual_assoc': 0.0})
        self.weight('L_v1', 'L_visual_assoc', 0.8)
        self.weight('L_language_temporal', 'L_language_frontal', 0.6)
        routed = self.network.step(activity)
        self.assertEqual(routed.activity, {'L_language_frontal': 0.3, 'L_visual_assoc': 0.2})

    def test_dense_reference_equivalence_without_gating(self):
        # Dense multiplication reference, *only* for mathematical comparison.
        rng = random.Random(2026)
        net = SparseConnectivity(self.graph, self.weights, max_fanout=None,
                                 activation_threshold=0, contribution_threshold=0)
        ids = [r.id for r in self.graph.regions]
        matrix = [[0.0] * len(ids) for _ in ids]
        index = {value: i for i, value in enumerate(ids)}
        for edge in self.graph.connections:
            value = rng.uniform(-0.6, 0.6)
            self.weights.set(edge.id, value)
            matrix[index[edge.source]][index[edge.target]] += value
            if not edge.directed:
                matrix[index[edge.target]][index[edge.source]] += value
        sources = {r: rng.uniform(-0.95, 0.95) for r in ids}
        sparse = net.step(sources)
        dense = {}
        for target, _ in enumerate(ids):
            value = sum(sources[ids[src]] * matrix[src][target] for src in range(len(ids)))
            value = max(-1.0, min(1.0, value))
            if value != 0:
                dense[ids[target]] = value
        self.assertEqual(set(sparse.activity), set(dense))
        for key in dense:
            self.assertAlmostEqual(sparse.activity[key], dense[key], places=12)
        self.assertEqual(sparse.stats.examined_arcs, net.topology.directed_arcs)
        self.assertLess(net.topology.directed_arcs, net.topology.possible_directed_arcs)

    def test_dormant_scaling_is_constant_in_edge_work(self):
        for seed in range(10):
            rng = random.Random(seed)
            activity = {region.id: rng.uniform(0.2, 1.0) for region in rng.sample(self.graph.regions, 2)}
            result = self.network.step(activity)
            self.assertEqual(result.stats.examined_arcs,
                             sum(len(self.network.adjacency[region]) for region in activity))
            self.assertLess(result.stats.examined_arcs, self.network.topology.directed_arcs)


if __name__ == '__main__':
    unittest.main()
