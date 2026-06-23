from __future__ import annotations

import pandas as pd
import streamlit as st


def build_equipment_risk_filters(equipment_risk_model: pd.DataFrame) -> pd.DataFrame:
    """Render equipment risk filters and return filtered equipment risk data."""
    with st.expander("Equipment Risk Filters", expanded=True):
        risk_tiers = (
            equipment_risk_model["risk_tier"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        tier_order = ["Critical", "High", "Medium", "Low"]
        risk_tiers = [tier for tier in tier_order if tier in risk_tiers]

        filter_1, filter_2 = st.columns(2)

        with filter_1:
            selected_risk_tiers = st.multiselect(
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

        with filter_2:
            selected_equipment_types = st.multiselect(
                "Equipment type",
                options=equipment_types,
                default=equipment_types,
            )

        filter_3, filter_4 = st.columns(2)

        with filter_3:
            minimum_callbacks = st.slider(
                "Minimum callbacks",
                min_value=0,
                max_value=int(equipment_risk_model["callbacks"].max()),
                value=0,
            )

        with filter_4:
            minimum_mantraps = st.slider(
                "Minimum mantraps",
                min_value=0,
                max_value=int(equipment_risk_model["mantraps"].max()),
                value=0,
            )

    filtered = equipment_risk_model[
        equipment_risk_model["risk_tier"].astype(str).isin(selected_risk_tiers)
        & equipment_risk_model["equipment_type"]
        .astype(str)
        .isin(selected_equipment_types)
        & (equipment_risk_model["callbacks"] >= minimum_callbacks)
        & (equipment_risk_model["mantraps"] >= minimum_mantraps)
    ].copy()

    return filtered