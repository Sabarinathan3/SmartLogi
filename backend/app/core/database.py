"""
core/database.py – SQLAlchemy PostgreSQL engine & session factory.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Read from environment variable – set in backend/.env
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/smartlogi",  # local default
)

# PostgreSQL does NOT need check_same_thread (that's SQLite-only)
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ── Create all tables on startup ───────────────────────────────────────────────
def init_db() -> None:
    """Create all tables defined in models if they don't already exist."""
    Base.metadata.create_all(bind=engine)


# ── Dependency ────────────────────────────────────────────────────────────────
def get_db():
    """Yield a database session and close it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
