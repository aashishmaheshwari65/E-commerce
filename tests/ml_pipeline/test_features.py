"""
tests/ml_pipeline/test_features.py

Tests ML feature pipeline extraction and validation functions.
"""

import pytest
import pandas as pd
from ml_pipeline import feature_pipeline


@pytest.mark.unit
@pytest.mark.ml
def test_build_customer_features_synthetic():
    sales = pd.DataFrame({
        "customer_key": [1, 1, 2],
        "order_id": ["O1", "O2", "O3"],
        "net_sales": [100.0, 150.0, 200.0],
        "order_status": ["completed", "completed", "completed"]
    })
    data_dict = {"sales": sales}
    df = feature_pipeline.build_customer_features(data_dict)

    assert not df.empty
    assert "customer_id" in df.columns
    assert "recency_days" in df.columns
    assert "frequency" in df.columns
    assert "monetary_value" in df.columns
    assert len(df) == 2


@pytest.mark.unit
@pytest.mark.ml
def test_validate_features():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    assert feature_pipeline.validate_features(df, ["a", "b"]) is True

    with pytest.raises(ValueError):
        feature_pipeline.validate_features(df, ["a", "missing_col"])
