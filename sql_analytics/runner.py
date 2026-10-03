import duckdb
import os
import pandas as pd
from . import config

class AnalyticsRunner:
    def __init__(self):
        self.con = duckdb.connect(database=':memory:')
        
        # Register Parquet files as views
        self.register_view('fact_sales', os.path.join(config.FACTS_DIR, 'fact_sales.parquet'))
        self.register_view('dim_customer', os.path.join(config.DIMENSIONS_DIR, 'dim_customer.parquet'))
        self.register_view('dim_product', os.path.join(config.DIMENSIONS_DIR, 'dim_product.parquet'))
        self.register_view('dim_date', os.path.join(config.DIMENSIONS_DIR, 'dim_date.parquet'))
        self.register_view('dim_payment', os.path.join(config.DIMENSIONS_DIR, 'dim_payment.parquet'))
        self.register_view('dim_order', os.path.join(config.DIMENSIONS_DIR, 'dim_order.parquet'))

    def register_view(self, name, path):
        if os.path.exists(path):
            self.con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{path}')")
        else:
            print(f"Warning: {path} not found.")

    def run_query(self, query_string):
        return self.con.execute(query_string).fetchdf()

    def run_query_file(self, file_path):
        with open(file_path, 'r') as f:
            query = f.read()
        return self.run_query(query)
