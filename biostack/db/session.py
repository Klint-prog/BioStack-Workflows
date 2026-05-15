"""Database engine and session helpers."""

from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_DATABASE_URL = "sqlite:///./biostack.db"


def get_database_url() -> str:
    """Return the configured database URL.

    The CLI remains filesystem-first and does not require this setting. The Docker
    platform API uses PostgreSQL through BIOSTACK_DATABASE_URL.
    """
    return os.getenv("BIOSTACK_DATABASE_URL", DEFAULT_DATABASE_URL)


def get_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine for the configured database."""
    url = database_url or get_database_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, future=True, pool_pre_ping=True, connect_args=connect_args)


def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    """Return a configured session factory."""
    return sessionmaker(bind=get_engine(database_url), autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency yielding one database session."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def session_scope(database_url: str | None = None) -> Generator[Session, None, None]:
    """Provide a transactional scope for scripts and tests."""
    factory = get_session_factory(database_url)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
