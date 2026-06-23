from __future__ import annotations

import numpy as np
import pandas as pd


def min_max_score(series: pd.Series) -> pd.Series:
    """Scale a numeric series between 0 and 1."""
    minimum = series.min()
    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum) or minimum == maximum:
        return pd.Series(0.0, index=series.index)

    return (series - minimum) / (maximum - minimum)


def get_primary_driver(row: pd.Series, driver_columns: dict[str, str]) -> str:
    """Return the strongest risk driver based on component scores."""
    available_scores = {
        column_name: row[column_name]
        for column_name in driver_columns
        if column_name in row.index and pd.notna(row[column_name])
    }

    if not available_scores:
        return "Unknown"

    strongest_column = max(available_scores, key=available_scores.get)

    return driver_columns[strongest_column]


def build_equipment_risk_explanation(row: pd.Series) -> str:
    """Create a human-readable equipment risk explanation."""
    return (
        f"{row['equipment_description_raw']} at {row['account_name_raw']} has "
        f"{int(row['callbacks'])} callbacks, {int(row['mantraps'])} mantraps, "
        f"{row['mantrap_rate_pct']:.2f}% mantrap rate, "
        f"{int(row['callbacks_last_365_days'])} callbacks in the last 365 days, "
        f"and {int(row['mantraps_last_365_days'])} mantraps in the last 365 days."
    )


def build_account_risk_explanation(row: pd.Series) -> str:
    """Create a human-readable account risk explanation."""
    return (
        f"{row['account_name_raw']} has {int(row['callbacks'])} callbacks across "
        f"{int(row['unique_equipment'])} equipment, {int(row['mantraps'])} mantraps, "
        f"{row['callbacks_per_equipment']:.2f} callbacks per equipment, and "
        f"{row['mantrap_rate_pct']:.2f}% mantrap rate."
    )


def build_analysis_callbacks(silver_callbacks: pd.DataFrame) -> pd.DataFrame:
    """Filter callbacks used for management analytics."""
    return silver_callbacks[
        silver_callbacks["analysis_status_group"].eq("completed_or_verified")
    ].copy()


def build_fault_family_summary(analysis_callbacks: pd.DataFrame) -> pd.DataFrame:
    """Summarize callback performance by fault family."""
    summary = (
        analysis_callbacks
        .groupby("fault_family_final", dropna=False)
        .agg(
            callbacks=("callback_id", "count"),
            mantraps=("mantrap_flag", "sum"),
            unique_accounts=("account_code", "nunique"),
            unique_equipment=("equipment_description_raw", "nunique"),
            median_response_minutes=("valid_response_minutes", "median"),
            median_repair_minutes=("valid_repair_minutes", "median"),
        )
        .reset_index()
    )

    summary["callback_share_pct"] = (
        summary["callbacks"] / summary["callbacks"].sum() * 100
    ).round(2)

    summary["mantrap_rate_pct"] = (
        summary["mantraps"] / summary["callbacks"] * 100
    ).round(2)

    return summary.sort_values("callbacks", ascending=False)


def build_equipment_risk_model(analysis_callbacks: pd.DataFrame) -> pd.DataFrame:
    """Build equipment-level risk model with historical and recent risk signals."""
    equipment_summary = (
        analysis_callbacks
        .groupby(
            [
                "equipment_description_raw",
                "account_name_raw",
                "equipment_type",
            ],
            dropna=False,
        )
        .agg(
            callbacks=("callback_id", "count"),
            mantraps=("mantrap_flag", "sum"),
            unique_fault_families=("fault_family_final", "nunique"),
            median_response_minutes=("valid_response_minutes", "median"),
            median_repair_minutes=("valid_repair_minutes", "median"),
            first_event_at=("event_at", "min"),
            last_event_at=("event_at", "max"),
        )
        .reset_index()
    )

    equipment_summary["mantrap_rate_pct"] = (
        equipment_summary["mantraps"] / equipment_summary["callbacks"] * 100
    ).round(2)

    equipment_summary["active_days"] = (
        equipment_summary["last_event_at"] - equipment_summary["first_event_at"]
    ).dt.days.clip(lower=1)

    minimum_exposure_days = 180

    equipment_summary["exposure_days_adjusted"] = (
        equipment_summary["active_days"].clip(lower=minimum_exposure_days)
    )

    equipment_summary["callbacks_per_365_days_adjusted"] = (
        equipment_summary["callbacks"]
        / equipment_summary["exposure_days_adjusted"]
        * 365
    ).round(2)

    equipment_summary["sample_confidence_factor"] = (
        equipment_summary["callbacks"] / 20
    ).clip(upper=1)

    equipment_summary["median_repair_minutes_filled"] = (
        equipment_summary["median_repair_minutes"]
        .fillna(equipment_summary["median_repair_minutes"].median())
    )

    equipment_summary["callback_frequency_score"] = min_max_score(
        equipment_summary["callbacks_per_365_days_adjusted"]
    )

    equipment_summary["callback_volume_score"] = min_max_score(
        equipment_summary["callbacks"]
    )

    equipment_summary["mantrap_count_score"] = min_max_score(
        equipment_summary["mantraps"]
    )

    equipment_summary["mantrap_rate_score"] = min_max_score(
        equipment_summary["mantrap_rate_pct"]
    )

    equipment_summary["repair_duration_score"] = min_max_score(
        equipment_summary["median_repair_minutes_filled"]
    )

    equipment_summary["fault_diversity_score"] = min_max_score(
        equipment_summary["unique_fault_families"]
    )

    equipment_summary["raw_equipment_risk_score"] = (
        equipment_summary["callback_volume_score"] * 0.25
        + equipment_summary["callback_frequency_score"] * 0.20
        + equipment_summary["mantrap_count_score"] * 0.25
        + equipment_summary["mantrap_rate_score"] * 0.15
        + equipment_summary["repair_duration_score"] * 0.10
        + equipment_summary["fault_diversity_score"] * 0.05
    ) * 100

    equipment_summary["equipment_risk_score"] = (
        equipment_summary["raw_equipment_risk_score"]
        * equipment_summary["sample_confidence_factor"]
    )

    equipment_summary["risk_signal_type"] = np.select(
        [
            equipment_summary["callbacks"] < 5,
            equipment_summary["callbacks"].between(5, 19),
            equipment_summary["callbacks"] >= 20,
        ],
        [
            "Emerging signal - low evidence",
            "Watchlist - moderate evidence",
            "Established risk",
        ],
        default="Unknown",
    )

    reference_date = analysis_callbacks["event_at"].max()

    for days in [90, 180, 365]:
        window_start = reference_date - pd.Timedelta(days=days)
        recent = analysis_callbacks[analysis_callbacks["event_at"] >= window_start]

        recent_summary = (
            recent
            .groupby("equipment_description_raw", dropna=False)
            .agg(
                **{
                    f"callbacks_last_{days}_days": ("callback_id", "count"),
                    f"mantraps_last_{days}_days": ("mantrap_flag", "sum"),
                }
            )
            .reset_index()
        )

        equipment_summary = equipment_summary.merge(
            recent_summary,
            on="equipment_description_raw",
            how="left",
        )

    recent_columns = [
        "callbacks_last_90_days",
        "mantraps_last_90_days",
        "callbacks_last_180_days",
        "mantraps_last_180_days",
        "callbacks_last_365_days",
        "mantraps_last_365_days",
    ]

    equipment_summary[recent_columns] = (
        equipment_summary[recent_columns].fillna(0).astype(int)
    )

    equipment_summary["recent_callback_score"] = min_max_score(
        equipment_summary["callbacks_last_365_days"]
    )

    equipment_summary["recent_mantrap_score"] = min_max_score(
        equipment_summary["mantraps_last_365_days"]
    )

    equipment_summary["equipment_risk_score_v3"] = (
        equipment_summary["equipment_risk_score"] * 0.70
        + equipment_summary["recent_callback_score"] * 100 * 0.15
        + equipment_summary["recent_mantrap_score"] * 100 * 0.15
    )

    equipment_summary["risk_tier"] = pd.cut(
        equipment_summary["equipment_risk_score_v3"],
        bins=[-np.inf, 15, 30, 50, np.inf],
        labels=["Low", "Medium", "High", "Critical"],
    )

    equipment_driver_columns = {
        "callback_volume_score": "High callback volume",
        "callback_frequency_score": "High callback frequency",
        "mantrap_count_score": "High mantrap count",
        "mantrap_rate_score": "High mantrap rate",
        "repair_duration_score": "Long repair duration",
        "fault_diversity_score": "Diverse fault families",
        "recent_callback_score": "High recent callback activity",
        "recent_mantrap_score": "High recent mantrap activity",
    }

    equipment_summary["primary_risk_driver"] = equipment_summary.apply(
        lambda row: get_primary_driver(row, equipment_driver_columns),
        axis=1,
    )

    equipment_summary["risk_explanation"] = equipment_summary.apply(
        build_equipment_risk_explanation,
        axis=1,
    )

    return equipment_summary.sort_values(
        "equipment_risk_score_v3",
        ascending=False,
    )


def build_account_risk_model(analysis_callbacks: pd.DataFrame) -> pd.DataFrame:
    """Build account-level risk model."""
    account_summary = (
        analysis_callbacks
        .groupby(
            [
                "account_code",
                "account_name_raw",
            ],
            dropna=False,
        )
        .agg(
            callbacks=("callback_id", "count"),
            mantraps=("mantrap_flag", "sum"),
            unique_equipment=("equipment_description_raw", "nunique"),
            unique_fault_families=("fault_family_final", "nunique"),
            median_response_minutes=("valid_response_minutes", "median"),
            median_repair_minutes=("valid_repair_minutes", "median"),
        )
        .reset_index()
    )

    account_summary["callbacks_per_equipment"] = (
        account_summary["callbacks"] / account_summary["unique_equipment"]
    ).round(2)

    account_summary["mantrap_rate_pct"] = (
        account_summary["mantraps"] / account_summary["callbacks"] * 100
    ).round(2)

    account_summary["median_repair_minutes_filled"] = (
        account_summary["median_repair_minutes"]
        .fillna(account_summary["median_repair_minutes"].median())
    )

    account_summary["callback_volume_score"] = min_max_score(
        account_summary["callbacks"]
    )

    account_summary["callbacks_per_equipment_score"] = min_max_score(
        account_summary["callbacks_per_equipment"]
    )

    account_summary["mantrap_count_score"] = min_max_score(
        account_summary["mantraps"]
    )

    account_summary["mantrap_rate_score"] = min_max_score(
        account_summary["mantrap_rate_pct"]
    )

    account_summary["repair_duration_score"] = min_max_score(
        account_summary["median_repair_minutes_filled"]
    )

    account_summary["account_risk_score"] = (
        account_summary["callback_volume_score"] * 0.25
        + account_summary["callbacks_per_equipment_score"] * 0.25
        + account_summary["mantrap_count_score"] * 0.25
        + account_summary["mantrap_rate_score"] * 0.15
        + account_summary["repair_duration_score"] * 0.10
    ) * 100

    account_summary["risk_tier"] = pd.cut(
        account_summary["account_risk_score"],
        bins=[-np.inf, 25, 50, 75, np.inf],
        labels=["Low", "Medium", "High", "Critical"],
    )

    account_driver_columns = {
        "callback_volume_score": "High callback volume",
        "callbacks_per_equipment_score": "High callbacks per equipment",
        "mantrap_count_score": "High mantrap count",
        "mantrap_rate_score": "High mantrap rate",
        "repair_duration_score": "Long repair duration",
    }

    account_summary["primary_risk_driver"] = account_summary.apply(
        lambda row: get_primary_driver(row, account_driver_columns),
        axis=1,
    )

    account_summary["risk_explanation"] = account_summary.apply(
        build_account_risk_explanation,
        axis=1,
    )

    return account_summary.sort_values(
        "account_risk_score",
        ascending=False,
    )


def build_emerging_equipment_alerts(
    equipment_risk_model: pd.DataFrame,
) -> pd.DataFrame:
    """Build a low-evidence but high-severity emerging alert table."""
    return (
        equipment_risk_model[
            (equipment_risk_model["callbacks"] < 5)
            & (equipment_risk_model["mantraps"] > 0)
        ]
        .sort_values(
            ["mantraps", "mantrap_rate_pct", "median_repair_minutes"],
            ascending=False,
        )
    )


def build_data_quality_summary(silver_callbacks: pd.DataFrame) -> pd.DataFrame:
    """Build a data quality summary for dashboard transparency."""
    total_rows = len(silver_callbacks)

    quality_records = [
        {
            "check_name": "Total callback records",
            "value": total_rows,
            "rate_pct": 100.00,
            "status": "Info",
        },
        {
            "check_name": "Completed / verified records",
            "value": int(
                silver_callbacks["analysis_status_group"]
                .eq("completed_or_verified")
                .sum()
            ),
            "rate_pct": round(
                silver_callbacks["analysis_status_group"]
                .eq("completed_or_verified")
                .mean()
                * 100,
                2,
            ),
            "status": "Info",
        },
        {
            "check_name": "Fault-code master matched rows",
            "value": int(silver_callbacks["fault_code_master_match_flag"].sum()),
            "rate_pct": round(
                silver_callbacks["fault_code_master_match_flag"].mean() * 100,
                2,
            ),
            "status": "Good",
        },
        {
            "check_name": "Missing fault-code rows",
            "value": int(silver_callbacks["fault_code_key"].isna().sum()),
            "rate_pct": round(
                silver_callbacks["fault_code_key"].isna().mean() * 100,
                2,
            ),
            "status": "Review",
        },
        {
            "check_name": "Invalid response-time rows",
            "value": int(silver_callbacks["invalid_response_time_flag"].sum()),
            "rate_pct": round(
                silver_callbacks["invalid_response_time_flag"].mean() * 100,
                2,
            ),
            "status": "Review",
        },
        {
            "check_name": "Invalid repair-time rows",
            "value": int(silver_callbacks["invalid_repair_time_flag"].sum()),
            "rate_pct": round(
                silver_callbacks["invalid_repair_time_flag"].mean() * 100,
                2,
            ),
            "status": "Review",
        },
        {
            "check_name": "Open / in-process rows",
            "value": int(
                silver_callbacks["analysis_status_group"]
                .eq("active_or_in_progress")
                .sum()
            ),
            "rate_pct": round(
                silver_callbacks["analysis_status_group"]
                .eq("active_or_in_progress")
                .mean()
                * 100,
                2,
            ),
            "status": "Info",
        },
        {
            "check_name": "Rejected rows",
            "value": int(
                silver_callbacks["analysis_status_group"]
                .eq("rejected")
                .sum()
            ),
            "rate_pct": round(
                silver_callbacks["analysis_status_group"].eq("rejected").mean()
                * 100,
                2,
            ),
            "status": "Info",
        },
    ]

    return pd.DataFrame(quality_records)


def build_executive_summary(
    analysis_callbacks: pd.DataFrame,
    fault_family_summary: pd.DataFrame,
    equipment_risk_model: pd.DataFrame,
    account_risk_model: pd.DataFrame,
) -> pd.DataFrame:
    """Build compact executive summary metrics."""
    return pd.DataFrame(
        [
            {
                "metric": "Completed / verified callbacks",
                "value": int(len(analysis_callbacks)),
            },
            {
                "metric": "Unique accounts",
                "value": int(analysis_callbacks["account_code"].nunique()),
            },
            {
                "metric": "Unique equipment",
                "value": int(
                    analysis_callbacks["equipment_description_raw"].nunique()
                ),
            },
            {
                "metric": "Total mantraps",
                "value": int(analysis_callbacks["mantrap_flag"].sum()),
            },
            {
                "metric": "Median response minutes",
                "value": round(
                    float(analysis_callbacks["valid_response_minutes"].median()),
                    2,
                ),
            },
            {
                "metric": "Median repair minutes",
                "value": round(
                    float(analysis_callbacks["valid_repair_minutes"].median()),
                    2,
                ),
            },
            {
                "metric": "Top fault family",
                "value": fault_family_summary.iloc[0]["fault_family_final"],
            },
            {
                "metric": "Top risk account",
                "value": account_risk_model.iloc[0]["account_name_raw"],
            },
            {
                "metric": "Top risk equipment",
                "value": equipment_risk_model.iloc[0]["equipment_description_raw"],
            },
        ]
    )