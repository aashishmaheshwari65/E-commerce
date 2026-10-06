import pytest
import pandas as pd
from recommendation_system.collaborative import build_interaction_matrix, build_item_similarity, recommend_collaborative

def test_collaborative_recommendations():
    interactions = pd.DataFrame({
        "user_id": ["U1", "U1", "U2", "U2", "U3"],
        "product_id": ["P1", "P2", "P1", "P2", "P1"],
        "interaction_score": [5.0, 5.0, 5.0, 3.0, 4.0]
    })

    mat, u2i, i2u, p2i, i2p = build_interaction_matrix(interactions)
    assert mat.shape == (3, 2)
    assert u2i["U1"] == 0
    assert p2i["P1"] == 0

    item_sim = build_item_similarity(mat)
    assert item_sim.shape == (2, 2)

    # U3 interacted with P1, P1 & P2 co-occur in U1 & U2 -> should recommend P2 for U3
    recs = recommend_collaborative(
        user_id="U3",
        user_item_matrix=mat,
        item_similarity=item_sim,
        user_to_idx=u2i,
        idx_to_user=i2u,
        product_to_idx=p2i,
        idx_to_product=i2p,
        n=10,
        exclude_purchased=True
    )

    assert len(recs) == 1
    assert recs[0]["product_id"] == "P2"
    assert recs[0]["method"] == "collaborative"

def test_collaborative_cold_start_user():
    interactions = pd.DataFrame({
        "user_id": ["U1"],
        "product_id": ["P1"],
        "interaction_score": [5.0]
    })
    mat, u2i, i2u, p2i, i2p = build_interaction_matrix(interactions)
    item_sim = build_item_similarity(mat)

    recs = recommend_collaborative(
        user_id="UNKNOWN_USER",
        user_item_matrix=mat,
        item_similarity=item_sim,
        user_to_idx=u2i,
        idx_to_user=i2u,
        product_to_idx=p2i,
        idx_to_product=i2p
    )
    assert recs == []
