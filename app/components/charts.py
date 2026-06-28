from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CHART_FONT_FAMILY = (
    "-apple-system, BlinkMacSystemFont, SF Pro Display, "
    "SF Pro Text, Inter, Segoe UI, Roboto, Arial, sans-serif"
)

BACKGROUND_TRANSPARENT = "rgba(0,0,0,0)"
GRID_COLOR = "rgba(255, 255, 255, 0.08)"
TEXT_MAIN = "#F5F7FA"
TEXT_MUTED = "#9CA3AF"

COLOR_CALLBACKS = "#60A5FA"
COLOR_MANTRAPS = "#FB7185"
COLOR_RESPONSE = "#38BDF8"
COLOR_REPAIR = "#2DD4BF"
COLOR_ACCENT = "#2DD4BF"
COLOR_PURPLE = "#C084FC"
COLOR_WARNING = "#FDBA74"
COLOR_YELLOW = "#FDE68A"

CHART_COLOR_SEQUENCE = [
    "#60A5FA",
    "#2DD4BF",
    "#C084FC",
    "#FDBA74",
    "#FDE68A",
    "#FB7185",
    "#93C5FD",
    "#99F6E4",
]


def build_empty_chart(message: str, height: int):
    """Build an empty chart surface with a clear annotation."""
    figure = go.Figure()
    figure.add_annotation(
        text=message,
        showarrow=False,
        font={"color": TEXT_MUTED, "size": 14},
    )
    return apply_modern_dark_layout(figure, height=height)


def apply_modern_dark_layout(
    figure,
    height: int,
    xaxis_title: str = "",
    yaxis_title: str = "",
    force_category_xaxis: bool = False,
):
    """Apply modern dark chart layout."""
    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor=BACKGROUND_TRANSPARENT,
        plot_bgcolor=BACKGROUND_TRANSPARENT,
        height=height,
        margin={"l": 24, "r": 24, "t": 68, "b": 42},
        font={
            "family": CHART_FONT_FAMILY,
            "color": TEXT_MAIN,
            "size": 12,
        },
        title={
            "font": {
                "family": CHART_FONT_FAMILY,
                "size": 18,
                "color": TEXT_MAIN,
            },
            "x": 0.02,
            "xanchor": "left",
            "y": 0.96,
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.03,
            "xanchor": "right",
            "x": 1,
            "font": {"size": 11, "color": TEXT_MUTED},
            "title": None,
            "bgcolor": BACKGROUND_TRANSPARENT,
        },
        hovermode="x unified",
        hoverlabel={
            "bgcolor": "#111827",
            "bordercolor": "rgba(255,255,255,0.10)",
            "font": {"family": CHART_FONT_FAMILY, "size": 12, "color": TEXT_MAIN},
        },
    )

    figure.update_xaxes(
        title_text=xaxis_title,
        showgrid=False,
        zeroline=False,
        showline=False,
        ticks="",
        tickfont={"size": 11, "color": TEXT_MUTED},
        title_font={"size": 12, "color": TEXT_MUTED},
    )

    figure.update_yaxes(
        title_text=yaxis_title,
        gridcolor=GRID_COLOR,
        zeroline=False,
        showline=False,
        ticks="",
        tickfont={"size": 11, "color": TEXT_MUTED},
        title_font={"size": 12, "color": TEXT_MUTED},
    )

    if force_category_xaxis:
        figure.update_xaxes(type="category")

    return figure


def prepare_month_label(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Prepare event month as clean display label."""
    prepared = dataframe.copy()
    prepared["event_month"] = prepared["event_month"].astype(str)
    return prepared


def build_grouped_bar_for_single_period(
    dataframe: pd.DataFrame,
    x_column: str,
    y_column: str,
    color_column: str,
    title: str,
    colors: list[str],
):
    """Build a modern grouped bar chart for one-period data."""
    figure = px.bar(
        dataframe,
        x=x_column,
        y=y_column,
        color=color_column,
        barmode="group",
        title=title,
        color_discrete_sequence=colors,
    )

    figure.update_traces(
        marker_line_width=0,
        opacity=0.95,
        width=0.38,
    )

    return figure


def build_smooth_line_chart(
    dataframe: pd.DataFrame,
    x_column: str,
    y_column: str,
    color_column: str,
    title: str,
    colors: list[str],
):
    """Build a smooth line chart with modern markers."""
    figure = px.line(
        dataframe,
        x=x_column,
        y=y_column,
        color=color_column,
        markers=True,
        title=title,
        color_discrete_sequence=colors,
        line_shape="spline",
    )

    figure.update_traces(
        line={"width": 3.2},
        marker={
            "size": 8,
            "line": {"width": 2, "color": "#070A12"},
        },
    )

    return figure


def build_monthly_callback_chart(monthly_callback_trend: pd.DataFrame):
    """Build callback and mantrap monthly trend chart."""
    required_columns = {"event_month", "callbacks", "mantraps"}
    if monthly_callback_trend.empty or not required_columns.issubset(
        monthly_callback_trend.columns
    ):
        return build_empty_chart("No monthly callback data available.", height=430)

    trend = prepare_month_label(monthly_callback_trend)

    melted = trend.melt(
        id_vars=["event_month"],
        value_vars=["callbacks", "mantraps"],
        var_name="metric",
        value_name="value",
    )

    melted["metric"] = melted["metric"].map(
        {
            "callbacks": "Callbacks",
            "mantraps": "Mantraps",
        }
    )

    if trend["event_month"].nunique() <= 1:
        figure = build_grouped_bar_for_single_period(
            dataframe=melted,
            x_column="event_month",
            y_column="value",
            color_column="metric",
            title="Callback and Mantrap Volume",
            colors=[COLOR_CALLBACKS, COLOR_MANTRAPS],
        )
    else:
        figure = build_smooth_line_chart(
            dataframe=melted,
            x_column="event_month",
            y_column="value",
            color_column="metric",
            title="Monthly Callback and Mantrap Trend",
            colors=[COLOR_CALLBACKS, COLOR_MANTRAPS],
        )

    return apply_modern_dark_layout(
        figure,
        height=430,
        xaxis_title="Month",
        yaxis_title="Count",
        force_category_xaxis=True,
    )


def build_monthly_response_repair_chart(monthly_callback_trend: pd.DataFrame):
    """Build median response and repair monthly trend chart."""
    required_columns = {
        "event_month",
        "median_response_minutes",
        "median_repair_minutes",
    }
    if monthly_callback_trend.empty or not required_columns.issubset(
        monthly_callback_trend.columns
    ):
        return build_empty_chart(
            "No response or repair timing data available.", height=430
        )

    trend = prepare_month_label(monthly_callback_trend)

    melted = trend.melt(
        id_vars=["event_month"],
        value_vars=["median_response_minutes", "median_repair_minutes"],
        var_name="metric",
        value_name="minutes",
    )

    melted["metric"] = melted["metric"].map(
        {
            "median_response_minutes": "Median Response",
            "median_repair_minutes": "Median Repair",
        }
    )

    if trend["event_month"].nunique() <= 1:
        figure = build_grouped_bar_for_single_period(
            dataframe=melted,
            x_column="event_month",
            y_column="minutes",
            color_column="metric",
            title="Median Response and Repair Time",
            colors=[COLOR_RESPONSE, COLOR_REPAIR],
        )
    else:
        figure = build_smooth_line_chart(
            dataframe=melted,
            x_column="event_month",
            y_column="minutes",
            color_column="metric",
            title="Monthly Median Response and Repair Time",
            colors=[COLOR_RESPONSE, COLOR_REPAIR],
        )

    return apply_modern_dark_layout(
        figure,
        height=430,
        xaxis_title="Month",
        yaxis_title="Minutes",
        force_category_xaxis=True,
    )


def build_fault_family_chart(fault_family_summary: pd.DataFrame):
    """Build fault-family callback volume chart."""
    required_columns = {"fault_family_final", "callbacks"}
    if fault_family_summary.empty or not required_columns.issubset(
        fault_family_summary.columns
    ):
        return build_empty_chart("No fault family data available.", height=480)

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
        color="callbacks",
        color_continuous_scale=[
            "#1E293B",
            "#2563EB",
            "#2DD4BF",
        ],
    )

    figure.update_traces(
        marker_line_width=0,
        opacity=0.96,
    )

    figure.update_layout(coloraxis_showscale=False)

    return apply_modern_dark_layout(
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
    required_columns = {"event_month", "fault_family_final", "callbacks"}
    if monthly_fault_family_trend.empty or not required_columns.issubset(
        monthly_fault_family_trend.columns
    ):
        return build_empty_chart("No fault family trend data available.", height=520)

    trend = monthly_fault_family_trend[
        monthly_fault_family_trend["fault_family_final"].isin(selected_fault_families)
    ].copy()

    trend = prepare_month_label(trend)

    if trend.empty:
        figure = go.Figure()
        figure.add_annotation(
            text="No data available for selected fault families.",
            showarrow=False,
            font={"color": TEXT_MUTED, "size": 14},
        )
    elif trend["event_month"].nunique() <= 1:
        figure = px.bar(
            trend,
            x="fault_family_final",
            y="callbacks",
            title="Fault Family Volume",
            color="fault_family_final",
            color_discrete_sequence=CHART_COLOR_SEQUENCE,
        )
        figure.update_traces(marker_line_width=0, opacity=0.95)
    else:
        figure = build_smooth_line_chart(
            dataframe=trend,
            x_column="event_month",
            y_column="callbacks",
            color_column="fault_family_final",
            title="Monthly Fault Family Trend",
            colors=CHART_COLOR_SEQUENCE,
        )

    return apply_modern_dark_layout(
        figure,
        height=520,
        xaxis_title="Month",
        yaxis_title="Callbacks",
        force_category_xaxis=True,
    )


def build_equipment_type_trend_chart(monthly_equipment_type_trend: pd.DataFrame):
    """Build monthly equipment type callback trend."""
    required_columns = {"event_month", "equipment_type", "callbacks"}
    if monthly_equipment_type_trend.empty or not required_columns.issubset(
        monthly_equipment_type_trend.columns
    ):
        return build_empty_chart("No equipment type trend data available.", height=520)

    top_equipment_types = (
        monthly_equipment_type_trend.groupby("equipment_type")["callbacks"]
        .sum()
        .sort_values(ascending=False)
        .head(8)
        .index.tolist()
    )

    trend = monthly_equipment_type_trend[
        monthly_equipment_type_trend["equipment_type"].isin(top_equipment_types)
    ].copy()

    trend = prepare_month_label(trend)

    if trend["event_month"].nunique() <= 1:
        figure = px.bar(
            trend,
            x="equipment_type",
            y="callbacks",
            title="Callback Volume by Equipment Type",
            color="equipment_type",
            color_discrete_sequence=CHART_COLOR_SEQUENCE,
        )
        figure.update_traces(marker_line_width=0, opacity=0.95)
    else:
        figure = build_smooth_line_chart(
            dataframe=trend,
            x_column="event_month",
            y_column="callbacks",
            color_column="equipment_type",
            title="Monthly Callback Trend by Equipment Type",
            colors=CHART_COLOR_SEQUENCE,
        )

    return apply_modern_dark_layout(
        figure,
        height=520,
        xaxis_title="Month",
        yaxis_title="Callbacks",
        force_category_xaxis=True,
    )


def build_top_account_chart(account_risk_model: pd.DataFrame):
    """Build top account risk chart."""
    required_columns = {"account_name_raw", "account_risk_score"}
    if account_risk_model.empty or not required_columns.issubset(
        account_risk_model.columns
    ):
        return build_empty_chart("No account risk data available.", height=520)

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
            "#1E293B",
            "#2563EB",
            "#2DD4BF",
        ],
    )

    figure.update_traces(marker_line_width=0, opacity=0.96)
    figure.update_layout(coloraxis_showscale=False)

    return apply_modern_dark_layout(
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
    required_columns = {"event_month", "account_name_raw", "callbacks", "mantraps"}
    if monthly_account_trend.empty or not required_columns.issubset(
        monthly_account_trend.columns
    ):
        return build_empty_chart("No monthly account trend data available.", height=460)

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

    melted["metric"] = melted["metric"].map(
        {
            "callbacks": "Callbacks",
            "mantraps": "Mantraps",
        }
    )

    if trend["event_month"].nunique() <= 1:
        figure = build_grouped_bar_for_single_period(
            dataframe=melted,
            x_column="event_month",
            y_column="value",
            color_column="metric",
            title=f"Monthly Trend: {selected_account_name}",
            colors=[COLOR_CALLBACKS, COLOR_MANTRAPS],
        )
    else:
        figure = build_smooth_line_chart(
            dataframe=melted,
            x_column="event_month",
            y_column="value",
            color_column="metric",
            title=f"Monthly Trend: {selected_account_name}",
            colors=[COLOR_CALLBACKS, COLOR_MANTRAPS],
        )

    return apply_modern_dark_layout(
        figure,
        height=460,
        xaxis_title="Month",
        yaxis_title="Count",
        force_category_xaxis=True,
    )


def build_equipment_monthly_chart(
    monthly_equipment_trend: pd.DataFrame,
    selected_equipment: str,
    selected_account_name: str | None = None,
):
    """Build monthly callback and mantrap trend for selected equipment."""
    required_columns = {
        "event_month",
        "equipment_description_raw",
        "callbacks",
        "mantraps",
    }
    if monthly_equipment_trend.empty or not required_columns.issubset(
        monthly_equipment_trend.columns
    ):
        return build_empty_chart(
            "No monthly equipment trend data available.", height=460
        )

    trend = monthly_equipment_trend[
        monthly_equipment_trend["equipment_description_raw"].eq(selected_equipment)
    ].copy()

    if selected_account_name is not None and "account_name_raw" in trend.columns:
        trend = trend[trend["account_name_raw"].eq(selected_account_name)].copy()

    if trend.empty:
        return build_empty_chart(
            "No monthly trend data available for the selected equipment.",
            height=460,
        )

    trend = prepare_month_label(trend)

    melted = trend.melt(
        id_vars=["event_month"],
        value_vars=["callbacks", "mantraps"],
        var_name="metric",
        value_name="value",
    )

    melted["metric"] = melted["metric"].map(
        {
            "callbacks": "Callbacks",
            "mantraps": "Mantraps",
        }
    )

    if trend["event_month"].nunique() <= 1:
        figure = build_grouped_bar_for_single_period(
            dataframe=melted,
            x_column="event_month",
            y_column="value",
            color_column="metric",
            title=f"Monthly Equipment Trend: {selected_equipment}",
            colors=[COLOR_CALLBACKS, COLOR_MANTRAPS],
        )
    else:
        figure = build_smooth_line_chart(
            dataframe=melted,
            x_column="event_month",
            y_column="value",
            color_column="metric",
            title=f"Monthly Equipment Trend: {selected_equipment}",
            colors=[COLOR_CALLBACKS, COLOR_MANTRAPS],
        )

    return apply_modern_dark_layout(
        figure,
        height=460,
        xaxis_title="Month",
        yaxis_title="Count",
        force_category_xaxis=True,
    )


def build_equipment_fault_mix_chart(
    equipment_fault_family_mix: pd.DataFrame,
    selected_equipment: str,
    selected_account_name: str | None = None,
):
    """Build fault family mix chart for selected equipment."""
    required_columns = {"equipment_description_raw", "fault_family_final", "callbacks"}
    if equipment_fault_family_mix.empty or not required_columns.issubset(
        equipment_fault_family_mix.columns
    ):
        return build_empty_chart(
            "No equipment fault-family mix data available.", height=460
        )

    mix = equipment_fault_family_mix[
        equipment_fault_family_mix["equipment_description_raw"].eq(selected_equipment)
    ].copy()

    if selected_account_name is not None and "account_name_raw" in mix.columns:
        mix = mix[mix["account_name_raw"].eq(selected_account_name)].copy()

    if mix.empty:
        return build_empty_chart(
            "No fault-family mix data available for the selected equipment.",
            height=460,
        )

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
            "#1E293B",
            "#2563EB",
            "#FDBA74",
            "#FB7185",
        ],
    )

    figure.update_traces(marker_line_width=0, opacity=0.96)
    figure.update_layout(coloraxis_showscale=False)

    return apply_modern_dark_layout(
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
    required_columns = {"account_name_raw", "fault_family_final", "callbacks"}
    if account_fault_family_mix.empty or not required_columns.issubset(
        account_fault_family_mix.columns
    ):
        return build_empty_chart(
            "No account fault-family mix data available.", height=460
        )

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
            "#1E293B",
            "#2563EB",
            "#FDBA74",
            "#FB7185",
        ],
    )

    figure.update_traces(marker_line_width=0, opacity=0.96)
    figure.update_layout(coloraxis_showscale=False)

    return apply_modern_dark_layout(
        figure,
        height=460,
        xaxis_title="Callbacks",
        yaxis_title="Fault Family",
    )


def build_fault_code_volume_chart(fault_code_summary: pd.DataFrame):
    """Build actual fault-code callback volume chart."""
    required_columns = {"fault_code_display", "fault_code_name", "callbacks"}
    if fault_code_summary.empty or not required_columns.issubset(
        fault_code_summary.columns
    ):
        return build_empty_chart("No fault-code volume data available.", height=620)

    chart_data = (
        fault_code_summary.sort_values("callbacks", ascending=False)
        .head(20)
        .sort_values("callbacks", ascending=True)
        .copy()
    )

    chart_data["fault_code_label"] = (
        chart_data["fault_code_display"].astype(str)
        + " - "
        + chart_data["fault_code_name"].astype(str)
    )

    figure = px.bar(
        chart_data,
        x="callbacks",
        y="fault_code_label",
        orientation="h",
        title="Top Actual Fault Codes by Callback Volume",
        hover_data=[
            "fault_family_final",
            "mantraps",
            "mantrap_rate_pct",
            "unique_accounts",
            "unique_equipment",
            "median_response_minutes",
            "median_repair_minutes",
        ],
        color="callbacks",
        color_continuous_scale=[
            "#1E293B",
            "#2563EB",
            "#2DD4BF",
        ],
    )

    figure.update_traces(marker_line_width=0, opacity=0.96)
    figure.update_layout(coloraxis_showscale=False)

    return apply_modern_dark_layout(
        figure,
        height=620,
        xaxis_title="Callbacks",
        yaxis_title="",
    )


def build_fault_code_mantrap_chart(fault_code_summary: pd.DataFrame):
    """Build actual fault-code mantrap volume chart."""
    required_columns = {"fault_code_display", "fault_code_name", "mantraps"}
    if fault_code_summary.empty or not required_columns.issubset(
        fault_code_summary.columns
    ):
        return build_empty_chart("No fault-code mantrap data available.", height=620)

    chart_data = (
        fault_code_summary.sort_values("mantraps", ascending=False)
        .head(20)
        .sort_values("mantraps", ascending=True)
        .copy()
    )

    chart_data["fault_code_label"] = (
        chart_data["fault_code_display"].astype(str)
        + " - "
        + chart_data["fault_code_name"].astype(str)
    )

    figure = px.bar(
        chart_data,
        x="mantraps",
        y="fault_code_label",
        orientation="h",
        title="Top Actual Fault Codes by Mantrap Volume",
        hover_data=[
            "fault_family_final",
            "callbacks",
            "mantrap_rate_pct",
            "unique_accounts",
            "unique_equipment",
            "median_response_minutes",
            "median_repair_minutes",
        ],
        color="mantraps",
        color_continuous_scale=[
            "#1E293B",
            "#FDBA74",
            "#FB7185",
        ],
    )

    figure.update_traces(marker_line_width=0, opacity=0.96)
    figure.update_layout(coloraxis_showscale=False)

    return apply_modern_dark_layout(
        figure,
        height=620,
        xaxis_title="Mantraps",
        yaxis_title="",
    )


def build_fault_code_trend_chart(
    monthly_fault_code_trend: pd.DataFrame,
    selected_fault_codes: list[str],
):
    """Build monthly trend for selected actual fault codes."""
    required_columns = {"event_month", "fault_code_display", "callbacks"}
    if monthly_fault_code_trend.empty or not required_columns.issubset(
        monthly_fault_code_trend.columns
    ):
        return build_empty_chart("No fault-code trend data available.", height=520)

    trend = monthly_fault_code_trend[
        monthly_fault_code_trend["fault_code_display"].isin(selected_fault_codes)
    ].copy()

    trend = prepare_month_label(trend)

    if trend.empty:
        figure = go.Figure()
        figure.add_annotation(
            text="No data available for selected fault codes.",
            showarrow=False,
            font={"color": TEXT_MUTED, "size": 14},
        )
    elif trend["event_month"].nunique() <= 1:
        figure = px.bar(
            trend,
            x="fault_code_display",
            y="callbacks",
            title="Selected Fault Code Volume",
            color="fault_code_display",
            color_discrete_sequence=CHART_COLOR_SEQUENCE,
        )
        figure.update_traces(marker_line_width=0, opacity=0.95)
    else:
        figure = build_smooth_line_chart(
            dataframe=trend,
            x_column="event_month",
            y_column="callbacks",
            color_column="fault_code_display",
            title="Monthly Actual Fault Code Trend",
            colors=CHART_COLOR_SEQUENCE,
        )

    return apply_modern_dark_layout(
        figure,
        height=520,
        xaxis_title="Month",
        yaxis_title="Callbacks",
        force_category_xaxis=True,
    )
