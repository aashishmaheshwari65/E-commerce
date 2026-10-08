"""
tests/ml_pipeline/test_evaluation.py

Tests ML evaluation metrics, including sMAPE, silhouette, and classification metrics.
"""

import pytest
import numpy as np
from ml_pipeline.evaluation_pipeline import smape


@pytest.mark.unit
@pytest.mark.ml
def test_smape_metric_calculation():
    y_true = np.array([100.0, 200.0, 300.0])
    y_pred = np.array([110.0, 190.0, 300.0])

    score = smape(y_true, y_pred)
    assert score >= 0.0
    assert isinstance(score, float)

    # Identical predictions must yield 0% error
    assert smape(y_true, y_true) == 0.0
