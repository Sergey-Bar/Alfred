"""
Alfred Platform Lifecycle Orchestration

[ARCHITECTURAL ROLE]
This module defines the modular blocks for the FastAPI application lifecycle.
It centralizes the "Bootstrapping" sequence—ensuring the database is in the
correct state, organization parameters are seeded, and external integration
sinks are properly bound before the application starts accepting traffic.

# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: This module orchestrates the FastAPI app's startup and shutdown, including DB schema sync, org seeding, and notification setup.
# Why: Centralizing lifecycle logic ensures reliable, repeatable startup and teardown.
# Root Cause: Without a single entrypoint, resource leaks and inconsistent state are likely.
# Context: All app-wide bootstrapping should be handled here. Future: consider async DB migrations and health checks.
# Model Suitability: For lifecycle patterns, GPT-4.1 is sufficient; for advanced orchestration, a more advanced model may be preferred.
"""

from contextlib import asynccontextmanager

from sqlmodel import Session, SQLModel, select

from .config import settings
from .database import engine
from .integrations import setup_notifications
from .logging_config import get_logger
from .models import OrgSettings

logger = get_logger(__name__)


def create_tables_if_needed(engine):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Creates all DB tables in dev/test, never in prod (use Alembic for prod migrations).
    # Why: Ensures local/test environments are always in sync without manual intervention.
    # Root Cause: Auto-migrations in prod are dangerous; safe in dev/test.
    # Context: Called at startup in dev/test only.
    """
    Schema Synchronization Hook.

    Warning: This is only active in 'development' or 'test' environments.
    Production schema changes must be orchestrated via Alembic migrations.
    """
    if settings.environment in ("development", "test"):
        SQLModel.metadata.create_all(engine)
        logger.info("Sandbox Sync: Local database tables synchronized.")


def initialize_org_settings(engine):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Ensures a baseline OrgSettings record exists for global governance.
    # Why: Prevents platform from running without required org-level config.
    # Root Cause: Missing org settings would break quota and privacy logic.
    # Context: Called at startup after DB is ready.
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
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Initializes notification integrations (Slack, Teams, Telegram) if enabled in config.
    # Why: Ensures alerts and notifications are routed to admins and users.
    # Root Cause: Notification failures should not block startup but must be logged.
    # Context: Called at startup after org seeding.
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
                telegram_bot_token=getattr(settings, "telegram_bot_token", None),
            )
            logger.info("Integrations: Notification subsystem online.")
        except Exception as e:
            logger.error(
                f"Integrations Failure: Connectivity issues with notification sinks ({e})."
            )


@asynccontextmanager
async def alfred_lifespan(app: FastAPI) -> AsyncGenerator:
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Wraps FastAPI's lifespan with startup/shutdown hooks for DB, org, and integrations.
    # Why: Ensures all resources are initialized and cleaned up safely.
    # Root Cause: Unmanaged startup/shutdown leads to resource leaks and partial failures.
    # Context: Registered as the lifespan handler in main.py.
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
            "mode": "STRICT_PROD" if settings.is_production else "LAX_DEV",
        },
    )
    try:
        # Pre-flight initialization sequence
        create_tables_if_needed(engine)
        initialize_org_settings(engine)
        setup_notifications_if_enabled()

        yield  # Start serving requests

    except Exception as e:
        logger.error(f"Critical Startup Collision: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Alfred Core Shutdown: All lifecycle hooks released.")
