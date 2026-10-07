import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_forecast_valid():
    response = client.post("/forecast", json={"horizon": 7})
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert data["data"]["horizon"] == 7
        assert len(data["data"]["forecast"]) == 7
        assert "predicted_revenue" in data["data"]["forecast"][0]
    else:
        assert response.status_code == 503

def test_forecast_invalid_horizon():
    response = client.post("/forecast", json={"horizon": 10})
    assert response.status_code in [400, 422]

def test_forecast_model_metadata():
    response = client.get("/forecast/model")
    assert response.status_code in [200, 503]
