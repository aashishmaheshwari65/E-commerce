import os
import json
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from ml_pipeline import config

def get_logger(name="ml_pipeline"):
    """Configure and return a standard logger."""
    config.ensure_directories()
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")

        # Stream handler
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        # File handler
        log_file = config.LOG_ROOT / "pipeline.log"
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

def serialize_metrics(val):
    """Recursively convert numpy/pandas numeric dtypes to standard python types for JSON serialization."""
    if isinstance(val, dict):
        return {k: serialize_metrics(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [serialize_metrics(v) for v in val]
    elif isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    elif isinstance(val, (np.floating, np.float64, np.float32)):
        return float(val)
    elif isinstance(val, (bool, np.bool_)):
        return bool(val)
    else:
        return str(val) if not isinstance(val, (int, float, str, type(None))) else val

def save_json(filepath, data):
    """Save dictionary/list to formatted JSON file."""
    path = Path(filepath)
    os.makedirs(path.parent, exist_ok=True)
    serialized = serialize_metrics(data)
    with open(path, "w") as f:
        json.dump(serialized, f, indent=2)

def load_json(filepath, default=None):
    """Load JSON file safely."""
    path = Path(filepath)
    if not path.exists():
        return default if default is not None else {}
    with open(path, "r") as f:
        return json.load(f)

def find_priority_file(filenames, priority_dirs=None):
    """
    Find existing file path from prioritized list of directories.
    """
    if priority_dirs is None:
        priority_dirs = [
            config.WAREHOUSE_DIR / "facts",
            config.WAREHOUSE_DIR / "dimensions",
            config.CUSTOMER_SEGMENTATION_DIR / "features",
            config.CHURN_PREDICTION_DIR / "features",
            config.SALES_FORECASTING_DIR / "aggregated",
            config.RECOMMENDATIONS_DIR / "interactions",
            config.LAKE_GOLD_DIR,
            config.PROCESSED_DIR,
            config.RAW_DIR
        ]

    for fname in filenames:
        for pdir in priority_dirs:
            candidate = Path(pdir) / fname
            if candidate.exists():
                return candidate
    return None
