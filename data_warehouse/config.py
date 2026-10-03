import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Input paths
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# Output paths
WAREHOUSE_DIR = os.path.join(BASE_DIR, "data", "warehouse")
DIMENSIONS_DIR = os.path.join(WAREHOUSE_DIR, "dimensions")
FACTS_DIR = os.path.join(WAREHOUSE_DIR, "facts")
QUALITY_DIR = os.path.join(WAREHOUSE_DIR, "quality")
METADATA_DIR = os.path.join(WAREHOUSE_DIR, "metadata")

for d in [DIMENSIONS_DIR, FACTS_DIR, QUALITY_DIR, METADATA_DIR]:
    os.makedirs(d, exist_ok=True)
