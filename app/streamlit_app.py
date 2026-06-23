from __future__ import annotations

import streamlit as st

from services.data_loader import load_css, load_dashboard_data
from views.account_risk import render_account_risk
from views.data_quality import render_data_quality
from views.emerging_alerts import render_emerging_alerts
from views.equipment_risk import render_equipment_risk
from views.executive import render_executive_overview
from views.fault_analysis import render_fault_analysis


def main() -> None:
    """Run VT-RAP Streamlit dashboard."""
    st.set_page_config(
        page_title="VT-RAP Command Center",
        layout="wide",
    )

    load_css()

    st.title("VT-RAP Command Center")
    st.caption("Vertical Transport Reliability Analytics Platform")

    dashboard_data = load_dashboard_data()

    overview_tab, equipment_tab, account_tab, fault_tab, emerging_tab, quality_tab = st.tabs(
        [
            "Executive Overview",
            "Equipment Risk",
            "Account Risk",
            "Fault Analysis",
            "Emerging Alerts",
            "Data Quality",
        ]
    )

    with overview_tab:
        render_executive_overview(
            executive_summary=dashboard_data["executive_summary"],
            fault_family_summary=dashboard_data["fault_family_summary"],
            equipment_risk_model=dashboard_data["equipment_risk_model"],
            account_risk_model=dashboard_data["account_risk_model"],
            emerging_equipment_alerts=dashboard_data["emerging_equipment_alerts"],
            monthly_callback_trend=dashboard_data["monthly_callback_trend"],
        )

    with equipment_tab:
        render_equipment_risk(
            equipment_risk_model=dashboard_data["equipment_risk_model"],
            monthly_equipment_trend=dashboard_data["monthly_equipment_trend"],
            equipment_fault_family_mix=dashboard_data["equipment_fault_family_mix"],
        )

    with account_tab:
        render_account_risk(
            account_risk_model=dashboard_data["account_risk_model"],
            monthly_account_trend=dashboard_data["monthly_account_trend"],
            equipment_risk_model=dashboard_data["equipment_risk_model"],
            account_fault_family_mix=dashboard_data["account_fault_family_mix"],
        )

    with fault_tab:
        render_fault_analysis(
            fault_family_summary=dashboard_data["fault_family_summary"],
            monthly_fault_family_trend=dashboard_data["monthly_fault_family_trend"],
            monthly_equipment_type_trend=dashboard_data[
                "monthly_equipment_type_trend"
            ],
        )

    with emerging_tab:
        render_emerging_alerts(
            emerging_equipment_alerts=dashboard_data["emerging_equipment_alerts"],
        )

    with quality_tab:
        render_data_quality(
            data_quality_summary=dashboard_data["data_quality_summary"],
        )


if __name__ == "__main__":
    main()