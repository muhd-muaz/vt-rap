from __future__ import annotations

import pandas as pd


def format_table_for_display(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return a display-safe copy with rounded numeric columns."""
    display_dataframe = dataframe.copy()

    for column_name in display_dataframe.select_dtypes(include=["float"]).columns:
        display_dataframe[column_name] = display_dataframe[column_name].round(2)

    return display_dataframe
