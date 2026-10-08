"""
tests/database/test_database_operations.py

Tests CRUD and schema creation operations using isolated SQLite in-memory database.
"""

from datetime import date, datetime
import pytest
from sqlalchemy.orm import sessionmaker

# Safely import the SQLAlchemy models from ingestion.database
from ingestion.database import (
    Base,
    User,
    Product,
    Order,
    OrderItem,
    Payment,
    Review,
    UserEvent,
    create_tables,
)


@pytest.fixture
def db_session(sqlite_engine):
    """Creates all tables in the SQLite in-memory database and yields a session."""
    create_tables(sqlite_engine)
    Session = sessionmaker(bind=sqlite_engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(sqlite_engine)


@pytest.mark.unit
def test_create_tables_and_insert_user(db_session):
    user = User(
        user_id=1,
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        city="New York",
        country="USA",
        registration_date=date(2024, 1, 15),
    )
    db_session.add(user)
    db_session.commit()

    retrieved = db_session.query(User).filter_by(user_id=1).first()
    assert retrieved is not None
    assert retrieved.email == "alice@example.com"
    assert retrieved.first_name == "Alice"


@pytest.mark.unit
def test_product_insert_and_query(db_session):
    product = Product(
        product_id=10,
        product_name="Mechanical Keyboard",
        category="Electronics",
        price=120.0,
        discount_percent=10,
        stock=25,
        rating=4.7,
    )
    db_session.add(product)
    db_session.commit()

    item = db_session.query(Product).filter_by(product_id=10).first()
    assert item is not None
    assert item.price == 120.0
    assert item.stock == 25


@pytest.mark.unit
def test_order_and_items_relationship(db_session):
    user = User(user_id=2, first_name="Bob", last_name="Jones", email="bob@example.com")
    product = Product(product_id=20, product_name="Mouse", price=50.0)
    db_session.add_all([user, product])
    db_session.commit()

    order = Order(
        order_id=200,
        user_id=2,
        order_date=date(2024, 6, 1),
        order_status="delivered",
        payment_method="credit_card",
        total_amount=50.0,
    )
    db_session.add(order)
    db_session.commit()

    order_item = OrderItem(
        order_item_id=500,
        order_id=200,
        product_id=20,
        quantity=1,
        unit_price=50.0,
        line_total=50.0,
    )
    db_session.add(order_item)
    db_session.commit()

    retrieved_order = db_session.query(Order).filter_by(order_id=200).first()
    retrieved_item = db_session.query(OrderItem).filter_by(order_id=200).first()
    assert retrieved_order is not None
    assert retrieved_item is not None
    assert retrieved_item.line_total == 50.0
