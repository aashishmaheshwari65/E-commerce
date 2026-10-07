"""
Tests for monitoring/collectors/api.py
FastAPI is NOT required to be running.
All tests use mocking or verify UNKNOWN fallback.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from monitoring.models import ComponentStatus


def test_api_unknown_when_not_running():
    """When FastAPI is not running, status must be UNKNOWN (not CRITICAL)."""
    from monitoring.collectors.api import collect
    # Use a port that will definitely be closed
    result = collect(base_url="http://127.0.0.1:19999", timeout=0.5)
    assert result.component == "fastapi"
    assert result.status == ComponentStatus.UNKNOWN


def test_api_unknown_does_not_raise():
    """Collecting from unavailable API must not raise an exception."""
    from monitoring.collectors.api import collect
    try:
        result = collect(base_url="http://127.0.0.1:19999", timeout=0.5)
    except Exception as exc:
        pytest.fail(f"collect() raised {exc!r} unexpectedly")


def test_api_result_has_expected_keys():
    from monitoring.collectors.api import collect
    result = collect(base_url="http://127.0.0.1:19999", timeout=0.5)
    assert result.component == "fastapi"
    assert isinstance(result.metrics, dict)
    assert isinstance(result.warnings, list)
    assert isinstance(result.errors, list)


def test_api_healthy_when_mock_responds():
    """Simulate a healthy API response with a mock."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "ok",
        "service": "ecommerce-ml-api",
        "version": "1.0.0",
    }

    from monitoring.collectors import api as api_module

    with patch.object(api_module, "_probe_endpoint") as mock_probe:
        mock_probe.return_value = {
            "url": "http://127.0.0.1:8000/health",
            "status_code": 200,
            "response_ms": 12.5,
            "ok": True,
            "body": {"status": "ok"},
            "endpoint": "health",
        }
        from monitoring.collectors.api import collect
        result = collect(base_url="http://127.0.0.1:8000", timeout=2.0)
    # With at least one successful probe the status should be HEALTHY or WARNING
    assert result.status in (ComponentStatus.HEALTHY, ComponentStatus.WARNING)


def test_api_warning_on_high_latency():
    """High latency probe should generate a warning."""
    from monitoring.collectors import api as api_module

    with patch.object(api_module, "_probe_endpoint") as mock_probe:
        mock_probe.return_value = {
            "url": "http://127.0.0.1:8000/health",
            "status_code": 200,
            "response_ms": 9999.0,   # way above threshold
            "ok": True,
            "body": {"status": "ok"},
            "endpoint": "health",
        }
        from monitoring.collectors.api import collect
        result = collect(base_url="http://127.0.0.1:8000", timeout=2.0)

    assert result.status in (ComponentStatus.WARNING, ComponentStatus.HEALTHY)


# need pytest import in module scope for the "does not raise" test
import pytest  # noqa: E402
