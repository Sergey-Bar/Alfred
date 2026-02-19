import sys
sys.path.insert(0, 'src/backend')
import importlib
m = importlib.import_module('app.main')
app = getattr(m, 'app')
print('Total routes:', len(app.routes))
for r in app.routes:
    print(r.path)
