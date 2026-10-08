"""
tests/ml_pipeline/test_training.py

Tests ML training pipeline functions across segmentation, churn, and forecasting.
"""

import pytest
import pandas as pd
from ml_pipeline.training_pipeline import train_customer_segmentation


@pytest.mark.unit
@pytest.mark.ml
def test_train_customer_segmentation():
    df = pd.DataFrame({
        "recency_days": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        "frequency": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
        "monetary_value": [100.0, 200.0, 300.0, 400.0, 500.0, 150.0, 250.0, 350.0, 450.0, 550.0],
    })
    res = train_customer_segmentation(df)

    assert "models" in res
    assert "kmeans_k3" in res["models"]
    assert "kmeans_k4" in res["models"]
    assert "kmeans_k5" in res["models"]
