from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards import render_command_card
from components.charts import (
    build_account_fault_mix_chart,
    build_account_monthly_chart,
)
from components.layout import render_section_header


def get_available_risk_tiers(account_risk_model: pd.DataFrame) -> list[str]:
    """Return available account risk tiers."""
    if "risk_tier" not in account_risk_model.columns:
        return []

    return (
        account_risk_model["risk_tier"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )


def render_account_overview_cards(account_risk_model: pd.DataFrame) -> None:
    """Render account risk overview cards."""
    total_accounts = len(account_risk_model)

    critical_accounts = int(
        account_risk_model["risk_tier"].eq("Critical").sum()
        if "risk_tier" in account_risk_model.columns
        else 0
    )

    high_accounts = int(
        account_risk_model["risk_tier"].eq("High").sum()
        if "risk_tier" in account_risk_model.columns
        else 0
    )

    total_mantraps = int(
        account_risk_model["mantraps"].sum()
        if "mantraps" in account_risk_model.columns
        else 0
    )

    card_col_1, card_col_2, card_col_3, card_col_4 = st.columns(4)

    with card_col_1:
        render_command_card(
            title="Accounts Analyzed",
            value=f"{total_accounts:,}",
            caption="Customer accounts active in the selected period.",
        )

    with card_col_2:
        render_command_card(
            title="Critical Accounts",
            value=f"{critical_accounts:,}",
            caption="Accounts classified as critical operational risk.",
        )

    with card_col_3:
        render_command_card(
            title="High-Risk Accounts",
            value=f"{high_accounts:,}",
            caption="Accounts classified as high operational risk.",
        )

    with card_col_4:
        render_command_card(
            title="Account Mantraps",
            value=f"{total_mantraps:,}",
            caption="Total mantrap events across account records.",
        )


def filter_account_risk_model(account_risk_model: pd.DataFrame) -> pd.DataFrame:
    """Render account filters and return filtered account risk model."""
    with st.container(border=True):
        st.caption("Account risk filters")

        filter_col_1, filter_col_2, filter_col_3, filter_col_4 = st.columns(
            [1.1, 1, 1, 1]
        )

        with filter_col_1:
            selected_risk_tiers = st.multiselect(
                "Risk tier",
                options=get_available_risk_tiers(account_risk_model),
                default=get_available_risk_tiers(account_risk_model),
                key="account_risk_tier_filter",
            )

        with filter_col_2:
            minimum_callbacks = st.number_input(
                "Minimum callbacks",
                min_value=0,
                value=0,
                step=1,
                key="account_minimum_callbacks_filter",
            )

        with filter_col_3:
            minimum_mantraps = st.number_input(
                "Minimum mantraps",
                min_value=0,
                value=0,
                step=1,
                key="account_minimum_mantraps_filter",
            )

        with filter_col_4:
            minimum_equipment = st.number_input(
                "Minimum equipment",
                min_value=0,
                value=0,
                step=1,
                key="account_minimum_equipment_filter",
            )

        search_text = st.text_input(
            "Search account",
            placeholder="Type account name or account code...",
            key="account_search_filter",
        )

    filtered = account_risk_model.copy()

    if selected_risk_tiers:
        filtered = filtered[filtered["risk_tier"].isin(selected_risk_tiers)]

    filtered = filtered[
        filtered["callbacks"].ge(minimum_callbacks)
        & filtered["mantraps"].ge(minimum_mantraps)
        & filtered["unique_equipment"].ge(minimum_equipment)
    ]

    if search_text.strip():
        search_value = search_text.strip().lower()

        filtered = filtered[
            filtered["account_name_raw"]
            .astype(str)
            .str.lower()
            .str.contains(search_value, na=False)
            | filtered["account_code"]
            .astype(str)
            .str.lower()
            .str.contains(search_value, na=False)
        ]

    return filtered


def render_account_risk_table(filtered_accounts: pd.DataFrame) -> None:
    """Render filtered account risk table."""
    display_columns = [
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

    available_columns = [
        column for column in display_columns if column in filtered_accounts.columns
    ]

    st.dataframe(
        filtered_accounts[available_columns],
        width="stretch",
        hide_index=True,
    )


def render_selected_account_profile(selected_row: pd.Series) -> None:
    """Render selected account profile."""
    st.markdown(
        f"""
        <div class="insight-panel">
            <div class="insight-panel-title">Selected account profile</div>
            <div class="insight-grid">
                <div>
                    <span>Account</span>
                    <strong>{selected_row.get("account_name_raw", "-")}</strong>
                    <p>Customer account selected for operational drilldown.</p>
                </div>
                <div>
                    <span>Account code</span>
                    <strong>{selected_row.get("account_code", "-")}</strong>
                    <p>Original account identifier from the source records.</p>
                </div>
                <div>
                    <span>Risk tier</span>
                    <strong>{selected_row.get("risk_tier", "-")}</strong>
                    <p>Current account-level risk classification.</p>
                </div>
                <div>
                    <span>Primary driver</span>
                    <strong>{selected_row.get("primary_risk_driver", "-")}</strong>
                    <p>Main factor contributing to the account risk score.</p>
                </div>
                <div>
                    <span>Callbacks</span>
                    <strong>{int(selected_row.get("callbacks", 0)):,}</strong>
                    <p>Total callback volume under this account.</p>
                </div>
                <div>
                    <span>Mantraps</span>
                    <strong>{int(selected_row.get("mantraps", 0)):,}</strong>
                    <p>Mantrap-related callback events under this account.</p>
                </div>
                <div>
                    <span>Unique equipment</span>
                    <strong>{int(selected_row.get("unique_equipment", 0)):,}</strong>
                    <p>Number of equipment units linked to this account.</p>
                </div>
                <div>
                    <span>Risk score</span>
                    <strong>{float(selected_row.get("account_risk_score", 0)):,.2f}</strong>
                    <p>Composite account risk score.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_account_equipment_table(
    equipment_risk_model: pd.DataFrame,
    selected_account_name: str,
) -> None:
    """Render equipment ranking under selected account."""
    account_equipment = equipment_risk_model[
        equipment_risk_model["account_name_raw"].eq(selected_account_name)
    ].copy()

    if account_equipment.empty:
        st.info("No equipment risk records found for the selected account.")
        return

    account_equipment = account_equipment.sort_values(
        "equipment_risk_score_v3",
        ascending=False,
    )

    display_columns = [
        "equipment_description_raw",
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
    ]

    available_columns = [
        column for column in display_columns if column in account_equipment.columns
    ]

    st.dataframe(
        account_equipment[available_columns],
        width="stretch",
        hide_index=True,
    )


def render_account_risk(
    account_risk_model: pd.DataFrame,
    monthly_account_trend: pd.DataFrame,
    equipment_risk_model: pd.DataFrame,
    account_fault_family_mix: pd.DataFrame,
) -> None:
    """Render account risk dashboard page."""
    render_section_header(
        title="Account Risk",
        subtitle="Identify customer accounts with concentrated callback volume, mantrap exposure, and equipment reliability risk.",
    )

    render_account_overview_cards(account_risk_model)

    filtered_accounts = filter_account_risk_model(account_risk_model)

    if filtered_accounts.empty:
        st.warning("No accounts match the selected filters.")
        return

    filtered_accounts = filtered_accounts.sort_values(
        "account_risk_score",
        ascending=False,
    )

    render_section_header(
        title="Filtered account ranking",
        subtitle="Accounts ranked by composite operational risk score after applying the current filters.",
    )

    render_account_risk_table(filtered_accounts.head(100))

    selected_account_name = st.selectbox(
        "Select account for drilldown",
        options=filtered_accounts["account_name_raw"].tolist(),
        index=0,
        key="selected_account_drilldown",
    )

    selected_row = filtered_accounts[
        filtered_accounts["account_name_raw"].eq(selected_account_name)
    ].iloc[0]

    render_selected_account_profile(selected_row)

    chart_col_1, chart_col_2 = st.columns(2)

    with chart_col_1:
        st.plotly_chart(
            build_account_monthly_chart(
                monthly_account_trend=monthly_account_trend,
                selected_account_name=selected_account_name,
            ),
            width="stretch",
            key="account_risk_monthly_chart",
        )

    with chart_col_2:
        st.plotly_chart(
            build_account_fault_mix_chart(
                account_fault_family_mix=account_fault_family_mix,
                selected_account_name=selected_account_name,
            ),
            width="stretch",
            key="account_risk_fault_mix_chart",
        )

    render_section_header(
        title="Equipment under selected account",
        subtitle="Equipment linked to the selected account, ranked by equipment risk score.",
    )

    render_account_equipment_table(
        equipment_risk_model=equipment_risk_model,
        selected_account_name=selected_account_name,
    )
