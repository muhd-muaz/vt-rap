from __future__ import annotations

import pandas as pd

from app.services.filtering import prepare_silver_callbacks_for_dashboard


def test_prepare_silver_callbacks_parses_mantrap_flag_strings() -> None:
    dataframe = pd.DataFrame(
        {
            "mantrap_flag": ["True", "False", "true", "false", "1", "0"],
        }
    )

    prepared = prepare_silver_callbacks_for_dashboard(dataframe)

    assert prepared["mantrap_flag"].tolist() == [
        True,
        False,
        True,
        False,
        True,
        False,
    ]


def test_prepare_silver_callbacks_preserves_existing_boolean_mantrap_flags() -> None:
    dataframe = pd.DataFrame(
        {
            "mantrap_flag": [True, False, True],
        }
    )

    prepared = prepare_silver_callbacks_for_dashboard(dataframe)

    assert prepared["mantrap_flag"].tolist() == [True, False, True]
