import os
from pathlib import Path
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from ml_pipeline import config
from ml_pipeline.pipeline_utils import get_logger
from ml_pipeline import feature_pipeline

logger = get_logger("training_pipeline")

def train_customer_segmentation(df=None):
    """
    Train candidate K-Means models for customer segmentation.
    Returns dictionary: {'models': {k: model_pipeline}, 'data': X_scaled, 'df': df}
    """
    if df is None:
        cust_path = config.FEATURE_ROOT / "customer_features.parquet"
        if cust_path.exists():
            df = pd.read_parquet(cust_path)
        else:
            df = feature_pipeline.build_customer_features()

    feature_cols = ["recency_days", "frequency", "monetary_value"]
    X = df[feature_cols].fillna(0.0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    candidate_k = [3, 4, 5]
    trained_models = {}

    for k in candidate_k:
        kmeans = KMeans(n_clusters=k, random_state=config.RANDOM_STATE, n_init=10)
        kmeans.fit(X_scaled)
        
        # Bundle with scaler in dict/tuple
        trained_models[f"kmeans_k{k}"] = {
            "scaler": scaler,
            "clusterer": kmeans,
            "k": k,
            "feature_cols": feature_cols
        }

    logger.info(f"Trained {len(trained_models)} K-Means candidate segmentation models.")
    return {
        "models": trained_models,
        "X_scaled": X_scaled,
        "feature_cols": feature_cols,
        "df": df
    }

def train_churn_models(df=None):
    """
    Train candidate classification models for customer churn prediction.
    Candidates: Logistic Regression, Random Forest, HistGradientBoosting.
    """
    if df is None:
        churn_path = config.FEATURE_ROOT / "churn_features.parquet"
        if churn_path.exists():
            df = pd.read_parquet(churn_path)
        else:
            df = feature_pipeline.build_churn_features()

    feature_cols = ["total_orders", "total_spend", "recency_days", "average_items_per_order"]
    X = df[feature_cols]
    y = df["churn_label"]

    # Stratified train test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=config.RANDOM_STATE, stratify=y if len(y.unique()) > 1 else None
    )

    candidates = {
        "logistic_regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(random_state=config.RANDOM_STATE, max_iter=500))
        ]),
        "random_forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", RandomForestClassifier(n_estimators=50, random_state=config.RANDOM_STATE, class_weight="balanced"))
        ]),
        "hist_gradient_boosting": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", HistGradientBoostingClassifier(random_state=config.RANDOM_STATE))
        ])
    }

    trained_models = {}
    for name, model_pipeline in candidates.items():
        model_pipeline.fit(X_train, y_train)
        trained_models[name] = model_pipeline

    logger.info(f"Trained {len(trained_models)} candidate churn prediction models.")
    return {
        "models": trained_models,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "feature_cols": feature_cols
    }

def train_sales_forecasting(df=None):
    """
    Train candidate regression models for sales forecasting.
    Candidates: Random Forest, HistGradientBoosting, Ridge.
    """
    if df is None:
        sales_path = config.FEATURE_ROOT / "sales_features.parquet"
        if sales_path.exists():
            df = pd.read_parquet(sales_path)
        else:
            df = feature_pipeline.build_sales_features()

    feature_cols = ["day_of_week", "month", "lag_1", "lag_7", "rolling_mean_7"]
    target_col = "total_revenue"

    X = df[feature_cols].fillna(0.0)
    y = df[target_col].fillna(0.0)

    # Time series / sequential train test split
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    candidates = {
        "random_forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("regressor", RandomForestRegressor(n_estimators=50, random_state=config.RANDOM_STATE))
        ]),
        "hist_gradient_boosting": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("regressor", HistGradientBoostingRegressor(random_state=config.RANDOM_STATE))
        ]),
        "ridge": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("regressor", Ridge())
        ])
    }

    trained_models = {}
    for name, model_pipeline in candidates.items():
        model_pipeline.fit(X_train, y_train)
        trained_models[name] = model_pipeline

    logger.info(f"Trained {len(trained_models)} candidate sales forecasting models.")
    return {
        "models": trained_models,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "feature_cols": feature_cols
    }

def train_recommendation_models(df=None):
    """
    Train candidate recommendation algorithms (Collaborative, Content, Hybrid, Popularity).
    Reuses recommendation_system functionality.
    """
    if df is None:
        rec_path = config.FEATURE_ROOT / "recommendation_features.parquet"
        if rec_path.exists():
            df = pd.read_parquet(rec_path)
        else:
            df = feature_pipeline.build_recommendation_features()

    from recommendation_system.collaborative import build_interaction_matrix, build_item_similarity
    from recommendation_system.content_features import build_content_similarity
    from recommendation_system.data_loader import load_products

    products_df = load_products()
    user_item_matrix, u2i, i2u, p2i, i2p = build_interaction_matrix(df)
    item_similarity = build_item_similarity(user_item_matrix)
    content_similarity, c_p2i, c_i2p, _ = build_content_similarity(products_df)

    models_bundle = {
        "collaborative": {
            "user_item_matrix": user_item_matrix,
            "item_similarity": item_similarity,
            "user_to_idx": u2i,
            "idx_to_user": i2u,
            "product_to_idx": p2i,
            "idx_to_product": i2p
        },
        "content": {
            "content_similarity": content_similarity,
            "content_p2i": c_p2i,
            "content_i2p": c_i2p
        },
        "hybrid": {
            "user_item_matrix": user_item_matrix,
            "item_similarity": item_similarity,
            "content_similarity": content_similarity,
            "user_to_idx": u2i,
            "idx_to_user": i2u,
            "product_to_idx": p2i,
            "idx_to_product": i2p,
            "content_p2i": c_p2i,
            "content_i2p": c_i2p
        },
        "popular": {
            "products_df": products_df,
            "interactions_df": df
        }
    }

    logger.info("Trained candidate recommendation models.")
    return {
        "models": models_bundle,
        "interactions_df": df,
        "products_df": products_df
    }

def train_all():
    """Execute training for all 4 ML domains."""
    return {
        "segmentation": train_customer_segmentation(),
        "churn": train_churn_models(),
        "forecasting": train_sales_forecasting(),
        "recommendation": train_recommendation_models()
    }
