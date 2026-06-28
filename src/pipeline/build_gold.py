from __future__ import annotations

import pandas as pd

from src.models.risk_scoring import (
    build_account_fault_family_mix,
    build_account_risk_model,
    build_analysis_callbacks,
    build_data_quality_summary,
    build_emerging_equipment_alerts,
    build_equipment_fault_family_mix,
    build_equipment_risk_model,
    build_executive_summary,
    build_fault_code_summary,
    build_fault_family_summary,
    build_monthly_account_trend,
    build_monthly_callback_trend,
    build_monthly_equipment_trend,
    build_monthly_equipment_type_trend,
    build_monthly_fault_code_trend,
    build_monthly_fault_family_trend,
)


def build_gold_tables(silver_callbacks: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Build management-ready gold tables."""
    analysis_callbacks = build_analysis_callbacks(silver_callbacks)

    if analysis_callbacks.empty:
        empty_table = pd.DataFrame()

        executive_summary = build_executive_summary(
            analysis_callbacks=analysis_callbacks,
            fault_family_summary=empty_table,
            equipment_risk_model=empty_table,
            account_risk_model=empty_table,
        )

        data_quality_summary = build_data_quality_summary(silver_callbacks)

        return {
            "fault_family_summary": empty_table.copy(),
            "fault_code_summary": empty_table.copy(),
            "equipment_risk_model": empty_table.copy(),
            "account_risk_model": empty_table.copy(),
            "emerging_equipment_alerts": empty_table.copy(),
            "executive_summary": executive_summary,
            "data_quality_summary": data_quality_summary,
            "monthly_callback_trend": empty_table.copy(),
            "monthly_fault_family_trend": empty_table.copy(),
            "monthly_fault_code_trend": empty_table.copy(),
            "monthly_equipment_type_trend": empty_table.copy(),
            "monthly_account_trend": empty_table.copy(),
            "monthly_equipment_trend": empty_table.copy(),
            "equipment_fault_family_mix": empty_table.copy(),
            "account_fault_family_mix": empty_table.copy(),
        }

    fault_family_summary = build_fault_family_summary(analysis_callbacks)
    fault_code_summary = build_fault_code_summary(analysis_callbacks)

    equipment_risk_model = build_equipment_risk_model(analysis_callbacks)
    account_risk_model = build_account_risk_model(analysis_callbacks)

    emerging_equipment_alerts = build_emerging_equipment_alerts(equipment_risk_model)

    executive_summary = build_executive_summary(
        analysis_callbacks=analysis_callbacks,
        fault_family_summary=fault_family_summary,
        equipment_risk_model=equipment_risk_model,
        account_risk_model=account_risk_model,
    )

    data_quality_summary = build_data_quality_summary(silver_callbacks)

    monthly_callback_trend = build_monthly_callback_trend(analysis_callbacks)
    monthly_fault_family_trend = build_monthly_fault_family_trend(analysis_callbacks)
    monthly_fault_code_trend = build_monthly_fault_code_trend(analysis_callbacks)
    monthly_equipment_type_trend = build_monthly_equipment_type_trend(
        analysis_callbacks
    )
    monthly_account_trend = build_monthly_account_trend(analysis_callbacks)
    monthly_equipment_trend = build_monthly_equipment_trend(analysis_callbacks)

    equipment_fault_family_mix = build_equipment_fault_family_mix(analysis_callbacks)
    account_fault_family_mix = build_account_fault_family_mix(analysis_callbacks)

    return {
        "fault_family_summary": fault_family_summary,
        "fault_code_summary": fault_code_summary,
        "equipment_risk_model": equipment_risk_model,
        "account_risk_model": account_risk_model,
        "emerging_equipment_alerts": emerging_equipment_alerts,
        "executive_summary": executive_summary,
        "data_quality_summary": data_quality_summary,
        "monthly_callback_trend": monthly_callback_trend,
        "monthly_fault_family_trend": monthly_fault_family_trend,
        "monthly_fault_code_trend": monthly_fault_code_trend,
        "monthly_equipment_type_trend": monthly_equipment_type_trend,
        "monthly_account_trend": monthly_account_trend,
        "monthly_equipment_trend": monthly_equipment_trend,
        "equipment_fault_family_mix": equipment_fault_family_mix,
        "account_fault_family_mix": account_fault_family_mix,
    }
