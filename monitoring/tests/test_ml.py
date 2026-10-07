"""
Tests for monitoring/collectors/ml.py
Uses temporary directories with synthetic model artifacts.
Does NOT require real models or a running ML pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from monitoring.models import ComponentStatus


def _write_model_version(
    models_dir: Path,
    domain: str,
    version: str,
    metadata: dict,
) -> None:
    ver_dir = models_dir / domain / version
    ver_dir.mkdir(parents=True)
    (ver_dir / "metadata.json").write_text(
        json.dumps(metadata), encoding="utf-8"
    )
    (ver_dir / "model.joblib").write_bytes(b"FAKE_MODEL")


def _write_metrics(metrics_dir: Path, domain: str, metrics: dict) -> None:
    metrics_dir.mkdir(parents=True, exist_ok=True)
    (metrics_dir / f"{domain}_metrics.json").write_text(
        json.dumps(metrics), encoding="utf-8"
    )


@pytest.fixture()
def ml_dirs(tmp_path: Path):
    models_dir = tmp_path / "models"
    ml_pipeline_dir = tmp_path / "ml_pipeline"
    metrics_dir = ml_pipeline_dir / "metrics"

    # Churn model
    _write_model_version(
        models_dir,
        "churn",
        "20260101_120000",
        {
            "model_type": "churn",
            "model_name": "random_forest",
            "version": "20260101_120000",
            "training_timestamp": "2026-01-01T12:00:00",
            "feature_count": 4,
            "training_rows": 80,
        },
    )
    _write_metrics(
        metrics_dir,
        "churn",
        {
            "domain": "churn",
            "primary_metric": "roc_auc",
            "selected_model": "random_forest",
            "candidates": [
                {
                    "model_name": "random_forest",
                    "roc_auc": 0.95,
                    "pr_auc": 0.90,
                    "accuracy": 0.92,
                    "precision": 0.91,
                    "recall": 0.93,
                    "f1": 0.92,
                    "selected": True,
                }
            ],
        },
    )

    # Segmentation model
    _write_model_version(
        models_dir,
        "segmentation",
        "20260101_120000",
        {
            "model_type": "segmentation",
            "model_name": "kmeans_k3",
            "version": "20260101_120000",
            "training_timestamp": "2026-01-01T12:00:00",
            "feature_count": 5,
            "training_rows": 98,
        },
    )
    _write_metrics(
        metrics_dir,
        "segmentation",
        {
            "domain": "segmentation",
            "primary_metric": "silhouette_score",
            "selected_model": "kmeans_k3",
            "candidates": [
                {
                    "model_name": "kmeans_k3",
                    "k": 3,
                    "silhouette_score": 0.45,
                    "inertia": 80.0,
                    "selected": True,
                }
            ],
        },
    )

    return models_dir, ml_pipeline_dir


def test_collect_returns_component_result(ml_dirs):
    models_dir, ml_pipeline_dir = ml_dirs
    from monitoring.collectors.ml import collect
    result = collect(models_dir=models_dir, ml_pipeline_dir=ml_pipeline_dir)
    assert result.component == "ml"
    assert result.status in ComponentStatus.__members__.values()


def test_models_available_count(ml_dirs):
    models_dir, ml_pipeline_dir = ml_dirs
    from monitoring.collectors.ml import collect
    result = collect(models_dir=models_dir, ml_pipeline_dir=ml_pipeline_dir)
    # churn + segmentation = 2 available; forecasting + recommendation missing
    assert result.metrics["models_available"] >= 2


def test_churn_metrics_populated(ml_dirs):
    models_dir, ml_pipeline_dir = ml_dirs
    from monitoring.collectors.ml import collect
    result = collect(models_dir=models_dir, ml_pipeline_dir=ml_pipeline_dir)
    churn_info = next(
        d for d in result.metrics["domains"] if d["domain"] == "churn"
    )
    assert churn_info["model_available"] is True
    assert "roc_auc" in churn_info["metrics"]


def test_missing_domain_reported(ml_dirs):
    """forecasting has no model dir → model_available=False."""
    models_dir, ml_pipeline_dir = ml_dirs
    from monitoring.collectors.ml import collect
    result = collect(models_dir=models_dir, ml_pipeline_dir=ml_pipeline_dir)
    fc_info = next(
        d for d in result.metrics["domains"] if d["domain"] == "forecasting"
    )
    assert fc_info["model_available"] is False


def test_no_models_returns_critical_or_unknown(tmp_path):
    """Completely empty models directory → CRITICAL or UNKNOWN."""
    from monitoring.collectors.ml import collect
    result = collect(
        models_dir=tmp_path / "models",
        ml_pipeline_dir=tmp_path / "ml_pipeline",
    )
    assert result.status in (ComponentStatus.CRITICAL, ComponentStatus.UNKNOWN)
