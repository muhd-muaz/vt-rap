# VT-RAP Sprint 2 Plan

## Goal

Stabilize VT-RAP after the dashboard presentation.

The focus is to make the system more trustworthy, repeatable, explainable, and safer for future refresh or deployment.

## Priority 1: validation hardening

Current issue:

The validation script still checks fixed historical metrics. When new callback data is added, validation can fail even when the pipeline works correctly.

Required improvement:

- Replace fixed row-count checks with consistency checks.
- Check that raw and silver tables are not empty.
- Check that silver row count matches raw row count.
- Check required columns exist.
- Check Gold tables are generated.
- Check key metrics are non-null and within sensible ranges.
- Keep strict checks only where values should never change.

Target commit:

```text
Make validation resilient to updated source data
