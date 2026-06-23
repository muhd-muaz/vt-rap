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


def render_management_interpretation(
    executive_summary: pd.DataFrame,
    fault_family_summary: pd.DataFrame,
    equipment_risk_model: pd.DataFrame,
    account_risk_model: pd.DataFrame,
    emerging_equipment_alerts: pd.DataFrame,
) -> None:
    """Render concise management interpretation for the current period."""
    total_callbacks = get_summary_value(executive_summary, "total_callbacks")
    total_mantraps = get_summary_value(executive_summary, "total_mantraps")
    median_response = get_summary_value(
        executive_summary,
        "median_response_minutes",
    )
    median_repair = get_summary_value(
        executive_summary,
        "median_repair_minutes",
    )

    top_fault_family = "-"
    if not fault_family_summary.empty:
        top_fault_family = fault_family_summary.iloc[0]["fault_family_final"]

    critical_equipment = 0
    if "risk_tier" in equipment_risk_model.columns:
        critical_equipment = int(
            equipment_risk_model["risk_tier"].eq("Critical").sum()
        )

    critical_accounts = 0
    if "risk_tier" in account_risk_model.columns:
        critical_accounts = int(
            account_risk_model["risk_tier"].eq("Critical").sum()
        )

    emerging_count = len(emerging_equipment_alerts)

    st.markdown(
        f"""
        <div class="insight-panel">
            <div class="insight-panel-title">Management interpretation</div>
            <div class="insight-grid">
                <div>
                    <span>Current workload</span>
                    <strong>{total_callbacks}</strong>
                    <p>Total callbacks in the selected analysis period.</p>
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
            column for column in equipment_columns
            if column in equipment_risk_model.columns
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
            column for column in account_columns
            if column in account_risk_model.columns
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
        column for column in emerging_columns
        if column in emerging_equipment_alerts.columns
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
        subtitle="A management-level summary of callback volume, mantrap exposure, response timing, and reliability risk.",
    )

    kpi_col_1, kpi_col_2, kpi_col_3, kpi_col_4 = st.columns(4)

    with kpi_col_1:
        render_command_card(
            title="Total Callbacks",
            value=get_summary_value(executive_summary, "total_callbacks"),
            caption="All callback records in the selected period.",
        )

    with kpi_col_2:
        render_command_card(
            title="Completed / Verified",
            value=get_summary_value(
                executive_summary,
                "completed_or_verified_callbacks",
            ),
            caption="Records used for operational analysis.",
        )

    with kpi_col_3:
        render_command_card(
            title="Total Mantraps",
            value=get_summary_value(executive_summary, "total_mantraps"),
            caption="Callback events flagged as mantrap.",
        )

    with kpi_col_4:
        render_command_card(
            title="Median Response",
            value=f"{get_summary_value(executive_summary, 'median_response_minutes')} min",
            caption="Median time from event to attendance.",
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
        )

    analysis_col_1, analysis_col_2 = st.columns([1.05, 1])

    with analysis_col_1:
        st.plotly_chart(
            build_fault_family_chart(fault_family_summary),
            width="stretch",

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
