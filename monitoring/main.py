"""
monitoring/main.py

CLI entry-point for Functionality 20: Monitoring.

Usage:
    python -m monitoring.main [options]

Options:
    --all            Run all collectors (default)
    --data-quality   Run data quality collector only
    --pipelines      Run pipeline health collector only
    --kafka          Run Kafka collector only
    --ml             Run ML model collector only
    --api            Run FastAPI collector only
    --report         Generate/display the latest report only (no collection)

Exit codes:
    0  HEALTHY or NOT_CONFIGURED only
    1  WARNING
    2  CRITICAL
    3  UNKNOWN (any component unknown, nothing critical/warning)
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
)
logger = logging.getLogger("monitoring.main")


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _collect_all(args: argparse.Namespace) -> None:
    """Run all or selected collectors, aggregate, save, and report."""
    from monitoring.collectors import data_quality, pipelines, kafka, ml, api
    from monitoring.checks import health, thresholds
    from monitoring.storage import metrics_store
    from monitoring.reporting import report
    from monitoring.models import ComponentStatus

    run_id = _run_id()
    logger.info("Monitoring run %s started", run_id)

    results = []

    run_all = args.all or not any(
        [args.data_quality, args.pipelines, args.kafka, args.ml, args.api]
    )

    if run_all or args.data_quality:
        logger.info("Collecting data quality metrics...")
        try:
            results.append(data_quality.collect())
        except Exception as exc:
            logger.error("data_quality collector failed: %s", exc)

    if run_all or args.pipelines:
        logger.info("Collecting pipeline health metrics...")
        try:
            results.append(pipelines.collect())
        except Exception as exc:
            logger.error("pipelines collector failed: %s", exc)

    if run_all or args.kafka:
        logger.info("Collecting Kafka status...")
        try:
            results.append(kafka.collect())
        except Exception as exc:
            logger.error("kafka collector failed: %s", exc)

    if run_all or args.ml:
        logger.info("Collecting ML model metrics...")
        try:
            results.append(ml.collect())
        except Exception as exc:
            logger.error("ml collector failed: %s", exc)

    if run_all or args.api:
        logger.info("Collecting FastAPI metrics...")
        try:
            results.append(api.collect())
        except Exception as exc:
            logger.error("api collector failed: %s", exc)

    if not results:
        logger.error("No collector results – nothing to report.")
        sys.exit(3)

    # Generate alerts from threshold evaluation
    all_alerts = []
    for res in results:
        _alerts = _evaluate_component_alerts(res)
        all_alerts.extend(_alerts)

    # Deduplicate alerts by (component, metric, severity)
    seen = set()
    unique_alerts = []
    for a in all_alerts:
        key = (a.component, a.metric, a.severity)
        if key not in seen:
            seen.add(key)
            unique_alerts.append(a)

    # Aggregate snapshot
    snapshot = health.aggregate(run_id, results, unique_alerts)

    # Persist
    metrics_store.save(snapshot)

    # Generate reports
    summary_text = report.generate_summary(snapshot)
    report.generate_json_report(snapshot)

    # Print to console — encode safely for Windows cp1252 terminals
    try:
        print(summary_text)
    except UnicodeEncodeError:
        # Strip non-ASCII characters and retry (Windows legacy console)
        safe_text = summary_text.encode("ascii", errors="replace").decode("ascii")
        print(safe_text)


    status = snapshot.overall_status
    if status == ComponentStatus.CRITICAL:
        sys.exit(1)
    else:
        sys.exit(0)


def _evaluate_component_alerts(result) -> list:
    """Extract threshold alerts from a single ComponentResult."""
    from monitoring.checks.thresholds import evaluate

    alerts = []
    comp = result.component
    m = result.metrics

    if comp == "data_quality":
        # Null percentage per dataset
        for ds in m.get("datasets", []):
            a = evaluate(
                "null_percentage",
                ds.get("null_percentage"),
                component=comp,
            )
            if a:
                a.metric = f"null_percentage[{ds['dataset']}]"
                alerts.append(a)

    elif comp == "ml":
        for domain_info in m.get("domains", []):
            domain = domain_info["domain"]
            dm = domain_info.get("metrics", {})
            age = domain_info.get("age_days")

            # Model age
            if age is not None:
                a = evaluate("model_age_days", age, component=comp)
                if a:
                    a.metric = f"model_age_days[{domain}]"
                    alerts.append(a)

            # Domain-specific metrics
            if domain == "churn":
                for metric in ("churn_roc_auc", "churn_f1"):
                    key = metric.replace("churn_", "")
                    val = dm.get(key) or dm.get(metric)
                    a = evaluate(metric, val, component=comp)
                    if a:
                        alerts.append(a)

            elif domain == "forecasting":
                a = evaluate(
                    "forecasting_smape", dm.get("smape"), component=comp
                )
                if a:
                    alerts.append(a)

            elif domain == "segmentation":
                a = evaluate(
                    "segmentation_silhouette",
                    dm.get("silhouette_score"),
                    component=comp,
                )
                if a:
                    alerts.append(a)

            elif domain == "recommendation":
                a = evaluate(
                    "recommendation_ndcg",
                    dm.get("ndcg_10"),
                    component=comp,
                )
                if a:
                    alerts.append(a)

    elif comp == "fastapi":
        for probe in m.get("probes", []):
            a = evaluate(
                "api_response_ms",
                probe.get("response_ms"),
                component=comp,
            )
            if a:
                a.metric = f"api_response_ms[{probe.get('endpoint', '?')}]"
                alerts.append(a)

    return alerts


def _show_report() -> None:
    """Display the most recently saved report."""
    from monitoring.storage.metrics_store import load_current

    data = load_current()
    if data is None:
        print("No monitoring data found. Run: python -m monitoring.main --all")
        sys.exit(3)

    import json

    print(json.dumps(data, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="E-Commerce Platform Monitoring CLI (Functionality 20)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Run all collectors (default when no flag is given)",
    )
    parser.add_argument(
        "--data-quality",
        dest="data_quality",
        action="store_true",
        help="Run data quality collector",
    )
    parser.add_argument(
        "--pipelines",
        action="store_true",
        help="Run pipeline health collector",
    )
    parser.add_argument(
        "--kafka",
        action="store_true",
        help="Run Kafka status collector",
    )
    parser.add_argument(
        "--ml",
        action="store_true",
        help="Run ML model health collector",
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Run FastAPI health collector",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Display latest saved report without collecting new data",
    )

    args = parser.parse_args()

    if args.report:
        _show_report()
    else:
        _collect_all(args)


if __name__ == "__main__":
    main()
