import pandas as pd
from pathlib import Path
from sqlalchemy.exc import IntegrityError
from ingestion.database import (
    get_engine, create_tables, get_session,
    User, Product, Order, OrderItem, Payment, Review, UserEvent
)

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

def ingest_data(db_path="sqlite:///data/ecommerce.db"):
    print(f"Starting ingestion from {RAW_DATA_DIR} to {db_path}")
    engine = get_engine(db_path)
    create_tables(engine)
    session = get_session(engine)

    # 1. Ingest Users
    try:
        users_df = pd.read_csv(RAW_DATA_DIR / "users.csv")
        users_df['registration_date'] = pd.to_datetime(users_df['registration_date']).dt.date
        users = [User(**row) for row in users_df.to_dict('records')]
        session.bulk_save_objects(users)
        session.commit()
        print(f"Ingested {len(users)} users.")
    except Exception as e:
        session.rollback()
        print(f"Error ingesting users: {e}")

    # 2. Ingest Products
    try:
        products_df = pd.read_csv(RAW_DATA_DIR / "products.csv")
        products = [Product(**row) for row in products_df.to_dict('records')]
        session.bulk_save_objects(products)
        session.commit()
        print(f"Ingested {len(products)} products.")
    except Exception as e:
        session.rollback()
        print(f"Error ingesting products: {e}")

    # 3. Ingest Orders
    try:
        orders_df = pd.read_csv(RAW_DATA_DIR / "orders.csv")
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date']).dt.date
        orders = [Order(**row) for row in orders_df.to_dict('records')]
        session.bulk_save_objects(orders)
        session.commit()
        print(f"Ingested {len(orders)} orders.")
    except Exception as e:
        session.rollback()
        print(f"Error ingesting orders: {e}")

    # 4. Ingest Order Items
    try:
        items_df = pd.read_csv(RAW_DATA_DIR / "order_items.csv")
        items = [OrderItem(**row) for row in items_df.to_dict('records')]
        session.bulk_save_objects(items)
        session.commit()
        print(f"Ingested {len(items)} order items.")
    except Exception as e:
        session.rollback()
        print(f"Error ingesting order items: {e}")

    # 5. Ingest Payments
    try:
        payments_df = pd.read_csv(RAW_DATA_DIR / "payments.csv")
        payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date']).dt.date
        payments = [Payment(**row) for row in payments_df.to_dict('records')]
        session.bulk_save_objects(payments)
        session.commit()
        print(f"Ingested {len(payments)} payments.")
    except Exception as e:
        session.rollback()
        print(f"Error ingesting payments: {e}")

    # 6. Ingest Reviews
    try:
        reviews_df = pd.read_csv(RAW_DATA_DIR / "reviews.csv")
        reviews_df['review_date'] = pd.to_datetime(reviews_df['review_date']).dt.date
        reviews = [Review(**row) for row in reviews_df.to_dict('records')]
        session.bulk_save_objects(reviews)
        session.commit()
        print(f"Ingested {len(reviews)} reviews.")
    except Exception as e:
        session.rollback()
        print(f"Error ingesting reviews: {e}")

    # 7. Ingest User Events
    try:
        events_df = pd.read_csv(RAW_DATA_DIR / "user_events.csv")
        # Replace NaNs with None for nullable fields
        events_df['product_id'] = events_df['product_id'].where(pd.notnull(events_df['product_id']), None)
        events_df['search_query'] = events_df['search_query'].where(pd.notnull(events_df['search_query']), None)
        events_df['event_timestamp'] = pd.to_datetime(events_df['event_timestamp'])
        
        events = [UserEvent(**row) for row in events_df.to_dict('records')]
        session.bulk_save_objects(events)
        session.commit()
        print(f"Ingested {len(events)} user events.")
    except Exception as e:
        session.rollback()
        print(f"Error ingesting user events: {e}")

    print("Data ingestion complete.")
    session.close()

if __name__ == "__main__":
    ingest_data()
