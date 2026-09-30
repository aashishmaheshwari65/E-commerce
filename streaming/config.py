import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
REALTIME_DATA_DIR = DATA_DIR / "realtime"
OUTPUT_DIR = REALTIME_DATA_DIR / "metrics"

DEFAULT_EVENTS_FILE = REALTIME_DATA_DIR / "events.jsonl"
CHECKPOINT_FILE = OUTPUT_DIR / "checkpoint.json"
LIVE_METRICS_FILE = OUTPUT_DIR / "live_metrics.json"
TRENDS_FILE = OUTPUT_DIR / "trends.csv"
TOP_PRODUCTS_FILE = OUTPUT_DIR / "top_products.csv"

PRODUCTS_CSV = RAW_DATA_DIR / "products.csv"
USERS_CSV = RAW_DATA_DIR / "users.csv"

EVENT_TYPES = {"product_view", "search", "add_to_cart", "purchase"}
