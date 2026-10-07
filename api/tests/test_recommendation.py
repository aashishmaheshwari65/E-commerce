import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_recommendations_valid():
    response = client.get("/recommendations/USER001?n=5&method=hybrid")
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert data["data"]["user_id"] == "USER001"
        assert data["data"]["method"] == "hybrid"
        assert len(data["data"]["recommendations"]) <= 5
    else:
        assert response.status_code == 503

def test_recommendations_invalid_method():
    response = client.get("/recommendations/USER001?n=5&method=invalid_method_xyz")
    assert response.status_code in [400, 422]

def test_recommendations_invalid_n():
    response = client.get("/recommendations/USER001?n=0")
    assert response.status_code in [400, 422]

def test_recommendation_model_metadata():
    response = client.get("/recommendations/model")
    assert response.status_code in [200, 503]
