from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.pipeline.build_gold import build_gold_tables
from src.pipeline.build_raw import build_callbacks_raw, build_master_tables
from src.pipeline.build_silver import build_silver_callbacks

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_CALLBACKS_DIR = PROJECT_ROOT / "data" / "raw" / "callbacks"
RAW_MASTER_DIR = PROJECT_ROOT / "data" / "raw" / "master"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def prepare_dataframe_for_parquet(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare dataframe for Parquet export.

    Object columns with mixed values are converted to string to avoid Arrow
    conversion errors.
    """
    prepared = dataframe.copy()

    for column_name in prepared.columns:
        if prepared[column_name].dtype == "object":
            prepared[column_name] = prepared[column_name].astype("string")

    return prepared


def save_dataframe_outputs(
    dataframe: pd.DataFrame,
    table_name: str,
    output_directory: Path,
) -> None:
    """Save a dataframe as CSV and Parquet."""
    dataframe.to_csv(
        output_directory / f"{table_name}.csv",
        index=False,
    )

    parquet_ready_dataframe = prepare_dataframe_for_parquet(dataframe)

    parquet_ready_dataframe.to_parquet(
        output_directory / f"{table_name}.parquet",
        index=False,
    )


def save_management_workbook(
    gold_tables: dict[str, pd.DataFrame],
    output_directory: Path,
) -> None:
    """Save management-ready outputs into one Excel workbook."""
    excel_output_path = output_directory / "vt_rap_management_outputs.xlsx"

    with pd.ExcelWriter(excel_output_path, engine="openpyxl") as writer:
        gold_tables["executive_summary"].to_excel(
            writer,
            sheet_name="Executive Summary",
            index=False,
        )
        gold_tables["fault_family_summary"].to_excel(
            writer,
            sheet_name="Fault Family Summary",
            index=False,
        )
        gold_tables["equipment_risk_model"].to_excel(
            writer,
            sheet_name="Equipment Risk",
            index=False,
        )
        gold_tables["account_risk_model"].to_excel(
            writer,
            sheet_name="Account Risk",
            index=False,
        )
        gold_tables["emerging_equipment_alerts"].to_excel(
            writer,
            sheet_name="Emerging Alerts",
            index=False,
        )
        gold_tables["data_quality_summary"].to_excel(
            writer,
            sheet_name="Data Quality",
            index=False,
        )
        gold_tables["monthly_callback_trend"].to_excel(
            writer,
            sheet_name="Monthly Callback Trend",
            index=False,
        )

    print(f"Saved Excel workbook: {excel_output_path}")


def save_pipeline_metadata(
    callbacks_raw: pd.DataFrame,
    silver_callbacks: pd.DataFrame,
    gold_tables: dict[str, pd.DataFrame],
    master_tables: dict[str, pd.DataFrame],
    output_directory: Path,
) -> None:
    """Save pipeline run metadata for dashboard display."""
    raw_callback_files = sorted(
        file_path.name for file_path in RAW_CALLBACKS_DIR.glob("Call Back Report *.xls")
    )

    raw_master_files = sorted(
        file_path.name for file_path in RAW_MASTER_DIR.iterdir() if file_path.is_file()
    )

    latest_event_month = None
    latest_event_at = None

    if "event_at" in silver_callbacks.columns:
        latest_event_at_value = pd.to_datetime(
            silver_callbacks["event_at"],
            errors="coerce",
        ).max()

        if pd.notna(latest_event_at_value):
            latest_event_at = latest_event_at_value.strftime("%Y-%m-%d %H:%M:%S")
            latest_event_month = latest_event_at_value.strftime("%Y-%m")

    metadata = {
        "pipeline_name": "VT-RAP",
        "run_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "raw_callback_file_count": len(raw_callback_files),
        "raw_master_file_count": len(raw_master_files),
        "raw_callback_files": raw_callback_files,
        "raw_master_files": raw_master_files,
        "callbacks_raw_rows": int(len(callbacks_raw)),
        "silver_callbacks_rows": int(len(silver_callbacks)),
        "latest_event_at": latest_event_at,
        "latest_event_month": latest_event_month,
        "gold_tables": {
            table_name: {
                "rows": int(len(dataframe)),
                "columns": int(len(dataframe.columns)),
            }
            for table_name, dataframe in gold_tables.items()
        },
        "master_tables": {
            table_name: {
                "rows": int(len(dataframe)),
                "columns": int(len(dataframe.columns)),
            }
            for table_name, dataframe in master_tables.items()
        },
        "validation_status": "Not yet run",
    }

    metadata_output_path = output_directory / "pipeline_metadata.json"

    metadata_output_path.write_text(
        json.dumps(metadata, indent=4),
        encoding="utf-8",
    )

    print(f"Saved pipeline metadata: {metadata_output_path}")


def main() -> None:
    """Run VT-RAP backend pipeline."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Building raw callback table...")
    callbacks_raw = build_callbacks_raw(RAW_CALLBACKS_DIR)

    print("Building master tables...")
    master_tables = build_master_tables(RAW_MASTER_DIR)

    print("Building silver callback table...")
    silver_callbacks = build_silver_callbacks(
        callbacks_raw=callbacks_raw,
        fault_codes_raw=master_tables["fault_codes_raw"],
    )

    print("Building gold management tables...")
    gold_tables = build_gold_tables(silver_callbacks)

    print("Saving processed outputs...")
    save_dataframe_outputs(
        dataframe=callbacks_raw,
        table_name="callbacks_raw",
        output_directory=PROCESSED_DIR,
    )

    save_dataframe_outputs(
        dataframe=silver_callbacks,
        table_name="silver_callbacks",
        output_directory=PROCESSED_DIR,
    )

    for table_name, dataframe in gold_tables.items():
        save_dataframe_outputs(
            dataframe=dataframe,
            table_name=table_name,
            output_directory=PROCESSED_DIR,
        )

    save_management_workbook(
        gold_tables=gold_tables,
        output_directory=PROCESSED_DIR,
    )

    save_pipeline_metadata(
        callbacks_raw=callbacks_raw,
        silver_callbacks=silver_callbacks,
        gold_tables=gold_tables,
        master_tables=master_tables,
        output_directory=PROCESSED_DIR,
    )

    print("\nPipeline completed.")
    print(f"callbacks_raw rows: {len(callbacks_raw):,}")
    print(f"callbacks_raw columns: {len(callbacks_raw.columns):,}")
    print(f"silver_callbacks rows: {len(silver_callbacks):,}")
    print(f"silver_callbacks columns: {len(silver_callbacks.columns):,}")

    print("\nSilver quality checks:")
    print(
        "completed_or_verified rows:",
        int(
            silver_callbacks["analysis_status_group"].eq("completed_or_verified").sum()
        ),
    )
    print("total mantraps:", int(silver_callbacks["mantrap_flag"].sum()))
    print(
        "valid response rows:",
        int(silver_callbacks["valid_response_time_flag"].sum()),
    )
    print(
        "valid repair rows:",
        int(silver_callbacks["valid_repair_time_flag"].sum()),
    )
    print(
        "median response minutes:",
        round(float(silver_callbacks["valid_response_minutes"].median()), 2),
    )
    print(
        "median repair minutes:",
        round(float(silver_callbacks["valid_repair_minutes"].median()), 2),
    )
    print(
        "fault-code master matched rows:",
        int(silver_callbacks["fault_code_master_match_flag"].sum()),
    )
    print(
        "missing fault-code rows:",
        int(silver_callbacks["fault_code_key"].isna().sum()),
    )

    print("\nTop fault families:")
    print(
        silver_callbacks["fault_family_final"]
        .value_counts(dropna=False)
        .head(10)
        .to_string()
    )

    print("\nGold tables:")
    for table_name, dataframe in gold_tables.items():
        print(
            f"{table_name}: rows={len(dataframe):,}, "
            f"columns={len(dataframe.columns):,}"
        )

    print("\nMaster tables:")
    for table_name, dataframe in master_tables.items():
        print(
            f"{table_name}: rows={len(dataframe):,}, "
            f"columns={len(dataframe.columns):,}"
        )


if __name__ == "__main__":
    main()
