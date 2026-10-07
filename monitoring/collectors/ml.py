"""
monitoring/collectors/ml.py

ML model monitoring collector for Functionality 20.

Inspects real model artifacts in data/models/ and real metrics
in data/ml_pipeline/metrics/.  Never invents metrics.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from monitoring.config import (
    MODELS_DIR,
    ML_PIPELINE_DIR,
    MAX_MODEL_AGE_DAYS_WARN,
    MAX_MODEL_AGE_DAYS_CRITICAL,
    MIN_CHURN_ROC_AUC,
    MIN_CHURN_F1,
    MAX_FORECASTING_SMAPE,
    MIN_SEGMENTATION_SILHOUETTE,
    MIN_RECOMMENDATION_NDCG,
)
from monitoring.models import ComponentResult, ComponentStatus

logger = logging.getLogger(__name__)

_DOMAINS = ["churn", "segmentation", "forecasting", "recommendation"]


def _age_days(ts_str: str) -> float | None:
    """Return age in days for an ISO timestamp string; None on failure."""
    try:
        ts = datetime.fromisoformat(ts_str)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - ts).total_seconds() / 86400.0
    except Exception:
        return None


def _newest_version(domain_dir: Path) -> Path | None:
    """Return the newest version sub-directory (by directory name sort)."""
    if not domain_dir.exists():
        return None
    versions = [d for d in domain_dir.iterdir() if d.is_dir()]
    if not versions:
        return None
    return sorted(versions)[-1]


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Failed to read %s: %s", path, exc)
        return None


def _check_domain(
    domain: str,
    models_dir: Path,
    metrics_dir: Path,
) -> dict[str, Any]:
    domain_dir = models_dir / domain
    version_dir = _newest_version(domain_dir)

    result: dict[str, Any] = {
        "domain": domain,
        "model_available": False,
        "version": None,
        "training_timestamp": None,
        "age_days": None,
        "age_status": "UNKNOWN",
        "selected_model": None,
        "feature_count": None,
        "training_rows": None,
        "metrics": {},
        "performance_status": "UNKNOWN",
        "warnings": [],
        "errors": [],
    }

    if version_dir is None:
        result["errors"].append(f"No model versions found for {domain}")
        return result

    result["model_available"] = True
    result["version"] = version_dir.name

    # Read metadata
    meta = _load_json(version_dir / "metadata.json")
    if meta:
        result["training_timestamp"] = meta.get("training_timestamp")
        result["selected_model"] = meta.get("model_name")
        result["feature_count"] = meta.get("feature_count")
        result["training_rows"] = meta.get("training_rows")

    # Age
    if result["training_timestamp"]:
        age_d = _age_days(result["training_timestamp"])
        if age_d is not None:
            result["age_days"] = round(age_d, 2)
            if age_d > MAX_MODEL_AGE_DAYS_CRITICAL:
                result["age_status"] = "CRITICAL"
                result["errors"].append(
                    f"{domain} model is {age_d:.1f} days old "
                    f"(threshold: {MAX_MODEL_AGE_DAYS_CRITICAL}d)"
                )
            elif age_d > MAX_MODEL_AGE_DAYS_WARN:
                result["age_status"] = "WARNING"
                result["warnings"].append(
                    f"{domain} model is {age_d:.1f} days old "
                    f"(threshold: {MAX_MODEL_AGE_DAYS_WARN}d)"
                )
            else:
                result["age_status"] = "HEALTHY"

    # Metrics
    metrics_file = metrics_dir / f"{domain}_metrics.json"
    metrics = _load_json(metrics_file)
    if metrics:
        selected_candidate = next(
            (
                c for c in metrics.get("candidates", [])
                if c.get("selected")
            ),
            None,
        )
        if selected_candidate:
            result["metrics"] = {
                k: v
                for k, v in selected_candidate.items()
                if k != "selected"
            }
            result["selected_model"] = selected_candidate.get("model_name")

    # Performance check per domain
    perf_ok = True
    m = result["metrics"]

    if domain == "churn":
        roc = m.get("roc_auc")
        f1 = m.get("f1")
        if roc is not None and roc < MIN_CHURN_ROC_AUC:
            result["warnings"].append(
                f"Churn ROC-AUC {roc:.3f} below threshold {MIN_CHURN_ROC_AUC}"
            )
            perf_ok = False
        if f1 is not None and f1 < MIN_CHURN_F1:
            result["warnings"].append(
                f"Churn F1 {f1:.3f} below threshold {MIN_CHURN_F1}"
            )
            perf_ok = False

    elif domain == "forecasting":
        smape = m.get("smape")
        if smape is not None and smape > MAX_FORECASTING_SMAPE:
            result["warnings"].append(
                f"Forecasting sMAPE {smape:.2f} exceeds threshold "
                f"{MAX_FORECASTING_SMAPE}"
            )
            perf_ok = False

    elif domain == "segmentation":
        sil = m.get("silhouette_score")
        if sil is not None and sil < MIN_SEGMENTATION_SILHOUETTE:
            result["warnings"].append(
                f"Segmentation silhouette {sil:.3f} below threshold "
                f"{MIN_SEGMENTATION_SILHOUETTE}"
            )
            perf_ok = False

    elif domain == "recommendation":
        ndcg = m.get("ndcg_10")
        if ndcg is not None and ndcg < MIN_RECOMMENDATION_NDCG:
            result["warnings"].append(
                f"Recommendation NDCG@10 {ndcg:.3f} below threshold "
                f"{MIN_RECOMMENDATION_NDCG}"
            )
            perf_ok = False

    if m:
        result["performance_status"] = "HEALTHY" if perf_ok else "WARNING"

    return result


def collect(
    models_dir: Path | None = None,
    ml_pipeline_dir: Path | None = None,
) -> ComponentResult:
    """Collect ML model health for all domains."""
    models_dir = models_dir or MODELS_DIR
    ml_pipeline_dir = ml_pipeline_dir or ML_PIPELINE_DIR
    metrics_dir = ml_pipeline_dir / "metrics"
    ts = datetime.now(timezone.utc).isoformat()

    domain_results: list[dict] = []
    all_warnings: list[str] = []
    all_errors: list[str] = []

    for domain in _DOMAINS:
        res = _check_domain(domain, models_dir, metrics_dir)
        domain_results.append(res)
        all_warnings.extend(res["warnings"])
        all_errors.extend(res["errors"])

    models_available = sum(
        1 for r in domain_results if r["model_available"]
    )

    if all_errors:
        status = ComponentStatus.CRITICAL
    elif all_warnings:
        status = ComponentStatus.WARNING
    elif models_available == 0:
        status = ComponentStatus.UNKNOWN
    else:
        status = ComponentStatus.HEALTHY

    return ComponentResult(
        component="ml",
        status=status,
        timestamp=ts,
        metrics={
            "models_available": models_available,
            "domains_checked": len(_DOMAINS),
            "domains": domain_results,
        },
        warnings=all_warnings,
        errors=all_errors,
    )
