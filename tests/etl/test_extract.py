"""
tests/etl/test_extract.py

Tests for DataExtractor class.
"""

from pathlib import Path
import pytest
from etl.extract import DataExtractor


@pytest.mark.unit
def test_extract_all_files(temp_raw_dir: Path):
    extractor = DataExtractor(data_path=str(temp_raw_dir))
    data = extractor.extract()

    assert isinstance(data, dict)
    expected_keys = ["users", "products", "orders", "order_items", "payments", "reviews", "events"]
    for key in expected_keys:
        assert key in data
        assert len(data[key]) > 0


@pytest.mark.unit
def test_extract_missing_file_raises_error(tmp_path: Path):
    empty_dir = tmp_path / "empty_raw"
    empty_dir.mkdir()
    extractor = DataExtractor(data_path=str(empty_dir))

    with pytest.raises(FileNotFoundError):
        extractor.extract()
