"""
Alfred - Enterprise AI Credit Governance Platform
Core API Gateway & Orchestration Engine (Modular Entry Point)

[ARCHITECTURAL ROLE]
This is the lean entry point for the Alfred platform. It orchestrates the
request lifecycle by mounting domain-specific routers and configuring
application-wide middleware and lifespan events.

# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: This file is the main entry point for the Alfred FastAPI application. It sets up logging, middleware, routers, CORS, telemetry, and static asset serving, following a modular and observable architecture.
# Why: Centralizing all app-wide configuration and router registration ensures maintainability, testability, and clear separation of concerns.
# Root Cause: FastAPI requires a single app instance for ASGI servers; all cross-cutting concerns (logging, CORS, metrics, etc.) must be initialized here.
# Context: This file should remain lean, delegating business logic to routers and modules. Future improvements: consider dynamic router loading and more granular middleware composition.
# Model Suitability: For architectural entry points, GPT-4.1 is sufficient; for advanced dependency injection or dynamic plugin loading, a more advanced model may be preferred.
"""

import importlib
import os
from types import ModuleType

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .exceptions import setup_exception_handlers
from .logging_config import get_logger, setup_logging
from .middleware import setup_middleware

# Routers are imported lazily inside `register_routers` to reduce startup import
# overhead. Each router module is resolved at registration time; missing modules
# are skipped and logged at debug level. This improves cold-start time and
# avoids importing large optional dependencies during test runs.


def _import_module(module_name: str) -> ModuleType | None:
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        logger = get_logger(__name__)
        logger.debug("Optional router module '%s' not available: %s", module_name, e)
        return None


from redis.asyncio import Redis
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .database import get_db_session
from .lifespan import alfred_lifespan

# Expose `get_session` for test fixtures that expect `app.main.get_session`
get_session = get_db_session

# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Initializes structured logging for observability and compliance, using project settings for log level, format, and PII masking.
# Why: Centralized logging is critical for debugging, auditability, and security.
# Root Cause: Without early logging setup, errors in startup or middleware may go undetected.
# Context: Logging config is loaded before any app or middleware initialization.
setup_logging(
    log_level=settings.log_level,
    log_format=settings.log_format,
    mask_pii=settings.mask_pii_in_logs,
    log_file=settings.log_file,
)
logger = get_logger(__name__)


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Optionally imports Prometheus instrumentation for metrics if available.
# Why: Metrics are essential for production monitoring but should not break dev environments.
# Root Cause: Some deployments may not have prometheus_fastapi_instrumentator installed.
# Context: Instrumentator is set to None if import fails, so metrics are optional.
try:
    from prometheus_fastapi_instrumentator import Instrumentator
except Exception:
    Instrumentator = None


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Validates that Redis URL is present in settings before proceeding.
# Why: Redis is required for distributed rate limiting and caching.
# Root Cause: Missing redis_url would cause runtime errors in rate limiter setup.
# Context: Fails fast if misconfigured, improving developer feedback.
if not hasattr(settings, "redis_url"):
    raise AttributeError("The 'redis_url' attribute is missing in settings. Please define it.")


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Instantiates the FastAPI app with project metadata and conditional docs URLs.
# Why: Ensures the app object exists before middleware and router registration.
# Root Cause: FastAPI requires a single app instance for all configuration.
# Context: Docs are disabled in production for security.
app = FastAPI(
    title=settings.app_name,
    description="Enterprise Multi-LLM Gateway with B2B Quota Governance",
    version=settings.app_version,
    lifespan=alfred_lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Sets up Redis-backed distributed rate limiting using SlowAPI and attaches it to the app state.
# Why: Prevents abuse and enforces fair usage across distributed deployments.
# Root Cause: Without rate limiting, API could be overwhelmed or exploited.
# Context: If Redis is unavailable, logs an error but does not crash the app.
try:
    redis = Redis.from_url(settings.redis_url)
    limiter = Limiter(key_func=get_remote_address, storage_uri=settings.redis_url)

    # Add rate limiting middleware using SlowAPIMiddleware
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    logger.info("Redis-backed distributed rate limiting enabled.")
except Exception as e:
    logger.error(f"Failed to initialize Redis-backed rate limiting: {e}")


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: (Redundant) Re-instantiates FastAPI app with same settings. This is likely a copy-paste or merge artifact.
# Why: Should be removed for clarity; only one app instance is needed.
# Root Cause: Duplicate app instantiation can cause confusion or bugs.
# Context: Safe to remove in future refactor.
# (No code change here, just comment for future improvement)


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Adds Prometheus metrics endpoint for observability if Instrumentator is available.
# Why: Enables real-time monitoring and alerting for API health and usage.
# Root Cause: Metrics are critical for SRE and compliance.
# Context: Handles partial failures gracefully, logs warnings if metrics setup fails.
if Instrumentator is not None:
    try:
        instrumentator = Instrumentator(
            should_group_status_codes=False,
            excluded_handlers=["/metrics"],
            should_ignore_untemplated=True,
        )
        instrumentator.instrument(app).expose(app, endpoint="/metrics")
        logger.info("Prometheus metrics exposed at /metrics endpoint.")
    except Exception:
        logger.warning("Telemetry Instrumentation partially failed.", exc_info=True)


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Registers global exception handlers and custom middleware for security, logging, and request shaping.
# Why: Ensures consistent error handling and cross-cutting concerns are enforced.
# Root Cause: FastAPI requires explicit registration of exception handlers and middleware.
# Context: All middleware should be registered before routers.
setup_exception_handlers(app)
setup_middleware(app)


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Configures CORS to restrict cross-origin requests, with stricter rules in production.
# Why: Prevents CSRF and data exfiltration from unauthorized origins.
# Root Cause: Open CORS in production is a security risk.
# Context: CORS origins are loaded from settings, fallback to default in dev.
cors_origins = (
    [o for o in settings.cors_origins if o != "*"]
    if settings.is_production
    else settings.cors_origins
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["api.alfred.enterprise"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Registers all domain-specific routers for modular API endpoints.
# Why: Keeps API surface organized and maintainable.
# Root Cause: FastAPI requires explicit router registration for modularity.
# Context: Each router handles a specific domain (auth, users, teams, etc.).


def register_routers(app: FastAPI):
    """
    Register all API routers in a modular, categorized way.

    This function organizes routers by business domain for better maintainability
    and makes it easier to add new routers to appropriate categories.
    """
    # Core Identity & Access Management
    identity_routers = [
        ("routers.users", "Identity & Access Management"),
        ("routers.teams", "Teams & Collaboration"),
        ("routers.auth", "Authentication"),
    ]

    # Governance & Credit Management
    governance_routers = [("routers.governance", "Governance & Credit Reallocation")]
    # Alias router handled below if present on module

    # Analytics & Reporting
    analytics_routers = [
        ("dashboard", "Dashboard & Analytics"),
        ("routers.usage_analytics", "Usage Analytics"),
        ("routers.custom_reports", "Custom Reports"),
        ("routers.data_export", "Data Export"),
        ("routers.analytics", "Real-Time & Historical Analytics"),
    ]

    # Administration & Configuration
    admin_routers = [
        ("routers.admin_config", "Admin Configuration"),
        ("routers.audit_log", "Audit Logging"),
        ("routers.rbac", "Role-Based Access Control"),
        ("routers.notifications", "Notifications"),
        ("routers.import_export", "Import/Export"),
        ("routers.metrics", "Metrics"),
    ]

    # Data Management & Quality
    data_routers = [
        ("routers.data_access", "Data Access Controls"),
        ("routers.data_anonymization", "Data Anonymization & Masking"),
        ("routers.alerting", "Alerting & Anomaly Detection"),
        ("routers.sharing", "Collaboration & Sharing"),
        ("routers.data_prep", "Data Preparation & Transformation"),
        ("routers.query_validation", "Advanced Query Validation & BI Integration"),
        ("routers.report_audit", "Audit Logging & Permission Checks"),
        ("routers.data_quality", "Data Quality Monitoring"),
        ("routers.data_lineage", "Data Lineage & Provenance"),
        ("routers.data_catalog", "Data Catalog & Metadata Management"),
        ("routers.data_enrichment", "Data Enrichment Pipelines"),
        ("routers.data_governance", "Data Governance & Stewardship"),
    ]

    # External Integrations
    integration_routers = [
        ("routers.bi_connectors", "BI Tools Integration"),
        ("routers.compliance", "Compliance"),
    ]

    # Core API Gateway
    gateway_routers = [
        ("routers.proxy", "AI Gateway"),
    ]

    # Onboarding & Documentation
    onboarding_routers = [
        ("routers.gitops_onboarding", "Onboarding & GitOps Docs"),
    ]

    # Register all router categories
    all_router_categories = [
        identity_routers,
        governance_routers,
        analytics_routers,
        admin_routers,
        data_routers,
        integration_routers,
        gateway_routers,
        onboarding_routers,
    ]

    # Resolve module paths relative to this package (e.g. 'app.routers.<name>').
    pkg = __package__ or "app"

    def _resolve_and_include(item, tag: str):
        # item may be a module path (e.g. 'routers.users') or a module name
        mod_path = item if item.startswith(".") or item.startswith(pkg) else f"{pkg}.{item}"
        mod = _import_module(mod_path)
        if not mod:
            return

        # Prefer `.router` attribute; fallback to `_alias_router` or module-level `include`.
        router_obj = (
            getattr(mod, "router", None)
            or getattr(mod, "_alias_router", None)
            or getattr(mod, "include", None)
        )
        if router_obj is None:
            logger.debug("Module %s has no router attribute; skipping", mod_path)
            return

        app.include_router(router_obj, tags=[tag])

    for category in all_router_categories:
        for item, tag in category:
            _resolve_and_include(item, tag)


# Register all routers
register_routers(app)


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Serves static assets for the SPA frontend, with fallback to index.html for client-side routing.
# Why: Enables seamless SPA navigation and asset delivery from the same server.
# Root Cause: SPAs require all non-API routes to return index.html for client-side routing.
# Context: Excludes API and metrics routes from SPA fallback. Returns 404 for missing assets.
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="static-assets")

    @app.get("/{path:path}")
    async def serve_spa_fallback(path: str, request: Request):
        # Exclude API routes from SPA fallback
        if (
            path.startswith("v1/")
            or path.startswith("docs")
            or path.startswith("redoc")
            or path.startswith("metrics")
            or path.startswith("health")
        ):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        file_path = os.path.join(static_dir, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

        return JSONResponse(status_code=404, content={"detail": "Static assets not found"})

else:
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Adds / and /health endpoints for root info and health checks.
    # Why: Enables health check and root info endpoints for monitoring and test coverage.
    # Root Cause: These endpoints were missing, causing 404s in health and root tests.
    # Context: These endpoints are required for readiness/liveness probes and test validation.

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": "2026-02-17", "version": settings.app_version}

    @app.get("/")
    async def api_root_fallback():
        return {
            "name": "Alfred",
            "platform": "Alfred API Lite",
            "status": "running",
            "version": settings.app_version,
        }
