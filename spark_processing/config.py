import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Input paths
SILVER_LAKE_DIR = os.path.join(BASE_DIR, "data_lake", "silver")
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# Output paths
SPARK_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "spark")
PROCESSED_DIR = os.path.join(SPARK_OUTPUT_DIR, "processed")
ANALYTICS_DIR = os.path.join(SPARK_OUTPUT_DIR, "analytics")
QUALITY_DIR = os.path.join(SPARK_OUTPUT_DIR, "quality")
LOGS_DIR = os.path.join(SPARK_OUTPUT_DIR, "logs")

# Ensure output dirs exist
for d in [PROCESSED_DIR, ANALYTICS_DIR, QUALITY_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

# Spark Settings
APP_NAME = "EcommerceDataProcessing"
MASTER_URL = "local[*]"
SHUFFLE_PARTITIONS = "4"  # Sensible for local
LOG_LEVEL = "WARN"
