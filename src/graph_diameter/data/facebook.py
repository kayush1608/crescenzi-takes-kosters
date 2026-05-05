from __future__ import annotations

from pathlib import Path

import networkx as nx


def _load_edges(edges_path: Path) -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    with edges_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) == 2:
                edges.append((int(parts[0]), int(parts[1])))
    return edges


def _load_feat_nodes(feat_path: Path) -> set[int]:
    nodes: set[int] = set()
    if not feat_path.exists():
        return nodes

    with feat_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            parts = line.split()
            if parts:
                nodes.add(int(parts[0]))
    return nodes


def load_combined_facebook_graph(dataset_dir: str | Path) -> nx.Graph:
    """
    Merge the Facebook ego networks into a single undirected graph.

    Each ego node is connected to alters observed in its local network.
    """

    dataset_path = Path(dataset_dir)
    graph = nx.Graph()

    for edges_path in sorted(dataset_path.glob("*.edges")):
        ego_id = int(edges_path.stem)
        feat_path = edges_path.with_suffix(".feat")

        alters: set[int] = set()
        graph.add_node(ego_id)

        for u, v in _load_edges(edges_path):
            graph.add_edge(u, v)
            alters.add(u)
            alters.add(v)

        alters.update(_load_feat_nodes(feat_path))

        for alter in alters:
            graph.add_edge(ego_id, alter)

    if not nx.is_connected(graph):
        largest_component = max(nx.connected_components(graph), key=len)
        graph = graph.subgraph(largest_component).copy()

    return graph
