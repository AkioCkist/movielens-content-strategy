"""Run consecutive Python pipeline steps in separate processes."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
STEPS = {
    1: "01_create_schema.py",
    2: "02_load_data.py",
    3: "03_quality_checks.py",
    4: "04_create_splits.py",
    5: "05_feature_tables.py",
    6: "06_logistic_features.py",
    7: "07_dashboard_views.py",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-step", type=int, choices=STEPS, default=1)
    parser.add_argument("--through", type=int, choices=STEPS, default=5)
    args = parser.parse_args()
    if args.from_step > args.through:
        parser.error("--from-step must be <= --through")

    for number in range(args.from_step, args.through + 1):
        script = HERE / STEPS[number]
        print(f"\n{'=' * 72}\nStep {number}: {script.name}\n{'=' * 72}", flush=True)
        subprocess.run([sys.executable, str(script)], check=True)

    if args.through == 5:
        print("\nSteps 1-5 complete. After KNIME writes user_segments, run:")
        print(f'  "{sys.executable}" "{HERE / "run_pipeline.py"}" --from-step 6 --through 7')


if __name__ == "__main__":
    main()

