from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
STYLE_PATH = PROJECT_ROOT / "app" / "styles" / "theme.css"


def load_css() -> None:
    """Load local CSS theme."""
    if STYLE_PATH.exists():
        st.markdown(
            f"<style>{STYLE_PATH.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


@st.cache_data
def load_processed_table(file_name: str) -> pd.DataFrame:
    """Load a processed CSV table."""
    file_path = PROCESSED_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing processed file: {file_path}. "
            "Run `python scripts/run_pipeline.py` first."
        )

    return pd.read_csv(file_path, low_memory=False)


@st.cache_data
def load_pipeline_metadata() -> dict:
    """Load pipeline run metadata."""
    metadata_path = PROCESSED_DIR / "pipeline_metadata.json"

    if not metadata_path.exists():
        return {
            "pipeline_name": "VT-RAP",
            "run_timestamp": "Not available",
            "raw_callback_file_count": "-",
            "raw_master_file_count": "-",
            "callbacks_raw_rows": "-",
            "silver_callbacks_rows": "-",
            "latest_event_month": "-",
            "validation_status": "Not available",
        }

    return json.loads(metadata_path.read_text(encoding="utf-8"))


def load_dashboard_data() -> dict[str, pd.DataFrame | dict]:
    """Load base processed data required by the dashboard."""
    return {
        "metadata": load_pipeline_metadata(),
        "silver_callbacks": load_processed_table("silver_callbacks.csv"),
    }
