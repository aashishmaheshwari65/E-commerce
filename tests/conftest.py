"""
tests/conftest.py

Shared pytest fixtures for the E-Commerce platform test suite.
All fixtures are deterministic and isolated in memory or temporary directories.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import pytest
import pandas as pd
import numpy as np

# Ensure safe fallback DATABASE_URL for isolated testing environments (such as CI/CD) if not set
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Root directory of tests
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Path to static CSV fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def sample_users_df(fixtures_dir: Path) -> pd.DataFrame:
    """Sample users DataFrame loaded from fixture."""
    return pd.read_csv(fixtures_dir / "users.csv")


@pytest.fixture
def sample_products_df(fixtures_dir: Path) -> pd.DataFrame:
    """Sample products DataFrame loaded from fixture."""
    return pd.read_csv(fixtures_dir / "products.csv")


@pytest.fixture
def sample_orders_df(fixtures_dir: Path) -> pd.DataFrame:
    """Sample orders DataFrame loaded from fixture."""
    return pd.read_csv(fixtures_dir / "orders.csv")


@pytest.fixture
def sample_order_items_df(fixtures_dir: Path) -> pd.DataFrame:
    """Sample order_items DataFrame loaded from fixture."""
    return pd.read_csv(fixtures_dir / "order_items.csv")


@pytest.fixture
def sample_payments_df(fixtures_dir: Path) -> pd.DataFrame:
    """Sample payments DataFrame loaded from fixture."""
    return pd.read_csv(fixtures_dir / "payments.csv")


@pytest.fixture
def sample_reviews_df(fixtures_dir: Path) -> pd.DataFrame:
    """Sample reviews DataFrame loaded from fixture."""
    return pd.read_csv(fixtures_dir / "reviews.csv")


@pytest.fixture
def sample_user_events_df(fixtures_dir: Path) -> pd.DataFrame:
    """Sample user_events DataFrame loaded from fixture."""
    return pd.read_csv(fixtures_dir / "user_events.csv")


@pytest.fixture
def temp_raw_dir(tmp_path: Path, fixtures_dir: Path) -> Path:
    """
    Creates a temporary directory with all raw CSV fixture files.
    """
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    for csv_file in fixtures_dir.glob("*.csv"):
        shutil.copy(csv_file, raw_dir / csv_file.name)
    return raw_dir


@pytest.fixture
def temp_processed_dir(tmp_path: Path, fixtures_dir: Path) -> Path:
    """
    Creates a temporary directory with transformed clean processed CSVs for SilverLayer / ETL tests.
    """
    from etl.transform import DataTransformer
    transformer = DataTransformer()

    processed_dir = tmp_path / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    users = transformer.transform_users(pd.read_csv(fixtures_dir / "users.csv"))
    products = transformer.transform_products(pd.read_csv(fixtures_dir / "products.csv"))
    orders = transformer.transform_orders(pd.read_csv(fixtures_dir / "orders.csv"))
    order_items = transformer.transform_order_items(pd.read_csv(fixtures_dir / "order_items.csv"))
    payments = transformer.transform_payments(pd.read_csv(fixtures_dir / "payments.csv"))
    reviews = transformer.transform_reviews(pd.read_csv(fixtures_dir / "reviews.csv"))
    events = transformer.transform_events(pd.read_csv(fixtures_dir / "user_events.csv"))

    users.to_csv(processed_dir / "users_clean.csv", index=False)
    products.to_csv(processed_dir / "products_clean.csv", index=False)
    orders.to_csv(processed_dir / "orders_clean.csv", index=False)
    order_items.to_csv(processed_dir / "order_items_clean.csv", index=False)
    payments.to_csv(processed_dir / "payments_clean.csv", index=False)
    reviews.to_csv(processed_dir / "reviews_clean.csv", index=False)
    events.to_csv(processed_dir / "user_events_clean.csv", index=False)

    return processed_dir


@pytest.fixture
def sample_customer_features() -> pd.DataFrame:
    """Synthetic customer features for segmentation & churn tests."""
    return pd.DataFrame({
        "customer_key": [1, 2, 3, 4, 5],
        "recency_days": [10, 45, 120, 15, 90],
        "frequency": [5, 2, 1, 6, 2],
        "monetary_value": [550.0, 120.0, 40.0, 720.0, 180.0],
    })


@pytest.fixture
def sample_churn_dataset() -> pd.DataFrame:
    """Deterministic customer features with binary churn labels."""
    return pd.DataFrame({
        "customer_key": [1, 2, 3, 4, 5, 6],
        "total_orders": [5, 1, 1, 6, 2, 1],
        "total_spend": [550.0, 40.0, 30.0, 720.0, 180.0, 25.0],
        "recency_days": [10, 120, 150, 15, 90, 160],
        "average_items_per_order": [2.5, 1.0, 1.0, 3.0, 1.5, 1.0],
        "churn_label": [0, 1, 1, 0, 0, 1],
    })


@pytest.fixture
def sample_forecasting_dataset() -> pd.DataFrame:
    """Deterministic daily sales series for forecasting tests."""
    dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
    return pd.DataFrame({
        "order_date": dates,
        "total_revenue": [100.0 + (i % 7) * 20.0 for i in range(30)],
        "total_orders": [5 + (i % 5) for i in range(30)],
        "total_units_sold": [10 + (i % 5) * 2 for i in range(30)],
    })


@pytest.fixture
def sample_recommendation_interactions() -> dict[str, pd.DataFrame]:
    """Deterministic products and purchases for recommendation system tests."""
    products = pd.DataFrame({
        "product_id": [1, 2, 3, 4, 5],
        "product_name": ["Wireless Headphones", "Coffee Maker", "Denim Jacket", "Python Cookbook", "Running Shoes"],
        "category": ["Electronics", "Home & Kitchen", "Fashion", "Books", "Footwear"],
        "price": [100.0, 80.0, 60.0, 40.0, 120.0],
        "rating": [4.5, 4.2, 4.0, 4.8, 4.6],
        "stock": [50, 30, 40, 100, 25],
    })
    purchases = pd.DataFrame({
        "user_id": [1, 1, 2, 3, 4],
        "product_id": [1, 2, 3, 4, 5],
        "quantity": [1, 1, 1, 1, 1],
        "line_total": [100.0, 80.0, 60.0, 40.0, 120.0],
    })
    return {"products": products, "purchases": purchases}


@pytest.fixture
def sqlite_engine():
    """In-memory SQLite SQLAlchemy engine for isolated database tests."""
    from sqlalchemy import create_engine
    return create_engine("sqlite:///:memory:", echo=False)


@pytest.fixture
def api_client():
    """FastAPI TestClient for REST API route tests without starting a server."""
    from fastapi.testclient import TestClient
    from api.main import app
    return TestClient(app)
