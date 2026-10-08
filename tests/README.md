# Comprehensive Testing Framework

Real-Time E-Commerce Data Engineering & AI Analytics Platform

---

## 1. Overview

This testing framework provides an isolated, deterministic, and comprehensive `pytest` testing layer across all platform modules (Functionalities 1–20).

All tests:
- Run locally on Windows and on Linux (CI/CD).
- Use temporary directories (`tmp_path`) and small synthetic fixtures.
- **Never modify production data** in `data/raw/`, `data/lake/`, or `data/warehouse/`.
- **Never require external services** (Kafka, Docker, Apache Airflow, or live FastAPI servers).
- Mock or isolate database operations with in-memory SQLite and explicitly skip live database calls if `DATABASE_URL` is unconfigured.

---

## 2. Directory Structure

```
tests/
├── __init__.py
├── conftest.py                       # Shared deterministic fixtures and test helpers
├── report.py                         # Generates data/testing/test_report.json
├── fixtures/                         # Deterministic CSV data fixtures
│   ├── __init__.py
│   ├── users.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── order_items.csv
│   ├── payments.csv
│   ├── reviews.csv
│   └── user_events.csv
├── validation/                       # Functionality 3: Data Quality & Rules
│   ├── __init__.py
│   ├── test_rules.py
│   └── test_validation.py
├── etl/                              # Functionality 4: Extract, Transform, Load
│   ├── __init__.py
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
├── database/                         # Functionality 2: Database / Supabase Schema & Operations
│   ├── __init__.py
│   ├── test_database_connection.py
│   └── test_database_operations.py
├── data_lake/                        # Functionality 5: Bronze, Silver, Gold Lake Layers
│   ├── __init__.py
│   ├── test_bronze.py
│   ├── test_silver.py
│   └── test_gold.py
├── data_warehouse/                   # Functionality 11: Star Schema & Fact Sales
│   ├── __init__.py
│   └── test_warehouse.py
├── sql_analytics/                    # Functionality 12: SQL Analytics via DuckDB
│   ├── __init__.py
│   └── test_analytics.py
├── customer_segmentation/            # Functionality 14: RFM & KMeans Clustering
│   ├── __init__.py
│   ├── test_features.py
│   ├── test_preprocessing.py
│   └── test_clustering.py
├── churn_prediction/                 # Functionality 15: Churn Risk Modeling
│   ├── __init__.py
│   ├── test_features.py
│   ├── test_labeling.py
│   ├── test_preprocessing.py
│   ├── test_training.py
│   └── test_predictions.py
├── sales_forecasting/                # Functionality 16: Sales Forecasting
│   ├── __init__.py
│   ├── test_aggregation.py
│   ├── test_features.py
│   ├── test_models.py
│   └── test_forecast.py
├── recommendation_system/            # Functionality 17: Collaborative, Content, Hybrid RecSys
│   ├── __init__.py
│   ├── test_interactions.py
│   ├── test_content_features.py
│   ├── test_collaborative.py
│   ├── test_content_based.py
│   ├── test_hybrid.py
│   └── test_recommendations.py
├── ml_pipeline/                      # Functionality 18: Automated ML Pipeline & Registry
│   ├── __init__.py
│   ├── test_features.py
│   ├── test_training.py
│   ├── test_evaluation.py
│   └── test_registry.py
├── api/                              # Functionality 19: FastAPI REST Endpoints
│   ├── __init__.py
│   ├── test_health.py
│   ├── test_churn.py
│   ├── test_forecasting.py
│   ├── test_recommendation.py
│   └── test_model_loader.py
├── monitoring/                       # Functionality 20: Operational & Data Monitoring
│   ├── __init__.py
│   ├── test_data_quality.py
│   ├── test_pipeline_monitoring.py
│   ├── test_ml_monitoring.py
│   └── test_api_monitoring.py
├── test_realtime.py                  # Real-time event validation & buffer tests
└── test_streaming.py                 # Near-real-time streaming processor tests
```

---

## 3. Test Markers

Configured in `pytest.ini`:
- `unit`: Fast unit tests (default).
- `integration`: End-to-end multi-step flows.
- `database`: Tests interacting with database schema/engine.
- `ml`: Machine learning training, scoring, and feature tests.
- `api`: FastAPI route and schema tests.
- `slow`: Long-running or heavy tests.

---

## 4. Test Commands

### Run All Tests
```bash
python -m pytest -v
```

### Run Specific Functional Areas
```bash
# Data Validation
python -m pytest tests/validation -v

# ETL Pipelines
python -m pytest tests/etl -v

# Database Operations
python -m pytest tests/database -v

# Data Lake
python -m pytest tests/data_lake -v

# Data Warehouse
python -m pytest tests/data_warehouse -v

# SQL Analytics
python -m pytest tests/sql_analytics -v

# Machine Learning Modules
python -m pytest tests/customer_segmentation tests/churn_prediction tests/sales_forecasting tests/recommendation_system tests/ml_pipeline -v

# FastAPI REST Endpoints
python -m pytest tests/api -v

# Monitoring
python -m pytest tests/monitoring -v
```

### Filter by Marker
```bash
# Unit tests only
python -m pytest -m unit

# ML tests only
python -m pytest -m ml

# API tests only
python -m pytest -m api
```

### Coverage Report
```bash
python -m pytest --cov=. --cov-report=term-missing
```

### Generate Automated Test Report
```bash
python -m tests.report
```
Generates `data/testing/test_report.json` with execution counts, duration, and status.

---

## 5. CI/CD Integration

A GitHub Actions workflow is provided at `.github/workflows/tests.yml`. It runs automatically on pushes and pull requests against `ubuntu-latest` without requiring external services or secrets.
