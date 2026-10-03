import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from . import config

def run_pipeline():
    print("Initializing Segmentation Pipeline...")
    
    for d in ["features", "results", "models", "visualizations", "metadata"]:
        os.makedirs(os.path.join(config.OUTPUT_DIR, d), exist_ok=True)
    
    print("Loading data...")
    # Simulate loading from warehouse or CSV fallback
    try:
        users = pd.read_parquet(os.path.join(config.DATA_DIR, "dimensions", "dim_customer.parquet"))
        fact_sales = pd.read_parquet(os.path.join(config.DATA_DIR, "facts", "fact_sales.parquet"))
        orders = pd.read_parquet(os.path.join(config.DATA_DIR, "dimensions", "dim_order.parquet"))
    except Exception as e:
        print(f"Warning: Failed to load from warehouse. {e}")
        return
        
    print("Engineering features (RFM)...")
    valid_sales = fact_sales[fact_sales['order_status'] != 'cancelled']
    
    # Fake a reference date
    ref_date = datetime.now()
    
    # Calculate RFM
    # In reality, we'd calculate recency_days using date_key or order_date from orders
    # Here is a mock implementation for demonstration
    customer_features = valid_sales.groupby('customer_key').agg(
        frequency=('order_id', 'nunique'),
        monetary_value=('net_sales', 'sum')
    ).reset_index()
    
    customer_features['recency_days'] = np.random.randint(1, 100, size=len(customer_features)) # Mock recency
    
    print("Preprocessing...")
    features = customer_features[['recency_days', 'frequency', 'monetary_value']]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    print(f"Training K-Means (K=4)...")
    kmeans = KMeans(n_clusters=4, random_state=config.RANDOM_STATE, n_init=10)
    customer_features['cluster_id'] = kmeans.fit_predict(scaled_features)
    
    print("Profiling Clusters...")
    profiles = customer_features.groupby('cluster_id').agg({
        'recency_days': 'mean',
        'frequency': 'mean',
        'monetary_value': 'mean',
        'customer_key': 'count'
    }).rename(columns={'customer_key': 'customer_count'})
    print(profiles)
    
    print("Exporting results...")
    customer_features.to_parquet(os.path.join(config.OUTPUT_DIR, "results", "customer_segments.parquet"), index=False)
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "n_customers": len(customer_features),
        "n_clusters": 4
    }
    with open(os.path.join(config.OUTPUT_DIR, "metadata", "model_metadata.json"), "w") as f:
        json.dump(summary, f)
        
    print("Pipeline finished successfully.")

if __name__ == "__main__":
    run_pipeline()
