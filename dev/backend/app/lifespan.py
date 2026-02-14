"""
Alfred Platform Lifecycle Orchestration

[ARCHITECTURAL ROLE]
This module defines the modular blocks for the FastAPI application lifecycle. 
It centralizes the "Bootstrapping" sequence—ensuring the database is in the 
correct state, organization parameters are seeded, and external integration 
sinks are properly bound before the application starts accepting traffic.

[SEQUENCE]
1. Environment Audit: Log version and tier metadata.
2. Schema Baseline: Auto-synchronize tables in non-production tiers.
3. Governance Seeding: Ensure at least one 'OrgSettings' record exists.
4. Integration Binding: Initialize Slack/Teams/Email notification managers.
"""

from contextlib import asynccontextmanager

from sqlmodel import Session, SQLModel, select

from .config import settings
from .integrations import setup_notifications
from .logging_config import get_logger
from .models import OrgSettings

logger = get_logger(__name__)

def create_tables_if_needed(engine):
    """
    Schema Synchronization Hook.
    
    Warning: This is only active in 'development' or 'test' environments. 
    Production schema changes must be orchestrated via Alembic migrations.
    """
    if settings.environment in ("development", "test"):
        SQLModel.metadata.create_all(engine)
        logger.info("Sandbox Sync: Local database tables synchronized.")


def initialize_org_settings(engine):
    """
    Governance Baseline Seeding.
    
    Ensures that the global OrgSettings entry is present. This record governs 
    platform-wide behaviors like privacy modes and credit policy.
    """
    with Session(engine) as session:
        org_settings = session.exec(select(OrgSettings)).first()
        if not org_settings:
            # First-run scenario: creating internal record 001
            org_settings = OrgSettings()
            session.add(org_settings)
            session.commit()
            logger.info("Governance: Initial Organization Settings record seeded.")


def setup_notifications_if_enabled():
    """
    Integration Subsystem Binding.
    
    Initializes the multi-channel notification manager with credentials 
    sourced from the configuration layer.
    """
    if settings.notifications_enabled:
        try:
            notification_manager = setup_notifications(
                slack_webhook_url=settings.slack_webhook_url,
                slack_alerts_webhook_url=settings.slack_alerts_webhook_url,
                slack_bot_token=settings.slack_bot_token,
                teams_webhook_url=settings.teams_webhook_url,
                # Additional notification sinks can be mapped here
                telegram_bot_token=getattr(settings, 'telegram_bot_token', None),
                whatsapp_token=getattr(settings, 'whatsapp_token', None),
            )
            logger.info("Integrations: Notification subsystem online.")
        except Exception as e:
            logger.error(f"Integrations Failure: Connectivity issues with notification sinks ({e}).")

@asynccontextmanager
def alfred_lifespan(app, engine):
    """
    Stateful Lifespan Coordinator.
    
    Wraps the startup and shutdown sequence in a context manager to ensure 
    resources are cleaned up correctly even if a crash occurs during boot.
    """
    logger.info(
        "Alfred Core Initializing...",
        extra_data={
            "v": settings.app_version,
            "tier": settings.environment,
            "mode": "STRICT_PROD" if settings.is_production else "LAX_DEV"
        }
    )
    try:
        # Pre-flight initialization sequence
        create_tables_if_needed(engine)
        initialize_org_settings(engine)
        setup_notifications_if_enabled()
        
        yield # Start serving requests
        
    except Exception as e:
        logger.error(f"Critical Startup Collision: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Alfred Core Shutdown: All lifecycle hooks released.")
