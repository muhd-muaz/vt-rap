from __future__ import annotations

import pandas as pd
import streamlit as st


def build_equipment_risk_filters(equipment_risk_model: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filters and return filtered equipment risk data."""
    st.sidebar.header("Risk Filters")

    risk_tiers = (
        equipment_risk_model["risk_tier"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    tier_order = ["Critical", "High", "Medium", "Low"]
    risk_tiers = [tier for tier in tier_order if tier in risk_tiers]

    selected_risk_tiers = st.sidebar.multiselect(
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

    selected_equipment_types = st.sidebar.multiselect(
        "Equipment type",
        options=equipment_types,
        default=equipment_types,
    )

    minimum_callbacks = st.sidebar.slider(
        "Minimum callbacks",
        min_value=0,
        max_value=int(equipment_risk_model["callbacks"].max()),
        value=0,
    )

    minimum_mantraps = st.sidebar.slider(
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