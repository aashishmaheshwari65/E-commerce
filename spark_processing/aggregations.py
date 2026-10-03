from pyspark.sql.functions import col, count, sum, avg, max, year, month, countDistinct

def customer_analytics(users_df, orders_df):
    """
    Customer Analytics
    * user_id
    * customer name (first_name + " " + last_name)
    * total orders
    * total spending
    * average order value
    * last order date
    * customer lifetime value (same as total spending here)
    """
    # Join Orders + Users
    # Inner join because we only want analytics for users who made orders, or left join to include all users.
    # We will use left join to see all users.
    valid_orders = orders_df.filter(col("is_valid") == True).filter(col("order_status") != "cancelled")
    
    user_orders = users_df.join(valid_orders, "user_id", "left")
    
    return user_orders.groupBy("user_id", "first_name", "last_name").agg(
        count("order_id").alias("total_orders"),
        sum("total_amount").alias("total_spending"),
        avg("total_amount").alias("average_order_value"),
        max("order_date").alias("last_order_date")
    ).withColumn("customer_lifetime_value", col("total_spending"))

def product_analytics(products_df, order_items_df, reviews_df, orders_df):
    """
    Product Analytics
    * product_id, product_name, category
    * units sold, total revenue, average selling price
    * number of reviews, average review rating
    """
    valid_orders = orders_df.filter(col("is_valid") == True).filter(col("order_status") != "cancelled")
    valid_items = order_items_df.join(valid_orders, "order_id", "inner")
    
    # Aggregate order items
    item_agg = valid_items.groupBy("product_id").agg(
        sum("quantity").alias("units_sold"),
        sum("calculated_line_total").alias("total_revenue")
    ).withColumn("average_selling_price", col("total_revenue") / col("units_sold"))
    
    # Aggregate reviews
    review_agg = reviews_df.filter(col("is_valid") == True).groupBy("product_id").agg(
        count("review_id").alias("number_of_reviews"),
        avg("rating").alias("average_review_rating")
    )
    
    # Join Products + Order Items (Inner/Left)
    prod_analytics = products_df.join(item_agg, "product_id", "left") \
                                .join(review_agg, "product_id", "left")
                                
    return prod_analytics.select(
        "product_id", "product_name", "category",
        "units_sold", "total_revenue", "average_selling_price",
        "number_of_reviews", "average_review_rating"
    )

def monthly_sales(orders_df):
    """
    Monthly Sales
    * year, month, total orders, total revenue, average order value
    """
    valid_orders = orders_df.filter(col("is_valid") == True).filter(col("order_status") != "cancelled")
    
    return valid_orders.withColumn("year", year("order_date")) \
                       .withColumn("month", month("order_date")) \
                       .groupBy("year", "month").agg(
                           count("order_id").alias("total_orders"),
                           sum("total_amount").alias("total_revenue"),
                           avg("total_amount").alias("average_order_value")
                       )

def category_performance(products_df, order_items_df, orders_df):
    """
    Category Performance
    * category, number of products sold, total units sold, total revenue, average selling price
    """
    valid_orders = orders_df.filter(col("is_valid") == True).filter(col("order_status") != "cancelled")
    valid_items = order_items_df.join(valid_orders, "order_id", "inner")
    
    items_with_prod = valid_items.join(products_df, "product_id", "inner")
    
    return items_with_prod.groupBy("category").agg(
        countDistinct("product_id").alias("number_of_products_sold"),
        sum("quantity").alias("total_units_sold"),
        sum("calculated_line_total").alias("total_revenue")
    ).withColumn("average_selling_price", col("total_revenue") / col("total_units_sold"))

def payment_analytics(payments_df):
    """
    Payment Analytics
    * payment method, successful payments, failed payments, total successful payment amount
    """
    # Assuming payment_status can be 'success', 'failed', etc.
    return payments_df.groupBy("payment_method").agg(
        sum(when(col("payment_status") == "success", 1).otherwise(0)).alias("successful_payments"),
        sum(when(col("payment_status") == "failed", 1).otherwise(0)).alias("failed_payments"),
        sum(when(col("payment_status") == "success", col("amount")).otherwise(0)).alias("total_successful_payment_amount")
    )
    
def event_analytics(events_df):
    """
    Event Analytics
    * event type, total event count, unique users, unique products, daily event trends
    """
    # We'll just group by event_type. For daily trends, we might need a separate table or group by date too.
    # The requirement says "Event Analytics: event type, total event count, unique users, unique products, daily event trends"
    # To keep it in one table, we might aggregate by event type and date.
    return events_df.withColumn("event_date", to_date("event_timestamp")).groupBy("event_type", "event_date").agg(
        count("event_id").alias("total_event_count"),
        countDistinct("user_id").alias("unique_users"),
        countDistinct("product_id").alias("unique_products")
    )
