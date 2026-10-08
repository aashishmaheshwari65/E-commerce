"""
tests/churn_prediction/test_predictions.py

Tests probability predictions, boundary checks (0 to 1), and risk category buckets.
"""

import pytest
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from churn_prediction import config


@pytest.mark.unit
@pytest.mark.ml
def test_churn_probability_and_risk_categorization(sample_churn_dataset):
    X = sample_churn_dataset[["total_orders", "total_spend", "recency_days", "average_items_per_order"]]
    y = sample_churn_dataset["churn_label"]

    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(X, y)

    probs = clf.predict_proba(X)[:, 1]

    # Verify probability range [0, 1]
    assert np.all(probs >= 0.0)
    assert np.all(probs <= 1.0)

    # Risk categorization logic
    risk_categories = np.where(
        probs < config.LOW_RISK_THRESHOLD,
        "Low Risk",
        np.where(probs >= config.HIGH_RISK_THRESHOLD, "High Risk", "Medium Risk")
    )

    valid_categories = {"Low Risk", "Medium Risk", "High Risk"}
    assert set(risk_categories).issubset(valid_categories)
