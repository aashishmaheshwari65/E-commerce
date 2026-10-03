import os
import json
from datetime import datetime
from . import config
from .source_reader import load_source_data
from .dimensions import build_dim_customer, build_dim_product, build_dim_date, build_dim_payment, build_dim_order
from .fact_sales import build_fact_sales

def build_warehouse():
    users = load_source_data("users")
    products = load_source_data("products")
    orders = load_source_data("orders")
    order_items = load_source_data("order_items")
    payments = load_source_data("payments")
    
    print("Building dimensions...")
    dim_customer = build_dim_customer(users)
    dim_product = build_dim_product(products)
    dim_date = build_dim_date(orders)
    dim_payment = build_dim_payment(payments)
    dim_order = build_dim_order(orders)
    
    print("Building fact table...")
    fact_sales = build_fact_sales(order_items, orders, dim_customer, dim_product, dim_date, dim_payment, dim_order, payments)
    
    print("Saving to Parquet...")
    dim_customer.to_parquet(os.path.join(config.DIMENSIONS_DIR, "dim_customer.parquet"), index=False)
    dim_product.to_parquet(os.path.join(config.DIMENSIONS_DIR, "dim_product.parquet"), index=False)
    dim_date.to_parquet(os.path.join(config.DIMENSIONS_DIR, "dim_date.parquet"), index=False)
    dim_payment.to_parquet(os.path.join(config.DIMENSIONS_DIR, "dim_payment.parquet"), index=False)
    dim_order.to_parquet(os.path.join(config.DIMENSIONS_DIR, "dim_order.parquet"), index=False)
    
    fact_sales.to_parquet(os.path.join(config.FACTS_DIR, "fact_sales.parquet"), index=False)
    
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "tables": {
            "dim_customer": len(dim_customer),
            "dim_product": len(dim_product),
            "dim_date": len(dim_date),
            "dim_payment": len(dim_payment),
            "dim_order": len(dim_order),
            "fact_sales": len(fact_sales)
        }
    }
    
    with open(os.path.join(config.METADATA_DIR, "warehouse_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=4)
        
    return manifest
