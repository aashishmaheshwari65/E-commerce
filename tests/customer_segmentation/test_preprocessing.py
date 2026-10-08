"""
tests/customer_segmentation/test_preprocessing.py

Tests feature preprocessing, scaling, and data hygiene for customer segmentation.
"""

import pytest
import numpy as np
from sklearn.preprocessing import StandardScaler


@pytest.mark.unit
@pytest.mark.ml
def test_preprocessing_and_scaling(sample_customer_features):
    features = sample_customer_features[["recency_days", "frequency", "monetary_value"]]
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    # Verify no NaN or infinite values
    assert not np.isnan(scaled).any()
    assert not np.isinf(scaled).any()

    # Verify mean is near 0 and variance is near 1
    assert np.allclose(scaled.mean(axis=0), 0, atol=1e-7)
    assert np.allclose(scaled.std(axis=0), 1, atol=1e-7)

    # Customer keys preserved in original DataFrame
    assert len(sample_customer_features["customer_key"]) == len(scaled)
