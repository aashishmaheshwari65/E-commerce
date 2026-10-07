"""
Tests for monitoring/storage/metrics_store.py
Uses temporary directories to avoid touching production data.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from monitoring.models import (
    Alert,
    ComponentResult,
    ComponentStatus,
    MonitoringSnapshot,
)


def _make_snapshot(run_id: str = "test_run_001") -> MonitoringSnapshot:
    comp = ComponentResult(
        component="data_quality",
        status=ComponentStatus.HEALTHY,
        metrics={"tables_checked": 3, "rows_checked": 100},
        warnings=[],
        errors=[],
    )
    kafka = ComponentResult(
        component="kafka",
        status=ComponentStatus.NOT_CONFIGURED,
        metrics={},
        warnings=["Kafka not configured"],
        errors=[],
    )
    alert = Alert(
        timestamp="2026-01-01T00:00:00+00:00",
        severity="WARNING",
        component="data_quality",
        metric="null_percentage[users]",
        value=6.0,
        threshold=5.0,
        message="null_percentage value 6.0 exceeds warning threshold",
    )
    from monitoring.checks.health import aggregate
    snapshot = aggregate(run_id, [comp, kafka], [alert])
    return snapshot


def test_save_creates_current_status_json(tmp_path):
    from monitoring.storage.metrics_store import save
    snapshot = _make_snapshot()
    save(snapshot, monitoring_root=tmp_path)
    assert (tmp_path / "current_status.json").exists()


def test_save_creates_metrics_json(tmp_path):
    from monitoring.storage.metrics_store import save
    snapshot = _make_snapshot()
    save(snapshot, monitoring_root=tmp_path)
    assert (tmp_path / "metrics.json").exists()


def test_save_creates_alerts_json(tmp_path):
    from monitoring.storage.metrics_store import save
    snapshot = _make_snapshot()
    save(snapshot, monitoring_root=tmp_path)
    alerts_file = tmp_path / "alerts.json"
    assert alerts_file.exists()
    alerts = json.loads(alerts_file.read_text())
    assert len(alerts) == 1
    assert alerts[0]["component"] == "data_quality"


def test_save_appends_to_history_jsonl(tmp_path):
    from monitoring.storage.metrics_store import save
    for i in range(3):
        snap = _make_snapshot(run_id=f"run_{i}")
        save(snap, monitoring_root=tmp_path)

    history_file = tmp_path / "history.jsonl"
    assert history_file.exists()
    lines = [l for l in history_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 3


def test_history_never_overwritten(tmp_path):
    """history.jsonl must grow with each save, not be reset."""
    from monitoring.storage.metrics_store import save

    snap1 = _make_snapshot("first_run")
    save(snap1, monitoring_root=tmp_path)

    snap2 = _make_snapshot("second_run")
    save(snap2, monitoring_root=tmp_path)

    lines = (tmp_path / "history.jsonl").read_text().splitlines()
    run_ids = [json.loads(l)["run_id"] for l in lines if l.strip()]
    assert "first_run" in run_ids
    assert "second_run" in run_ids


def test_load_current_returns_dict(tmp_path):
    from monitoring.storage.metrics_store import save, load_current
    snap = _make_snapshot()
    save(snap, monitoring_root=tmp_path)
    data = load_current(monitoring_root=tmp_path)
    assert data is not None
    assert "overall_status" in data


def test_load_current_returns_none_if_missing(tmp_path):
    from monitoring.storage.metrics_store import load_current
    data = load_current(monitoring_root=tmp_path)
    assert data is None


def test_load_alerts_returns_list(tmp_path):
    from monitoring.storage.metrics_store import save, load_alerts
    snap = _make_snapshot()
    save(snap, monitoring_root=tmp_path)
    alerts = load_alerts(monitoring_root=tmp_path)
    assert isinstance(alerts, list)
    assert len(alerts) == 1
