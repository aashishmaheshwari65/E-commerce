import os
from . import config

def load_dataset(spark, dataset_name):
    """
    Attempts to load a dataset from the Silver Parquet layer first.
    If it doesn't exist, falls back to the processed CSV layer.
    """
    # 1. Try Silver Parquet
    parquet_path = os.path.join(config.SILVER_LAKE_DIR, dataset_name)
    if os.path.exists(parquet_path):
        print(f"Loading {dataset_name} from Parquet: {parquet_path}")
        return spark.read.parquet(parquet_path)
    
    # 2. Try Processed CSV
    csv_filename = f"{dataset_name}_clean.csv"
    csv_path = os.path.join(config.RAW_DATA_DIR, csv_filename)
    if os.path.exists(csv_path):
        print(f"Loading {dataset_name} from CSV: {csv_path}")
        return spark.read.csv(csv_path, header=True, inferSchema=True)
    
    # 3. Error
    raise FileNotFoundError(f"Dataset {dataset_name} not found in Silver Parquet ({parquet_path}) or Processed CSV ({csv_path}).")
