"""
Alfred Integrations
External service integrations for notifications and webhooks.
"""

from .base import NotificationProvider, NotificationEvent, EventType
from .slack import SlackNotifier
from .teams import TeamsNotifier
from .telegram import TelegramNotifier
from .whatsapp import WhatsAppNotifier
from .manager import (
    NotificationManager,
    setup_notifications,
    get_notification_manager,
    emit_quota_exceeded,
    emit_quota_warning,
    emit_approval_requested,
    emit_approval_resolved,
    emit_vacation_status_change,
    emit_token_transfer,
)

__all__ = [
    "NotificationProvider",
    "NotificationEvent",
    "EventType",
    "SlackNotifier",
    "TeamsNotifier",
    "TelegramNotifier",
    "WhatsAppNotifier",
    "NotificationManager",
    "setup_notifications",
    "get_notification_manager",
    "emit_quota_exceeded",
    "emit_quota_warning",
    "emit_approval_requested",
    "emit_approval_resolved",
    "emit_vacation_status_change",
    "emit_token_transfer",
]
