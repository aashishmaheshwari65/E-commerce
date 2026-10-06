import pytest
import pandas as pd
from unittest.mock import patch
from recommendation_system.data_loader import load_users, load_products

def test_load_users_excludes_pii():
    mock_users = pd.DataFrame({
        "customer_key": [1, 2],
        "user_id": ["U1", "U2"],
        "first_name": ["Alice", "Bob"],
        "last_name": ["Smith", "Jones"],
        "email": ["a@x.com", "b@x.com"],
        "city": ["NYC", "LA"],
        "country": ["USA", "USA"]
    })
    with patch("pandas.read_parquet", return_value=mock_users):
        with patch("os.path.exists", return_value=True):
            users_df = load_users()
            assert "email" not in users_df.columns
            assert "first_name" not in users_df.columns
            assert "last_name" not in users_df.columns
            assert "user_id" in users_df.columns
            assert "city" in users_df.columns

def test_load_products_schema():
    mock_products = pd.DataFrame({
        "product_id": ["P1", "P2"],
        "product_name": ["Widget A", "Widget B"],
        "category": ["Electronics", "Electronics"],
        "price": [10.0, 20.0],
        "rating": [4.5, 4.0]
    })
    with patch("os.path.exists", side_effect=lambda path: "products_clean.csv" in str(path)):
        with patch("pandas.read_csv", return_value=mock_products):
            prods = load_products()
            assert len(prods) == 2
            assert "product_id" in prods.columns
            assert "product_name" in prods.columns
