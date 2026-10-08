"""
tests/sales_forecasting/test_models.py

Tests regression model training, chronological split, and evaluation metrics (MAE, RMSE).
"""

import pytest
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


@pytest.mark.unit
@pytest.mark.ml
def test_forecasting_chronological_split_and_evaluation(sample_forecasting_dataset):
    df = sample_forecasting_dataset.copy()
    df["day_of_week"] = df["order_date"].dt.dayofweek
    df["lag_1"] = df["total_revenue"].shift(1)
    df = df.dropna().reset_index(drop=True)

    # Chronological train/test split (no random shuffle!)
    split_idx = int(len(df) * 0.8)
    train = df.iloc[:split_idx]
    test = df.iloc[split_idx:]

    features = ["day_of_week", "lag_1"]
    X_train, y_train = train[features], train["total_revenue"]
    X_test, y_test = test[features], test["total_revenue"]

    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    mae = float(mean_absolute_error(y_test, preds))
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))

    assert mae >= 0.0
    assert rmse >= 0.0
    assert len(preds) == len(test)
