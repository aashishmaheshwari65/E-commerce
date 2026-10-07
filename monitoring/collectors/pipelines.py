"""
monitoring/collectors/pipelines.py

Pipeline health collector for Functionality 20.

Inspects output artifacts and run metadata for each pipeline
implemented in Functionalities 4-18.  A pipeline is only marked
HEALTHY when actual output files and a recent successful run can
be confirmed – not merely because its directory exists.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from monitoring.config import (
    DATA_ROOT,
    ML_PIPELINE_DIR,
    LAKE_DIR,
    WAREHOUSE_DIR,
    SEGMENTATION_DIR,
    CHURN_DIR,
    FORECASTING_DIR,
    RECOMMENDATIONS_DIR,
)
from monitoring.models import ComponentResult, ComponentStatus

logger = logging.getLogger(__name__)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _age_hours(ts_str: str) -> float | None:
    """Return age in hours for an ISO timestamp string; None on failure."""
    try:
        ts = datetime.fromisoformat(ts_str)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return (_now_utc() - ts).total_seconds() / 3600.0
    except Exception:
        return None


def _newest_file_age_hours(directory: Path, glob: str = "**/*") -> float | None:
    """Return age in hours of the newest file under directory; None if empty."""
    try:
        files = [f for f in directory.glob(glob) if f.is_file()]
        if not files:
            return None
        newest = max(f.stat().st_mtime for f in files)
        age_s = _now_utc().timestamp() - newest
        return age_s / 3600.0
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Individual pipeline checks
# ---------------------------------------------------------------------------

def _check_etl(data_root: Path) -> dict[str, Any]:
    processed_dir = data_root / "processed"
    files = list(processed_dir.glob("**/*.parquet")) if processed_dir.exists() else []
    age_h = _newest_file_age_hours(processed_dir, "**/*.parquet")
    return {
        "pipeline": "etl",
        "output_dir_exists": processed_dir.exists(),
        "output_file_count": len(files),
        "newest_output_age_hours": round(age_h, 2) if age_h is not None else None,
        "status": "HEALTHY" if files else "UNKNOWN",
    }


def _check_data_lake(lake_dir: Path) -> dict[str, Any]:
    layers = {}
    for layer in ("bronze", "silver", "gold"):
        layer_dir = lake_dir / layer
        files = list(layer_dir.glob("**/*.parquet")) if layer_dir.exists() else []
        layers[layer] = {
            "exists": layer_dir.exists(),
            "parquet_files": len(files),
        }
    has_gold = layers.get("gold", {}).get("parquet_files", 0) > 0
    return {
        "pipeline": "data_lake",
        "layers": layers,
        "status": "HEALTHY" if has_gold else "WARNING",
    }


def _check_warehouse(wh_dir: Path) -> dict[str, Any]:
    fact_file = wh_dir / "facts" / "fact_sales.parquet"
    dim_dir = wh_dir / "dimensions"
    dim_files = list(dim_dir.glob("*.parquet")) if dim_dir.exists() else []
    return {
        "pipeline": "data_warehouse",
        "fact_sales_exists": fact_file.exists(),
        "dimension_count": len(dim_files),
        "status": (
            "HEALTHY"
            if fact_file.exists() and dim_files
            else "WARNING"
        ),
    }


def _check_ml_pipeline(ml_dir: Path) -> dict[str, Any]:
    runs_file = ml_dir / "pipeline_runs.json"
    if not runs_file.exists():
        return {
            "pipeline": "automated_ml_pipeline",
            "status": "UNKNOWN",
            "reason": "pipeline_runs.json not found",
        }

    try:
        runs = json.loads(runs_file.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "pipeline": "automated_ml_pipeline",
            "status": "UNKNOWN",
            "reason": str(exc),
        }

    if not runs:
        return {
            "pipeline": "automated_ml_pipeline",
            "status": "UNKNOWN",
            "reason": "no runs recorded",
        }

    # Most recent run with complete status
    successful = [
        r for r in runs
        if r.get("status") == "success"
        and r.get("training_status") == "success"
    ]
    latest = runs[0]  # list is newest-first by convention
    last_successful = successful[0] if successful else None

    age_h = None
    if last_successful:
        age_h = _age_hours(last_successful.get("end_time", ""))

    status = "HEALTHY" if last_successful else "CRITICAL"

    return {
        "pipeline": "automated_ml_pipeline",
        "total_runs": len(runs),
        "last_run": latest.get("start_time"),
        "last_run_status": latest.get("status"),
        "last_successful_run": (
            last_successful.get("end_time") if last_successful else None
        ),
        "hours_since_success": round(age_h, 2) if age_h else None,
        "selected_models": (
            last_successful.get("selected_models", {})
            if last_successful
            else {}
        ),
        "duration_seconds": last_successful.get("duration_seconds"),
        "status": status,
    }


def _check_segmentation(seg_dir: Path) -> dict[str, Any]:
    files = list(seg_dir.glob("**/*")) if seg_dir.exists() else []
    actual_files = [f for f in files if f.is_file()]
    return {
        "pipeline": "customer_segmentation",
        "output_files": len(actual_files),
        "status": "HEALTHY" if actual_files else "UNKNOWN",
    }


def _check_churn(churn_dir: Path) -> dict[str, Any]:
    files = list(churn_dir.glob("**/*")) if churn_dir.exists() else []
    actual_files = [f for f in files if f.is_file()]
    return {
        "pipeline": "churn_prediction",
        "output_files": len(actual_files),
        "status": "HEALTHY" if actual_files else "UNKNOWN",
    }


def _check_forecasting(fc_dir: Path) -> dict[str, Any]:
    files = list(fc_dir.glob("**/*")) if fc_dir.exists() else []
    actual_files = [f for f in files if f.is_file()]
    return {
        "pipeline": "sales_forecasting",
        "output_files": len(actual_files),
        "status": "HEALTHY" if actual_files else "UNKNOWN",
    }


def _check_recommendations(rec_dir: Path) -> dict[str, Any]:
    files = list(rec_dir.glob("**/*")) if rec_dir.exists() else []
    actual_files = [f for f in files if f.is_file()]
    return {
        "pipeline": "recommendation_system",
        "output_files": len(actual_files),
        "status": "HEALTHY" if actual_files else "UNKNOWN",
    }


def _check_airflow() -> dict[str, Any]:
    """
    Try the Airflow REST API.  Gracefully returns UNKNOWN if not reachable
    – we do NOT install or start Airflow from here.
    """
    from monitoring.config import AIRFLOW_BASE_URL, AIRFLOW_USERNAME, AIRFLOW_PASSWORD

    dag_ids = ["automated_ml_pipeline", "ecommerce_data_pipeline"]
    dag_results = {}

    try:
        import requests  # type: ignore
        session = requests.Session()
        session.auth = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
        session.timeout = 4

        for dag_id in dag_ids:
            try:
                resp = session.get(
                    f"{AIRFLOW_BASE_URL}/api/v1/dags/{dag_id}",
                )
                if resp.status_code == 200:
                    data = resp.json()
                    dag_results[dag_id] = {
                        "found": True,
                        "is_paused": data.get("is_paused"),
                        "is_active": data.get("is_active"),
                    }
                    # Latest run
                    runs_resp = session.get(
                        f"{AIRFLOW_BASE_URL}/api/v1/dags/{dag_id}/dagRuns",
                        params={"order_by": "-start_date", "limit": 1},
                    )
                    if runs_resp.status_code == 200:
                        runs = runs_resp.json().get("dag_runs", [])
                        if runs:
                            dag_results[dag_id]["latest_run"] = {
                                "state": runs[0].get("state"),
                                "start_date": runs[0].get("start_date"),
                                "end_date": runs[0].get("end_date"),
                            }
                elif resp.status_code == 404:
                    dag_results[dag_id] = {"found": False}
                else:
                    dag_results[dag_id] = {
                        "found": False,
                        "http_status": resp.status_code,
                    }
            except Exception as exc:
                dag_results[dag_id] = {"error": str(exc)}

        return {
            "pipeline": "airflow",
            "accessible": True,
            "dags": dag_results,
            "status": "HEALTHY",
        }
    except ImportError:
        return {
            "pipeline": "airflow",
            "accessible": False,
            "status": "UNKNOWN",
            "reason": "requests library not available",
        }
    except Exception as exc:
        return {
            "pipeline": "airflow",
            "accessible": False,
            "status": "UNKNOWN",
            "reason": str(exc),
        }


# ---------------------------------------------------------------------------
# Main collector
# ---------------------------------------------------------------------------

def collect(
    data_root: Path | None = None,
    lake_dir: Path | None = None,
    warehouse_dir: Path | None = None,
    ml_pipeline_dir: Path | None = None,
    segmentation_dir: Path | None = None,
    churn_dir: Path | None = None,
    forecasting_dir: Path | None = None,
    recommendations_dir: Path | None = None,
) -> ComponentResult:
    """Run all pipeline health checks and return a ComponentResult."""
    data_root = data_root or DATA_ROOT
    lake_dir = lake_dir or LAKE_DIR
    warehouse_dir = warehouse_dir or WAREHOUSE_DIR
    ml_pipeline_dir = ml_pipeline_dir or ML_PIPELINE_DIR
    segmentation_dir = segmentation_dir or SEGMENTATION_DIR
    churn_dir = churn_dir or CHURN_DIR
    forecasting_dir = forecasting_dir or FORECASTING_DIR
    recommendations_dir = recommendations_dir or RECOMMENDATIONS_DIR

    ts = datetime.now(timezone.utc).isoformat()

    pipeline_checks = [
        _check_etl(data_root),
        _check_data_lake(lake_dir),
        _check_warehouse(warehouse_dir),
        _check_ml_pipeline(ml_pipeline_dir),
        _check_segmentation(segmentation_dir),
        _check_churn(churn_dir),
        _check_forecasting(forecasting_dir),
        _check_recommendations(recommendations_dir),
        _check_airflow(),
    ]

    warnings: list[str] = []
    errors: list[str] = []

    for check in pipeline_checks:
        st = check.get("status", "UNKNOWN")
        reason = check.get("reason", "")
        name = check.get("pipeline", "unknown")
        if st == "CRITICAL":
            errors.append(f"{name}: CRITICAL – {reason}")
        elif st == "WARNING":
            warnings.append(f"{name}: WARNING")
        elif st == "UNKNOWN":
            warnings.append(
                f"{name}: UNKNOWN"
                + (f" – {reason}" if reason else "")
            )

    if errors:
        status = ComponentStatus.CRITICAL
    elif warnings:
        status = ComponentStatus.WARNING
    else:
        status = ComponentStatus.HEALTHY

    return ComponentResult(
        component="pipelines",
        status=status,
        timestamp=ts,
        metrics={"pipelines": pipeline_checks},
        warnings=warnings,
        errors=errors,
    )
