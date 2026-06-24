from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.ingestion.readers import read_table_with_clean_headers
from src.ingestion.schema import validate_callback_schema


def extract_year_from_callback_file(file_name: str) -> int:
    """Extract year from callback file name such as 'Call Back Report 2026.xls'."""
    return int(file_name.replace("Call Back Report ", "").replace(".xls", "").strip())


def add_callback_lineage(dataframe: pd.DataFrame, source_file: str) -> pd.DataFrame:
    """Add source lineage for auditability and monthly refresh tracking."""
    enriched = dataframe.copy()

    enriched.insert(0, "source_file", source_file)
    enriched.insert(1, "source_year", extract_year_from_callback_file(source_file))
    enriched.insert(2, "source_row_number", range(1, len(enriched) + 1))

    return enriched


def build_callbacks_raw(callbacks_directory: Path) -> pd.DataFrame:
    """Read and combine all callback report files."""

    callback_files = sorted(callbacks_directory.glob("Call Back Report *.xls"))

    if not callback_files:
        raise FileNotFoundError(f"No callback files found in {callbacks_directory}")

    callback_frames: list[pd.DataFrame] = []

    for file_path in callback_files:
        dataframe = read_table_with_clean_headers(file_path)
        validate_callback_schema(dataframe.columns.tolist(), file_path.name)

        dataframe = add_callback_lineage(dataframe, file_path.name)
        callback_frames.append(dataframe)

    return pd.concat(callback_frames, ignore_index=True)


def build_master_tables(master_directory: Path) -> dict[str, pd.DataFrame]:
    """Read master/reference CRM files."""

    required_files = {
        "accounts_raw": "CRMSearch.xlsx",
        "fault_codes_raw": "faultcode.xlsx",
        "equipment_master_raw": "LogItemNumbers.xls",
        "configuration_raw": "SMSConfigurationSearch.xls",
        "contracts_raw": "SMSContracts.xls",
    }

    master_tables: dict[str, pd.DataFrame] = {}

    for table_name, file_name in required_files.items():
        file_path = master_directory / file_name

        if not file_path.exists():
            raise FileNotFoundError(f"Missing required master file: {file_path}")

        master_tables[table_name] = read_table_with_clean_headers(file_path)

    return master_tables
