from __future__ import annotations

import time
from collections import deque

import networkx as nx
import psutil

from graph_diameter.algorithms.base import DiameterAlgorithm
from graph_diameter.models import AlgorithmResult


# Run a plain BFS and return distances from one source to every reachable node.
def _bfs_distances(graph: nx.Graph, source: int) -> dict[int, int]:
    distances = {source: 0}
    queue = deque([source])

    while queue:
        node = queue.popleft()
        for neighbor in graph.neighbors(node):
            if neighbor not in distances:
                distances[neighbor] = distances[node] + 1
                queue.append(neighbor)

    return distances


class ExactDiameter(DiameterAlgorithm):
    """
    Exact baseline for small graphs.

    This is intentionally expensive and should only be used for validation or
    for moderately sized graphs.
    """

    name = "Exact"

    def run(self, graph: nx.Graph) -> AlgorithmResult:
        # Measure wall-clock time and resident memory for the full exact run.
        process = psutil.Process()
        start = time.perf_counter()

        diameter = 0
        bfs_traversals = 0

        # The exact baseline simply treats every node as a BFS source.
        for node in graph.nodes:
            distances = _bfs_distances(graph, node)
            if len(distances) != graph.number_of_nodes():
                raise ValueError("Exact baseline expects a connected graph.")
            diameter = max(diameter, max(distances.values(), default=0))
            bfs_traversals += 1

        runtime = time.perf_counter() - start
        memory_bytes = process.memory_info().rss

        # For the exact baseline, the returned diameter is both the lower and upper bound.
        return AlgorithmResult(
            name=self.name,
            diameter=diameter,
            runtime_seconds=runtime,
            memory_bytes=memory_bytes,
            bfs_traversals=bfs_traversals,
            lower_bound=diameter,
            upper_bound=diameter,
        )
