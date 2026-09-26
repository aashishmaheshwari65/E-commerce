"""
Ingestion module for E-Commerce.
"""
from .database import get_engine, get_session, create_tables
from .ingest import ingest_data
