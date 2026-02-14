"""
Alfred - Enterprise AI Credit Governance Platform
Core API Gateway & Orchestration Engine (Modular Entry Point)

[ARCHITECTURAL ROLE]
This is the lean entry point for the Alfred platform. It orchestrates the 
request lifecycle by mounting domain-specific routers and configuring 
application-wide middleware and lifespan events.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, SQLModel, select

from .config import settings
from .database import engine
from .dependencies import get_session
from .exceptions import setup_exception_handlers
from .integrations import (
    get_notification_manager,
    setup_notifications,
    setup_sso
)
from .logging_config import get_logger, setup_logging
from .middleware import setup_middleware
from .models import OrgSettings
from .dashboard import router as dashboard_router
from .routers import proxy, users, teams, governance, system, websocket

# Bootstrapping the Observability Framework
setup_logging(
    log_level=settings.log_level,
    log_format=settings.log_format,
    mask_pii=settings.mask_pii_in_logs,
    log_file=settings.log_file
)
logger = get_logger(__name__)

# Prometheus instrumentation is optional
try:
    from prometheus_fastapi_instrumentator import Instrumentator
except Exception:
    Instrumentator = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application Lifecycle Orchestrator."""
    logger.info(
        "Alfred Core Initialization",
        extra_data={
            "v": settings.app_version,
            "tier": settings.environment,
            "mode": "PROD" if settings.is_production else "DEV"
        }
    )
    
    # 1. Secret Management Verification
    if settings.vault_enabled:
        if not settings.vault_addr or not settings.vault_token:
            logger.error("CRITICAL SECURITY RISK: Vault enabled but credentials missing.")

    try:
        # 2. Schema Management
        if settings.environment in ("development", "test"):
            SQLModel.metadata.create_all(engine)
            logger.info("Sandbox Environment: Local tables synchronized.")
        else:
            logger.info("Production Environment: DB migrations managed by external orchestrator.")

        # 3. Governance Baseline
        with Session(engine) as session:
            org_settings = session.exec(select(OrgSettings)).first()
            if not org_settings:
                org_settings = OrgSettings()
                session.add(org_settings)
                session.commit()
                logger.info("Governance: Global Organization settings seeded.")

        # 4. Notification Integration
        if settings.notifications_enabled:
            setup_notifications(
                slack_webhook_url=settings.slack_webhook_url,
                slack_alerts_webhook_url=settings.slack_alerts_webhook_url,
                slack_bot_token=settings.slack_bot_token,
                teams_webhook_url=settings.teams_webhook_url,
                teams_alerts_webhook_url=settings.teams_alerts_webhook_url,
            )

        # 5. SSO Initialization
        setup_sso(settings)
        
        yield
        
    finally:
        # Graceful Shutdown
        if settings.notifications_enabled:
            manager = get_notification_manager()
            await manager.close()
        logger.info("Alfred Core Shutdown: All subsystems released.")


app = FastAPI(
    title=settings.app_name,
    description="Enterprise Multi-LLM Gateway with B2B Quota Governance",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None
)

# Telemetry
if Instrumentator is not None:
    try:
        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    except Exception:
        logger.warning("Telemetry Instrumentation partially failed.")

# Middleware & Exceptions
setup_exception_handlers(app)
setup_middleware(app)

# CORS
cors_origins = [o for o in settings.cors_origins if o != "*"] if settings.is_production else settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["api.alfred.enterprise"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route Mounting
app.include_router(system.router)
app.include_router(websocket.router)
app.include_router(proxy.router)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(governance.router)
app.include_router(dashboard_router)

# SPA Static Asset Pipeline
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
if os.path.exists(static_dir):
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="static-assets")

    @app.get("/{path:path}")
    async def serve_spa_fallback(path: str, request: Request):
        # Exclude API routes from SPA fallback
        if path.startswith("v1/") or path.startswith("docs") or path.startswith("redoc") or path.startswith("metrics") or path.startswith("health"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        
        file_path = os.path.join(static_dir, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        return JSONResponse(status_code=404, content={"detail": "Static assets not found"})
else:
    @app.get("/")
    async def api_root_fallback():
        return {"platform": "Alfred API Lite", "status": "running"}
