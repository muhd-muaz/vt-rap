from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards_v2 import (
    render_detail_panel,
    render_empty_state,
    render_filter_panel_heading,
    render_metric_card,
)
from components.layout_v2 import render_section_header
from components.downloads import render_csv_download_button


def render_emerging_overview_cards(
    emerging_equipment_alerts: pd.DataFrame,
) -> None:
    """Render emerging alert overview cards."""
    total_alerts = len(emerging_equipment_alerts)

    total_callbacks = int(
        emerging_equipment_alerts["callbacks"].sum()
        if "callbacks" in emerging_equipment_alerts.columns
        else 0
    )

    total_mantraps = int(
        emerging_equipment_alerts["mantraps"].sum()
        if "mantraps" in emerging_equipment_alerts.columns
        else 0
    )

    high_recent_activity = int(
        emerging_equipment_alerts[
            emerging_equipment_alerts.get("callbacks_last_90_days", 0) >= 2
        ].shape[0]
        if "callbacks_last_90_days" in emerging_equipment_alerts.columns
        else 0
    )

    card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(4, gap="medium")

    with card_col_1:
        render_metric_card(
            title="Emerging alerts",
            value=f"{total_alerts:,}",
            caption="Low-history equipment with early warning signals.",
            accent="default",
        )

    with card_col_2:
        render_metric_card(
            title="Alert callbacks",
            value=f"{total_callbacks:,}",
            caption="Callback volume from emerging-alert equipment.",
            accent="blue",
        )

    with card_col_3:
        render_metric_card(
            title="Alert mantraps",
            value=f"{total_mantraps:,}",
            caption="Mantrap events from emerging-alert equipment.",
            accent="danger",
        )

    with card_col_4:
        render_metric_card(
            title="Recent activity",
            value=f"{high_recent_activity:,}",
            caption="Alert equipment with at least two recent 90-day callbacks.",
            accent="warning",
        )


def filter_emerging_alerts(
    emerging_equipment_alerts: pd.DataFrame,
) -> pd.DataFrame:
    """Render emerging-alert filters and return filtered records."""
    render_filter_panel_heading(
        title="Emerging alert filters",
        subtitle="Prioritize early warning records without changing the global period filter.",
    )

    with st.container(border=True):
        filter_col_1, filter_col_2, filter_col_3 = st.columns(3, gap="medium")

        with filter_col_1:
            minimum_callbacks = st.number_input(
                "Minimum callbacks",
                min_value=0,
                value=0,
                step=1,
                key="emerging_minimum_callbacks_filter",
            )

        with filter_col_2:
            minimum_mantraps = st.number_input(
                "Minimum mantraps",
                min_value=0,
                value=0,
                step=1,
                key="emerging_minimum_mantraps_filter",
            )

        with filter_col_3:
            minimum_callbacks_last_90_days = st.number_input(
                "Minimum recent 90-day callbacks",
                min_value=0,
                value=0,
                step=1,
                key="emerging_minimum_callbacks_last_90_days_filter",
            )

        search_text = st.text_input(
            "Search equipment or account",
            placeholder="Type equipment description or account name...",
            key="emerging_search_filter",
        )

    filtered = emerging_equipment_alerts.copy()

    if "callbacks" in filtered.columns:
        filtered = filtered[filtered["callbacks"].ge(minimum_callbacks)]

    if "mantraps" in filtered.columns:
        filtered = filtered[filtered["mantraps"].ge(minimum_mantraps)]

    if "callbacks_last_90_days" in filtered.columns:
        filtered = filtered[
            filtered["callbacks_last_90_days"].ge(minimum_callbacks_last_90_days)
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


def render_emerging_interpretation(
    filtered_alerts: pd.DataFrame,
) -> None:
    """Render interpretation for emerging alerts."""
    if filtered_alerts.empty:
        st.info("No emerging alerts match the selected filters.")
        return

    top_alert = filtered_alerts.sort_values(
        "equipment_risk_score_v3",
        ascending=False,
    ).iloc[0]

    top_equipment = format_text(top_alert.get("equipment_description_raw", "-"))
    top_account = format_text(top_alert.get("account_name_raw", "-"))
    top_driver = format_text(top_alert.get("primary_risk_driver", "-"))
    top_score = float(top_alert.get("equipment_risk_score_v3", 0))

    alert_with_mantraps = int(
        filtered_alerts[filtered_alerts["mantraps"].gt(0)].shape[0]
        if "mantraps" in filtered_alerts.columns
        else 0
    )

    render_detail_panel(
        eyebrow="Emerging interpretation",
        title="Early warning focus for the filtered set",
        score_label="Top score",
        score_value=f"{top_score:,.2f}",
        items=[
            (
                "Top equipment",
                top_equipment,
                "Equipment with the strongest emerging warning signal.",
            ),
            (
                "Linked account",
                top_account,
                "Customer account associated with the top emerging alert.",
            ),
            (
                "Main driver",
                top_driver,
                "Main factor behind the top emerging alert.",
            ),
            (
                "Alerts with mantraps",
                f"{alert_with_mantraps:,}",
                "Emerging equipment where at least one mantrap event was recorded.",
            ),
        ],
    )


def render_filtered_alert_summary(filtered_alerts: pd.DataFrame) -> None:
    """Render compact priority readout for the filtered emerging-alert set."""
    alert_count = len(filtered_alerts)
    alert_with_mantraps = int(
        filtered_alerts[filtered_alerts["mantraps"].gt(0)].shape[0]
        if "mantraps" in filtered_alerts.columns
        else 0
    )
    recent_callbacks = int(
        filtered_alerts["callbacks_last_90_days"].sum()
        if "callbacks_last_90_days" in filtered_alerts.columns
        else 0
    )
    top_score = (
        filtered_alerts["equipment_risk_score_v3"].max()
        if "equipment_risk_score_v3" in filtered_alerts.columns
        else 0
    )

    summary_col_1, summary_col_2, summary_col_3, summary_col_4 = st.columns(
        4,
        gap="medium",
    )

    with summary_col_1:
        render_metric_card(
            title="Filtered alerts",
            value=f"{alert_count:,}",
            caption="Emerging records after page-level filters.",
            accent="default",
        )

    with summary_col_2:
        render_metric_card(
            title="With mantraps",
            value=f"{alert_with_mantraps:,}",
            caption="Filtered alerts with at least one mantrap.",
            accent="danger",
        )

    with summary_col_3:
        render_metric_card(
            title="Recent callbacks",
            value=f"{recent_callbacks:,}",
            caption="90-day callback volume in the filtered set.",
            accent="blue",
        )

    with summary_col_4:
        render_metric_card(
            title="Highest score",
            value=format_float(top_score),
            caption="Maximum equipment risk score in the filtered set.",
            accent="warning",
        )


def format_float(value) -> str:
    """Format decimal display values."""
    try:
        if value is None or pd.isna(value):
            return "0.00"
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "0.00"


def format_text(value, fallback: str = "-") -> str:
    """Format source text for V2 display helpers."""
    if value is None or pd.isna(value):
        return fallback

    value_text = str(value).strip()
    return value_text if value_text else fallback


def render_emerging_alert_table(filtered_alerts: pd.DataFrame) -> None:
    """Render filtered emerging alert table."""
    display_columns = [
        "equipment_description_raw",
        "account_name_raw",
        "equipment_type",
        "callbacks",
        "mantraps",
        "mantrap_rate_pct",
        "callbacks_last_90_days",
        "mantraps_last_90_days",
        "callbacks_last_180_days",
        "callbacks_last_365_days",
        "equipment_risk_score_v3",
        "risk_tier",
        "risk_signal_type",
        "primary_risk_driver",
        "risk_explanation",
    ]

    available_columns = [
        column for column in display_columns if column in filtered_alerts.columns
    ]

    export_data = filtered_alerts[available_columns].copy()

    st.dataframe(
        export_data,
        width="stretch",
        hide_index=True,
    )

    render_csv_download_button(
        dataframe=export_data,
        filename_prefix="filtered_emerging_alerts",
        label="Download filtered emerging alerts CSV",
        key="download_filtered_emerging_alerts",
    )


def render_emerging_alerts(
    emerging_equipment_alerts: pd.DataFrame,
) -> None:
    """Render emerging equipment alert dashboard page."""
    render_section_header(
        title="Emerging alerts",
        subtitle="Detect low-history equipment that already shows early warning signals from recent callbacks, mantraps, or risk-score behavior.",
    )

    if emerging_equipment_alerts.empty:
        render_empty_state(
            title="No emerging equipment alerts",
            message="The selected global period has no low-history equipment alerts.",
        )
        return

    render_emerging_overview_cards(emerging_equipment_alerts)

    filtered_alerts = filter_emerging_alerts(emerging_equipment_alerts)

    if filtered_alerts.empty:
        st.warning("No emerging alerts match the selected filters.")
        return

    filtered_alerts = filtered_alerts.sort_values(
        "equipment_risk_score_v3",
        ascending=False,
    )

    render_section_header(
        title="Filtered alert priority",
        subtitle="Fast readout of the alert set after local filters are applied.",
    )

    render_filtered_alert_summary(filtered_alerts)
    render_emerging_interpretation(filtered_alerts)

    render_section_header(
        title="Emerging alert ranking",
        subtitle="Filtered emerging-alert equipment ranked by composite equipment risk score.",
    )

    render_emerging_alert_table(filtered_alerts)
