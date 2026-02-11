"""
TokenPool Middleware
Rate limiting, request logging, and other middleware components.
"""

import time
import uuid
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .logging_config import (
    get_logger, 
    log_request, 
    request_id_var, 
    user_id_var
)

logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to add request context (request ID, timing) to all requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(request_id)
        
        # Start timing
        start_time = time.perf_counter()
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(
                f"Unhandled exception in request: {e}",
                exc_info=True,
                extra_data={"request_id": request_id, "path": request.url.path}
            )
            raise
        finally:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Log request if enabled
            if settings.log_requests:
                log_request(
                    logger=logger,
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    user_id=user_id_var.get()
                )
        
        # Add headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        
        # Clear context
        request_id_var.set(None)
        user_id_var.set(None)
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    
    For production, consider using Redis-backed rate limiting.
    This implementation uses a sliding window algorithm.
    """
    
    def __init__(self, app: FastAPI, requests_per_window: int, window_seconds: int, burst: int = 10):
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.burst = burst
        self._requests: dict = {}  # client_id -> list of timestamps
        self._cleanup_interval = 60  # seconds
        self._last_cleanup = time.time()
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get API key first (for authenticated requests)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return f"key:{auth_header[7:20]}"  # Use partial key hash
        
        api_key = request.headers.get("X-API-Key", "")
        if api_key:
            return f"key:{api_key[:20]}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        
        return f"ip:{request.client.host if request.client else 'unknown'}"
    
    def _cleanup_old_entries(self) -> None:
        """Remove old entries to prevent memory bloat."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        cutoff = now - self.window_seconds
        for client_id in list(self._requests.keys()):
            self._requests[client_id] = [
                ts for ts in self._requests[client_id] if ts > cutoff
            ]
            if not self._requests[client_id]:
                del self._requests[client_id]
        
        self._last_cleanup = now
    
    def _is_rate_limited(self, client_id: str) -> tuple[bool, int, int]:
        """
        Check if client is rate limited.
        
        Returns:
            tuple: (is_limited, remaining_requests, retry_after_seconds)
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Get timestamps for this client
        if client_id not in self._requests:
            self._requests[client_id] = []
        
        # Filter to current window
        timestamps = [ts for ts in self._requests[client_id] if ts > window_start]
        self._requests[client_id] = timestamps
        
        # Check limits
        request_count = len(timestamps)
        remaining = max(0, self.requests_per_window - request_count)
        
        # Allow burst for new clients
        effective_limit = self.requests_per_window + self.burst if request_count < self.burst else self.requests_per_window
        
        if request_count >= effective_limit:
            # Calculate retry-after
            oldest_in_window = min(timestamps) if timestamps else now
            retry_after = int(oldest_in_window + self.window_seconds - now) + 1
            return True, 0, max(1, retry_after)
        
        # Record this request
        self._requests[client_id].append(now)
        
        return False, remaining - 1, 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting if disabled
        if not settings.rate_limit_enabled:
            return await call_next(request)
        
        # Skip rate limiting for health checks and docs
        skip_paths = {"/health", "/docs", "/redoc", "/openapi.json"}
        if request.url.path in skip_paths:
            return await call_next(request)
        
        # Periodic cleanup
        self._cleanup_old_entries()
        
        # Check rate limit
        client_id = self._get_client_id(request)
        is_limited, remaining, retry_after = self._is_rate_limited(client_id)
        
        if is_limited:
            logger.warning(
                f"Rate limit exceeded for client",
                extra_data={"client_id": client_id, "path": request.url.path}
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "code": "rate_limit_exceeded",
                    "message": f"Too many requests. Please retry after {retry_after} seconds.",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests_per_window),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_seconds)
        
        return response


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the application."""
    # Add request context middleware (should be outermost)
    app.add_middleware(RequestContextMiddleware)
    
    # Add rate limiting middleware
    if settings.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_window=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_window_seconds,
            burst=settings.rate_limit_burst
        )
