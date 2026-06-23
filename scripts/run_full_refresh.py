from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str]) -> None:
    """Run a command from the project root and stop if it fails."""
    result = subprocess.run(command, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    """Run the full VT-RAP refresh workflow."""
    run_command([sys.executable, "scripts/run_pipeline.py"])
    run_command([sys.executable, "scripts/validate_outputs.py"])
    run_command([sys.executable, "-m", "compileall", "src", "app", "scripts"])

    print("Full refresh completed successfully.")


if __name__ == "__main__":
    main()
