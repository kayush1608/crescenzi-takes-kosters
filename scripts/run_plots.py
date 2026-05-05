import os
from pathlib import Path

import pandas as pd

# Keep Matplotlib's cache inside the repo so plot regeneration works everywhere.
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))

from graph_diameter.experiments.plots import generate_plots

CSV_PATH = ROOT / "results" / "data" / "benchmark_results.csv"
PLOTS_DIR = ROOT / "results" / "plots"


# Reload the saved benchmark CSV and rebuild the plot artifacts from it.
def main() -> None:
    dataframe = pd.read_csv(CSV_PATH)
    created = generate_plots(dataframe, PLOTS_DIR)
    for plot_path in created:
        print(f"Saved plot to {plot_path}")


if __name__ == "__main__":
    main()
