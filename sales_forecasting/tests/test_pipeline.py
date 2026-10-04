import pytest
import pandas as pd
import os
import json
from unittest.mock import patch
from sales_forecasting.main import run_pipeline
from sales_forecasting import config

@pytest.fixture
def sample_fact_sales():
    return pd.DataFrame({
        'order_date': pd.date_range(start='2023-01-01', periods=20, freq='D'),
        'net_sales': [100.0] * 20,
        'order_id': range(20),
        'quantity': [1] * 20,
        'order_status': ['completed'] * 20
    })

def test_full_pipeline(sample_fact_sales, tmp_path):
    # Reroute output dir to tmp_path
    original_output_dir = config.OUTPUT_DIR
    config.OUTPUT_DIR = str(tmp_path)
    
    try:
        with patch('sales_forecasting.main.pd.read_parquet') as mock_read_parquet:
            mock_read_parquet.return_value = sample_fact_sales
            run_pipeline()
        
        # Verify outputs were created
        assert os.path.exists(os.path.join(config.OUTPUT_DIR, "features", "sales_features.parquet"))
        assert os.path.exists(os.path.join(config.OUTPUT_DIR, "evaluation", "evaluation_metrics.json"))
        assert os.path.exists(os.path.join(config.OUTPUT_DIR, "reports", "sales_forecast_report.json"))
        
        # Load and verify report
        with open(os.path.join(config.OUTPUT_DIR, "reports", "sales_forecast_report.json")) as f:
            report = json.load(f)
        
        assert report['historical_periods'] == 20
        assert report['forecast_horizon'] == config.FORECAST_HORIZON_DAYS
        
    finally:
        config.OUTPUT_DIR = original_output_dir
