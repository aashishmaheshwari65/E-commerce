"""
tests/data_lake/test_silver.py

Tests for SilverLayer (processed CSV to Parquet) in isolated temporary directories.
"""

from pathlib import Path
import pytest
import pandas as pd
from data_lake.silver import SilverLayer


@pytest.mark.unit
def test_silver_layer_converts_processed_to_parquet(temp_processed_dir: Path, tmp_path: Path):
    output_dir = tmp_path / "lake" / "silver"
    silver = SilverLayer(input_path=str(temp_processed_dir), output_path=str(output_dir))
    silver.load()

    expected_parquets = [
        "users.parquet",
        "products.parquet",
        "orders.parquet",
        "order_items.parquet",
        "payments.parquet",
        "reviews.parquet",
        "events.parquet",
    ]

    for pfile in expected_parquets:
        target = output_dir / pfile
        assert target.exists(), f"Expected Silver Parquet {pfile} was not created"
        df = pd.read_parquet(target)
        assert len(df) > 0


@pytest.mark.unit
def test_silver_layer_missing_input_dir(tmp_path: Path):
    missing_dir = tmp_path / "missing_proc"
    output_dir = tmp_path / "silver_out"
    silver = SilverLayer(input_path=str(missing_dir), output_path=str(output_dir))

    with pytest.raises(Exception):
        silver.load()
