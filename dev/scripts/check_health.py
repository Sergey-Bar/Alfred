"""Simple script to verify the FastAPI app health and test DB visibility.

Run: `python dev/scripts/check_health.py`
"""
import os
from pathlib import Path

from fastapi.testclient import TestClient

# Ensure repo src/backend is on path when script is executed from repo root
root = Path(__file__).resolve().parents[2]
src_backend = root / "src" / "backend"
import sys
if str(src_backend) not in sys.path:
    sys.path.insert(0, str(src_backend))

# Prefer a file-backed test DB so both app and fixtures can observe it when used in CI
tmp = Path(root) / ".pytest_tmp"
tmp.mkdir(exist_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{tmp / 'health_check.db'}")
os.environ.setdefault("ENVIRONMENT", "test")

try:
    import app.main as main
except Exception as e:
    print("Failed to import app.main:", e)
    raise

client = TestClient(main.app)

# Ensure tables exist on the application's engine for a meaningful users_count check
try:
    from sqlmodel import SQLModel
    import app.database as _app_db

    SQLModel.metadata.create_all(_app_db.engine)
except Exception as _:
    pass

for path in ("/health", "/test/users_count"):
    resp = client.get(path)
    print(path, resp.status_code, resp.text)
