"""
Tests for monitoring/checks/thresholds.py
"""

from __future__ import annotations

import pytest

from monitoring.checks.thresholds import evaluate, evaluate_all
from monitoring.models import Alert


def test_evaluate_returns_none_for_unknown_metric():
    result = evaluate("unknown_metric_xyz", 100)
    assert result is None


def test_evaluate_returns_none_when_value_is_none():
    result = evaluate("null_percentage", None)
    assert result is None


def test_evaluate_warning_above_warn_threshold():
    # null_percentage warn default = 5.0
    alert = evaluate("null_percentage", 6.0)
    assert alert is not None
    assert alert.severity == "WARNING"
    assert alert.metric == "null_percentage"
    assert alert.value == pytest.approx(6.0)


def test_evaluate_critical_above_critical_threshold():
    # null_percentage critical default = 15.0 (5 * 3)
    alert = evaluate("null_percentage", 20.0)
    assert alert is not None
    assert alert.severity == "CRITICAL"


def test_evaluate_no_alert_within_threshold():
    # null_percentage warn=5 → 2.0 should be fine
    alert = evaluate("null_percentage", 2.0)
    assert alert is None


def test_evaluate_below_direction_warning():
    # churn_roc_auc warn=0.70 → 0.68 below warn → WARNING
    alert = evaluate("churn_roc_auc", 0.68)
    assert alert is not None
    assert alert.severity == "WARNING"


def test_evaluate_below_direction_critical():
    # churn_roc_auc critical = 0.70 * 0.85 ≈ 0.595
    alert = evaluate("churn_roc_auc", 0.50)
    assert alert is not None
    assert alert.severity == "CRITICAL"


def test_evaluate_model_age_days_warn():
    # default warn = 7 days
    alert = evaluate("model_age_days", 8.0)
    assert alert is not None
    assert alert.severity == "WARNING"


def test_evaluate_api_latency_warn():
    # default warn = 500 ms
    alert = evaluate("api_response_ms", 600.0)
    assert alert is not None
    assert alert.severity == "WARNING"


def test_evaluate_all_returns_list():
    metrics = {
        "null_percentage": 0.5,   # fine
        "churn_roc_auc": 0.65,    # WARNING
        "api_response_ms": 200.0, # fine
    }
    alerts = evaluate_all(metrics)
    assert isinstance(alerts, list)
    # only churn_roc_auc should trigger
    assert any(a.metric == "churn_roc_auc" for a in alerts)


def test_alert_is_json_serializable():
    import json
    alert = evaluate("null_percentage", 10.0)
    assert alert is not None
    d = alert.to_dict()
    serialized = json.dumps(d)
    assert "null_percentage" in serialized
