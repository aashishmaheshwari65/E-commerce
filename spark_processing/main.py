import argparse
import time
import os
from . import config
from .spark_session import create_spark_session
from .reader import load_dataset
from .transformations import (transform_users, transform_products, transform_orders, 
                              transform_order_items, transform_payments, transform_reviews, transform_user_events)
from .aggregations import (customer_analytics, product_analytics, monthly_sales, 
                           category_performance, payment_analytics, event_analytics)
from .writer import write_parquet, generate_quality_report

def main():
    parser = argparse.ArgumentParser(description="PySpark Distributed Data Processing")
    parser.add_argument("--log-level", default="WARN", help="Spark log level")
    args = parser.parse_args()
    
    config.LOG_LEVEL = args.log_level
    
    start_time = time.time()
    
    print("Initializing Spark session...")
    spark = create_spark_session()
    
    try:
        # Load datasets
        print("Loading input datasets...")
        users_raw = load_dataset(spark, "users")
        products_raw = load_dataset(spark, "products")
        orders_raw = load_dataset(spark, "orders")
        order_items_raw = load_dataset(spark, "order_items")
        payments_raw = load_dataset(spark, "payments")
        reviews_raw = load_dataset(spark, "reviews")
        user_events_raw = load_dataset(spark, "user_events")
        
        # Transformations
        print("Applying transformations...")
        users_df = transform_users(users_raw).cache()
        products_df = transform_products(products_raw).cache()
        orders_df = transform_orders(orders_raw).cache()
        order_items_df = transform_order_items(order_items_raw).cache()
        payments_df = transform_payments(payments_raw).cache()
        reviews_df = transform_reviews(reviews_raw).cache()
        user_events_df = transform_user_events(user_events_raw).cache()
        
        # Generate quality report
        print("Generating data quality report...")
        dataframes_dict = {
            "users": users_df,
            "products": products_df,
            "orders": orders_df,
            "order_items": order_items_df,
            "payments": payments_df,
            "reviews": reviews_df,
            "user_events": user_events_df
        }
        generate_quality_report(dataframes_dict)
        
        # Aggregations
        print("Performing aggregations...")
        cust_analytics_df = customer_analytics(users_df, orders_df)
        prod_analytics_df = product_analytics(products_df, order_items_df, reviews_df, orders_df)
        monthly_sales_df = monthly_sales(orders_df)
        cat_performance_df = category_performance(products_df, order_items_df, orders_df)
        pay_analytics_df = payment_analytics(payments_df)
        evt_analytics_df = event_analytics(user_events_df)
        
        # Writing processed data
        print("Writing outputs...")
        write_parquet(users_df, os.path.join(config.PROCESSED_DIR, "users"))
        write_parquet(products_df, os.path.join(config.PROCESSED_DIR, "products"))
        write_parquet(orders_df, os.path.join(config.PROCESSED_DIR, "orders"))
        write_parquet(order_items_df, os.path.join(config.PROCESSED_DIR, "order_items"))
        write_parquet(payments_df, os.path.join(config.PROCESSED_DIR, "payments"))
        write_parquet(reviews_df, os.path.join(config.PROCESSED_DIR, "reviews"))
        write_parquet(user_events_df, os.path.join(config.PROCESSED_DIR, "user_events"))
        
        # Writing analytics data
        write_parquet(cust_analytics_df, os.path.join(config.ANALYTICS_DIR, "customer_analytics"))
        write_parquet(prod_analytics_df, os.path.join(config.ANALYTICS_DIR, "product_analytics"))
        write_parquet(monthly_sales_df, os.path.join(config.ANALYTICS_DIR, "monthly_sales"), partition_by=["year", "month"])
        write_parquet(cat_performance_df, os.path.join(config.ANALYTICS_DIR, "category_performance"))
        write_parquet(pay_analytics_df, os.path.join(config.ANALYTICS_DIR, "payment_analytics"))
        write_parquet(evt_analytics_df, os.path.join(config.ANALYTICS_DIR, "event_analytics"))
        
        end_time = time.time()
        print(f"Pipeline completed successfully in {end_time - start_time:.2f} seconds.")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
    finally:
        print("Stopping Spark session...")
        spark.stop()

if __name__ == "__main__":
    main()
