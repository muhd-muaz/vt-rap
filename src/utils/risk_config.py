from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RISK_CONFIG_PATH = PROJECT_ROOT / "config" / "risk_weights.json"


def load_risk_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load risk scoring configuration from JSON."""
    resolved_path = config_path or DEFAULT_RISK_CONFIG_PATH

    if not resolved_path.exists():
        raise FileNotFoundError(f"Risk config file not found: {resolved_path}")

    with resolved_path.open("r", encoding="utf-8") as file:
        return json.load(file)
