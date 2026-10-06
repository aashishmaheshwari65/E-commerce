import pytest
import pandas as pd
import numpy as np
from recommendation_system.content_features import build_product_features, build_content_similarity

def test_build_product_features():
    products = pd.DataFrame({
        "product_id": ["P1", "P2", "P3"],
        "product_name": ["Wireless Headphones", "Bluetooth Speaker", "Running Shoes"],
        "category": ["Electronics", "Electronics", "Footwear"],
        "price": [99.99, 49.99, 79.99],
        "rating": [4.5, 4.0, 4.8]
    })

    tfidf, tfidf_mat, combined_mat = build_product_features(products)
    assert tfidf is not None
    assert tfidf_mat.shape[0] == 3
    assert combined_mat.shape[0] == 3

def test_build_content_similarity():
    products = pd.DataFrame({
        "product_id": ["P1", "P2", "P3"],
        "product_name": ["Wireless Headphones", "Bluetooth Speaker", "Running Shoes"],
        "category": ["Electronics", "Electronics", "Footwear"],
        "price": [99.99, 49.99, 79.99],
        "rating": [4.5, 4.0, 4.8]
    })

    sim_mat, p2i, i2p, _ = build_content_similarity(products)
    assert sim_mat.shape == (3, 3)
    assert p2i["P1"] == 0
    # P1 (Headphones, Electronics) should be more similar to P2 (Speaker, Electronics) than P3 (Shoes, Footwear)
    assert sim_mat[0, 1] > sim_mat[0, 2]
