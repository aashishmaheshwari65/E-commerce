"""
tests/monitoring/test_api_monitoring.py

Tests FastAPI monitoring collector and offline fallback behavior.
"""

from unittest.mock import MagicMock, patch
import pytest
from monitoring.collectors import api
from monitoring.models import ComponentStatus


@pytest.mark.unit
def test_api_collector_offline():
    """When API is unreachable, collector gracefully returns UNKNOWN status."""
    result = api.collect(base_url="http://127.0.0.1:9999")
    assert result.component == "fastapi"
    assert result.status == ComponentStatus.UNKNOWN
    assert len(result.warnings) > 0


@pytest.mark.unit
def test_api_collector_online_mock():
    mock_health = MagicMock(status_code=200, elapsed=MagicMock(total_seconds=lambda: 0.015))
    mock_models = MagicMock(status_code=200, elapsed=MagicMock(total_seconds=lambda: 0.020))

    with patch("requests.get", side_effect=[mock_health, mock_models]):
        result = api.collect(base_url="http://127.0.0.1:8000")
        assert result.component == "fastapi"
        assert result.status == ComponentStatus.HEALTHY
        assert result.metrics["reachable"] is True
        assert result.metrics["endpoints_probed"] > 0
