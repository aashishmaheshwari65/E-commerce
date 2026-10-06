import pytest
import pandas as pd
from recommendation_system.collaborative import build_interaction_matrix, build_item_similarity
from recommendation_system.content_features import build_content_similarity
from recommendation_system.hybrid import recommend_hybrid, normalize_scores

def test_normalize_scores():
    raw_scores = {"P1": 10.0, "P2": 5.0, "P3": 0.0}
    norm = normalize_scores(raw_scores)
    assert norm["P1"] == 1.0
    assert norm["P3"] == 0.0
    assert norm["P2"] == 0.5

def test_hybrid_recommendation():
    products = pd.DataFrame({
        "product_id": ["P1", "P2", "P3"],
        "product_name": ["Wireless Headphones", "Bluetooth Earbuds", "Running Shoes"],
        "category": ["Electronics", "Electronics", "Footwear"],
        "price": [99.99, 49.99, 79.99]
    })
    cnt_sim, c_p2i, c_i2p, _ = build_content_similarity(products)

    interactions = pd.DataFrame({
        "user_id": ["U1", "U1", "U2"],
        "product_id": ["P1", "P3", "P1"],
        "interaction_score": [5.0, 5.0, 5.0]
    })

    mat, u2i, i2u, p2i, i2p = build_interaction_matrix(interactions)
    item_sim = build_item_similarity(mat)

    recs = recommend_hybrid(
        user_id="U2",
        user_item_matrix=mat,
        item_similarity=item_sim,
        content_similarity=cnt_sim,
        user_to_idx=u2i,
        idx_to_user=i2u,
        product_to_idx=p2i,
        idx_to_product=i2p,
        interactions_df=interactions,
        n=10,
        collaborative_weight=0.6,
        content_weight=0.4,
        exclude_purchased=True
    )

    assert len(recs) >= 1
    assert "collaborative_score" in recs[0]
    assert "content_score" in recs[0]
    assert recs[0]["recommendation_method"] == "hybrid"
