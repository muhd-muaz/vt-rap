from __future__ import annotations

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="VT-RAP Demo",
    page_icon="📊",
    layout="wide",
)

st.title("VT-RAP - Vertical Transport Reliability Analytics Platform")
st.caption("Sanitized public demo version")

st.markdown(
    """
    This public demo shows the structure and workflow of VT-RAP without exposing
    company callback, account, equipment, or customer data.
    """
)

summary = pd.DataFrame(
    [
        {"Metric": "Callback records processed", "Value": "33,160"},
        {"Metric": "Completed / verified callbacks", "Value": "31,627"},
        {"Metric": "Mantrap events", "Value": "3,939"},
        {"Metric": "Median response time", "Value": "21 minutes"},
        {"Metric": "Median repair time", "Value": "75 minutes"},
        {"Metric": "Top fault family", "Value": "Door System"},
    ]
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Callbacks processed", "33,160")

with col2:
    st.metric("Completed / verified", "31,627")

with col3:
    st.metric("Mantrap events", "3,939")

st.divider()

st.subheader("Pipeline workflow")

st.markdown(
    """
    **Raw layer**  
    Source callback exports and master/reference inputs.

    **Silver layer**  
    Cleaned callback records with timestamp, duration, fault-code, mantrap,
    account, and equipment features.

    **Gold layer**  
    Dashboard-ready management tables for executive summary, equipment risk,
    account risk, fault analysis, emerging alerts, and data quality.
    """
)

st.subheader("Demo executive summary")
st.dataframe(summary, use_container_width=True, hide_index=True)

st.subheader("Dashboard modules")

modules = pd.DataFrame(
    [
        {
            "Page": "Executive Overview",
            "Purpose": "Management-level KPI and operational summary.",
        },
        {
            "Page": "Equipment Risk",
            "Purpose": "Ranks equipment by callback, mantrap, recency, and timing risk.",
        },
        {
            "Page": "Account Risk",
            "Purpose": "Highlights customer accounts with higher service reliability exposure.",
        },
        {
            "Page": "Fault Analysis",
            "Purpose": "Preserves actual CRM fault codes while grouping faults for management review.",
        },
        {
            "Page": "Emerging Alerts",
            "Purpose": "Flags equipment with early warning signals.",
        },
        {
            "Page": "Data Quality",
            "Purpose": "Tracks missing values, invalid durations, and master-data matching quality.",
        },
    ]
)

st.dataframe(modules, use_container_width=True, hide_index=True)

st.subheader("Future enhancement")

st.info(
    """
    VT-RAP can be extended into an automated daily monitoring workflow.
    At a scheduled time, such as 9:00 AM, Windows Task Scheduler can trigger
    a controlled export process from Exact Synergy, place the latest callback
    file into the VT-RAP input folder, run the full refresh pipeline, execute
    validation checks, update processed outputs, and launch the Streamlit
    dashboard for daily operational review.
    """
)

st.caption(
    "Note: This public demo uses sanitized summary information and does not include confidential company records."
)