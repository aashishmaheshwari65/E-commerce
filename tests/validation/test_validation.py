"""
tests/validation/test_validation.py

Tests for DataValidator orchestrator class using isolated temporary directories.
"""

from pathlib import Path
import pytest
from validation.validate import DataValidator


@pytest.mark.unit
def test_data_validator_load_data(temp_raw_dir: Path, tmp_path: Path):
    validator = DataValidator()
    validator.data_path = str(temp_raw_dir)
    validator.report_path = str(tmp_path / "val_report")
    
    data = validator.load_data()
    assert isinstance(data, dict)
    expected_tables = ["users", "products", "orders", "order_items", "payments", "reviews", "events"]
    for table in expected_tables:
        assert table in data
        assert not data[table].empty


@pytest.mark.unit
def test_data_validator_run_clean_data(temp_raw_dir: Path, tmp_path: Path):
    validator = DataValidator()
    validator.data_path = str(temp_raw_dir)
    report_dir = tmp_path / "val_report"
    report_dir.mkdir(parents=True, exist_ok=True)
    validator.report_path = str(report_dir)

    # Fixture data should pass without fatal crashes
    validator.run()
    assert (report_dir / "validation_report.json").exists()
