"""
tests/recommendation_system/test_recommendations.py

Tests end-to-end recommend() function: top-N, cold-start fallback, and purchased exclusion.
"""

import pytest
import pandas as pd
from recommendation_system.recommend import recommend


@pytest.mark.unit
@pytest.mark.ml
def test_recommend_known_user(sample_recommendation_interactions):
    df = recommend(
        user_id="1",
        n=2,
        method="hybrid",
        exclude_purchased=True,
        data_dict=sample_recommendation_interactions,
    )

    assert not df.empty
    assert len(df) <= 2
    for col in ["rank", "user_id", "product_id", "recommendation_score"]:
        assert col in df.columns
    assert pd.api.types.is_numeric_dtype(df["recommendation_score"])


@pytest.mark.unit
@pytest.mark.ml
def test_recommend_cold_start_unknown_user(sample_recommendation_interactions):
    df = recommend(
        user_id="UNKNOWN_USER_999",
        n=3,
        method="hybrid",
        data_dict=sample_recommendation_interactions,
    )

    assert not df.empty
    assert len(df) <= 3
    assert df["user_id"].iloc[0] == "UNKNOWN_USER_999"


@pytest.mark.unit
@pytest.mark.ml
def test_recommend_exclude_purchased_products(sample_recommendation_interactions):
    # User 1 purchased products 1 and 2 (3 unpurchased items remain)
    df = recommend(
        user_id="1",
        n=2,
        method="hybrid",
        exclude_purchased=True,
        data_dict=sample_recommendation_interactions,
    )

    if not df.empty:
        recommended_pids = set(df["product_id"].astype(str))
        assert "1" not in recommended_pids
        assert "2" not in recommended_pids
