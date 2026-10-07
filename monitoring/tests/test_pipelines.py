"""
Tests for monitoring/collectors/pipelines.py
Does NOT require Airflow, Kafka, or any external service.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from monitoring.models import ComponentStatus


@pytest.fixture()
def minimal_data(tmp_path: Path) -> Path:
    """
    Build a minimal data directory tree with key artifacts.
    """
    # Warehouse fact
    facts_dir = tmp_path / "warehouse" / "facts"
    facts_dir.mkdir(parents=True)
    (facts_dir / "fact_sales.parquet").write_bytes(b"PARQUET")

    # Warehouse dimensions
    dims_dir = tmp_path / "warehouse" / "dimensions"
    dims_dir.mkdir(parents=True)
    (dims_dir / "dim_customer.parquet").write_bytes(b"PARQUET")

    # Gold lake
    gold_dir = tmp_path / "lake" / "gold"
    gold_dir.mkdir(parents=True)
    (gold_dir / "customer_sales.parquet").write_bytes(b"PARQUET")

    # ML pipeline runs
    ml_dir = tmp_path / "ml_pipeline"
    ml_dir.mkdir(parents=True)
    runs = [
        {
            "run_id": "20260101_120000",
            "start_time": "2026-01-01T12:00:00",
            "status": "success",
            "feature_status": "success",
            "training_status": "success",
            "evaluation_status": "success",
            "model_save_status": "success",
            "selected_models": {"churn": "random_forest"},
            "errors": [],
            "end_time": "2026-01-01T12:00:05",
            "duration_seconds": 5.0,
        }
    ]
    (ml_dir / "pipeline_runs.json").write_text(
        json.dumps(runs), encoding="utf-8"
    )

    return tmp_path


def test_collect_returns_component_result(minimal_data):
    from monitoring.collectors.pipelines import collect
    result = collect(
        data_root=minimal_data,
        lake_dir=minimal_data / "lake",
        warehouse_dir=minimal_data / "warehouse",
        ml_pipeline_dir=minimal_data / "ml_pipeline",
        segmentation_dir=minimal_data / "customer_segmentation",
        churn_dir=minimal_data / "churn_prediction",
        forecasting_dir=minimal_data / "sales_forecasting",
        recommendations_dir=minimal_data / "recommendations",
    )
    assert result.component == "pipelines"
    assert result.status in ComponentStatus.__members__.values()


def test_metrics_contain_pipelines_key(minimal_data):
    from monitoring.collectors.pipelines import collect
    result = collect(
        data_root=minimal_data,
        lake_dir=minimal_data / "lake",
        warehouse_dir=minimal_data / "warehouse",
        ml_pipeline_dir=minimal_data / "ml_pipeline",
        segmentation_dir=minimal_data / "customer_segmentation",
        churn_dir=minimal_data / "churn_prediction",
        forecasting_dir=minimal_data / "sales_forecasting",
        recommendations_dir=minimal_data / "recommendations",
    )
    assert "pipelines" in result.metrics
    assert isinstance(result.metrics["pipelines"], list)


def test_warehouse_detected(minimal_data):
    from monitoring.collectors.pipelines import collect
    result = collect(
        data_root=minimal_data,
        lake_dir=minimal_data / "lake",
        warehouse_dir=minimal_data / "warehouse",
        ml_pipeline_dir=minimal_data / "ml_pipeline",
        segmentation_dir=minimal_data / "customer_segmentation",
        churn_dir=minimal_data / "churn_prediction",
        forecasting_dir=minimal_data / "sales_forecasting",
        recommendations_dir=minimal_data / "recommendations",
    )
    wh = next(
        (p for p in result.metrics["pipelines"] if p["pipeline"] == "data_warehouse"),
        None,
    )
    assert wh is not None
    assert wh["fact_sales_exists"] is True


def test_ml_pipeline_run_detected(minimal_data):
    from monitoring.collectors.pipelines import collect
    result = collect(
        data_root=minimal_data,
        lake_dir=minimal_data / "lake",
        warehouse_dir=minimal_data / "warehouse",
        ml_pipeline_dir=minimal_data / "ml_pipeline",
        segmentation_dir=minimal_data / "customer_segmentation",
        churn_dir=minimal_data / "churn_prediction",
        forecasting_dir=minimal_data / "sales_forecasting",
        recommendations_dir=minimal_data / "recommendations",
    )
    ml = next(
        (p for p in result.metrics["pipelines"] if p["pipeline"] == "automated_ml_pipeline"),
        None,
    )
    assert ml is not None
    assert ml["status"] == "HEALTHY"


def test_missing_ml_runs_file_returns_unknown(tmp_path):
    from monitoring.collectors.pipelines import collect
    # No pipeline_runs.json → UNKNOWN for ml pipeline
    ml_dir = tmp_path / "ml_pipeline"
    ml_dir.mkdir()
    result = collect(
        data_root=tmp_path,
        lake_dir=tmp_path / "lake",
        warehouse_dir=tmp_path / "warehouse",
        ml_pipeline_dir=ml_dir,
        segmentation_dir=tmp_path / "customer_segmentation",
        churn_dir=tmp_path / "churn_prediction",
        forecasting_dir=tmp_path / "sales_forecasting",
        recommendations_dir=tmp_path / "recommendations",
    )
    ml = next(
        (p for p in result.metrics["pipelines"] if p["pipeline"] == "automated_ml_pipeline"),
        None,
    )
    assert ml is not None
    assert ml["status"] == "UNKNOWN"
