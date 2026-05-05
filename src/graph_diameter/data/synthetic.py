from __future__ import annotations

import networkx as nx


def _largest_connected_component(graph: nx.Graph) -> nx.Graph:
    if nx.is_connected(graph):
        return graph
    component = max(nx.connected_components(graph), key=len)
    return graph.subgraph(component).copy()


def make_erdos_renyi_graph(nodes: int, probability: float, seed: int = 42) -> nx.Graph:
    graph = nx.erdos_renyi_graph(nodes, probability, seed=seed)
    return _largest_connected_component(graph)


def make_barabasi_albert_graph(nodes: int, attachments: int, seed: int = 42) -> nx.Graph:
    return nx.barabasi_albert_graph(nodes, attachments, seed=seed)


def make_watts_strogatz_graph(nodes: int, neighbors: int, probability: float, seed: int = 42) -> nx.Graph:
    graph = nx.watts_strogatz_graph(nodes, neighbors, probability, seed=seed)
    return _largest_connected_component(graph)
