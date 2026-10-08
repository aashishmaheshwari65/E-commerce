"""
tests/api/test_forecasting.py

Tests FastAPI sales forecasting endpoint (/forecast).
"""

import pytest


@pytest.mark.unit
@pytest.mark.api
def test_forecast_valid(api_client):
    response = api_client.post("/forecast", json={"horizon": 7})
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert data["data"]["horizon"] == 7
        assert len(data["data"]["forecast"]) == 7
        assert "predicted_revenue" in data["data"]["forecast"][0]
    else:
        assert response.status_code == 503


@pytest.mark.unit
@pytest.mark.api
def test_forecast_invalid_horizon(api_client):
    response = api_client.post("/forecast", json={"horizon": 10})
    assert response.status_code in [400, 422]
