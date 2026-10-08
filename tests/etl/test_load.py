"""
tests/etl/test_load.py

Tests for DataLoader writing cleaned datasets to target directory.
"""

from pathlib import Path
import pytest
import pandas as pd
from etl.load import DataLoader


@pytest.mark.unit
def test_load_writes_all_files(tmp_path: Path, sample_users_df, sample_products_df, sample_orders_df,
                               sample_order_items_df, sample_payments_df, sample_reviews_df, sample_user_events_df):
    output_dir = tmp_path / "processed_output"
    loader = DataLoader(output_path=str(output_dir))

    data = {
        "users": sample_users_df,
        "products": sample_products_df,
        "orders": sample_orders_df,
        "order_items": sample_order_items_df,
        "payments": sample_payments_df,
        "reviews": sample_reviews_df,
        "events": sample_user_events_df,
    }

    loader.load(data)

    expected_files = [
        "users_clean.csv",
        "products_clean.csv",
        "orders_clean.csv",
        "order_items_clean.csv",
        "payments_clean.csv",
        "reviews_clean.csv",
        "user_events_clean.csv",
    ]

    for fname in expected_files:
        target = output_dir / fname
        assert target.exists(), f"Expected file {fname} not created"
        df = pd.read_csv(target)
        assert len(df) > 0
