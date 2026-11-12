"""Deterministic tests for the structural, untrained human-inspired graph."""

import csv
import json
import math
import tempfile
import unittest
from pathlib import Path

from structural_connectome import Connection, LearningWeights, Region, StructuralGraph, load_undirected_matrix, make_schematic_graph


class StructuralConnectomeTests(unittest.TestCase):
    def setUp(self):
        self.graph = make_schematic_graph()

    def test_scaffold_has_bilateral_regions_and_callosal_paths(self):
        self.assertEqual(len(self.graph.regions), 38)
        self.assertEqual(len(self.graph.connections), 2 * 28 + 7)
        self.assertEqual(len({e.id for e in self.graph.connections}), len(self.graph.connections))
        self.assertTrue(any(e.pathway == "corpus_callosum_schematic" and not e.directed for e in self.graph.connections))

    def test_scaffold_does_not_pretend_to_have_empirical_coordinates_or_weights(self):
        self.assertTrue(all(r.xyz is None for r in self.graph.regions))
        exported = self.graph.to_dict()
        self.assertTrue(all("weight" not in e for e in exported["connections"]))
        self.assertTrue(all(e["evidence"].startswith("schematic") for e in exported["connections"]))

    def test_empty_learning_slots_separate_from_structure(self):
        weights = LearningWeights(self.graph)
        self.assertTrue(all(v is None for v in weights.values.values()))
        edge_id = self.graph.connections[0].id
        weights.set(edge_id, -0.25)
        self.assertEqual(weights.values[edge_id], -0.25)
        self.assertNotIn("weights", self.graph.to_dict())
        with self.assertRaises(KeyError):
            weights.set("not-an-edge", 1)
        for value in (float("nan"), float("inf"), True, "0.2"):
            with self.assertRaises(ValueError):
                weights.set(edge_id, value)

    def test_invalid_structural_graphs_fail(self):
        r = [Region("a", "a", "L", "cortex"), Region("b", "b", "R", "cortex")]
        with self.assertRaises(ValueError):
            StructuralGraph(r + [r[0]], [], "none", "source", "type")
        with self.assertRaises(ValueError):
            StructuralGraph(r, [Connection("a", "missing", "path", "label", True)], "none", "source", "type")
        with self.assertRaises(ValueError):
            StructuralGraph(r, [Connection("a", "a", "path", "label", True)], "none", "source", "type")
        e = Connection("a", "b", "path", "label", False)
        with self.assertRaises(ValueError):
            StructuralGraph(r, [e, Connection("b", "a", "path", "label", False)], "none", "source", "type")
        with self.assertRaises(ValueError):
            StructuralGraph([Region("a", "a", "L", "cortex", (1, math.nan, 3))], [], "none", "source", "type")

    def create_matrix(self, directory, matrix, region_ids=("A", "B", "C"), *, header=None):
        region_path = directory / "regions.csv"
        matrix_path = directory / "matrix.csv"
        with region_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name", "hemisphere", "system", "x", "y", "z"])
            for key in region_ids:
                writer.writerow([key, key, "L", "cortex", "0", "1", "2"])
        with matrix_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(header or ["region", *region_ids])
            for name, row in zip(region_ids, matrix):
                writer.writerow([name, *row])
        return matrix_path, region_path

    def test_matrix_import_binarizes_without_using_anatomical_values_as_synaptic_weights(self):
        with tempfile.TemporaryDirectory() as path:
            directory = Path(path)
            matrix_path, region_path = self.create_matrix(directory, [[0, 10, 0], [10, 0, 2], [0, 2, 0]])
            graph = load_undirected_matrix(matrix_path, region_path, threshold=3.0, provenance="test study")
            self.assertEqual(len(graph.connections), 1)
            self.assertEqual((graph.connections[0].source, graph.connections[0].target), ("A", "B"))
            self.assertFalse(graph.connections[0].directed)
            self.assertEqual(graph.regions[0].xyz, (0.0, 1.0, 2.0))
            self.assertIsNone(LearningWeights(graph).values[graph.connections[0].id])
            self.assertNotIn("10", json.dumps(graph.to_dict()["connections"]))
            graph.write_json(directory / "graph.json")
            self.assertEqual(json.loads((directory / "graph.json").read_text())["format"], "brain-structural-graph/1")

    def test_matrix_threshold_is_strict_and_isolates_allowed(self):
        with tempfile.TemporaryDirectory() as path:
            matrix_path, region_path = self.create_matrix(Path(path), [[0, 2, 0], [2, 0, 0], [0, 0, 0]])
            graph = load_undirected_matrix(matrix_path, region_path, threshold=2)
            self.assertEqual(len(graph.connections), 0)
            self.assertEqual(len(graph.regions), 3)

    def test_rejects_asymmetric_negative_nonfinite_nonzero_diagonal_and_bad_header(self):
        bad_matrices = [
            [[0, 1, 0], [0, 0, 0], [0, 0, 0]],
            [[0, -1, 0], [-1, 0, 0], [0, 0, 0]],
            [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
            [[0, float("nan"), 0], [float("nan"), 0, 0], [0, 0, 0]],
            [[0, float("inf"), 0], [float("inf"), 0, 0], [0, 0, 0]],
        ]
        with tempfile.TemporaryDirectory() as path:
            for matrix in bad_matrices:
                matrix_path, region_path = self.create_matrix(Path(path), matrix)
                with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                    load_undirected_matrix(matrix_path, region_path)
            matrix_path, region_path = self.create_matrix(Path(path), [[0, 0, 0]] * 3, header=["region", "B", "A", "C"])
            with self.assertRaises(ValueError):
                load_undirected_matrix(matrix_path, region_path)
            for threshold in (-1, float("nan"), float("inf")):
                with self.assertRaises(ValueError):
                    load_undirected_matrix(matrix_path, region_path, threshold=threshold)

    def test_output_is_deterministic(self):
        graph1 = make_schematic_graph().to_dict()
        graph2 = make_schematic_graph().to_dict()
        self.assertEqual(graph1, graph2)


if __name__ == "__main__":
    unittest.main()
