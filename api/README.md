# Functionality 19: FastAPI REST API

## Overview
Functionality 19 provides a modular, production-style FastAPI REST API for the Real-Time E-Commerce Data Engineering & AI Analytics Platform.

The API exposes inference endpoints for:
1. **Customer Churn Prediction** (`/churn/predict`, `/churn/predict/batch`, `/churn/model`)
2. **Sales Forecasting** (`/forecast`, `/forecast/model`)
3. **Product Recommendations** (`/recommendations/{user_id}`, `/recommendations/model`)
4. **Service & Model Health Checks** (`/health`, `/health/models`)

---

## Key Architecture & Design Rules

- **Inference Only**: The API performs inference only. Model training remains fully handled by Functionality 18 / Airflow DAG workflows.
- **Model Registry Integration**: Integrates directly with Functionality 18 model registry (`data/models/<model_type>/<version>/`).
- **Lazy Loading & Memory Caching**: Models are loaded lazily on first request and cached in memory to prevent repeated disk I/O.
- **Fail-Fast Error Handling**: If a requested model artifact is unavailable, returns a clear `503 Service Unavailable` response instead of fabricating dummy output.
- **Input Validation**: Uses Pydantic schemas to validate parameters (`horizon` ∈ {7, 14, 30}, `n` ∈ [1, 100], `method` ∈ {hybrid, collaborative, content, popular}).

---

## API Endpoints Summary

| Method | Endpoint | Purpose | Request Body / Params | Response |
|---|---|---|---|---|
| **GET** | `/health` | API Health Check | None | `{"status": "ok", "service": "...", "version": "1.0.0"}` |
| **GET** | `/health/models` | Model Availability Check | None | `{"status": "ok", "models": {"churn": true, ...}}` |
| **POST** | `/churn/predict` | Single Churn Prediction | `{"customer_id": "USER001"}` | `{"success": true, "data": {"churn_probability": 0.73, "risk_category": "high"}}` |
| **POST** | `/churn/predict/batch` | Batch Churn Prediction | `{"customer_ids": ["USER001", "USER002"]}` | `{"success": true, "count": 2, "data": [...]}` |
| **GET** | `/churn/model` | Churn Model Metadata | None | `{"success": true, "data": {...}}` |
| **POST** | `/forecast` | Sales Revenue Forecast | `{"horizon": 7}` | `{"success": true, "data": {"forecast": [...]}}` |
| **GET** | `/forecast/model` | Forecast Model Metadata | None | `{"success": true, "data": {...}}` |
| **GET** | `/recommendations/{user_id}` | Top-N Recommendations | `?n=10&method=hybrid` | `{"success": true, "data": {"recommendations": [...]}}` |
| **GET** | `/recommendations/model` | Recommendation Metadata | None | `{"success": true, "data": {...}}` |

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `ML_MODEL_ROOT` | Path to trained model registry | `data/models` |
| `ML_DATA_ROOT` | Path to base data directory | `data` |
| `API_CORS_ORIGINS` | Comma-separated allowed CORS origins | `http://localhost:3000,http://localhost:5173` |

---

## Running Locally

Run the Uvicorn dev server:
```powershell
python -m uvicorn api.main:app --reload
```

Interactive API documentation:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## Testing

Run unit tests using FastAPI `TestClient`:
```powershell
python -m pytest api/tests -v
```

---

## PowerShell API Request Examples

### 1. Health Check
```powershell
Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/health" `
    -Method Get
```

### 2. Model Availability Check
```powershell
Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/health/models" `
    -Method Get
```

### 3. Single Customer Churn Prediction
```powershell
Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/churn/predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{"customer_id":"USER001"}'
```

### 4. Sales Forecast (7-day Horizon)
```powershell
Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/forecast" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{"horizon":7}'
```

### 5. Product Recommendations for User
```powershell
Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/recommendations/USER001?n=10&method=hybrid&exclude_purchased=true" `
    -Method Get
```
