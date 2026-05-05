from __future__ import annotations

import networkx as nx


# Retry Erdos-Renyi generation until we get a connected graph of the requested size.
def _connected_erdos_renyi_graph(nodes: int, probability: float, seed: int) -> nx.Graph:
    rng = seed
    while True:
        graph = nx.erdos_renyi_graph(nodes, probability, seed=rng)
        if nx.is_connected(graph):
            return graph
        rng += 1


# Build a connected Erdos-Renyi graph for benchmarking.
def make_erdos_renyi_graph(nodes: int, probability: float, seed: int = 42) -> nx.Graph:
    return _connected_erdos_renyi_graph(nodes, probability, seed)


# Build a Barabasi-Albert graph, which is connected by construction here.
def make_barabasi_albert_graph(nodes: int, attachments: int, seed: int = 42) -> nx.Graph:
    return nx.barabasi_albert_graph(nodes, attachments, seed=seed)


# Build a connected Watts-Strogatz graph without changing the requested node count.
def make_watts_strogatz_graph(nodes: int, neighbors: int, probability: float, seed: int = 42) -> nx.Graph:
    return nx.connected_watts_strogatz_graph(
        nodes,
        neighbors,
        probability,
        seed=seed,
    )
