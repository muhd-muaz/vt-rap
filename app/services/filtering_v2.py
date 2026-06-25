from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from services.filtering import (
    build_period_label,
    filter_silver_callbacks_by_period,
    get_available_months_for_year,
    get_available_years,
    prepare_silver_callbacks_for_dashboard,
)


def render_sidebar_period_filter_v2(
    silver_callbacks: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Render V2 period filter in the sidebar and return filtered callbacks."""
    prepared_callbacks = prepare_silver_callbacks_for_dashboard(silver_callbacks)
    available_years = get_available_years(prepared_callbacks)

    if not available_years:
        context = {
            "period_label": "No valid event dates",
            "filter_mode": "All Time",
            "selected_year": None,
            "selected_month": None,
            "start_date": None,
            "end_date": None,
            "filtered_rows": len(prepared_callbacks),
            "completed_or_verified_rows": 0,
            "mantraps": 0,
        }
        return prepared_callbacks, context

    min_event_date = prepared_callbacks["event_at"].min().date()
    max_event_date = prepared_callbacks["event_at"].max().date()

    st.sidebar.markdown(
        '<div class="v2-sidebar-section-label">Analysis Period</div>',
        unsafe_allow_html=True,
    )

    filter_mode = st.sidebar.radio(
        "Period mode",
        options=["All Time", "Year", "Month", "Custom Range"],
        index=0,
        key="v2_period_filter_mode",
        label_visibility="collapsed",
    )

    selected_year: int | None = None
    selected_month: int | None = None
    start_date: date | None = None
    end_date: date | None = None

    if filter_mode == "Year":
        selected_year = st.sidebar.selectbox(
            "Year",
            options=available_years,
            index=len(available_years) - 1,
            key="v2_period_year",
        )

    elif filter_mode == "Month":
        selected_year = st.sidebar.selectbox(
            "Year",
            options=available_years,
            index=len(available_years) - 1,
            key="v2_period_month_year",
        )

        available_months = get_available_months_for_year(
            prepared_callbacks,
            selected_year,
        )

        month_options = {
            month_number: pd.Timestamp(
                year=selected_year,
                month=month_number,
                day=1,
            ).strftime("%B")
            for month_number in available_months
        }

        selected_month = st.sidebar.selectbox(
            "Month",
            options=list(month_options.keys()),
            format_func=lambda month_number: month_options[month_number],
            index=0,
            key="v2_period_month",
        )

    elif filter_mode == "Custom Range":
        start_date = st.sidebar.date_input(
            "Start date",
            value=min_event_date,
            min_value=min_event_date,
            max_value=max_event_date,
            key="v2_period_start_date",
        )

        end_date = st.sidebar.date_input(
            "End date",
            value=max_event_date,
            min_value=min_event_date,
            max_value=max_event_date,
            key="v2_period_end_date",
        )

        if start_date > end_date:
            st.sidebar.warning("Start date cannot be after end date. Showing all time.")
            filter_mode = "All Time"
            start_date = None
            end_date = None

    filtered_callbacks = filter_silver_callbacks_by_period(
        silver_callbacks=prepared_callbacks,
        filter_mode=filter_mode,
        selected_year=selected_year,
        selected_month=selected_month,
        start_date=start_date,
        end_date=end_date,
    )

    period_label = build_period_label(
        filter_mode=filter_mode,
        selected_year=selected_year,
        selected_month=selected_month,
        start_date=start_date,
        end_date=end_date,
    )

    completed_or_verified_rows = int(
        filtered_callbacks["analysis_status_group"].eq("completed_or_verified").sum()
    )

    mantraps = int(filtered_callbacks["mantrap_flag"].sum())

    context = {
        "period_label": period_label,
        "filter_mode": filter_mode,
        "selected_year": selected_year,
        "selected_month": selected_month,
        "start_date": start_date,
        "end_date": end_date,
        "filtered_rows": int(len(filtered_callbacks)),
        "completed_or_verified_rows": completed_or_verified_rows,
        "mantraps": mantraps,
    }

    render_sidebar_period_summary_v2(context)

    return filtered_callbacks, context


def render_sidebar_period_summary_v2(period_context: dict) -> None:
    """Render compact V2 sidebar period summary."""
    st.sidebar.markdown(
        f"""
        <div class="v2-sidebar-status-card">
            <div class="v2-sidebar-section-label">Current View</div>
            <div class="v2-filter-summary-row">
                <span>Period</span>
                <strong>{period_context["period_label"]}</strong>
            </div>
            <div class="v2-filter-summary-row">
                <span>Rows</span>
                <strong>{period_context["filtered_rows"]:,}</strong>
            </div>
            <div class="v2-filter-summary-row">
                <span>Completed / Verified</span>
                <strong>{period_context["completed_or_verified_rows"]:,}</strong>
            </div>
            <div class="v2-filter-summary-row">
                <span>Mantraps</span>
                <strong>{period_context["mantraps"]:,}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
