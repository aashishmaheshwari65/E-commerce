"""
monitoring/collectors/data_quality.py

Data quality collector for Functionality 20.

Inspects the raw CSV datasets using the same rules implemented
in Functionality 3 (validation/rules.py) and reports counts,
null rates, duplicate violations, and data freshness.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from monitoring.config import (
    RAW_DATA_DIR,
    MAX_NULL_PERCENTAGE,
    MAX_DUPLICATE_PERCENTAGE,
    MAX_DATA_STALENESS_HOURS_WARN,
    MAX_DATA_STALENESS_HOURS_CRITICAL,
)
from monitoring.models import ComponentResult, ComponentStatus

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dataset definitions  (name → file, pk_col, timestamp_col)
# ---------------------------------------------------------------------------
_DATASETS: list[dict] = [
    {
        "name": "users",
        "file": "users.csv",
        "pk": "user_id",
        "ts_col": "registration_date",
    },
    {
        "name": "products",
        "file": "products.csv",
        "pk": "product_id",
        "ts_col": None,
    },
    {
        "name": "orders",
        "file": "orders.csv",
        "pk": "order_id",
        "ts_col": "order_date",
    },
    {
        "name": "order_items",
        "file": "order_items.csv",
        "pk": "order_item_id",
        "ts_col": None,
    },
    {
        "name": "payments",
        "file": "payments.csv",
        "pk": "payment_id",
        "ts_col": "payment_date",
    },
    {
        "name": "reviews",
        "file": "reviews.csv",
        "pk": "review_id",
        "ts_col": "review_date",
    },
    {
        "name": "user_events",
        "file": "user_events.csv",
        "pk": "event_id",
        "ts_col": "event_timestamp",
    },
]


def _age_hours(ts: pd.Timestamp) -> float:
    """Return age in hours from a pandas Timestamp to now (UTC)."""
    now = pd.Timestamp.now(tz="UTC")
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return (now - ts).total_seconds() / 3600.0


def _check_dataset(
    dataset: dict,
    raw_dir: Path,
) -> dict[str, Any]:
    """Run quality checks on a single CSV dataset."""
    result: dict[str, Any] = {
        "dataset": dataset["name"],
        "file_exists": False,
        "row_count": 0,
        "column_count": 0,
        "null_count": 0,
        "null_percentage": 0.0,
        "duplicate_pk_count": 0,
        "freshness": None,
        "errors": [],
        "warnings": [],
    }

    fpath = raw_dir / dataset["file"]
    if not fpath.exists():
        result["errors"].append(f"File not found: {fpath.name}")
        return result

    try:
        df = pd.read_csv(fpath)
    except Exception as exc:
        result["errors"].append(f"Failed to read {fpath.name}: {exc}")
        return result

    result["file_exists"] = True
    result["row_count"] = len(df)
    result["column_count"] = len(df.columns)

    # Null check
    null_count = int(df.isnull().sum().sum())
    total_cells = len(df) * len(df.columns)
    null_pct = (null_count / total_cells * 100) if total_cells > 0 else 0.0
    result["null_count"] = null_count
    result["null_percentage"] = round(null_pct, 2)

    if null_pct > MAX_NULL_PERCENTAGE:
        result["warnings"].append(
            f"Null percentage {null_pct:.1f}% exceeds threshold "
            f"{MAX_NULL_PERCENTAGE}%"
        )

    # Duplicate primary-key check
    pk = dataset.get("pk")
    if pk and pk in df.columns:
        dup_count = int(df[pk].duplicated().sum())
        result["duplicate_pk_count"] = dup_count
        if dup_count > 0:
            dup_pct = dup_count / len(df) * 100
            if dup_pct > MAX_DUPLICATE_PERCENTAGE:
                result["errors"].append(
                    f"Duplicate {pk} found: {dup_count} rows "
                    f"({dup_pct:.1f}%)"
                )
            else:
                result["warnings"].append(
                    f"Duplicate {pk} found: {dup_count} rows "
                    f"({dup_pct:.1f}%)"
                )

    # Freshness
    ts_col = dataset.get("ts_col")
    if ts_col and ts_col in df.columns:
        try:
            parsed = pd.to_datetime(df[ts_col], errors="coerce")
            latest = parsed.dropna().max()
            if pd.isnull(latest):
                result["freshness"] = {"status": "UNKNOWN", "reason": "no valid timestamps"}
            else:
                age_h = _age_hours(latest)
                fs = {
                    "latest_timestamp": str(latest),
                    "age_hours": round(age_h, 2),
                }
                if age_h > MAX_DATA_STALENESS_HOURS_CRITICAL:
                    fs["status"] = "CRITICAL"
                    result["errors"].append(
                        f"{dataset['name']} data is {age_h:.1f}h old "
                        f"(threshold: {MAX_DATA_STALENESS_HOURS_CRITICAL}h)"
                    )
                elif age_h > MAX_DATA_STALENESS_HOURS_WARN:
                    fs["status"] = "WARNING"
                    result["warnings"].append(
                        f"{dataset['name']} data is {age_h:.1f}h old "
                        f"(threshold: {MAX_DATA_STALENESS_HOURS_WARN}h)"
                    )
                else:
                    fs["status"] = "HEALTHY"
                result["freshness"] = fs
        except Exception as exc:
            result["freshness"] = {
                "status": "UNKNOWN",
                "reason": str(exc),
            }
    else:
        result["freshness"] = {
            "status": "UNKNOWN",
            "reason": "no timestamp column defined",
        }

    return result


def collect(raw_dir: Path | None = None) -> ComponentResult:
    """
    Run data quality checks on all raw datasets.

    Parameters
    ----------
    raw_dir:
        Override the raw data directory (used in tests).
    """
    raw_dir = raw_dir or RAW_DATA_DIR
    ts = datetime.now(timezone.utc).isoformat()

    dataset_results: list[dict] = []
    all_warnings: list[str] = []
    all_errors: list[str] = []

    for ds in _DATASETS:
        res = _check_dataset(ds, raw_dir)
        dataset_results.append(res)
        all_warnings.extend(res["warnings"])
        all_errors.extend(res["errors"])

    # Aggregate metrics
    total_rows = sum(r["row_count"] for r in dataset_results)
    total_nulls = sum(r["null_count"] for r in dataset_results)
    total_dup_pks = sum(r["duplicate_pk_count"] for r in dataset_results)
    tables_checked = sum(1 for r in dataset_results if r["file_exists"])

    # Determine status
    if all_errors:
        status = ComponentStatus.CRITICAL
    elif all_warnings:
        status = ComponentStatus.WARNING
    else:
        status = ComponentStatus.HEALTHY

    return ComponentResult(
        component="data_quality",
        status=status,
        timestamp=ts,
        metrics={
            "tables_checked": tables_checked,
            "rows_checked": total_rows,
            "null_violations": total_nulls,
            "duplicate_pk_violations": total_dup_pks,
            "datasets": dataset_results,
        },
        warnings=all_warnings,
        errors=all_errors,
    )
