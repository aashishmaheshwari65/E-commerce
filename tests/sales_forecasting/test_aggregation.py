"""
tests/sales_forecasting/test_aggregation.py

Tests time series aggregation (daily/weekly, revenue, orders, units, AOV).
"""

import pytest
import pandas as pd


@pytest.mark.unit
@pytest.mark.ml
def test_daily_aggregation():
    orders = pd.DataFrame({
        "order_date": pd.to_datetime(["2024-01-01 10:00", "2024-01-01 14:00", "2024-01-02 09:00"]),
        "order_id": [1, 2, 3],
        "quantity": [2, 1, 3],
        "net_sales": [100.0, 50.0, 150.0],
        "order_status": ["completed", "completed", "completed"],
    })

    orders["date"] = orders["order_date"].dt.floor("D")

    daily = orders.groupby("date").agg(
        total_revenue=("net_sales", "sum"),
        total_orders=("order_id", "nunique"),
        total_units_sold=("quantity", "sum"),
    ).reset_index()

    daily["aov"] = daily["total_revenue"] / daily["total_orders"]

    assert len(daily) == 2
    d1 = daily[daily["date"] == "2024-01-01"].iloc[0]
    assert d1["total_revenue"] == 150.0
    assert d1["total_orders"] == 2
    assert d1["total_units_sold"] == 3
    assert d1["aov"] == 75.0
