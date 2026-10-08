"""
tests/recommendation_system/test_hybrid.py

Tests hybrid score combination and normalization.
"""

import pytest
from recommendation_system.hybrid import normalize_scores


@pytest.mark.unit
@pytest.mark.ml
def test_normalize_scores_min_max():
    raw_scores = {"P1": 10.0, "P2": 20.0, "P3": 30.0}
    norm = normalize_scores(raw_scores)

    assert norm["P1"] == 0.0
    assert norm["P2"] == 0.5
    assert norm["P3"] == 1.0


@pytest.mark.unit
@pytest.mark.ml
def test_normalize_scores_empty_and_constant():
    assert normalize_scores({}) == {}
    constant = {"P1": 5.0, "P2": 5.0}
    norm_const = normalize_scores(constant)
    assert norm_const["P1"] == 1.0
    assert norm_const["P2"] == 1.0
