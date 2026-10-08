"""
tests/churn_prediction/test_preprocessing.py

Tests data imputation and feature scaling pipeline for customer churn prediction.
"""

import pytest
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


@pytest.mark.unit
@pytest.mark.ml
def test_churn_imputer_and_scaler(sample_churn_dataset):
    X = sample_churn_dataset[["total_orders", "total_spend", "recency_days", "average_items_per_order"]].copy()

    # Introduce a missing value to test imputer robustness
    X.loc[0, "total_spend"] = np.nan

    preprocessor = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    transformed = preprocessor.fit_transform(X)

    assert not np.isnan(transformed).any()
    assert transformed.shape == X.shape
