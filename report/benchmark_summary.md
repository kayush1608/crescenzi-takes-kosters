# Benchmark Summary

This file summarizes the current benchmark pipeline outputs.

## Generated Artifacts

- `results/data/benchmark_results.csv`
- `results/plots/runtime_vs_nodes.png`
- `results/plots/bfs_traversals_vs_nodes.png`
- `results/plots/relative_error_vs_nodes.png`
- `results/plots/runtime_by_family.png`
- `results/plots/facebook_runtime_comparison.png`

## Current Setup

- Real-world graph: merged Facebook ego-network graph
- Synthetic families:
  - Erdős-Rényi
  - Barabási-Albert
  - Watts-Strogatz
- Sizes:
  - 120 nodes
  - 220 nodes
  - 500 nodes

## Validation

For graphs up to the configured small-graph threshold, the exact baseline is used to compute:

- exact diameter
- absolute error
- relative error

## Current Observation

In the present run, both implemented algorithms matched the exact diameter on the validated synthetic graphs.
