import argparse

from graph_diameter.experiments.benchmark import main


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run graph diameter benchmarks.")
    parser.add_argument(
        "--profile",
        default="standard",
        choices=["quick", "standard", "large", "full"],
        help="Benchmark size profile to run.",
    )
    args = parser.parse_args()
    main(profile=args.profile)
