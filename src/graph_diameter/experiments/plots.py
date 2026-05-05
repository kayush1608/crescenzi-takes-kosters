from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _save_family_metric_plot(
    dataframe: pd.DataFrame,
    y_column: str,
    title: str,
    output_path: Path,
    ylabel: str,
) -> None:
    families = sorted(dataframe["family"].unique())
    fig, axes = plt.subplots(len(families), 1, figsize=(9, 4 * len(families)), squeeze=False)

    for axis, family in zip(axes.flatten(), families):
        subset = dataframe[dataframe["family"] == family].sort_values(["nodes", "graph"])
        for algorithm, group in subset.groupby("algorithm"):
            axis.plot(group["nodes"], group[y_column], marker="o", linewidth=2, label=algorithm)
        axis.set_title(f"{title} on {family}")
        axis.set_xlabel("Nodes")
        axis.set_ylabel(ylabel)
        axis.grid(alpha=0.3)
        axis.legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def _save_family_average_runtime_plot(dataframe: pd.DataFrame, output_path: Path) -> None:
    summary = (
        dataframe.groupby(["family", "algorithm"], as_index=False)["runtime_seconds"]
        .mean()
        .rename(columns={"runtime_seconds": "mean_runtime_seconds"})
    )
    pivot = summary.pivot(index="family", columns="algorithm", values="mean_runtime_seconds")

    fig, ax = plt.subplots(figsize=(9, 5))
    pivot.plot(kind="bar", ax=ax)
    ax.set_title("Mean Runtime by Graph Family")
    ax.set_xlabel("Graph Family")
    ax.set_ylabel("Mean Runtime (s)")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(title="Algorithm")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def _save_facebook_runtime_plot(dataframe: pd.DataFrame, output_path: Path) -> None:
    facebook_rows = dataframe[dataframe["graph"] == "facebook_combined"].copy()
    if facebook_rows.empty:
        return

    facebook_rows = facebook_rows.sort_values("algorithm").reset_index(drop=True)
    nodes = int(facebook_rows["nodes"].iloc[0])
    edges = int(facebook_rows["edges"].iloc[0])

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        facebook_rows["algorithm"],
        facebook_rows["runtime_seconds"],
        color=["#1f77b4", "#ff7f0e"],
    )
    ax.set_title(f"Facebook Combined Runtime Comparison ({nodes} nodes, {edges} edges)")
    ax.set_ylabel("Runtime (s)")
    ax.grid(axis="y", alpha=0.3)

    for bar, runtime in zip(bars, facebook_rows["runtime_seconds"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{runtime:.6f} s",
            ha="center",
            va="bottom",
        )

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
        _save_family_metric_plot(
            overall,
            "runtime_seconds",
            "Runtime vs Nodes",
            runtime_plot,
            "Runtime (s)",
        )
        created.append(runtime_plot)

        bfs_plot = output_path / "bfs_traversals_vs_nodes.png"
        _save_family_metric_plot(
            overall,
            "bfs_traversals",
            "BFS Traversals vs Nodes",
            bfs_plot,
            "BFS Traversals",
        )
        created.append(bfs_plot)

        if overall["exact_diameter"].notna().any():
            exact_rows = overall[overall["exact_diameter"].notna()].copy()
            if not exact_rows.empty:
                exact_rows["relative_error"] = exact_rows["relative_error"].fillna(0.0)
                error_plot = output_path / "relative_error_vs_nodes.png"
                _save_family_metric_plot(
                    exact_rows,
                    "relative_error",
                    "Relative Error vs Nodes",
                    error_plot,
                    "Relative Error",
                )
                created.append(error_plot)

        family_runtime_plot = output_path / "runtime_by_family.png"
        _save_family_average_runtime_plot(overall, family_runtime_plot)
        created.append(family_runtime_plot)

    facebook_rows = dataframe[dataframe["graph"] == "facebook_combined"]
    if not facebook_rows.empty:
        facebook_plot = output_path / "facebook_runtime_comparison.png"
        _save_facebook_runtime_plot(dataframe, facebook_plot)
        created.append(facebook_plot)

    return created
