import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "churn_prediction")

# Data source
DATA_DIR = os.path.join(BASE_DIR, "data", "warehouse")

OBSERVATION_WINDOW_DAYS = 180
CHURN_HORIZON_DAYS = 90
RANDOM_STATE = 42

LOW_RISK_THRESHOLD = 0.30
HIGH_RISK_THRESHOLD = 0.60
