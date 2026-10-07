# Functionality 20: Monitoring

Real-Time E-Commerce Data Engineering & AI Analytics Platform

---

## Overview

The monitoring module provides continuous health visibility across all platform components (Functionalities 1–19). It collects real metrics, evaluates configurable thresholds, generates alerts, stores historical data, and produces human- and machine-readable reports.

---

## Architecture

```
monitoring/
├── config.py              # All paths and thresholds (env-overridable)
├── models.py              # Status enums and dataclasses
├── collectors/
│   ├── data_quality.py    # Raw CSV inspection
│   ├── pipelines.py       # Pipeline artifact + Airflow check
│   ├── kafka.py           # Kafka probe (graceful NOT_CONFIGURED)
│   ├── ml.py              # Model age, version, metrics
│   └── api.py             # FastAPI latency and availability
├── checks/
│   ├── thresholds.py      # Centralized threshold evaluation → Alerts
│   └── health.py          # Component → overall status aggregation
├── storage/
│   └── metrics_store.py   # Writes JSON files, appends history.jsonl
├── reporting/
│   └── report.py          # summary.txt + monitoring_report.json
├── main.py                # CLI entry-point
└── tests/                 # pytest test suite
```

Output directory: `data/monitoring/`

```
data/monitoring/
├── current_status.json     # Full snapshot of most recent run
├── metrics.json            # Metrics-only subset
├── alerts.json             # Alerts from most recent run
├── history.jsonl           # Append-only history (never overwritten)
├── summary.txt             # Human-readable report
└── reports/
    └── monitoring_report.json
```

---

## Component Monitoring

| Component | What is monitored |
|-----------|------------------|
| Data Quality | Row counts, null rates, duplicate PKs, data freshness from real timestamp columns |
| ETL | Parquet output existence and freshness |
| Data Lake | Bronze / Silver / Gold layer artifact count |
| Data Warehouse | fact_sales and dimension table existence |
| Airflow | DAG state and latest run via REST API (graceful UNKNOWN if down) |
| ML Pipeline | pipeline_runs.json – latest/successful run, selected models |
| Customer Segmentation | Output artifact existence |
| Churn Prediction | Output artifact existence |
| Sales Forecasting | Output artifact existence |
| Recommendation System | Output artifact existence |
| Kafka | Broker reachability (gracefully NOT_CONFIGURED if deferred) |
| ML Models | Age, version, training metrics per domain |
| FastAPI | /health and /health/models latency and HTTP status |

---

## Status Values

| Status | Meaning |
|--------|---------|
| `HEALTHY` | All checks pass |
| `WARNING` | At least one threshold exceeded but not critical |
| `CRITICAL` | At least one critical threshold exceeded |
| `UNKNOWN` | Cannot determine status (service unreachable, no data) |
| `NOT_CONFIGURED` | Component intentionally excluded (e.g., Kafka) |

### Overall Status Rules

- Any `CRITICAL` component → overall `CRITICAL`
- Any `WARNING` (no CRITICAL) → overall `WARNING`
- All healthy → `HEALTHY`
- `NOT_CONFIGURED` components are excluded from escalation
- Mix of `HEALTHY` + `UNKNOWN` → `WARNING`

---

## Kafka Monitoring

Kafka was intentionally deferred in this project.

- The collector **never** fails the monitoring system.
- If Kafka is unreachable or `kafka-python` is not installed → status = `NOT_CONFIGURED`
- `NOT_CONFIGURED` does not cause system-wide `CRITICAL`

To test with a real Kafka, set:
```
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

---

## Airflow Monitoring

Airflow is monitored via its REST API (`/api/v1/dags`).

- If Airflow is not running → status = `UNKNOWN`
- DAGs checked: `automated_ml_pipeline`, `ecommerce_data_pipeline`

Configure:
```
AIRFLOW_BASE_URL=http://localhost:8080
AIRFLOW_USERNAME=airflow
AIRFLOW_PASSWORD=airflow
```

---

## ML Monitoring

Models checked: `churn`, `segmentation`, `forecasting`, `recommendation`

- Model availability (`.joblib` artifact)
- Model version (directory name)
- Training timestamp and age
- Evaluation metrics from `data/ml_pipeline/metrics/*.json`

### Model Age Thresholds

| Threshold | Default |
|-----------|---------|
| `MAX_MODEL_AGE_DAYS_WARN` | 7 days |
| `MAX_MODEL_AGE_DAYS_CRITICAL` | 30 days |

### Performance Thresholds

| Metric | Threshold | Direction |
|--------|-----------|-----------|
| `churn_roc_auc` | ≥ 0.70 | below = bad |
| `churn_f1` | ≥ 0.65 | below = bad |
| `forecasting_smape` | ≤ 30% | above = bad |
| `segmentation_silhouette` | ≥ 0.20 | below = bad |
| `recommendation_ndcg` | ≥ 0.05 | below = bad |

---

## FastAPI Monitoring

Endpoints probed:
- `GET /health`
- `GET /health/models`

| Threshold | Default |
|-----------|---------|
| `MAX_API_LATENCY_MS` | 500 ms |
| `API_TIMEOUT_SECONDS` | 5 s |

If FastAPI is not running → status = `UNKNOWN` (not CRITICAL).

---

## Data Quality Thresholds

| Threshold | Default |
|-----------|---------|
| `MAX_NULL_PERCENTAGE` | 5% |
| `MAX_DUPLICATE_PERCENTAGE` | 1% |
| `MAX_DATA_STALENESS_HOURS_WARN` | 24 h |
| `MAX_DATA_STALENESS_HOURS_CRITICAL` | 72 h |

---

## CLI Commands

```bash
# Run all collectors (default)
python -m monitoring.main
python -m monitoring.main --all

# Individual components
python -m monitoring.main --data-quality
python -m monitoring.main --pipelines
python -m monitoring.main --kafka
python -m monitoring.main --ml
python -m monitoring.main --api

# Display latest saved report without running collectors
python -m monitoring.main --report
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | HEALTHY (or NOT_CONFIGURED only) |
| 1 | WARNING |
| 2 | CRITICAL |
| 3 | UNKNOWN |

---

## API Monitoring Endpoints (Functionality 19 Integration)

These endpoints serve the **stored** results of the last monitoring run.
Zero per-request collection overhead.

| Endpoint | Description |
|----------|-------------|
| `GET /monitoring` | Overall status and component summary |
| `GET /monitoring/metrics` | Per-component metrics |
| `GET /monitoring/alerts` | List of alerts from last run |
| `GET /monitoring/health` | Component health with warnings/errors |

To populate these endpoints, run monitoring first:
```bash
python -m monitoring.main --all
python -m uvicorn api.main:app --reload
# then visit http://127.0.0.1:8000/monitoring
```

---

## Historical Metrics

`data/monitoring/history.jsonl` grows with every run. It is **never overwritten**.

Each record contains:
```json
{
  "run_id": "20261007_120000",
  "timestamp": "2026-10-07T12:00:00+00:00",
  "overall_status": "HEALTHY",
  "component_statuses": {
    "data_quality": "HEALTHY",
    "pipelines": "WARNING",
    "kafka": "NOT_CONFIGURED",
    "ml": "HEALTHY",
    "fastapi": "UNKNOWN"
  },
  "alert_count": 1
}
```

---

## Alerts

`data/monitoring/alerts.json` is overwritten each run with the current run's alerts.

Alert format:
```json
{
  "timestamp": "2026-10-07T12:00:00+00:00",
  "severity": "WARNING",
  "component": "ml",
  "metric": "model_age_days[churn]",
  "value": 8.5,
  "threshold": 7.0,
  "message": "model_age_days value 8.5 exceeds warning threshold 7.0 days"
}
```

Alerts are deduplicated within a single run (no duplicate `component+metric+severity` triplets).

---

## Optional Prometheus Support

The monitoring system is designed to be Prometheus-compatible.
Metrics stored in `data/monitoring/metrics.json` can be exported
to a Prometheus exporter without changes to the core module.

To add Prometheus export later:
```bash
pip install prometheus-client
```
Then create `monitoring/exporters/prometheus.py` that reads `metrics.json`
and exposes a `/metrics` endpoint. Prometheus is **not** required for the
core monitoring system.

---

## Running Tests

```bash
python -m pytest monitoring/tests -v
```

Tests use `tmp_path` fixtures and small synthetic data.
No external services are required (Kafka, Airflow, FastAPI all mocked/skipped).

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MONITORING_DATA_ROOT` | `data/` | Project data root |
| `MONITORING_ROOT` | `data/monitoring/` | Monitoring output directory |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka broker address |
| `API_BASE_URL` | `http://127.0.0.1:8000` | FastAPI base URL |
| `AIRFLOW_BASE_URL` | `http://localhost:8080` | Airflow base URL |
| `MAX_NULL_PERCENTAGE` | `5.0` | Null rate warning threshold (%) |
| `MAX_DUPLICATE_PERCENTAGE` | `1.0` | Duplicate PK warning threshold (%) |
| `MAX_DATA_STALENESS_HOURS_WARN` | `24.0` | Data freshness warning (hours) |
| `MAX_DATA_STALENESS_HOURS_CRITICAL` | `72.0` | Data freshness critical (hours) |
| `MAX_MODEL_AGE_DAYS_WARN` | `7.0` | Model age warning (days) |
| `MAX_MODEL_AGE_DAYS_CRITICAL` | `30.0` | Model age critical (days) |
| `MAX_API_LATENCY_MS` | `500.0` | API latency warning (ms) |

---

## Troubleshooting

**`No monitoring data available`**
→ Run `python -m monitoring.main --all` first.

**Kafka shows `NOT_CONFIGURED`**
→ Expected. Kafka was deferred. This is not a failure.

**FastAPI shows `UNKNOWN`**
→ Start the API: `python -m uvicorn api.main:app --reload`
→ Then re-run `python -m monitoring.main --api`

**Airflow shows `UNKNOWN`**
→ Airflow is monitored via Docker. Start it with `docker-compose up airflow-webserver`.
→ This is not a system failure.

**ML shows `CRITICAL`**
→ Run the ML pipeline: `python -m ml_pipeline.main`

---

## Integration with Functionalities 1-19

| Functionality | How Monitoring Integrates |
|---------------|--------------------------|
| 1 – Data Generation | Monitors raw CSV row counts and freshness |
| 2 – Supabase Ingestion | Indirectly via data quality checks |
| 3 – Data Validation | Reuses validation rule patterns |
| 4 – Batch ETL | Checks processed/ parquet output |
| 5 – Data Lake | Verifies Bronze/Silver/Gold layers |
| 6 – Airflow | REST API DAG health check |
| 7 – Real-time Events | Checks user_events.csv freshness |
| 8 – Kafka Streaming | Gracefully reports NOT_CONFIGURED |
| 9 – Near-RT Processing | Checks realtime/ output |
| 10 – PySpark | Checks spark-processed artifacts |
| 11 – Data Warehouse | Verifies fact_sales and dimensions |
| 12 – SQL Analytics | Checks analytics output files |
| 13 – Power BI | External; not directly monitored |
| 14 – Segmentation | Checks output files, model age |
| 15 – Churn Prediction | ROC-AUC, F1, model age, artifacts |
| 16 – Sales Forecasting | sMAPE, MAE, model age, artifacts |
| 17 – Recommendation | NDCG@10, coverage, model age |
| 18 – ML Pipeline | pipeline_runs.json status, selected models |
| 19 – FastAPI | /health and /health/models latency |
