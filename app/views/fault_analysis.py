from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards_v2 import (
    render_chart_card,
    render_detail_panel,
    render_filter_panel_heading,
    render_metric_card,
)
from components.charts import (
    build_equipment_type_trend_chart,
    build_fault_code_mantrap_chart,
    build_fault_code_trend_chart,
    build_fault_code_volume_chart,
    build_fault_family_chart,
    build_fault_family_trend_chart,
)
from components.layout_v2 import render_section_header
from components.downloads import render_csv_download_button


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

    return f"{top_row['fault_code_display']} - {top_row['fault_code_name']}"


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

    card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(4, gap="medium")

    with card_col_1:
        render_metric_card(
            title="Fault families",
            value=f"{total_fault_families:,}",
            caption="Grouped management-level fault categories.",
            accent="default",
        )

    with card_col_2:
        render_metric_card(
            title="Actual fault codes",
            value=f"{total_fault_codes:,}",
            caption="Original CRM fault codes retained for investigation.",
            accent="blue",
        )

    with card_col_3:
        render_metric_card(
            title="Fault-code mantraps",
            value=f"{total_mantraps:,}",
            caption="Mantrap events across actual fault codes.",
            accent="danger",
        )

    with card_col_4:
        render_metric_card(
            title="High-mantrap codes",
            value=f"{high_mantrap_codes:,}",
            caption="Codes with at least 10 callbacks and 20% or higher mantrap rate.",
            accent="warning",
        )

    render_detail_panel(
        eyebrow="Fault interpretation",
        title="Source-code fidelity and grouped analysis",
        items=[
            (
                "Top fault family",
                top_family,
                "Highest-volume grouped fault category in the selected period.",
            ),
            (
                "Top actual fault code",
                top_code,
                "Most frequent original CRM fault code for operational investigation.",
            ),
            (
                "Recommended view",
                "Use both levels",
                "Family view explains the pattern. Actual code view preserves the precise source record.",
            ),
            (
                "Data rule",
                "No code replacement",
                "Fault families are added as grouping, not used to overwrite actual fault codes.",
            ),
        ],
    )


def render_fault_family_tab(
    fault_family_summary: pd.DataFrame,
    monthly_fault_family_trend: pd.DataFrame,
) -> None:
    """Render fault family analysis tab."""
    render_section_header(
        title="Fault family analysis",
        subtitle="Management-level grouping for understanding broad fault patterns.",
    )

    chart_col, table_col = st.columns([1.25, 1], gap="large")

    with chart_col:
        render_chart_card(
            title="Fault family volume",
            subtitle="Grouped fault categories by callback volume.",
            chart_key="fault_analysis_family_volume_chart",
            figure=build_fault_family_chart(fault_family_summary),
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

    render_filter_panel_heading(
        title="Fault family trend filters",
        subtitle="Select grouped fault families to compare across the current period.",
    )

    with st.container(border=True):
        selected_fault_families = st.multiselect(
            "Select fault families for monthly trend",
            options=fault_family_summary["fault_family_final"].tolist(),
            default=default_families,
            key="fault_analysis_family_trend_filter",
        )

    render_chart_card(
        title="Monthly fault family trend",
        subtitle="Callback volume trend for selected fault families.",
        chart_key="fault_analysis_family_trend_chart",
        figure=build_fault_family_trend_chart(
            monthly_fault_family_trend=monthly_fault_family_trend,
            selected_fault_families=selected_fault_families,
        ),
    )


def render_actual_fault_code_tab(fault_code_summary: pd.DataFrame) -> None:
    """Render actual fault-code analysis tab."""
    render_section_header(
        title="Actual fault code analysis",
        subtitle="Original CRM fault codes with readable names, family grouping, and operational metrics.",
    )

    chart_col_1, chart_col_2 = st.columns(2, gap="large")

    with chart_col_1:
        render_chart_card(
            title="Actual fault-code volume",
            subtitle="Highest-volume original CRM fault codes.",
            chart_key="fault_analysis_code_volume_chart",
            figure=build_fault_code_volume_chart(fault_code_summary),
        )

    with chart_col_2:
        render_chart_card(
            title="Actual fault-code mantraps",
            subtitle="Original fault codes with the most mantrap events.",
            chart_key="fault_analysis_code_mantrap_chart",
            figure=build_fault_code_mantrap_chart(fault_code_summary),
        )

    render_section_header(
        title="Actual fault-code detail",
        subtitle="Original code detail retained for investigation and CSV export.",
    )

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
        column for column in display_columns if column in fault_code_summary.columns
    ]

    export_data = fault_code_summary[available_columns].copy()

    st.dataframe(
        export_data,
        width="stretch",
        hide_index=True,
    )

    render_csv_download_button(
        dataframe=export_data,
        filename_prefix="actual_fault_code_summary",
        label="Download actual fault code summary CSV",
        key="download_actual_fault_code_summary",
    )


def render_fault_code_trend_tab(
    fault_code_summary: pd.DataFrame,
    monthly_fault_code_trend: pd.DataFrame,
) -> None:
    """Render actual fault-code trend tab."""
    render_section_header(
        title="Fault code trend",
        subtitle="Track selected actual CRM fault codes across the selected analysis period.",
    )

    top_fault_codes = (
        fault_code_summary.sort_values("callbacks", ascending=False)
        .head(8)["fault_code_display"]
        .tolist()
    )

    render_filter_panel_heading(
        title="Fault-code trend filters",
        subtitle="Select original CRM fault codes to track without changing the global period.",
    )

    with st.container(border=True):
        selected_fault_codes = st.multiselect(
            "Select actual fault codes",
            options=fault_code_summary["fault_code_display"].tolist(),
            default=top_fault_codes,
            key="fault_analysis_code_trend_filter",
        )

    render_chart_card(
        title="Monthly actual fault-code trend",
        subtitle="Callback volume trend for selected original fault codes.",
        chart_key="fault_analysis_code_trend_chart",
        figure=build_fault_code_trend_chart(
            monthly_fault_code_trend=monthly_fault_code_trend,
            selected_fault_codes=selected_fault_codes,
        ),
    )

    selected_code_details = fault_code_summary[
        fault_code_summary["fault_code_display"].isin(selected_fault_codes)
    ].copy()

    selected_code_columns = [
        "fault_code_display",
        "fault_code_name",
        "fault_family_final",
        "callbacks",
        "mantraps",
        "mantrap_rate_pct",
        "fault_code_description",
        "fault_code_rectification",
    ]

    available_selected_code_columns = [
        column
        for column in selected_code_columns
        if column in selected_code_details.columns
    ]

    export_data = selected_code_details[available_selected_code_columns].copy()

    st.dataframe(
        export_data,
        width="stretch",
        hide_index=True,
    )

    render_csv_download_button(
        dataframe=export_data,
        filename_prefix="selected_fault_code_trend_details",
        label="Download selected fault code details CSV",
        key="download_selected_fault_code_details",
    )


def render_equipment_type_trend_tab(
    monthly_equipment_type_trend: pd.DataFrame,
) -> None:
    """Render equipment type trend tab."""
    render_section_header(
        title="Equipment type trend",
        subtitle="Shows how callback volume changes across elevator, escalator, and other equipment types.",
    )

    render_chart_card(
        title="Monthly equipment type trend",
        subtitle="Callback volume by equipment type across the selected period.",
        chart_key="fault_analysis_equipment_type_trend_chart",
        figure=build_equipment_type_trend_chart(monthly_equipment_type_trend),
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
        title="Fault analysis",
        subtitle="Analyze both high-level fault families and the original recorded CRM fault codes.",
    )

    render_fault_overview_cards(
        fault_family_summary=fault_family_summary,
        fault_code_summary=fault_code_summary,
    )

    family_tab, code_tab, trend_tab, equipment_tab = st.tabs(
        [
            "Fault family",
            "Actual fault code",
            "Fault code trend",
            "Equipment type trend",
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
