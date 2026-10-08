"""
tests/monitoring/test_data_quality.py

Tests data quality monitoring collector (nulls, duplicates, row counts, freshness).
"""

from pathlib import Path
import pytest
from monitoring.collectors import data_quality
from monitoring.models import ComponentStatus


@pytest.mark.unit
def test_data_quality_collector(temp_raw_dir: Path):
    result = data_quality.collect(raw_dir=temp_raw_dir)

    assert result.component == "data_quality"
    assert result.status in (ComponentStatus.HEALTHY, ComponentStatus.WARNING, ComponentStatus.CRITICAL)
    assert "tables_checked" in result.metrics
    assert result.metrics["tables_checked"] > 0
