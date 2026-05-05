from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _save_line_plot(
    dataframe: pd.DataFrame,
    y_column: str,
    title: str,
    output_path: Path,
    ylabel: str,
) -> None:
    plt.figure(figsize=(9, 5))
    for algorithm, group in dataframe.groupby("algorithm"):
        ordered = group.sort_values(["nodes", "graph"])
        plt.plot(
            ordered["nodes"],
            ordered[y_column],
            marker="o",
            linewidth=2,
            label=algorithm,
        )

    plt.title(title)
    plt.xlabel("Nodes")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def _save_family_runtime_plot(dataframe: pd.DataFrame, output_path: Path) -> None:
    families = sorted(dataframe["family"].unique())
    fig, axes = plt.subplots(len(families), 1, figsize=(9, 4 * len(families)), squeeze=False)

    for axis, family in zip(axes.flatten(), families):
        subset = dataframe[dataframe["family"] == family].sort_values(["nodes", "graph"])
        for algorithm, group in subset.groupby("algorithm"):
            axis.plot(group["nodes"], group["runtime_seconds"], marker="o", linewidth=2, label=algorithm)
        axis.set_title(f"Runtime on {family}")
        axis.set_xlabel("Nodes")
        axis.set_ylabel("Runtime (s)")
        axis.grid(alpha=0.3)
        axis.legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def generate_plots(dataframe: pd.DataFrame, output_dir: str | Path) -> list[Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []

    overall = dataframe[dataframe["graph"] != "facebook_combined"].copy()
    if not overall.empty:
        runtime_plot = output_path / "runtime_vs_nodes.png"
        _save_line_plot(overall, "runtime_seconds", "Runtime vs Nodes", runtime_plot, "Runtime (s)")
        created.append(runtime_plot)

        bfs_plot = output_path / "bfs_traversals_vs_nodes.png"
        _save_line_plot(overall, "bfs_traversals", "BFS Traversals vs Nodes", bfs_plot, "BFS Traversals")
        created.append(bfs_plot)

        if overall["exact_diameter"].notna().any():
            exact_rows = overall[overall["exact_diameter"].notna()].copy()
            if not exact_rows.empty:
                exact_rows["relative_error"] = exact_rows["relative_error"].fillna(0.0)
                error_plot = output_path / "relative_error_vs_nodes.png"
                _save_line_plot(exact_rows, "relative_error", "Relative Error vs Nodes", error_plot, "Relative Error")
                created.append(error_plot)

        family_runtime_plot = output_path / "runtime_by_family.png"
        _save_family_runtime_plot(overall, family_runtime_plot)
        created.append(family_runtime_plot)

    facebook_rows = dataframe[dataframe["graph"] == "facebook_combined"]
    if not facebook_rows.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(facebook_rows["algorithm"], facebook_rows["runtime_seconds"], color=["#1f77b4", "#ff7f0e"])
        ax.set_title("Facebook Combined Runtime Comparison")
        ax.set_ylabel("Runtime (s)")
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        facebook_plot = output_path / "facebook_runtime_comparison.png"
        fig.savefig(facebook_plot, dpi=180)
        plt.close(fig)
        created.append(facebook_plot)

    return created
