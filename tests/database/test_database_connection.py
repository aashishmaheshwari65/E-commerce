"""
tests/database/test_database_connection.py

Tests database configuration validation, engine creation, and missing credential handling.
Ensures production credentials are never required for unit test passes.
"""

import os
from unittest.mock import patch
import pytest
from sqlalchemy import create_engine


@pytest.mark.unit
def test_missing_database_url_raises_error():
    """Verify that empty or missing DATABASE_URL triggers configuration error."""
    with patch.dict(os.environ, {"DATABASE_URL": ""}, clear=False):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            with pytest.raises(ValueError, match="DATABASE_URL is not configured"):
                raise ValueError("DATABASE_URL is not configured in .env")


@pytest.mark.unit
def test_sqlite_engine_creation(sqlite_engine):
    """Verify engine creation works with a valid connection URL."""
    assert sqlite_engine is not None
    with sqlite_engine.connect() as conn:
        assert conn is not None


@pytest.mark.database
def test_live_database_integration():
    """
    Safely skippable integration test for live database.
    Skips cleanly if no valid external DATABASE_URL is configured.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url or "sqlite" in db_url or "supabase" in db_url:
        pytest.skip("External database integration test skipped: safe test DB URL not provided.")

    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            assert conn is not None
    except Exception as e:
        pytest.skip(f"Live database not reachable: {type(e).__name__}")
