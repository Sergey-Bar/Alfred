"""
Alfred Integrations
External service integrations for notifications, webhooks, and SSO/OAuth2.

SSO/OAuth2 integration is managed via the `sso.py` module, which provides a modular interface for adding new providers (Okta, Azure AD, Google, Keycloak, etc.).

How to add a new SSO provider:
1. Extend the `SSOProviderConfig` in `sso.py` with any provider-specific fields if needed.
2. Implement provider-specific logic in `SSOManager` if the standard OIDC flow is not sufficient.
3. Use the `validate_token` method to validate tokens and extract user info.
4. Register the provider in your FastAPI app by creating an `SSOManager` instance with the appropriate config.

Example usage:
    from .integrations.sso import SSOManager, SSOProviderConfig
    sso_config = SSOProviderConfig(
        provider="okta",
        client_id="...",
        client_secret="...",
        issuer_url="https://dev-123456.okta.com/oauth2/default"
    )
    sso_manager = SSOManager(sso_config)
    user_info = await sso_manager.validate_token(token)

See `sso.py` for more details and usage examples.
"""

from typing import Optional

from .base import EventType, NotificationEvent, NotificationProvider
from .manager import (
    NotificationManager,
    emit_approval_requested,
    emit_approval_resolved,
    emit_quota_exceeded,
    emit_quota_warning,
    emit_token_transfer,
    emit_vacation_status_change,
    get_notification_manager,
    setup_notifications,
)
from .slack import SlackNotifier
from .sso import SSOManager, SSOProviderConfig
from .teams import TeamsNotifier
from .telegram import TelegramNotifier
from .whatsapp import WhatsAppNotifier
from .email import EmailNotifier, create_email_notifier
from .webhook import WebhookNotifier, create_webhook_notifier
from .escalation import (
    AlertDeduplicator,
    EscalationLadder,
    EscalationLevel,
    EscalationTarget,
    EscalationRule,
    DEFAULT_ESCALATION_RULES,
)
from .digest import daily_digest_loop

# Global SSO Manager Singleton
sso_manager: Optional[SSOManager] = None


def setup_sso(settings) -> Optional[SSOManager]:
    global sso_manager
    if settings.sso_enabled and settings.sso_provider and settings.sso_client_id:
        config = SSOProviderConfig(
            provider=settings.sso_provider,
            client_id=settings.sso_client_id,
            client_secret=settings.sso_client_secret or "",
            issuer_url=settings.sso_issuer_url or "",
        )
        sso_manager = SSOManager(config)
    return sso_manager


__all__ = [
    "NotificationProvider",
    "NotificationEvent",
    "EventType",
    "SlackNotifier",
    "TeamsNotifier",
    "TelegramNotifier",
    "WhatsAppNotifier",
    "EmailNotifier",
    "create_email_notifier",
    "WebhookNotifier",
    "create_webhook_notifier",
    "AlertDeduplicator",
    "EscalationLadder",
    "EscalationLevel",
    "EscalationTarget",
    "EscalationRule",
    "DEFAULT_ESCALATION_RULES",
    "daily_digest_loop",
    "NotificationManager",
    "setup_notifications",
    "get_notification_manager",
    "emit_quota_exceeded",
    "emit_quota_warning",
    "emit_approval_requested",
    "emit_approval_resolved",
    "emit_vacation_status_change",
    "emit_token_transfer",
    "sso_manager",
    "setup_sso",
]
