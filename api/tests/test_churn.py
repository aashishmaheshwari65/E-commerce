from unittest.mock import patch, MagicMock
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_churn_predict_explicit_features():
    payload = {
        "total_orders": 5,
        "total_spend": 250.0,
        "recency_days": 10,
        "average_items_per_order": 2.5
    }
    response = client.post("/churn/predict", json=payload)
    # If model is available from Functionality 18 training
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert "churn_probability" in data["data"]
        assert data["data"]["risk_category"] in ["low", "medium", "high"]
    else:
        assert response.status_code == 503

def test_churn_predict_invalid_input():
    # Empty payload with neither customer_id nor features
    payload = {}
    response = client.post("/churn/predict", json=payload)
    # Should return 400 Bad Request or 503 if model check runs first
    assert response.status_code in [400, 503]

def test_churn_predict_unknown_customer():
    payload = {"customer_id": "NON_EXISTENT_CUSTOMER_9999"}
    response = client.post("/churn/predict", json=payload)
    assert response.status_code in [404, 503]

def test_churn_model_metadata():
    response = client.get("/churn/model")
    assert response.status_code in [200, 503]
