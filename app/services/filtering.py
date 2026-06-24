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


def prepare_silver_callbacks_for_dashboard(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Prepare silver callback data after loading from CSV.

    CSV loading can convert datetime and boolean columns into strings.
    This function restores the types needed by dashboard filtering and metrics.
    """
    prepared = dataframe.copy()

    datetime_columns = [
        "event_datetime",
        "attended_datetime",
        "completed_datetime",
        "event_date",
        "event_month",
        "event_year",
        "source_file_modified_at",
    ]

    for column in datetime_columns:
        if column in prepared.columns:
            prepared[column] = pd.to_datetime(
                prepared[column],
                errors="coerce",
            )

    if "mantrap_flag" in prepared.columns:
        prepared["mantrap_flag"] = (
            prepared["mantrap_flag"]
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

    return prepared
