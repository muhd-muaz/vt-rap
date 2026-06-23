from __future__ import annotations

import numpy as np
import pandas as pd


def add_business_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Create standardized business columns from raw callback fields."""
    enriched = dataframe.copy()

    enriched["callback_id"] = enriched["ID"]
    enriched["account_code"] = enriched["Account: Code"]
    enriched["account_name_raw"] = enriched["Account"]
    enriched["equipment_description_raw"] = enriched["Serial number 1 (Description)"]
    enriched["equipment_type"] = enriched["Item 1"]
    enriched["fault_code_raw"] = enriched["Item 2 (Code)"]
    enriched["fault_description_raw"] = enriched["Item 2"]
    enriched["status_raw"] = enriched["Status"]
    enriched["mantrap_flag"] = enriched["Mantrap"].eq("V")

    enriched["analysis_status_group"] = np.select(
        [
            enriched["Status"].isin(["Processed", "Verified"]),
            enriched["Status"].isin(["Open", "Process"]),
            enriched["Status"].eq("Rejected"),
        ],
        [
            "completed_or_verified",
            "active_or_in_progress",
            "rejected",
        ],
        default="other",
    )

    return enriched