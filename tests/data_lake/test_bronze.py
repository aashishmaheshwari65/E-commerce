"""
tests/data_lake/test_bronze.py

Tests for BronzeLayer (CSV to Parquet raw ingestion) in isolated temporary directories.
"""

from pathlib import Path
import pytest
import pandas as pd
from data_lake.bronze import BronzeLayer


@pytest.mark.unit
def test_bronze_layer_converts_csv_to_parquet(temp_raw_dir: Path, tmp_path: Path):
    output_dir = tmp_path / "lake" / "bronze"
    bronze = BronzeLayer(input_path=str(temp_raw_dir), output_path=str(output_dir))
    bronze.load()

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
        assert target.exists(), f"Expected Parquet file {pfile} was not created"
        df = pd.read_parquet(target)
        assert len(df) > 0


@pytest.mark.unit
def test_bronze_layer_missing_input_dir(tmp_path: Path):
    missing_dir = tmp_path / "non_existent_raw"
    output_dir = tmp_path / "bronze_out"
    bronze = BronzeLayer(input_path=str(missing_dir), output_path=str(output_dir))

    with pytest.raises(Exception):
        bronze.load()
