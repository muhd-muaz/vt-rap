from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards import render_command_card


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
            emerging_equipment_alerts.get("recent_90d_callbacks", 0) >= 2
        ].shape[0]
        if "recent_90d_callbacks" in emerging_equipment_alerts.columns
        else 0
    )

    card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(4)

    with card_col_1:
        render_command_card(
            title="Emerging Alerts",
            value=f"{total_alerts:,}",
            caption="Low-history equipment with early warning signals.",
        )

    with card_col_2:
        render_command_card(
            title="Alert Callbacks",
            value=f"{total_callbacks:,}",
            caption="Callback volume from emerging-alert equipment.",
        )

    with card_col_3:
        render_command_card(
            title="Alert Mantraps",
            value=f"{total_mantraps:,}",
            caption="Mantrap events from emerging-alert equipment.",
        )

    with card_col_4:
        render_command_card(
            title="Recent Activity",
            value=f"{high_recent_activity:,}",
            caption="Alert equipment with at least two recent 90-day callbacks.",
        )


def filter_emerging_alerts(
    emerging_equipment_alerts: pd.DataFrame,
) -> pd.DataFrame:
    """Render emerging-alert filters and return filtered records."""
    with st.container(border=True):
        st.caption("Emerging alert filters")

        filter_col_1, filter_col_2, filter_col_3 = st.columns(3)

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
            minimum_recent_90d_callbacks = st.number_input(
                "Minimum recent 90-day callbacks",
                min_value=0,
                value=0,
                step=1,
                key="emerging_minimum_recent_90d_callbacks_filter",
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

    if "recent_90d_callbacks" in filtered.columns:
        filtered = filtered[
            filtered["recent_90d_callbacks"].ge(minimum_recent_90d_callbacks)
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

    top_equipment = top_alert.get("equipment_description_raw", "-")
    top_account = top_alert.get("account_name_raw", "-")
    top_driver = top_alert.get("primary_risk_driver", "-")
    top_score = float(top_alert.get("equipment_risk_score_v3", 0))

    alert_with_mantraps = int(
        filtered_alerts[filtered_alerts["mantraps"].gt(0)].shape[0]
        if "mantraps" in filtered_alerts.columns
        else 0
    )

    st.markdown(
        f"""
        <div class="insight-panel">
            <div class="insight-panel-title">Emerging alert interpretation</div>
            <div class="insight-grid">
                <div>
                    <span>Highest emerging score</span>
                    <strong>{top_score:,.2f}</strong>
                    <p>Highest composite risk score among filtered emerging alerts.</p>
                </div>
                <div>
                    <span>Top equipment</span>
                    <strong>{top_equipment}</strong>
                    <p>Equipment with the strongest emerging warning signal.</p>
                </div>
                <div>
                    <span>Linked account</span>
                    <strong>{top_account}</strong>
                    <p>Customer account associated with the top emerging alert.</p>
                </div>
                <div>
                    <span>Main driver</span>
                    <strong>{top_driver}</strong>
                    <p>Main factor behind the top emerging alert.</p>
                </div>
                <div>
                    <span>Alerts with mantraps</span>
                    <strong>{alert_with_mantraps:,}</strong>
                    <p>Emerging equipment where at least one mantrap event was recorded.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_emerging_alert_table(filtered_alerts: pd.DataFrame) -> None:
    """Render filtered emerging alert table."""
    display_columns = [
        "equipment_description_raw",
        "account_name_raw",
        "equipment_type",
        "callbacks",
        "mantraps",
        "mantrap_rate_pct",
        "recent_90d_callbacks",
        "recent_90d_mantraps",
        "recent_180d_callbacks",
        "recent_365d_callbacks",
        "equipment_risk_score_v3",
        "risk_tier",
        "risk_signal_type",
        "primary_risk_driver",
        "risk_explanation",
    ]

    available_columns = [
        column for column in display_columns
        if column in filtered_alerts.columns
    ]

    st.dataframe(
        filtered_alerts[available_columns],
        width="stretch",
        hide_index=True,
    )


def render_emerging_alerts(
    emerging_equipment_alerts: pd.DataFrame,
) -> None:
    """Render emerging equipment alert dashboard page."""
    render_section_header(
        title="Emerging Alerts",
        subtitle="Detect low-history equipment that already shows early warning signals from recent callbacks, mantraps, or risk-score behavior.",
    )

    if emerging_equipment_alerts.empty:
        st.info("No emerging equipment alerts for the selected period.")
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

    render_emerging_interpretation(filtered_alerts)

    render_section_header(
        title="Emerging alert ranking",
        subtitle="Filtered emerging-alert equipment ranked by composite equipment risk score.",
    )

    render_emerging_alert_table(filtered_alerts)
