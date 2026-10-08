"""
tests/recommendation_system/test_interactions.py

Tests interaction builder and user-item interaction scoring.
"""

import pytest
import pandas as pd
from recommendation_system.interaction_builder import build_interactions


@pytest.mark.unit
@pytest.mark.ml
def test_build_interactions(sample_recommendation_interactions):
    interactions = build_interactions(data_dict=sample_recommendation_interactions)

    assert not interactions.empty
    assert "user_id" in interactions.columns
    assert "product_id" in interactions.columns
    assert "interaction_score" in interactions.columns
    assert all(interactions["interaction_score"] > 0)
