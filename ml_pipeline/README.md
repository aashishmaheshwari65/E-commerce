# Functionality 18: Automated ML Pipeline

## Overview
Functionality 18 implements a production-style, modular Automated Machine Learning (ML) Pipeline for the Real-Time E-Commerce Data Engineering & AI Analytics Platform.

The pipeline automates feature engineering, multi-model candidate training, evaluation, automated model selection based on domain metrics, model versioning, local model registry management, and Airflow orchestration across:
1. **Customer Segmentation** (Functionality 14)
2. **Customer Churn Prediction** (Functionality 15)
3. **Sales Forecasting** (Functionality 16)
4. **Product Recommendation System** (Functionality 17)

---

## Pipeline Architecture & Workflow

```
START
  ↓
Load latest processed/warehouse data
  ↓
Feature Engineering  ──────►  [data/ml_pipeline/features/]
  ↓
Validate Features
  ↓
Train Models         ──────►  Candidate Models (LR, RF, HistGB, K-Means, etc.)
  ↓
Evaluate Models      ──────►  Metric Calculation (ROC-AUC, sMAPE, Silhouette, NDCG)
  ↓
Select Best Model    ──────►  Domain Primary Metric Optimization
  ↓
Save Model           ──────►  [data/models/<model_type>/<version>/]
  ↓
Save Metrics & Metadata
  ↓
Generate Reports     ──────►  [data/ml_pipeline/reports/]
  ↓
END
```

---

## Directory Structure

```
ml_pipeline/
├── __init__.py                 # Package initializer
├── config.py                   # Path configuration and environment variables
├── pipeline_utils.py           # Logger, JSON serialization, priority file resolution
├── feature_pipeline.py         # Data loading, feature extraction & Parquet exports
├── training_pipeline.py        # Candidate model training per domain
├── evaluation_pipeline.py      # Metric evaluation, scoring & best model selection
├── model_registry.py           # Local model registry (saving, loading, versioning)
├── pipeline.py                 # Core end-to-end pipeline orchestrator & run logger
├── main.py                     # CLI entrypoint
├── artifacts/
│   └── .gitkeep
├── tests/                      # Unit tests using synthetic fixtures
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_features.py
│   ├── test_training.py
│   ├── test_evaluation.py
│   ├── test_registry.py
│   └── test_pipeline.py
└── README.md                   # Complete module documentation

airflow/dags/
└── automated_ml_pipeline.py    # Airflow DAG orchestration script
```

---

## Supported Models & Selection Criteria

| Domain | Candidate Models | Primary Metric | Selection Criteria |
|---|---|---|---|
| **Customer Segmentation** | K-Means (K=3, K=4, K=5) | Silhouette Score | Maximize Silhouette Score |
| **Churn Prediction** | Logistic Regression, Random Forest, HistGradientBoosting | ROC-AUC | Maximize ROC-AUC |
| **Sales Forecasting** | Random Forest Regressor, HistGradientBoosting Regressor, Ridge | sMAPE (%) | Minimize sMAPE |
| **Recommendation System** | Item-Item Collaborative, Content-Based TF-IDF, Hybrid, Popularity | NDCG@10 | Maximize NDCG@10 |

---

## Model Versioning & Local Registry

Models are versioned chronologically using `YYYYMMDD_HHMMSS` timestamps.
Saved directory structure:

```
data/models/
├── churn/
│   └── <version>/
│       ├── model.joblib
│       ├── metadata.json
│       └── metrics.json
├── segmentation/
│   └── <version>/
├── forecasting/
│   └── <version>/
└── recommendation/
    └── <version>/
```

Metadata schema includes:
```json
{
  "model_type": "churn",
  "model_name": "random_forest",
  "version": "20261006_234500",
  "training_timestamp": "2026-10-06T23:45:00",
  "training_data_source": "data/ml_pipeline/features/churn_features.parquet",
  "feature_count": 4,
  "training_rows": 100,
  "status": "selected"
}
```

---

## Execution & Usage (Windows PowerShell)

### 1. Run Unit Tests
Run unit tests with synthetic fixtures without needing production data or Airflow:
```powershell
python -m pytest ml_pipeline/tests -v
```

### 2. Run End-to-End Pipeline via CLI
Execute complete feature engineering, training, evaluation, model selection, and registry saving:
```powershell
python -m ml_pipeline.main --run-all
```

### 3. Feature Engineering Layer Only
```powershell
python -m ml_pipeline.main --features-only
```

### 4. Target Specific Model Type (e.g. Churn Only)
```powershell
python -m ml_pipeline.main --train-only --model-type churn
python -m ml_pipeline.main --evaluate-only --model-type churn
```

---

## Airflow Orchestration

Airflow DAG: `automated_ml_pipeline` (`airflow/dags/automated_ml_pipeline.py`)

Airflow Task Dependency Chain:
```
start -> feature_engineering -> validate_features -> train_models -> evaluate_models -> select_best_models -> save_models -> generate_report -> end
```

To run Airflow via existing Docker Compose setup:
```powershell
docker-compose up -d
```
Access Airflow UI at `http://localhost:8080` and trigger `automated_ml_pipeline`.

---

## Output Files Summary

- Features: `data/ml_pipeline/features/*.parquet`
- Metrics: `data/ml_pipeline/metrics/*_metrics.json`
- Reports: `data/ml_pipeline/reports/pipeline_report.json`, `pipeline_report.csv`, `model_comparison.csv`
- Runs log: `data/ml_pipeline/pipeline_runs.json`
- Registered Models: `data/models/<domain>/<version>/model.joblib`
