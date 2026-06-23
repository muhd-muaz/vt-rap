from __future__ import annotations

import pandas as pd
import streamlit as st

from components.charts import (
    build_equipment_type_trend_chart,
    build_fault_code_mantrap_chart,
    build_fault_code_trend_chart,
    build_fault_code_volume_chart,
    build_fault_family_chart,
    build_fault_family_trend_chart,
)


def render_fault_analysis(
    fault_family_summary: pd.DataFrame,
    fault_code_summary: pd.DataFrame,
    monthly_fault_family_trend: pd.DataFrame,
    monthly_fault_code_trend: pd.DataFrame,
    monthly_equipment_type_trend: pd.DataFrame,
) -> None:
    """Render fault family and actual fault-code analysis."""
    st.subheader("Fault Analysis")

    st.markdown(
        """
        <div class="command-card">
            <div class="command-card-title">Fault Analysis Structure</div>
            <div class="command-card-caption">
                Fault family gives the management-level view. Actual fault code preserves the original CRM fault code for operational investigation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    family_tab, code_tab, trend_tab, equipment_tab = st.tabs(
        [
            "Fault Family",
            "Actual Fault Code",
            "Fault Code Trend",
            "Equipment Type Trend",
        ]
    )

    with family_tab:
        st.plotly_chart(
            build_fault_family_chart(fault_family_summary),
            use_container_width=True,
        )

        default_families = (
            fault_family_summary
            .sort_values("callbacks", ascending=False)
            .head(6)["fault_family_final"]
            .tolist()
        )

        selected_fault_families = st.multiselect(
            "Select fault families for monthly trend",
            options=fault_family_summary["fault_family_final"].tolist(),
            default=default_families,
        )

        st.plotly_chart(
            build_fault_family_trend_chart(
                monthly_fault_family_trend=monthly_fault_family_trend,
                selected_fault_families=selected_fault_families,
            ),
            use_container_width=True,
        )

        st.dataframe(
            fault_family_summary[
                [
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
            ],
            use_container_width=True,
            hide_index=True,
        )

    with code_tab:
        chart_col_1, chart_col_2 = st.columns(2)

        with chart_col_1:
            st.plotly_chart(
                build_fault_code_volume_chart(fault_code_summary),
                use_container_width=True,
            )

        with chart_col_2:
            st.plotly_chart(
                build_fault_code_mantrap_chart(fault_code_summary),
                use_container_width=True,
            )

        st.markdown("#### Actual Fault Code Detail")

        st.dataframe(
            fault_code_summary[
                [
                    "fault_code_display",
                    "fault_code_name",
                    "fault_family_final",
                    "callbacks",
                    "callback_share_pct",
                    "mantraps",
                    "mantrap_rate_pct",
                    "unique_accounts",
                    "unique_equipment",
                    "median_response_minutes",
                    "median_repair_minutes",
                    "fault_code_description",
                    "fault_code_rectification",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    with trend_tab:
        top_fault_codes = (
            fault_code_summary
            .sort_values("callbacks", ascending=False)
            .head(8)["fault_code_display"]
            .tolist()
        )

        selected_fault_codes = st.multiselect(
            "Select actual fault codes",
            options=fault_code_summary["fault_code_display"].tolist(),
            default=top_fault_codes,
        )

        st.plotly_chart(
            build_fault_code_trend_chart(
                monthly_fault_code_trend=monthly_fault_code_trend,
                selected_fault_codes=selected_fault_codes,
            ),
            use_container_width=True,
        )

        selected_code_details = fault_code_summary[
            fault_code_summary["fault_code_display"].isin(selected_fault_codes)
        ].copy()

        st.dataframe(
            selected_code_details[
                [
                    "fault_code_display",
                    "fault_code_name",
                    "fault_family_final",
                    "callbacks",
                    "mantraps",
                    "mantrap_rate_pct",
                    "fault_code_description",
                    "fault_code_rectification",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    with equipment_tab:
        st.plotly_chart(
            build_equipment_type_trend_chart(monthly_equipment_type_trend),
            use_container_width=True,
        )

        st.dataframe(
            monthly_equipment_type_trend.sort_values(
                ["event_month", "callbacks"],
                ascending=[False, False],
            ),
            use_container_width=True,
            hide_index=True,
        )