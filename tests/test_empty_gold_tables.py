import pandas as pd

from src.pipeline.build_gold import build_gold_tables


def test_build_gold_tables_handles_empty_analysis_period() -> None:
    silver_callbacks = pd.DataFrame(
        {
            "analysis_status_group": ["active_or_in_progress"],
            "account_code": ["A001"],
            "account_name_raw": ["Example account"],
            "equipment_description_raw": ["Lift 01"],
            "equipment_type": ["Bed Lift"],
            "callback_id": ["CB001"],
            "mantrap_flag": [False],
            "event_at": pd.to_datetime(["2026-01-01"]),
            "event_month": ["2026-01"],
            "fault_family_final": ["Door System"],
            "fault_code_key": ["2LDA"],
            "fault_code_master_match_flag": [True],
            "valid_response_minutes": [10.0],
            "valid_repair_minutes": [30.0],
            "invalid_response_time_flag": [False],
            "invalid_repair_time_flag": [False],
        }
    )

    gold_tables = build_gold_tables(silver_callbacks)

    assert set(gold_tables) == {
        "fault_family_summary",
        "fault_code_summary",
        "equipment_risk_model",
        "account_risk_model",
        "emerging_equipment_alerts",
        "executive_summary",
        "data_quality_summary",
        "monthly_callback_trend",
        "monthly_fault_family_trend",
        "monthly_fault_code_trend",
        "monthly_equipment_type_trend",
        "monthly_account_trend",
        "monthly_equipment_trend",
        "equipment_fault_family_mix",
        "account_fault_family_mix",
    }

    executive_summary = gold_tables["executive_summary"]

    completed_metric = executive_summary.loc[
        executive_summary["metric"].eq("Completed / verified callbacks"),
        "value",
    ].iloc[0]

    top_fault_family = executive_summary.loc[
        executive_summary["metric"].eq("Top fault family"),
        "value",
    ].iloc[0]

    assert completed_metric == 0
    assert top_fault_family == "No data"
