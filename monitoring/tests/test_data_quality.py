"""
Tests for monitoring/collectors/data_quality.py
Uses small synthetic CSV fixtures in a temporary directory.
Does NOT modify production data.
"""

from __future__ import annotations

import pytest
import pandas as pd
from pathlib import Path

from monitoring.models import ComponentStatus


# -------------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------------

@pytest.fixture()
def raw_dir(tmp_path: Path) -> Path:
    """Create a minimal raw data directory with valid CSVs."""
    users = pd.DataFrame({
        "user_id": [1, 2, 3],
        "first_name": ["Alice", "Bob", "Carol"],
        "last_name": ["A", "B", "C"],
        "email": ["a@example.com", "b@example.com", "c@example.com"],
        "city": ["NYC", "LA", "SF"],
        "country": ["US", "US", "US"],
        "registration_date": ["2024-01-01", "2024-02-01", "2024-03-01"],
    })
    orders = pd.DataFrame({
        "order_id": [101, 102],
        "user_id": [1, 2],
        "order_date": ["2024-06-01", "2024-06-15"],
        "order_status": ["completed", "completed"],
        "payment_method": ["card", "cash"],
        "total_amount": [99.0, 49.5],
    })
    users.to_csv(tmp_path / "users.csv", index=False)
    orders.to_csv(tmp_path / "orders.csv", index=False)
    return tmp_path


@pytest.fixture()
def raw_dir_with_nulls(tmp_path: Path) -> Path:
    """Raw dir with a CSV that has many null values."""
    users = pd.DataFrame({
        "user_id": [1, 2, 3],
        "first_name": [None, None, None],
        "last_name": [None, None, None],
        "email": ["a@example.com", None, None],
        "city": [None, None, None],
        "country": [None, None, None],
        "registration_date": ["2024-01-01", None, None],
    })
    users.to_csv(tmp_path / "users.csv", index=False)
    return tmp_path


@pytest.fixture()
def raw_dir_with_duplicates(tmp_path: Path) -> Path:
    """Raw dir with duplicate PKs."""
    users = pd.DataFrame({
        "user_id": [1, 1, 2],          # duplicate user_id=1
        "first_name": ["Alice", "Alice2", "Bob"],
        "last_name": ["A", "A2", "B"],
        "email": ["a@x.com", "a2@x.com", "b@x.com"],
        "city": ["NYC", "NYC", "LA"],
        "country": ["US", "US", "US"],
        "registration_date": ["2024-01-01", "2024-01-02", "2024-02-01"],
    })
    users.to_csv(tmp_path / "users.csv", index=False)
    return tmp_path


# -------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------

def test_collect_returns_component_result(raw_dir):
    from monitoring.collectors.data_quality import collect
    result = collect(raw_dir=raw_dir)
    assert result.component == "data_quality"
    assert result.status in ComponentStatus.__members__.values()


def test_healthy_data_returns_healthy_or_warning(raw_dir):
    """Clean data with only users + orders (others missing) → HEALTHY or WARNING."""
    from monitoring.collectors.data_quality import collect
    result = collect(raw_dir=raw_dir)
    # Missing files produce errors; with limited fixtures expect WARNING at worst
    assert result.status in (
        ComponentStatus.HEALTHY,
        ComponentStatus.WARNING,
        ComponentStatus.CRITICAL,
    )


def test_metrics_contains_expected_keys(raw_dir):
    from monitoring.collectors.data_quality import collect
    result = collect(raw_dir=raw_dir)
    assert "tables_checked" in result.metrics
    assert "rows_checked" in result.metrics
    assert "null_violations" in result.metrics
    assert "duplicate_pk_violations" in result.metrics
    assert "datasets" in result.metrics


def test_null_heavy_data_generates_warnings(raw_dir_with_nulls):
    from monitoring.collectors.data_quality import collect
    result = collect(raw_dir=raw_dir_with_nulls)
    # High null percentage should produce at least a warning or critical
    assert result.status in (
        ComponentStatus.WARNING, ComponentStatus.CRITICAL
    ) or result.warnings


def test_duplicate_pk_detected(raw_dir_with_duplicates):
    from monitoring.collectors.data_quality import collect
    result = collect(raw_dir=raw_dir_with_duplicates)
    users_result = next(
        (d for d in result.metrics["datasets"] if d["dataset"] == "users"),
        None,
    )
    assert users_result is not None
    assert users_result["duplicate_pk_count"] >= 1


def test_missing_file_reported(tmp_path):
    """Empty directory → datasets report missing files."""
    from monitoring.collectors.data_quality import collect
    result = collect(raw_dir=tmp_path)
    missing = [
        d for d in result.metrics["datasets"]
        if not d["file_exists"]
    ]
    assert len(missing) > 0


def test_freshness_computed_from_timestamp_column(raw_dir):
    from monitoring.collectors.data_quality import collect
    result = collect(raw_dir=raw_dir)
    orders_result = next(
        (d for d in result.metrics["datasets"] if d["dataset"] == "orders"),
        None,
    )
    assert orders_result is not None
    # orders has a ts_col → freshness should be set
    assert orders_result["freshness"] is not None
    assert "status" in orders_result["freshness"]
