from __future__ import annotations

EXPECTED_CALLBACK_COLUMNS = [
    "ID",
    "Created",
    "Job Code",
    "Account: Sector",
    "Account: Subsector",
    "Item 2",
    "Item 2 (Code)",
    "Start date + time (Realised)",
    "Account",
    "Person: Cost centre",
    "Serial number 1 (Description)",
    "Item 1",
    "Mantrap",
    "Description",
    "Start date + time",
    "End date + time",
    "Creator",
    "Your ref.",
    "Account: Manager",
    "Person",
    "Status",
    "Remarks: Workflow",
    "Remarks: Request",
    "Account: Code",
    "Current actors",
]


def validate_callback_schema(columns: list[str], source_name: str) -> None:
    """Validate callback report schema before processing."""

    missing_columns = [
        column for column in EXPECTED_CALLBACK_COLUMNS if column not in columns
    ]

    unexpected_columns = [
        column for column in columns if column not in EXPECTED_CALLBACK_COLUMNS
    ]

    if missing_columns or unexpected_columns:
        raise ValueError(
            f"Callback schema mismatch in {source_name}.\n"
            f"Missing columns: {missing_columns}\n"
            f"Unexpected columns: {unexpected_columns}"
        )
