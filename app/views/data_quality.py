from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards import render_command_card
from components.layout import render_section_header
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
    card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(4)

    with card_col_1:
        render_command_card(
            title="Total Records",
            value=get_quality_value(data_quality_summary, "Total callback records"),
            caption="All callback records loaded into the pipeline.",
        )

    with card_col_2:
        render_command_card(
            title="Completed / Verified",
            value=get_quality_value(
                data_quality_summary,
                "Completed / verified records",
            ),
            caption=(
                f"{get_quality_rate(data_quality_summary, 'Completed / verified records')} "
                "of records are finalized for analysis."
            ),
        )

    with card_col_3:
        render_command_card(
            title="Fault-Code Match",
            value=get_quality_rate(
                data_quality_summary,
                "Fault-code master matched rows",
            ),
            caption="Recorded fault codes matched to the fault-code master.",
        )

    with card_col_4:
        render_command_card(
            title="Missing Fault Codes",
            value=get_quality_value(
                data_quality_summary,
                "Missing fault-code rows",
            ),
            caption=(
                f"{get_quality_rate(data_quality_summary, 'Missing fault-code rows')} "
                "of records are retained as Unclassified."
            ),
        )


def render_quality_risk_cards(data_quality_summary: pd.DataFrame) -> None:
    """Render data-quality risk cards."""
    card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(4)

    with card_col_1:
        render_command_card(
            title="Invalid Response",
            value=get_quality_value(
                data_quality_summary,
                "Invalid response-time rows",
            ),
            caption=(
                f"{get_quality_rate(data_quality_summary, 'Invalid response-time rows')} "
                "of records have invalid response duration."
            ),
        )

    with card_col_2:
        render_command_card(
            title="Invalid Repair",
            value=get_quality_value(
                data_quality_summary,
                "Invalid repair-time rows",
            ),
            caption=(
                f"{get_quality_rate(data_quality_summary, 'Invalid repair-time rows')} "
                "of records have invalid repair duration."
            ),
        )

    with card_col_3:
        render_command_card(
            title="Open / In Process",
            value=get_quality_value(
                data_quality_summary,
                "Open / in-process rows",
            ),
            caption="Records not yet finalized at source status level.",
        )

    with card_col_4:
        render_command_card(
            title="Rejected",
            value=get_quality_value(
                data_quality_summary,
                "Rejected rows",
            ),
            caption="Rejected records retained for audit visibility.",
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

    st.markdown(
        f"""
        <div class="insight-panel">
            <div class="insight-panel-title">Data quality interpretation</div>
            <div class="insight-grid">
                <div>
                    <span>Trust level</span>
                    <strong>{trust_label}</strong>
                    <p>{trust_description}</p>
                </div>
                <div>
                    <span>Fault-code coverage</span>
                    <strong>{fault_code_match_rate:,.2f}%</strong>
                    <p>Matched against the uploaded fault-code master table.</p>
                </div>
                <div>
                    <span>Missing fault codes</span>
                    <strong>{missing_fault_codes}</strong>
                    <p>These records are retained as Unclassified, not removed.</p>
                </div>
                <div>
                    <span>Timing validity</span>
                    <strong>{invalid_response} / {invalid_repair}</strong>
                    <p>Invalid response and repair rows are excluded from median timing calculations.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quality_table(data_quality_summary: pd.DataFrame) -> None:
    """Render full data-quality summary table."""
    render_section_header(
        title="Full Data Quality Summary",
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


def render_data_quality(data_quality_summary: pd.DataFrame) -> None:
    """Render data quality dashboard page."""
    render_section_header(
        title="Data Quality",
        subtitle="Audit source completeness, status coverage, timing validity, and fault-code matching.",
    )

    render_quality_overview_cards(data_quality_summary)
    render_quality_risk_cards(data_quality_summary)
    render_data_quality_interpretation(data_quality_summary)
    render_quality_table(data_quality_summary)
