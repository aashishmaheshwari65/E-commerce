"""
tests/customer_segmentation/test_features.py

Tests RFM feature extraction (recency, frequency, monetary value).
"""

import pytest
import pandas as pd


@pytest.mark.unit
@pytest.mark.ml
def test_rfm_calculation_from_sales():
    fact_sales = pd.DataFrame({
        "customer_key": [1, 1, 2, 3],
        "order_id": [101, 102, 201, 301],
        "net_sales": [100.0, 50.0, 200.0, 80.0],
        "order_status": ["completed", "completed", "completed", "cancelled"],
    })

    valid_sales = fact_sales[fact_sales["order_status"] != "cancelled"]

    rfm = valid_sales.groupby("customer_key").agg(
        frequency=("order_id", "nunique"),
        monetary_value=("net_sales", "sum"),
    ).reset_index()

    assert len(rfm) == 2
    c1 = rfm[rfm["customer_key"] == 1].iloc[0]
    assert c1["frequency"] == 2
    assert c1["monetary_value"] == 150.0

    c2 = rfm[rfm["customer_key"] == 2].iloc[0]
    assert c2["frequency"] == 1
    assert c2["monetary_value"] == 200.0
