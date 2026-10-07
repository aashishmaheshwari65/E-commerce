"""
monitoring/config.py

Centralised configuration for Functionality 20.
All paths are relative to the project root so the system
works on any machine without hardcoded absolute paths.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Project root – resolved once at import time.
# __file__ is  <project>/monitoring/config.py  →  parent is <project>/
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Data roots (overridable via environment variables)
# ---------------------------------------------------------------------------
DATA_ROOT = Path(os.getenv("MONITORING_DATA_ROOT", PROJECT_ROOT / "data"))
MONITORING_ROOT = Path(os.getenv("MONITORING_ROOT", DATA_ROOT / "monitoring"))

# ---------------------------------------------------------------------------
# Sub-directories that monitoring inspects
# ---------------------------------------------------------------------------
RAW_DATA_DIR = DATA_ROOT / "raw"
PROCESSED_DATA_DIR = DATA_ROOT / "processed"
LAKE_DIR = DATA_ROOT / "lake"
WAREHOUSE_DIR = DATA_ROOT / "warehouse"
ML_PIPELINE_DIR = DATA_ROOT / "ml_pipeline"
MODELS_DIR = DATA_ROOT / "models"
SEGMENTATION_DIR = DATA_ROOT / "customer_segmentation"
CHURN_DIR = DATA_ROOT / "churn_prediction"
FORECASTING_DIR = DATA_ROOT / "sales_forecasting"
RECOMMENDATIONS_DIR = DATA_ROOT / "recommendations"

# ---------------------------------------------------------------------------
# Monitoring output files
# ---------------------------------------------------------------------------
CURRENT_STATUS_FILE = MONITORING_ROOT / "current_status.json"
METRICS_FILE = MONITORING_ROOT / "metrics.json"
ALERTS_FILE = MONITORING_ROOT / "alerts.json"
HISTORY_FILE = MONITORING_ROOT / "history.jsonl"
SUMMARY_FILE = MONITORING_ROOT / "summary.txt"
REPORTS_DIR = MONITORING_ROOT / "reports"

# ---------------------------------------------------------------------------
# External service configuration
# ---------------------------------------------------------------------------
KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
)
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Airflow webserver (REST API v1)
AIRFLOW_BASE_URL = os.getenv("AIRFLOW_BASE_URL", "http://localhost:8080")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "airflow")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "airflow")

# ---------------------------------------------------------------------------
# Threshold defaults (all overridable via env vars)
# ---------------------------------------------------------------------------

# Data quality
MAX_NULL_PERCENTAGE = float(os.getenv("MAX_NULL_PERCENTAGE", "5.0"))
MAX_DUPLICATE_PERCENTAGE = float(os.getenv("MAX_DUPLICATE_PERCENTAGE", "1.0"))

# Data freshness
MAX_DATA_STALENESS_HOURS_WARN = float(
    os.getenv("MAX_DATA_STALENESS_HOURS_WARN", "24.0")
)
MAX_DATA_STALENESS_HOURS_CRITICAL = float(
    os.getenv("MAX_DATA_STALENESS_HOURS_CRITICAL", "72.0")
)

# Model age
MAX_MODEL_AGE_DAYS_WARN = float(os.getenv("MAX_MODEL_AGE_DAYS_WARN", "7.0"))
MAX_MODEL_AGE_DAYS_CRITICAL = float(
    os.getenv("MAX_MODEL_AGE_DAYS_CRITICAL", "30.0")
)

# ML performance
MIN_CHURN_ROC_AUC = float(os.getenv("MIN_CHURN_ROC_AUC", "0.70"))
MIN_CHURN_F1 = float(os.getenv("MIN_CHURN_F1", "0.65"))
MAX_FORECASTING_SMAPE = float(os.getenv("MAX_FORECASTING_SMAPE", "30.0"))
MIN_SEGMENTATION_SILHOUETTE = float(
    os.getenv("MIN_SEGMENTATION_SILHOUETTE", "0.20")
)
MIN_RECOMMENDATION_NDCG = float(os.getenv("MIN_RECOMMENDATION_NDCG", "0.05"))

# API performance
MAX_API_LATENCY_MS = float(os.getenv("MAX_API_LATENCY_MS", "500.0"))
API_TIMEOUT_SECONDS = float(os.getenv("API_TIMEOUT_SECONDS", "5.0"))
