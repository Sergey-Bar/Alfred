"""
Alfred - Enterprise AI Credit Governance Platform
Persistence Layer & Session Management

[ARCHITECTURAL ROLE]
This module manages the lifecycle of database connections. It uses SQLModel/SQLAlchemy
to provide a thread-safe connection pool and session handling for both synchronous
background tasks and asynchronous FastAPI request cycles.

[DESIGN PATTERNS]
1. Connection Pooling: Efficiently reuses TCP connections to the database.
2. Context Management: Ensures sessions are reliably committed or rolled back.
3. Dependency Injection: Provides standard sessions to FastAPI route handlers.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from .config import settings


def create_db_engine() -> Engine:
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
        "pool_pre_ping": True
    }
    
    # Performance tuning: Only apply pool limits to persistent databases (PostgreSQL/MySQL).
    # SQLite uses dedicated pooling strategies that don't support these parameters.
    if not settings.is_sqlite:
        engine_kwargs["pool_size"] = settings.database_pool_size
        engine_kwargs["max_overflow"] = settings.database_max_overflow

    engine = create_engine(
        settings.database_url,
        **engine_kwargs
    )

    return engine


# --- Global Singleton Engine ---
# Initialized once at application startup.
engine = create_db_engine()


@contextmanager
def get_session() -> Generator[Session, None, None]:
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
