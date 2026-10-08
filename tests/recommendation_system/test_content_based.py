"""
tests/recommendation_system/test_content_based.py

Tests content-based recommendation logic given product similarity.
"""

import pytest
import numpy as np
from recommendation_system.content_based import recommend_content_based_for_product


@pytest.mark.unit
@pytest.mark.ml
def test_recommend_content_based_for_product():
    # 3x3 identity + off-diagonal similarity matrix
    sim = np.array([
        [1.0, 0.8, 0.2],
        [0.8, 1.0, 0.5],
        [0.2, 0.5, 1.0],
    ])
    p2i = {"1": 0, "2": 1, "3": 2}
    i2p = {0: "1", 1: "2", 2: "3"}

    recs = recommend_content_based_for_product("1", sim, p2i, i2p, n=2)

    assert len(recs) <= 2
    assert recs[0]["product_id"] == "2"
    assert recs[0]["score"] == 0.8
    assert recs[0]["method"] == "content"
