# Crescenzi vs Takes-Kosters

Project `8` for the IAE graph diameter comparison track.

This repository is structured to compare two graph diameter algorithms in practice:

- `Crescenzi`
- `Takes-Kosters`

The goal is to study how they behave on multiple graph families, measure their performance, and generate plots/report material.

## Current Scope

The repository now includes:

- a common graph loader interface
- paper-based implementations for both algorithms
- an exact baseline for small graphs
- synthetic graph generation utilities
- an expanded benchmark runner and CSV output path
- plot generation for runtime, BFS traversals, and error
- a clean directory layout for code, plots, and report writing

## Repository Layout

```text
crescenzi-takes-kosters/
├── dataset/                      # Facebook ego-network files
├── report/
│   ├── benchmark_summary.md      # Auto-written experiment summary
│   └── notes.md                  # Working notes for report writing
├── results/
│   ├── data/                     # Benchmark CSV files
│   └── plots/                    # Generated plots
├── scripts/
│   ├── run_benchmarks.py         # Main benchmark entry point
│   └── run_plots.py              # Rebuild plots from existing CSV
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
│       │   └── benchmark.py
│       ├── __init__.py
│       └── models.py
└── requirements.txt
```

## Recommended Workflow

1. Keep the merged Facebook graph as the real-world dataset.
2. Use the synthetic graph families already wired into the benchmark.
3. Validate correctness on smaller graphs using the exact baseline.
4. Benchmark runtime, memory, BFS traversals, and diameter quality.
5. Generate plots and convert the benchmark output into report material.

## Dataset Note

Each `*.edges` file in `dataset/` is an ego network. For a larger connected graph, this repo includes a loader that combines all ego networks into one undirected graph by:

- adding alter-to-alter edges from each `.edges` file
- connecting each ego node to the alters observed in its network

This is the same general idea used in the reference `aad` repo.

## Setup

Create a virtual environment if you want, then install dependencies:

```bash
pip install -r requirements.txt
```

## Running The Benchmark

From the repository root:

```bash
PYTHONPATH=src python scripts/run_benchmarks.py
```

This will:

- load the merged Facebook graph
- generate multiple synthetic graph families and sizes
- run both paper-based algorithms
- save results to `results/data/benchmark_results.csv`
- save plots to `results/plots/`

To regenerate plots from the latest CSV:

```bash
PYTHONPATH=src python scripts/run_plots.py
```

## Implemented Algorithms

- `src/graph_diameter/algorithms/crescenzi.py`
  Uses the `iFUB` algorithm from Crescenzi et al. with 4-Sweep high-degree initialization by default.

- `src/graph_diameter/algorithms/takes_kosters.py`
  Uses the `BoundingDiameters` bound-based exact method from Takes and Kosters with alternating candidate selection.

These two files are the main comparison targets for your report.

## Metrics To Compare

You will likely want at least:

- runtime
- memory usage
- returned diameter
- exact diameter on small graphs
- absolute error
- relative error
- number of BFS traversals / iterations

If the paper gives bounds instead of exact answers, also record:

- lower bound
- upper bound
- bound gap

## Current Benchmark Set

- `facebook_combined`
- `erdos_renyi_{120,220,500}`
- `barabasi_albert_{120,220,500}`
- `watts_strogatz_{120,220,500}`

Exact validation is automatically computed for smaller graphs in the benchmark suite.

## Report Advice

A strong report should compare the algorithms on:

- the Facebook graph
- sparse random graphs
- scale-free graphs
- small-world graphs

And discuss:

- speed vs quality tradeoff
- how graph structure affects behavior
- where each algorithm is stronger or weaker
