from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards import render_command_card
from components.charts import (
    build_account_fault_mix_chart,
    build_account_monthly_chart,
)
from components.tables import format_table_for_display


def render_account_risk(
    account_risk_model: pd.DataFrame,
    monthly_account_trend: pd.DataFrame,
    equipment_risk_model: pd.DataFrame,
    account_fault_family_mix: pd.DataFrame,
) -> None:
    """Render account risk tab."""
    st.subheader("Account Risk Command View")

    table_columns = [
        "account_code",
        "account_name_raw",
        "callbacks",
        "mantraps",
        "unique_equipment",
        "callbacks_per_equipment",
        "mantrap_rate_pct",
        "median_response_minutes",
        "median_repair_minutes",
        "account_risk_score",
        "risk_tier",
        "primary_risk_driver",
        "risk_explanation",
    ]

    st.dataframe(
        format_table_for_display(account_risk_model[table_columns].head(200)),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Account Detail Drilldown")

    selected_account = st.selectbox(
        "Select account",
        options=account_risk_model["account_name_raw"].head(300).tolist(),
    )

    selected_row = account_risk_model[
        account_risk_model["account_name_raw"].eq(selected_account)
    ].iloc[0]

    account_1, account_2, account_3, account_4 = st.columns(4)

    with account_1:
        render_command_card(
            "Callbacks",
            f"{int(selected_row['callbacks']):,}",
            "Total completed/verified callbacks.",
        )

    with account_2:
        render_command_card(
            "Mantraps",
            f"{int(selected_row['mantraps']):,}",
            "Total mantrap events.",
        )

    with account_3:
        render_command_card(
            "Equipment",
            f"{int(selected_row['unique_equipment']):,}",
            "Unique equipment under account.",
        )

    with account_4:
        render_command_card(
            "Risk Score",
            f"{float(selected_row['account_risk_score']):.2f}",
            str(selected_row["risk_tier"]),
        )

    st.info(str(selected_row["risk_explanation"]))

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.plotly_chart(
            build_account_monthly_chart(
                monthly_account_trend=monthly_account_trend,
                selected_account_name=selected_account,
            ),
            use_container_width=True,
            key="account_detail_monthly_chart",
        )

    with chart_right:
        st.plotly_chart(
            build_account_fault_mix_chart(
                account_fault_family_mix=account_fault_family_mix,
                selected_account_name=selected_account,
            ),
            use_container_width=True,
            key="account_fault_mix_chart",
        )

    st.markdown("### Equipment Under Selected Account")

    account_equipment = equipment_risk_model[
        equipment_risk_model["account_name_raw"].eq(selected_account)
    ].copy()

    equipment_columns = [
        "equipment_description_raw",
        "equipment_type",
        "callbacks",
        "mantraps",
        "mantrap_rate_pct",
        "callbacks_last_365_days",
        "mantraps_last_365_days",
        "equipment_risk_score_v3",
        "risk_tier",
        "primary_risk_driver",
        "risk_explanation",
    ]

    st.dataframe(
        format_table_for_display(account_equipment[equipment_columns].head(100)),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Account Fault Family Detail")

    account_fault_rows = account_fault_family_mix[
        account_fault_family_mix["account_name_raw"].eq(selected_account)
    ]

    fault_columns = [
        "fault_family_final",
        "callbacks",
        "mantraps",
        "mantrap_rate_pct",
        "unique_equipment",
        "median_response_minutes",
        "median_repair_minutes",
    ]

    st.dataframe(
        format_table_for_display(account_fault_rows[fault_columns]),
        use_container_width=True,
        hide_index=True,
    )