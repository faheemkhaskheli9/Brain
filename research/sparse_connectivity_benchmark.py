"""Reproducible *operation count*, not a learning or wall-clock benchmark."""

import json
import random
import statistics

from sparse_connectivity import make_sparse_schematic


def run(seed_count: int = 10) -> dict:
    if type(seed_count) is not int or not 1 <= seed_count <= 100:
        raise ValueError("seed_count must be an integer from 1 to 100")
    graph = make_sparse_schematic(max_fanout=4)
    # A deliberately artificial, uniform assigned weight on each structural edge.
    # It does not imply that the brain has learned or that 0.4 is biological.
    for edge in graph.graph.connections:
        graph.weights.set(edge.id, 0.4)
    visited, products, emitted = [], [], []
    samples = []
    nodes = tuple(graph.adjacency)
    for seed in range(seed_count):
        rng = random.Random(seed)
        selected = rng.sample(nodes, 2)
        outcome = graph.step({name: 0.8 for name in selected})
        visited.append(outcome.stats.examined_arcs)
        products.append(outcome.stats.weighted_products)
        emitted.append(outcome.stats.delivered_events)
        samples.append({"seed": seed, "active_sources": selected,
                        "arcs_examined": visited[-1], "weighted_products": products[-1],
                        "events_delivered": emitted[-1]})
    return {
        "format": "brain-sparse-routing-counts/1",
        "scope": "synthetic operation counts; no training, accuracy, speed or biology measurement",
        "configuration": {"seeds": seed_count, "sources_per_step": 2,
                          "assigned_demo_weight": 0.4, "fanout_limit": 4,
                          "activation_threshold": 0.01, "contribution_threshold": 0.01},
        "possible_dense_arcs": graph.topology.possible_directed_arcs,
        "structural_arcs": graph.topology.directed_arcs,
        "topology_density": graph.topology.density,
        "mean_examined_arcs": statistics.mean(visited),
        "mean_weighted_products": statistics.mean(products),
        "mean_events_delivered": statistics.mean(emitted),
        "samples": samples,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
