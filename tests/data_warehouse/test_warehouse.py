"""
tests/data_warehouse/test_warehouse.py

Tests star schema dimensions, surrogate key generation, fact_sales grain,
and referential integrity using deterministic fixtures.
"""

import pytest
import pandas as pd
from data_warehouse.dimensions import (
    generate_key,
    build_dim_customer,
    build_dim_product,
    build_dim_date,
    build_dim_payment,
    build_dim_order,
)
from data_warehouse.fact_sales import build_fact_sales


@pytest.mark.unit
def test_surrogate_key_generation():
    k1 = generate_key(101)
    k2 = generate_key(101)
    k3 = generate_key(102)
    assert k1 == k2
    assert k1 != k3
    assert generate_key(None) == -1


@pytest.mark.unit
def test_build_dimensions(sample_users_df, sample_products_df, sample_orders_df, sample_payments_df):
    dim_customer = build_dim_customer(sample_users_df)
    assert "customer_key" in dim_customer.columns
    assert "full_name" in dim_customer.columns
    assert len(dim_customer) == len(sample_users_df)

    dim_product = build_dim_product(sample_products_df)
    assert "product_key" in dim_product.columns
    assert "discounted_price" in dim_product.columns
    assert len(dim_product) == len(sample_products_df)

    dim_date = build_dim_date(sample_orders_df)
    assert "date_key" in dim_date.columns
    assert "year" in dim_date.columns
    assert "is_weekend" in dim_date.columns

    dim_payment = build_dim_payment(sample_payments_df)
    assert "payment_key" in dim_payment.columns

    dim_order = build_dim_order(sample_orders_df)
    assert "order_key" in dim_order.columns
    assert len(dim_order) == len(sample_orders_df)


@pytest.mark.unit
def test_build_fact_sales_grain_and_calculations(
    sample_users_df, sample_products_df, sample_orders_df, sample_order_items_df, sample_payments_df
):
    dim_customer = build_dim_customer(sample_users_df)
    dim_product = build_dim_product(sample_products_df)
    dim_date = build_dim_date(sample_orders_df)
    dim_payment = build_dim_payment(sample_payments_df)
    dim_order = build_dim_order(sample_orders_df)

    fact = build_fact_sales(
        sample_order_items_df,
        sample_orders_df,
        dim_customer,
        dim_product,
        dim_date,
        dim_payment,
        dim_order,
        sample_payments_df,
    )

    # Fact table grain must match order_items
    assert len(fact) == len(sample_order_items_df)

    # Check key columns
    expected_cols = [
        "sales_key", "order_item_id", "order_id", "customer_key", "product_key",
        "date_key", "payment_key", "order_key", "gross_sales", "discount_amount", "net_sales"
    ]
    for col in expected_cols:
        assert col in fact.columns

    # Verify calculation: gross_sales = quantity * unit_price
    for _, row in fact.iterrows():
        assert row["gross_sales"] == row["quantity"] * row["unit_price"]
        assert row["net_sales"] <= row["gross_sales"]

    # Verify referential integrity of customer keys
    valid_customer_keys = set(dim_customer["customer_key"])
    for ck in fact["customer_key"]:
        assert ck in valid_customer_keys


@pytest.mark.unit
def test_order_items_join_does_not_multiply_order_totals():
    """
    Verify that an order with multiple items maintains accurate line items
    without multiplying order-level totals incorrectly.
    """
    orders = pd.DataFrame({
        "order_id": [999],
        "user_id": [1],
        "order_date": ["2024-06-01"],
        "order_status": ["delivered"],
        "payment_method": ["credit_card"],
        "total_amount": [150.0],
    })
    order_items = pd.DataFrame({
        "order_item_id": [1, 2],
        "order_id": [999, 999],
        "product_id": [1, 2],
        "quantity": [1, 1],
        "unit_price": [100.0, 50.0],
        "line_total": [100.0, 50.0],
    })
    products = pd.DataFrame({
        "product_id": [1, 2],
        "product_name": ["A", "B"],
        "category": ["C", "C"],
        "price": [100.0, 50.0],
        "discount_percent": [0, 0],
        "stock": [10, 10],
        "rating": [4.0, 4.0],
    })
    users = pd.DataFrame({
        "user_id": [1],
        "first_name": ["Alice"],
        "last_name": ["Smith"],
        "email": ["alice@example.com"],
        "city": ["NYC"],
        "country": ["USA"],
        "registration_date": ["2024-01-01"],
    })
    payments = pd.DataFrame({
        "payment_id": [1],
        "order_id": [999],
        "payment_date": ["2024-06-01"],
        "payment_method": ["credit_card"],
        "payment_status": ["paid"],
        "amount": [150.0],
    })

    dim_customer = build_dim_customer(users)
    dim_product = build_dim_product(products)
    dim_date = build_dim_date(orders)
    dim_payment = build_dim_payment(payments)
    dim_order = build_dim_order(orders)

    fact = build_fact_sales(order_items, orders, dim_customer, dim_product, dim_date, dim_payment, dim_order, payments)

    assert len(fact) == 2
    assert fact["gross_sales"].sum() == 150.0
