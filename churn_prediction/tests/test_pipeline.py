import pytest
import pandas as pd
import os
import json
from unittest.mock import patch
from churn_prediction.main import run_pipeline
from churn_prediction import config

@pytest.fixture
def sample_fact_sales():
    return pd.DataFrame({
        'customer_key': [1, 1, 2, 3, 3, 3, 4, 5, 5, 6],
        'order_id': [101, 102, 201, 301, 302, 303, 401, 501, 502, 601],
        'net_sales': [50.0, 150.0, 200.0, 10.0, 20.0, 30.0, 300.0, 15.0, 15.0, 400.0],
        'order_status': ['completed', 'completed', 'completed', 'completed', 'completed', 'cancelled', 'completed', 'completed', 'completed', 'completed']
    })

def test_full_pipeline(sample_fact_sales, tmp_path):
    # Reroute output dir to tmp_path to not overwrite actual runs during testing
    original_output_dir = config.OUTPUT_DIR
    config.OUTPUT_DIR = str(tmp_path)
    
    try:
        with patch('churn_prediction.main.pd.read_parquet') as mock_read_parquet:
            mock_read_parquet.return_value = sample_fact_sales
            run_pipeline()
        
        # Verify outputs were created
        assert os.path.exists(os.path.join(config.OUTPUT_DIR, "features", "customer_features.parquet"))
        assert os.path.exists(os.path.join(config.OUTPUT_DIR, "evaluation", "evaluation_metrics.json"))
        assert os.path.exists(os.path.join(config.OUTPUT_DIR, "reports", "churn_summary.json"))
        
        # Load and verify features
        features = pd.read_parquet(os.path.join(config.OUTPUT_DIR, "features", "customer_features.parquet"))
        assert len(features) == 6 # 6 unique customers with non-cancelled orders
        assert 'churn_probability' in features.columns
        assert 'risk_category' in features.columns
        
        # Check specific calculated features for customer 1
        c1 = features[features['customer_key'] == 1].iloc[0]
        assert c1['total_orders'] == 2
        assert c1['total_spend'] == 200.0
        
        # Load and verify report
        with open(os.path.join(config.OUTPUT_DIR, "reports", "churn_summary.json")) as f:
            report = json.load(f)
        
        assert report['total_eligible_customers'] == 6
        
    finally:
        config.OUTPUT_DIR = original_output_dir
