from __future__ import annotations

import pandas as pd
import streamlit as st

from components.tables import format_table_for_display


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