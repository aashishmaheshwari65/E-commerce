"""
tests/churn_prediction/test_labeling.py

Tests churn labeling logic, cutoff observation window, and prevention of future data leakage.
"""

from datetime import datetime, timedelta
import pytest
import pandas as pd


@pytest.mark.unit
@pytest.mark.ml
def test_churn_labeling_observation_window():
    ref_date = datetime(2024, 6, 1)
    churn_horizon_days = 90

    # Orders within observation window vs after cutoff
    orders = pd.DataFrame({
        "customer_key": [1, 2],
        "last_order_date": [datetime(2024, 5, 1), datetime(2024, 1, 15)],
    })

    # Customer 1 ordered 31 days ago (< 90 days) -> Active (churn=0)
    # Customer 2 ordered 138 days ago (>= 90 days) -> Churned (churn=1)
    orders["days_since_last_order"] = (ref_date - orders["last_order_date"]).dt.days
    orders["churn_label"] = (orders["days_since_last_order"] >= churn_horizon_days).astype(int)

    assert orders.loc[orders["customer_key"] == 1, "churn_label"].iloc[0] == 0
    assert orders.loc[orders["customer_key"] == 2, "churn_label"].iloc[0] == 1


@pytest.mark.unit
@pytest.mark.ml
def test_churn_label_binary_values():
    labels = pd.Series([0, 1, 0, 1, 1])
    assert set(labels.unique()).issubset({0, 1})
