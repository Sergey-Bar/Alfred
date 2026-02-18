from pathlib import Path
import os, sys
root = Path(__file__).resolve().parents[2]
_tmp = root / '.pytest_tmp'
_tmp.mkdir(exist_ok=True)
os.environ.setdefault('DATABASE_URL', f"sqlite:///{_tmp / 'test.db'}")
os.environ.setdefault('ENVIRONMENT', 'test')

# ensure src/backend is on path
src_backend = root / 'src' / 'backend'
if str(src_backend) not in sys.path:
    sys.path.insert(0, str(src_backend))

print('PYTHON PATH [0:3]:', sys.path[0:3])

try:
    import importlib
    app_db = importlib.import_module('app.database')
    import app.models  # noqa: F401
    from sqlalchemy import text
    try:
        eng = app_db.get_engine() if hasattr(app_db, 'get_engine') else getattr(app_db, 'engine')
    except Exception:
        eng = getattr(app_db, 'engine')
    print('Engine repr:', eng)
    try:
        with eng.connect() as conn:
            res = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
            print('tables:', res.fetchall())
    except Exception as e:
        print('Error listing tables:', e)
except Exception as e:
    import traceback
    print('Import error:', e)
    traceback.print_exc()
