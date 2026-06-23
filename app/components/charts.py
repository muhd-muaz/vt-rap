from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


CHART_FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"

COLOR_PRIMARY = "#0A84FF"
COLOR_SUCCESS = "#30D158"
COLOR_WARNING = "#FF9F0A"
COLOR_DANGER = "#FF453A"
COLOR_PURPLE = "#BF5AF2"
COLOR_MUTED = "#8E8E93"

CHART_COLOR_SEQUENCE = [
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_PURPLE,
    COLOR_DANGER,
    "#64D2FF",
    "#FFD60A",
    "#FF375F",
]


def apply_smooth_chart_layout(
    figure,
    height: int,
    xaxis_title: str = "",
    yaxis_title: str = "",
    force_category_xaxis: bool = False,
):
    """Apply shared smooth dashboard chart styling."""
    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "family": CHART_FONT_FAMILY,
            "color": "#F5F5F7",
            "size": 12,
        },
        title={
            "font": {
                "family": CHART_FONT_FAMILY,
                "size": 18,
                "color": "#F5F5F7",
            },
            "x": 0.02,
            "xanchor": "left",
        },
        height=height,
        margin={"l": 24, "r": 24, "t": 64, "b": 40},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"size": 11},
            "title": None,
        },
        hovermode="x unified",
    )

    figure.update_xaxes(
        title_text=xaxis_title,
        showgrid=False,
        zeroline=False,
        showline=False,
        tickfont={"size": 11, "color": "#C7C7CC"},
        title_font={"size": 12, "color": "#C7C7CC"},
    )

    figure.update_yaxes(
        title_text=yaxis_title,
        gridcolor="rgba(142, 142, 147, 0.18)",
        zeroline=False,
        showline=False,
        tickfont={"size": 11, "color": "#C7C7CC"},
        title_font={"size": 12, "color": "#C7C7CC"},
    )

    if force_category_xaxis:
        figure.update_xaxes(type="category")

    return figure


def prepare_month_label(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Prepare event month as a clean categorical display label."""
    prepared = dataframe.copy()
    prepared["event_month"] = prepared["event_month"].astype(str)
    return prepared


def build_monthly_callback_chart(monthly_callback_trend: pd.DataFrame):
    """Build callback and mantrap monthly trend chart."""
    trend = prepare_month_label(monthly_callback_trend)

    melted = trend.melt(
        id_vars=["event_month"],
        value_vars=["callbacks", "mantraps"],
        var_name="metric",
        value_name="value",
    )

    metric_labels = {
        "callbacks": "Callbacks",
        "mantraps": "Mantraps",
    }

    melted["metric"] = melted["metric"].map(metric_labels)

    if trend["event_month"].nunique() <= 1:
        figure = px.bar(
            melted,
            x="event_month",
            y="value",
            color="metric",
            barmode="group",
            title="Monthly Callback and Mantrap Trend",
            color_discrete_sequence=[COLOR_PRIMARY, COLOR_DANGER],
        )
    else:
        figure = px.line(
            melted,
            x="event_month",
            y="value",
            color="metric",
            markers=True,
            title="Monthly Callback and Mantrap Trend",
            color_discrete_sequence=[COLOR_PRIMARY, COLOR_DANGER],
            line_shape="spline",
        )

        figure.update_traces(
            line={"width": 3},
            marker={"size": 8},
        )

    return apply_smooth_chart_layout(
        figure,
        height=430,
        xaxis_title="Month",
        yaxis_title="Count",
        force_category_xaxis=True,
    )


def build_monthly_response_repair_chart(monthly_callback_trend: pd.DataFrame):
    """Build median response and repair monthly trend chart."""
    trend = prepare_month_label(monthly_callback_trend)

    melted = trend.melt(
        id_vars=["event_month"],
        value_vars=["median_response_minutes", "median_repair_minutes"],
        var_name="metric",
        value_name="minutes",
    )

    metric_labels = {
        "median_response_minutes": "Median Response",
        "median_repair_minutes": "Median Repair",
    }

    melted["metric"] = melted["metric"].map(metric_labels)

    if trend["event_month"].nunique() <= 1:
        figure = px.bar(
            melted,
            x="event_month",
            y="minutes",
            color="metric",
            barmode="group",
            title="Monthly Median Response and Repair Time",
            color_discrete_sequence=[COLOR_PRIMARY, COLOR_SUCCESS],
        )
    else:
        figure = px.line(
            melted,
            x="event_month",
            y="minutes",
            color="metric",
            markers=True,
            title="Monthly Median Response and Repair Time",
            color_discrete_sequence=[COLOR_PRIMARY, COLOR_SUCCESS],
            line_shape="spline",
        )

        figure.update_traces(
            line={"width": 3},
            marker={"size": 8},
        )

    return apply_smooth_chart_layout(
        figure,
        height=430,
        xaxis_title="Month",
        yaxis_title="Minutes",
        force_category_xaxis=True,
    )


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
        color_continuous_scale=[
            "#1C1C1E",
            "#2E5EAA",
            "#0A84FF",
            "#30D158",
        ],
    )

    figure.update_traces(
        marker_line_width=0,
        opacity=0.92,
    )

    return apply_smooth_chart_layout(
        figure,
        height=480,
        xaxis_title="Callbacks",
        yaxis_title="",
    )


def build_fault_family_trend_chart(
    monthly_fault_family_trend: pd.DataFrame,
    selected_fault_families: list[str],
):
    """Build monthly trend for selected fault families."""
    trend = monthly_fault_family_trend[
        monthly_fault_family_trend["fault_family_final"].isin(selected_fault_families)
    ].copy()

    trend = prepare_month_label(trend)

    if trend.empty:
        figure = go.Figure()
        figure.add_annotation(
            text="No data available for selected fault families.",
            showarrow=False,
            font={"color": "#C7C7CC", "size": 14},
        )
    else:
        figure = px.line(
            trend,
            x="event_month",
            y="callbacks",
            color="fault_family_final",
            markers=True,
            title="Monthly Fault Family Trend",
            color_discrete_sequence=CHART_COLOR_SEQUENCE,
            line_shape="spline",
        )

        figure.update_traces(
            line={"width": 3},
            marker={"size": 7},
        )

    return apply_smooth_chart_layout(
        figure,
        height=520,
        xaxis_title="Month",
        yaxis_title="Callbacks",
        force_category_xaxis=True,
    )


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

    trend = prepare_month_label(trend)

    figure = px.line(
        trend,
        x="event_month",
        y="callbacks",
        color="equipment_type",
        markers=True,
        title="Monthly Callback Trend by Equipment Type",
        color_discrete_sequence=CHART_COLOR_SEQUENCE,
        line_shape="spline",
    )

    figure.update_traces(
        line={"width": 3},
        marker={"size": 7},
    )

    return apply_smooth_chart_layout(
        figure,
        height=520,
        xaxis_title="Month",
        yaxis_title="Callbacks",
        force_category_xaxis=True,
    )


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
        color_continuous_scale=[
            "#1C1C1E",
            "#164E63",
            "#0A84FF",
            "#30D158",
        ],
    )

    figure.update_traces(
        marker_line_width=0,
        opacity=0.92,
    )

    return apply_smooth_chart_layout(
        figure,
        height=520,
        xaxis_title="Risk Score",
        yaxis_title="",
    )


def build_account_monthly_chart(
    monthly_account_trend: pd.DataFrame,
    selected_account_name: str,
):
    """Build monthly trend for selected account."""
    trend = monthly_account_trend[
        monthly_account_trend["account_name_raw"].eq(selected_account_name)
    ].copy()

    trend = prepare_month_label(trend)

    melted = trend.melt(
        id_vars=["event_month"],
        value_vars=["callbacks", "mantraps"],
        var_name="metric",
        value_name="value",
    )

    metric_labels = {
        "callbacks": "Callbacks",
        "mantraps": "Mantraps",
    }

    melted["metric"] = melted["metric"].map(metric_labels)

    if trend["event_month"].nunique() <= 1:
        figure = px.bar(
            melted,
            x="event_month",
            y="value",
            color="metric",
            barmode="group",
            title=f"Monthly Trend: {selected_account_name}",
            color_discrete_sequence=[COLOR_PRIMARY, COLOR_DANGER],
        )
    else:
        figure = px.line(
            melted,
            x="event_month",
            y="value",
            color="metric",
            markers=True,
            title=f"Monthly Trend: {selected_account_name}",
            color_discrete_sequence=[COLOR_PRIMARY, COLOR_DANGER],
            line_shape="spline",
        )

        figure.update_traces(
            line={"width": 3},
            marker={"size": 8},
        )

    return apply_smooth_chart_layout(
        figure,
        height=460,
        xaxis_title="Month",
        yaxis_title="Count",
        force_category_xaxis=True,
    )


def build_equipment_monthly_chart(
    monthly_equipment_trend: pd.DataFrame,
    selected_equipment: str,
):
    """Build monthly callback and mantrap trend for selected equipment."""
    trend = monthly_equipment_trend[
        monthly_equipment_trend["equipment_description_raw"].eq(selected_equipment)
    ].copy()

    trend = prepare_month_label(trend)

    melted = trend.melt(
        id_vars=["event_month"],
        value_vars=["callbacks", "mantraps"],
        var_name="metric",
        value_name="value",
    )

    metric_labels = {
        "callbacks": "Callbacks",
        "mantraps": "Mantraps",
    }

    melted["metric"] = melted["metric"].map(metric_labels)

    if trend["event_month"].nunique() <= 1:
        figure = px.bar(
            melted,
            x="event_month",
            y="value",
            color="metric",
            barmode="group",
            title=f"Monthly Equipment Trend: {selected_equipment}",
            color_discrete_sequence=[COLOR_PRIMARY, COLOR_DANGER],
        )
    else:
        figure = px.line(
            melted,
            x="event_month",
            y="value",
            color="metric",
            markers=True,
            title=f"Monthly Equipment Trend: {selected_equipment}",
            color_discrete_sequence=[COLOR_PRIMARY, COLOR_DANGER],
            line_shape="spline",
        )

        figure.update_traces(
            line={"width": 3},
            marker={"size": 8},
        )

    return apply_smooth_chart_layout(
        figure,
        height=460,
        xaxis_title="Month",
        yaxis_title="Count",
        force_category_xaxis=True,
    )


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
        color_continuous_scale=[
            "#1C1C1E",
            "#0A84FF",
            "#FF9F0A",
            "#FF453A",
        ],
    )

    figure.update_traces(
        marker_line_width=0,
        opacity=0.92,
    )

    return apply_smooth_chart_layout(
        figure,
        height=460,
        xaxis_title="Callbacks",
        yaxis_title="Fault Family",
    )


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
        color_continuous_scale=[
            "#1C1C1E",
            "#0A84FF",
            "#FF9F0A",
            "#FF453A",
        ],
    )

    figure.update_traces(
        marker_line_width=0,
        opacity=0.92,
    )

    return apply_smooth_chart_layout(
        figure,
        height=460,
        xaxis_title="Callbacks",
        yaxis_title="Fault Family",
    )