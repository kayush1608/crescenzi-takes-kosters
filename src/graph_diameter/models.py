from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AlgorithmResult:
    # One result record keeps the benchmark pipeline simple and uniform.
    name: str
    diameter: int | None
    runtime_seconds: float
    memory_bytes: int
    bfs_traversals: int = 0
    lower_bound: int | None = None
    upper_bound: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
