"""Force-create all SQLModel tables on the application's engine using test DB.

Usage:
  python tools/force_create_tables.py
"""
import os
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
src_backend = root / "src" / "backend"
if str(src_backend) not in sys.path:
    sys.path.insert(0, str(src_backend))

_tmp = root / ".pytest_tmp"
_tmp.mkdir(exist_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp / 'test.db'}")
os.environ.setdefault("ENVIRONMENT", "test")

try:
    import app.database as _app_db  # type: ignore
    from sqlmodel import SQLModel
    import app.models  # noqa: F401

    SQLModel.metadata.create_all(_app_db.engine)
    print("Created tables on:", _app_db.engine.url)
except Exception as e:
    print("Failed to create tables:", e)
    raise
