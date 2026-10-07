import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = Path(os.getenv("ML_DATA_ROOT", PROJECT_ROOT / "data"))
MODEL_ROOT = Path(os.getenv("ML_MODEL_ROOT", DATA_ROOT / "models"))
FEATURE_ROOT = Path(os.getenv("ML_FEATURE_ROOT", DATA_ROOT / "ml_pipeline" / "features"))

cors_env = os.getenv("API_CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",") if origin.strip()]

API_TITLE = "E-Commerce ML API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "FastAPI REST API exposing churn prediction, sales forecasting, and product recommendations."
