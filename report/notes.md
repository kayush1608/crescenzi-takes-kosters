# Report Notes

## Goal

Compare `Crescenzi` and `Takes-Kosters` for graph diameter computation on real-world and synthetic undirected unweighted graphs.

## Current Experimental Setup

- Real-world graph:
  - merged Facebook graph from SNAP ego networks
- Synthetic graph families:
  - Erdős-Rényi
  - Barabási-Albert
  - Watts-Strogatz
- Tested sizes:
  - 120 nodes
  - 220 nodes
  - 500 nodes

## Algorithms

- Crescenzi:
  - implemented as `iFUB`
  - initialized using `4-Sweep` with a highest-degree start node
- Takes-Kosters:
  - implemented as `BoundingDiameters`
  - uses alternating candidate selection by eccentricity bounds

## Metrics Collected

- Runtime
- Memory
- Diameter returned
- Exact diameter on smaller graphs
- Absolute error
- Relative error
- Number of BFS traversals
- Lower bound
- Upper bound
- Bound gap

## Early Observations

- Both algorithms matched the exact diameter on the currently validated synthetic graphs.
- On the merged Facebook graph, both algorithms returned diameter `8`.
- Crescenzi tends to use very few BFS traversals on the Facebook graph.
- Takes-Kosters appears competitive or faster on several synthetic graphs, while often using fewer BFS traversals than Crescenzi on larger synthetic cases.

## Questions To Answer In The Report

- Which algorithm is faster in practice across graph families?
- Which algorithm uses fewer BFS traversals?
- How does graph structure affect performance?
- Does either algorithm scale more gracefully as graph size grows?
- Are there families where one algorithm is consistently more robust?
