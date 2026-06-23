from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


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


def get_summary_value(summary: pd.DataFrame, metric_name: str) -> str:
    """Return a metric value from the executive summary table."""
    matched_rows = summary.loc[summary["metric"].eq(metric_name), "value"]

    if matched_rows.empty:
        return "-"

    return str(matched_rows.iloc[0])


def main() -> None:
    """Run VT-RAP Streamlit dashboard."""
    st.set_page_config(
        page_title="VT-RAP Reliability Dashboard",
        page_icon="VT",
        layout="wide",
    )

    st.title("VT-RAP Reliability Analytics Platform")
    st.caption(
        "Vertical Transport callback, mantrap, fault-family, and risk monitoring dashboard."
    )

    executive_summary = load_processed_table("executive_summary.csv")
    fault_family_summary = load_processed_table("fault_family_summary.csv")
    equipment_risk_model = load_processed_table("equipment_risk_model.csv")
    account_risk_model = load_processed_table("account_risk_model.csv")
    emerging_equipment_alerts = load_processed_table("emerging_equipment_alerts.csv")

    st.subheader("Executive Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Completed / Verified Callbacks",
        get_summary_value(executive_summary, "Completed / verified callbacks"),
    )
    col2.metric(
        "Unique Accounts",
        get_summary_value(executive_summary, "Unique accounts"),
    )
    col3.metric(
        "Unique Equipment",
        get_summary_value(executive_summary, "Unique equipment"),
    )
    col4.metric(
        "Total Mantraps",
        get_summary_value(executive_summary, "Total mantraps"),
    )

    col5, col6, col7 = st.columns(3)

    col5.metric(
        "Median Response Minutes",
        get_summary_value(executive_summary, "Median response minutes"),
    )
    col6.metric(
        "Median Repair Minutes",
        get_summary_value(executive_summary, "Median repair minutes"),
    )
    col7.metric(
        "Top Fault Family",
        get_summary_value(executive_summary, "Top fault family"),
    )

    st.divider()

    st.subheader("Fault Family Summary")

    fault_family_chart = px.bar(
        fault_family_summary.sort_values("callbacks", ascending=True),
        x="callbacks",
        y="fault_family_final",
        orientation="h",
        title="Callbacks by Fault Family",
        hover_data=[
            "mantraps",
            "mantrap_rate_pct",
            "median_response_minutes",
            "median_repair_minutes",
        ],
    )

    st.plotly_chart(fault_family_chart, use_container_width=True)

    st.dataframe(
        fault_family_summary[
            [
                "fault_family_final",
                "callbacks",
                "callback_share_pct",
                "mantraps",
                "mantrap_rate_pct",
                "median_response_minutes",
                "median_repair_minutes",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Equipment Risk Ranking")

    risk_tier_options = sorted(
        equipment_risk_model["risk_tier"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_risk_tiers = st.multiselect(
        "Filter equipment by risk tier",
        options=risk_tier_options,
        default=risk_tier_options,
    )

    filtered_equipment = equipment_risk_model[
        equipment_risk_model["risk_tier"].astype(str).isin(selected_risk_tiers)
    ].copy()

    st.dataframe(
        filtered_equipment[
            [
                "equipment_description_raw",
                "account_name_raw",
                "equipment_type",
                "callbacks",
                "mantraps",
                "mantrap_rate_pct",
                "callbacks_last_365_days",
                "mantraps_last_365_days",
                "equipment_risk_score_v3",
                "risk_tier",
                "risk_signal_type",
            ]
        ].head(100),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Account Risk Ranking")

    st.dataframe(
        account_risk_model[
            [
                "account_code",
                "account_name_raw",
                "callbacks",
                "mantraps",
                "unique_equipment",
                "callbacks_per_equipment",
                "mantrap_rate_pct",
                "median_response_minutes",
                "median_repair_minutes",
                "account_risk_score",
                "risk_tier",
            ]
        ].head(100),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Emerging Equipment Alerts")
    st.caption(
        "Low-history equipment with early serious signals. These are not established risks yet."
    )

    st.dataframe(
        emerging_equipment_alerts[
            [
                "equipment_description_raw",
                "account_name_raw",
                "equipment_type",
                "callbacks",
                "mantraps",
                "mantrap_rate_pct",
                "median_response_minutes",
                "median_repair_minutes",
                "risk_signal_type",
            ]
        ].head(100),
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    main()