"""Database connection and session management"""

from sqlmodel import create_engine, Session
from sqlalchemy.engine import Engine
from contextlib import contextmanager
from typing import Generator

from .config import settings


def create_db_engine() -> Engine:
    """
    Factory function to create database engine.
    
    This factory pattern improves testability by allowing
    easy engine replacement in tests.
    
    Returns:
        Engine: Configured SQLAlchemy engine
    """
    connect_args = {"check_same_thread": False} if settings.is_sqlite else {}
    
    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo,
        connect_args=connect_args,
        pool_pre_ping=True  # Enable connection health checks
    )
    
    return engine


# Global engine instance (created once at startup)
engine = create_db_engine()


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage:
        with get_session() as session:
            user = session.get(User, user_id)
    
    Yields:
        Session: Database session
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


def get_db_session():
    """
    Dependency injection for FastAPI routes.
    
    Usage:
        @app.get("/users")
        def get_users(session: Session = Depends(get_db_session)):
            ...
    
    Yields:
        Session: Database session
    """
    with Session(engine) as session:
        yield session
