"""
tests/api/test_recommendation.py

Tests FastAPI product recommendations endpoint (/recommendations/{user_id}).
"""

import pytest


@pytest.mark.unit
@pytest.mark.api
def test_recommendations_valid(api_client):
    response = api_client.get("/recommendations/USER001?n=5&method=hybrid")
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert data["data"]["user_id"] == "USER001"
        assert data["data"]["method"] == "hybrid"
        assert len(data["data"]["recommendations"]) <= 5
    else:
        assert response.status_code == 503


@pytest.mark.unit
@pytest.mark.api
def test_recommendations_invalid_method(api_client):
    response = api_client.get("/recommendations/USER001?n=5&method=invalid_method_xyz")
    assert response.status_code in [400, 422]


@pytest.mark.unit
@pytest.mark.api
def test_recommendations_invalid_n(api_client):
    response = api_client.get("/recommendations/USER001?n=0")
    assert response.status_code in [400, 422]
