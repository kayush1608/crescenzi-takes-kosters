from pathlib import Path

import pandas as pd

from graph_diameter.experiments.plots import generate_plots


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "results" / "data" / "benchmark_results.csv"
PLOTS_DIR = ROOT / "results" / "plots"


def main() -> None:
    dataframe = pd.read_csv(CSV_PATH)
    created = generate_plots(dataframe, PLOTS_DIR)
    for plot_path in created:
        print(f"Saved plot to {plot_path}")


if __name__ == "__main__":
    main()
