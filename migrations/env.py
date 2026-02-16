"""
Minimal Alembic env.py tailored for this repository.
This loads `src/backend` onto sys.path and uses `app.models.SQLModel.metadata`
as the target metadata. It reads the DB URL from `DATABASE_URL` env var
and falls back to a local SQLite file for convenience.
"""
from __future__ import with_statement
import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

# ensure backend package is importable
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(repo_root, "src", "backend"))

fileConfig(os.path.join(repo_root, "src", "backend", "config", "logging.ini")) if os.path.exists(os.path.join(repo_root, "src", "backend", "config", "logging.ini")) else None

try:
    # import SQLModel metadata
    from app import models
    target_metadata = models.SQLModel.metadata
except Exception:
    target_metadata = None


def run_migrations_offline() -> None:
    url = os.environ.get("DATABASE_URL", "sqlite:///./alfred.db")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = os.environ.get("DATABASE_URL", "sqlite:///./alfred.db")
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
