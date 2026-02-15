"""
Pytest configuration and fixtures for Alfred backend unit tests.

This file loads all fixtures from the main QA Backend conftest.py to enable test discovery and fixture reuse.
"""

import importlib.util
import sys
from pathlib import Path

# Correct path to dev/QA/Backend/conftest.py
qa_backend_conftest = Path(__file__).parent.parent.parent.parent.parent.parent / "dev" / "QA" / "Backend" / "conftest.py"
spec = importlib.util.spec_from_file_location("qa_backend_conftest", str(qa_backend_conftest))
qa_backend = importlib.util.module_from_spec(spec)
sys.modules["qa_backend_conftest"] = qa_backend
spec.loader.exec_module(qa_backend)

globals().update({k: v for k, v in qa_backend.__dict__.items() if not k.startswith("__")})
