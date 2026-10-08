"""
tests/monitoring/test_pipeline_monitoring.py

Tests pipeline health collector and Kafka NOT_CONFIGURED graceful behavior.
"""

from pathlib import Path
import pytest
from monitoring.collectors import pipelines, kafka
from monitoring.checks import health
from monitoring.models import ComponentResult, ComponentStatus


@pytest.mark.unit
def test_pipeline_collector(tmp_path: Path):
    result = pipelines.collect(data_root=tmp_path)
    assert result.component == "pipelines"
    assert result.status in (ComponentStatus.HEALTHY, ComponentStatus.WARNING, ComponentStatus.CRITICAL, ComponentStatus.UNKNOWN)
    assert "pipelines" in result.metrics


@pytest.mark.unit
def test_kafka_not_configured_when_unreachable():
    """Kafka is intentionally deferred; collector must report NOT_CONFIGURED without crashing."""
    result = kafka.collect(bootstrap_servers="localhost:9999")
    assert result.component == "kafka"
    assert result.status == ComponentStatus.NOT_CONFIGURED
    assert len(result.warnings) > 0
    assert result.errors == []


@pytest.mark.unit
def test_health_aggregation_with_not_configured():
    results = [
        ComponentResult(component="data_quality", status=ComponentStatus.HEALTHY, timestamp="2026-10-08T00:00:00Z"),
        ComponentResult(component="kafka", status=ComponentStatus.NOT_CONFIGURED, timestamp="2026-10-08T00:00:00Z"),
    ]
    snapshot = health.aggregate("run_1", results)
    # NOT_CONFIGURED components should not escalate to CRITICAL
    assert snapshot.overall_status == ComponentStatus.HEALTHY
