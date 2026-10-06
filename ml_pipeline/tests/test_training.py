import pytest
import pandas as pd
import numpy as np
from ml_pipeline import training_pipeline

def test_train_customer_segmentation():
    df = pd.DataFrame({
        "recency_days": [10, 20, 30, 40, 50, 60],
        "frequency": [1, 2, 3, 4, 5, 6],
        "monetary_value": [100, 200, 300, 400, 500, 600]
    })
    res = training_pipeline.train_customer_segmentation(df)
    assert "models" in res
    assert "kmeans_k3" in res["models"]
    assert "kmeans_k4" in res["models"]

def test_train_churn_models():
    df = pd.DataFrame({
        "customer_id": [f"C{i}" for i in range(20)],
        "total_orders": np.random.randint(1, 10, size=20),
        "total_spend": np.random.uniform(50, 500, size=20),
        "recency_days": np.random.randint(5, 100, size=20),
        "average_items_per_order": np.random.uniform(1, 4, size=20),
        "churn_label": [0, 1] * 10
    })
    res = training_pipeline.train_churn_models(df)
    assert "models" in res
    assert "logistic_regression" in res["models"]
    assert "random_forest" in res["models"]
    assert "hist_gradient_boosting" in res["models"]

def test_train_sales_forecasting():
    dates = pd.date_range("2025-01-01", periods=30)
    df = pd.DataFrame({
        "order_date": dates,
        "total_revenue": np.random.uniform(100, 1000, size=30),
        "day_of_week": dates.dayofweek,
        "month": dates.month,
        "lag_1": np.random.uniform(100, 1000, size=30),
        "lag_7": np.random.uniform(100, 1000, size=30),
        "rolling_mean_7": np.random.uniform(100, 1000, size=30)
    })
    res = training_pipeline.train_sales_forecasting(df)
    assert "models" in res
    assert "random_forest" in res["models"]
    assert "hist_gradient_boosting" in res["models"]
    assert "ridge" in res["models"]
