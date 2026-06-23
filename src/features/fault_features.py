from __future__ import annotations

import pandas as pd


FAULT_FAMILY_BY_CODE = {
    "2LDA": "Door System",
    "2CDS": "Door System",
    "2CDA": "Door System",
    "2CDL": "Door System",
    "2CLS": "Door System",
    "5D": "Contamination / Sill Obstruction",
    "5FC": "False Call / Running Normal",
    "6ROA": "False Call / Running Normal",
    "14ETC": "False Call / Running Normal",
    "3ID": "Inverter / Drive / Encoder",
    "4EN": "Inverter / Drive / Encoder",
    "3PCB": "Controller / Board / Relay",
    "3MB": "Controller / Board / Relay",
    "3CR": "Controller / Board / Relay",
    "3LC": "Controller / Board / Relay",
    "3SS": "Safety Circuit",
    "3SLB": "Safety Circuit",
    "3SC": "Safety Circuit",
    "5B": "Building / External",
    "5A": "Building / External",
    "5V": "Building / External",
    "5W": "Building / External",
    "7PB": "Button / Indicator",
    "7F": "Button / Indicator",
    "7L": "Button / Indicator",
    "10ETC": "Escalator / Travellator System",
    "11ETC": "Escalator / Travellator System",
    "12ETC": "Escalator / Travellator System",
    "13ETC": "Escalator / Travellator System",
    "1ETC": "Escalator / Travellator System",
}


def normalise_fault_code(series: pd.Series) -> pd.Series:
    """Standardize fault-code text for joining."""
    return (
        series.astype("string")
        .str.replace("\xa0", " ", regex=False)
        .str.strip()
        .str.upper()
        .replace("", pd.NA)
    )


def build_fault_lookup(fault_codes_raw: pd.DataFrame) -> pd.DataFrame:
    """Build a clean fault-code lookup table."""
    fault_lookup = fault_codes_raw.copy()

    fault_lookup.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in fault_lookup.columns
    ]

    required_columns = [
        "category",
        "primary",
        "sub",
        "item_2_(code)",
        "exact",
        "exact_60",
        "current",
        "description",
        "rectification",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in fault_lookup.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Fault-code master is missing required columns: {missing_columns}"
        )

    fault_lookup["fault_code_key"] = normalise_fault_code(
        fault_lookup["item_2_(code)"]
    )

    fault_lookup = fault_lookup[
        [
            "fault_code_key",
            "category",
            "primary",
            "sub",
            "exact",
            "exact_60",
            "current",
            "description",
            "rectification",
        ]
    ].drop_duplicates(subset=["fault_code_key"])

    return fault_lookup


def add_fault_features(
    silver_callbacks: pd.DataFrame,
    fault_codes_raw: pd.DataFrame,
) -> pd.DataFrame:
    """Attach fault-code master information and fault-family fields."""
    enriched = silver_callbacks.copy()

    enriched["fault_code_key"] = normalise_fault_code(enriched["fault_code_raw"])

    fault_lookup = build_fault_lookup(fault_codes_raw)

    enriched = enriched.merge(
        fault_lookup,
        on="fault_code_key",
        how="left",
        suffixes=("", "_fault_master"),
    )

    enriched["fault_family_from_recorded_code"] = (
        enriched["fault_code_key"]
        .map(FAULT_FAMILY_BY_CODE)
        .fillna("Other / Detailed Code")
    )

    enriched["fault_family_final"] = enriched["fault_family_from_recorded_code"]

    enriched.loc[
        enriched["fault_code_key"].isna(),
        "fault_family_final",
    ] = "Unclassified"

    enriched["fault_code_master_match_flag"] = (
        enriched["fault_code_key"].notna()
        & enriched["category"].notna()
    )

    return enriched