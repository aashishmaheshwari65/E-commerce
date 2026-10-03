import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "customer_segmentation")

# Data source
DATA_DIR = os.path.join(BASE_DIR, "data", "warehouse")

RANDOM_STATE = 42
MIN_CLUSTERS = 2
MAX_CLUSTERS = 8
