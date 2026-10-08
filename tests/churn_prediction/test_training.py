"""
tests/churn_prediction/test_training.py

Tests RandomForestClassifier model training and metric computation for churn prediction.
"""

import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


@pytest.mark.unit
@pytest.mark.ml
def test_churn_model_training_and_metrics(sample_churn_dataset):
    X = sample_churn_dataset[["total_orders", "total_spend", "recency_days", "average_items_per_order"]]
    y = sample_churn_dataset["churn_label"]

    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(X, y)

    preds = clf.predict(X)

    acc = accuracy_score(y, preds)
    prec = precision_score(y, preds, zero_division=0)
    rec = recall_score(y, preds, zero_division=0)
    f1 = f1_score(y, preds, zero_division=0)

    assert 0.0 <= acc <= 1.0
    assert 0.0 <= prec <= 1.0
    assert 0.0 <= rec <= 1.0
    assert 0.0 <= f1 <= 1.0
