import pytest
from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp
from spark_processing.aggregations import customer_analytics, monthly_sales

@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder \
        .appName("TestSparkAggregations") \
        .master("local[1]") \
        .getOrCreate()
    yield spark
    spark.stop()

def test_customer_analytics(spark):
    users_data = [(1, "John", "Doe", "john@example.com", "City", "Country", "2023-01-01")]
    users_cols = ["user_id", "first_name", "last_name", "email", "city", "country", "registration_date"]
    users_df = spark.createDataFrame(users_data, users_cols)
    
    orders_data = [
        (101, 1, "2023-01-02", "completed", "credit", 150.0, True),
        (102, 1, "2023-01-03", "cancelled", "credit", 50.0, True), # Should be excluded
        (103, 1, "2023-01-04", "completed", "credit", 200.0, True)
    ]
    orders_cols = ["order_id", "user_id", "order_date", "order_status", "payment_method", "total_amount", "is_valid"]
    orders_df = spark.createDataFrame(orders_data, orders_cols)
    
    agg_df = customer_analytics(users_df, orders_df)
    results = agg_df.collect()
    
    assert len(results) == 1
    assert results[0].total_orders == 2
    assert results[0].total_spending == 350.0
    assert results[0].average_order_value == 175.0

def test_monthly_sales(spark):
    orders_data = [
        (101, 1, "2023-01-02 10:00:00", "completed", "credit", 150.0, True),
        (102, 1, "2023-01-03 11:00:00", "completed", "credit", 200.0, True),
        (103, 1, "2023-02-04 12:00:00", "completed", "credit", 300.0, True)
    ]
    orders_cols = ["order_id", "user_id", "order_date", "order_status", "payment_method", "total_amount", "is_valid"]
    orders_df = spark.createDataFrame(orders_data, orders_cols)
    orders_df = orders_df.withColumn("order_date", to_timestamp("order_date"))
    
    agg_df = monthly_sales(orders_df)
    results = agg_df.collect()
    
    # Sort results by month
    results.sort(key=lambda x: x.month)
    
    assert len(results) == 2
    assert results[0].month == 1
    assert results[0].total_orders == 2
    assert results[0].total_revenue == 350.0
    
    assert results[1].month == 2
    assert results[1].total_orders == 1
    assert results[1].total_revenue == 300.0
