from fastapi import APIRouter
from ..config import settings

router = APIRouter(tags=["System Reliability"])

@router.get("/health")
async def health_check():
    """Container Liveness/Readiness probe."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.4.2-stable"
    }

@router.get("/v1/system/integrations")
async def get_integrations_config():
    """Operational status of outbound notification sinks."""
    return {
        "slack": settings.slack_webhook_url is not None,
        "telegram": settings.telegram_bot_token is not None,
        "teams": settings.teams_webhook_url is not None,
        "whatsapp": settings.whatsapp_access_token is not None,
        "email": settings.sso_enabled # Using sso_enabled as a proxy if smtp_host is missing
    }

@router.get("/")
async def api_root():
    """Human-readable root status."""
    return {
        "name": "Alfred",
        "platform": "Alfred Enterprise AI Gateway",
        "doc_url": "/docs",
        "status": "operational",
        "version": "1.4.2-stable"
    }
