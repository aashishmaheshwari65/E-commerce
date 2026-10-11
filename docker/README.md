# Docker Containerization Guide (Functionality 22)

E-Commerce Data Engineering & AI Analytics Platform

---

## 1. Overview & Architecture

This repository provides a modular, containerized multi-service architecture using Docker and Docker Compose. Each functional layer is decoupled into distinct services connected via a private bridge network (`ecommerce-network`):

```
+---------------------------------------------------------------------------------+
|                                 Host System                                     |
|  - Windows / PowerShell / Linux                                                 |
|  - Browser / Postman (http://localhost:8000, 8080, 8081, 8085)                 |
+---------------------------------------------------------------------------------+
                                      |
                         [ Bridge: ecommerce-network ]
                                      |
     +--------------------------------+--------------------------------+
     |                                |                                |
+----+----+                      +----+----+                      +----+----+
|   API   |                      | Airflow |                      |  Kafka  |
| Service |                      | Cluster |                      | (KRaft) |
+----+----+                      +----+----+                      +----+----+
     |                                |                                |
  FastAPI                         Webserver                        Single-Node
  Uvicorn                         Scheduler                        KRaft Broker
  Port 8000                       Postgres DB                      Port 9092 / 29092
                                  Port 8080                        Kafka UI: 8085
                                      |
                                 +----+----+
                                 |  Spark  |
                                 | Cluster |
                                 +----+----+
                                      |
                                  Master (7077 / 8081)
                                  Worker (8082)
                                      |
                     [ Shared Persistent Storage ]
                     - ./data (Parquet lake, models, warehouse)
                     - Named volumes for Airflow & Kafka
```

---

## 2. Prerequisites

1. **Docker Desktop**: Version 20.10+ (with Docker Compose v2.0+).
   - Ensure WSL 2 backend is enabled in Docker Desktop settings on Windows.
2. **Environment File**:
   Copy `.env.example` to `.env` in the project root:
   ```powershell
   Copy-Item .env.example .env
   ```
   Provide your Supabase / PostgreSQL credentials if running database pipelines.

---

## 3. Quickstart: Core API & Application

The primary stack runs the production FastAPI inference service.

### Build and Start
```powershell
# Build application image
docker compose build

# Start API service in detached mode
docker compose up -d

# Verify container status and health
docker compose ps
```

### Accessing the API
- **Root Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Model Health Check**: [http://localhost:8000/health/models](http://localhost:8000/health/models)
- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Check Logs
```powershell
docker compose logs -f api
```

### Graceful Shutdown
```powershell
# Stops containers without deleting persistent host data or named volumes
docker compose down
```

---

## 4. Apache Airflow Orchestration Stack

The Airflow stack orchestrates the automated data engineering and ML pipelines (`automated_ml_pipeline.py` and `ecommerce_pipeline.py`).

### Start Airflow
```powershell
docker compose -f docker-compose.airflow.yml up -d
```

### Airflow Services
- **`airflow-postgres`**: Dedicated PostgreSQL metadata database (isolated from Supabase).
- **`airflow-init`**: Automatically initializes metadata tables and registers the default admin user.
- **`airflow-webserver`**: Local Web UI at [http://localhost:8080](http://localhost:8080).
  - **Username**: `admin`
  - **Password**: `admin`
- **`airflow-scheduler`**: Executes scheduled DAG runs.

### Shutdown Airflow
```powershell
docker compose -f docker-compose.airflow.yml down
```

---

## 5. Optional Services

### A. Apache Kafka (KRaft Mode)
Used for real-time event streaming without ZooKeeper.

```powershell
# Start Kafka and Kafka UI
docker compose -f docker-compose.kafka.yml up -d

# View Kafka status
docker compose -f docker-compose.kafka.yml ps

# Open Kafka UI in browser
# http://localhost:8085

# Stop Kafka
docker compose -f docker-compose.kafka.yml down
```

- **Container connection**: `kafka:9092`
- **Windows host connection**: `localhost:29092`

### B. Apache Spark Standalone Cluster
Used for distributed PySpark processing (`spark_processing/`).

```powershell
# Start Spark Master and Worker
docker compose -f docker-compose.spark.yml up -d

# Spark Master Web UI: http://localhost:8081
# Spark Worker Web UI: http://localhost:8082
# Master RPC URL: spark://spark-master:7077

# Submit a Spark job inside the cluster
docker exec -it ecommerce-spark-master spark-submit \
  --master spark://spark-master:7077 \
  /opt/bitnami/spark/spark_processing/main.py

# Stop Spark
docker compose -f docker-compose.spark.yml down
```

---

## 6. Multi-Stack Execution

To run multiple services simultaneously, combine compose files:

```powershell
# Run API + Airflow together
docker compose -f docker-compose.yml -f docker-compose.airflow.yml up -d

# Run All Services (API + Airflow + Kafka + Spark)
docker compose -f docker-compose.yml -f docker-compose.airflow.yml -f docker-compose.kafka.yml -f docker-compose.spark.yml up -d

# Stop All Services
docker compose -f docker-compose.yml -f docker-compose.airflow.yml -f docker-compose.kafka.yml -f docker-compose.spark.yml down
```

---

## 7. Storage, Volumes, and Persistence

| Resource | Mount / Volume | Description |
| :--- | :--- | :--- |
| **Data Lake & Models** | `./data:/app/data` (Host mount) | Parquet Bronze/Silver/Gold layers, feature store, and serialized model files (`.pkl`, `.joblib`). |
| **Airflow Metadata** | `ecommerce-airflow-postgres-data` (Named volume) | Persists Airflow connection metadata and execution history across container restarts. |
| **Airflow DAGs & Logs**| `./airflow/dags`, `./airflow/logs` (Host mount) | Real-time DAG sync and host-inspectable scheduler logs. |
| **Kafka Messages** | `ecommerce-kafka-data` (Named volume) | Persists topic logs and commit offsets. |

---

## 8. Running Tests

### Outside Containers (Host Environment)
```powershell
python -m pytest -v
```

### Inside the API Docker Container
```powershell
# Run tests inside the running API container
docker exec -it ecommerce-api python -m pytest -v

# Or run an ephemeral test container
docker compose run --rm api python -m pytest -v
```

---

## 9. Troubleshooting & Common Scenarios

1. **Port Already in Use**:
   If port 8000 or 8080 is occupied, set custom ports in your `.env` file:
   ```env
   API_PORT=8001
   ```
2. **Rebuilding After Code Changes**:
   Whenever Python files or requirements change, rebuild the image:
   ```powershell
   docker compose build --no-cache
   docker compose up -d
   ```
3. **Inspect Container Logs**:
   ```powershell
   docker logs ecommerce-api
   docker logs airflow-scheduler
   docker logs ecommerce-kafka
   ```
