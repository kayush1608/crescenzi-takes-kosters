from __future__ import annotations

import math
import random
import time
from collections import deque

import networkx as nx
import psutil

from graph_diameter.algorithms.base import DiameterAlgorithm
from graph_diameter.models import AlgorithmResult


def _bfs_distances(graph: nx.Graph, source: int) -> dict[int, int]:
    distances = {source: 0}
    queue = deque([source])

    while queue:
        node = queue.popleft()
        for neighbor in graph.neighbors(node):
            if neighbor in distances:
                continue
            distances[neighbor] = distances[node] + 1
            queue.append(neighbor)

    return distances


class TakesKostersDiameter(DiameterAlgorithm):
    """
    Exact bound-based implementation inspired by Takes and Kosters'
    BoundingDiameters algorithm.

    The default node selection uses the paper's strongest practical strategy:
    alternate between selecting the candidate with the largest eccentricity
    upper bound and the smallest eccentricity lower bound, breaking ties by
    highest degree.
    """

    name = "Takes-Kosters"

    def __init__(
        self,
        selection_strategy: str = "alternate_bounds",
        random_seed: int = 42,
    ) -> None:
        self.selection_strategy = selection_strategy
        self.random_seed = random_seed

    def _select_candidate(
        self,
        graph: nx.Graph,
        candidates: set[int],
        lower_bounds: dict[int, int],
        upper_bounds: dict[int, float],
        iteration: int,
        rng: random.Random,
    ) -> int:
        if self.selection_strategy == "random":
            return rng.choice(list(candidates))

        if self.selection_strategy == "highest_degree_first" and iteration == 0:
            return max(candidates, key=lambda node: (graph.degree[node], -node))

        if self.selection_strategy == "largest_bound_gap":
            return max(
                candidates,
                key=lambda node: (
                    upper_bounds[node] - lower_bounds[node],
                    graph.degree[node],
                    -node,
                ),
            )

        choose_upper = iteration % 2 == 0
        if choose_upper:
            return max(
                candidates,
                key=lambda node: (upper_bounds[node], graph.degree[node], -node),
            )
        return min(
            candidates,
            key=lambda node: (lower_bounds[node], -graph.degree[node], node),
        )

    def run(self, graph: nx.Graph) -> AlgorithmResult:
        if graph.number_of_nodes() == 0:
            raise ValueError("Takes-Kosters requires a non-empty graph.")
        if not nx.is_connected(graph):
            raise ValueError("Takes-Kosters expects a connected graph.")

        process = psutil.Process()
        start = time.perf_counter()
        rng = random.Random(self.random_seed)

        candidates = set(graph.nodes)
        lower_bounds = {node: -math.inf for node in graph.nodes}
        upper_bounds = {node: math.inf for node in graph.nodes}

        diameter_lower = -math.inf
        diameter_upper = math.inf
        bfs_traversals = 0
        iteration = 0

        while candidates and diameter_lower != diameter_upper:
            current = self._select_candidate(
                graph,
                candidates,
                lower_bounds,
                upper_bounds,
                iteration,
                rng,
            )

            distances = _bfs_distances(graph, current)
            if len(distances) != graph.number_of_nodes():
                raise ValueError("Takes-Kosters expects a connected graph.")

            eccentricity = max(distances.values(), default=0)
            bfs_traversals += 1

            diameter_lower = max(diameter_lower, eccentricity)
            diameter_upper = min(diameter_upper, 2 * eccentricity)

            removable: set[int] = set()
            for node in candidates:
                distance = distances[node]
                lower_bounds[node] = max(
                    lower_bounds[node],
                    max(eccentricity - distance, distance),
                )
                upper_bounds[node] = min(
                    upper_bounds[node],
                    eccentricity + distance,
                )

                if (
                    upper_bounds[node] <= diameter_lower
                    and lower_bounds[node] >= diameter_upper / 2
                ) or lower_bounds[node] == upper_bounds[node]:
                    removable.add(node)

            candidates -= removable
            iteration += 1

        runtime = time.perf_counter() - start
        memory_bytes = process.memory_info().rss
        exact_by_exhaustion = not candidates
        reported_upper_bound = int(diameter_lower) if exact_by_exhaustion else int(diameter_upper)

        return AlgorithmResult(
            name=self.name,
            diameter=int(diameter_lower),
            runtime_seconds=runtime,
            memory_bytes=memory_bytes,
            bfs_traversals=bfs_traversals,
            lower_bound=int(diameter_lower),
            upper_bound=reported_upper_bound,
            metadata={
                "algorithm": "BoundingDiameters",
                "selection_strategy": self.selection_strategy,
                "remaining_candidates": len(candidates),
                "iterations": iteration,
                "exact_by_exhaustion": exact_by_exhaustion,
            },
        )
