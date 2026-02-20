import importlib

import pytest
from sqlmodel import create_engine
from sqlalchemy.pool import StaticPool


def test_engine_injection_roundtrip():
    """Ensure `app.database.set_engine()` updates the app engine and
    `app.database.get_engine()` returns the same Engine instance.
    """
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    app_db = importlib.import_module("app.database")

    if not hasattr(app_db, "set_engine") or not hasattr(app_db, "get_engine"):
        pytest.skip("app.database does not support engine injection")

    app_db.set_engine(engine)
    got = app_db.get_engine()
    assert got is engine
