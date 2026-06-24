# VT-RAP — Vertical Transport Reliability Analytics Platform

VT-RAP is a Python-based analytics pipeline and Streamlit dashboard for elevator callback reliability analysis.

It processes callback records, enriches them with master data, builds management-level gold tables, scores equipment/account risk, detects emerging equipment alerts, and provides an interactive dashboard with CSV exports.

## Key Features

- Raw-to-silver-to-gold data pipeline
- Fault-code enrichment and fault-family grouping
- Equipment-level risk scoring
- Account-level risk scoring
- Emerging equipment alert detection
- Monthly callback and response/repair trend analysis
- Fault family and actual fault code analysis
- Streamlit dashboard with period filtering
- Filtered CSV exports from dashboard tables

## Dashboard Pages

- Executive Overview
- Equipment Risk
- Account Risk
- Fault Analysis
- Emerging Alerts
- Data Quality

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements.txt