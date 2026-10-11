# Real-Time E-Commerce Data Engineering & AI Analytics Platform

A production-grade, enterprise-scale Data Engineering and AI analytics platform integrating synthetic data generation, PostgreSQL/Supabase ingestion, data validation, batch ETL, Bronze/Silver/Gold data lake layers, Apache Airflow orchestration, star-schema data warehouse, DuckDB SQL analytics, machine learning (customer segmentation, churn prediction, sales forecasting, recommendation system), automated ML pipelines, FastAPI REST inference, platform monitoring, comprehensive testing, and Docker containerization.

---

## Architecture Overview

```
+---------------------------------------------------------------------------------------------------------+
|                                              HOST / CLIENT                                              |
|                                     Browser / REST Client / CLI                                         |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                   [ Bridge: ecommerce-network ]
                                                     |
         +-------------------------------------------+-------------------------------------------+
         |                                           |                                           |
+--------+--------+                         +--------+--------+                         +--------+--------+
|  FastAPI (API)  |                         | Apache Airflow  |                         |  Apache Kafka   |
|   Port: 8000    |                         |   Port: 8080    |                         |   Port: 9092    |
|  (Inference)    |                         | (Orchestration) |                         | (Event Stream)  |
+--------+--------+                         +--------+--------+                         +--------+--------+
         |                                           |                                           |
         |                                  +--------+--------+                         +--------+--------+
         |                                  |   Airflow DB    |                         |  Apache Spark   |
         |                                  | (PostgreSQL 13) |                         |  Master: 8081   |
         |                                  +-----------------+                         +--------+--------+
         |                                           |                                           |
+----------------------------------------------------+---------------------------------------------------+
|                               SHARED STORAGE & PERSISTENCE                                              |
|  - data/raw, data/processed, data/lake (Bronze/Silver/Gold Parquet)                                    |
|  - data/warehouse, data/models (ML Registry), data/testing, data/monitoring                            |
|  - Named volumes for Airflow & Kafka state                                                             |
+---------------------------------------------------------------------------------------------------------+
```

---

## Platform Features & Modules

1. **Synthetic Data Generation** (`dataset_generator/`): Deterministic e-commerce transaction, user, and event generator.
2. **Database Integration** (`ingestion/`): Supabase PostgreSQL ORM models and ingestion pipeline.
3. **Data Quality & Validation** (`validation/`): Comprehensive data quality rules and validator.
4. **Batch ETL Pipeline** (`etl/`): Robust Extract, Transform, Load processes with clean Parquet outputs.
5. **Data Lake Architecture** (`data_lake/`): Medallion architecture featuring Bronze, Silver, and Gold Parquet layers.
6. **Airflow Orchestration** (`airflow/`): Production DAGs (`automated_ml_pipeline.py`, `ecommerce_pipeline.py`).
7. **Real-Time Event Generation** (`realtime/`): High-throughput event generator and buffered writers.
8. **Near-Real-Time Stream Processing** (`streaming/`): Micro-batch event ingestion and metrics tracking.
9. **PySpark Processing** (`spark_processing/`): Distributed large-scale transformations and analytics.
10. **Data Warehouse** (`data_warehouse/`): Kimball dimensional star schema and fact table generator.
11. **SQL Analytics** (`sql_analytics/`): In-memory analytical queries and executive KPI metrics via DuckDB.
12. **Customer Segmentation** (`customer_segmentation/`): RFM feature engineering and KMeans clustering.
13. **Customer Churn Prediction** (`churn_prediction/`): Observation-window churn labeling, Random Forest modeling, and risk scoring.
14. **Sales Forecasting** (`sales_forecasting/`): Chronological lag/calendar feature engineering and multi-horizon forecasting.
15. **Recommendation System** (`recommendation_system/`): Collaborative, TF-IDF content-based, and hybrid recommendation engine.
16. **Automated ML Pipeline** (`ml_pipeline/`): End-to-end feature store, model training, evaluation, and registry.
17. **FastAPI REST API** (`api/`): Production REST service exposing `/health`, `/predict/churn`, `/forecast/sales`, `/recommendations/{user_id}`, and `/monitoring/health`.
18. **Platform Monitoring** (`monitoring/`): Data quality freshness, pipeline status, model drift, and API performance telemetry.
19. **Comprehensive Testing** (`tests/`): Complete Pytest test suite (109 tests) with deterministic fixtures and zero required external services. See [TESTING.md](file:///c:/Users/Lenovo/Downloads/E-Commerce/TESTING.md).
20. **Docker Containerization** (`Dockerfile`, `docker-compose.yml`): Production multi-service Docker Compose architecture. See [docker/README.md](file:///c:/Users/Lenovo/Downloads/E-Commerce/docker/README.md).

---

## Docker Quickstart

Ensure Docker Desktop is running on your machine:

```powershell
# 1. Validate Docker Compose configuration
docker compose -f docker-compose.yml config --quiet

# 2. Build and start the primary API service
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml up -d

# 3. Check API health
curl http://localhost:8000/health
# Interactive Swagger Documentation: http://localhost:8000/docs

# 4. Optional: Start Apache Airflow
docker compose -f docker-compose.airflow.yml up -d
# Airflow Web UI: http://localhost:8080 (admin / admin)

# 5. Optional: Start Apache Kafka (KRaft mode)
docker compose -f docker-compose.kafka.yml up -d
# Kafka UI: http://localhost:8085

# 6. Optional: Start Apache Spark Cluster
docker compose -f docker-compose.spark.yml up -d
# Spark Master UI: http://localhost:8081

# 7. Safe Shutdown (preserves persistent volumes)
docker compose -f docker-compose.yml down
```

For detailed containerization documentation, volume mapping, and multi-stack setups, consult [docker/README.md](file:///c:/Users/Lenovo/Downloads/E-Commerce/docker/README.md).

---

## Local Development & Testing

### Running Tests Outside Containers
```powershell
# Run the entire hermetic test suite (108 passed, 1 skipped)
python -m pytest -v

# Run API tests specifically
python -m pytest tests/api -v

# Generate test report JSON
python tests/report.py
```
Detailed testing documentation is available in [TESTING.md](file:///c:/Users/Lenovo/Downloads/E-Commerce/TESTING.md).
