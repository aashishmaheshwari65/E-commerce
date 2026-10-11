# Comprehensive Testing Framework (Functionality 21)

E-Commerce Data Engineering & AI Analytics Platform

---

## 1. Overview

The testing framework provides a modular, deterministic, and isolated `pytest` suite for the entire platform (Functionalities 1 through 20). 

### Key Guarantees
- **Hermetic & Isolated**: Tests use temporary directories (`tmp_path`) and synthetic fixtures.
- **Data Protection**: Tests **never** modify production or lake datasets (`data/raw/`, `data/lake/`, `data/warehouse/`).
- **Zero External Dependencies**: Standard unit and regression tests run without live Supabase credentials, Kafka brokers, Docker containers, Apache Airflow, or active Uvicorn processes.
- **Safe Database Testing**: Relies on an in-memory SQLite engine (`sqlite:///:memory:`) for schema creation and CRUD tests. Live external database tests skip cleanly when unconfigured.
- **Deterministic**: Random states are seeded across all ML fixtures to ensure reproducible outputs.

---

## 2. Directory Structure

```text
tests/
├── __init__.py
├── conftest.py                       # Root fixtures, temporary environments, transformed DataFrames, SQLite engine
├── report.py                         # Test runner emitting structured data/testing/test_report.json
├── fixtures/                         # Deterministic CSV mock tables (10 rows each)
│   ├── users.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── order_items.csv
│   ├── payments.csv
│   ├── reviews.csv
│   └── user_events.csv
├── validation/                       # Functionality 3: Data Quality & Schema Validation
│   ├── test_rules.py
│   └── test_validation.py
├── etl/                              # Functionality 4: Extract, Transform, Load Pipelines
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
├── database/                         # Functionality 2: Database / Supabase Schema & Operations
│   ├── test_database_connection.py
│   └── test_database_operations.py
├── data_lake/                        # Functionality 5: Bronze, Silver, Gold Lake Layers
│   ├── test_bronze.py
│   ├── test_silver.py
│   └── test_gold.py
├── data_warehouse/                   # Functionality 11: Star Schema & Fact Sales
│   └── test_warehouse.py
├── sql_analytics/                    # Functionality 12: DuckDB SQL Analytics
│   └── test_analytics.py
├── customer_segmentation/            # Functionality 14: RFM & KMeans Clustering
│   ├── test_features.py
│   ├── test_preprocessing.py
│   └── test_clustering.py
├── churn_prediction/                 # Functionality 15: Churn Risk Modeling & Probability
│   ├── test_features.py
│   ├── test_labeling.py
│   ├── test_preprocessing.py
│   ├── test_training.py
│   └── test_predictions.py
├── sales_forecasting/                # Functionality 16: Sales Forecasting & Feature Engineering
│   ├── test_aggregation.py
│   ├── test_features.py
│   ├── test_models.py
│   └── test_forecast.py
├── recommendation_system/            # Functionality 17: Collaborative, Content-Based, & Hybrid RecSys
│   ├── test_interactions.py
│   ├── test_content_features.py
│   ├── test_collaborative.py
│   ├── test_content_based.py
│   ├── test_hybrid.py
│   └── test_recommendations.py
├── ml_pipeline/                      # Functionality 18: End-to-End ML Pipeline & Model Registry
│   ├── test_features.py
│   ├── test_training.py
│   ├── test_evaluation.py
│   └── test_registry.py
├── api/                              # Functionality 19: FastAPI Endpoints via TestClient
│   ├── test_health.py
│   ├── test_churn.py
│   ├── test_forecasting.py
│   ├── test_recommendation.py
│   └── test_model_loader.py
├── monitoring/                       # Functionality 20: Platform & Pipeline Monitoring
│   ├── test_data_quality.py
│   ├── test_pipeline_monitoring.py
│   ├── test_ml_monitoring.py
│   └── test_api_monitoring.py
├── test_realtime.py                  # Functionality 7: Real-time Event Ingestion & Buffer
└── test_streaming.py                 # Functionality 8: Near-Real-Time Stream Processing
```

---

## 3. Pytest Configuration & Markers

Defined in `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v
markers =
    unit: Fast unit tests isolated to pure logic and mock data
    integration: Multi-stage pipeline integration tests
    database: Database schema and engine tests (SQLite / mock)
    ml: Machine learning feature engineering, model training, and inference tests
    api: FastAPI REST API route and schema validation tests
    slow: Long-running or resource-intensive tests
```

---

## 4. Test Execution Commands (PowerShell & Bash)

### Run Entire Test Suite
```powershell
python -m pytest -v
```

### Run Pytest Collection Only
```powershell
python -m pytest --collect-only -q
```

### Run by Functional Area
```powershell
# 1. Validation Tests
python -m pytest tests/validation -v

# 2. ETL Tests
python -m pytest tests/etl -v

# 3. Database Tests
python -m pytest tests/database -v

# 4. Data Lake Tests (Bronze / Silver / Gold)
python -m pytest tests/data_lake -v

# 5. Data Warehouse Tests (Star Schema)
python -m pytest tests/data_warehouse -v

# 6. SQL Analytics Tests (DuckDB)
python -m pytest tests/sql_analytics -v

# 7. Customer Segmentation Tests
python -m pytest tests/customer_segmentation -v

# 8. Churn Prediction Tests
python -m pytest tests/churn_prediction -v

# 9. Sales Forecasting Tests
python -m pytest tests/sales_forecasting -v

# 10. Recommendation System Tests
python -m pytest tests/recommendation_system -v

# 11. ML Pipeline & Registry Tests
python -m pytest tests/ml_pipeline -v

# 12. FastAPI Endpoint Tests
python -m pytest tests/api -v

# 13. Platform Monitoring Tests
python -m pytest tests/monitoring -v

# 14. Realtime & Streaming Tests
python -m pytest tests/test_realtime.py tests/test_streaming.py -v
```

### Run by Marker
```powershell
# Unit tests
python -m pytest -m unit -v

# ML tests
python -m pytest -m ml -v

# API tests
python -m pytest -m api -v

# Database tests
python -m pytest -m database -v
```

### Generate Coverage Report
```powershell
python -m pytest --cov=. --cov-report=term-missing
```

### Generate Automated JSON Report
```powershell
python tests/report.py
```
Outputs execution statistics, duration, and test counts to `data/testing/test_report.json`.

---

## 5. Continuous Integration (CI/CD)

The GitHub Actions workflow is defined at `.github/workflows/tests.yml`:
- Triggered on `push` and `pull_request` to `main`, `master`, and `dev`.
- Runs on `ubuntu-latest` with Python 3.11.
- Automatically installs required dependencies from `requirements.txt` and `requirements-api.txt`.
- Injects `DATABASE_URL: sqlite:///:memory:` so tests run hermetically without external secrets.
