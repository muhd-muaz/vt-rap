from __future__ import annotations

import pandas as pd

from src.features.business_features import add_business_features
from src.features.fault_features import add_fault_features
from src.features.time_features import add_time_features, parse_callback_timestamps


def build_silver_callbacks(
    callbacks_raw: pd.DataFrame,
    fault_codes_raw: pd.DataFrame,
) -> pd.DataFrame:
    """Build the silver callback table from raw callbacks."""
    silver_callbacks = callbacks_raw.copy()

    silver_callbacks = parse_callback_timestamps(silver_callbacks)
    silver_callbacks = add_business_features(silver_callbacks)
    silver_callbacks = add_time_features(silver_callbacks)
    silver_callbacks = add_fault_features(
        silver_callbacks=silver_callbacks,
        fault_codes_raw=fault_codes_raw,
    )

    return silver_callbacks