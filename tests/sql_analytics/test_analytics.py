"""
tests/sql_analytics/test_analytics.py

Tests SQL analytics queries and metrics (revenue, orders, AOV, customers)
using an in-memory DuckDB database and small deterministic datasets.
"""

import pytest
import duckdb
import pandas as pd


@pytest.fixture
def analytics_db():
    """Sets up an in-memory DuckDB connection with small deterministic tables."""
    con = duckdb.connect(database=":memory:")

    fact_sales = pd.DataFrame({
        "sales_key": [1, 2, 3],
        "order_id": [101, 101, 102],
        "customer_key": [1, 1, 2],
        "product_key": [10, 20, 10],
        "quantity": [2, 1, 3],
        "gross_sales": [200.0, 50.0, 300.0],
        "discount_amount": [20.0, 0.0, 30.0],
        "net_sales": [180.0, 50.0, 270.0],
        "order_status": ["completed", "completed", "completed"],
    })

    dim_customer = pd.DataFrame({
        "customer_key": [1, 2],
        "full_name": ["Alice Smith", "Bob Jones"],
        "country": ["USA", "USA"],
    })

    dim_product = pd.DataFrame({
        "product_key": [10, 20],
        "product_name": ["Keyboard", "Mouse"],
        "category": ["Electronics", "Electronics"],
    })

    con.register("fact_sales", fact_sales)
    con.register("dim_customer", dim_customer)
    con.register("dim_product", dim_product)

    yield con
    con.close()


@pytest.mark.unit
def test_total_revenue_and_orders(analytics_db):
    query = """
    SELECT 
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(net_sales) AS total_revenue,
        COUNT(DISTINCT customer_key) AS total_customers
    FROM fact_sales
    WHERE order_status = 'completed'
    """
    res = analytics_db.execute(query).fetchdf()

    assert res["total_orders"].iloc[0] == 2
    assert res["total_revenue"].iloc[0] == 500.0  # 180 + 50 + 270
    assert res["total_customers"].iloc[0] == 2


@pytest.mark.unit
def test_average_order_value_kpi(analytics_db):
    query = """
    SELECT 
        SUM(net_sales) / COUNT(DISTINCT order_id) AS aov
    FROM fact_sales
    WHERE order_status = 'completed'
    """
    res = analytics_db.execute(query).fetchdf()
    expected_aov = 500.0 / 2  # 250.0
    assert res["aov"].iloc[0] == expected_aov


@pytest.mark.unit
def test_revenue_by_product_category(analytics_db):
    query = """
    SELECT 
        p.category,
        SUM(f.net_sales) AS category_revenue,
        SUM(f.quantity) AS total_units
    FROM fact_sales f
    JOIN dim_product p ON f.product_key = p.product_key
    GROUP BY p.category
    """
    res = analytics_db.execute(query).fetchdf()

    assert len(res) == 1
    assert res["category"].iloc[0] == "Electronics"
    assert res["category_revenue"].iloc[0] == 500.0
    assert res["total_units"].iloc[0] == 6


@pytest.mark.unit
def test_top_customer_spending(analytics_db):
    query = """
    SELECT 
        c.full_name,
        SUM(f.net_sales) AS customer_spend
    FROM fact_sales f
    JOIN dim_customer c ON f.customer_key = c.customer_key
    GROUP BY c.full_name
    ORDER BY customer_spend DESC
    """
    res = analytics_db.execute(query).fetchdf()

    assert len(res) == 2
    # Bob Jones spent 270, Alice Smith spent 230
    assert res["full_name"].iloc[0] == "Bob Jones"
    assert res["customer_spend"].iloc[0] == 270.0
    assert res["full_name"].iloc[1] == "Alice Smith"
    assert res["customer_spend"].iloc[1] == 230.0
