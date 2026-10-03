import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAREHOUSE_DIR = os.path.join(BASE_DIR, "data", "warehouse")
DIMENSIONS_DIR = os.path.join(WAREHOUSE_DIR, "dimensions")
FACTS_DIR = os.path.join(WAREHOUSE_DIR, "facts")

ANALYTICS_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "analytics")

QUERIES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queries")

os.makedirs(ANALYTICS_OUTPUT_DIR, exist_ok=True)
