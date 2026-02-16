"""
Compatibility shim so tests importing `backend.app.logging_config`
can find the real implementation under `src/backend/app` (package `app`).
"""

from importlib import import_module

_mod = import_module("app.logging_config")

setup_logging = _mod.setup_logging

__all__ = ["setup_logging"]
