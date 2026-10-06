import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Input paths
WAREHOUSE_FACTS_PATH = DATA_DIR / "warehouse" / "facts" / "fact_sales.parquet"
WAREHOUSE_PRODUCT_DIM_PATH = DATA_DIR / "warehouse" / "dimensions" / "dim_product.parquet"
WAREHOUSE_CUSTOMER_DIM_PATH = DATA_DIR / "warehouse" / "dimensions" / "dim_customer.parquet"

PROCESSED_USERS_PATH = DATA_DIR / "processed" / "users_clean.csv"
PROCESSED_PRODUCTS_PATH = DATA_DIR / "processed" / "products_clean.csv"
PROCESSED_ORDERS_PATH = DATA_DIR / "processed" / "orders_clean.csv"
PROCESSED_ORDER_ITEMS_PATH = DATA_DIR / "processed" / "order_items_clean.csv"
PROCESSED_REVIEWS_PATH = DATA_DIR / "processed" / "reviews_clean.csv"
PROCESSED_USER_EVENTS_PATH = DATA_DIR / "processed" / "user_events_clean.csv"

# Output directories
RECOMMENDATION_DATA_DIR = DATA_DIR / "recommendations"
INTERACTIONS_DIR = RECOMMENDATION_DATA_DIR / "interactions"
MODELS_DIR = RECOMMENDATION_DATA_DIR / "models"
RECOMMENDATIONS_OUTPUT_DIR = RECOMMENDATION_DATA_DIR / "recommendations"
EVALUATION_DIR = RECOMMENDATION_DATA_DIR / "evaluation"
VISUALIZATIONS_DIR = RECOMMENDATION_DATA_DIR / "visualizations"
REPORTS_DIR = RECOMMENDATION_DATA_DIR / "reports"

# Default interaction weights
DEFAULT_INTERACTION_WEIGHTS = {
    "product_view": 1.0,
    "search": 1.0,
    "add_to_cart": 3.0,
    "purchase": 5.0,
    "review": 4.0,
}

# Hybrid model default weights
DEFAULT_HYBRID_WEIGHTS = {
    "collaborative_weight": 0.6,
    "content_weight": 0.4,
}

# Top N default
DEFAULT_TOP_N = 10

def ensure_directories():
    """Ensure all required output directories exist."""
    dirs = [
        INTERACTIONS_DIR,
        MODELS_DIR,
        RECOMMENDATIONS_OUTPUT_DIR,
        EVALUATION_DIR,
        VISUALIZATIONS_DIR,
        REPORTS_DIR,
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
