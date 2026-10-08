"""
tests/data_lake/test_gold.py

Tests for GoldLayer (curated business aggregations and denormalized views)
using isolated temporary directories.
"""

from pathlib import Path
import pytest
import pandas as pd
from data_lake.silver import SilverLayer
from data_lake.gold import GoldLayer


@pytest.fixture
def silver_lake_dir(temp_processed_dir: Path, tmp_path: Path) -> Path:
    """Pre-populates a silver lake directory with parquet files for gold layer tests."""
    silver_dir = tmp_path / "lake" / "silver"
    silver = SilverLayer(input_path=str(temp_processed_dir), output_path=str(silver_dir))
    silver.load()
    return silver_dir


@pytest.mark.unit
def test_gold_layer_customer_sales(silver_lake_dir: Path, tmp_path: Path):
    gold_dir = tmp_path / "lake" / "gold"
    gold = GoldLayer(input_path=str(silver_lake_dir), output_path=str(gold_dir))
    gold.create_customer_sales()

    target = gold_dir / "customer_sales.parquet"
    assert target.exists()
    df = pd.read_parquet(target)
    assert not df.empty
    expected_cols = ["order_id", "user_id", "first_name", "last_name", "product_id", "quantity", "line_total"]
    for col in expected_cols:
        assert col in df.columns


@pytest.mark.unit
def test_gold_layer_product_sales(silver_lake_dir: Path, tmp_path: Path):
    gold_dir = tmp_path / "lake" / "gold"
    gold = GoldLayer(input_path=str(silver_lake_dir), output_path=str(gold_dir))
    gold.create_product_sales()

    target = gold_dir / "product_sales.parquet"
    assert target.exists()
    df = pd.read_parquet(target)
    assert not df.empty
    assert "product_id" in df.columns
