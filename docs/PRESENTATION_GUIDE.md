# VT-RAP Dashboard Presentation Guide

## Opening

Good afternoon. Today I will present VT-RAP, which stands for Vertical Transport Reliability Analytics Platform.

This project focuses on elevator callback data. The idea is simple: the company already has callback data, but raw data is hard to review directly. So I built a Python pipeline that cleans the data, enriches it, creates management-ready tables, and displays the output in a Streamlit dashboard.

## Problem

The data exists, but the insight is not ready yet.

Raw callback data usually has many rows and columns. It is difficult to quickly answer questions like:

- Which equipment is more risky?
- Which customer account has higher callback exposure?
- What fault happens the most?
- How many cases involve mantrap?
- Is the data clean enough for reporting?

VT-RAP acts as an analytics layer on top of the exported data.

## Pipeline

The system follows a Raw, Silver, and Gold pipeline.

Raw means the original exported data.

Silver is where the data is cleaned and enriched. This includes event time, attended time, completed time, response duration, repair duration, mantrap flag, fault-code mapping, account details, and equipment details.

Gold is the final dashboard-ready layer. It includes executive summary, equipment risk, account risk, fault summaries, emerging alerts, monthly trends, and data quality summary.

Simple version:

Raw is source data. Silver is cleaned and enriched data. Gold is dashboard-ready data.

## Demo flow

Start with All Time.

Then use Year 2025 as a full-year management review example.

Then use May 2026 as a recent monthly monitoring example.

This shows that the dashboard is not static. The same dashboard recalculates based on the selected period.

## Executive Overview

This page gives the high-level operational picture.

It summarizes analyzed callbacks, mantrap exposure, median response time, and median repair time.

Median is used because callback timing can have extreme values. Some jobs may take unusually long due to special cases, missing updates, or operational delay. Median gives a more stable typical value compared to average.

This page is like the "what is going on overall?" page.

## Equipment Risk

This page answers: which equipment should we pay attention to?

Instead of only counting callbacks, the system combines callback count, mantrap count, recent activity, and timing-related factors.

High risk does not mean the equipment is definitely faulty. It means the equipment shows stronger warning signals and should be reviewed.

## Account Risk

Equipment Risk tells us which unit is risky.

Account Risk tells us which customer account has higher exposure.

This is useful because one customer account can have multiple equipment units. So this page supports customer-level operational review and service planning.

## Fault Analysis

This page looks at fault data at two levels.

Fault family is useful for management summary, such as Door System, Controller, Safety Circuit, and so on.

Actual CRM fault code is useful for technical investigation.

VT-RAP does not replace the original fault code. It preserves the actual CRM code and adds fault family as an extra grouping layer.

## Emerging Alerts

This page is for early warning.

Emerging Alerts focuses on equipment that may not have a very long history yet, but already shows concerning signals.

For example, it may have recent callbacks, mantrap involvement, or a high emerging score.

This page does not say the equipment is definitely failing. It says the equipment is showing early warning behavior and should be reviewed.

## Emerging Interpretation panel

The Top Score shows the highest emerging alert score in the filtered data.

The Top Equipment shows which equipment has the strongest early warning signal.

The Linked Account tells us which customer account is related to that equipment.

The Main Driver explains why the system flagged it. For example, if the main driver is high mantrap rate, the alert is mainly pushed by mantrap-related behavior.

Alerts with Mantraps shows how many emerging-alert equipment records already have at least one mantrap event.

Simple version:

This page is like asking, "before this becomes a big problem, which equipment already looks suspicious?"

## Data Quality

This page checks whether the dashboard output can be trusted.

It tracks total records, completed or verified records, fault-code match rate, invalid response time, invalid repair time, and open or in-process records.

Analytics is only useful if the data behind it is reliable.

Invalid rows are not simply deleted because they are still useful for data quality monitoring.

## Why some columns are not shown

The dashboard is not meant to be a raw data viewer.

Some source columns are too operational, too detailed, repetitive, sensitive, or not directly useful for decision-making.

The raw data is not ignored. It is transformed.

The dashboard only shows fields that support the main business questions: callback volume, equipment risk, account risk, mantrap exposure, fault pattern, timing performance, emerging alerts, and data quality.

## Why Streamlit

Streamlit is suitable because the whole project is Python-based.

Since the pipeline is already built with Python, Streamlit allows the processed tables to be displayed quickly without building a separate frontend framework.

For production, the system would still need secure hosting, access control, and approved deployment.

## Why rule-based scoring

For this stage, rule-based scoring is used because it is explainable.

Machine learning would require proper labels, model validation, and business approval.

With rule-based scoring, the reason can be explained more clearly: callback volume, mantrap exposure, recency, and timing behavior.

## Limitations

The current risk score is rule-based and relative to the selected data cohort.

For future improvement, the scoring can be strengthened using fixed operational thresholds, historical baselines, and more stable equipment and account identifiers.

## Future enhancement

VT-RAP can be extended into an automated daily monitoring workflow.

At a scheduled time, such as 9:00 AM, Windows Task Scheduler can trigger a controlled export process from Exact Synergy, place the latest callback file into the VT-RAP input folder, run the full refresh pipeline, execute validation checks, update the processed outputs, and launch the Streamlit dashboard for daily operational review.

This would reduce manual refresh work and make VT-RAP closer to a daily reliability monitoring tool.

## Closing

To conclude, VT-RAP turns elevator callback records into a structured reliability analytics dashboard.

The main value is not only the dashboard interface, but the full processing flow behind it: data ingestion, cleaning, feature engineering, risk scoring, Gold table generation, validation, and interactive reporting.

It helps users review equipment risk, account risk, fault patterns, emerging alerts, and data quality from one place.
