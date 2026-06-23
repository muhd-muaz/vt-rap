from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st


def dataframe_to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
    """Convert a DataFrame to UTF-8 CSV bytes."""
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def safe_export_filename(name: str) -> str:
    """Create a timestamped CSV export filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = (
        name.strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace("-", "_")
    )

    return f"{safe_name}_{timestamp}.csv"


def render_csv_download_button(
    dataframe: pd.DataFrame,
    filename_prefix: str,
    label: str = "Download CSV",
    key: str | None = None,
) -> None:
    """Render a CSV download button for a DataFrame."""
    if dataframe.empty:
        st.caption("No rows available for download.")
        return

    st.download_button(
        label=label,
        data=dataframe_to_csv_bytes(dataframe),
        file_name=safe_export_filename(filename_prefix),
        mime="text/csv",
        key=key,
    )
