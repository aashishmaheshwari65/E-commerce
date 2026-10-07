import os
import pandas as pd
import numpy as np
from pathlib import Path
from api.services.model_loader import load_latest_model
from api.schemas.churn import ChurnPredictionRequest, BatchChurnPredictionRequest, ChurnPredictionData
from api.utils.errors import ResourceNotFoundError, InvalidInputError
from api import config

def get_risk_category(prob: float) -> str:
    """Categorize churn probability into risk category."""
    if prob < 0.30:
        return "low"
    elif prob < 0.60:
        return "medium"
    else:
        return "high"

def load_churn_features_df():
    """Load feature Parquet dataset for customer lookup."""
    priority_paths = [
        config.FEATURE_ROOT / "churn_features.parquet",
        config.DATA_ROOT / "churn_prediction" / "features" / "customer_features.parquet",
        config.FEATURE_ROOT / "customer_features.parquet"
    ]
    for p in priority_paths:
        if p.exists():
            return pd.read_parquet(p)
    return pd.DataFrame()

def predict_single_churn(request: ChurnPredictionRequest) -> ChurnPredictionData:
    """Perform churn prediction for a single customer or explicit feature vector."""
    loaded = load_latest_model("churn")
    model_obj = loaded["model"]

    feature_cols = ["total_orders", "total_spend", "recency_days", "average_items_per_order"]

    # Scenario A: Lookup customer by ID from dataset
    if request.customer_id and (request.total_orders is None or request.total_spend is None):
        df_features = load_churn_features_df()
        if df_features.empty:
            raise ResourceNotFoundError("Customer Dataset", request.customer_id)

        cust_col = "customer_id" if "customer_id" in df_features.columns else ("customer_key" if "customer_key" in df_features.columns else "user_id")
        cust_df = df_features[df_features[cust_col].astype(str) == str(request.customer_id)]

        if cust_df.empty:
            raise ResourceNotFoundError("Customer", request.customer_id)

        row = cust_df.iloc[0]
        input_data = {
            "total_orders": float(row.get("total_orders", row.get("frequency", 1))),
            "total_spend": float(row.get("total_spend", row.get("monetary_value", 100.0))),
            "recency_days": float(row.get("recency_days", 30)),
            "average_items_per_order": float(row.get("average_items_per_order", 2.0))
        }
        cust_id_label = str(request.customer_id)

    # Scenario B: Explicit feature input
    elif request.total_orders is not None and request.total_spend is not None:
        input_data = {
            "total_orders": float(request.total_orders),
            "total_spend": float(request.total_spend),
            "recency_days": float(request.recency_days if request.recency_days is not None else 30),
            "average_items_per_order": float(request.average_items_per_order if request.average_items_per_order is not None else 2.0)
        }
        cust_id_label = str(request.customer_id) if request.customer_id else "CUSTOM_INPUT"

    else:
        raise InvalidInputError("Must provide either a valid 'customer_id' or explicit customer features (total_orders, total_spend).")

    X_in = pd.DataFrame([input_data])[feature_cols]

    clf = model_obj.named_steps["classifier"] if hasattr(model_obj, "named_steps") and "classifier" in model_obj.named_steps else model_obj
    n_expected = getattr(clf, "n_features_in_", len(feature_cols))
    X_mat = X_in.iloc[:, :n_expected].values if X_in.shape[1] >= n_expected else X_in.values

    try:
        if hasattr(model_obj, "predict_proba"):
            try:
                probs = model_obj.predict_proba(X_in)
            except Exception:
                probs = model_obj.predict_proba(X_mat)
            prob = float(probs[0, 1]) if probs.shape[1] > 1 else float(probs[0, 0])
        elif hasattr(model_obj, "decision_function"):
            score = float(model_obj.decision_function(X_mat)[0])
            prob = 1.0 / (1.0 + np.exp(-score))
        else:
            pred = model_obj.predict(X_mat)[0]
            prob = float(pred)
    except Exception as e:
        raise InvalidInputError(f"Prediction error: {str(e)}")

    risk_cat = get_risk_category(prob)

    return ChurnPredictionData(
        customer_id=cust_id_label,
        churn_probability=round(prob, 4),
        risk_category=risk_cat
    )

def predict_batch_churn(request: BatchChurnPredictionRequest):
    """Perform batch churn prediction for a list of customer IDs."""
    results = []
    for cid in request.customer_ids:
        single_req = ChurnPredictionRequest(customer_id=cid)
        res = predict_single_churn(single_req)
        results.append(res)
    return results
