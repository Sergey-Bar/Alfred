"""
Alfred - Enterprise AI Credit Governance Platform
Persistence Layer & Session Management

[ARCHITECTURAL ROLE]
This module manages the lifecycle of database connections. It uses SQLModel/SQLAlchemy
to provide a thread-safe connection pool and session handling for both synchronous
background tasks and asynchronous FastAPI request cycles.

"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from .config import settings

# Guard to avoid repeated create_all calls during test runs
_tables_created = False


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
        "pool_pre_ping": True,
    }

    # Performance tuning: Only apply pool limits to persistent databases (PostgreSQL/MySQL).
    # SQLite uses dedicated pooling strategies that don't support these parameters.
    if not settings.is_sqlite:
        engine_kwargs["pool_size"] = settings.database_pool_size
        engine_kwargs["max_overflow"] = settings.database_max_overflow

    engine = create_engine(settings.database_url, **engine_kwargs)

    return engine


class _EngineProxy:
    """Lazy engine proxy that can be overridden in tests by assigning
    `app.database.engine = some_engine` or by calling `set_engine()`.

    Accessing attributes forwards to the underlying Engine instance.
    """

    def __init__(self):
        self._engine: Engine | None = None

    def set(self, engine: Engine) -> None:
        self._engine = engine

    def get(self) -> Engine:
        if self._engine is None:
            self._engine = create_db_engine()
        return self._engine

    def __getattr__(self, item):
        return getattr(self.get(), item)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"_EngineProxy({self._engine!r})"


# Module-level engine proxy. Tests can replace the real Engine by
# assigning to `app.database.engine` or calling `set_engine()` below.
engine: _EngineProxy | Engine = _EngineProxy()


def set_engine(e: Engine) -> None:
    """Override the module engine with a provided Engine instance."""
    global engine
    if isinstance(engine, _EngineProxy):
        engine.set(e)
    else:
        engine = e


def get_engine() -> Engine:
    """Return the underlying Engine, creating it lazily if needed."""
    if isinstance(engine, _EngineProxy):
        return engine.get()
    return engine


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
    session = Session(get_engine())
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
    # In test or development environments, ensure schema exists on the engine.
    # Always attempt to create missing tables on the active engine in test/dev so
    # that tests cannot observe a missing-table race due to import-order.
    if settings.environment in ("development", "test"):
        try:
            # Import models so SQLModel metadata is populated
            import app.models  # noqa: F401
        except Exception:
            pass
        try:
            SQLModel.metadata.create_all(get_engine())
        except Exception:
            # Best-effort: if create_all fails, allow the request to proceed
            # so upstream handlers can surface a clearer error for debugging.
            pass

    with Session(get_engine()) as session:
        yield session


# Base model for SQLAlchemy/SQLModel ORM
class Base(SQLModel):
    pass
