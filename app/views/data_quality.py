from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards import render_command_card
from components.tables import format_table_for_display


def get_quality_value(
    data_quality_summary: pd.DataFrame,
    check_name: str,
    value_column: str = "value",
) -> str:
    """Return a formatted data quality value."""
    matched_rows = data_quality_summary.loc[
        data_quality_summary["check_name"].eq(check_name),
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


def render_quality_status_panel(data_quality_summary: pd.DataFrame) -> None:
    """Render high-level data quality cards."""
    card_1, card_2, card_3, card_4 = st.columns(4)

    with card_1:
        render_command_card(
            "Total Records",
            get_quality_value(data_quality_summary, "Total callback records"),
            "Raw callback records loaded into the pipeline.",
        )

    with card_2:
        render_command_card(
            "Completed / Verified",
            get_quality_value(data_quality_summary, "Completed / verified records"),
            "Records used for management analytics.",
        )

    with card_3:
        render_command_card(
            "Fault-Code Match Rate",
            f"{get_quality_value(data_quality_summary, 'Fault-code master matched rows', 'rate_pct')}%",
            "Rows matched against the fault-code master.",
        )

    with card_4:
        render_command_card(
            "Missing Fault Codes",
            get_quality_value(data_quality_summary, "Missing fault-code rows"),
            "Rows without recorded fault-code mapping.",
        )


def render_quality_review_panel(data_quality_summary: pd.DataFrame) -> None:
    """Render review-focused quality cards."""
    card_1, card_2, card_3, card_4 = st.columns(4)

    with card_1:
        render_command_card(
            "Invalid Response Times",
            get_quality_value(data_quality_summary, "Invalid response-time rows"),
            "Rows where response duration is negative or invalid.",
        )

    with card_2:
        render_command_card(
            "Invalid Repair Times",
            get_quality_value(data_quality_summary, "Invalid repair-time rows"),
            "Rows where repair duration is negative or invalid.",
        )

    with card_3:
        render_command_card(
            "Open / In-Process",
            get_quality_value(data_quality_summary, "Open / in-process rows"),
            "Records not yet completed or verified.",
        )

    with card_4:
        render_command_card(
            "Rejected Records",
            get_quality_value(data_quality_summary, "Rejected rows"),
            "Rows excluded from completed/verified analysis.",
        )


def render_quality_interpretation(data_quality_summary: pd.DataFrame) -> None:
    """Render plain-English interpretation of data quality status."""
    fault_match_rate = float(
        data_quality_summary.loc[
            data_quality_summary["check_name"].eq("Fault-code master matched rows"),
            "rate_pct",
        ].iloc[0]
    )

    missing_fault_rate = float(
        data_quality_summary.loc[
            data_quality_summary["check_name"].eq("Missing fault-code rows"),
            "rate_pct",
        ].iloc[0]
    )

    invalid_response_rate = float(
        data_quality_summary.loc[
            data_quality_summary["check_name"].eq("Invalid response-time rows"),
            "rate_pct",
        ].iloc[0]
    )

    invalid_repair_rate = float(
        data_quality_summary.loc[
            data_quality_summary["check_name"].eq("Invalid repair-time rows"),
            "rate_pct",
        ].iloc[0]
    )

    interpretation_points = []

    if fault_match_rate >= 95:
        interpretation_points.append(
            "Fault-code master coverage is strong enough for family-level analysis."
        )
    else:
        interpretation_points.append(
            "Fault-code master coverage needs review before relying heavily on fault-code analysis."
        )

    if missing_fault_rate <= 5:
        interpretation_points.append(
            "Missing fault-code volume is controlled but should still be monitored."
        )
    else:
        interpretation_points.append(
            "Missing fault-code volume is material and may affect fault-family conclusions."
        )

    if invalid_response_rate <= 2:
        interpretation_points.append(
            "Invalid response-time rows are low relative to the total dataset."
        )
    else:
        interpretation_points.append(
            "Invalid response-time rows should be reviewed before SLA-style reporting."
        )

    if invalid_repair_rate <= 1:
        interpretation_points.append(
            "Invalid repair-time rows are very low and unlikely to distort median repair analysis."
        )
    else:
        interpretation_points.append(
            "Invalid repair-time rows need review before repair-duration reporting."
        )

    st.markdown("### Audit Interpretation")

    for point in interpretation_points:
        st.markdown(f"- {point}")


def render_data_quality(data_quality_summary: pd.DataFrame) -> None:
    """Render data quality tab."""
    st.subheader("Data Quality Audit Panel")

    st.caption(
        "Checks source completeness, timing validity, fault-code coverage, and records excluded from management analytics."
    )

    render_quality_status_panel(data_quality_summary)

    st.markdown("### Records Requiring Review")

    render_quality_review_panel(data_quality_summary)

    render_quality_interpretation(data_quality_summary)

    st.markdown("### Full Data Quality Table")

    st.dataframe(
        format_table_for_display(data_quality_summary),
        use_container_width=True,
        hide_index=True,
    )