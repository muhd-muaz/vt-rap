from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards import render_command_card
from components.charts import (
    build_equipment_type_trend_chart,
    build_fault_code_mantrap_chart,
    build_fault_code_trend_chart,
    build_fault_code_volume_chart,
    build_fault_family_chart,
    build_fault_family_trend_chart,
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


def get_top_fault_family(fault_family_summary: pd.DataFrame) -> str:
    """Return top fault family by callback volume."""
    if fault_family_summary.empty:
        return "-"

    return str(fault_family_summary.iloc[0]["fault_family_final"])


def get_top_fault_code(fault_code_summary: pd.DataFrame) -> str:
    """Return top actual fault code by callback volume."""
    if fault_code_summary.empty:
        return "-"

    top_row = fault_code_summary.iloc[0]

    return f"{top_row['fault_code_display']} — {top_row['fault_code_name']}"


def render_fault_overview_cards(
    fault_family_summary: pd.DataFrame,
    fault_code_summary: pd.DataFrame,
) -> None:
    """Render fault analysis overview metric cards."""
    total_fault_families = len(fault_family_summary)
    total_fault_codes = len(fault_code_summary)

    top_family = get_top_fault_family(fault_family_summary)
    top_code = get_top_fault_code(fault_code_summary)

    total_mantraps = int(fault_code_summary["mantraps"].sum())

    high_mantrap_codes = int(
        fault_code_summary[
            (fault_code_summary["callbacks"] >= 10)
            & (fault_code_summary["mantrap_rate_pct"] >= 20)
        ].shape[0]
    )

    card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(4)

    with card_col_1:
        render_command_card(
            title="Fault Families",
            value=f"{total_fault_families:,}",
            caption="Grouped management-level fault categories.",
        )

    with card_col_2:
        render_command_card(
            title="Actual Fault Codes",
            value=f"{total_fault_codes:,}",
            caption="Original CRM fault codes retained for investigation.",
        )

    with card_col_3:
        render_command_card(
            title="Fault-Code Mantraps",
            value=f"{total_mantraps:,}",
            caption="Mantrap events across actual fault codes.",
        )

    with card_col_4:
        render_command_card(
            title="High-Mantrap Codes",
            value=f"{high_mantrap_codes:,}",
            caption="Codes with at least 10 callbacks and ≥20% mantrap rate.",
        )

    st.markdown(
        f"""
        <div class="insight-panel">
            <div class="insight-panel-title">Fault interpretation</div>
            <div class="insight-grid">
                <div>
                    <span>Top fault family</span>
                    <strong>{top_family}</strong>
                    <p>Highest-volume grouped fault category in the selected period.</p>
                </div>
                <div>
                    <span>Top actual fault code</span>
                    <strong>{top_code}</strong>
                    <p>Most frequent original CRM fault code. Use this for operational investigation.</p>
                </div>
                <div>
                    <span>Recommended view</span>
                    <strong>Use both levels</strong>
                    <p>Family view explains the pattern. Actual code view preserves the precise source record.</p>
                </div>
                <div>
                    <span>Data rule</span>
                    <strong>No code replacement</strong>
                    <p>Fault families are added as grouping, not used to overwrite actual fault codes.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_fault_family_tab(
    fault_family_summary: pd.DataFrame,
    monthly_fault_family_trend: pd.DataFrame,
) -> None:
    """Render fault family analysis tab."""
    render_section_header(
        title="Fault Family Analysis",
        subtitle="Management-level grouping for understanding broad fault patterns.",
    )

    chart_col, table_col = st.columns([1.25, 1])

    with chart_col:
        st.plotly_chart(
            build_fault_family_chart(fault_family_summary),
            width="stretch",
            key="fault_analysis_family_volume_chart",
        )

    with table_col:
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
            width="stretch",
            hide_index=True,
        )

    default_families = (
        fault_family_summary.sort_values("callbacks", ascending=False)
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
    width="stretch",
    key="fault_analysis_family_trend_chart",
)


def render_actual_fault_code_tab(fault_code_summary: pd.DataFrame) -> None:
    """Render actual fault-code analysis tab."""
    render_section_header(
        title="Actual Fault Code Analysis",
        subtitle="Original CRM fault codes with readable names, family grouping, and operational metrics.",
    )

    chart_col_1, chart_col_2 = st.columns(2)

    with chart_col_1:
        st.plotly_chart(
            build_fault_code_volume_chart(fault_code_summary),
            width="stretch",
            key="fault_analysis_code_volume_chart",
        )

    with chart_col_2:
        st.plotly_chart(
            build_fault_code_mantrap_chart(fault_code_summary),
            width="stretch",
            key="fault_analysis_code_mantrap_chart",
        )

    st.markdown("#### Actual Fault Code Detail")

    display_columns = [
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

    available_columns = [
        column for column in display_columns
        if column in fault_code_summary.columns
    ]

    st.dataframe(
        fault_code_summary[available_columns],
        width="stretch",
        hide_index=True,
    )


def render_fault_code_trend_tab(
    fault_code_summary: pd.DataFrame,
    monthly_fault_code_trend: pd.DataFrame,
) -> None:
    """Render actual fault-code trend tab."""
    render_section_header(
        title="Fault Code Trend",
        subtitle="Track selected actual CRM fault codes across the selected analysis period.",
    )

    top_fault_codes = (
        fault_code_summary.sort_values("callbacks", ascending=False)
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
        width="stretch",
        key="fault_analysis_code_trend_chart",
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
        width="stretch",
        hide_index=True,
    )


def render_equipment_type_trend_tab(
    monthly_equipment_type_trend: pd.DataFrame,
) -> None:
    """Render equipment type trend tab."""
    render_section_header(
        title="Equipment Type Trend",
        subtitle="Shows how callback volume changes across elevator, escalator, and other equipment types.",
    )

    st.plotly_chart(
        build_equipment_type_trend_chart(monthly_equipment_type_trend),
        width="stretch",
        key="fault_analysis_equipment_type_trend_chart",
    )

    st.dataframe(
        monthly_equipment_type_trend.sort_values(
            ["event_month", "callbacks"],
            ascending=[False, False],
        ),
        width="stretch",
        hide_index=True,
    )


def render_fault_analysis(
    fault_family_summary: pd.DataFrame,
    fault_code_summary: pd.DataFrame,
    monthly_fault_family_trend: pd.DataFrame,
    monthly_fault_code_trend: pd.DataFrame,
    monthly_equipment_type_trend: pd.DataFrame,
) -> None:
    """Render fault family and actual fault-code analysis."""
    render_section_header(
        title="Fault Analysis",
        subtitle="Analyze both high-level fault families and the original recorded CRM fault codes.",
    )

    render_fault_overview_cards(
        fault_family_summary=fault_family_summary,
        fault_code_summary=fault_code_summary,
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
        render_fault_family_tab(
            fault_family_summary=fault_family_summary,
            monthly_fault_family_trend=monthly_fault_family_trend,
        )

    with code_tab:
        render_actual_fault_code_tab(fault_code_summary=fault_code_summary)

    with trend_tab:
        render_fault_code_trend_tab(
            fault_code_summary=fault_code_summary,
            monthly_fault_code_trend=monthly_fault_code_trend,
        )

    with equipment_tab:
        render_equipment_type_trend_tab(
            monthly_equipment_type_trend=monthly_equipment_type_trend,
        )
