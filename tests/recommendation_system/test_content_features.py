"""
tests/recommendation_system/test_content_features.py

Tests product content feature extraction (TF-IDF and numerical scaling).
"""

import pytest
from recommendation_system.content_features import build_product_features


@pytest.mark.unit
@pytest.mark.ml
def test_build_product_features(sample_recommendation_interactions):
    products = sample_recommendation_interactions["products"]
    tfidf, tfidf_mat, combined_mat = build_product_features(products)

    assert tfidf is not None
    assert combined_mat.shape[0] == len(products)
