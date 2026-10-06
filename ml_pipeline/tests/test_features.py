import pytest
import pandas as pd
import numpy as np
from ml_pipeline import feature_pipeline

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

def test_build_churn_features():
    df = feature_pipeline.build_churn_features()
    assert not df.empty
    assert "churn_label" in df.columns
    assert "total_orders" in df.columns
    assert "total_spend" in df.columns

def test_validate_features_pass():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    assert feature_pipeline.validate_features(df, ["a", "b"]) is True

def test_validate_features_fail():
    df = pd.DataFrame({"a": [1, 2]})
    with pytest.raises(ValueError):
        feature_pipeline.validate_features(df, ["a", "b"])

def test_validate_features_empty():
    df = pd.DataFrame()
    with pytest.raises(ValueError):
        feature_pipeline.validate_features(df, ["a"])
