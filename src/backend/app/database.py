"""
Alfred - Enterprise AI Credit Governance Platform
Persistence Layer & Session Management

[ARCHITECTURAL ROLE]
This module manages the lifecycle of database connections. It uses SQLModel/SQLAlchemy
to provide a thread-safe connection pool and session handling for both synchronous
background tasks and asynchronous FastAPI request cycles.

# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: This module centralizes all DB connection logic, providing a singleton engine and safe session management for both FastAPI and background jobs.
# Why: Centralizing DB logic ensures reliability, testability, and prevents connection leaks.
# Root Cause: Without a single engine and robust session management, concurrency bugs and resource leaks are likely.
# Context: All DB access should use these helpers. Future: consider async engine for full async support.
# Model Suitability: For SQLModel/SQLAlchemy patterns, GPT-4.1 is sufficient; for advanced async/ORM, a more advanced model may be preferred.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from .config import settings


def create_db_engine() -> Engine:
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Factory for SQLAlchemy engine, configures SQLite for dev and pool tuning for prod.
    # Why: Ensures correct DB driver and pool settings for each environment.
    # Root Cause: SQLite and Postgres/MySQL require different connection/pooling strategies.
    # Context: Called once at startup; engine is reused everywhere.
    """
    SQLAlchemy Engine Configuration Factory.

    Creates a high-performance engine based on the environment settings.
    In development/test (SQLite), it disables 'check_same_thread' to allow
    multi-threaded access patterns typical of FastAPI.

    In production (Postgres/MySQL), it uses a robust connection pool.

    Returns:
        Engine: A configured SQLAlchemy/SQLModel engine instance.
    """
    # SQLite-specific multi-threading configuration
    connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

    # Engine parameters
    engine_kwargs = {
        "echo": settings.database_echo,
        "connect_args": connect_args,
        "pool_pre_ping": True,
    }

    # Performance tuning: Only apply pool limits to persistent databases (PostgreSQL/MySQL).
    # SQLite uses dedicated pooling strategies that don't support these parameters.
    if not settings.is_sqlite:
        engine_kwargs["pool_size"] = settings.database_pool_size
        engine_kwargs["max_overflow"] = settings.database_max_overflow

    engine = create_engine(settings.database_url, **engine_kwargs)

    return engine


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Singleton global engine, created once at startup for all DB access.
# Why: Prevents multiple engines and connection pool exhaustion.
# Root Cause: Multiple engines can cause subtle bugs and resource leaks.
# Context: All sessions use this engine instance.
engine = create_db_engine()


@contextmanager
def get_session() -> Generator[Session, None, None]:
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Context-managed session for scripts and background jobs, ensures commit/rollback/close.
    # Why: Prevents uncommitted transactions and session leaks in non-FastAPI code.
    # Root Cause: Manual session management is error-prone; context manager guarantees cleanup.
    # Context: Use in CLI tools, migrations, or jobs outside FastAPI request cycle.
    """
    Context-managed Synchronous Session.

    Designed for use in standalone scripts, background workers, or CLI tools
    where FastAPI dependency injection is not available.

    Guarantees:
    1. COMMIT if no exceptions occur.
    2. ROLLBACK if an error is raised.
    3. CLOSE regardless of the outcome.

    Yields:
        Session: An active SQLModel session.
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_session() -> Generator[Session, None, None]:
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: FastAPI dependency for per-request DB sessions, using session-per-request pattern.
    # Why: Ensures each HTTP request gets a fresh, isolated session.
    # Root Cause: Sharing sessions across requests can cause data leaks and concurrency bugs.
    # Context: Use as Depends(get_db_session) in route handlers.
    """
    FastAPI Dependency: Database Session Provider.

    Usage:
        @app.get("/users")
        def list_users(session: Session = Depends(get_db_session)):
            ...

    This follows the 'Session-per-Request' pattern. Each HTTP request gets its
    own isolated database session which is automatically closed after the
    response is sent.

    Yields:
        Session: A request-scoped database session.
    """
    with Session(engine) as session:
        yield session


# Base model for SQLAlchemy/SQLModel ORM
class Base(SQLModel):
    pass
