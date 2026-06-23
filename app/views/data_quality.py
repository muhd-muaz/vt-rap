from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards import render_command_card


def render_section_header(title: str, subtitle: str) -> None:
    """Render a clean section heading."""
    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-title">{title}</div>
            <div class="section-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_quality_value(
    data_quality_summary: pd.DataFrame,
    metric_name: str,
    value_column: str = "value",
) -> str:
    """Return a data-quality metric value."""
    matched_rows = data_quality_summary.loc[
        data_quality_summary["metric"].eq(metric_name),
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


def get_quality_numeric_value(
    data_quality_summary: pd.DataFrame,
    metric_name: str,
    value_column: str = "value",
) -> float:
    """Return a numeric data-quality metric value."""
    matched_rows = data_quality_summary.loc[
        data_quality_summary["metric"].eq(metric_name),
        value_column,
    ]

    if matched_rows.empty:
        return 0.0

    try:
        return float(matched_rows.iloc[0])

    except (TypeError, ValueError):
        return 0.0


def render_quality_overview_cards(data_quality_summary: pd.DataFrame) -> None:
    """Render data quality KPI cards."""
    total_records = get_quality_value(data_quality_summary, "total_records")
    completed_verified = get_quality_value(
        data_quality_summary,
        "completed_or_verified_records",
    )
    fault_code_match_rate = get_quality_value(
        data_quality_summary,
        "fault_code_match_rate_pct",
    )
    missing_fault_codes = get_quality_value(
        data_quality_summary,
        "missing_fault_code_records",
    )

    card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(4)

    with card_col_1:
        render_command_card(
            title="Total Records",
            value=total_records,
            caption="All callback records loaded into the pipeline.",
        )

    with card_col_2:
        render_command_card(
            title="Completed / Verified",
            value=completed_verified,
            caption="Records used as the core operational analysis base.",
        )

    with card_col_3:
        render_command_card(
            title="Fault-Code Match",
            value=f"{fault_code_match_rate}%",
            caption="Share of recorded fault codes matched to the fault-code master.",
        )

    with card_col_4:
        render_command_card(
            title="Missing Fault Codes",
            value=missing_fault_codes,
            caption="Records without a usable actual fault code.",
        )


def render_quality_risk_cards(data_quality_summary: pd.DataFrame) -> None:
    """Render data-quality risk cards."""
    invalid_response = get_quality_value(
        data_quality_summary,
        "invalid_response_time_records",
    )
    invalid_repair = get_quality_value(
        data_quality_summary,
        "invalid_repair_time_records",
    )
    open_in_process = get_quality_value(
        data_quality_summary,
        "open_or_in_process_records",
    )
    rejected = get_quality_value(
        data_quality_summary,
        "rejected_records",
    )

    card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(4)

    with card_col_1:
        render_command_card(
            title="Invalid Response",
            value=invalid_response,
            caption="Records where response duration is not analytically valid.",
        )

    with card_col_2:
        render_command_card(
            title="Invalid Repair",
            value=invalid_repair,
            caption="Records where repair duration is not analytically valid.",
        )

    with card_col_3:
        render_command_card(
            title="Open / In Process",
            value=open_in_process,
            caption="Records not yet finalized at source status level.",
        )

    with card_col_4:
        render_command_card(
            title="Rejected",
            value=rejected,
            caption="Rejected callback records retained for audit visibility.",
        )


def render_data_quality_interpretation(data_quality_summary: pd.DataFrame) -> None:
    """Render management interpretation of data quality."""
    fault_code_match_rate = get_quality_numeric_value(
        data_quality_summary,
        "fault_code_match_rate_pct",
    )
    missing_fault_codes = get_quality_value(
        data_quality_summary,
        "missing_fault_code_records",
    )
    invalid_response = get_quality_value(
        data_quality_summary,
        "invalid_response_time_records",
    )
    invalid_repair = get_quality_value(
        data_quality_summary,
        "invalid_repair_time_records",
    )

    trust_label = "Strong"
    trust_description = (
        "The dataset is suitable for management reporting and operational analysis."
    )

    if fault_code_match_rate < 90:
        trust_label = "Moderate"
        trust_description = (
            "The dataset can still be used, but missing or unmatched fault-code records "
            "should be reviewed before using fault-code conclusions heavily."
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
                    <p>Invalid response and repair records are excluded from median timing calculations.</p>
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
        use_container_width=True,
        hide_index=True,
    )


def render_data_quality(data_quality_summary: pd.DataFrame) -> None:
    """Render data quality dashboard page."""
    render_section_header(
        title="Data Quality",
        subtitle="Audit the reliability of source records, status coverage, timing validity, and fault-code matching.",
    )

    render_quality_overview_cards(data_quality_summary)
    render_quality_risk_cards(data_quality_summary)
    render_data_quality_interpretation(data_quality_summary)
    render_quality_table(data_quality_summary)