from __future__ import annotations

import pandas as pd
import streamlit as st

from components.tables import format_table_for_display


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