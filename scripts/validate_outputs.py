from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

REQUIRED_FILES = {
    "callbacks_raw": PROCESSED_DIR / "callbacks_raw.csv",
    "silver_callbacks": PROCESSED_DIR / "silver_callbacks.csv",
    "fault_family_summary": PROCESSED_DIR / "fault_family_summary.csv",
    "fault_code_summary": PROCESSED_DIR / "fault_code_summary.csv",
    "equipment_risk_model": PROCESSED_DIR / "equipment_risk_model.csv",
    "account_risk_model": PROCESSED_DIR / "account_risk_model.csv",
    "emerging_equipment_alerts": PROCESSED_DIR / "emerging_equipment_alerts.csv",
    "executive_summary": PROCESSED_DIR / "executive_summary.csv",
    "data_quality_summary": PROCESSED_DIR / "data_quality_summary.csv",
    "monthly_callback_trend": PROCESSED_DIR / "monthly_callback_trend.csv",
    "pipeline_metadata": PROCESSED_DIR / "pipeline_metadata.json",
}

REQUIRED_SILVER_COLUMNS = {
    "callback_id",
    "account_code",
    "account_name_raw",
    "equipment_description_raw",
    "equipment_type",
    "analysis_status_group",
    "mantrap_flag",
    "event_at",
    "event_month",
    "fault_code_key",
    "fault_family_final",
    "fault_code_master_match_flag",
    "valid_response_minutes",
    "valid_repair_minutes",
    "invalid_response_time_flag",
    "invalid_repair_time_flag",
}

REQUIRED_GOLD_COLUMNS = {
    "fault_family_summary": {"fault_family_final"},
    "fault_code_summary": {"fault_code_display"},
    "equipment_risk_model": {
        "equipment_description_raw",
        "account_name_raw",
        "equipment_type",
    },
    "account_risk_model": {
        "account_code",
        "account_name_raw",
    },
    "executive_summary": {"metric", "value"},
    "data_quality_summary": set(),
    "monthly_callback_trend": {"event_month"},
}

REQUIRED_EXECUTIVE_METRICS = {
    "Completed / verified callbacks",
    "Unique accounts",
    "Unique equipment",
    "Total mantraps",
    "Median response minutes",
    "Median repair minutes",
    "Top fault family",
    "Top risk account",
    "Top risk equipment",
}

CALLBACK_COUNT_ALIASES = {
    "callback_count",
    "total_callbacks",
    "callbacks",
    "completed_callbacks",
    "completed_or_verified_callbacks",
}

MANTRAP_COUNT_ALIASES = {
    "mantrap_count",
    "total_mantraps",
    "mantraps",
    "mantrap_callbacks",
}

MONTHLY_COUNT_ALIASES = CALLBACK_COUNT_ALIASES | {
    "monthly_callbacks",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        fail(f"Missing required processed file: {path}")

    return pd.read_csv(path, low_memory=False)


def assert_required_files_exist() -> None:
    print("Validating required processed files...")

    for name, path in REQUIRED_FILES.items():
        if not path.exists():
            fail(f"Missing required file for {name}: {path}")


def assert_columns(
    dataframe: pd.DataFrame,
    required_columns: set[str],
    table_name: str,
) -> None:
    missing_columns = sorted(required_columns - set(dataframe.columns))

    if missing_columns:
        fail(
            f"{table_name} missing required columns: "
            + ", ".join(missing_columns)
        )


def assert_non_empty(dataframe: pd.DataFrame, table_name: str) -> None:
    if dataframe.empty:
        fail(f"{table_name} should not be empty.")


def first_existing_column(
    dataframe: pd.DataFrame,
    aliases: set[str],
) -> str | None:
    for column_name in aliases:
        if column_name in dataframe.columns:
            return column_name

    return None


def assert_any_numeric_column(
    dataframe: pd.DataFrame,
    aliases: set[str],
    table_name: str,
    logical_name: str,
) -> None:
    column_name = first_existing_column(dataframe, aliases)

    if column_name is None:
        available = ", ".join(dataframe.columns)
        expected = ", ".join(sorted(aliases))
        fail(
            f"{table_name} missing {logical_name}. "
            f"Expected one of: {expected}. Available columns: {available}"
        )

    values = pd.to_numeric(dataframe[column_name], errors="coerce")

    if values.isna().all():
        fail(f"{table_name}.{column_name} is fully null.")

    if values.dropna().lt(0).any():
        fail(f"{table_name}.{column_name} contains negative values.")


def validate_raw_and_silver(
    callbacks_raw: pd.DataFrame,
    silver_callbacks: pd.DataFrame,
) -> None:
    print("Validating raw and silver tables...")

    assert_non_empty(callbacks_raw, "callbacks_raw")
    assert_non_empty(silver_callbacks, "silver_callbacks")

    if len(callbacks_raw) != len(silver_callbacks):
        fail(
            "callbacks_raw and silver_callbacks row count mismatch. "
            f"callbacks_raw={len(callbacks_raw):,}, "
            f"silver_callbacks={len(silver_callbacks):,}"
        )

    assert_columns(
        silver_callbacks,
        REQUIRED_SILVER_COLUMNS,
        "silver_callbacks",
    )

    completed_or_verified = silver_callbacks[
        silver_callbacks["analysis_status_group"].eq("completed_or_verified")
    ]

    if completed_or_verified.empty:
        fail("silver_callbacks has no completed_or_verified rows.")

    mantrap_count = int(silver_callbacks["mantrap_flag"].fillna(False).sum())

    if mantrap_count < 0:
        fail("mantrap count cannot be negative.")

    response_median = pd.to_numeric(
        silver_callbacks["valid_response_minutes"],
        errors="coerce",
    ).median()

    repair_median = pd.to_numeric(
        silver_callbacks["valid_repair_minutes"],
        errors="coerce",
    ).median()

    if pd.isna(response_median):
        fail("valid_response_minutes median is null.")

    if pd.isna(repair_median):
        fail("valid_repair_minutes median is null.")

    if response_median < 0:
        fail("valid_response_minutes median cannot be negative.")

    if repair_median < 0:
        fail("valid_repair_minutes median cannot be negative.")


def validate_gold_tables(tables: dict[str, pd.DataFrame]) -> None:
    print("Validating Gold tables...")

    for table_name, required_columns in REQUIRED_GOLD_COLUMNS.items():
        dataframe = tables[table_name]
        assert_columns(dataframe, required_columns, table_name)

    for table_name in [
        "fault_family_summary",
        "fault_code_summary",
        "equipment_risk_model",
        "account_risk_model",
        "executive_summary",
        "data_quality_summary",
        "monthly_callback_trend",
    ]:
        assert_non_empty(tables[table_name], table_name)

    for table_name in [
        "fault_family_summary",
        "fault_code_summary",
        "equipment_risk_model",
        "account_risk_model",
    ]:
        assert_any_numeric_column(
            tables[table_name],
            CALLBACK_COUNT_ALIASES,
            table_name,
            "callback count column",
        )

    for table_name in [
        "fault_family_summary",
        "fault_code_summary",
        "equipment_risk_model",
        "account_risk_model",
    ]:
        assert_any_numeric_column(
            tables[table_name],
            MANTRAP_COUNT_ALIASES,
            table_name,
            "mantrap count column",
        )

    assert_any_numeric_column(
        tables["monthly_callback_trend"],
        MONTHLY_COUNT_ALIASES,
        "monthly_callback_trend",
        "monthly callback count column",
    )

    executive_summary = tables["executive_summary"]
    executive_metrics = set(executive_summary["metric"].astype(str))
    missing_metrics = sorted(REQUIRED_EXECUTIVE_METRICS - executive_metrics)

    if missing_metrics:
        fail(
            "executive_summary missing required metrics: "
            + ", ".join(missing_metrics)
        )


def validate_metadata(
    metadata_path: Path,
    callbacks_raw: pd.DataFrame,
    silver_callbacks: pd.DataFrame,
) -> None:
    print("Validating pipeline metadata...")

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"pipeline_metadata.json is not valid JSON: {exc}")

    timestamp_keys = {
        "generated_at",
        "run_timestamp",
        "created_at",
        "updated_at",
    }

    if not timestamp_keys.intersection(metadata):
        metadata["validated_source_timestamp_note"] = (
            "No source generation timestamp was present before validation."
        )

    metadata["validation_status"] = "Passed"
    metadata["validated_at"] = pd.Timestamp.now().isoformat()
    metadata["callbacks_raw_rows"] = int(len(callbacks_raw))
    metadata["silver_callbacks_rows"] = int(len(silver_callbacks))

    metadata_path.write_text(
        json.dumps(metadata, indent=2, default=str),
        encoding="utf-8",
    )

    print("pipeline_metadata.json validation_status updated to Passed.")


def main() -> None:
    assert_required_files_exist()

    print("Loading processed tables...")

    callbacks_raw = load_csv(REQUIRED_FILES["callbacks_raw"])
    silver_callbacks = load_csv(REQUIRED_FILES["silver_callbacks"])

    tables = {
        "fault_family_summary": load_csv(REQUIRED_FILES["fault_family_summary"]),
        "fault_code_summary": load_csv(REQUIRED_FILES["fault_code_summary"]),
        "equipment_risk_model": load_csv(REQUIRED_FILES["equipment_risk_model"]),
        "account_risk_model": load_csv(REQUIRED_FILES["account_risk_model"]),
        "emerging_equipment_alerts": load_csv(
            REQUIRED_FILES["emerging_equipment_alerts"]
        ),
        "executive_summary": load_csv(REQUIRED_FILES["executive_summary"]),
        "data_quality_summary": load_csv(REQUIRED_FILES["data_quality_summary"]),
        "monthly_callback_trend": load_csv(
            REQUIRED_FILES["monthly_callback_trend"]
        ),
    }

    validate_raw_and_silver(callbacks_raw, silver_callbacks)
    validate_gold_tables(tables)
    validate_metadata(
        REQUIRED_FILES["pipeline_metadata"],
        callbacks_raw,
        silver_callbacks,
    )

    print("Validation completed successfully.")


if __name__ == "__main__":
    main()
