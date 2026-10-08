"""
tests/monitoring/test_ml_monitoring.py

Tests ML monitoring collector for model metrics and staleness evaluation.
"""

from pathlib import Path
import pytest
from monitoring.collectors import ml
from monitoring.checks import thresholds
from monitoring.models import ComponentStatus


@pytest.mark.unit
def test_ml_collector_empty_dir(tmp_path: Path):
    result = ml.collect(models_dir=tmp_path / "models", ml_pipeline_dir=tmp_path / "ml_pipeline")
    assert result.component == "ml"
    assert result.status in (ComponentStatus.CRITICAL, ComponentStatus.UNKNOWN)


@pytest.mark.unit
def test_threshold_evaluation_model_age():
    # If model is 15 days old (> 7d warn, < 30d critical) -> WARNING alert
    alert = thresholds.evaluate("model_age_days", 15.0, "ml")
    assert alert is not None
    assert alert.severity == "WARNING"
    assert alert.component == "ml"

    # If model is 45 days old (> 30d critical) -> CRITICAL alert
    alert_crit = thresholds.evaluate("model_age_days", 45.0, "ml")
    assert alert_crit is not None
    assert alert_crit.severity == "CRITICAL"
