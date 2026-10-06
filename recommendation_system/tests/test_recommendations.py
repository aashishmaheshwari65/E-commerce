import pytest
import pandas as pd
from recommendation_system.recommend import recommend

def test_recommend_api_known_user():
    products = pd.DataFrame({
        "product_id": ["P1", "P2", "P3"],
        "product_name": ["Wireless Headphones", "Bluetooth Earbuds", "Running Shoes"],
        "category": ["Electronics", "Electronics", "Footwear"],
        "price": [99.99, 49.99, 79.99],
        "rating": [4.5, 4.0, 4.8],
        "stock": [10, 5, 0]
    })
    purchases = pd.DataFrame({
        "user_id": ["U1", "U2"],
        "product_id": ["P1", "P1"],
        "quantity": [1, 1],
        "line_total": [99.99, 99.99]
    })

    data_dict = {
        "products": products,
        "purchases": purchases
    }

    df = recommend(
        user_id="U2",
        n=2,
        method="hybrid",
        exclude_purchased=True,
        data_dict=data_dict
    )

    assert not df.empty
    assert len(df) <= 2
    required_cols = ["rank", "user_id", "product_id", "product_name", "category", "price", "rating", "recommendation_score", "recommendation_method"]
    for col in required_cols:
        assert col in df.columns

def test_recommend_api_unknown_user_cold_start():
    products = pd.DataFrame({
        "product_id": ["P1", "P2"],
        "product_name": ["Widget A", "Widget B"],
        "category": ["Misc", "Misc"],
        "price": [10.0, 20.0],
        "rating": [4.0, 5.0],
        "stock": [10, 10]
    })
    data_dict = {"products": products}

    df = recommend(
        user_id="UNKNOWN_USER_123",
        n=2,
        method="hybrid",
        data_dict=data_dict
    )

    assert not df.empty
    assert len(df) == 2
    assert df["user_id"].iloc[0] == "UNKNOWN_USER_123"
    assert df["recommendation_method"].iloc[0] == "popular"
