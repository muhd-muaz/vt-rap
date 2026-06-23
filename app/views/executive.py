from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards import get_summary_value, render_command_card
from components.charts import (
    build_fault_family_chart,
    build_monthly_callback_chart,
    build_monthly_response_repair_chart,
    build_top_account_chart,
)
from components.layout import render_section_header


def render_management_interpretation(
    executive_summary: pd.DataFrame,
    fault_family_summary: pd.DataFrame,
    equipment_risk_model: pd.DataFrame,
    account_risk_model: pd.DataFrame,
    emerging_equipment_alerts: pd.DataFrame,
) -> None:
    """Render concise management interpretation for the current period."""
    analyzed_callbacks = get_summary_value(
        executive_summary,
        "Completed / verified callbacks",
    )
    total_mantraps = get_summary_value(executive_summary, "Total mantraps")
    median_response = get_summary_value(
        executive_summary,
        "Median response minutes",
    )
    median_repair = get_summary_value(
        executive_summary,
        "Median repair minutes",
    )
    top_fault_family = get_summary_value(executive_summary, "Top fault family")
    top_risk_account = get_summary_value(executive_summary, "Top risk account")
    top_risk_equipment = get_summary_value(executive_summary, "Top risk equipment")

    if top_fault_family == "-" and not fault_family_summary.empty:
        top_fault_family = str(fault_family_summary.iloc[0]["fault_family_final"])

    critical_equipment = 0
    if "risk_tier" in equipment_risk_model.columns:
        critical_equipment = int(equipment_risk_model["risk_tier"].eq("Critical").sum())

    critical_accounts = 0
    if "risk_tier" in account_risk_model.columns:
        critical_accounts = int(account_risk_model["risk_tier"].eq("Critical").sum())

    emerging_count = len(emerging_equipment_alerts)

    st.markdown(
        f"""
        <div class="insight-panel">
            <div class="insight-panel-title">Management interpretation</div>
            <div class="insight-grid">
                <div>
                    <span>Analyzed workload</span>
                    <strong>{analyzed_callbacks}</strong>
                    <p>Completed or verified callbacks used for operational analysis.</p>
                </div>
                <div>
                    <span>Mantrap exposure</span>
                    <strong>{total_mantraps}</strong>
                    <p>Callback events marked as mantrap-related.</p>
                </div>
                <div>
                    <span>Dominant fault family</span>
                    <strong>{top_fault_family}</strong>
                    <p>Highest-volume grouped fault family.</p>
                </div>
                <div>
                    <span>Service timing</span>
                    <strong>{median_response} / {median_repair} min</strong>
                    <p>Median response and repair duration.</p>
                </div>
                <div>
                    <span>Top risk account</span>
                    <strong>{top_risk_account}</strong>
                    <p>Account with the highest risk score in the selected period.</p>
                </div>
                <div>
                    <span>Top risk equipment</span>
                    <strong>{top_risk_equipment}</strong>
                    <p>Equipment with the highest risk score in the selected period.</p>
                </div>
                <div>
                    <span>Critical equipment</span>
                    <strong>{critical_equipment:,}</strong>
                    <p>Equipment currently classified as critical risk.</p>
                </div>
                <div>
                    <span>Critical accounts</span>
                    <strong>{critical_accounts:,}</strong>
                    <p>Accounts currently classified as critical risk.</p>
                </div>
                <div>
                    <span>Emerging alerts</span>
                    <strong>{emerging_count:,}</strong>
                    <p>Low-history equipment with early warning signals.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top_tables(
    equipment_risk_model: pd.DataFrame,
    account_risk_model: pd.DataFrame,
    emerging_equipment_alerts: pd.DataFrame,
) -> None:
    """Render compact top-risk tables."""
    table_col_1, table_col_2 = st.columns(2)

    with table_col_1:
        render_section_header(
            title="Highest-risk equipment",
            subtitle="Top equipment ranked by risk score for the selected period.",
        )

        equipment_columns = [
            "equipment_description_raw",
            "account_name_raw",
            "equipment_type",
            "callbacks",
            "mantraps",
            "equipment_risk_score_v3",
            "risk_tier",
            "primary_risk_driver",
        ]

        available_equipment_columns = [
            column for column in equipment_columns if column in equipment_risk_model
        ]

        st.dataframe(
            equipment_risk_model[available_equipment_columns].head(12),
            width="stretch",
            hide_index=True,
        )

    with table_col_2:
        render_section_header(
            title="Highest-risk accounts",
            subtitle="Top accounts ranked by operational risk score.",
        )

        account_columns = [
            "account_name_raw",
            "callbacks",
            "mantraps",
            "unique_equipment",
            "account_risk_score",
            "risk_tier",
            "primary_risk_driver",
        ]

        available_account_columns = [
            column for column in account_columns if column in account_risk_model
        ]

        st.dataframe(
            account_risk_model[available_account_columns].head(12),
            width="stretch",
            hide_index=True,
        )

    render_section_header(
        title="Emerging equipment alerts",
        subtitle="Equipment with limited history but meaningful recent warning signals.",
    )

    emerging_columns = [
        "equipment_description_raw",
        "account_name_raw",
        "equipment_type",
        "callbacks",
        "mantraps",
        "recent_90d_callbacks",
        "recent_90d_mantraps",
        "equipment_risk_score_v3",
        "primary_risk_driver",
    ]

    available_emerging_columns = [
        column for column in emerging_columns if column in emerging_equipment_alerts
    ]

    st.dataframe(
        emerging_equipment_alerts[available_emerging_columns].head(15),
        width="stretch",
        hide_index=True,
    )


def render_executive_overview(
    executive_summary: pd.DataFrame,
    fault_family_summary: pd.DataFrame,
    equipment_risk_model: pd.DataFrame,
    account_risk_model: pd.DataFrame,
    emerging_equipment_alerts: pd.DataFrame,
    monthly_callback_trend: pd.DataFrame,
) -> None:
    """Render the executive overview dashboard page."""
    render_section_header(
        title="Executive Overview",
        subtitle=(
            "A management-level summary of analyzed callback volume, "
            "mantrap exposure, response timing, and reliability risk."
        ),
    )

    kpi_col_1, kpi_col_2, kpi_col_3, kpi_col_4 = st.columns(4)

    with kpi_col_1:
        render_command_card(
            title="Analyzed Callbacks",
            value=get_summary_value(
                executive_summary,
                "Completed / verified callbacks",
            ),
            caption="Completed or verified callback records used for operational analysis.",
        )

    with kpi_col_2:
        render_command_card(
            title="Unique Accounts",
            value=get_summary_value(executive_summary, "Unique accounts"),
            caption="Customer accounts represented in the selected period.",
        )

    with kpi_col_3:
        render_command_card(
            title="Total Mantraps",
            value=get_summary_value(executive_summary, "Total mantraps"),
            caption="Callback events flagged as mantrap.",
        )

    with kpi_col_4:
        render_command_card(
            title="Median Response",
            value=(
                f"{get_summary_value(executive_summary, 'Median response minutes')} min"
            ),
            caption="Median time from event to attendance.",
        )

    secondary_col_1, secondary_col_2, secondary_col_3, secondary_col_4 = st.columns(4)

    with secondary_col_1:
        render_command_card(
            title="Unique Equipment",
            value=get_summary_value(executive_summary, "Unique equipment"),
            caption="Equipment units represented in the analysis base.",
        )

    with secondary_col_2:
        render_command_card(
            title="Median Repair",
            value=f"{get_summary_value(executive_summary, 'Median repair minutes')} min",
            caption="Median time from attendance to completion.",
        )

    with secondary_col_3:
        render_command_card(
            title="Top Fault Family",
            value=get_summary_value(executive_summary, "Top fault family"),
            caption="Highest-volume grouped fault family.",
        )

    with secondary_col_4:
        render_command_card(
            title="Top Risk Account",
            value=get_summary_value(executive_summary, "Top risk account"),
            caption="Account with the highest operational risk score.",
        )

    trend_col_1, trend_col_2 = st.columns(2)

    with trend_col_1:
        st.plotly_chart(
            build_monthly_callback_chart(monthly_callback_trend),
            width="stretch",
            key="executive_monthly_callback_chart",
        )

    with trend_col_2:
        st.plotly_chart(
            build_monthly_response_repair_chart(monthly_callback_trend),
            width="stretch",
            key="executive_monthly_response_repair_chart",
        )

    analysis_col_1, analysis_col_2 = st.columns([1.05, 1])

    with analysis_col_1:
        st.plotly_chart(
            build_fault_family_chart(fault_family_summary),
            width="stretch",
            key="executive_fault_family_chart",
        )

    with analysis_col_2:
        st.plotly_chart(
            build_top_account_chart(account_risk_model),
            width="stretch",
            key="executive_top_account_chart",
        )

    render_management_interpretation(
        executive_summary=executive_summary,
        fault_family_summary=fault_family_summary,
        equipment_risk_model=equipment_risk_model,
        account_risk_model=account_risk_model,
        emerging_equipment_alerts=emerging_equipment_alerts,
    )

    render_top_tables(
        equipment_risk_model=equipment_risk_model,
        account_risk_model=account_risk_model,
        emerging_equipment_alerts=emerging_equipment_alerts,
    )
