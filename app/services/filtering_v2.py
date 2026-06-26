from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from services.filtering import (
    build_period_label,
    filter_silver_callbacks_by_period,
    prepare_silver_callbacks_for_dashboard,
)

DATE_COLUMN_CANDIDATES = [
    "event_at",
    "event_datetime",
    "event_date",
    "Event Date",
    "event created date",
    "Event Created Date",
    "callback_date",
    "Callback Date",
    "breakdown_date",
    "Breakdown Date",
]


def ensure_event_at_for_filtering(callbacks: pd.DataFrame) -> pd.DataFrame:
    """Ensure a usable event_at column exists for dashboard period filtering."""
    prepared = callbacks.copy()

    if "event_at" in prepared.columns:
        prepared["event_at"] = pd.to_datetime(
            prepared["event_at"],
            errors="coerce",
            dayfirst=True,
        )

        if prepared["event_at"].notna().any():
            return prepared

    for column in DATE_COLUMN_CANDIDATES:
        if column not in prepared.columns:
            continue

        parsed_dates = pd.to_datetime(
            prepared[column],
            errors="coerce",
            dayfirst=True,
        )

        if parsed_dates.notna().any():
            prepared["event_at"] = parsed_dates
            return prepared

    return prepared


def count_completed_or_verified(callbacks: pd.DataFrame) -> int:
    """Count completed or verified rows when the status column is available."""
    if callbacks.empty or "analysis_status_group" not in callbacks.columns:
        return 0

    return int(callbacks["analysis_status_group"].eq("completed_or_verified").sum())


def count_mantraps(callbacks: pd.DataFrame) -> int:
    """Count mantrap rows when the flag column is available."""
    if callbacks.empty or "mantrap_flag" not in callbacks.columns:
        return 0

    mantrap_flag = (
        callbacks["mantrap_flag"]
        .map(
            {
                True: True,
                False: False,
                "True": True,
                "False": False,
                "true": True,
                "false": False,
                "TRUE": True,
                "FALSE": False,
                "1": True,
                "0": False,
                1: True,
                0: False,
            }
        )
        .fillna(False)
        .astype(bool)
    )

    return int(mantrap_flag.sum())


def build_no_valid_dates_context(callbacks: pd.DataFrame) -> dict:
    """Build fallback period context when no usable event date exists."""
    return {
        "period_label": "No valid event dates",
        "filter_mode": "All Time",
        "selected_year": None,
        "selected_month": None,
        "start_date": None,
        "end_date": None,
        "filtered_rows": int(len(callbacks)),
        "completed_or_verified_rows": count_completed_or_verified(callbacks),
        "mantraps": count_mantraps(callbacks),
    }


def render_sidebar_period_filter_v2(
    silver_callbacks: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Render V2 period filter in the sidebar and return filtered callbacks."""
    prepared_callbacks = prepare_silver_callbacks_for_dashboard(silver_callbacks)
    prepared_callbacks = ensure_event_at_for_filtering(prepared_callbacks)

    st.sidebar.markdown(
        '<div class="v2-sidebar-section-label">Analysis Period</div>',
        unsafe_allow_html=True,
    )

    if "event_at" not in prepared_callbacks.columns:
        context = build_no_valid_dates_context(prepared_callbacks)
        st.sidebar.warning(
            "No event date column was found. Showing all available records without period filtering."
        )
        render_sidebar_period_summary_v2(context)
        return prepared_callbacks, context

    valid_event_dates = prepared_callbacks["event_at"].dropna()

    if valid_event_dates.empty:
        context = build_no_valid_dates_context(prepared_callbacks)
        st.sidebar.warning(
            "Event date column exists, but no valid dates could be parsed. Showing all available records without period filtering."
        )
        render_sidebar_period_summary_v2(context)
        return prepared_callbacks, context

    available_years = (
        prepared_callbacks["event_at"]
        .dropna()
        .dt.year.dropna()
        .astype(int)
        .unique()
        .tolist()
    )
    available_years = sorted(available_years)

    if not available_years:
        context = build_no_valid_dates_context(prepared_callbacks)
        st.sidebar.warning(
            "No valid analysis years found. Showing all available records without period filtering."
        )
        render_sidebar_period_summary_v2(context)
        return prepared_callbacks, context

    min_event_date = valid_event_dates.min().date()
    max_event_date = valid_event_dates.max().date()

    with st.sidebar.expander("Select analysis period", expanded=True):
        filter_mode = st.selectbox(
            "Period mode",
            options=["All Time", "Year", "Month", "Custom Range"],
            index=0,
            key="v2_period_filter_mode",
        )

        selected_year: int | None = None
        selected_month: int | None = None
        start_date: date | None = None
        end_date: date | None = None

        if filter_mode == "Year":
            selected_year = st.selectbox(
                "Year",
                options=available_years,
                index=len(available_years) - 1,
                key="v2_period_year",
            )

        elif filter_mode == "Month":
            selected_year = st.selectbox(
                "Year",
                options=available_years,
                index=len(available_years) - 1,
                key="v2_period_month_year",
            )

            available_months = (
                prepared_callbacks.loc[
                    prepared_callbacks["event_at"].dt.year.eq(selected_year),
                    "event_at",
                ]
                .dropna()
                .dt.month.dropna()
                .astype(int)
                .unique()
                .tolist()
            )
            available_months = sorted(available_months)

            month_options = {
                month_number: pd.Timestamp(
                    year=selected_year,
                    month=month_number,
                    day=1,
                ).strftime("%B")
                for month_number in available_months
            }

            selected_month = st.selectbox(
                "Month",
                options=list(month_options.keys()),
                format_func=lambda month_number: month_options[month_number],
                index=0,
                key="v2_period_month",
            )

        elif filter_mode == "Custom Range":
            start_date = st.date_input(
                "Start date",
                value=min_event_date,
                min_value=min_event_date,
                max_value=max_event_date,
                key="v2_period_start_date",
            )

            end_date = st.date_input(
                "End date",
                value=max_event_date,
                min_value=min_event_date,
                max_value=max_event_date,
                key="v2_period_end_date",
            )

            if start_date > end_date:
                st.warning("Start date cannot be after end date. Showing all time.")
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

    context = {
        "period_label": period_label,
        "filter_mode": filter_mode,
        "selected_year": selected_year,
        "selected_month": selected_month,
        "start_date": start_date,
        "end_date": end_date,
        "filtered_rows": int(len(filtered_callbacks)),
        "completed_or_verified_rows": count_completed_or_verified(filtered_callbacks),
        "mantraps": count_mantraps(filtered_callbacks),
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
