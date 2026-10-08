"""
tests/validation/test_rules.py

Unit tests for ValidationRules across all entity datasets.
Covers both valid and invalid scenarios deterministically.
"""

import pytest
import pandas as pd
from validation.rules import ValidationRules


@pytest.mark.unit
def test_users_valid(sample_users_df):
    errors = ValidationRules.validate_users(sample_users_df)
    assert errors == []


@pytest.mark.unit
def test_users_missing_columns(sample_users_df):
    bad_users = sample_users_df.drop(columns=["email"])
    errors = ValidationRules.validate_users(bad_users)
    assert any("Missing columns in users.csv" in e for e in errors)


@pytest.mark.unit
def test_users_duplicate_primary_key(sample_users_df):
    dup = sample_users_df.copy()
    dup.loc[len(dup)] = dup.iloc[0]
    errors = ValidationRules.validate_users(dup)
    assert any("Duplicate user_id" in e for e in errors)


@pytest.mark.unit
def test_users_invalid_email_format(sample_users_df):
    bad = sample_users_df.copy()
    bad.loc[0, "email"] = "not-an-email"
    errors = ValidationRules.validate_users(bad)
    assert any("Invalid email format" in e for e in errors)


@pytest.mark.unit
def test_products_valid(sample_products_df):
    errors = ValidationRules.validate_products(sample_products_df)
    assert errors == []


@pytest.mark.unit
def test_products_invalid_rating(sample_products_df):
    bad = sample_products_df.copy()
    bad.loc[0, "rating"] = 7.5
    errors = ValidationRules.validate_products(bad)
    assert any("Invalid product rating" in e for e in errors)


@pytest.mark.unit
def test_orders_valid(sample_orders_df, sample_users_df):
    errors = ValidationRules.validate_orders(sample_orders_df, sample_users_df)
    assert errors == []


@pytest.mark.unit
def test_orders_foreign_key_violation(sample_orders_df, sample_users_df):
    bad_orders = sample_orders_df.copy()
    bad_orders.loc[0, "user_id"] = 999999
    errors = ValidationRules.validate_orders(bad_orders, sample_users_df)
    assert any("Invalid user_id found in orders" in e for e in errors)


@pytest.mark.unit
def test_orders_negative_total_amount(sample_orders_df, sample_users_df):
    bad_orders = sample_orders_df.copy()
    bad_orders.loc[0, "total_amount"] = -50.0
    errors = ValidationRules.validate_orders(bad_orders, sample_users_df)
    assert any("Negative total_amount" in e for e in errors)


@pytest.mark.unit
def test_order_items_valid(sample_order_items_df, sample_orders_df, sample_products_df):
    errors = ValidationRules.validate_order_items(sample_order_items_df, sample_orders_df, sample_products_df)
    assert errors == []


@pytest.mark.unit
def test_order_items_foreign_key_violation(sample_order_items_df, sample_orders_df, sample_products_df):
    bad_items = sample_order_items_df.copy()
    bad_items.loc[0, "product_id"] = 999999
    errors = ValidationRules.validate_order_items(bad_items, sample_orders_df, sample_products_df)
    assert any("Invalid product_id found in order_items" in e for e in errors)


@pytest.mark.unit
def test_payments_valid(sample_payments_df, sample_orders_df):
    errors = ValidationRules.validate_payments(sample_payments_df, sample_orders_df)
    assert errors == []


@pytest.mark.unit
def test_payments_invalid_order_foreign_key(sample_payments_df, sample_orders_df):
    bad_payments = sample_payments_df.copy()
    bad_payments.loc[0, "order_id"] = 999999
    errors = ValidationRules.validate_payments(bad_payments, sample_orders_df)
    assert any("Invalid order_id found in payments" in e for e in errors)


@pytest.mark.unit
def test_reviews_valid(sample_reviews_df, sample_users_df, sample_products_df):
    errors = ValidationRules.validate_reviews(sample_reviews_df, sample_users_df, sample_products_df)
    assert errors == []


@pytest.mark.unit
def test_events_valid(sample_user_events_df, sample_users_df, sample_products_df):
    errors = ValidationRules.validate_events(sample_user_events_df, sample_users_df, sample_products_df)
    assert errors == []


@pytest.mark.unit
def test_events_missing_event_type(sample_user_events_df, sample_users_df, sample_products_df):
    bad_events = sample_user_events_df.copy()
    bad_events.loc[0, "event_type"] = None
    errors = ValidationRules.validate_events(bad_events, sample_users_df, sample_products_df)
    assert any("Missing event_type" in e for e in errors)
