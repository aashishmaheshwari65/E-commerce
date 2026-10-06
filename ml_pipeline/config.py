import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Base data directory
DATA_ROOT = Path(os.getenv("ML_DATA_ROOT", BASE_DIR / "data"))

# Pipeline specific root directories
MODEL_ROOT = Path(os.getenv("ML_MODEL_ROOT", DATA_ROOT / "models"))
PIPELINE_ROOT = Path(os.getenv("ML_PIPELINE_ROOT", DATA_ROOT / "ml_pipeline"))
FEATURE_ROOT = Path(os.getenv("ML_FEATURE_ROOT", PIPELINE_ROOT / "features"))
METRIC_ROOT = Path(os.getenv("ML_METRIC_ROOT", PIPELINE_ROOT / "metrics"))
REPORT_ROOT = Path(os.getenv("ML_REPORT_ROOT", PIPELINE_ROOT / "reports"))
LOG_ROOT = Path(os.getenv("ML_LOG_ROOT", PIPELINE_ROOT / "logs"))

# Priority data source paths
WAREHOUSE_DIR = DATA_ROOT / "warehouse"
CUSTOMER_SEGMENTATION_DIR = DATA_ROOT / "customer_segmentation"
CHURN_PREDICTION_DIR = DATA_ROOT / "churn_prediction"
SALES_FORECASTING_DIR = DATA_ROOT / "sales_forecasting"
RECOMMENDATIONS_DIR = DATA_ROOT / "recommendations"
LAKE_GOLD_DIR = DATA_ROOT / "lake" / "gold"
PROCESSED_DIR = DATA_ROOT / "processed"
RAW_DIR = DATA_ROOT / "raw"

# Model types supported
MODEL_TYPES = ["segmentation", "churn", "forecasting", "recommendation"]

# Default Random Seed
RANDOM_STATE = 42

def generate_version():
    """Generate model version timestamp in YYYYMMDD_HHMMSS format."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_directories():
    """Ensure all required pipeline directories exist."""
    dirs = [
        MODEL_ROOT,
        PIPELINE_ROOT,
        FEATURE_ROOT,
        METRIC_ROOT,
        REPORT_ROOT,
        LOG_ROOT
    ]
    for m in MODEL_TYPES:
        dirs.append(MODEL_ROOT / m)
    for d in dirs:
        os.makedirs(d, exist_ok=True)
