from __future__ import annotations

import calendar
from datetime import date

import pandas as pd
import streamlit as st

from src.pipeline.build_gold import build_gold_tables


DATETIME_COLUMNS = [
    "Created",
    "event_at",
    "attended_at",
    "completed_at",
    "Start date + time (Realised)",
    "Start date + time",
    "End date + time",
]


def prepare_silver_callbacks_for_dashboard(
    silver_callbacks: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare silver callback data loaded from CSV for dashboard filtering."""
    prepared = silver_callbacks.copy()

    for column_name in DATETIME_COLUMNS:
        if column_name in prepared.columns:
            prepared[column_name] = pd.to_datetime(
                prepared[column_name],
                errors="coerce",
            )

    return prepared


def get_available_years(silver_callbacks: pd.DataFrame) -> list[int]:
    """Return available event years."""
    return (
        silver_callbacks["event_at"]
        .dropna()
        .dt.year
        .astype(int)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )


def get_available_months_for_year(
    silver_callbacks: pd.DataFrame,
    selected_year: int,
) -> list[int]:
    """Return available event months for a selected year."""
    return (
        silver_callbacks.loc[
            silver_callbacks["event_at"].dt.year.eq(selected_year),
            "event_at",
        ]
        .dropna()
        .dt.month
        .astype(int)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )


def filter_silver_callbacks_by_period(
    silver_callbacks: pd.DataFrame,
    filter_mode: str,
    selected_year: int | None,
    selected_month: int | None,
    start_date: date | None,
    end_date: date | None,
) -> pd.DataFrame:
    """Filter silver callbacks by selected dashboard period."""
    if filter_mode == "All Time":
        return silver_callbacks.copy()

    if filter_mode == "Year" and selected_year is not None:
        return silver_callbacks[
            silver_callbacks["event_at"].dt.year.eq(selected_year)
        ].copy()

    if (
        filter_mode == "Month"
        and selected_year is not None
        and selected_month is not None
    ):
        return silver_callbacks[
            silver_callbacks["event_at"].dt.year.eq(selected_year)
            & silver_callbacks["event_at"].dt.month.eq(selected_month)
        ].copy()

    if filter_mode == "Custom Range" and start_date is not None and end_date is not None:
        start_timestamp = pd.Timestamp(start_date)
        end_timestamp = pd.Timestamp(end_date) + pd.Timedelta(days=1)

        return silver_callbacks[
            silver_callbacks["event_at"].ge(start_timestamp)
            & silver_callbacks["event_at"].lt(end_timestamp)
        ].copy()

    return silver_callbacks.copy()


def build_period_label(
    filter_mode: str,
    selected_year: int | None,
    selected_month: int | None,
    start_date: date | None,
    end_date: date | None,
) -> str:
    """Build human-readable selected period label."""
    if filter_mode == "All Time":
        return "All time"

    if filter_mode == "Year" and selected_year is not None:
        return str(selected_year)

    if filter_mode == "Month" and selected_year is not None and selected_month is not None:
        return f"{calendar.month_name[selected_month]} {selected_year}"

    if filter_mode == "Custom Range" and start_date is not None and end_date is not None:
        return f"{start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}"

    return "All time"


def render_period_summary_cards(period_context: dict) -> None:
    """Render compact selected-period summary cards."""
    card_1, card_2, card_3, card_4 = st.columns(4)

    with card_1:
        st.markdown(
            f"""
            <div class="period-card">
                <div class="period-card-label">Current View</div>
                <div class="period-card-value">{period_context["period_label"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with card_2:
        st.markdown(
            f"""
            <div class="period-card">
                <div class="period-card-label">Filtered Rows</div>
                <div class="period-card-value">{period_context["filtered_rows"]:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with card_3:
        st.markdown(
            f"""
            <div class="period-card">
                <div class="period-card-label">Completed / Verified</div>
                <div class="period-card-value">{period_context["completed_or_verified_rows"]:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with card_4:
        st.markdown(
            f"""
            <div class="period-card">
                <div class="period-card-label">Mantraps</div>
                <div class="period-card-value">{period_context["mantraps"]:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_period_filter(
    silver_callbacks: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Render global period filter and return filtered silver callbacks."""
    prepared_callbacks = prepare_silver_callbacks_for_dashboard(silver_callbacks)
    available_years = get_available_years(prepared_callbacks)

    if not available_years:
        return prepared_callbacks, {
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

    min_event_date = prepared_callbacks["event_at"].min().date()
    max_event_date = prepared_callbacks["event_at"].max().date()

    st.markdown(
        """
        <div class="period-panel">
            <div class="period-panel-title">Analysis Period</div>
            <div class="period-panel-subtitle">
                Filter the entire dashboard by all time, year, month, or custom date range.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filter_mode = st.segmented_control(
        "Period mode",
        options=["All Time", "Year", "Month", "Custom Range"],
        default="All Time",
        key="global_period_filter_mode",
        label_visibility="collapsed",
    )

    selected_year = None
    selected_month = None
    start_date = None
    end_date = None

    if filter_mode == "Year":
        selected_year = st.selectbox(
            "Select year",
            options=available_years,
            index=len(available_years) - 1,
            key="global_period_year",
        )

    elif filter_mode == "Month":
        filter_col_1, filter_col_2 = st.columns(2)

        with filter_col_1:
            selected_year = st.selectbox(
                "Select year",
                options=available_years,
                index=len(available_years) - 1,
                key="global_period_month_year",
            )

        available_months = get_available_months_for_year(
            prepared_callbacks,
            selected_year,
        )

        month_options = {
            calendar.month_name[month_number]: month_number
            for month_number in available_months
        }

        with filter_col_2:
            selected_month_name = st.selectbox(
                "Select month",
                options=list(month_options.keys()),
                index=0,
                key="global_period_month",
            )

        selected_month = month_options[selected_month_name]

    elif filter_mode == "Custom Range":
        filter_col_1, filter_col_2 = st.columns(2)

        with filter_col_1:
            start_date = st.date_input(
                "Start date",
                value=min_event_date,
                min_value=min_event_date,
                max_value=max_event_date,
                key="global_period_start_date",
            )

        with filter_col_2:
            end_date = st.date_input(
                "End date",
                value=max_event_date,
                min_value=min_event_date,
                max_value=max_event_date,
                key="global_period_end_date",
            )

        if start_date > end_date:
            st.warning("Start date cannot be after end date. Showing all time instead.")
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
        filtered_callbacks["analysis_status_group"]
        .eq("completed_or_verified")
        .sum()
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

    render_period_summary_cards(context)

    return filtered_callbacks, context

def build_filtered_dashboard_tables(
    filtered_silver_callbacks: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Build dashboard gold tables from the selected filtered period."""
    return build_gold_tables(filtered_silver_callbacks)