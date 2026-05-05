from __future__ import annotations

import random
import time
from collections import deque

import networkx as nx
import psutil

from graph_diameter.algorithms.base import DiameterAlgorithm
from graph_diameter.models import AlgorithmResult


# Build one BFS tree and keep the extra structure iFUB needs later.
def _bfs_tree(
    graph: nx.Graph,
    source: int,
) -> tuple[dict[int, int], dict[int, int | None], list[list[int]], int]:
    distances = {source: 0}
    parents: dict[int, int | None] = {source: None}
    levels: list[list[int]] = [[source]]
    queue = deque([source])
    farthest = source

    while queue:
        node = queue.popleft()
        farthest = node
        for neighbor in graph.neighbors(node):
            if neighbor in distances:
                continue
            next_distance = distances[node] + 1
            distances[neighbor] = next_distance
            parents[neighbor] = node
            if next_distance == len(levels):
                levels.append([])
            levels[next_distance].append(neighbor)
            queue.append(neighbor)

    return distances, parents, levels, farthest


# Rebuild a shortest path by walking backward through BFS parents.
def _reconstruct_path(parents: dict[int, int | None], target: int) -> list[int]:
    path: list[int] = []
    current: int | None = target
    while current is not None:
        path.append(current)
        current = parents[current]
    path.reverse()
    return path


# Pick the middle node of a path, which acts like a center estimate.
def _middle_of_path(path: list[int]) -> int:
    return path[len(path) // 2]


# Return the farthest reached node together with the source eccentricity.
def _farthest_and_eccentricity(graph: nx.Graph, source: int) -> tuple[int, int, dict[int, int | None], list[list[int]]]:
    distances, parents, levels, farthest = _bfs_tree(graph, source)
    eccentricity = distances[farthest]
    return farthest, eccentricity, parents, levels


class CrescenziDiameter(DiameterAlgorithm):
    # Practical iFUB implementation with a configurable starting strategy.
    """
    Implementation of the iFUB algorithm from Crescenzi et al. (2013).

    Default behavior mirrors the paper's effective practical variant:
    choose the initial node for 4-Sweep as a highest-degree node.
    """

    name = "Crescenzi"

    def __init__(
        self,
        precision_threshold: int = 0,
        start_mode: str = "4-sweep-high-degree",
        random_seed: int = 42,
    ) -> None:
        self.precision_threshold = precision_threshold
        self.start_mode = start_mode
        self.random_seed = random_seed

    def _select_initial_node(self, graph: nx.Graph) -> int:
        # The start node choice matters because it drives the quality of the early lower bound.
        if self.start_mode == "random":
            nodes = list(graph.nodes)
            return random.Random(self.random_seed).choice(nodes)
        if self.start_mode in {"high-degree", "4-sweep-high-degree"}:
            return max(graph.nodes, key=graph.degree)
        if self.start_mode == "4-sweep-random":
            nodes = list(graph.nodes)
            return random.Random(self.random_seed).choice(nodes)
        raise ValueError(f"Unsupported start_mode: {self.start_mode}")

    def _four_sweep(self, graph: nx.Graph) -> tuple[int, int, int]:
        # 4-Sweep gives iFUB a much stronger starting point than a single arbitrary BFS.
        bfs_traversals = 0

        r1 = self._select_initial_node(graph)
        a1, _, _, _ = _farthest_and_eccentricity(graph, r1)
        bfs_traversals += 1

        b1, ecc_a1, parents_a1, _ = _farthest_and_eccentricity(graph, a1)
        bfs_traversals += 1
        path_a1_b1 = _reconstruct_path(parents_a1, b1)
        r2 = _middle_of_path(path_a1_b1)

        a2, _, _, _ = _farthest_and_eccentricity(graph, r2)
        bfs_traversals += 1

        b2, ecc_a2, parents_a2, _ = _farthest_and_eccentricity(graph, a2)
        bfs_traversals += 1
        path_a2_b2 = _reconstruct_path(parents_a2, b2)
        u = _middle_of_path(path_a2_b2)

        lower_bound = max(ecc_a1, ecc_a2)
        return lower_bound, u, bfs_traversals

    def _ifub(self, graph: nx.Graph, start_node: int, lower_bound: int) -> tuple[int, int, int | None]:
        # Cache eccentricities so repeated fringe checks do not rerun the same BFS.
        bfs_traversals = 0
        eccentricity_cache: dict[int, int] = {}

        _, _, levels, _ = _bfs_tree(graph, start_node)
        bfs_traversals += 1

        ecc_u = len(levels) - 1
        lb = max(ecc_u, lower_bound)
        ub = 2 * ecc_u
        i = ecc_u

        # Walk inward from the outer fringe until the lower and upper bounds meet.
        while ub - lb > self.precision_threshold:
            max_bi = lb
            for node in levels[i]:
                if node not in eccentricity_cache:
                    _, ecc_node, _, _ = _farthest_and_eccentricity(graph, node)
                    eccentricity_cache[node] = ecc_node
                    bfs_traversals += 1
                if eccentricity_cache[node] > max_bi:
                    max_bi = eccentricity_cache[node]

            # This is the early-stop condition used by the iFUB analysis.
            if max_bi > 2 * (i - 1):
                return max_bi, bfs_traversals, None

            lb = max_bi
            ub = 2 * (i - 1)
            i -= 1

        return lb, bfs_traversals, ub

    def run(self, graph: nx.Graph) -> AlgorithmResult:
        if graph.number_of_nodes() == 0:
            raise ValueError("Crescenzi iFUB requires a non-empty graph.")
        if not nx.is_connected(graph):
            raise ValueError("Crescenzi iFUB expects a connected graph.")

        process = psutil.Process()
        start = time.perf_counter()

        # Either use 4-Sweep or fall back to a simpler single-source initialization.
        if self.start_mode.startswith("4-sweep"):
            initial_lower_bound, start_node, sweep_bfses = self._four_sweep(graph)
        else:
            start_node = self._select_initial_node(graph)
            _, initial_lower_bound, _, _ = _farthest_and_eccentricity(graph, start_node)
            sweep_bfses = 1

        diameter, ifub_bfses, final_upper_bound = self._ifub(
            graph,
            start_node=start_node,
            lower_bound=initial_lower_bound,
        )

        runtime = time.perf_counter() - start
        memory_bytes = process.memory_info().rss
        total_bfses = sweep_bfses + ifub_bfses

        # When iFUB converges exactly, the final lower and upper bounds collapse together.
        return AlgorithmResult(
            name=self.name,
            diameter=diameter,
            runtime_seconds=runtime,
            memory_bytes=memory_bytes,
            bfs_traversals=total_bfses,
            lower_bound=diameter,
            upper_bound=final_upper_bound if final_upper_bound is not None else diameter,
            metadata={
                "algorithm": "iFUB",
                "precision_threshold": self.precision_threshold,
                "start_mode": self.start_mode,
                "start_node": start_node,
                "initial_lower_bound": initial_lower_bound,
            },
        )
