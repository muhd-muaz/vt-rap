from __future__ import annotations

import numpy as np
import pandas as pd


TIMESTAMP_COLUMNS = [
    "Created",
    "Start date + time (Realised)",
    "Start date + time",
    "End date + time",
]


def parse_datetime_series(series: pd.Series) -> pd.Series:
    """
    Parse CRM datetime values safely.

    The CRM exports mostly use ISO-like datetime strings after ingestion.
    Invalid or out-of-business-range dates are coerced to missing values.
    """
    text_values = (
        series.astype("string")
        .str.replace("\xa0", " ", regex=False)
        .str.strip()
        .replace("", pd.NA)
    )

    parsed = pd.to_datetime(
        text_values,
        errors="coerce",
    )

    valid_business_year_mask = parsed.dt.year.between(2020, 2035)

    parsed = parsed.where(valid_business_year_mask)

    return parsed


def parse_callback_timestamps(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Parse operational timestamp fields into datetime columns."""
    parsed = dataframe.copy()

    for column_name in TIMESTAMP_COLUMNS:
        parsed[column_name] = parse_datetime_series(parsed[column_name])

    return parsed


def add_time_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Create response, repair, and calendar features."""
    enriched = dataframe.copy()

    enriched["event_at"] = enriched["Start date + time (Realised)"]
    enriched["attended_at"] = enriched["Start date + time"]
    enriched["completed_at"] = enriched["End date + time"]

    enriched["response_minutes"] = (
        enriched["attended_at"] - enriched["event_at"]
    ).dt.total_seconds() / 60

    enriched["repair_minutes"] = (
        enriched["completed_at"] - enriched["attended_at"]
    ).dt.total_seconds() / 60

    enriched["total_job_minutes"] = (
        enriched["completed_at"] - enriched["event_at"]
    ).dt.total_seconds() / 60

    enriched["invalid_response_time_flag"] = enriched["response_minutes"] < 0
    enriched["invalid_repair_time_flag"] = enriched["repair_minutes"] < 0
    enriched["invalid_total_job_time_flag"] = enriched["total_job_minutes"] < 0

    enriched["valid_response_time_flag"] = (
        enriched["response_minutes"].notna()
        & (enriched["response_minutes"] >= 0)
        & (enriched["response_minutes"] <= 24 * 60)
    )

    enriched["valid_repair_time_flag"] = (
        enriched["repair_minutes"].notna()
        & (enriched["repair_minutes"] >= 0)
        & (enriched["repair_minutes"] <= 7 * 24 * 60)
    )

    enriched["valid_total_job_time_flag"] = (
        enriched["total_job_minutes"].notna()
        & (enriched["total_job_minutes"] >= 0)
        & (enriched["total_job_minutes"] <= 7 * 24 * 60)
    )

    enriched["valid_response_minutes"] = np.where(
        enriched["valid_response_time_flag"],
        enriched["response_minutes"],
        np.nan,
    )

    enriched["valid_repair_minutes"] = np.where(
        enriched["valid_repair_time_flag"],
        enriched["repair_minutes"],
        np.nan,
    )

    enriched["event_year"] = enriched["event_at"].dt.year
    enriched["event_month"] = enriched["event_at"].dt.to_period("M").astype("string")
    enriched["event_day_of_week"] = enriched["event_at"].dt.day_name()
    enriched["event_hour"] = enriched["event_at"].dt.hour

    enriched["after_hours_flag"] = (
        (enriched["event_hour"] < 8)
        | (enriched["event_hour"] >= 18)
    )

    enriched["data_entry_lag_days"] = (
        enriched["Created"] - enriched["event_at"].dt.normalize()
    ).dt.days

    return enriched