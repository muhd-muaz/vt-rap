from __future__ import annotations

import pandas as pd
import plotly.express as px


def apply_dark_chart_layout(figure, height: int):
    """Apply shared Plotly dark command-center layout."""
    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f8fafc"},
        height=height,
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
    )

    return figure


def build_monthly_callback_chart(monthly_callback_trend: pd.DataFrame):
    """Build callback and mantrap monthly trend chart."""
    trend = monthly_callback_trend.copy()
    trend["event_month"] = trend["event_month"].astype(str)

    melted = trend.melt(
        id_vars=["event_month"],
        value_vars=["callbacks", "mantraps"],
        var_name="metric",
        value_name="value",
    )

    figure = px.line(
        melted,
        x="event_month",
        y="value",
        color="metric",
        markers=True,
        title="Monthly Callback and Mantrap Trend",
    )

    figure.update_xaxes(title_text="Month")
    figure.update_yaxes(title_text="Count")

    return apply_dark_chart_layout(figure, height=430)


def build_monthly_response_repair_chart(monthly_callback_trend: pd.DataFrame):
    """Build median response and repair monthly trend chart."""
    trend = monthly_callback_trend.copy()
    trend["event_month"] = trend["event_month"].astype(str)

    melted = trend.melt(
        id_vars=["event_month"],
        value_vars=["median_response_minutes", "median_repair_minutes"],
        var_name="metric",
        value_name="minutes",
    )

    figure = px.line(
        melted,
        x="event_month",
        y="minutes",
        color="metric",
        markers=True,
        title="Monthly Median Response and Repair Time",
    )

    figure.update_xaxes(title_text="Month")
    figure.update_yaxes(title_text="Minutes")

    return apply_dark_chart_layout(figure, height=430)


def build_fault_family_chart(fault_family_summary: pd.DataFrame):
    """Build fault-family callback volume chart."""
    chart_data = fault_family_summary.sort_values("callbacks", ascending=True)

    figure = px.bar(
        chart_data,
        x="callbacks",
        y="fault_family_final",
        orientation="h",
        title="Callback Volume by Fault Family",
        hover_data=[
            "mantraps",
            "mantrap_rate_pct",
            "median_response_minutes",
            "median_repair_minutes",
        ],
        color="mantrap_rate_pct",
        color_continuous_scale="Reds",
    )

    figure.update_xaxes(title_text="Callbacks")
    figure.update_yaxes(title_text="")

    return apply_dark_chart_layout(figure, height=480)


def build_fault_family_trend_chart(
    monthly_fault_family_trend: pd.DataFrame,
    selected_fault_families: list[str],
):
    """Build monthly trend for selected fault families."""
    trend = monthly_fault_family_trend[
        monthly_fault_family_trend["fault_family_final"].isin(selected_fault_families)
    ].copy()

    trend["event_month"] = trend["event_month"].astype(str)

    figure = px.line(
        trend,
        x="event_month",
        y="callbacks",
        color="fault_family_final",
        markers=True,
        title="Monthly Fault Family Trend",
    )

    figure.update_xaxes(title_text="Month")
    figure.update_yaxes(title_text="Callbacks")

    return apply_dark_chart_layout(figure, height=520)


def build_equipment_type_trend_chart(monthly_equipment_type_trend: pd.DataFrame):
    """Build monthly equipment type callback trend."""
    top_equipment_types = (
        monthly_equipment_type_trend.groupby("equipment_type")["callbacks"]
        .sum()
        .sort_values(ascending=False)
        .head(8)
        .index
        .tolist()
    )

    trend = monthly_equipment_type_trend[
        monthly_equipment_type_trend["equipment_type"].isin(top_equipment_types)
    ].copy()

    trend["event_month"] = trend["event_month"].astype(str)

    figure = px.line(
        trend,
        x="event_month",
        y="callbacks",
        color="equipment_type",
        markers=True,
        title="Monthly Callback Trend by Equipment Type",
    )

    figure.update_xaxes(title_text="Month")
    figure.update_yaxes(title_text="Callbacks")

    return apply_dark_chart_layout(figure, height=520)


def build_top_account_chart(account_risk_model: pd.DataFrame):
    """Build top account risk chart."""
    chart_data = account_risk_model.head(15).sort_values(
        "account_risk_score",
        ascending=True,
    )

    figure = px.bar(
        chart_data,
        x="account_risk_score",
        y="account_name_raw",
        orientation="h",
        title="Top Account Risk Score",
        hover_data=[
            "callbacks",
            "mantraps",
            "unique_equipment",
            "mantrap_rate_pct",
            "primary_risk_driver",
        ],
        color="account_risk_score",
        color_continuous_scale="Bluered",
    )

    figure.update_xaxes(title_text="Risk Score")
    figure.update_yaxes(title_text="")

    return apply_dark_chart_layout(figure, height=520)


def build_account_monthly_chart(
    monthly_account_trend: pd.DataFrame,
    selected_account_name: str,
):
    """Build monthly trend for selected account."""
    trend = monthly_account_trend[
        monthly_account_trend["account_name_raw"].eq(selected_account_name)
    ].copy()

    trend["event_month"] = trend["event_month"].astype(str)

    melted = trend.melt(
        id_vars=["event_month"],
        value_vars=["callbacks", "mantraps"],
        var_name="metric",
        value_name="value",
    )

    figure = px.line(
        melted,
        x="event_month",
        y="value",
        color="metric",
        markers=True,
        title=f"Monthly Trend: {selected_account_name}",
    )

    figure.update_xaxes(title_text="Month")
    figure.update_yaxes(title_text="Count")

    return apply_dark_chart_layout(figure, height=460)

def build_equipment_monthly_chart(
    monthly_equipment_trend: pd.DataFrame,
    selected_equipment: str,
):
    """Build monthly callback and mantrap trend for selected equipment."""
    trend = monthly_equipment_trend[
        monthly_equipment_trend["equipment_description_raw"].eq(selected_equipment)
    ].copy()

    trend["event_month"] = trend["event_month"].astype(str)

    melted = trend.melt(
        id_vars=["event_month"],
        value_vars=["callbacks", "mantraps"],
        var_name="metric",
        value_name="value",
    )

    figure = px.line(
        melted,
        x="event_month",
        y="value",
        color="metric",
        markers=True,
        title=f"Monthly Equipment Trend: {selected_equipment}",
    )

    figure.update_xaxes(title_text="Month")
    figure.update_yaxes(title_text="Count")

    return apply_dark_chart_layout(figure, height=460)


def build_equipment_fault_mix_chart(
    equipment_fault_family_mix: pd.DataFrame,
    selected_equipment: str,
):
    """Build fault family mix chart for selected equipment."""
    mix = equipment_fault_family_mix[
        equipment_fault_family_mix["equipment_description_raw"].eq(selected_equipment)
    ].copy()

    mix = mix.sort_values("callbacks", ascending=True)

    figure = px.bar(
        mix,
        x="callbacks",
        y="fault_family_final",
        orientation="h",
        title=f"Fault Family Mix: {selected_equipment}",
        hover_data=[
            "mantraps",
            "mantrap_rate_pct",
            "median_response_minutes",
            "median_repair_minutes",
        ],
        color="mantraps",
        color_continuous_scale="Reds",
    )

    figure.update_xaxes(title_text="Callbacks")
    figure.update_yaxes(title_text="Fault Family")

    return apply_dark_chart_layout(figure, height=460)

def build_account_fault_mix_chart(
    account_fault_family_mix: pd.DataFrame,
    selected_account_name: str,
):
    """Build fault family mix chart for selected account."""
    mix = account_fault_family_mix[
        account_fault_family_mix["account_name_raw"].eq(selected_account_name)
    ].copy()

    mix = mix.sort_values("callbacks", ascending=True)

    figure = px.bar(
        mix,
        x="callbacks",
        y="fault_family_final",
        orientation="h",
        title=f"Fault Family Mix: {selected_account_name}",
        hover_data=[
            "mantraps",
            "mantrap_rate_pct",
            "unique_equipment",
            "median_response_minutes",
            "median_repair_minutes",
        ],
        color="mantraps",
        color_continuous_scale="Reds",
    )

    figure.update_xaxes(title_text="Callbacks")
    figure.update_yaxes(title_text="Fault Family")

    return apply_dark_chart_layout(figure, height=460)