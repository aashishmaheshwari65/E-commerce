"""
monitoring/storage/metrics_store.py

Persists monitoring results to the data/monitoring/ directory.

Files written:
  current_status.json  – full snapshot of the most recent run
  metrics.json         – metrics-only subset for quick consumption
  alerts.json          – all alerts from the most recent run
  history.jsonl        – append-only log of every run (never overwritten)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from monitoring.config import (
    MONITORING_ROOT,
    CURRENT_STATUS_FILE,
    METRICS_FILE,
    ALERTS_FILE,
    HISTORY_FILE,
)
from monitoring.models import MonitoringSnapshot

logger = logging.getLogger(__name__)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save(snapshot: MonitoringSnapshot, monitoring_root: Path | None = None) -> None:
    """
    Persist a MonitoringSnapshot to disk.

    Parameters
    ----------
    snapshot:
        The completed snapshot to store.
    monitoring_root:
        Override output directory (used in tests).
    """
    root = monitoring_root or MONITORING_ROOT
    _ensure_dir(root)

    current_file = root / "current_status.json"
    metrics_file = root / "metrics.json"
    alerts_file = root / "alerts.json"
    history_file = root / "history.jsonl"

    snap_dict = snapshot.to_dict()

    # 1. current_status.json (overwrite)
    try:
        current_file.write_text(
            json.dumps(snap_dict, indent=2, default=str),
            encoding="utf-8",
        )
        logger.debug("Wrote %s", current_file)
    except Exception as exc:
        logger.error("Failed to write current_status.json: %s", exc)

    # 2. metrics.json – lightweight metrics-only subset (overwrite)
    try:
        metrics_subset = {
            "run_id": snapshot.run_id,
            "timestamp": snapshot.timestamp,
            "overall_status": snapshot.overall_status.value,
            "components": {
                name: {
                    "status": res.status.value,
                    "metrics": res.metrics,
                }
                for name, res in snapshot.components.items()
            },
        }
        metrics_file.write_text(
            json.dumps(metrics_subset, indent=2, default=str),
            encoding="utf-8",
        )
        logger.debug("Wrote %s", metrics_file)
    except Exception as exc:
        logger.error("Failed to write metrics.json: %s", exc)

    # 3. alerts.json (overwrite with current run's alerts)
    try:
        alerts_list = [a.to_dict() for a in snapshot.alerts]
        alerts_file.write_text(
            json.dumps(alerts_list, indent=2, default=str),
            encoding="utf-8",
        )
        logger.debug("Wrote %s", alerts_file)
    except Exception as exc:
        logger.error("Failed to write alerts.json: %s", exc)

    # 4. history.jsonl – APPEND only, never overwrite
    try:
        history_record = {
            "run_id": snapshot.run_id,
            "timestamp": snapshot.timestamp,
            "overall_status": snapshot.overall_status.value,
            "component_statuses": {
                name: res.status.value
                for name, res in snapshot.components.items()
            },
            "alert_count": len(snapshot.alerts),
        }
        with history_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(history_record, default=str) + "\n")
        logger.debug("Appended to %s", history_file)
    except Exception as exc:
        logger.error("Failed to append to history.jsonl: %s", exc)


def load_current(monitoring_root: Path | None = None) -> dict | None:
    """Load the most recent current_status.json, or None if not found."""
    root = monitoring_root or MONITORING_ROOT
    current_file = root / "current_status.json"
    if not current_file.exists():
        return None
    try:
        return json.loads(current_file.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error("Failed to read current_status.json: %s", exc)
        return None


def load_alerts(monitoring_root: Path | None = None) -> list[dict]:
    """Load the most recent alerts.json, or empty list if not found."""
    root = monitoring_root or MONITORING_ROOT
    alerts_file = root / "alerts.json"
    if not alerts_file.exists():
        return []
    try:
        return json.loads(alerts_file.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error("Failed to read alerts.json: %s", exc)
        return []


def load_metrics(monitoring_root: Path | None = None) -> dict | None:
    """Load the most recent metrics.json, or None if not found."""
    root = monitoring_root or MONITORING_ROOT
    metrics_file = root / "metrics.json"
    if not metrics_file.exists():
        return None
    try:
        return json.loads(metrics_file.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error("Failed to read metrics.json: %s", exc)
        return None
