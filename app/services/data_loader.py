from __future__ import annotations

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


def load_dashboard_data() -> dict[str, pd.DataFrame]:
    """Load all processed tables required by the dashboard."""
    return {
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
    }