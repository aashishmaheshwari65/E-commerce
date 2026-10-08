"""
tests/etl/test_transform.py

Tests for DataTransformer cleaning, whitespace stripping, and type conversions.
"""

import pytest
import pandas as pd
from etl.transform import DataTransformer


@pytest.fixture
def transformer():
    return DataTransformer()


@pytest.mark.unit
def test_transform_users(transformer, sample_users_df):
    messy_users = sample_users_df.copy()
    messy_users.loc[0, "email"] = "  ALICE.SMITH@EXAMPLE.COM  "
    messy_users.loc[0, "first_name"] = "  Alice  "

    clean_users = transformer.transform_users(messy_users)
    assert clean_users.loc[0, "email"] == "alice.smith@example.com"
    assert clean_users.loc[0, "first_name"] == "Alice"
    assert pd.api.types.is_datetime64_any_dtype(clean_users["registration_date"])


@pytest.mark.unit
def test_transform_products(transformer, sample_products_df):
    clean_products = transformer.transform_products(sample_products_df)
    assert pd.api.types.is_numeric_dtype(clean_products["price"])
    assert pd.api.types.is_numeric_dtype(clean_products["discount_percent"])


@pytest.mark.unit
def test_transform_orders(transformer, sample_orders_df):
    clean_orders = transformer.transform_orders(sample_orders_df)
    assert pd.api.types.is_datetime64_any_dtype(clean_orders["order_date"])
    assert pd.api.types.is_numeric_dtype(clean_orders["total_amount"])


@pytest.mark.unit
def test_transform_order_items(transformer, sample_order_items_df):
    clean_items = transformer.transform_order_items(sample_order_items_df)
    assert pd.api.types.is_numeric_dtype(clean_items["unit_price"])
    assert pd.api.types.is_numeric_dtype(clean_items["line_total"])


@pytest.mark.unit
def test_transform_payments(transformer, sample_payments_df):
    clean_payments = transformer.transform_payments(sample_payments_df)
    assert pd.api.types.is_datetime64_any_dtype(clean_payments["payment_date"])
    assert pd.api.types.is_numeric_dtype(clean_payments["amount"])


@pytest.mark.unit
def test_transform_reviews(transformer, sample_reviews_df):
    clean_reviews = transformer.transform_reviews(sample_reviews_df)
    assert pd.api.types.is_datetime64_any_dtype(clean_reviews["review_date"])


@pytest.mark.unit
def test_transform_events(transformer, sample_user_events_df):
    clean_events = transformer.transform_events(sample_user_events_df)
    assert pd.api.types.is_datetime64_any_dtype(clean_events["event_timestamp"])
