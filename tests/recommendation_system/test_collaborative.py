"""
tests/recommendation_system/test_collaborative.py

Tests collaborative filtering user-item matrix construction and indexing.
"""

import pytest
from recommendation_system.interaction_builder import build_interactions
from recommendation_system.collaborative import build_interaction_matrix


@pytest.mark.unit
@pytest.mark.ml
def test_build_interaction_matrix(sample_recommendation_interactions):
    interactions = build_interactions(data_dict=sample_recommendation_interactions)
    mat, u2i, i2u, p2i, i2p = build_interaction_matrix(interactions)

    assert mat.shape[0] == len(u2i)
    assert mat.shape[1] == len(p2i)
    assert len(u2i) > 0
    assert len(p2i) > 0
