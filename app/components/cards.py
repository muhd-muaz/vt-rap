from __future__ import annotations

import html

import pandas as pd
import streamlit as st


def normalise_metric_name(value: object) -> str:
    """Normalize metric names for flexible matching."""
    return (
        str(value).strip().lower().replace("-", "_").replace("/", "_").replace(" ", "_")
    )


def get_summary_value(summary: pd.DataFrame, metric_name: str) -> str:
    """Return a metric value from the executive summary table."""
    if summary.empty:
        return "-"

    metric_column = "metric" if "metric" in summary.columns else summary.columns[0]
    value_column = "value" if "value" in summary.columns else summary.columns[1]

    target_metric = normalise_metric_name(metric_name)

    working_summary = summary.copy()
    working_summary["_normalised_metric"] = working_summary[metric_column].map(
        normalise_metric_name
    )

    matched_rows = working_summary.loc[
        working_summary["_normalised_metric"].eq(target_metric),
        value_column,
    ]

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


def render_app_header() -> None:
    """Render the main dashboard header."""
    st.markdown(
        """
        <div class="app-hero">
            <div>
                <div class="app-eyebrow">Vertical Transport Reliability Analytics Platform</div>
                <div class="app-title">VT-RAP Command Center</div>
                <div class="app-subtitle">
                    Monitor callback volume, mantrap risk, equipment reliability,
                    fault-code patterns, and operational data quality.
                </div>
            </div>
            <div class="app-status-pill">
                <span class="status-dot"></span>
                Live analytics view
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_command_card(title: str, value: str, caption: str = "") -> None:
    """Render a styled metric card."""
    safe_title = html.escape(str(title))
    safe_value = html.escape(str(value))
    safe_caption = html.escape(str(caption))

    st.markdown(
        f"""
        <div class="command-card">
            <div class="command-card-title">{safe_title}</div>
            <div class="command-card-value">{safe_value}</div>
            <div class="command-card-caption">{safe_caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metadata_header(metadata: dict, period_context: dict | None = None) -> None:
    """Render pipeline and selected-period metadata using native Streamlit components."""
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

    with st.container(border=True):
        st.caption("Pipeline")

        (
            pipeline_col_1,
            pipeline_col_2,
            pipeline_col_3,
            pipeline_col_4,
            pipeline_col_5,
        ) = st.columns(5)

        pipeline_col_1.metric("Last run", run_timestamp)
        pipeline_col_2.metric("Latest event month", latest_event_month)
        pipeline_col_3.metric("Raw files", raw_callback_file_count)
        pipeline_col_4.metric("Raw rows", callbacks_raw_rows)
        pipeline_col_5.metric("Validation", validation_status)

        st.divider()

        st.caption("Current analysis period")

        period_col_1, period_col_2, period_col_3, period_col_4 = st.columns(4)

        period_col_1.metric("Period", period_label)
        period_col_2.metric("Filtered rows", filtered_rows)
        period_col_3.metric("Completed / verified", completed_rows)
        period_col_4.metric("Mantraps", mantraps)
