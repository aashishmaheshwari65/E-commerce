"""
tests/sales_forecasting/test_forecast.py

Tests forecast generation across 7, 14, and 30-day horizons, verifying shape and non-negativity.
"""

import pytest
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


@pytest.mark.unit
@pytest.mark.ml
@pytest.mark.parametrize("horizon", [7, 14, 30])
def test_forecast_horizon_and_non_negativity(sample_forecasting_dataset, horizon):
    df = sample_forecasting_dataset.copy()
    df["day_of_week"] = df["order_date"].dt.dayofweek
    df["lag_1"] = df["total_revenue"].shift(1)
    df = df.dropna().reset_index(drop=True)

    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(df[["day_of_week", "lag_1"]], df["total_revenue"])

    # Generate synthetic future horizon dates
    last_date = df["order_date"].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq="D")

    # Generate forecast
    future_df = pd.DataFrame({
        "order_date": future_dates,
        "day_of_week": future_dates.dayofweek,
        "lag_1": [df["total_revenue"].iloc[-1]] * horizon,
    })

    predictions = model.predict(future_df[["day_of_week", "lag_1"]])

    assert len(predictions) == horizon
    assert np.all(predictions >= 0.0), "Forecast predictions must be non-negative"
