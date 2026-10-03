import pandas as pd
import hashlib

def generate_key(value):
    if pd.isna(value):
        return -1
    return int(hashlib.md5(str(value).encode('utf-8')).hexdigest(), 16) % (10**10)

def build_dim_customer(users_df):
    dim = users_df.copy()
    dim['customer_key'] = dim['user_id'].apply(generate_key)
    dim['full_name'] = dim['first_name'] + ' ' + dim['last_name']
    return dim[['customer_key', 'user_id', 'first_name', 'last_name', 'full_name', 'email', 'city', 'country', 'registration_date']].drop_duplicates()

def build_dim_product(products_df):
    dim = products_df.copy()
    dim['product_key'] = dim['product_id'].apply(generate_key)
    dim['discounted_price'] = dim['price'] * (1 - dim['discount_percent'].fillna(0) / 100.0)
    dim = dim.rename(columns={'price': 'original_price'})
    return dim[['product_key', 'product_id', 'product_name', 'category', 'original_price', 'discount_percent', 'discounted_price', 'stock', 'rating']].drop_duplicates()

def build_dim_date(orders_df):
    dates = pd.to_datetime(orders_df['order_date']).dt.date.unique()
    dim = pd.DataFrame({'full_date': pd.to_datetime(dates)})
    dim['date_key'] = dim['full_date'].dt.strftime('%Y%m%d').astype(int)
    dim['day'] = dim['full_date'].dt.day
    dim['day_of_week'] = dim['full_date'].dt.dayofweek
    dim['day_name'] = dim['full_date'].dt.day_name()
    dim['week_of_year'] = dim['full_date'].dt.isocalendar().week
    dim['month'] = dim['full_date'].dt.month
    dim['month_name'] = dim['full_date'].dt.month_name()
    dim['quarter'] = dim['full_date'].dt.quarter
    dim['year'] = dim['full_date'].dt.year
    dim['is_weekend'] = dim['day_of_week'].isin([5, 6])
    return dim

def build_dim_payment(payments_df):
    dim = payments_df[['payment_method', 'payment_status']].drop_duplicates().copy()
    dim['payment_method'] = dim['payment_method'].str.lower().str.strip()
    dim['payment_status'] = dim['payment_status'].str.lower().str.strip()
    dim = dim.drop_duplicates()
    dim['payment_key'] = dim.apply(lambda row: generate_key(f"{row['payment_method']}_{row['payment_status']}"), axis=1)
    return dim

def build_dim_order(orders_df):
    dim = orders_df.copy()
    dim['order_key'] = dim['order_id'].apply(generate_key)
    return dim[['order_key', 'order_id', 'order_status', 'payment_method']].drop_duplicates()
