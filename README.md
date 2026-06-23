# VT-RAP: Vertical Transport Reliability Analytics Platform

VT-RAP is a Python-based reliability analytics platform for vertical transport callback data. It processes CRM callback exports, enriches them with business and fault-code features, builds management-ready risk models, and presents the results through a Streamlit command-center dashboard.

The project is designed to support operational monitoring for elevator, escalator, and related vertical transport assets.

## Project Purpose

The platform answers key operational questions:

* Which equipment has the highest callback and mantrap risk?
* Which accounts or sites create the most operational burden?
* Which fault families dominate callback volume?
* Are callbacks and mantraps increasing or decreasing over time?
* Which equipment shows early warning signals despite limited history?
* Can the analytics output be trusted based on data quality checks?

## Current Dashboard Features

### Executive Overview

* Completed and verified callback count
* Total mantrap count
* Median response time
* Median repair time
* Monthly callback and mantrap trends
* Monthly response and repair time trends
* Top equipment risk ranking
* Top account risk ranking
* Fault-family callback distribution

### Equipment Risk

* Equipment-level risk scoring
* Risk tier classification
* Primary risk driver explanation
* Equipment monthly callback and mantrap trend
* Fault-family mix by selected equipment
* Equipment fault detail table

### Account Risk

* Account/site-level risk scoring
* Monthly callback and mantrap trend by selected account
* Fault-family mix by selected account
* Equipment under selected account ranked by risk
* Account risk explanation

### Fault Analysis

* Fault-family callback ranking
* Mantrap rate by fault family
* Monthly fault-family trend
* Monthly equipment-type trend

### Emerging Alerts

* Low-history equipment with early mantrap signals
* Emerging risk monitoring for assets with fewer completed callbacks

### Data Quality

* Total loaded records
* Completed and verified records
* Fault-code master match rate
* Missing fault-code count
* Invalid response-time rows
* Invalid repair-time rows
* Open, in-process, and rejected records
* Plain-English audit interpretation

## Project Architecture

```text
vt-rap/
├── app/
│   ├── streamlit_app.py
│   ├── components/
│   │   ├── cards.py
│   │   ├── charts.py
│   │   ├── filters.py
│   │   └── tables.py
│   ├── services/
│   │   └── data_loader.py
│   ├── styles/
│   │   └── theme.css
│   └── views/
│       ├── account_risk.py
│       ├── data_quality.py
│       ├── emerging_alerts.py
│       ├── equipment_risk.py
│       ├── executive.py
│       └── fault_analysis.py
├── configs/
├── data/
│   ├── raw/
│   │   ├── callbacks/
│   │   └── master/
│   ├── processed/
│   └── logs/
├── scripts/
│   ├── check_raw_files.py
│   └── run_pipeline.py
├── src/
│   ├── features/
│   │   ├── business_features.py
│   │   ├── fault_features.py
│   │   └── time_features.py
│   ├── ingestion/
│   │   ├── readers.py
│   │   └── schema.py
│   ├── models/
│   │   └── risk_scoring.py
│   ├── pipeline/
│   │   ├── build_gold.py
│   │   ├── build_raw.py
│   │   └── build_silver.py
│   └── utils/
├── tests/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Data Pipeline

The pipeline follows a raw-to-silver-to-gold structure.

### Raw Layer

Reads CRM callback reports and master/reference files from:

```text
data/raw/callbacks/
data/raw/master/
```

Raw callback reports are combined into one callback table with lineage fields:

* `source_file`
* `source_year`
* `source_row_number`

### Silver Layer

The silver layer standardizes operational callback records and creates analytical fields:

* Callback ID
* Account code
* Account name
* Equipment description
* Equipment type
* Fault code
* Fault family
* Status group
* Mantrap flag
* Event timestamp
* Attended timestamp
* Completed timestamp
* Response duration
* Repair duration
* Timing validity flags

### Gold Layer

The gold layer creates dashboard-ready outputs:

* `fault_family_summary`
* `equipment_risk_model`
* `account_risk_model`
* `emerging_equipment_alerts`
* `executive_summary`
* `data_quality_summary`
* `monthly_callback_trend`
* `monthly_fault_family_trend`
* `monthly_equipment_type_trend`
* `monthly_account_trend`
* `monthly_equipment_trend`
* `equipment_fault_family_mix`
* `account_fault_family_mix`

Outputs are saved as CSV and Parquet files in:

```text
data/processed/
```

A management Excel workbook is also generated:

```text
data/processed/vt_rap_management_outputs.xlsx
```

## Risk Scoring Approach

The project uses rule-based risk scoring for transparency and explainability.

### Equipment Risk Score

Equipment risk considers:

* Callback volume
* Callback frequency
* Mantrap count
* Mantrap rate
* Median repair duration
* Fault-family diversity
* Recent callback activity
* Recent mantrap activity

Each equipment record includes:

* Risk score
* Risk tier
* Risk signal type
* Primary risk driver
* Plain-English risk explanation

### Account Risk Score

Account risk considers:

* Total callback volume
* Callbacks per equipment
* Mantrap count
* Mantrap rate
* Median repair duration

Each account record includes:

* Risk score
* Risk tier
* Primary risk driver
* Plain-English risk explanation

## Data Quality Notes

The dashboard includes a data quality audit panel to make reporting more defensible.

Current validation checks include:

* Total callback records loaded
* Completed and verified record count
* Fault-code master match rate
* Missing fault-code count
* Invalid response-time row count
* Invalid repair-time row count
* Open or in-process row count
* Rejected row count

The dashboard separates completed/verified records from open, in-process, and rejected records to avoid mixing incomplete workflow records into management analytics.

## How to Run Locally

### 1. Clone the repository

```powershell
git clone https://github.com/muhd-muaz/vt-rap.git
cd vt-rap
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
pip install -e .
```

### 4. Create local data folders

```powershell
mkdir data\raw\callbacks, data\raw\master, data\processed, data\logs
```

### 5. Place raw data files locally

Callback reports should be placed in:

```text
data/raw/callbacks/
```

Master/reference files should be placed in:

```text
data/raw/master/
```

### 6. Run the backend pipeline

```powershell
python scripts/run_pipeline.py
```

### 7. Run the dashboard

```powershell
streamlit run app/streamlit_app.py
```

## Data Privacy

Company, client, equipment, callback, and operational data are intentionally excluded from Git.

The repository should only contain code and documentation. The following folders are ignored:

```text
data/raw/
data/processed/
data/logs/
```

Do not commit:

* Raw Excel files
* Processed CSV files
* Processed Parquet files
* Management Excel workbooks
* Screenshots containing confidential client or equipment information
* Environment files
* Virtual environment folders

## Current Limitations

* Fault-family classification currently depends mainly on recorded fault codes and the available fault-code master.
* Missing fault-code rows are marked as unclassified rather than inferred automatically.
* The risk scoring model is rule-based, not machine-learning based.
* Timing fields contain some invalid or negative durations, so validity flags are used.
* The current dashboard is a local Streamlit application, not a deployed production web application.
* The system does not yet include authentication, role-based access, or database persistence.

## Roadmap

Planned improvements:

* Add stronger data validation tests.
* Add monthly pipeline metadata and run history.
* Improve data quality audit charts.
* Add account and equipment search improvements.
* Add downloadable filtered outputs.
* Add configurable risk-score weights.
* Add missing fault-code review workflow.
* Add FastAPI backend layer.
* Consider a React or Next.js frontend for production deployment.
* Add database support for larger-scale refreshes.

## Technology Stack

* Python
* pandas
* NumPy
* Streamlit
* Plotly
* openpyxl
* PyArrow
* lxml
* html5lib
* BeautifulSoup

## Project Status

Current status: working local analytics prototype.

The backend pipeline successfully builds raw, silver, and gold outputs. The Streamlit dashboard provides executive overview, equipment risk, account risk, fault analysis, emerging alerts, and data quality views.
