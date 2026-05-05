# IAE Project

## Crescenzi vs Takes-Kosters

This project compares two graph diameter algorithms on real-world and synthetic graphs:

- `Crescenzi` implemented as `iFUB`
- `Takes-Kosters` implemented as `BoundingDiameters`

The main goal is to study their correctness, runtime behavior, BFS usage, and practical performance on different graph families.

## Project Objectives

- implement both graph diameter algorithms
- compare them on multiple graph types
- validate correctness on smaller graphs using an exact baseline
- generate results, plots, and report-ready observations

## What Is Implemented

- common algorithm interface
- `Crescenzi` / `iFUB` implementation
- `Takes-Kosters` / `BoundingDiameters` implementation
- exact diameter baseline for small connected graphs
- Facebook ego-network loader merged into one connected graph
- synthetic graph generation for:
  - Erdos-Renyi
  - Barabasi-Albert
  - Watts-Strogatz
- benchmark runner with multiple size profiles
- CSV result export
- automatic plot generation
- auto-generated benchmark summary for report writing

## Repository Structure

```text
crescenzi-takes-kosters/
├── dataset/                      # Facebook ego-network files
├── report/
│   ├── benchmark_summary.md      # Auto-generated benchmark summary
│   └── notes.md                  # Report drafting notes
├── results/
│   ├── data/                     # Benchmark CSV output
│   └── plots/                    # Generated plots
├── scripts/
│   ├── run_benchmarks.py         # Runs all benchmarks for a chosen profile
│   └── run_plots.py              # Regenerates plots from saved CSV data
├── src/
│   └── graph_diameter/
│       ├── algorithms/
│       │   ├── base.py
│       │   ├── crescenzi.py
│       │   ├── exact.py
│       │   └── takes_kosters.py
│       ├── data/
│       │   ├── facebook.py
│       │   └── synthetic.py
│       ├── experiments/
│       │   ├── benchmark.py
│       │   └── plots.py
│       ├── __init__.py
│       └── models.py
└── requirements.txt
```

## Dataset

The real-world graph is built from the Facebook ego-network dataset in `dataset/`.

Each `*.edges` file represents one ego network. The loader:

- adds alter-to-alter edges from each ego network
- adds the ego node itself
- connects the ego node to its observed alters
- keeps the largest connected component if needed

This produces the `facebook_combined` graph used in benchmarking.

## Setup

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## How The Benchmark Works

You do not need to manually provide one graph as input.

When you run the benchmark script, it automatically:

- loads the merged Facebook graph
- generates synthetic graphs for the selected profile
- runs both algorithms on all graphs in that profile
- computes exact diameter on smaller graphs when enabled
- saves CSV results
- generates plots
- writes a benchmark summary markdown file

## Running The Code

Run the benchmark from the project root:

```bash
PYTHONPATH=src python scripts/run_benchmarks.py --profile large
```

Available benchmark profiles:

- `quick`: `7` graphs total
- `standard`: `16` graphs total
- `large`: `16` graphs total
- `full`: `25` graphs total

To regenerate plots from the latest CSV:

```bash
PYTHONPATH=src python scripts/run_plots.py
```

## Benchmark Graphs

For the `large` profile used in the final report, the benchmark includes:

- `facebook_combined`
- `erdos_renyi_{1000,2000,5000,10000,20000}`
- `barabasi_albert_{1000,2000,5000,10000,20000}`
- `watts_strogatz_{1000,2000,5000,10000,20000}`

This gives:

- `16` graph instances total
- `32` algorithm runs total because each graph is tested with both algorithms

## Metrics Collected

- returned diameter
- exact diameter for small graphs
- absolute error
- relative error
- runtime in seconds
- memory usage
- BFS traversals
- lower bound
- upper bound
- bound gap

## Output Files

The benchmark creates these main artifacts:

- `results/data/benchmark_results.csv`
- `report/benchmark_summary.md`
- `results/plots/runtime_vs_nodes.png`
- `results/plots/bfs_traversals_vs_nodes.png`
- `results/plots/runtime_by_family.png`
- `results/plots/facebook_runtime_comparison.png`

The `relative_error_vs_nodes.png` plot is generated only when the selected
benchmark profile includes graphs that are also validated by the exact baseline.

## Current Results Summary

From the current `large` benchmark run:

- this run is focused on scalability, so it does not include exact-baseline rows
- `Takes-Kosters` was faster overall on the synthetic benchmark set
- `Crescenzi` was faster on the real-world `facebook_combined` graph
- on `facebook_combined`, both algorithms returned diameter `8`

Facebook graph comparison:

- `Crescenzi`: diameter `8`, runtime `0.029051 s`, `5` BFS traversals
- `Takes-Kosters`: diameter `8`, runtime `0.060778 s`, `10` BFS traversals

Overall synthetic benchmark trend:

- `Takes-Kosters` was faster on all `5/5` Watts-Strogatz graphs
- `Takes-Kosters` was faster on all `5/5` Erdos-Renyi graphs
- `Takes-Kosters` was faster on `4/5` Barabasi-Albert graphs

## Main Algorithm Files

- `src/graph_diameter/algorithms/crescenzi.py`
- `src/graph_diameter/algorithms/takes_kosters.py`
- `src/graph_diameter/algorithms/exact.py`
