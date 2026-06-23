from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards import render_command_card
from components.charts import (
    build_equipment_fault_mix_chart,
    build_equipment_monthly_chart,
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
    with st.container(border=True):
        st.caption("Equipment risk filters")

        filter_col_1, filter_col_2, filter_col_3, filter_col_4 = st.columns(
            [1.1, 1.1, 1, 1]
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
        filtered = filtered[
            filtered["equipment_type"].isin(selected_equipment_types)
        ]

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

    card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(4)

    with card_col_1:
        render_command_card(
            title="Equipment Analyzed",
            value=f"{total_equipment:,}",
            caption="Unique equipment in the selected period.",
        )

    with card_col_2:
        render_command_card(
            title="Critical Risk",
            value=f"{critical_equipment:,}",
            caption="Equipment classified as critical risk.",
        )

    with card_col_3:
        render_command_card(
            title="High Risk",
            value=f"{high_equipment:,}",
            caption="Equipment classified as high risk.",
        )

    with card_col_4:
        render_command_card(
            title="Emerging Signals",
            value=f"{emerging_equipment:,}",
            caption="Low-history equipment with early warning signals.",
        )


def render_selected_equipment_profile(selected_row: pd.Series) -> None:
    """Render selected equipment profile cards."""
    st.markdown(
        f"""
        <div class="insight-panel">
            <div class="insight-panel-title">Selected equipment profile</div>
            <div class="insight-grid">
                <div>
                    <span>Equipment</span>
                    <strong>{selected_row.get("equipment_description_raw", "-")}</strong>
                    <p>Original equipment description used for risk grouping.</p>
                </div>
                <div>
                    <span>Account</span>
                    <strong>{selected_row.get("account_name_raw", "-")}</strong>
                    <p>Customer account linked to this equipment.</p>
                </div>
                <div>
                    <span>Risk tier</span>
                    <strong>{selected_row.get("risk_tier", "-")}</strong>
                    <p>Current risk classification for the selected period.</p>
                </div>
                <div>
                    <span>Primary driver</span>
                    <strong>{selected_row.get("primary_risk_driver", "-")}</strong>
                    <p>Main factor contributing to the equipment risk score.</p>
                </div>
                <div>
                    <span>Callbacks</span>
                    <strong>{int(selected_row.get("callbacks", 0)):,}</strong>
                    <p>Total callback volume for this equipment.</p>
                </div>
                <div>
                    <span>Mantraps</span>
                    <strong>{int(selected_row.get("mantraps", 0)):,}</strong>
                    <p>Mantrap-related callback events.</p>
                </div>
                <div>
                    <span>Risk score</span>
                    <strong>{float(selected_row.get("equipment_risk_score_v3", 0)):,.2f}</strong>
                    <p>Composite equipment risk score.</p>
                </div>
                <div>
                    <span>Signal type</span>
                    <strong>{selected_row.get("risk_signal_type", "-")}</strong>
                    <p>Established, watchlist, or emerging risk signal.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
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
        column for column in display_columns
        if column in filtered_equipment.columns
    ]

    st.dataframe(
        filtered_equipment[available_columns],
        use_container_width=True,
        hide_index=True,
    )


def render_equipment_risk(
    equipment_risk_model: pd.DataFrame,
    monthly_equipment_trend: pd.DataFrame,
    equipment_fault_family_mix: pd.DataFrame,
) -> None:
    """Render equipment risk dashboard page."""
    render_section_header(
        title="Equipment Risk",
        subtitle="Identify high-risk equipment, inspect the main risk drivers, and drill into trend and fault-mix behavior.",
    )

    render_equipment_overview_cards(equipment_risk_model)

    filtered_equipment = filter_equipment_risk_model(equipment_risk_model)

    if filtered_equipment.empty:
        st.warning("No equipment matches the selected filters.")
        return

    filtered_equipment = filtered_equipment.sort_values(
        "equipment_risk_score_v3",
        ascending=False,
    )

    render_section_header(
        title="Filtered equipment ranking",
        subtitle="Equipment ranked by composite risk score after applying the current filters.",
    )

    render_equipment_risk_table(filtered_equipment.head(100))

    selected_equipment = st.selectbox(
        "Select equipment for drilldown",
        options=filtered_equipment["equipment_description_raw"].tolist(),
        index=0,
        key="selected_equipment_drilldown",
    )

    selected_row = filtered_equipment[
        filtered_equipment["equipment_description_raw"].eq(selected_equipment)
    ].iloc[0]

    render_selected_equipment_profile(selected_row)

    chart_col_1, chart_col_2 = st.columns(2)

    with chart_col_1:
        st.plotly_chart(
            build_equipment_monthly_chart(
                monthly_equipment_trend=monthly_equipment_trend,
                selected_equipment=selected_equipment,
            ),
            use_container_width=True,
        )

    with chart_col_2:
        st.plotly_chart(
            build_equipment_fault_mix_chart(
                equipment_fault_family_mix=equipment_fault_family_mix,
                selected_equipment=selected_equipment,
            ),
            use_container_width=True,
        )