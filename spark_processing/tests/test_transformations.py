import pytest
from pyspark.sql import SparkSession
from spark_processing.transformations import transform_products, transform_order_items

@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder \
        .appName("TestSparkProcessing") \
        .master("local[1]") \
        .getOrCreate()
    yield spark
    spark.stop()

def test_transform_products(spark):
    data = [
        (1, "Prod A", "Cat A", 100.0, 10.0, 50, 4.5),
        (2, "Prod B", "Cat B", -10.0, 0.0, 10, 5.0) # Invalid price
    ]
    columns = ["product_id", "product_name", "category", "price", "discount_percent", "stock", "rating"]
    df = spark.createDataFrame(data, columns)
    
    transformed_df = transform_products(df)
    results = transformed_df.collect()
    
    # Check discounted price calculation
    assert results[0].discounted_price == 90.0
    
    # Check valid flag
    assert results[0].is_valid == True
    assert results[1].is_valid == False

def test_transform_order_items(spark):
    data = [
        (1, 101, 1001, 2, 50.0, 100.0), # Valid
        (2, 102, 1002, 2, 50.0, 90.0)   # Discrepancy
    ]
    columns = ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "line_total"]
    df = spark.createDataFrame(data, columns)
    
    transformed_df = transform_order_items(df)
    results = transformed_df.collect()
    
    assert results[0].calculated_line_total == 100.0
    assert results[0].discrepancy_flag == False
    
    assert results[1].calculated_line_total == 100.0
    assert results[1].discrepancy_flag == True
