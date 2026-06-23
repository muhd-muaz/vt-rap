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

    return pd.read_csv(file_path)


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
    """Load all processed tables required by the dashboard."""
    return {
        "metadata": load_pipeline_metadata(),
        "executive_summary": load_processed_table("executive_summary.csv"),
        "fault_family_summary": load_processed_table("fault_family_summary.csv"),
        "equipment_risk_model": load_processed_table("equipment_risk_model.csv"),
        "account_risk_model": load_processed_table("account_risk_model.csv"),
        "emerging_equipment_alerts": load_processed_table(
            "emerging_equipment_alerts.csv"
        ),
        "data_quality_summary": load_processed_table("data_quality_summary.csv"),
        "monthly_callback_trend": load_processed_table("monthly_callback_trend.csv"),
        "monthly_fault_family_trend": load_processed_table(
            "monthly_fault_family_trend.csv"
        ),
        "monthly_equipment_type_trend": load_processed_table(
            "monthly_equipment_type_trend.csv"
        ),
        "monthly_account_trend": load_processed_table("monthly_account_trend.csv"),
        "monthly_equipment_trend": load_processed_table(
            "monthly_equipment_trend.csv"
        ),
        "equipment_fault_family_mix": load_processed_table(
            "equipment_fault_family_mix.csv"
        ),
        "account_fault_family_mix": load_processed_table(
            "account_fault_family_mix.csv"
        ),
    }