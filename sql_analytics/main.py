import os
import argparse
from datetime import datetime
from .runner import AnalyticsRunner
from . import config

def main():
    parser = argparse.ArgumentParser(description="SQL Analytics")
    parser.add_argument("--group", help="Query group to run", default="all")
    args = parser.parse_args()
    
    runner = AnalyticsRunner()
    
    queries = {
        "revenue": "01_revenue_analytics.sql",
        "sales": "02_sales_analytics.sql",
        "customers": "03_customer_analytics.sql",
        "products": "04_product_analytics.sql",
        "retention": "05_retention_analytics.sql",
        "payments": "06_payment_analytics.sql",
        "kpis": "07_business_kpis.sql",
        "advanced": "08_advanced_analytics.sql"
    }
    
    groups_to_run = queries.keys() if args.group == "all" else [args.group]
    
    for group in groups_to_run:
        if group not in queries:
            print(f"Group {group} not found.")
            continue
            
        sql_file = os.path.join(config.QUERIES_DIR, queries[group])
        if os.path.exists(sql_file):
            print(f"Running {group} analytics...")
            df = runner.run_query_file(sql_file)
            output_dir = os.path.join(config.ANALYTICS_OUTPUT_DIR, group)
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{group}_results.csv")
            df.to_csv(output_file, index=False)
            print(f"Results saved to {output_file}")
            print(df.head())
        else:
            print(f"Warning: SQL file {sql_file} not found.")

if __name__ == "__main__":
    main()
