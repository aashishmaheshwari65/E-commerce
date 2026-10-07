"""
api/routes/monitoring.py

Monitoring endpoints for Functionality 20.
These endpoints return STORED monitoring data (from the last run),
NOT live collection – so they add zero overhead to normal API requests.

GET /monitoring          – overall status from last run
GET /monitoring/metrics  – metrics-only subset
GET /monitoring/alerts   – alerts from last run
GET /monitoring/health   – component health summary
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from monitoring.storage.metrics_store import (
    load_current,
    load_alerts,
    load_metrics,
)

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


def _require_current() -> dict:
    data = load_current()
    if data is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "No monitoring data available. "
                "Run: python -m monitoring.main --all"
            ),
        )
    return data


@router.get("", summary="Overall monitoring status")
def monitoring_status() -> dict:
    """
    Returns the overall platform status from the most recent monitoring run.
    """
    data = _require_current()
    return {
        "overall_status": data.get("overall_status"),
        "timestamp": data.get("timestamp"),
        "run_id": data.get("run_id"),
        "components": {
            name: info.get("status")
            for name, info in data.get("components", {}).items()
        },
    }


@router.get("/metrics", summary="Detailed metrics from last monitoring run")
def monitoring_metrics() -> dict:
    """
    Returns per-component metrics collected during the last monitoring run.
    """
    data = load_metrics()
    if data is None:
        raise HTTPException(
            status_code=503,
            detail="No metrics data available. Run monitoring first.",
        )
    return data


@router.get("/alerts", summary="Alerts from last monitoring run")
def monitoring_alerts() -> list:
    """
    Returns the list of alerts generated during the last monitoring run.
    """
    return load_alerts()


@router.get("/health", summary="Component health summary")
def monitoring_health() -> dict:
    """
    Returns a per-component health summary from the last monitoring run.
    """
    data = _require_current()
    components = {}
    for name, info in data.get("components", {}).items():
        components[name] = {
            "status": info.get("status"),
            "warnings": info.get("warnings", []),
            "errors": info.get("errors", []),
        }
    return {
        "overall_status": data.get("overall_status"),
        "timestamp": data.get("timestamp"),
        "components": components,
        "alert_count": len(data.get("alerts", [])),
    }
