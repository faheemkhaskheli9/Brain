"""Event-driven sparse propagation on the *schematic regional* structural graph.

This is a testable engineering router, not a neuron, brain, or learning model.
Topology stores only anatomically proposed edges; weight values are supplied by
an external learner. No weight is fabricated or trained by this module.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real
from typing import TYPE_CHECKING, Mapping

from structural_connectome import LearningWeights, StructuralGraph, make_schematic_graph

if TYPE_CHECKING:
    from sensorimotor_bridge import SensoryPacket


def _bounded(value: float, label: str, *, signed: bool = True) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite real number")
    result = float(value)
    if signed and not -1 <= result <= 1:
        raise ValueError(f"{label} must be in [-1, 1]")
    if not signed and not 0 <= result <= 1:
        raise ValueError(f"{label} must be in [0, 1]")
    return result


@dataclass(frozen=True)
class TopologyStats:
    regions: int
    structural_edges: int
    directed_arcs: int
    possible_directed_arcs: int
    density: float


@dataclass(frozen=True)
class RoutingStats:
    active_sources: int
    examined_arcs: int
    weighted_products: int
    delivered_events: int
    active_targets: int


@dataclass(frozen=True)
class RoutingStep:
    activity: dict[str, float]
    stats: RoutingStats


class SparseConnectivity:
    """Sparse adjacency + event-gated weighted routing, without a dense N×N array.

    Every *structural* connection has a unique ID, even when there are multiple
    pathways between the same regions. Undirected connections create two arcs
    sharing one weight slot. Missing / None weights do not transmit.

    max_fanout is an **activity gate**, not physical axon pruning. As it depends
    on supplied weights and signals, it is a hypothetical algorithm, not a
    known biological mechanism. Disabling a connection is also reversible.
    """

    def __init__(
        self,
        graph: StructuralGraph,
        weights: LearningWeights,
        *,
        max_fanout: int | None = 4,
        activation_threshold: float = 0.01,
        contribution_threshold: float = 0.01,
    ) -> None:
        if max_fanout is not None and (isinstance(max_fanout, bool) or not isinstance(max_fanout, int)
                                   or max_fanout < 1):
            raise ValueError("max_fanout must be a positive integer or None")
        self.activation_threshold = _bounded(activation_threshold, "activation_threshold", signed=False)
        self.contribution_threshold = _bounded(contribution_threshold, "contribution_threshold", signed=False)
        self.max_fanout = max_fanout
        edge_ids = {edge.id for edge in graph.connections}
        if set(weights.values) != edge_ids:
            raise ValueError("Weight slots must match the selected structural graph exactly")
        self.graph = graph
        self.weights = weights
        self.enabled = set(edge_ids)
        self.adjacency: dict[str, list[tuple[str, str]]] = {region.id: [] for region in graph.regions}
        for edge in graph.connections:
            self.adjacency[edge.source].append((edge.target, edge.id))
            if not edge.directed:
                self.adjacency[edge.target].append((edge.source, edge.id))
        for edges in self.adjacency.values():
            edges.sort(key=lambda entry: (entry[1], entry[0]))
        count = sum(map(len, self.adjacency.values()))
        total = len(self.adjacency) * (len(self.adjacency) - 1)
        self.topology = TopologyStats(len(graph.regions), len(graph.connections), count, total,
                                      count / total if total else 0.0)

    def set_enabled(self, edge_id: str, enabled: bool) -> None:
        if edge_id not in self.weights.values:
            raise KeyError(f"Unknown edge: {edge_id}")
        if not isinstance(enabled, bool):
            raise ValueError("enabled must be a boolean")
        if enabled:
            self.enabled.add(edge_id)
        else:
            self.enabled.discard(edge_id)

    def step(self, sources: Mapping[str, float]) -> RoutingStep:
        if not isinstance(sources, Mapping):
            raise TypeError("Source activity must be a region-to-scalar mapping")
        active = {}
        for region, value in sources.items():
            if region not in self.adjacency:
                raise KeyError(f"Unknown region: {region}")
            checked = _bounded(value, f"source {region}")
            if abs(checked) > self.activation_threshold:
                active[region] = checked
        totals: dict[str, float] = {}
        examined = products = delivered = 0
        # Sorting active source names makes results reproducible regardless of caller order.
        for source in sorted(active):
            arcs = self.adjacency[source]  # Only this region's actual out-neighbours.
            examined += len(arcs)
            candidates = []
            for target, edge_id in arcs:
                weight = self.weights.values[edge_id]
                if edge_id not in self.enabled or weight is None or weight == 0.0:
                    continue
                # LearningWeights.set validates finite values, but check again to
                # reject direct, unsafe edits to its public dictionary.
                if isinstance(weight, bool) or not isinstance(weight, Real) or not math.isfinite(weight):
                    raise ValueError(f"Invalid current weight for {edge_id}")
                signal = active[source] * float(weight)
                products += 1
                if abs(signal) > self.contribution_threshold:
                    candidates.append((target, edge_id, signal))
            candidates.sort(key=lambda item: (-abs(item[2]), item[1], item[0]))
            selected = candidates if self.max_fanout is None else candidates[:self.max_fanout]
            for target, _, signal in selected:
                totals[target] = totals.get(target, 0.0) + signal
                delivered += 1
        # Engineering-only clipping; not biophysical membrane integration.
        result = {region: max(-1.0, min(1.0, totals[region])) for region in sorted(totals)
                  if totals[region] != 0.0}
        return RoutingStep(result, RoutingStats(len(active), examined, products, delivered, len(result)))

    def propagate(self, sources: Mapping[str, float], *, hops: int = 1) -> tuple[RoutingStep, ...]:
        """Each hop processes *new* activity only; no implicit all-to-all broadcast."""
        if isinstance(hops, bool) or not isinstance(hops, int) or not 1 <= hops <= 32:
            raise ValueError("hops must be an integer from 1 through 32")
        activity = sources
        trace = []
        for _ in range(hops):
            outcome = self.step(activity)
            trace.append(outcome)
            activity = outcome.activity
            if not activity:
                break
        return tuple(trace)

    def input_packets(self, packets: tuple[SensoryPacket, ...]) -> dict[str, float]:
        """Lossy *fixed* pooling: nonzero packet -> one regional activity event.

        No semantics, video understanding, text decoding, or learned projection.
        One input packet's many feature channels are compressed to mean |value|.
        """
        activity: dict[str, float] = {}
        for packet in packets:
            target = packet.cortical_target
            if target not in self.adjacency:
                raise KeyError(f"Cortical region missing from graph: {target}")
            if not packet.values:
                raise ValueError("Cannot pool an empty sensory packet")
            energy = sum(abs(_bounded(v, f"{target} sensory component")) for v in packet.values) / len(packet.values)
            activity[target] = max(activity.get(target, 0.0), energy)
        return activity


def make_sparse_schematic(*, max_fanout: int | None = 4) -> SparseConnectivity:
    """No weights allocated for absent edges; all existing weights remain None."""
    graph = make_schematic_graph()
    return SparseConnectivity(graph, LearningWeights(graph), max_fanout=max_fanout)


if __name__ == "__main__":
    network = make_sparse_schematic()
    print(f"Sparse regional graph: {network.topology}")
    print(f"No assigned weights: {network.step({'L_v1': 0.8})}")
    for edge in network.graph.connections:
        if (edge.source, edge.target) in {('L_v1', 'L_visual_assoc'), ('L_visual_assoc', 'L_temporal_assoc')}:
            network.weights.set(edge.id, 0.6)  # externally injected illustration, NOT learned
    print(f"Explicitly assigned demo edges, two hops: {network.propagate({'L_v1': 0.8}, hops=2)}")
