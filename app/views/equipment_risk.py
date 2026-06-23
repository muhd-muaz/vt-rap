from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards import render_command_card
from components.charts import (
    build_equipment_fault_mix_chart,
    build_equipment_monthly_chart,
)
from components.filters import build_equipment_risk_filters
from components.tables import format_table_for_display


def render_equipment_risk(
    equipment_risk_model: pd.DataFrame,
    monthly_equipment_trend: pd.DataFrame,
    equipment_fault_family_mix: pd.DataFrame,
) -> None:
    """Render equipment risk tab."""
    st.subheader("Equipment Risk Command View")

    filtered_equipment = build_equipment_risk_filters(equipment_risk_model)

    st.caption(
        f"Showing {len(filtered_equipment):,} equipment records after filters."
    )

    table_columns = [
        "equipment_description_raw",
        "account_name_raw",
        "equipment_type",
        "callbacks",
        "mantraps",
        "mantrap_rate_pct",
        "callbacks_last_365_days",
        "mantraps_last_365_days",
        "equipment_risk_score_v3",
        "risk_tier",
        "risk_signal_type",
        "primary_risk_driver",
        "risk_explanation",
    ]

    st.dataframe(
        format_table_for_display(filtered_equipment[table_columns].head(200)),
        use_container_width=True,
        hide_index=True,
    )

    if filtered_equipment.empty:
        st.warning("No equipment matches the selected filters.")
        return

    st.markdown("### Equipment Detail Drilldown")

    selected_equipment = st.selectbox(
        "Select equipment",
        options=filtered_equipment["equipment_description_raw"].head(300).tolist(),
    )

    selected_row = filtered_equipment[
        filtered_equipment["equipment_description_raw"].eq(selected_equipment)
    ].iloc[0]

    detail_1, detail_2, detail_3, detail_4 = st.columns(4)

    with detail_1:
        render_command_card(
            "Callbacks",
            f"{int(selected_row['callbacks']):,}",
            "Total completed/verified callbacks.",
        )

    with detail_2:
        render_command_card(
            "Mantraps",
            f"{int(selected_row['mantraps']):,}",
            "Total mantrap events.",
        )

    with detail_3:
        render_command_card(
            "Risk Score",
            f"{float(selected_row['equipment_risk_score_v3']):.2f}",
            str(selected_row["risk_tier"]),
        )

    with detail_4:
        render_command_card(
            "Primary Driver",
            str(selected_row["primary_risk_driver"]),
            "Strongest component in the risk score.",
        )

    st.info(str(selected_row["risk_explanation"]))

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.plotly_chart(
            build_equipment_monthly_chart(
                monthly_equipment_trend=monthly_equipment_trend,
                selected_equipment=selected_equipment,
            ),
            use_container_width=True,
            key="equipment_monthly_chart",
        )

    with chart_right:
        st.plotly_chart(
            build_equipment_fault_mix_chart(
                equipment_fault_family_mix=equipment_fault_family_mix,
                selected_equipment=selected_equipment,
            ),
            use_container_width=True,
            key="equipment_fault_mix_chart",
        )

    st.markdown("### Equipment Fault Family Detail")

    detail_rows = equipment_fault_family_mix[
        equipment_fault_family_mix["equipment_description_raw"].eq(selected_equipment)
    ]

    detail_columns = [
        "fault_family_final",
        "callbacks",
        "mantraps",
        "mantrap_rate_pct",
        "median_response_minutes",
        "median_repair_minutes",
    ]

    st.dataframe(
        format_table_for_display(detail_rows[detail_columns]),
        use_container_width=True,
        hide_index=True,
    )