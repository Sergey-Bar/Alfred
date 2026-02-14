"""
Alfred - Enterprise AI Credit Governance Platform
Observability & Structured Logging Framework

[ARCHITECTURAL ROLE]
This module defines the logging DNA of the platform. It provides:
1. Tracing Context: Automatic propagation of Request/User IDs via ContextVars.
2. Structured Data: JSON-formatted output for ELK/Datadog ingestion.
3. Security Hardening: Automated PII masking (email, keys) at the formatting layer.
4. Developer Experience: Human-readable, color-coded output for local development.

[LOGGING STRATEGY]
We use 'Structured Aggregation'. Instead of flat strings, we log machine-readable
objects that allow for complex querying and performance bottleneck analysis
across distributed traces.
"""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# --- Global Context Tracing ---
# ContextVars ensure that request/user identifiers are accessible to every function
# deep in the call stack without having to pass them explicitly.
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


class JSONFormatter(logging.Formatter):
    """
    Production-Grade Structured Formatter.
    
    Converts Python log records into standardized JSON blobs. 
    Implements recursive PII masking to ensure compliance with GDPR/SOC2.
    """

    def __init__(self, mask_pii: bool = True):
        super().__init__()
        self.mask_pii = mask_pii
        # Sensitive keys that must never appear in raw logs
        self._pii_fields = {"email", "api_key", "password", "token", "authorization", "secret"}

    def _mask_value(self, key: str, value: Any) -> Any:
        """Sanitizes sensitive data while preserving debug utility (shows first 4 chars)."""
        if not self.mask_pii:
            return value

        key_lower = key.lower()
        if any(pii in key_lower for pii in self._pii_fields):
            if isinstance(value, str) and len(value) > 4:
                return f"{value[:4]}***"
            return "***"
        return value

    def _mask_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Deep-walking masking algorithm for complex nested 'extra' data objects."""
        result = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key] = self._mask_dict(value)
            else:
                result[key] = self._mask_value(key, value)
        return result

    def format(self, record: logging.LogRecord) -> str:
        """Transformation: LogRecord -> JSON String."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Inject Cross-Cutting Context (Correlation IDs)
        if (req_id := request_id_var.get()): log_data["request_id"] = req_id
        if (usr_id := user_id_var.get()): log_data["user_id"] = usr_id

        # Merge Structured 'Extra' Metadata
        if hasattr(record, "extra_data"):
            extra = self._mask_dict(record.extra_data) if isinstance(record.extra_data, dict) else record.extra_data
            log_data["extra"] = extra

        # Precise Exception Reporting
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }

        return json.dumps(log_data, default=str)


class DevelopmentFormatter(logging.Formatter):
    """
    Console Beautifier.
    Used during development to provide high-visibility, color-coded output.
    """

    COLORS = {
        "DEBUG": "\033[36m", "INFO": "\033[32m", "WARNING": "\033[33m",
        "ERROR": "\033[31m", "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        
        # Identity Badge: Show first 8 chars of request ID for easy tracking
        req_ctx = f"[req:{rid[:8]}] " if (rid := request_id_var.get()) else ""

        message = (
            f"{color}[{timestamp}] [{record.levelname}]{self.RESET} "
            f"[{record.name}] {req_ctx}{record.getMessage()}"
        )

        if hasattr(record, "extra_data") and record.extra_data:
            message += f"\n  {color}▸ Data:{self.RESET} {record.extra_data}"

        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"

        return message


class StructuredLogger(logging.Logger):
    """
    Enhanced Logger API.
    Provides standard logging methods with a first-class `extra_data` argument.
    """

    def _log_with_extra(self, level: int, msg: str, args: tuple, extra_data: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        if extra_data:
            extra = kwargs.get("extra", {})
            extra["extra_data"] = extra_data
            kwargs["extra"] = extra
        super()._log(level, msg, args, **kwargs)

    def debug(self, msg: str, *args, extra_data: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self._log_with_extra(logging.DEBUG, msg, args, extra_data, **kwargs)

    def info(self, msg: str, *args, extra_data: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self._log_with_extra(logging.INFO, msg, args, extra_data, **kwargs)

    def warning(self, msg: str, *args, extra_data: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self._log_with_extra(logging.WARNING, msg, args, extra_data, **kwargs)

    def error(self, msg: str, *args, extra_data: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self._log_with_extra(logging.ERROR, msg, args, extra_data, **kwargs)

    def critical(self, msg: str, *args, extra_data: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self._log_with_extra(logging.CRITICAL, msg, args, extra_data, **kwargs)


# Inject custom implementation into logging system
logging.setLoggerClass(StructuredLogger)


def setup_logging(log_level: str = "INFO", log_format: str = "json", mask_pii: bool = True, log_file: Optional[str] = None) -> logging.Logger:
    """
    Bootstrap the logging subsystem.
    
    Initializes the root logger with handlers and formatters based on the 
    current Environment setting.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers.clear()

    # Formatter Selection
    if log_format.lower() == "json":
        formatter = JSONFormatter(mask_pii=mask_pii)
    else:
        formatter = DevelopmentFormatter()

    # STDOUT Configuration (Standard for K8s/Docker)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter(mask_pii=mask_pii))
        root_logger.addHandler(file_handler)

    # Noise Reduction: Muting overly chatty frameworks
    for chatty in ["uvicorn.access", "sqlalchemy.engine", "httpx", "httpcore"]:
        logging.getLogger(chatty).setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> StructuredLogger:
    """Standard access point for retrieving a configured StructuredLogger."""
    return logging.getLogger(name)


def log_request(logger: logging.Logger, method: str, path: str, status_code: int, duration_ms: float, 
                user_id: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> None:
    """
    Lifecycle Logger.
    Logs standard HTTP metadata for every processed endpoint.
    """
    data = {
        "method": method, "path": path, "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }
    if user_id: data["user_id"] = user_id
    if extra: data.update(extra)

    logger.info(f"{method} {path} {status_code} ({duration_ms:.2f}ms)", extra_data=data)
