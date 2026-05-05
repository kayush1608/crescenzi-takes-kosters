from __future__ import annotations

import os
from pathlib import Path

import networkx as nx
import pandas as pd

from graph_diameter.algorithms.crescenzi import CrescenziDiameter
from graph_diameter.algorithms.exact import ExactDiameter
from graph_diameter.algorithms.takes_kosters import TakesKostersDiameter
from graph_diameter.data.facebook import load_combined_facebook_graph
from graph_diameter.data.synthetic import (
    make_barabasi_albert_graph,
    make_erdos_renyi_graph,
    make_watts_strogatz_graph,
)
from graph_diameter.experiments.plots import generate_plots


ROOT = Path(__file__).resolve().parents[3]
DATASET_DIR = ROOT / "dataset"
RESULTS_DIR = ROOT / "results" / "data"
PLOTS_DIR = ROOT / "results" / "plots"
OUTPUT_CSV = RESULTS_DIR / "benchmark_results.csv"
PROFILE_SIZES = {
    "quick": [120, 220],
    "standard": [120, 220, 500, 1000, 2000],
    "large": [1000, 2000, 5000, 10000, 20000],
    "full": [120, 220, 500, 1000, 2000, 5000, 10000, 20000],
}


def _exact_if_small(graph: nx.Graph, node_limit: int = 220) -> int | None:
    if graph.number_of_nodes() > node_limit:
        return None
    return ExactDiameter().run(graph).diameter


def _erdos_renyi_probability(nodes: int) -> float:
    # Keep the average degree around 10 while slightly boosting small cases.
    if nodes <= 200:
        return 0.05
    if nodes <= 500:
        return 0.02
    return min(0.01, 10.0 / nodes)


def build_benchmark_graphs(profile: str = "standard") -> list[tuple[str, str, nx.Graph]]:
    if profile not in PROFILE_SIZES:
        valid = ", ".join(sorted(PROFILE_SIZES))
        raise ValueError(f"Unknown benchmark profile '{profile}'. Expected one of: {valid}")

    graphs: list[tuple[str, str, nx.Graph]] = [
        ("real_world", "facebook_combined", load_combined_facebook_graph(DATASET_DIR)),
    ]

    for nodes in PROFILE_SIZES[profile]:
        graphs.append(
            (
                "erdos_renyi",
                f"erdos_renyi_{nodes}",
                make_erdos_renyi_graph(
                    nodes=nodes,
                    probability=_erdos_renyi_probability(nodes),
                ),
            )
        )
        graphs.append(
            (
                "barabasi_albert",
                f"barabasi_albert_{nodes}",
                make_barabasi_albert_graph(nodes=nodes, attachments=3),
            )
        )
        graphs.append(
            (
                "watts_strogatz",
                f"watts_strogatz_{nodes}",
                make_watts_strogatz_graph(
                    nodes=nodes,
                    neighbors=8,
                    probability=0.15,
                ),
            )
        )

    return graphs


def run_benchmarks(profile: str = "standard") -> pd.DataFrame:
    algorithms = [CrescenziDiameter(), TakesKostersDiameter()]
    rows: list[dict[str, object]] = []

    for family, graph_name, graph in build_benchmark_graphs(profile=profile):
        exact_value = _exact_if_small(graph)
        for algorithm in algorithms:
            result = algorithm.run(graph)
            relative_error = None
            if exact_value not in (None, 0) and result.diameter is not None:
                relative_error = abs(result.diameter - exact_value) / exact_value

            rows.append(
                {
                    "family": family,
                    "graph": graph_name,
                    "nodes": graph.number_of_nodes(),
                    "edges": graph.number_of_edges(),
                    "algorithm": result.name,
                    "diameter": result.diameter,
                    "exact_diameter": exact_value,
                    "absolute_error": (
                        None
                        if exact_value is None or result.diameter is None
                        else abs(result.diameter - exact_value)
                    ),
                    "relative_error": relative_error,
                    "runtime_seconds": result.runtime_seconds,
                    "memory_bytes": result.memory_bytes,
                    "bfs_traversals": result.bfs_traversals,
                    "lower_bound": result.lower_bound,
                    "upper_bound": result.upper_bound,
                    "bound_gap": (
                        None
                        if result.lower_bound is None or result.upper_bound is None
                        else result.upper_bound - result.lower_bound
                    ),
                    "metadata": repr(result.metadata),
                }
            )

    return pd.DataFrame(rows).sort_values(["family", "nodes", "algorithm", "graph"]).reset_index(drop=True)


def main(profile: str | None = None) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    selected_profile = profile or os.environ.get("BENCHMARK_PROFILE", "standard")
    dataframe = run_benchmarks(profile=selected_profile)
    dataframe.to_csv(OUTPUT_CSV, index=False)
    created_plots = generate_plots(dataframe, PLOTS_DIR)
    print(f"Saved benchmark results to {OUTPUT_CSV}")
    print(f"Benchmark profile: {selected_profile}")
    for plot_path in created_plots:
        print(f"Saved plot to {plot_path}")
    print(dataframe.to_string(index=False))


if __name__ == "__main__":
    main()
