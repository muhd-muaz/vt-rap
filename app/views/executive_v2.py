from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from components.cards import get_summary_value
from components.cards_v2 import render_summary_metric_card
from components.charts import (
    build_fault_family_chart,
    build_monthly_callback_chart,
    build_monthly_response_repair_chart,
    build_top_account_chart,
)
from components.layout_v2 import render_section_header


def count_risk_tier(dataframe: pd.DataFrame, tier: str) -> int:
    """Count rows in a risk tier."""
    if dataframe.empty or "risk_tier" not in dataframe.columns:
        return 0

    return int(dataframe["risk_tier"].astype(str).eq(tier).sum())


def safe_summary_value(
    executive_summary: pd.DataFrame,
    metric_name: str,
    fallback: str = "No data",
) -> str:
    """Return escaped executive summary value for HTML rendering."""
    value = get_summary_value(executive_summary, metric_name)

    if value in {"", "-", None}:
        return fallback

    return html.escape(str(value))


def render_v2_insight_panel(
    executive_summary: pd.DataFrame,
    equipment_risk_model: pd.DataFrame,
    account_risk_model: pd.DataFrame,
    emerging_equipment_alerts: pd.DataFrame,
) -> None:
    """Render app-style executive interpretation panel."""
    top_fault_family = safe_summary_value(executive_summary, "Top fault family")
    top_risk_account = safe_summary_value(executive_summary, "Top risk account")
    top_risk_equipment = safe_summary_value(executive_summary, "Top risk equipment")
    median_response = safe_summary_value(executive_summary, "Median response minutes")
    median_repair = safe_summary_value(executive_summary, "Median repair minutes")

    critical_equipment = count_risk_tier(equipment_risk_model, "Critical")
    critical_accounts = count_risk_tier(account_risk_model, "Critical")

    st.markdown(
        f"""
        <div class="v2-insight-panel">
            <div class="v2-insight-copy">
                <div class="v2-eyebrow">Operational readout</div>
                <div class="v2-insight-title">Reliability focus for the selected period</div>
                <div class="v2-insight-text">
                    The dominant fault family is <strong>{top_fault_family}</strong>.
                    The highest-risk account is <strong>{top_risk_account}</strong>,
                    while the highest-risk equipment is <strong>{top_risk_equipment}</strong>.
                    Median response and repair timing are currently
                    <strong>{median_response} min</strong> and
                    <strong>{median_repair} min</strong>.
                </div>
            </div>
            <div class="v2-insight-stats">
                <div>
                    <span>Critical equipment</span>
                    <strong>{critical_equipment:,}</strong>
                </div>
                <div>
                    <span>Critical accounts</span>
                    <strong>{critical_accounts:,}</strong>
                </div>
                <div>
                    <span>Emerging alerts</span>
                    <strong>{len(emerging_equipment_alerts):,}</strong>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_v2_chart_card(title: str, subtitle: str, chart_key: str, figure) -> None:
    """Render a chart inside a V2 card surface."""
    safe_title = html.escape(str(title))
    safe_subtitle = html.escape(str(subtitle))

    st.markdown(
        f"""
        <div class="v2-card-heading">
            <div>
                <div class="v2-card-title">{safe_title}</div>
                <div class="v2-card-subtitle">{safe_subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        key=chart_key,
    )


def render_executive_overview_v2(
    executive_summary: pd.DataFrame,
    fault_family_summary: pd.DataFrame,
    equipment_risk_model: pd.DataFrame,
    account_risk_model: pd.DataFrame,
    emerging_equipment_alerts: pd.DataFrame,
    monthly_callback_trend: pd.DataFrame,
) -> None:
    """Render redesigned executive overview page."""
    kpi_col_1, kpi_col_2, kpi_col_3, kpi_col_4 = st.columns(4)

    with kpi_col_1:
        render_summary_metric_card(
            executive_summary=executive_summary,
            title="Analyzed callbacks",
            metric_name="Completed / verified callbacks",
            caption="Completed or verified callback records used for analysis.",
            accent="default",
        )

    with kpi_col_2:
        render_summary_metric_card(
            executive_summary=executive_summary,
            title="Mantrap exposure",
            metric_name="Total mantraps",
            caption="Callback events flagged as mantrap-related.",
            accent="danger",
        )

    with kpi_col_3:
        render_summary_metric_card(
            executive_summary=executive_summary,
            title="Median response",
            metric_name="Median response minutes",
            caption="Median time from event creation to attendance.",
            suffix=" min",
            accent="blue",
        )

    with kpi_col_4:
        render_summary_metric_card(
            executive_summary=executive_summary,
            title="Median repair",
            metric_name="Median repair minutes",
            caption="Median time from attendance to completion.",
            suffix=" min",
            accent="violet",
        )

    render_v2_insight_panel(
        executive_summary=executive_summary,
        equipment_risk_model=equipment_risk_model,
        account_risk_model=account_risk_model,
        emerging_equipment_alerts=emerging_equipment_alerts,
    )

    render_section_header(
        title="Callback and service timing",
        subtitle="Monthly workload and response/repair timing patterns.",
    )

    chart_col_1, chart_col_2 = st.columns(2)

    with chart_col_1:
        render_v2_chart_card(
            title="Monthly Callback Volume",
            subtitle="Callback volume trend for the selected period.",
            chart_key="executive_v2_monthly_callback_chart",
            figure=build_monthly_callback_chart(monthly_callback_trend),
        )

    with chart_col_2:
        render_v2_chart_card(
            title="Response and Repair Timing",
            subtitle="Median response and repair minutes by month.",
            chart_key="executive_v2_response_repair_chart",
            figure=build_monthly_response_repair_chart(monthly_callback_trend),
        )

    render_section_header(
        title="Risk focus",
        subtitle="Fault and account concentration for management review.",
    )

    risk_col_1, risk_col_2 = st.columns([1.05, 1])

    with risk_col_1:
        render_v2_chart_card(
            title="Fault Family Distribution",
            subtitle="Grouped fault categories by callback volume.",
            chart_key="executive_v2_fault_family_chart",
            figure=build_fault_family_chart(fault_family_summary),
        )

    with risk_col_2:
        render_v2_chart_card(
            title="Top Risk Accounts",
            subtitle="Accounts with the highest operational risk score.",
            chart_key="executive_v2_top_account_chart",
            figure=build_top_account_chart(account_risk_model),
        )
