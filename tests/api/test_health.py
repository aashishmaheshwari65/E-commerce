"""
tests/api/test_health.py

Tests FastAPI health endpoints (/health, /health/models).
"""

import pytest


@pytest.mark.unit
@pytest.mark.api
def test_get_health(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ecommerce-ml-api"
    assert data["version"] == "1.0.0"


@pytest.mark.unit
@pytest.mark.api
def test_get_health_models(api_client):
    response = api_client.get("/health/models")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "models" in data
    assert "churn" in data["models"]
    assert "forecasting" in data["models"]
    assert "recommendation" in data["models"]
