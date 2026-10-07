"""
monitoring/checks/thresholds.py

Centralised threshold evaluation.

All thresholds come from monitoring/config.py which reads
environment variables – no silent violations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from monitoring.config import (
    MAX_NULL_PERCENTAGE,
    MAX_DUPLICATE_PERCENTAGE,
    MAX_DATA_STALENESS_HOURS_WARN,
    MAX_DATA_STALENESS_HOURS_CRITICAL,
    MAX_MODEL_AGE_DAYS_WARN,
    MAX_MODEL_AGE_DAYS_CRITICAL,
    MAX_API_LATENCY_MS,
    MIN_CHURN_ROC_AUC,
    MIN_CHURN_F1,
    MAX_FORECASTING_SMAPE,
    MIN_SEGMENTATION_SILHOUETTE,
    MIN_RECOMMENDATION_NDCG,
)
from monitoring.models import Alert


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Threshold definitions (name, direction, warn_value, critical_value)
# direction: "above" means value > threshold is bad
#            "below" means value < threshold is bad
# ---------------------------------------------------------------------------
THRESHOLDS: dict[str, dict] = {
    "null_percentage": {
        "direction": "above",
        "warn": MAX_NULL_PERCENTAGE,
        "critical": MAX_NULL_PERCENTAGE * 3,
        "unit": "%",
        "component": "data_quality",
    },
    "duplicate_percentage": {
        "direction": "above",
        "warn": MAX_DUPLICATE_PERCENTAGE,
        "critical": MAX_DUPLICATE_PERCENTAGE * 5,
        "unit": "%",
        "component": "data_quality",
    },
    "data_staleness_hours": {
        "direction": "above",
        "warn": MAX_DATA_STALENESS_HOURS_WARN,
        "critical": MAX_DATA_STALENESS_HOURS_CRITICAL,
        "unit": "hours",
        "component": "data_quality",
    },
    "model_age_days": {
        "direction": "above",
        "warn": MAX_MODEL_AGE_DAYS_WARN,
        "critical": MAX_MODEL_AGE_DAYS_CRITICAL,
        "unit": "days",
        "component": "ml",
    },
    "api_response_ms": {
        "direction": "above",
        "warn": MAX_API_LATENCY_MS,
        "critical": MAX_API_LATENCY_MS * 3,
        "unit": "ms",
        "component": "fastapi",
    },
    "churn_roc_auc": {
        "direction": "below",
        "warn": MIN_CHURN_ROC_AUC,
        "critical": MIN_CHURN_ROC_AUC * 0.85,
        "unit": "score",
        "component": "ml",
    },
    "churn_f1": {
        "direction": "below",
        "warn": MIN_CHURN_F1,
        "critical": MIN_CHURN_F1 * 0.85,
        "unit": "score",
        "component": "ml",
    },
    "forecasting_smape": {
        "direction": "above",
        "warn": MAX_FORECASTING_SMAPE,
        "critical": MAX_FORECASTING_SMAPE * 2,
        "unit": "%",
        "component": "ml",
    },
    "segmentation_silhouette": {
        "direction": "below",
        "warn": MIN_SEGMENTATION_SILHOUETTE,
        "critical": MIN_SEGMENTATION_SILHOUETTE * 0.5,
        "unit": "score",
        "component": "ml",
    },
    "recommendation_ndcg": {
        "direction": "below",
        "warn": MIN_RECOMMENDATION_NDCG,
        "critical": MIN_RECOMMENDATION_NDCG * 0.5,
        "unit": "score",
        "component": "ml",
    },
}


def evaluate(
    metric: str,
    value: Any,
    component: str | None = None,
) -> Alert | None:
    """
    Evaluate a single metric value against its registered thresholds.

    Returns an Alert if the value violates a threshold, else None.
    """
    spec = THRESHOLDS.get(metric)
    if spec is None:
        return None

    comp = component or spec.get("component", "unknown")
    direction = spec["direction"]
    warn_thresh = spec["warn"]
    crit_thresh = spec["critical"]

    if value is None:
        return None

    try:
        fval = float(value)
    except (TypeError, ValueError):
        return None

    severity = None
    threshold_used = None
    message = None

    if direction == "above":
        if fval > crit_thresh:
            severity = "CRITICAL"
            threshold_used = crit_thresh
            message = (
                f"{metric} value {fval:.3g} exceeds critical threshold "
                f"{crit_thresh:.3g} {spec.get('unit', '')}"
            )
        elif fval > warn_thresh:
            severity = "WARNING"
            threshold_used = warn_thresh
            message = (
                f"{metric} value {fval:.3g} exceeds warning threshold "
                f"{warn_thresh:.3g} {spec.get('unit', '')}"
            )
    else:  # "below"
        if fval < crit_thresh:
            severity = "CRITICAL"
            threshold_used = crit_thresh
            message = (
                f"{metric} value {fval:.3g} is below critical threshold "
                f"{crit_thresh:.3g} {spec.get('unit', '')}"
            )
        elif fval < warn_thresh:
            severity = "WARNING"
            threshold_used = warn_thresh
            message = (
                f"{metric} value {fval:.3g} is below warning threshold "
                f"{warn_thresh:.3g} {spec.get('unit', '')}"
            )

    if severity is None:
        return None

    return Alert(
        timestamp=_now_iso(),
        severity=severity,
        component=comp,
        metric=metric,
        value=round(fval, 6),
        threshold=threshold_used,
        message=message,
    )


def evaluate_all(metric_values: dict[str, Any]) -> list[Alert]:
    """Evaluate a mapping of metric_name → value and return all alerts."""
    alerts: list[Alert] = []
    for metric, value in metric_values.items():
        alert = evaluate(metric, value)
        if alert:
            alerts.append(alert)
    return alerts
