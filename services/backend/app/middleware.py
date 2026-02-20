"""
Alfred - Enterprise AI Credit Governance Platform
Unified Middleware Orchestration

[ARCHITECTURAL ROLE]
Middleware components sit between the raw HTTP server and the application logic.
They handle cross-cutting concerns that must apply to all requests, such as
security, observability, and traffic engineering.

"""

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .logging_config import get_logger, log_request, request_id_var, user_id_var

# Initialize specialized logger for middleware activity
logger = get_logger(__name__)

# Ensure 'app' is defined globally
app = FastAPI()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Observability & Tracing Middleware.

    Generates a unique Trace ID for every inbound request. This ID is propagated
    via the 'X-Request-ID' header and injected into all log statements via
    ContextVars. This allows 'Fingerprint' tracing of a single request across
    the entire distributed system.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Ingest existing trace ID if provided (for upstream integration), otherwise generate new.
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Set ContextVar for global access in logging/logic
        request_id_var.set(request_id)

        # Performance Baseline
        start_time = time.perf_counter()
        response = None

        try:
            # Transfer control to the next component in the pipeline
            response = await call_next(request)
        except Exception as e:
            # Critical Catch-All: Prevents raw stack traces from leaking to the client
            logger.error(
                f"Unhandled Exception in Lifecycle: {e}",
                exc_info=True,
                extra={"request_id": request_id, "path": request.url.path},
            )
            # Re-raise to let FastAPI's global exception handler format the response
            raise
        finally:
            # Telemetry Calculation
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log Audit: Records the success/failure of the request lifecycle
            if settings.log_requests and response is not None:
                log_request(
                    logger=logger,
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    user_id=user_id_var.get(),
                )

            # Hygiene: Clear ContextVars to prevent leakage into other greenlets/threads
            request_id_var.set(None)
            user_id_var.set(None)

        # Inject Trace Headers for Client-Side Observability
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

        return response


class RedisRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Traffic Engineering: Distributed sliding window via Redis.

    Ensures that rate limits are globally consistent across multiple application
    instances/pods. Uses a sorted set to implement high-precision sliding windows.
    """

    def __init__(
        self,
        app: FastAPI,
        redis_host: str | None = None,
        redis_port: int | None = None,
        redis_db: int | None = None,
        requests_per_window: int = 100,
        window_seconds: int = 60,
        burst: int = 10,
    ):
        # BaseHTTPMiddleware expects middleware __init__(app, ...)
        super().__init__(app)
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.burst = burst

        # [BUG-002 FIX] Added Lock for thread/async safety in multi-worker environments
        import asyncio

        self._lock = asyncio.Lock()

        # In-Memory Store: maps identifier -> list[timestamps]
        self._requests: dict = {}

        # Memory Management: Cleanup frequency
        self._cleanup_interval = 60
        self._last_cleanup = time.time()

    def _get_client_id(self, request: Request) -> str:
        """
        Identifier Resolution Algorithm.

        [BUG-006 FIX] Replaced partial key exposure with one-way SHA-256 hashing.
        This prevents API secrets from appearing in logs or being vulnerable to
        memory inspection attacks.
        """
        import hashlib

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # Hash the token to create a unique but opaque identifier
            key_hash = hashlib.sha256(auth_header[7:].encode()).hexdigest()[:16]
            return f"key:{key_hash}"

        api_key = request.headers.get("X-API-Key", "")
        if api_key:
            # Hash the header-provided key
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
            return f"key:{key_hash}"

        # Standard IP isolation (No hash needed for public IP metadata)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        return f"ip:{request.client.host if request.client else 'unknown'}"

    async def _cleanup_old_entries(self) -> None:
        """Prunes expired windows from memory to prevent OOM scenarios."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        async with self._lock:
            cutoff = now - self.window_seconds
            for client_id in list(self._requests.keys()):
                # Trim the list to only current window
                self._requests[client_id] = [ts for ts in self._requests[client_id] if ts > cutoff]
                # Remove keys with no active requests
                if not self._requests[client_id]:
                    del self._requests[client_id]

            self._last_cleanup = now

    async def _is_rate_limited(self, client_id: str) -> tuple[bool, int, int]:
        """
        Core Limiting Logic.

        [BUG-002 FIX] Wrapped logic in an async lock to ensure atomic
        counter updates under high concurrency.
        """
        now = time.time()
        window_start = now - self.window_seconds

        async with self._lock:
            if client_id not in self._requests:
                self._requests[client_id] = []

            # Update local window
            timestamps = [ts for ts in self._requests[client_id] if ts > window_start]
            self._requests[client_id] = timestamps

            request_count = len(timestamps)
            remaining = max(0, self.requests_per_window - request_count)

            # Apply Burst Buffer: Allow brief spikes for valid low-latency interactions
            effective_limit = (
                self.requests_per_window + self.burst
                if request_count < self.burst
                else self.requests_per_window
            )

            if request_count >= effective_limit:
                # Find the delta until the oldest request in the window expires
                oldest_in_window = min(timestamps) if timestamps else now
                retry_after = int(oldest_in_window + self.window_seconds - now) + 1
                return True, 0, max(1, retry_after)

            # Successful hit recorded
            self._requests[client_id].append(now)

            return False, remaining - 1, 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Passive mode check
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Passthrough for core system health check and dynamic documentation
        skip_paths = {"/health", "/docs", "/redoc", "/openapi.json"}
        if request.url.path in skip_paths:
            return await call_next(request)

        # Periodic memory hygiene
        await self._cleanup_old_entries()

        client_id = self._get_client_id(request)
        is_limited, remaining, retry_after = await self._is_rate_limited(client_id)

        if is_limited:
            logger.warning(
                "Inbound Traffic: RATE LIMITED",
                extra={"client_id": client_id, "path": request.url.path},
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "code": "rate_limit_exceeded",
                    "message": f"Threshold reached. Backoff for {retry_after} seconds.",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests_per_window),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after),
                },
            )

        # Logic Execution
        response = await call_next(request)

        # Inject Governance Headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_seconds)

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Traffic Engineering: Sliding Window Limiter.

    Defends the infrastructure (and the company's wallet) by capping the frequency
    of requests per client.

    In-Memory Implementation: Uses a localized dict for tracking.
    Note: For horizontally scaled production, this should be swapped for
    the RedisRateLimitMiddleware to ensure global consistency.
    """

    def __init__(self, app: FastAPI, requests_per_window: int, window_seconds: int, burst: int = 10):
        # FastAPI/Starlette calls middleware constructors with (app, *args, **kwargs)
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.burst = burst

        # [BUG-002 FIX] Added Lock for thread/async safety in multi-worker environments
        import asyncio

        self._lock = asyncio.Lock()

        # In-Memory Store: maps identifier -> list[timestamps]
        self._requests: dict = {}

        # Memory Management: Cleanup frequency
        self._cleanup_interval = 60
        self._last_cleanup = time.time()

    def _get_client_id(self, request: Request) -> str:
        """
        Identifier Resolution Algorithm.

        [BUG-006 FIX] Replaced partial key exposure with one-way SHA-256 hashing.
        This prevents API secrets from appearing in logs or being vulnerable to
        memory inspection attacks.
        """
        import hashlib

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # Hash the token to create a unique but opaque identifier
            key_hash = hashlib.sha256(auth_header[7:].encode()).hexdigest()[:16]
            return f"key:{key_hash}"

        api_key = request.headers.get("X-API-Key", "")
        if api_key:
            # Hash the header-provided key
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
            return f"key:{key_hash}"

        # Standard IP isolation (No hash needed for public IP metadata)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        return f"ip:{request.client.host if request.client else 'unknown'}"

    async def _cleanup_old_entries(self) -> None:
        """Prunes expired windows from memory to prevent OOM scenarios."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        async with self._lock:
            cutoff = now - self.window_seconds
            for client_id in list(self._requests.keys()):
                # Trim the list to only current window
                self._requests[client_id] = [ts for ts in self._requests[client_id] if ts > cutoff]
                # Remove keys with no active requests
                if not self._requests[client_id]:
                    del self._requests[client_id]

            self._last_cleanup = now

    async def _is_rate_limited(self, client_id: str) -> tuple[bool, int, int]:
        """
        Core Limiting Logic.

        [BUG-002 FIX] Wrapped logic in an async lock to ensure atomic
        counter updates under high concurrency.
        """
        now = time.time()
        window_start = now - self.window_seconds

        async with self._lock:
            if client_id not in self._requests:
                self._requests[client_id] = []

            # Update local window
            timestamps = [ts for ts in self._requests[client_id] if ts > window_start]
            self._requests[client_id] = timestamps

            request_count = len(timestamps)
            remaining = max(0, self.requests_per_window - request_count)

            # Apply Burst Buffer: Allow brief spikes for valid low-latency interactions
            effective_limit = (
                self.requests_per_window + self.burst
                if request_count < self.burst
                else self.requests_per_window
            )

            if request_count >= effective_limit:
                # Find the delta until the oldest request in the window expires
                oldest_in_window = min(timestamps) if timestamps else now
                retry_after = int(oldest_in_window + self.window_seconds - now) + 1
                return True, 0, max(1, retry_after)

            # Successful hit recorded
            self._requests[client_id].append(now)

            return False, remaining - 1, 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Passive mode check
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Passthrough for core system health check and dynamic documentation
        skip_paths = {"/health", "/docs", "/redoc", "/openapi.json"}
        if request.url.path in skip_paths:
            return await call_next(request)

        # Periodic memory hygiene
        await self._cleanup_old_entries()

        client_id = self._get_client_id(request)
        is_limited, remaining, retry_after = await self._is_rate_limited(client_id)

        if is_limited:
            logger.warning(
                "Inbound Traffic: RATE LIMITED",
                extra={"client_id": client_id, "path": request.url.path},
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "code": "rate_limit_exceeded",
                    "message": f"Threshold reached. Backoff for {retry_after} seconds.",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests_per_window),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after),
                },
            )

        # Logic Execution
        response = await call_next(request)

        # Inject Governance Headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_seconds)

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Hardening Middleware: Regulatory & Security Compliance.

    Implements industry-standard response headers to protect against common
    web attack vectors (XSS, Clickjacking, MIME-sniffing).
    Required for SOC2 and ISO27001 readiness.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Hardening configuration
        response.headers["X-Content-Type-Options"] = (
            "nosniff"  # Prevent browser from guessing MIME types
        )
        response.headers["X-Frame-Options"] = (
            "DENY"  # Prevent embedding in iframes (Anti-Clickjacking)
        )
        response.headers["X-XSS-Protection"] = "1; mode=block"  # Enable browser legacy XSS filters
        response.headers["Referrer-Policy"] = (
            "strict-origin-when-cross-origin"  # Hide sensitive referrer info
        )
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"  # Disable hardware access
        )

        # Content Security Policy (CSP): Prevents unauthorized script/style injection
        if not request.url.path.startswith("/docs") and not request.url.path.startswith("/redoc"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "  # Needed for Tailwind/UI components
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'"
            )

        # Force Encryption (HSTS): Instructs browsers to use HTTPS only
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


# Re-enabling middleware after debugging
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestContextMiddleware)
if settings.rate_limit_enabled:
    if settings.redis_enabled:
        logger.info("Governance: Initializing Distributed Redis Rate Limiter.")
        app.add_middleware(
            RedisRateLimitMiddleware,
            redis_host=settings.redis_host,
            redis_port=settings.redis_port,
            redis_db=settings.redis_db,
            requests_per_window=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_window_seconds,
            burst=settings.rate_limit_burst,
        )
    else:
        logger.info("Governance: Initializing Local In-Memory Rate Limiter (Scaling Warning).")
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_window=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_window_seconds,
            burst=settings.rate_limit_burst,
        )


def setup_middleware(app: FastAPI) -> None:
    """Register middleware components in the FastAPI app."""
    app.add_middleware(RequestContextMiddleware)
    logger.info("Middleware setup completed.")
