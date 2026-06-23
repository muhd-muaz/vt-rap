from __future__ import annotations

import pandas as pd
import streamlit as st

from components.charts import (
    build_equipment_type_trend_chart,
    build_fault_family_chart,
    build_fault_family_trend_chart,
)
from components.tables import format_table_for_display


def render_fault_analysis(
    fault_family_summary: pd.DataFrame,
    monthly_fault_family_trend: pd.DataFrame,
    monthly_equipment_type_trend: pd.DataFrame,
) -> None:
    """Render fault analysis tab."""
    st.subheader("Fault Family Analysis")

    st.plotly_chart(
        build_fault_family_chart(fault_family_summary),
        use_container_width=True,
        key="fault_analysis_fault_family_chart",
    )

    fault_family_options = (
        fault_family_summary["fault_family_final"].dropna().astype(str).tolist()
    )

    default_families = fault_family_options[:6]

    selected_fault_families = st.multiselect(
        "Select fault families for monthly trend",
        options=fault_family_options,
        default=default_families,
    )

    st.plotly_chart(
        build_fault_family_trend_chart(
            monthly_fault_family_trend,
            selected_fault_families,
        ),
        use_container_width=True,
        key="fault_family_monthly_trend_chart",
    )

    st.plotly_chart(
        build_equipment_type_trend_chart(monthly_equipment_type_trend),
        use_container_width=True,
        key="equipment_type_monthly_trend_chart",
    )

    table_columns = [
        "fault_family_final",
        "callbacks",
        "callback_share_pct",
        "mantraps",
        "mantrap_rate_pct",
        "unique_accounts",
        "unique_equipment",
        "median_response_minutes",
        "median_repair_minutes",
    ]

    st.dataframe(
        format_table_for_display(fault_family_summary[table_columns]),
        use_container_width=True,
        hide_index=True,
    )