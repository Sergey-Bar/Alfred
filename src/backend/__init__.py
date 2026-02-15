# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Marks src/backend as a Python package for test discovery and import resolution.
# Why: Required for pytest and relative imports to work reliably in custom project layouts.
# Root Cause: Missing __init__.py prevents Python from treating this directory as a package.
# Context: Enables 'from app.logic' imports in tests.
# Model Suitability: Standard package marker; GPT-4.1 is sufficient.
