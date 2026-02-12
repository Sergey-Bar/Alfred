"""
Alfred Structured Logging Configuration
Provides structured logging with JSON output for production and readable output for development.
"""

import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import json
from contextvars import ContextVar

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging in production."""
    
    def __init__(self, mask_pii: bool = True):
        super().__init__()
        self.mask_pii = mask_pii
        self._pii_fields = {"email", "api_key", "password", "token", "authorization"}
    
    def _mask_value(self, key: str, value: Any) -> Any:
        """Mask sensitive values."""
        if not self.mask_pii:
            return value
        
        key_lower = key.lower()
        for pii_field in self._pii_fields:
            if pii_field in key_lower:
                if isinstance(value, str) and len(value) > 4:
                    return f"{value[:4]}***"
                return "***"
        return value
    
    def _mask_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively mask sensitive values in a dictionary."""
        result = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key] = self._mask_dict(value)
            else:
                result[key] = self._mask_value(key, value)
        return result
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add context variables
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            extra = self._mask_dict(record.extra_data) if isinstance(record.extra_data, dict) else record.extra_data
            log_data["extra"] = extra
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        return json.dumps(log_data, default=str)


class DevelopmentFormatter(logging.Formatter):
    """Readable log formatter for development."""
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record for development."""
        color = self.COLORS.get(record.levelname, "")
        reset = self.RESET
        
        # Build base message
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        parts = [
            f"{color}[{timestamp}]{reset}",
            f"{color}[{record.levelname}]{reset}",
            f"[{record.name}]",
            record.getMessage()
        ]
        
        # Add context if available
        request_id = request_id_var.get()
        if request_id:
            parts.insert(2, f"[req:{request_id[:8]}]")
        
        message = " ".join(parts)
        
        # Add extra data if present
        if hasattr(record, "extra_data") and record.extra_data:
            message += f"\n  Extra: {record.extra_data}"
        
        # Add exception info if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message


class StructuredLogger(logging.Logger):
    """Extended logger with structured logging support."""
    
    def _log_with_extra(
        self,
        level: int,
        msg: str,
        args: tuple,
        extra_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Log with extra structured data."""
        if extra_data:
            # Create a new LogRecord with extra_data attribute
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


# Register custom logger class
logging.setLoggerClass(StructuredLogger)


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    mask_pii: bool = True,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format - "json" for production, "text" for development
        mask_pii: Whether to mask PII in log output
        log_file: Optional file path for log output
    
    Returns:
        Configured root logger
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Choose formatter based on format setting
    if log_format.lower() == "json":
        formatter = JSONFormatter(mask_pii=mask_pii)
    else:
        formatter = DevelopmentFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter(mask_pii=mask_pii))  # Always JSON for files
        root_logger.addHandler(file_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        StructuredLogger instance
    """
    return logging.getLogger(name)


# Convenience function for request logging
def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """Log an HTTP request with structured data."""
    data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }
    if user_id:
        data["user_id"] = user_id
    if extra:
        data.update(extra)
    
    logger.info(
        f"{method} {path} {status_code} ({duration_ms:.2f}ms)",
        extra_data=data
    )
