"""
tests/sales_forecasting/test_features.py

Tests time series feature engineering: calendar features, lag features, rolling statistics,
and leakage prevention.
"""

import pytest
import pandas as pd


@pytest.mark.unit
@pytest.mark.ml
def test_forecasting_lag_and_calendar_features(sample_forecasting_dataset):
    df = sample_forecasting_dataset.copy()

    # Calendar features
    df["day_of_week"] = df["order_date"].dt.dayofweek
    df["month"] = df["order_date"].dt.month

    # Lag features
    df["lag_1"] = df["total_revenue"].shift(1)
    df["lag_7"] = df["total_revenue"].shift(7)

    # Rolling features
    df["rolling_mean_7"] = df["total_revenue"].shift(1).rolling(window=7).mean()

    assert "day_of_week" in df.columns
    assert "month" in df.columns
    assert "lag_1" in df.columns
    assert "lag_7" in df.columns
    assert "rolling_mean_7" in df.columns

    # Verify no future leakage in lag_1 (lag_1 at row 1 equals row 0's value)
    assert df.loc[1, "lag_1"] == df.loc[0, "total_revenue"]
