from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards_v2 import (
    render_chart_card,
    render_detail_panel,
    render_empty_state,
    render_filter_panel_heading,
    render_metric_card,
)
from components.charts import (
    build_equipment_fault_mix_chart,
    build_equipment_monthly_chart,
)
from components.layout_v2 import render_section_header
from components.downloads import render_csv_download_button


def get_available_risk_tiers(equipment_risk_model: pd.DataFrame) -> list[str]:
    """Return available equipment risk tiers."""
    if "risk_tier" not in equipment_risk_model.columns:
        return []

    return (
        equipment_risk_model["risk_tier"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )


def get_available_equipment_types(equipment_risk_model: pd.DataFrame) -> list[str]:
    """Return available equipment types."""
    if "equipment_type" not in equipment_risk_model.columns:
        return []

    return (
        equipment_risk_model["equipment_type"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )


def filter_equipment_risk_model(equipment_risk_model: pd.DataFrame) -> pd.DataFrame:
    """Render filters and return filtered equipment risk model."""
    render_filter_panel_heading(
        title="Equipment risk filters",
        subtitle="Narrow the ranked equipment set without changing the global period filter.",
    )

    with st.container(border=True):
        filter_col_1, filter_col_2, filter_col_3, filter_col_4 = st.columns(
            [1.15, 1.15, 1, 1],
            gap="medium",
        )

        with filter_col_1:
            selected_risk_tiers = st.multiselect(
                "Risk tier",
                options=get_available_risk_tiers(equipment_risk_model),
                default=get_available_risk_tiers(equipment_risk_model),
                key="equipment_risk_tier_filter",
            )

        with filter_col_2:
            selected_equipment_types = st.multiselect(
                "Equipment type",
                options=get_available_equipment_types(equipment_risk_model),
                default=get_available_equipment_types(equipment_risk_model),
                key="equipment_type_filter",
            )

        with filter_col_3:
            minimum_callbacks = st.number_input(
                "Minimum callbacks",
                min_value=0,
                value=0,
                step=1,
                key="equipment_minimum_callbacks_filter",
            )

        with filter_col_4:
            minimum_mantraps = st.number_input(
                "Minimum mantraps",
                min_value=0,
                value=0,
                step=1,
                key="equipment_minimum_mantraps_filter",
            )

        search_text = st.text_input(
            "Search equipment or account",
            placeholder="Type equipment description or account name...",
            key="equipment_search_filter",
        )

    filtered = equipment_risk_model.copy()

    if selected_risk_tiers:
        filtered = filtered[filtered["risk_tier"].isin(selected_risk_tiers)]

    if selected_equipment_types:
        filtered = filtered[filtered["equipment_type"].isin(selected_equipment_types)]

    filtered = filtered[
        filtered["callbacks"].ge(minimum_callbacks)
        & filtered["mantraps"].ge(minimum_mantraps)
    ]

    if search_text.strip():
        search_value = search_text.strip().lower()

        filtered = filtered[
            filtered["equipment_description_raw"]
            .astype(str)
            .str.lower()
            .str.contains(search_value, na=False)
            | filtered["account_name_raw"]
            .astype(str)
            .str.lower()
            .str.contains(search_value, na=False)
        ]

    return filtered


def render_equipment_overview_cards(equipment_risk_model: pd.DataFrame) -> None:
    """Render equipment risk overview cards."""
    total_equipment = len(equipment_risk_model)

    critical_equipment = int(
        equipment_risk_model["risk_tier"].eq("Critical").sum()
        if "risk_tier" in equipment_risk_model.columns
        else 0
    )

    high_equipment = int(
        equipment_risk_model["risk_tier"].eq("High").sum()
        if "risk_tier" in equipment_risk_model.columns
        else 0
    )

    emerging_equipment = int(
        equipment_risk_model["risk_signal_type"].eq("emerging").sum()
        if "risk_signal_type" in equipment_risk_model.columns
        else 0
    )

    card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(4, gap="medium")

    with card_col_1:
        render_metric_card(
            title="Equipment analyzed",
            value=f"{total_equipment:,}",
            caption="Unique equipment in the selected period.",
            accent="default",
        )

    with card_col_2:
        render_metric_card(
            title="Critical risk",
            value=f"{critical_equipment:,}",
            caption="Equipment classified as critical risk.",
            accent="danger",
        )

    with card_col_3:
        render_metric_card(
            title="High risk",
            value=f"{high_equipment:,}",
            caption="Equipment classified as high risk.",
            accent="warning",
        )

    with card_col_4:
        render_metric_card(
            title="Emerging signals",
            value=f"{emerging_equipment:,}",
            caption="Low-history equipment with early warning signals.",
            accent="blue",
        )


def format_profile_text(value, fallback: str = "-") -> str:
    """Format source text for V2 display helpers."""
    if value is None or pd.isna(value):
        return fallback

    value_text = str(value).strip()
    if not value_text:
        return fallback

    return value_text


def format_profile_int(value) -> str:
    """Format profile integer values."""
    try:
        if value is None or pd.isna(value):
            return "0"
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def format_profile_float(value) -> str:
    """Format profile decimal values."""
    try:
        if value is None or pd.isna(value):
            return "0.00"
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "0.00"


def render_selected_equipment_profile(selected_row: pd.Series) -> None:
    """Render selected equipment profile cards."""
    render_detail_panel(
        eyebrow="Selected equipment",
        title="Risk profile and service context",
        score_label="Risk score",
        score_value=format_profile_float(
            selected_row.get("equipment_risk_score_v3", 0)
        ),
        items=[
            (
                "Equipment",
                format_profile_text(selected_row.get("equipment_description_raw", "-")),
                "Original equipment description used for risk grouping.",
            ),
            (
                "Account",
                format_profile_text(selected_row.get("account_name_raw", "-")),
                "Customer account linked to this equipment.",
            ),
            (
                "Risk tier",
                format_profile_text(selected_row.get("risk_tier", "-")),
                "Current risk classification for the selected period.",
            ),
            (
                "Primary driver",
                format_profile_text(selected_row.get("primary_risk_driver", "-")),
                "Main factor contributing to the equipment risk score.",
            ),
            (
                "Callbacks",
                format_profile_int(selected_row.get("callbacks", 0)),
                "Total callback volume for this equipment.",
            ),
            (
                "Mantraps",
                format_profile_int(selected_row.get("mantraps", 0)),
                "Mantrap-related callback events.",
            ),
            (
                "Signal type",
                format_profile_text(selected_row.get("risk_signal_type", "-")),
                "Established, watchlist, or emerging risk signal.",
            ),
        ],
    )


def render_equipment_risk_table(filtered_equipment: pd.DataFrame) -> None:
    """Render filtered equipment risk table."""
    display_columns = [
        "equipment_description_raw",
        "account_name_raw",
        "equipment_type",
        "callbacks",
        "mantraps",
        "mantrap_rate_pct",
        "median_response_minutes",
        "median_repair_minutes",
        "equipment_risk_score_v3",
        "risk_tier",
        "risk_signal_type",
        "primary_risk_driver",
        "risk_explanation",
    ]

    available_columns = [
        column for column in display_columns if column in filtered_equipment.columns
    ]

    export_data = filtered_equipment[available_columns].copy()

    st.dataframe(
        export_data,
        width="stretch",
        hide_index=True,
    )

    render_csv_download_button(
        dataframe=export_data,
        filename_prefix="filtered_equipment_risk",
        label="Download filtered equipment risk CSV",
        key="download_filtered_equipment_risk",
    )


def render_equipment_risk(
    equipment_risk_model: pd.DataFrame,
    monthly_equipment_trend: pd.DataFrame,
    equipment_fault_family_mix: pd.DataFrame,
) -> None:
    """Render equipment risk dashboard page."""
    render_section_header(
        title="Equipment risk",
        subtitle="Identify high-risk equipment, inspect the main risk drivers, and drill into trend and fault-mix behavior.",
    )

    if equipment_risk_model.empty:
        render_empty_state(
            title="No equipment risk records",
            message="The selected global period has no equipment records to analyze.",
        )
        return

    render_equipment_overview_cards(equipment_risk_model)

    filtered_equipment = filter_equipment_risk_model(equipment_risk_model)

    if filtered_equipment.empty:
        st.warning("No equipment matches the selected filters.")
        return

    filtered_equipment = filtered_equipment.sort_values(
        "equipment_risk_score_v3",
        ascending=False,
    ).copy()

    render_section_header(
        title="Filtered equipment ranking",
        subtitle="Equipment ranked by composite risk score after applying the current filters.",
    )

    render_equipment_risk_table(filtered_equipment.head(100))

    drilldown_equipment = filtered_equipment.reset_index(drop=True)

    def format_equipment_option(row_position: int) -> str:
        row = drilldown_equipment.iloc[row_position]
        equipment_name = str(row.get("equipment_description_raw", "-"))
        account_name = str(row.get("account_name_raw", "-"))
        risk_tier = str(row.get("risk_tier", "-"))
        return f"{account_name} | {equipment_name} | {risk_tier}"

    selected_position = st.selectbox(
        "Select equipment for drilldown",
        options=list(range(len(drilldown_equipment))),
        format_func=format_equipment_option,
        index=0,
        key="selected_equipment_drilldown_v2",
    )

    selected_row = drilldown_equipment.iloc[selected_position]
    selected_equipment = str(selected_row.get("equipment_description_raw", ""))
    selected_account_name = str(selected_row.get("account_name_raw", ""))

    render_selected_equipment_profile(selected_row)

    render_section_header(
        title="Equipment drilldown",
        subtitle="Trend and fault-family mix for the selected equipment description.",
    )

    chart_col_1, chart_col_2 = st.columns(2, gap="large")

    with chart_col_1:
        render_chart_card(
            title="Monthly equipment trend",
            subtitle="Callbacks and mantraps for the selected equipment description.",
            chart_key="equipment_risk_monthly_chart",
            figure=build_equipment_monthly_chart(
                monthly_equipment_trend=monthly_equipment_trend,
                selected_equipment=selected_equipment,
                selected_account_name=selected_account_name,
            ),
        )

    with chart_col_2:
        render_chart_card(
            title="Fault family mix",
            subtitle="Fault-family callback volume for the selected equipment description.",
            chart_key="equipment_risk_fault_mix_chart",
            figure=build_equipment_fault_mix_chart(
                equipment_fault_family_mix=equipment_fault_family_mix,
                selected_equipment=selected_equipment,
                selected_account_name=selected_account_name,
            ),
        )
