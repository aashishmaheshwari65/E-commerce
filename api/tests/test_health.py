import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_get_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ecommerce-ml-api"
    assert data["version"] == "1.0.0"

def test_get_health_models():
    response = client.get("/health/models")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "models" in data
    assert "churn" in data["models"]
    assert "forecasting" in data["models"]
    assert "recommendation" in data["models"]
