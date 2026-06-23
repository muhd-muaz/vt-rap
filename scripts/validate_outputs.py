from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


REQUIRED_PROCESSED_FILES = [
    "callbacks_raw.csv",
    "silver_callbacks.csv",
    "fault_family_summary.csv",
    "equipment_risk_model.csv",
    "account_risk_model.csv",
    "emerging_equipment_alerts.csv",
    "executive_summary.csv",
    "data_quality_summary.csv",
    "monthly_callback_trend.csv",
    "monthly_fault_family_trend.csv",
    "monthly_equipment_type_trend.csv",
    "monthly_account_trend.csv",
    "monthly_equipment_trend.csv",
    "equipment_fault_family_mix.csv",
    "account_fault_family_mix.csv",
    "vt_rap_management_outputs.xlsx",
    "pipeline_metadata.json",
    "fault_code_summary.csv",
    "monthly_fault_code_trend.csv",
]


EXPECTED_METRICS = {
    "callbacks_raw_rows": 33160,
    "silver_callbacks_rows": 33160,
    "completed_or_verified_rows": 31627,
    "total_mantraps": 3939,
    "valid_response_rows": 32513,
    "valid_repair_rows": 32677,
    "fault_code_master_matched_rows": 31755,
    "missing_fault_code_rows": 1405,
}


REQUIRED_SILVER_COLUMNS = [
    "callback_id",
    "account_code",
    "account_name_raw",
    "equipment_description_raw",
    "equipment_type",
    "fault_code_raw",
    "fault_family_final",
    "analysis_status_group",
    "mantrap_flag",
    "event_at",
    "attended_at",
    "completed_at",
    "response_minutes",
    "repair_minutes",
    "valid_response_time_flag",
    "valid_repair_time_flag",
    "fault_code_master_match_flag",
]


REQUIRED_EQUIPMENT_RISK_COLUMNS = [
    "equipment_description_raw",
    "account_name_raw",
    "equipment_type",
    "callbacks",
    "mantraps",
    "mantrap_rate_pct",
    "equipment_risk_score_v3",
    "risk_tier",
    "risk_signal_type",
    "primary_risk_driver",
    "risk_explanation",
]


REQUIRED_ACCOUNT_RISK_COLUMNS = [
    "account_code",
    "account_name_raw",
    "callbacks",
    "mantraps",
    "unique_equipment",
    "callbacks_per_equipment",
    "mantrap_rate_pct",
    "account_risk_score",
    "risk_tier",
    "primary_risk_driver",
    "risk_explanation",
]

REQUIRED_FAULT_CODE_SUMMARY_COLUMNS = [
    "fault_code_display",
    "fault_code_name",
    "fault_family_final",
    "callbacks",
    "mantraps",
    "mantrap_rate_pct",
    "unique_accounts",
    "unique_equipment",
]

def assert_file_exists(file_name: str) -> None:
    """Validate that a processed file exists."""
    file_path = PROCESSED_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"Missing required processed file: {file_path}")


def assert_columns_exist(
    dataframe: pd.DataFrame,
    required_columns: list[str],
    table_name: str,
) -> None:
    """Validate required columns exist in a dataframe."""
    missing_columns = [
        column for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise AssertionError(
            f"{table_name} is missing required columns: {missing_columns}"
        )


def assert_equal(actual_value: int, expected_value: int, metric_name: str) -> None:
    """Validate exact metric match."""
    if actual_value != expected_value:
        raise AssertionError(
            f"{metric_name} mismatch. "
            f"Expected {expected_value:,}, got {actual_value:,}."
        )


def validate_pipeline_metadata() -> dict:
    """Validate pipeline metadata file and return metadata content."""
    metadata_path = PROCESSED_DIR / "pipeline_metadata.json"

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    required_metadata_keys = [
        "pipeline_name",
        "run_timestamp",
        "raw_callback_file_count",
        "raw_master_file_count",
        "callbacks_raw_rows",
        "silver_callbacks_rows",
        "latest_event_month",
        "gold_tables",
        "master_tables",
        "validation_status",
    ]

    missing_metadata_keys = [
        key for key in required_metadata_keys
        if key not in metadata
    ]

    if missing_metadata_keys:
        raise AssertionError(
            f"pipeline_metadata.json is missing keys: {missing_metadata_keys}"
        )

    return metadata


def update_pipeline_metadata_validation_status(status: str) -> None:
    """Update validation status in pipeline metadata."""
    metadata_path = PROCESSED_DIR / "pipeline_metadata.json"

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    metadata["validation_status"] = status
    metadata["validation_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    metadata_path.write_text(
        json.dumps(metadata, indent=4),
        encoding="utf-8",
    )


def main() -> None:
    """Validate VT-RAP processed outputs."""
    print("Validating required processed files...")

    for file_name in REQUIRED_PROCESSED_FILES:
        assert_file_exists(file_name)

    validate_pipeline_metadata()

    print("Loading processed tables...")

    callbacks_raw = pd.read_csv(
        PROCESSED_DIR / "callbacks_raw.csv",
        low_memory=False,
    )

    silver_callbacks = pd.read_csv(
        PROCESSED_DIR / "silver_callbacks.csv",
        low_memory=False,
    )

    equipment_risk_model = pd.read_csv(
        PROCESSED_DIR / "equipment_risk_model.csv",
        low_memory=False,
    )

    account_risk_model = pd.read_csv(
        PROCESSED_DIR / "account_risk_model.csv",
        low_memory=False,
    )

    data_quality_summary = pd.read_csv(
        PROCESSED_DIR / "data_quality_summary.csv",
        low_memory=False,
    )

    fault_code_summary = pd.read_csv(
        PROCESSED_DIR / "fault_code_summary.csv",
        low_memory=False,
    )

    print("Validating row counts and key metrics...")

    assert_equal(
        len(callbacks_raw),
        EXPECTED_METRICS["callbacks_raw_rows"],
        "callbacks_raw rows",
    )

    assert_equal(
        len(silver_callbacks),
        EXPECTED_METRICS["silver_callbacks_rows"],
        "silver_callbacks rows",
    )

    assert_equal(
        int(
            silver_callbacks["analysis_status_group"]
            .eq("completed_or_verified")
            .sum()
        ),
        EXPECTED_METRICS["completed_or_verified_rows"],
        "completed_or_verified rows",
    )

    assert_equal(
        int(silver_callbacks["mantrap_flag"].sum()),
        EXPECTED_METRICS["total_mantraps"],
        "total mantraps",
    )

    assert_equal(
        int(silver_callbacks["valid_response_time_flag"].sum()),
        EXPECTED_METRICS["valid_response_rows"],
        "valid response rows",
    )

    assert_equal(
        int(silver_callbacks["valid_repair_time_flag"].sum()),
        EXPECTED_METRICS["valid_repair_rows"],
        "valid repair rows",
    )

    assert_equal(
        int(silver_callbacks["fault_code_master_match_flag"].sum()),
        EXPECTED_METRICS["fault_code_master_matched_rows"],
        "fault-code master matched rows",
    )

    assert_equal(
        int(silver_callbacks["fault_code_key"].isna().sum()),
        EXPECTED_METRICS["missing_fault_code_rows"],
        "missing fault-code rows",
    )

    print("Validating required columns...")

    assert_columns_exist(
        dataframe=silver_callbacks,
        required_columns=REQUIRED_SILVER_COLUMNS,
        table_name="silver_callbacks",
    )

    assert_columns_exist(
        dataframe=equipment_risk_model,
        required_columns=REQUIRED_EQUIPMENT_RISK_COLUMNS,
        table_name="equipment_risk_model",
    )

    assert_columns_exist(
        dataframe=account_risk_model,
        required_columns=REQUIRED_ACCOUNT_RISK_COLUMNS,
        table_name="account_risk_model",
    )

    assert_columns_exist(
        dataframe=data_quality_summary,
        required_columns=["check_name", "value", "rate_pct", "status"],
        table_name="data_quality_summary",
    )

    assert_columns_exist(
        dataframe=fault_code_summary,
        required_columns=REQUIRED_FAULT_CODE_SUMMARY_COLUMNS,
        table_name="fault_code_summary",
    )

    update_pipeline_metadata_validation_status("Passed")

    print("Validation completed successfully.")
    print("pipeline_metadata.json validation_status updated to Passed.")


if __name__ == "__main__":
    main()