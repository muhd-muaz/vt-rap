# VT-RAP Agent Instructions

## Project
VT-RAP is a Python/Streamlit analytics dashboard for elevator callback, mantrap, fault, equipment risk, and account risk analysis.

## Critical rule
Correctness is more important than UI. Do not make visual changes before backend checks pass.

## Confidentiality
Do not expose, print, upload, or commit company raw data.

Never commit:
- data/raw/
- data/processed/
- data/logs/
- .venv/
- *.csv
- *.xlsx
- *.xls
- *.parquet
- *.bak
- __pycache__/
- *.pyc

Before committing or suggesting commit commands, always check:
git status
git ls-files data
git ls-files *.bak

## Required checks
After code changes, run:
python -m compileall src app scripts tests
python -m pytest

For pipeline/risk/scoring/filtering changes, also run:
python scripts/run_full_refresh.py

## Architecture
src/ingestion = raw data readers and schema checks
src/features = silver-layer feature engineering
src/models = risk scoring and gold analytics tables
src/pipeline = raw/silver/gold pipeline builders
app/services = dashboard loading, filtering, theme
app/components = shared Streamlit UI components
app/views = dashboard pages

## Streamlit apps
Stable dashboard:
app/streamlit_app.py

Experimental redesigned dashboard:
app/streamlit_app_v2.py

Do not break app/streamlit_app.py while working on V2.

## Coding style
Use professional Python.
Prefer small targeted changes.
Do not rewrite unrelated files.
Do not use emojis in code or comments.
Use clear names.
Preserve actual fault codes. Do not replace actual codes with broad fault families.

## Current priorities
1. Fix risk scoring correctness.
2. Add regression tests for same equipment name across different accounts.
3. Guard empty dashboard periods.
4. Escape CRM-sourced strings used with unsafe_allow_html=True.
5. Continue V2 UI redesign one page at a time.