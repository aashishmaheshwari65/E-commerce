import pytest
import pandas as pd
from recommendation_system.interaction_builder import build_interactions

def test_build_interactions_custom_weights():
    purchases = pd.DataFrame({
        "user_id": ["U1", "U1", "U2"],
        "product_id": ["P1", "P2", "P1"],
        "quantity": [1, 2, 1],
        "line_total": [10.0, 20.0, 10.0]
    })
    reviews = pd.DataFrame({
        "user_id": ["U1"],
        "product_id": ["P1"],
        "rating": [5.0]
    })
    events = pd.DataFrame({
        "user_id": ["U1", "U2"],
        "product_id": ["P1", "P1"],
        "event_type": ["product_view", "add_to_cart"]
    })

    data_dict = {
        "purchases": purchases,
        "reviews": reviews,
        "events": events
    }

    custom_weights = {
        "product_view": 1.0,
        "search": 1.0,
        "add_to_cart": 3.0,
        "purchase": 5.0,
        "review": 4.0
    }

    df = build_interactions(data_dict, weights=custom_weights)
    assert not df.empty
    assert "interaction_score" in df.columns
    # U1-P1 score: purchase(1*5) + review(1*4) + view(1*1) = 10.0
    u1_p1 = df[(df["user_id"] == "U1") & (df["product_id"] == "P1")]
    assert len(u1_p1) == 1
    assert u1_p1["interaction_score"].values[0] == 10.0

def test_build_interactions_filters_invalid_ids():
    purchases = pd.DataFrame({
        "user_id": ["U1", None, ""],
        "product_id": ["P1", "P2", None],
        "quantity": [1, 1, 1],
        "line_total": [10.0, 10.0, 10.0]
    })
    data_dict = {"purchases": purchases}
    df = build_interactions(data_dict)
    assert len(df) == 1
    assert df["user_id"].iloc[0] == "U1"
    assert df["product_id"].iloc[0] == "P1"
