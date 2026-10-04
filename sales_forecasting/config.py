import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "sales_forecasting")
DATA_DIR = os.path.join(BASE_DIR, "data", "warehouse")

RANDOM_STATE = 42
FORECAST_HORIZON_DAYS = 30
