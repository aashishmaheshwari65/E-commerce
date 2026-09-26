import os
from dotenv import load_dotenv

# pyrefly: ignore [missing-import]
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, ForeignKey, Date, DateTime
)
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "SUPABASE_URL is not configured in .env"
    )

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(200), unique=True)
    city = Column(String(100))
    country = Column(String(100))
    registration_date = Column(Date)

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(200))
    category = Column(String(100))
    price = Column(Float)
    discount_percent = Column(Integer)
    stock = Column(Integer)
    rating = Column(Float)

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    order_date = Column(Date)
    order_status = Column(String(50))
    payment_method = Column(String(50))
    total_amount = Column(Float)

class OrderItem(Base):
    __tablename__ = 'order_items'
    order_item_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))
    quantity = Column(Integer)
    unit_price = Column(Float)
    line_total = Column(Float)

class Payment(Base):
    __tablename__ = 'payments'
    payment_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    payment_date = Column(Date)
    payment_method = Column(String(50))
    payment_status = Column(String(50))
    amount = Column(Float)

class Review(Base):
    __tablename__ = 'reviews'
    review_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))
    rating = Column(Integer)
    review_title = Column(String(255))
    review_date = Column(Date)

class UserEvent(Base):
    __tablename__ = 'user_events'
    event_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    event_type = Column(String(50))
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=True)
    search_query = Column(String(255), nullable=True)
    event_timestamp = Column(DateTime)

def get_engine():

    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )

def create_tables(engine):
    Base.metadata.create_all(engine)

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
