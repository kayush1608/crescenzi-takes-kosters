from __future__ import annotations

import networkx as nx


def _connected_erdos_renyi_graph(nodes: int, probability: float, seed: int) -> nx.Graph:
    rng = seed
    while True:
        graph = nx.erdos_renyi_graph(nodes, probability, seed=rng)
        if nx.is_connected(graph):
            return graph
        rng += 1


def make_erdos_renyi_graph(nodes: int, probability: float, seed: int = 42) -> nx.Graph:
    return _connected_erdos_renyi_graph(nodes, probability, seed)


def make_barabasi_albert_graph(nodes: int, attachments: int, seed: int = 42) -> nx.Graph:
    return nx.barabasi_albert_graph(nodes, attachments, seed=seed)


def make_watts_strogatz_graph(nodes: int, neighbors: int, probability: float, seed: int = 42) -> nx.Graph:
    return nx.connected_watts_strogatz_graph(
        nodes,
        neighbors,
        probability,
        seed=seed,
    )
