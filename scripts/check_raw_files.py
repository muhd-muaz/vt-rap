from __future__ import annotations

from pathlib import Path

from src.ingestion.readers import read_table_with_clean_headers

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def main() -> None:
    """Check whether raw CRM files can be read successfully."""
    source_files = sorted(RAW_DATA_DIR.rglob("*.xls")) + sorted(
        RAW_DATA_DIR.rglob("*.xlsx")
    )

    if not source_files:
        print("No raw files found.")
        return

    for file_path in source_files:
        try:
            dataframe = read_table_with_clean_headers(file_path)
            print(
                f"OK | {file_path.relative_to(PROJECT_ROOT)} "
                f"| rows={len(dataframe):,} | columns={len(dataframe.columns):,}"
            )
        except Exception as error:
            print(
                f"FAILED | {file_path.relative_to(PROJECT_ROOT)} "
                f"| {type(error).__name__}: {error}"
            )


if __name__ == "__main__":
    main()
