from __future__ import annotations

import pandas as pd

from src.models.risk_scoring import build_equipment_risk_model


def test_equipment_recent_callbacks_are_grouped_by_account() -> None:
    analysis_callbacks = pd.DataFrame(
        {
            "callback_id": ["recent-a-1", "recent-a-2", "old-b-1"],
            "equipment_description_raw": ["Lift 1", "Lift 1", "Lift 1"],
            "account_name_raw": ["Account A", "Account A", "Account B"],
            "equipment_type": ["Elevator", "Elevator", "Elevator"],
            "mantrap_flag": [False, False, False],
            "fault_family_final": ["Door", "Door", "Drive"],
            "valid_response_minutes": [10.0, 12.0, 15.0],
            "valid_repair_minutes": [30.0, 35.0, 40.0],
            "event_at": pd.to_datetime(
                ["2024-12-30", "2024-12-31", "2023-12-01"]
            ),
        }
    )

    equipment_risk = build_equipment_risk_model(analysis_callbacks)

    recent_callbacks_by_account = equipment_risk.set_index("account_name_raw")[
        "callbacks_last_365_days"
    ].to_dict()

    assert recent_callbacks_by_account["Account A"] == 2
    assert recent_callbacks_by_account["Account B"] == 0
