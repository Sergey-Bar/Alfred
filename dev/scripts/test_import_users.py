import sys, traceback, importlib
sys.path.insert(0, 'src/backend')
try:
    importlib.import_module('app.routers.users')
    print('OK')
except Exception:
    traceback.print_exc()
