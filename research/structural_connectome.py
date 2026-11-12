"""Coarse human-inspired structural wiring, independent of synaptic learning.

This is NOT a neuron-level human connectome. A schematic example is provided;
real atlas-derived, *undirected* topology can instead be loaded from CSV.
No functional synaptic weights are inferred from anatomical observations.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Region:
    id: str
    name: str
    hemisphere: str
    system: str
    xyz: tuple[float, float, float] | None = None


@dataclass(frozen=True)
class Connection:
    source: str
    target: str
    pathway: str
    evidence: str
    directed: bool

    @property
    def id(self) -> str:
        a, b = (self.source, self.target) if self.directed else sorted((self.source, self.target))
        return f"{a}|{b}|{self.pathway}|{'directed' if self.directed else 'undirected'}"


@dataclass
class StructuralGraph:
    regions: list[Region]
    connections: list[Connection]
    coordinate_space: str
    provenance: str
    model_kind: str

    def __post_init__(self) -> None:
        ids = [region.id for region in self.regions]
        if any(not value or "|" in value for value in ids) or len(set(ids)) != len(ids):
            raise ValueError("Region IDs must be unique, nonempty and contain no '|'")
        if not self.provenance.strip() or not self.model_kind.strip():
            raise ValueError("Provenance and model kind are required")
        for region in self.regions:
            if region.xyz is not None and (len(region.xyz) != 3 or not all(math.isfinite(v) for v in region.xyz)):
                raise ValueError(f"Invalid coordinates: {region.id}")
        edge_ids: set[str] = set()
        for edge in self.connections:
            if edge.source not in ids or edge.target not in ids or edge.source == edge.target:
                raise ValueError(f"Invalid endpoints for {edge.pathway}: {edge.source} -> {edge.target}")
            if not edge.pathway or "|" in edge.pathway or not edge.evidence:
                raise ValueError("Every edge needs an unambiguous pathway and evidence class")
            if edge.id in edge_ids:
                raise ValueError(f"Duplicate edge: {edge.id}")
            edge_ids.add(edge.id)

    def to_dict(self) -> dict:
        return {
            "format": "brain-structural-graph/1",
            "model_kind": self.model_kind,
            "provenance": self.provenance,
            "coordinate_space": self.coordinate_space,
            "regions": [asdict(region) for region in self.regions],
            "connections": [{**asdict(edge), "id": edge.id} for edge in self.connections],
            "weight_status": "unassigned; learning parameters must be kept separately",
        }

    def write_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")


class LearningWeights:
    """Independent empty slots for a future learner; not anatomical measurements."""

    def __init__(self, graph: StructuralGraph):
        self.values: dict[str, float | None] = {edge.id: None for edge in graph.connections}

    def set(self, edge_id: str, value: float) -> None:
        if edge_id not in self.values:
            raise KeyError(f"Unknown structural connection: {edge_id}")
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
            raise ValueError("Learning weight must be a finite real number")
        self.values[edge_id] = float(value)

    def write_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps({"format": "brain-learning-weights/1", "values": self.values}, indent=2) + "\n", encoding="utf-8")


# Coarse hypotheses about pathways, NOT tract-by-tract evidence or neural synapses.
# Directed edges denote an illustrative information flow, not MRI-inferred direction.
_REGIONS = (
    ("lgn", "Lateral geniculate nucleus", "thalamus"),
    ("v1", "Primary visual cortex", "cortex"),
    ("visual_assoc", "Visual association cortex", "cortex"),
    ("temporal_assoc", "Temporal association cortex", "cortex"),
    ("parietal_assoc", "Parietal association cortex", "cortex"),
    ("s1", "Primary somatosensory cortex", "cortex"),
    ("premotor", "Premotor cortex", "cortex"),
    ("m1", "Primary motor cortex", "cortex"),
    ("pfc", "Prefrontal cortex", "cortex"),
    ("thalamus", "Thalamus (simplified, excluding LGN)", "thalamus"),
    ("striatum", "Striatum", "basal_ganglia"),
    ("pallidum", "Globus pallidus (simplified)", "basal_ganglia"),
    ("stn", "Subthalamic nucleus", "basal_ganglia"),
    ("entorhinal", "Entorhinal cortex", "medial_temporal"),
    ("hippocampus", "Hippocampus", "medial_temporal"),
    ("amygdala", "Amygdala", "limbic"),
    ("pons", "Pontine nuclei", "brainstem"),
    ("cerebellar_cortex", "Cerebellar cortex", "cerebellum"),
    ("cerebellar_nuclei", "Deep cerebellar nuclei", "cerebellum"),
)

# Source, target, named coarse pathway. Some paths skip biological relays.
_PATHS = (
    ("lgn", "v1", "geniculostriate"),
    ("v1", "visual_assoc", "visual_feedforward"),
    ("visual_assoc", "v1", "visual_feedback"),
    ("visual_assoc", "temporal_assoc", "ventral_visual"),
    ("visual_assoc", "parietal_assoc", "dorsal_visual"),
    ("thalamus", "s1", "somatosensory_thalamocortical"),
    ("s1", "parietal_assoc", "somatosensory_association"),
    ("parietal_assoc", "pfc", "frontoparietal_forward"),
    ("pfc", "parietal_assoc", "frontoparietal_feedback"),
    ("pfc", "premotor", "prefrontal_premotor"),
    ("premotor", "m1", "premotor_motor"),
    ("pfc", "striatum", "corticostriatal"),
    ("m1", "striatum", "motor_corticostriatal"),
    ("striatum", "pallidum", "basal_ganglia_direct_simplified"),
    ("pallidum", "thalamus", "pallidothalamic"),
    ("thalamus", "pfc", "thalamo_prefrontal"),
    ("thalamus", "m1", "thalamo_motor"),
    ("pfc", "stn", "hyperdirect"),
    ("stn", "pallidum", "subthalamopallidal"),
    ("temporal_assoc", "entorhinal", "perirhinal_entorhinal_simplified"),
    ("entorhinal", "hippocampus", "perforant_path_simplified"),
    ("hippocampus", "entorhinal", "hippocampal_output_simplified"),
    ("amygdala", "pfc", "amygdalofrontal"),
    ("pfc", "amygdala", "frontoamygdalar"),
    ("m1", "pons", "corticopontine"),
    ("pons", "cerebellar_cortex", "pontocerebellar"),
    ("cerebellar_cortex", "cerebellar_nuclei", "purkinje_deep_nuclei"),
    ("cerebellar_nuclei", "thalamus", "cerebellothalamic_simplified"),
)

# Homotopic cortical commissural targets; these are NOT a complete callosal map.
_CALLOSAL = ("pfc", "m1", "s1", "premotor", "parietal_assoc", "temporal_assoc", "visual_assoc")


def make_schematic_graph() -> StructuralGraph:
    regions = [
        Region(f"{side}_{key}", name, side, system)
        for side in ("L", "R")
        for key, name, system in _REGIONS
    ]
    connections = [
        Connection(f"{side}_{src}", f"{side}_{dst}", pathway, "schematic-anatomical-pathway", True)
        for side in ("L", "R")
        for src, dst, pathway in _PATHS
    ]
    connections.extend(
        Connection(f"L_{key}", f"R_{key}", "corpus_callosum_schematic", "schematic-anatomical-pathway", False)
        for key in _CALLOSAL
    )
    return StructuralGraph(
        regions,
        connections,
        coordinate_space="none (no measured positions)",
        provenance="Illustrative macro-anatomical pathways; NOT measured subject connectivity",
        model_kind="human-inspired-schematic",
    )


def _regions_from_csv(path: str | Path) -> list[Region]:
    with Path(path).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not {"id", "name", "hemisphere", "system"}.issubset(reader.fieldnames or []):
            raise ValueError("Region CSV requires id,name,hemisphere,system")
        regions = []
        for row in reader:
            coords = [row.get(k, "").strip() for k in ("x", "y", "z")]
            if any(coords) and not all(coords):
                raise ValueError(f"Incomplete x,y,z for region {row['id']}")
            xyz = tuple(float(v) for v in coords) if all(coords) else None
            regions.append(Region(row["id"].strip(), row["name"].strip(), row["hemisphere"].strip(), row["system"].strip(), xyz))
        return regions


def load_undirected_matrix(
    matrix_path: str | Path,
    regions_path: str | Path,
    *,
    threshold: float = 0.0,
    provenance: str = "user-supplied matrix (not independently validated)",
    coordinate_space: str = "user-supplied atlas coordinates, units unspecified",
) -> StructuralGraph:
    """Binarize a symmetric structural matrix; observed values are NOT learned weights.

    CSV first row: region,A,B; subsequent rows A,... then B,...
    Matrices must be symmetric and nonnegative. Edges exist when value > threshold.
    """
    if not math.isfinite(threshold) or threshold < 0:
        raise ValueError("Threshold must be finite and nonnegative")
    regions = _regions_from_csv(regions_path)
    region_ids = [region.id for region in regions]
    with Path(matrix_path).open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None or header[0].strip() != "region" or header[1:] != region_ids:
            raise ValueError("Matrix header must be region,<region IDs in regions CSV order>")
        rows = list(reader)
    if len(rows) != len(region_ids):
        raise ValueError("Matrix must have one row per region")
    matrix = []
    for index, row in enumerate(rows):
        if len(row) != len(region_ids) + 1 or row[0] != region_ids[index]:
            raise ValueError("Matrix rows must match the region IDs in order")
        try:
            values = [float(value) for value in row[1:]]
        except ValueError as exc:
            raise ValueError("Matrix must contain numeric values") from exc
        if any(not math.isfinite(value) or value < 0 for value in values):
            raise ValueError("Matrix values must be finite and nonnegative")
        matrix.append(values)
    connections = []
    for i in range(len(region_ids)):
        if matrix[i][i] != 0:
            raise ValueError("Self-connections in the input matrix are not supported")
        for j in range(i + 1, len(region_ids)):
            if not math.isclose(matrix[i][j], matrix[j][i], rel_tol=1e-8, abs_tol=1e-10):
                raise ValueError("Matrix must be symmetric: diffusion MRI does not establish axonal direction")
            if matrix[i][j] > threshold:
                connections.append(Connection(region_ids[i], region_ids[j], "structural_matrix", "user-supplied-undirected-estimate", False))
    return StructuralGraph(regions, connections, coordinate_space, provenance, "thresholded-undirected-structural-matrix")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", help="CSV symmetric structural-connectivity matrix; omit for schematic")
    parser.add_argument("--regions", help="CSV region metadata: id,name,hemisphere,system,x,y,z")
    parser.add_argument("--threshold", type=float, default=0.0, help="Matrix-only: keep observations strictly above threshold")
    parser.add_argument("--provenance", default="user-supplied matrix (not independently validated)")
    parser.add_argument("--coordinate-space", default="user-supplied atlas coordinates, units unspecified")
    parser.add_argument("--out", required=True, help="Write graph JSON here")
    parser.add_argument("--weights-out", help="Optionally write separate, null-initialized learning weights")
    args = parser.parse_args()
    if bool(args.matrix) != bool(args.regions):
        parser.error("--matrix and --regions must be supplied together")
    if not args.matrix and args.threshold != 0.0:
        parser.error("--threshold only applies to --matrix")
    graph = (
        load_undirected_matrix(args.matrix, args.regions, threshold=args.threshold, provenance=args.provenance, coordinate_space=args.coordinate_space)
        if args.matrix
        else make_schematic_graph()
    )
    graph.write_json(args.out)
    if args.weights_out:
        LearningWeights(graph).write_json(args.weights_out)
    print(f"{graph.model_kind}: {len(graph.regions)} regions, {len(graph.connections)} structural connections; weights unassigned")


if __name__ == "__main__":
    main()
