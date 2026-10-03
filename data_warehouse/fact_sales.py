import pandas as pd
from datetime import datetime
from .dimensions import generate_key

def build_fact_sales(order_items_df, orders_df, dim_customer, dim_product, dim_date, dim_payment, dim_order, payments_df):
    # Base is order_items_df
    fact = order_items_df.copy()
    
    # Merge orders to get order details
    fact = fact.merge(orders_df[['order_id', 'user_id', 'order_date', 'order_status']], on='order_id', how='inner')
    
    # Generate Surrogate keys based on business keys
    fact['sales_key'] = fact['order_item_id'].apply(generate_key)
    fact['order_key'] = fact['order_id'].apply(generate_key)
    fact['customer_key'] = fact['user_id'].apply(generate_key)
    fact['product_key'] = fact['product_id'].apply(generate_key)
    
    fact['date_key'] = pd.to_datetime(fact['order_date']).dt.strftime('%Y%m%d').astype(int)
    
    # Get payments for payment_key
    order_payment = payments_df[['order_id', 'payment_method', 'payment_status']].drop_duplicates('order_id')
    order_payment['payment_method'] = order_payment['payment_method'].str.lower().str.strip()
    order_payment['payment_status'] = order_payment['payment_status'].str.lower().str.strip()
    order_payment['payment_key'] = order_payment.apply(lambda row: generate_key(f"{row['payment_method']}_{row['payment_status']}"), axis=1)
    
    fact = fact.merge(order_payment[['order_id', 'payment_key']], on='order_id', how='left')
    fact['payment_key'] = fact['payment_key'].fillna(-1).astype(int) # -1 for unknown
    
    fact['gross_sales'] = fact['quantity'] * fact['unit_price']
    
    # Merge product to get discount
    fact = fact.merge(dim_product[['product_key', 'discount_percent']], on='product_key', how='left')
    fact['discount_amount'] = fact['gross_sales'] * (fact['discount_percent'].fillna(0) / 100.0)
    fact['net_sales'] = fact['gross_sales'] - fact['discount_amount']
    
    fact['warehouse_load_timestamp'] = datetime.now()
    
    columns = [
        'sales_key', 'order_item_id', 'order_id', 'customer_key', 'product_key', 
        'date_key', 'payment_key', 'order_key', 'quantity', 'unit_price', 
        'gross_sales', 'discount_amount', 'net_sales', 'order_status', 'warehouse_load_timestamp'
    ]
    
    return fact[columns]
