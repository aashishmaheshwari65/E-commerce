import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from api.services.model_loader import load_latest_model
from api.schemas.forecasting import ForecastItemData, ForecastData
from api.utils.errors import InvalidInputError
from api import config

def load_sales_features_df():
    """Load sales time series Parquet dataset."""
    priority_paths = [
        config.FEATURE_ROOT / "sales_features.parquet",
        config.DATA_ROOT / "sales_forecasting" / "aggregated" / "sales_daily.parquet"
    ]
    for p in priority_paths:
        if p.exists():
            return pd.read_parquet(p)
    return pd.DataFrame()

def generate_sales_forecast(horizon: int) -> ForecastData:
    """Generate sales revenue predictions for 7, 14, or 30 days ahead."""
    if horizon not in (7, 14, 30):
        raise InvalidInputError("Forecast horizon must be 7, 14, or 30 days.")

    loaded = load_latest_model("forecasting")
    model_obj = loaded["model"]

    df_sales = load_sales_features_df()

    if not df_sales.empty and "order_date" in df_sales.columns:
        last_date = pd.to_datetime(df_sales["order_date"]).max()
        history_rev = df_sales["total_revenue"].tolist()
    else:
        last_date = pd.to_datetime(datetime.now())
        history_rev = [500.0] * 14

    forecast_items = []
    curr_date = last_date
    history = list(history_rev)

    feature_cols = ["day_of_week", "month", "lag_1", "lag_7", "rolling_mean_7"]

    for i in range(1, horizon + 1):
        curr_date = curr_date + timedelta(days=1)
        dow = curr_date.dayofweek
        month = curr_date.month

        lag_1 = history[-1] if len(history) >= 1 else 500.0
        lag_7 = history[-7] if len(history) >= 7 else lag_1
        roll_7 = float(np.mean(history[-7:])) if len(history) >= 7 else lag_1

        X_step = pd.DataFrame([{
            "day_of_week": dow,
            "month": month,
            "lag_1": lag_1,
            "lag_7": lag_7,
            "rolling_mean_7": roll_7
        }])[feature_cols]

        pred_val = float(model_obj.predict(X_step)[0])
        pred_val = max(0.0, round(pred_val, 2))

        history.append(pred_val)

        forecast_items.append(ForecastItemData(
            date=curr_date.strftime("%Y-%m-%d"),
            predicted_revenue=pred_val
        ))

    return ForecastData(
        horizon=horizon,
        forecast=forecast_items
    )
