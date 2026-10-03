import pandas as pd
import os
from . import config

def load_source_data(dataset_name):
    """Loads cleaned CSV from processed data."""
    path = os.path.join(config.RAW_DATA_DIR, f"{dataset_name}_clean.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    raise FileNotFoundError(f"Dataset {dataset_name} not found at {path}")
