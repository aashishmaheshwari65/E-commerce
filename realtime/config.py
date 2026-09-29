"""Configuration for the real-time event generator."""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "realtime"
OUTPUT_FILE = OUTPUT_DIR / "events.jsonl"

USERS_CSV = RAW_DATA_DIR / "users.csv"
PRODUCTS_CSV = RAW_DATA_DIR / "products.csv"

# Event Types and Distributions
EVENT_TYPES = ["product_view", "search", "add_to_cart", "purchase"]
EVENT_WEIGHTS = [0.6, 0.2, 0.15, 0.05] # Product views are most frequent, purchases least

# Mock search queries for realistic data
MOCK_SEARCH_QUERIES = [
    "laptop", "smartphone", "wireless headphones", "smartwatch",
    "gaming mouse", "mechanical keyboard", "4k monitor",
    "bluetooth speaker", "tablet", "charger cable",
    "camera", "drone", "fitness tracker", "earbuds"
]
