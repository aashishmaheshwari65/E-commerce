"""
tests/api/test_churn.py

Tests FastAPI churn prediction endpoint (/churn/predict).
"""

import pytest


@pytest.mark.unit
@pytest.mark.api
def test_churn_predict_explicit_features(api_client):
    payload = {
        "total_orders": 5,
        "total_spend": 250.0,
        "recency_days": 10,
        "average_items_per_order": 2.5
    }
    response = api_client.post("/churn/predict", json=payload)
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert "churn_probability" in data["data"]
        assert data["data"]["risk_category"] in ["low", "medium", "high"]
    else:
        assert response.status_code == 503


@pytest.mark.unit
@pytest.mark.api
def test_churn_predict_invalid_input(api_client):
    payload = {}
    response = api_client.post("/churn/predict", json=payload)
    assert response.status_code in [400, 422, 503]


@pytest.mark.unit
@pytest.mark.api
def test_churn_predict_unknown_customer(api_client):
    payload = {"customer_id": "NON_EXISTENT_CUSTOMER_9999"}
    response = api_client.post("/churn/predict", json=payload)
    assert response.status_code in [404, 503]
