from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards_v2 import render_detail_panel, render_metric_card
from components.layout_v2 import render_section_header
from components.downloads import render_csv_download_button


def get_quality_row(
    data_quality_summary: pd.DataFrame,
    check_name: str,
) -> pd.Series | None:
    """Return a data-quality row by exact check name."""
    matched_rows = data_quality_summary[
        data_quality_summary["check_name"].eq(check_name)
    ]

    if matched_rows.empty:
        return None

    return matched_rows.iloc[0]


def format_number(value: object) -> str:
    """Format number for dashboard cards."""
    try:
        numeric_value = float(value)

        if numeric_value.is_integer():
            return f"{int(numeric_value):,}"

        return f"{numeric_value:,.2f}"

    except (TypeError, ValueError):
        return str(value)


def get_quality_value(
    data_quality_summary: pd.DataFrame,
    check_name: str,
) -> str:
    """Return formatted value for a quality check."""
    row = get_quality_row(data_quality_summary, check_name)

    if row is None:
        return "-"

    return format_number(row["value"])


def get_quality_rate(
    data_quality_summary: pd.DataFrame,
    check_name: str,
) -> str:
    """Return formatted rate percentage for a quality check."""
    row = get_quality_row(data_quality_summary, check_name)

    if row is None:
        return "-"

    return f"{float(row['rate_pct']):,.2f}%"


def get_quality_rate_number(
    data_quality_summary: pd.DataFrame,
    check_name: str,
) -> float:
    """Return numeric rate percentage for a quality check."""
    row = get_quality_row(data_quality_summary, check_name)

    if row is None:
        return 0.0

    return float(row["rate_pct"])


def render_quality_overview_cards(data_quality_summary: pd.DataFrame) -> None:
    """Render data quality KPI cards."""
    card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(4, gap="medium")

    with card_col_1:
        render_metric_card(
            title="Total records",
            value=get_quality_value(data_quality_summary, "Total callback records"),
            caption="All callback records loaded into the pipeline.",
            accent="default",
        )

    with card_col_2:
        render_metric_card(
            title="Completed / verified",
            value=get_quality_value(
                data_quality_summary,
                "Completed / verified records",
            ),
            caption=(
                f"{get_quality_rate(data_quality_summary, 'Completed / verified records')} "
                "of records are finalized for analysis."
            ),
            accent="blue",
        )

    with card_col_3:
        render_metric_card(
            title="Fault-code match",
            value=get_quality_rate(
                data_quality_summary,
                "Fault-code master matched rows",
            ),
            caption="Recorded fault codes matched to the fault-code master.",
            accent="violet",
        )

    with card_col_4:
        render_metric_card(
            title="Missing fault codes",
            value=get_quality_value(
                data_quality_summary,
                "Missing fault-code rows",
            ),
            caption=(
                f"{get_quality_rate(data_quality_summary, 'Missing fault-code rows')} "
                "of records are retained as Unclassified."
            ),
            accent="warning",
        )


def render_quality_risk_cards(data_quality_summary: pd.DataFrame) -> None:
    """Render data-quality risk cards."""
    card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(4, gap="medium")

    with card_col_1:
        render_metric_card(
            title="Invalid response",
            value=get_quality_value(
                data_quality_summary,
                "Invalid response-time rows",
            ),
            caption=(
                f"{get_quality_rate(data_quality_summary, 'Invalid response-time rows')} "
                "of records have invalid response duration."
            ),
            accent="danger",
        )

    with card_col_2:
        render_metric_card(
            title="Invalid repair",
            value=get_quality_value(
                data_quality_summary,
                "Invalid repair-time rows",
            ),
            caption=(
                f"{get_quality_rate(data_quality_summary, 'Invalid repair-time rows')} "
                "of records have invalid repair duration."
            ),
            accent="danger",
        )

    with card_col_3:
        render_metric_card(
            title="Open / in process",
            value=get_quality_value(
                data_quality_summary,
                "Open / in-process rows",
            ),
            caption="Records not yet finalized at source status level.",
            accent="warning",
        )

    with card_col_4:
        render_metric_card(
            title="Rejected",
            value=get_quality_value(
                data_quality_summary,
                "Rejected rows",
            ),
            caption="Rejected records retained for audit visibility.",
            accent="violet",
        )


def render_data_quality_interpretation(data_quality_summary: pd.DataFrame) -> None:
    """Render management interpretation of data quality."""
    fault_code_match_rate = get_quality_rate_number(
        data_quality_summary,
        "Fault-code master matched rows",
    )

    missing_fault_codes = get_quality_value(
        data_quality_summary,
        "Missing fault-code rows",
    )

    invalid_response = get_quality_value(
        data_quality_summary,
        "Invalid response-time rows",
    )

    invalid_repair = get_quality_value(
        data_quality_summary,
        "Invalid repair-time rows",
    )

    trust_label = "Strong"
    trust_description = (
        "The dataset is suitable for management reporting and operational analysis."
    )

    if fault_code_match_rate < 90:
        trust_label = "Moderate"
        trust_description = (
            "The dataset can still be used, but unmatched fault-code records should "
            "be reviewed before relying heavily on fault-code conclusions."
        )

    if fault_code_match_rate < 75:
        trust_label = "Needs review"
        trust_description = (
            "Fault-code coverage is low. Use high-level trend metrics carefully and "
            "prioritize source-data cleanup."
        )

    render_detail_panel(
        eyebrow="Data quality interpretation",
        title="Pipeline trust and analysis readiness",
        items=[
            (
                "Trust level",
                trust_label,
                trust_description,
            ),
            (
                "Fault-code coverage",
                f"{fault_code_match_rate:,.2f}%",
                "Matched against the uploaded fault-code master table.",
            ),
            (
                "Missing fault codes",
                missing_fault_codes,
                "These records are retained as Unclassified, not removed.",
            ),
            (
                "Timing validity",
                f"{invalid_response} / {invalid_repair}",
                "Invalid response and repair rows are excluded from median timing calculations.",
            ),
        ],
    )


def render_quality_table(data_quality_summary: pd.DataFrame) -> None:
    """Render full data-quality summary table."""
    render_section_header(
        title="Full data quality summary",
        subtitle="Detailed audit metrics generated from the processed callback dataset.",
    )

    st.dataframe(
        data_quality_summary,
        width="stretch",
        hide_index=True,
    )

    render_csv_download_button(
        dataframe=data_quality_summary,
        filename_prefix="data_quality_summary",
        label="Download data quality summary CSV",
        key="download_data_quality_summary",
    )


def render_data_quality(
    data_quality_summary: pd.DataFrame,
    metadata: dict | None = None,
) -> None:
    """Render data quality dashboard page."""
    render_section_header(
        title="Data quality",
        subtitle="Audit source completeness, status coverage, timing validity, and fault-code matching.",
    )

    render_quality_overview_cards(data_quality_summary)
    render_quality_risk_cards(data_quality_summary)
    render_data_quality_interpretation(data_quality_summary)
    render_quality_table(data_quality_summary)
