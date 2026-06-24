from __future__ import annotations

from src.utils.risk_config import load_risk_config


def test_risk_config_contains_required_sections() -> None:
    config = load_risk_config()

    assert "equipment" in config
    assert "account" in config
    assert "emerging_alerts" in config


def test_equipment_weights_sum_to_one() -> None:
    config = load_risk_config()

    base_weights = config["equipment"]["base_weights"]
    final_weights = config["equipment"]["final_weights"]

    assert round(sum(base_weights.values()), 6) == 1
    assert round(sum(final_weights.values()), 6) == 1


def test_account_weights_sum_to_one() -> None:
    config = load_risk_config()

    base_weights = config["account"]["base_weights"]

    assert round(sum(base_weights.values()), 6) == 1


def test_risk_tier_labels_match_bins() -> None:
    config = load_risk_config()

    equipment_bins = config["equipment"]["tier_bins"]
    equipment_labels = config["equipment"]["tier_labels"]

    account_bins = config["account"]["tier_bins"]
    account_labels = config["account"]["tier_labels"]

    assert len(equipment_bins) == len(equipment_labels) + 1
    assert len(account_bins) == len(account_labels) + 1
