from pyspark.sql.functions import col, to_timestamp, to_date, lower, trim, when, lit, coalesce
from pyspark.sql.types import IntegerType, DoubleType, DateType, TimestampType

def transform_users(df):
    """
    * Cast user IDs to appropriate types.
    * Normalize city and country strings.
    * Parse registration dates.
    * Identify duplicate user IDs and invalid records.
    """
    df = df.withColumn("user_id", col("user_id").cast(IntegerType())) \
           .withColumn("city", trim(lower(col("city")))) \
           .withColumn("country", trim(lower(col("country")))) \
           .withColumn("registration_date", to_timestamp(col("registration_date")))
    
    # Identify invalid records
    df = df.withColumn("is_valid", when(col("user_id").isNotNull() & col("email").isNotNull(), True).otherwise(False))
    return df

def transform_products(df):
    """
    * Cast price, discount_percent, stock, and rating to numeric types.
    * Normalize category names.
    * Calculate discounted price.
    * Identify invalid prices, discounts, stock values, and ratings.
    """
    df = df.withColumn("product_id", col("product_id").cast(IntegerType())) \
           .withColumn("price", col("price").cast(DoubleType())) \
           .withColumn("discount_percent", col("discount_percent").cast(DoubleType())) \
           .withColumn("stock", col("stock").cast(IntegerType())) \
           .withColumn("rating", col("rating").cast(DoubleType())) \
           .withColumn("category", trim(lower(col("category"))))
           
    # Calculate discounted price
    df = df.withColumn("discounted_price", 
                       col("price") * (1 - coalesce(col("discount_percent"), lit(0.0)) / 100.0))
    
    df = df.withColumn("is_valid", 
                       when((col("price") >= 0) & 
                            (col("discount_percent") >= 0) & (col("discount_percent") <= 100) &
                            (col("stock") >= 0) & 
                            (col("rating") >= 0) & (col("rating") <= 5), True).otherwise(False))
    return df

def transform_orders(df):
    """
    * Parse order dates.
    * Cast total_amount to a numeric type.
    * Normalize order status and payment method.
    * Identify invalid or duplicate orders.
    """
    df = df.withColumn("order_id", col("order_id").cast(IntegerType())) \
           .withColumn("user_id", col("user_id").cast(IntegerType())) \
           .withColumn("total_amount", col("total_amount").cast(DoubleType())) \
           .withColumn("order_date", to_timestamp(col("order_date"))) \
           .withColumn("order_status", trim(lower(col("order_status")))) \
           .withColumn("payment_method", trim(lower(col("payment_method"))))
           
    df = df.withColumn("is_valid", when(col("total_amount") >= 0, True).otherwise(False))
    return df

def transform_order_items(df):
    """
    * Cast quantity, unit_price, and line_total.
    * Calculate a derived line total using quantity multiplied by unit price.
    * Flag discrepancies between stored and calculated line totals.
    * Do not silently overwrite the original line_total.
    """
    df = df.withColumn("order_item_id", col("order_item_id").cast(IntegerType())) \
           .withColumn("order_id", col("order_id").cast(IntegerType())) \
           .withColumn("product_id", col("product_id").cast(IntegerType())) \
           .withColumn("quantity", col("quantity").cast(IntegerType())) \
           .withColumn("unit_price", col("unit_price").cast(DoubleType())) \
           .withColumn("line_total", col("line_total").cast(DoubleType()))
           
    df = df.withColumn("calculated_line_total", col("quantity") * col("unit_price"))
    
    # Flag discrepancy (allowing a small floating point margin of error)
    df = df.withColumn("discrepancy_flag", 
                       when(abs(col("line_total") - col("calculated_line_total")) > 0.01, True).otherwise(False))
                       
    df = df.withColumn("is_valid", when(col("quantity") > 0, True).otherwise(False))
    return df

def transform_payments(df):
    """
    * Parse payment dates.
    * Cast amounts to numeric types.
    * Normalize payment status.
    * Identify invalid payment amounts.
    """
    df = df.withColumn("payment_id", col("payment_id").cast(IntegerType())) \
           .withColumn("order_id", col("order_id").cast(IntegerType())) \
           .withColumn("amount", col("amount").cast(DoubleType())) \
           .withColumn("payment_date", to_timestamp(col("payment_date"))) \
           .withColumn("payment_status", trim(lower(col("payment_status")))) \
           .withColumn("payment_method", trim(lower(col("payment_method"))))
           
    df = df.withColumn("is_valid", when(col("amount") >= 0, True).otherwise(False))
    return df

def transform_reviews(df):
    """
    * Parse review dates.
    * Cast ratings to numeric types.
    * Identify ratings outside the valid range.
    """
    df = df.withColumn("review_id", col("review_id").cast(IntegerType())) \
           .withColumn("user_id", col("user_id").cast(IntegerType())) \
           .withColumn("product_id", col("product_id").cast(IntegerType())) \
           .withColumn("rating", col("rating").cast(DoubleType())) \
           .withColumn("review_date", to_timestamp(col("review_date")))
           
    df = df.withColumn("is_valid", when((col("rating") >= 1) & (col("rating") <= 5), True).otherwise(False))
    return df

def transform_user_events(df):
    """
    * Parse event timestamps.
    * Normalize event types.
    * Identify invalid user IDs and product IDs.
    * Preserve valid events for downstream analytics.
    """
    df = df.withColumn("event_id", col("event_id").cast(IntegerType())) \
           .withColumn("user_id", col("user_id").cast(IntegerType())) \
           .withColumn("product_id", col("product_id").cast(IntegerType())) \
           .withColumn("event_timestamp", to_timestamp(col("event_timestamp"))) \
           .withColumn("event_type", trim(lower(col("event_type"))))
           
    df = df.withColumn("is_valid", when(col("user_id").isNotNull(), True).otherwise(False))
    return df
