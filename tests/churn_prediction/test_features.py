"""
tests/churn_prediction/test_features.py

Tests feature extraction for customer churn prediction.
"""

import pytest
import pandas as pd


@pytest.mark.unit
@pytest.mark.ml
def test_churn_feature_generation():
    sales = pd.DataFrame({
        "customer_key": [1, 1, 2, 2, 2],
        "order_id": [101, 102, 201, 202, 203],
        "quantity": [2, 3, 1, 1, 2],
        "net_sales": [100.0, 150.0, 50.0, 60.0, 90.0],
        "order_status": ["completed", "completed", "completed", "completed", "completed"],
    })

    cust = sales.groupby("customer_key").agg(
        total_orders=("order_id", "nunique"),
        total_spend=("net_sales", "sum"),
        total_items=("quantity", "sum"),
    ).reset_index()

    cust["average_items_per_order"] = cust["total_items"] / cust["total_orders"]

    assert len(cust) == 2
    c1 = cust[cust["customer_key"] == 1].iloc[0]
    assert c1["total_orders"] == 2
    assert c1["total_spend"] == 250.0
    assert c1["average_items_per_order"] == 2.5
