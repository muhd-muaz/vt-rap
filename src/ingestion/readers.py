from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd


def read_crm_export(file_path: Path) -> pd.DataFrame:
    """
    Read CRM exports that may be genuine Excel files or HTML tables saved
    with an .xls extension.

    The CRM system exports some .xls files as HTML. This reader handles both.
    """
    suffix = file_path.suffix.lower()

    if suffix == ".xlsx":
        return pd.read_excel(file_path, dtype="string")

    raw_content = file_path.read_bytes()

    for encoding in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            decoded_content = raw_content.decode(encoding)
            tables = pd.read_html(StringIO(decoded_content))

            if not tables:
                continue

            largest_table = max(tables, key=lambda table: table.shape[0])
            return largest_table.astype("string")

        except (UnicodeDecodeError, ValueError):
            continue

    raise ValueError(f"Unable to read '{file_path.name}' as Excel or CRM HTML export.")


def normalise_column_name(column_name: object) -> str:
    """Normalize whitespace in source column names."""
    return " ".join(str(column_name).split()).strip()


def read_table_with_clean_headers(file_path: Path) -> pd.DataFrame:
    """Read a CRM export and normalize simple column headers."""
    dataframe = read_crm_export(file_path)
    dataframe.columns = [
        normalise_column_name(column_name) for column_name in dataframe.columns
    ]

    return dataframe
