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


def render_metadata_header(metadata: dict, period_context: dict | None = None) -> None:
    """Render pipeline metadata summary below the dashboard title."""
    run_timestamp = metadata.get("run_timestamp", "Not available")
    latest_event_month = metadata.get("latest_event_month", "-")
    raw_callback_file_count = metadata.get("raw_callback_file_count", "-")
    callbacks_raw_rows = metadata.get("callbacks_raw_rows", "-")
    validation_status = metadata.get("validation_status", "Not available")

    period_label = "-"
    filtered_rows = "-"
    completed_rows = "-"
    mantraps = "-"

    if period_context:
        period_label = period_context.get("period_label", "-")
        filtered_rows = f"{period_context.get('filtered_rows', 0):,}"
        completed_rows = f"{period_context.get('completed_or_verified_rows', 0):,}"
        mantraps = f"{period_context.get('mantraps', 0):,}"

    st.markdown(
        f"""
        <div class="command-card">
            <div class="command-card-title">Pipeline Status</div>
            <div class="command-card-caption">
                Last run: <b>{run_timestamp}</b> &nbsp; | &nbsp;
                Latest event month: <b>{latest_event_month}</b> &nbsp; | &nbsp;
                Raw callback files: <b>{raw_callback_file_count}</b> &nbsp; | &nbsp;
                Raw rows: <b>{callbacks_raw_rows}</b> &nbsp; | &nbsp;
                Validation: <b>{validation_status}</b>
                <br><br>
                Current period: <b>{period_label}</b> &nbsp; | &nbsp;
                Filtered rows: <b>{filtered_rows}</b> &nbsp; | &nbsp;
                Completed/verified: <b>{completed_rows}</b> &nbsp; | &nbsp;
                Mantraps: <b>{mantraps}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )