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
from components.tables import format_table_for_display


def render_executive_overview(
    executive_summary: pd.DataFrame,
    fault_family_summary: pd.DataFrame,
    equipment_risk_model: pd.DataFrame,
    account_risk_model: pd.DataFrame,
    emerging_equipment_alerts: pd.DataFrame,
    monthly_callback_trend: pd.DataFrame,
) -> None:
    """Render executive overview tab."""
    st.subheader("Executive Overview")

    kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)

    with kpi_1:
        render_command_card(
            "Completed / Verified Callbacks",
            get_summary_value(executive_summary, "Completed / verified callbacks"),
            "Clean operational records used for management analytics.",
        )

    with kpi_2:
        render_command_card(
            "Total Mantraps",
            get_summary_value(executive_summary, "Total mantraps"),
            "Trapped-passenger related callback events.",
        )

    with kpi_3:
        render_command_card(
            "Median Response",
            f"{get_summary_value(executive_summary, 'Median response minutes')} min",
            "Median time from realised event to attendance.",
        )

    with kpi_4:
        render_command_card(
            "Median Repair",
            f"{get_summary_value(executive_summary, 'Median repair minutes')} min",
            "Median time from attendance to completion.",
        )

    risk_1, risk_2, risk_3, risk_4 = st.columns(4)

    critical_count = int(
        equipment_risk_model["risk_tier"].astype(str).eq("Critical").sum()
    )
    high_count = int(equipment_risk_model["risk_tier"].astype(str).eq("High").sum())
    emerging_count = len(emerging_equipment_alerts)
    unclassified_count = int(
        fault_family_summary.loc[
            fault_family_summary["fault_family_final"].eq("Unclassified"),
            "callbacks",
        ].sum()
    )

    with risk_1:
        render_command_card(
            "Critical Equipment",
            f"{critical_count:,}",
            "Established assets with the highest risk scores.",
        )

    with risk_2:
        render_command_card(
            "High-Risk Equipment",
            f"{high_count:,}",
            "Assets requiring operational monitoring.",
        )

    with risk_3:
        render_command_card(
            "Emerging Alerts",
            f"{emerging_count:,}",
            "Low-history assets with early mantrap signals.",
        )

    with risk_4:
        render_command_card(
            "Unclassified Faults",
            f"{unclassified_count:,}",
            "Callbacks without mapped recorded fault code.",
        )

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.plotly_chart(
            build_monthly_callback_chart(monthly_callback_trend),
            use_container_width=True,
            key="overview_monthly_callback_chart",
        )

    with chart_right:
        st.plotly_chart(
            build_monthly_response_repair_chart(monthly_callback_trend),
            use_container_width=True,
            key="overview_monthly_response_repair_chart",
        )

    st.plotly_chart(
        build_fault_family_chart(fault_family_summary),
        use_container_width=True,
        key="overview_fault_family_chart",
    )

    left_column, right_column = st.columns(2)

    with left_column:
        st.markdown("### Top Equipment Risk")
        equipment_columns = [
            "equipment_description_raw",
            "account_name_raw",
            "equipment_type",
            "callbacks",
            "mantraps",
            "callbacks_last_365_days",
            "mantraps_last_365_days",
            "equipment_risk_score_v3",
            "risk_tier",
            "primary_risk_driver",
        ]

        st.dataframe(
            format_table_for_display(equipment_risk_model[equipment_columns].head(15)),
            use_container_width=True,
            hide_index=True,
        )

    with right_column:
        st.markdown("### Top Account Risk")
        st.plotly_chart(
            build_top_account_chart(account_risk_model),
            use_container_width=True,
            key="overview_top_account_chart",
        )