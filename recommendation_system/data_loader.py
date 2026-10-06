import os
import pandas as pd
import numpy as np
from recommendation_system import config

def load_products():
    """Load products dataset from warehouse or processed files."""
    if os.path.exists(config.WAREHOUSE_PRODUCT_DIM_PATH):
        try:
            df = pd.read_parquet(config.WAREHOUSE_PRODUCT_DIM_PATH)
            # Standardize column names if needed
            col_map = {
                "original_price": "price",
                "discounted_price": "final_price"
            }
            df = df.rename(columns=col_map)
            return df
        except Exception as e:
            print(f"Warning: Failed to load product dim: {e}")
            
    if os.path.exists(config.PROCESSED_PRODUCTS_PATH):
        df = pd.read_csv(config.PROCESSED_PRODUCTS_PATH)
        return df

    # Fallback minimal schema
    return pd.DataFrame(columns=[
        "product_id", "product_name", "category", "price", "discount_percent", "stock", "rating"
    ])

def load_users():
    """Load users dataset excluding PII (first_name, last_name, email)."""
    df = None
    if os.path.exists(config.WAREHOUSE_CUSTOMER_DIM_PATH):
        try:
            df = pd.read_parquet(config.WAREHOUSE_CUSTOMER_DIM_PATH)
        except Exception as e:
            print(f"Warning: Failed to load customer dim: {e}")

    if df is None and os.path.exists(config.PROCESSED_USERS_PATH):
        df = pd.read_csv(config.PROCESSED_USERS_PATH)

    if df is not None:
        # Exclude PII
        pii_cols = ["first_name", "last_name", "full_name", "email"]
        keep_cols = [c for c in df.columns if c not in pii_cols]
        return df[keep_cols]

    return pd.DataFrame(columns=["user_id", "city", "country", "registration_date"])

def load_orders_and_items():
    """Load orders and order items to get user purchase interactions."""
    orders_df = None
    items_df = None

    if os.path.exists(config.WAREHOUSE_FACTS_PATH):
        try:
            fact_sales = pd.read_parquet(config.WAREHOUSE_FACTS_PATH)
            dim_customer = load_users()
            dim_product = load_products()

            # Map customer_key -> user_id, product_key -> product_id if present
            if "customer_key" in fact_sales.columns and "customer_key" in dim_customer.columns:
                merged = fact_sales.merge(dim_customer[["customer_key", "user_id"]], on="customer_key", how="left")
            else:
                merged = fact_sales

            if "product_key" in merged.columns and "product_key" in dim_product.columns:
                merged = merged.merge(dim_product[["product_key", "product_id"]], on="product_key", how="left")

            return merged
        except Exception as e:
            print(f"Warning: Failed to load warehouse fact sales: {e}")

    if os.path.exists(config.PROCESSED_ORDERS_PATH) and os.path.exists(config.PROCESSED_ORDER_ITEMS_PATH):
        orders = pd.read_csv(config.PROCESSED_ORDERS_PATH)
        items = pd.read_csv(config.PROCESSED_ORDER_ITEMS_PATH)
        merged = items.merge(orders[["order_id", "user_id", "order_date", "order_status"]], on="order_id", how="left")
        return merged

    return pd.DataFrame(columns=[
        "user_id", "product_id", "order_id", "quantity", "unit_price", "line_total", "order_date"
    ])

def load_reviews():
    """Load product reviews."""
    if os.path.exists(config.PROCESSED_REVIEWS_PATH):
        try:
            return pd.read_csv(config.PROCESSED_REVIEWS_PATH)
        except Exception as e:
            print(f"Warning: Failed to load reviews: {e}")
    return pd.DataFrame(columns=["review_id", "user_id", "product_id", "rating", "review_date"])

def load_user_events():
    """Load user behavior events."""
    if os.path.exists(config.PROCESSED_USER_EVENTS_PATH):
        try:
            return pd.read_csv(config.PROCESSED_USER_EVENTS_PATH)
        except Exception as e:
            print(f"Warning: Failed to load user events: {e}")
    return pd.DataFrame(columns=["event_id", "user_id", "event_type", "product_id", "search_query", "event_timestamp"])

def load_all_data():
    """Load all datasets required for recommendations."""
    products = load_products()
    users = load_users()
    purchases = load_orders_and_items()
    reviews = load_reviews()
    events = load_user_events()

    return {
        "products": products,
        "users": users,
        "purchases": purchases,
        "reviews": reviews,
        "events": events
    }
