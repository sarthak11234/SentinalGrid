"""
SQLite database setup using SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from app.config import get_settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def _get_engine():
    settings = get_settings()
    url = settings.database_url

    # Ensure the data/ directory exists for SQLite
    if url.startswith("sqlite"):
        db_path = url.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        return create_engine(url, connect_args={"check_same_thread": False})

    return create_engine(url)


engine = _get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all tables. If schema has changed, drop and recreate (prototype only)."""
    from sqlalchemy import inspect

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # Check if schema is outdated by comparing columns
    needs_recreate = False
    for table_name, table in Base.metadata.tables.items():
        if table_name in existing_tables:
            existing_cols = {c["name"] for c in inspector.get_columns(table_name)}
            model_cols = {c.name for c in table.columns}
            if not model_cols.issubset(existing_cols):
                needs_recreate = True
                print(f"[DB] Schema change detected in '{table_name}': missing {model_cols - existing_cols}")
                break

    if needs_recreate:
        print("[DB] Dropping all tables and recreating...")
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency — yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
