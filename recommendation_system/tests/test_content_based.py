import pytest
import pandas as pd
from recommendation_system.content_features import build_content_similarity
from recommendation_system.content_based import recommend_content_based, recommend_content_based_for_product

def test_recommend_content_based_for_product():
    products = pd.DataFrame({
        "product_id": ["P1", "P2", "P3"],
        "product_name": ["Wireless Headphones", "Bluetooth Earbuds", "Running Shoes"],
        "category": ["Electronics", "Electronics", "Footwear"],
        "price": [99.99, 49.99, 79.99],
        "rating": [4.5, 4.0, 4.8]
    })

    sim_mat, p2i, i2p, _ = build_content_similarity(products)

    recs = recommend_content_based_for_product(
        product_id="P1",
        similarity_matrix=sim_mat,
        product_to_idx=p2i,
        idx_to_product=i2p,
        n=2
    )

    assert len(recs) >= 1
    # Top content match for P1 (Headphones) should be P2 (Earbuds)
    assert recs[0]["product_id"] == "P2"

def test_recommend_content_based_for_user():
    products = pd.DataFrame({
        "product_id": ["P1", "P2", "P3"],
        "product_name": ["Wireless Headphones", "Bluetooth Earbuds", "Running Shoes"],
        "category": ["Electronics", "Electronics", "Footwear"],
        "price": [99.99, 49.99, 79.99]
    })
    sim_mat, p2i, i2p, _ = build_content_similarity(products)

    interactions = pd.DataFrame({
        "user_id": ["U1"],
        "product_id": ["P1"],
        "interaction_score": [5.0]
    })

    recs = recommend_content_based(
        user_id="U1",
        interactions_df=interactions,
        similarity_matrix=sim_mat,
        product_to_idx=p2i,
        idx_to_product=i2p,
        n=10,
        exclude_purchased=True
    )

    assert len(recs) >= 1
    assert recs[0]["product_id"] == "P2"
