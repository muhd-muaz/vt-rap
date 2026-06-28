from __future__ import annotations

import pandas as pd

from app.components.charts import (
    build_equipment_fault_mix_chart,
    build_equipment_monthly_chart,
)


def test_equipment_monthly_chart_filters_same_equipment_by_account() -> None:
    monthly_equipment_trend = pd.DataFrame(
        {
            "event_month": ["2026-01", "2026-01"],
            "account_name_raw": ["Account A", "Account B"],
            "equipment_description_raw": ["Lift 01", "Lift 01"],
            "callbacks": [5, 2],
            "mantraps": [4, 1],
        }
    )

    figure = build_equipment_monthly_chart(
        monthly_equipment_trend=monthly_equipment_trend,
        selected_equipment="Lift 01",
        selected_account_name="Account B",
    )

    trace_values = [int(value) for trace in figure.data for value in trace.y]

    assert trace_values == [2, 1]


def test_equipment_fault_mix_chart_filters_same_equipment_by_account() -> None:
    equipment_fault_family_mix = pd.DataFrame(
        {
            "account_name_raw": ["Account A", "Account B"],
            "equipment_description_raw": ["Lift 01", "Lift 01"],
            "fault_family_final": ["Door", "Controller"],
            "callbacks": [7, 3],
            "mantraps": [2, 1],
            "mantrap_rate_pct": [28.57, 33.33],
            "median_response_minutes": [15, 20],
            "median_repair_minutes": [45, 55],
        }
    )

    figure = build_equipment_fault_mix_chart(
        equipment_fault_family_mix=equipment_fault_family_mix,
        selected_equipment="Lift 01",
        selected_account_name="Account B",
    )

    assert list(figure.data[0].x) == [3]
    assert list(figure.data[0].y) == ["Controller"]
