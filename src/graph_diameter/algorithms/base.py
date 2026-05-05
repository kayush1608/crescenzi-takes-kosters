from __future__ import annotations

from abc import ABC, abstractmethod

import networkx as nx

from graph_diameter.models import AlgorithmResult


class DiameterAlgorithm(ABC):
    # Shared interface so every algorithm returns results in the same shape.
    """Common interface for all diameter algorithms in this repo."""

    name: str

    @abstractmethod
    def run(self, graph: nx.Graph) -> AlgorithmResult:
        # Each concrete algorithm implements its own diameter routine here.
        raise NotImplementedError
