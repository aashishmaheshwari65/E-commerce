"""
Tests for monitoring/collectors/kafka.py

Kafka is NOT running in this project.
All tests must pass when Kafka is unavailable.
"""

from __future__ import annotations

from monitoring.models import ComponentStatus


def test_kafka_not_configured_when_unreachable():
    """
    Kafka collector must return NOT_CONFIGURED, not CRITICAL,
    when the broker cannot be reached.
    """
    from monitoring.collectors.kafka import collect
    result = collect(bootstrap_servers="localhost:9999")  # nothing running there
    assert result.component == "kafka"
    assert result.status == ComponentStatus.NOT_CONFIGURED


def test_kafka_result_has_warnings_not_errors():
    """
    A missing Kafka should produce warnings (not errors),
    so it doesn't escalate to system-wide CRITICAL.
    """
    from monitoring.collectors.kafka import collect
    result = collect(bootstrap_servers="localhost:9999")
    assert len(result.warnings) >= 1
    # errors list must be empty – Kafka absence is not a critical error
    assert len(result.errors) == 0


def test_kafka_metrics_dict_present():
    from monitoring.collectors.kafka import collect
    result = collect(bootstrap_servers="localhost:9999")
    assert isinstance(result.metrics, dict)


def test_kafka_timestamp_is_set():
    from monitoring.collectors.kafka import collect
    result = collect(bootstrap_servers="localhost:9999")
    assert result.timestamp is not None
    assert "T" in result.timestamp  # ISO format check


def test_kafka_to_dict_serializable():
    from monitoring.collectors.kafka import collect
    import json
    result = collect(bootstrap_servers="localhost:9999")
    d = result.to_dict()
    # Must be JSON-serializable
    serialized = json.dumps(d)
    assert "kafka" in serialized
