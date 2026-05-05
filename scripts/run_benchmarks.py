import os
import argparse
from pathlib import Path

# Keep Matplotlib's cache inside the repo so plotting works in restricted environments.
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))

from graph_diameter.experiments.benchmark import main


if __name__ == "__main__":
    # Expose the benchmark profile as a simple command-line switch.
    parser = argparse.ArgumentParser(description="Run graph diameter benchmarks.")
    parser.add_argument(
        "--profile",
        default="standard",
        choices=["quick", "standard", "large", "full"],
        help="Benchmark size profile to run.",
    )
    args = parser.parse_args()
    main(profile=args.profile)
