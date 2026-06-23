from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
STYLE_PATH = PROJECT_ROOT / "app" / "styles" / "theme.css"


def load_css() -> None:
    """Load local CSS theme."""
    if STYLE_PATH.exists():
        st.markdown(
            f"<style>{STYLE_PATH.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


@st.cache_data
def load_processed_table(file_name: str) -> pd.DataFrame:
    """Load a processed CSV table."""
    file_path = PROCESSED_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing processed file: {file_path}. "
            "Run `python scripts/run_pipeline.py` first."
        )

    return pd.read_csv(file_path)


def get_summary_value(summary: pd.DataFrame, metric_name: str) -> str:
    """Return a metric value from the executive summary table."""
    matched_rows = summary.loc[summary["metric"].eq(metric_name), "value"]

    if matched_rows.empty:
        return "-"

    value = matched_rows.iloc[0]

    try:
        numeric_value = float(value)

        if numeric_value.is_integer():
            return f"{int(numeric_value):,}"

        return f"{numeric_value:,.2f}"

    except (TypeError, ValueError):
        return str(value)


def render_command_card(title: str, value: str, caption: str = "") -> None:
    """Render a styled command-center card."""
    st.markdown(
        f"""
        <div class="command-card">
            <div class="command-card-title">{title}</div>
            <div class="command-card-value">{value}</div>
            <div class="command-card-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_table_for_display(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return a display-safe copy with rounded numeric columns."""
    display_dataframe = dataframe.copy()

    for column_name in display_dataframe.select_dtypes(include=["float"]).columns:
        display_dataframe[column_name] = display_dataframe[column_name].round(2)

    return display_dataframe


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

    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f8fafc"},
        xaxis_title="Month",
        yaxis_title="Count",
        height=430,
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
    )

    return figure


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

    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f8fafc"},
        xaxis_title="Month",
        yaxis_title="Minutes",
        height=430,
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
    )

    return figure


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

    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f8fafc"},
        title={"font": {"size": 20}},
        xaxis_title="Callbacks",
        yaxis_title="",
        height=480,
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
    )

    return figure


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

    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f8fafc"},
        xaxis_title="Month",
        yaxis_title="Callbacks",
        height=520,
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
    )

    return figure


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

    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f8fafc"},
        xaxis_title="Month",
        yaxis_title="Callbacks",
        height=520,
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
    )

    return figure


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

    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f8fafc"},
        xaxis_title="Risk Score",
        yaxis_title="",
        height=520,
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
    )

    return figure


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

    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f8fafc"},
        xaxis_title="Month",
        yaxis_title="Count",
        height=460,
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
    )

    return figure


def build_equipment_risk_filters(equipment_risk_model: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filters and return filtered equipment risk data."""
    st.sidebar.header("Risk Filters")

    risk_tiers = (
        equipment_risk_model["risk_tier"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    tier_order = ["Critical", "High", "Medium", "Low"]
    risk_tiers = [tier for tier in tier_order if tier in risk_tiers]

    selected_risk_tiers = st.sidebar.multiselect(
        "Risk tier",
        options=risk_tiers,
        default=risk_tiers,
    )

    equipment_types = (
        equipment_risk_model["equipment_type"]
        .dropna()
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    selected_equipment_types = st.sidebar.multiselect(
        "Equipment type",
        options=equipment_types,
        default=equipment_types,
    )

    minimum_callbacks = st.sidebar.slider(
        "Minimum callbacks",
        min_value=0,
        max_value=int(equipment_risk_model["callbacks"].max()),
        value=0,
    )

    minimum_mantraps = st.sidebar.slider(
        "Minimum mantraps",
        min_value=0,
        max_value=int(equipment_risk_model["mantraps"].max()),
        value=0,
    )

    filtered = equipment_risk_model[
        equipment_risk_model["risk_tier"].astype(str).isin(selected_risk_tiers)
        & equipment_risk_model["equipment_type"].astype(str).isin(selected_equipment_types)
        & (equipment_risk_model["callbacks"] >= minimum_callbacks)
        & (equipment_risk_model["mantraps"] >= minimum_mantraps)
    ].copy()

    return filtered


def render_executive_overview(
    executive_summary: pd.DataFrame,
    fault_family_summary: pd.DataFrame,
    equipment_risk_model: pd.DataFrame,
    account_risk_model: pd.DataFrame,
    emerging_equipment_alerts: pd.DataFrame,
    monthly_callback_trend: pd.DataFrame,
) -> None:
    """Render executive overview tab."""
    st.subheader("Executive Overview")

    kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)

    with kpi_1:
        render_command_card(
            "Completed / Verified Callbacks",
            get_summary_value(executive_summary, "Completed / verified callbacks"),
            "Clean operational records used for management analytics.",
        )

    with kpi_2:
        render_command_card(
            "Total Mantraps",
            get_summary_value(executive_summary, "Total mantraps"),
            "Trapped-passenger related callback events.",
        )

    with kpi_3:
        render_command_card(
            "Median Response",
            f"{get_summary_value(executive_summary, 'Median response minutes')} min",
            "Median time from realised event to attendance.",
        )

    with kpi_4:
        render_command_card(
            "Median Repair",
            f"{get_summary_value(executive_summary, 'Median repair minutes')} min",
            "Median time from attendance to completion.",
        )

    risk_1, risk_2, risk_3, risk_4 = st.columns(4)

    critical_count = int(
        equipment_risk_model["risk_tier"].astype(str).eq("Critical").sum()
    )
    high_count = int(
        equipment_risk_model["risk_tier"].astype(str).eq("High").sum()
    )
    emerging_count = len(emerging_equipment_alerts)
    unclassified_count = int(
        fault_family_summary.loc[
            fault_family_summary["fault_family_final"].eq("Unclassified"),
            "callbacks",
        ].sum()
    )

    with risk_1:
        render_command_card(
            "Critical Equipment",
            f"{critical_count:,}",
            "Established assets with the highest risk scores.",
        )

    with risk_2:
        render_command_card(
            "High-Risk Equipment",
            f"{high_count:,}",
            "Assets requiring operational monitoring.",
        )

    with risk_3:
        render_command_card(
            "Emerging Alerts",
            f"{emerging_count:,}",
            "Low-history assets with early mantrap signals.",
        )

    with risk_4:
        render_command_card(
            "Unclassified Faults",
            f"{unclassified_count:,}",
            "Callbacks without mapped recorded fault code.",
        )

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.plotly_chart(
            build_monthly_callback_chart(monthly_callback_trend),
            use_container_width=True,
            key="overview_monthly_callback_chart",
        )

    with chart_right:
        st.plotly_chart(
            build_monthly_response_repair_chart(monthly_callback_trend),
            use_container_width=True,
            key="overview_monthly_response_repair_chart",
        )

    st.plotly_chart(
        build_fault_family_chart(fault_family_summary),
        use_container_width=True,
        key="overview_fault_family_chart",
    )

    left_column, right_column = st.columns(2)

    with left_column:
        st.markdown("### Top Equipment Risk")
        equipment_columns = [
            "equipment_description_raw",
            "account_name_raw",
            "equipment_type",
            "callbacks",
            "mantraps",
            "callbacks_last_365_days",
            "mantraps_last_365_days",
            "equipment_risk_score_v3",
            "risk_tier",
            "primary_risk_driver",
        ]

        st.dataframe(
            format_table_for_display(equipment_risk_model[equipment_columns].head(15)),
            use_container_width=True,
            hide_index=True,
        )

    with right_column:
        st.markdown("### Top Account Risk")
        st.plotly_chart(
            build_top_account_chart(account_risk_model),
            use_container_width=True,
            key="overview_top_account_chart",
        )


def render_equipment_risk(equipment_risk_model: pd.DataFrame) -> None:
    """Render equipment risk tab."""
    st.subheader("Equipment Risk Command View")

    filtered_equipment = build_equipment_risk_filters(equipment_risk_model)

    st.caption(
        f"Showing {len(filtered_equipment):,} equipment records after filters."
    )

    table_columns = [
        "equipment_description_raw",
        "account_name_raw",
        "equipment_type",
        "callbacks",
        "mantraps",
        "mantrap_rate_pct",
        "callbacks_last_365_days",
        "mantraps_last_365_days",
        "equipment_risk_score_v3",
        "risk_tier",
        "risk_signal_type",
        "primary_risk_driver",
        "risk_explanation",
    ]

    st.dataframe(
        format_table_for_display(filtered_equipment[table_columns].head(200)),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Equipment Detail Drilldown")

    selected_equipment = st.selectbox(
        "Select equipment",
        options=filtered_equipment["equipment_description_raw"].head(300).tolist(),
    )

    selected_row = filtered_equipment[
        filtered_equipment["equipment_description_raw"].eq(selected_equipment)
    ].iloc[0]

    detail_1, detail_2, detail_3, detail_4 = st.columns(4)

    with detail_1:
        render_command_card(
            "Callbacks",
            f"{int(selected_row['callbacks']):,}",
            "Total completed/verified callbacks.",
        )

    with detail_2:
        render_command_card(
            "Mantraps",
            f"{int(selected_row['mantraps']):,}",
            "Total mantrap events.",
        )

    with detail_3:
        render_command_card(
            "Risk Score",
            f"{float(selected_row['equipment_risk_score_v3']):.2f}",
            str(selected_row["risk_tier"]),
        )

    with detail_4:
        render_command_card(
            "Primary Driver",
            str(selected_row["primary_risk_driver"]),
            "Strongest component in the risk score.",
        )

    st.info(str(selected_row["risk_explanation"]))


def render_account_risk(
    account_risk_model: pd.DataFrame,
    monthly_account_trend: pd.DataFrame,
) -> None:
    """Render account risk tab."""
    st.subheader("Account Risk Command View")

    table_columns = [
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

    st.dataframe(
        format_table_for_display(account_risk_model[table_columns].head(200)),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Account Detail Trend")

    selected_account = st.selectbox(
        "Select account",
        options=account_risk_model["account_name_raw"].head(200).tolist(),
    )

    selected_row = account_risk_model[
        account_risk_model["account_name_raw"].eq(selected_account)
    ].iloc[0]

    account_1, account_2, account_3, account_4 = st.columns(4)

    with account_1:
        render_command_card(
            "Callbacks",
            f"{int(selected_row['callbacks']):,}",
            "Total completed/verified callbacks.",
        )

    with account_2:
        render_command_card(
            "Mantraps",
            f"{int(selected_row['mantraps']):,}",
            "Total mantrap events.",
        )

    with account_3:
        render_command_card(
            "Equipment",
            f"{int(selected_row['unique_equipment']):,}",
            "Unique equipment under account.",
        )

    with account_4:
        render_command_card(
            "Risk Score",
            f"{float(selected_row['account_risk_score']):.2f}",
            str(selected_row["risk_tier"]),
        )

    st.info(str(selected_row["risk_explanation"]))

    st.plotly_chart(
        build_account_monthly_chart(monthly_account_trend, selected_account),
        use_container_width=True,
        key="account_detail_monthly_chart",
    )


def render_fault_analysis(
    fault_family_summary: pd.DataFrame,
    monthly_fault_family_trend: pd.DataFrame,
    monthly_equipment_type_trend: pd.DataFrame,
) -> None:
    """Render fault analysis tab."""
    st.subheader("Fault Family Analysis")

    st.plotly_chart(
        build_fault_family_chart(fault_family_summary),
        use_container_width=True,
        key="fault_analysis_fault_family_chart",
    )

    fault_family_options = (
        fault_family_summary["fault_family_final"].dropna().astype(str).tolist()
    )

    default_families = fault_family_options[:6]

    selected_fault_families = st.multiselect(
        "Select fault families for monthly trend",
        options=fault_family_options,
        default=default_families,
    )

    st.plotly_chart(
        build_fault_family_trend_chart(
            monthly_fault_family_trend,
            selected_fault_families,
        ),
        use_container_width=True,
        key="fault_family_monthly_trend_chart",
    )

    st.plotly_chart(
        build_equipment_type_trend_chart(monthly_equipment_type_trend),
        use_container_width=True,
        key="equipment_type_monthly_trend_chart",
    )

    table_columns = [
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

    st.dataframe(
        format_table_for_display(fault_family_summary[table_columns]),
        use_container_width=True,
        hide_index=True,
    )


def render_emerging_alerts(emerging_equipment_alerts: pd.DataFrame) -> None:
    """Render emerging alerts tab."""
    st.subheader("Emerging Equipment Alerts")

    st.caption(
        "Low-history equipment with early serious mantrap signals. "
        "These are not established risks yet and should be reviewed separately."
    )

    table_columns = [
        "equipment_description_raw",
        "account_name_raw",
        "equipment_type",
        "callbacks",
        "mantraps",
        "mantrap_rate_pct",
        "median_response_minutes",
        "median_repair_minutes",
        "risk_signal_type",
        "risk_explanation",
    ]

    st.dataframe(
        format_table_for_display(emerging_equipment_alerts[table_columns].head(200)),
        use_container_width=True,
        hide_index=True,
    )


def render_data_quality(data_quality_summary: pd.DataFrame) -> None:
    """Render data quality tab."""
    st.subheader("Data Quality Summary")

    st.caption(
        "This page shows whether the analytics output is based on reliable and complete source data."
    )

    st.dataframe(
        format_table_for_display(data_quality_summary),
        use_container_width=True,
        hide_index=True,
    )


def main() -> None:
    """Run VT-RAP Streamlit dashboard."""
    st.set_page_config(
        page_title="VT-RAP Command Center",
        layout="wide",
    )

    load_css()

    st.title("VT-RAP Command Center")
    st.caption("Vertical Transport Reliability Analytics Platform")

    executive_summary = load_processed_table("executive_summary.csv")
    fault_family_summary = load_processed_table("fault_family_summary.csv")
    equipment_risk_model = load_processed_table("equipment_risk_model.csv")
    account_risk_model = load_processed_table("account_risk_model.csv")
    emerging_equipment_alerts = load_processed_table("emerging_equipment_alerts.csv")
    data_quality_summary = load_processed_table("data_quality_summary.csv")
    monthly_callback_trend = load_processed_table("monthly_callback_trend.csv")
    monthly_fault_family_trend = load_processed_table("monthly_fault_family_trend.csv")
    monthly_equipment_type_trend = load_processed_table(
        "monthly_equipment_type_trend.csv"
    )
    monthly_account_trend = load_processed_table("monthly_account_trend.csv")

    overview_tab, equipment_tab, account_tab, fault_tab, emerging_tab, quality_tab = st.tabs(
        [
            "Executive Overview",
            "Equipment Risk",
            "Account Risk",
            "Fault Analysis",
            "Emerging Alerts",
            "Data Quality",
        ]
    )

    with overview_tab:
        render_executive_overview(
            executive_summary=executive_summary,
            fault_family_summary=fault_family_summary,
            equipment_risk_model=equipment_risk_model,
            account_risk_model=account_risk_model,
            emerging_equipment_alerts=emerging_equipment_alerts,
            monthly_callback_trend=monthly_callback_trend,
        )

    with equipment_tab:
        render_equipment_risk(equipment_risk_model)

    with account_tab:
        render_account_risk(
            account_risk_model=account_risk_model,
            monthly_account_trend=monthly_account_trend,
        )

    with fault_tab:
        render_fault_analysis(
            fault_family_summary=fault_family_summary,
            monthly_fault_family_trend=monthly_fault_family_trend,
            monthly_equipment_type_trend=monthly_equipment_type_trend,
        )

    with emerging_tab:
        render_emerging_alerts(emerging_equipment_alerts)

    with quality_tab:
        render_data_quality(data_quality_summary)


if __name__ == "__main__":
    main()