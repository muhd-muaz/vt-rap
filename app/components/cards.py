from __future__ import annotations

import pandas as pd
import streamlit as st


def get_summary_value(summary: pd.DataFrame, metric_name: str) -> str:
    """Return a metric value from the executive summary table."""
    matched_rows = summary.loc[summary["metric"].eq(metric_name), "value"]

    if matched_rows.empty:
        return "-"

    value = matched_rows.iloc[0]

    try:
        numeric_value = float(value)

        if numeric_value.is_integer():
            return f"{int(numeric_value):,}"

        return f"{numeric_value:,.2f}"

    except (TypeError, ValueError):
        return str(value)


def render_command_card(title: str, value: str, caption: str = "") -> None:
    """Render a styled command-center card."""
    st.markdown(
        f"""
        <div class="command-card">
            <div class="command-card-title">{title}</div>
            <div class="command-card-value">{value}</div>
            <div class="command-card-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )