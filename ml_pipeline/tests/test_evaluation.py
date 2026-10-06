import pytest
import pandas as pd
import numpy as np
from ml_pipeline import training_pipeline, evaluation_pipeline

def test_evaluate_segmentation():
    df = pd.DataFrame({
        "recency_days": [10, 20, 30, 40, 50, 60],
        "frequency": [1, 2, 3, 4, 5, 6],
        "monetary_value": [100, 200, 300, 400, 500, 600]
    })
    train_out = training_pipeline.train_customer_segmentation(df)
    res = evaluation_pipeline.evaluate_segmentation(train_out)
    assert res["domain"] == "segmentation"
    assert "selected_model" in res
    assert len(res["candidates"]) == 3

def test_evaluate_churn():
    df = pd.DataFrame({
        "customer_id": [f"C{i}" for i in range(20)],
        "total_orders": np.random.randint(1, 10, size=20),
        "total_spend": np.random.uniform(50, 500, size=20),
        "recency_days": np.random.randint(5, 100, size=20),
        "average_items_per_order": np.random.uniform(1, 4, size=20),
        "churn_label": [0, 1] * 10
    })
    train_out = training_pipeline.train_churn_models(df)
    res = evaluation_pipeline.evaluate_churn(train_out)
    assert res["domain"] == "churn"
    assert "selected_model" in res
    assert res["primary_metric"] == "roc_auc"
