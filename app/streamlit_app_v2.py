from __future__ import annotations

import streamlit as st

from components.layout_v2 import (
    PAGES,
    render_page_header,
    render_sidebar_navigation,
    render_sidebar_status,
)
from services.data_loader import load_dashboard_data, load_pipeline_metadata
from services.filtering import build_filtered_dashboard_tables, render_period_filter
from services.theme_v2 import load_theme_v2
from views.account_risk import render_account_risk
from views.data_quality import render_data_quality
from views.emerging_alerts import render_emerging_alerts
from views.equipment_risk import render_equipment_risk
from views.executive_v2 import render_executive_overview_v2
from views.fault_analysis import render_fault_analysis

st.set_page_config(
    page_title="VT-RAP Command Center",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_page_description(page_name: str) -> str:
    """Return page description from page metadata."""
    for page in PAGES:
        if page.key == page_name:
            return page.description

    return "Vertical transport reliability intelligence."


def main() -> None:
    """Render redesigned VT-RAP Streamlit app."""
    load_theme_v2()

    metadata = load_pipeline_metadata()
    validation_status = str(metadata.get("validation_status", "Unknown"))
    last_refresh = str(metadata.get("generated_at", "Unknown"))

    selected_page = render_sidebar_navigation()
    render_sidebar_status(
        validation_status=validation_status,
        last_refresh=last_refresh,
    )

    raw_dashboard_data = load_dashboard_data()

    filtered_silver_callbacks, period_context = render_period_filter(
        raw_dashboard_data["silver_callbacks"]
    )

    dashboard_data = build_filtered_dashboard_tables(
        filtered_silver_callbacks=filtered_silver_callbacks,
    )

    render_page_header(
        title=selected_page,
        description=get_page_description(selected_page),
        period_label=period_context["period_label"],
        validation_status=validation_status,
    )

    if selected_page == "Executive Overview":
        render_executive_overview_v2(
            executive_summary=dashboard_data["executive_summary"],
            fault_family_summary=dashboard_data["fault_family_summary"],
            equipment_risk_model=dashboard_data["equipment_risk_model"],
            account_risk_model=dashboard_data["account_risk_model"],
            emerging_equipment_alerts=dashboard_data["emerging_equipment_alerts"],
            monthly_callback_trend=dashboard_data["monthly_callback_trend"],
        )

    elif selected_page == "Equipment Risk":
        render_equipment_risk(
            equipment_risk_model=dashboard_data["equipment_risk_model"],
            monthly_equipment_trend=dashboard_data["monthly_equipment_trend"],
            equipment_fault_family_mix=dashboard_data["equipment_fault_family_mix"],
        )

    elif selected_page == "Account Risk":
        render_account_risk(
            account_risk_model=dashboard_data["account_risk_model"],
            equipment_risk_model=dashboard_data["equipment_risk_model"],
            monthly_account_trend=dashboard_data["monthly_account_trend"],
            account_fault_family_mix=dashboard_data["account_fault_family_mix"],
        )

    elif selected_page == "Fault Analysis":
        render_fault_analysis(
            fault_family_summary=dashboard_data["fault_family_summary"],
            fault_code_summary=dashboard_data["fault_code_summary"],
            monthly_fault_family_trend=dashboard_data["monthly_fault_family_trend"],
            monthly_fault_code_trend=dashboard_data["monthly_fault_code_trend"],
            monthly_equipment_type_trend=dashboard_data["monthly_equipment_type_trend"],
        )

    elif selected_page == "Emerging Alerts":
        render_emerging_alerts(
            emerging_equipment_alerts=dashboard_data["emerging_equipment_alerts"],
        )

    elif selected_page == "Data Quality":
        render_data_quality(
            data_quality_summary=dashboard_data["data_quality_summary"],
            metadata=metadata,
        )


if __name__ == "__main__":
    main()
