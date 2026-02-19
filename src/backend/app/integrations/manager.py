# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: NotificationManager is the central orchestrator for all notification providers (Slack, Teams, Telegram, WhatsApp), supporting pub/sub, event filtering, async batch sending, and graceful error handling.
# Why: Unifies notification logic, enabling extensible, maintainable, and robust event-driven notifications across multiple channels.
# Root Cause: Scattered notification logic leads to missed alerts, code duplication, and poor reliability.
# Context: Used by Alfred to send quota, audit, and system notifications. Future: add retry/backoff, provider health checks, and dynamic config.
# Model Suitability: For event-driven notification orchestration, GPT-4.1 is sufficient.
"""
Alfred Notification Manager
Central coordinator for all notification providers with pub/sub event system.
"""

import asyncio
import logging
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Set

from .base import (
    EventType,
    NotificationEvent,
    NotificationProvider,
    NotificationResult,
)
from .slack import create_slack_notifier
from .teams import create_teams_notifier
from .telegram import create_telegram_notifier

logger = logging.getLogger(__name__)

# Type alias for event handlers
EventHandler = Callable[[NotificationEvent], None]


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Implements event-driven notification manager with provider registration, event filtering, async batch sending, and pub/sub for custom handlers.
# Why: Centralizes notification logic for maintainability, extensibility, and reliability.
# Root Cause: Ad-hoc notification code is error-prone and hard to extend.
# Context: Used for quota, audit, and system events. Future: add persistent retry queue and metrics.
# Model Suitability: Notification manager logic is standard; GPT-4.1 is sufficient.
class NotificationManager:
    """
    Central notification manager with pub/sub event system.

    Features:
    - Multiple notification providers (Slack, Teams, etc.)
    - Event type filtering per provider
    - Async batch sending
    - Event subscription system
    - Graceful degradation on failures

    Usage:
        manager = NotificationManager()
        manager.add_provider(SlackNotifier(webhook_url="..."))
        manager.add_provider(TeamsNotifier(webhook_url="..."))

        # Subscribe to events
        @manager.on(EventType.QUOTA_EXCEEDED)
        def handle_quota_exceeded(event):
            logger.warning("Quota exceeded for %s", event.user_name)

        # Emit events
        await manager.emit(NotificationEvent(
            event_type=EventType.QUOTA_EXCEEDED,
            title="Quota Exceeded",
            message="Your quota has been exceeded",
            user_name="John Doe"
        ))
    """

    def __init__(self):
        self._providers: List[NotificationProvider] = []
        self._subscribers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._global_subscribers: List[EventHandler] = []
        self._event_filters: Dict[str, Set[EventType]] = {}
        self._enabled = True
        self._failed_events: List[NotificationEvent] = []  # For retry logic
        self._max_retry_queue = 100

    @property
    def providers(self) -> List[NotificationProvider]:
        """Get list of registered providers."""
        return self._providers.copy()

    @property
    def configured_providers(self) -> List[NotificationProvider]:
        """Get list of configured (ready to use) providers."""
        return [p for p in self._providers if p.is_configured]

    def add_provider(
        self, provider: NotificationProvider, event_filter: Optional[Set[EventType]] = None
    ) -> None:
        """
        Register a notification provider.

        Args:
            provider: The notification provider instance
            event_filter: Optional set of event types this provider should handle.
                         If None, handles all events.
        """
        self._providers.append(provider)
        if event_filter:
            self._event_filters[provider.name] = event_filter

    def remove_provider(self, provider_name: str) -> bool:
        """
        Remove a provider by name.

        Returns:
            True if removed, False if not found
        """
        for i, p in enumerate(self._providers):
            if p.name == provider_name:
                self._providers.pop(i)
                self._event_filters.pop(provider_name, None)
                return True
        return False

    def _should_notify_provider(
        self, provider: NotificationProvider, event: NotificationEvent
    ) -> bool:
        """Check if a provider should handle this event."""
        # Check provider-level support
        if not provider.supports_event(event.event_type):
            return False

        # Check event filter
        if provider.name in self._event_filters:
            if event.event_type not in self._event_filters[provider.name]:
                return False

        return True

    def on(self, *event_types: EventType) -> Callable:
        """
        Decorator to subscribe to specific event types.

        Usage:
            @manager.on(EventType.QUOTA_EXCEEDED, EventType.QUOTA_WARNING)
            def handle_quota_events(event):
                logger.info("Quota event: %s", event.title)
        """

        def decorator(handler: EventHandler) -> EventHandler:
            if not event_types:
                # Subscribe to all events
                self._global_subscribers.append(handler)
            else:
                for event_type in event_types:
                    self._subscribers[event_type].append(handler)
            return handler

        return decorator

    def subscribe(
        self, handler: EventHandler, event_types: Optional[List[EventType]] = None
    ) -> None:
        """
        Subscribe a handler to events.

        Args:
            handler: The callback function
            event_types: List of event types to subscribe to. If None, subscribes to all.
        """
        if event_types is None:
            self._global_subscribers.append(handler)
        else:
            for event_type in event_types:
                self._subscribers[event_type].append(handler)

    def unsubscribe(
        self, handler: EventHandler, event_types: Optional[List[EventType]] = None
    ) -> None:
        """
        Unsubscribe a handler from events.

        Args:
            handler: The callback function to remove
            event_types: List of event types to unsubscribe from. If None, removes from all.
        """
        if event_types is None:
            if handler in self._global_subscribers:
                self._global_subscribers.remove(handler)
            for subscribers in self._subscribers.values():
                if handler in subscribers:
                    subscribers.remove(handler)
        else:
            for event_type in event_types:
                if handler in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(handler)

    def _notify_subscribers(self, event: NotificationEvent) -> None:
        """Call all subscribed handlers for an event."""
        # Global subscribers
        for handler in self._global_subscribers:
            try:
                handler(event)
            except Exception:
                pass  # Don't let one handler break others

        # Event-specific subscribers
        for handler in self._subscribers.get(event.event_type, []):
            try:
                handler(event)
            except Exception:
                pass

    async def emit(
        self, event: NotificationEvent, providers: Optional[List[str]] = None
    ) -> Dict[str, NotificationResult]:
        """
        Emit a notification event to all (or specified) providers.

        Args:
            event: The notification event to send
            providers: Optional list of provider names to send to.
                      If None, sends to all configured providers.

        Returns:
            Dict mapping provider name to result
        """
        if not self._enabled:
            return {}

        results = {}

        # Notify local subscribers first (sync)
        self._notify_subscribers(event)

        # Filter providers
        target_providers = self.configured_providers
        if providers:
            target_providers = [p for p in target_providers if p.name in providers]

        # Send to each provider
        for provider in target_providers:
            if not self._should_notify_provider(provider, event):
                continue

            try:
                success = await provider.send(event)
                results[provider.name] = NotificationResult(
                    provider=provider.name,
                    event_id=event.event_id,
                    success=success,
                    error=None if success else "Send returned False",
                )
            except Exception as e:
                results[provider.name] = NotificationResult(
                    provider=provider.name, event_id=event.event_id, success=False, error=str(e)
                )

        # Track failed events for potential retry
        failed_providers = [name for name, result in results.items() if not result.success]
        if failed_providers and len(self._failed_events) < self._max_retry_queue:
            self._failed_events.append(event)

        return results

    async def emit_batch(
        self, events: List[NotificationEvent], providers: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, NotificationResult]]:
        """
        Emit multiple events to providers.

        Args:
            events: List of events to send
            providers: Optional list of provider names

        Returns:
            Dict mapping event_id to Dict mapping provider name to result
        """
        all_results = {}

        for event in events:
            results = await self.emit(event, providers)
            all_results[event.event_id] = results

        return all_results

    async def retry_failed(self) -> int:
        """
        Retry sending failed events.

        Returns:
            Number of events successfully retried
        """
        if not self._failed_events:
            return 0

        events_to_retry = self._failed_events.copy()
        self._failed_events.clear()

        success_count = 0
        for event in events_to_retry:
            results = await self.emit(event)
            if all(r.success for r in results.values()):
                success_count += 1

        return success_count

    def enable(self) -> None:
        """Enable notifications."""
        self._enabled = True

    def disable(self) -> None:
        """Disable notifications (useful for testing)."""
        self._enabled = False

    async def close(self) -> None:
        """Close all provider connections."""
        for provider in self._providers:
            close_method = getattr(provider, "close", None)
            if close_method and asyncio.iscoroutinefunction(close_method):
                await close_method()


# Global notification manager instance
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """Get the global notification manager instance."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


def setup_notifications(
    slack_webhook_url: Optional[str] = None,
    slack_alerts_webhook_url: Optional[str] = None,
    slack_bot_token: Optional[str] = None,
    teams_webhook_url: Optional[str] = None,
    teams_alerts_webhook_url: Optional[str] = None,
    telegram_bot_token: Optional[str] = None,
    telegram_chat_id: Optional[str] = None,
    telegram_alerts_chat_id: Optional[str] = None,
    whatsapp_phone_number_id: Optional[str] = None,
    whatsapp_access_token: Optional[str] = None,
    whatsapp_recipient_number: Optional[str] = None,
    whatsapp_alerts_recipient_number: Optional[str] = None,
    whatsapp_template_name: Optional[str] = None,
) -> NotificationManager:
    """
    Setup notification manager with providers from configuration.

    Args:
        slack_webhook_url: Slack incoming webhook URL
        slack_alerts_webhook_url: Slack webhook for critical alerts
        slack_bot_token: Slack bot token (optional)
        teams_webhook_url: MS Teams incoming webhook URL
        teams_alerts_webhook_url: Teams webhook for critical alerts
        telegram_bot_token: Telegram bot token from @BotFather
        telegram_chat_id: Default Telegram chat/group ID
        telegram_alerts_chat_id: Separate chat for critical alerts
        whatsapp_phone_number_id: WhatsApp Business Phone Number ID
        whatsapp_access_token: Meta Graph API access token
        whatsapp_recipient_number: Default recipient phone number
        whatsapp_alerts_recipient_number: Separate number for critical alerts
        whatsapp_template_name: Pre-approved template name

    Returns:
        Configured NotificationManager instance
    """
    manager = get_notification_manager()

    # Setup Slack
    slack_notifier = create_slack_notifier(
        webhook_url=slack_webhook_url,
        alerts_webhook_url=slack_alerts_webhook_url,
        bot_token=slack_bot_token,
    )
    if slack_notifier:
        manager.add_provider(slack_notifier)

    # Setup Teams
    teams_notifier = create_teams_notifier(
        webhook_url=teams_webhook_url,
        alerts_webhook_url=teams_alerts_webhook_url,
    )
    if teams_notifier:
        manager.add_provider(teams_notifier)

    # Setup Telegram
    telegram_notifier = create_telegram_notifier(
        bot_token=telegram_bot_token,
        chat_id=telegram_chat_id,
        alerts_chat_id=telegram_alerts_chat_id,
    )
    if telegram_notifier:
        manager.add_provider(telegram_notifier)

    # Setup WhatsApp
    # whatsapp_notifier = create_whatsapp_notifier(
    #     phone_number_id=whatsapp_phone_number_id,
    #     access_token=whatsapp_access_token,
    #     recipient_number=whatsapp_recipient_number,
    #     alerts_recipient_number=whatsapp_alerts_recipient_number,
    #     template_name=whatsapp_template_name,
    # )
    # if whatsapp_notifier:
    #     manager.add_provider(whatsapp_notifier)

    return manager


# Convenience functions for emitting common events


async def emit_quota_warning(
    user_id: str,
    user_name: str,
    user_email: str,
    quota_remaining: float,
    quota_total: float,
    percentage_used: float,
) -> Dict[str, NotificationResult]:
    """Emit a quota warning notification."""
    manager = get_notification_manager()

    event = NotificationEvent(
        event_type=EventType.QUOTA_WARNING,
        title="Quota Warning",
        message=f"{user_name} has used {percentage_used:.1f}% of their quota",
        user_id=user_id,
        user_name=user_name,
        user_email=user_email,
        severity="warning",
        data={
            "quota_remaining": f"{quota_remaining:.2f} credits",
            "quota_total": f"{quota_total:.2f} credits",
            "percentage_used": f"{percentage_used:.1f}%",
        },
    )

    return await manager.emit(event)


async def emit_quota_exceeded(
    user_id: str,
    user_name: str,
    user_email: str,
    requested_credits: float,
    available_credits: float,
) -> Dict[str, NotificationResult]:
    """Emit a quota exceeded notification."""
    manager = get_notification_manager()

    event = NotificationEvent(
        event_type=EventType.QUOTA_EXCEEDED,
        title="Quota Exceeded",
        message=f"{user_name}'s request was denied due to insufficient quota",
        user_id=user_id,
        user_name=user_name,
        user_email=user_email,
        severity="error",
        data={
            "requested_credits": f"{requested_credits:.2f}",
            "available_credits": f"{available_credits:.2f}",
            "shortfall": f"{(requested_credits - available_credits):.2f}",
        },
    )

    return await manager.emit(event)


async def emit_approval_requested(
    user_id: str,
    user_name: str,
    user_email: str,
    requested_credits: float,
    reason: str,
    team_name: Optional[str] = None,
) -> Dict[str, NotificationResult]:
    """Emit an approval request notification."""
    manager = get_notification_manager()

    event = NotificationEvent(
        event_type=EventType.APPROVAL_REQUESTED,
        title="Approval Request",
        message=f"{user_name} is requesting {requested_credits:.2f} additional credits",
        user_id=user_id,
        user_name=user_name,
        user_email=user_email,
        team_name=team_name,
        severity="info",
        data={"requested_credits": f"{requested_credits:.2f}", "reason": reason},
    )

    return await manager.emit(event)


async def emit_approval_resolved(
    user_id: str,
    user_name: str,
    user_email: str,
    approved: bool,
    credits: float,
    approver_name: str,
    reason: Optional[str] = None,
) -> Dict[str, NotificationResult]:
    """Emit an approval resolution notification."""
    manager = get_notification_manager()

    event_type = EventType.APPROVAL_APPROVED if approved else EventType.APPROVAL_REJECTED
    status = "approved" if approved else "rejected"
    severity = "info" if approved else "warning"

    event = NotificationEvent(
        event_type=event_type,
        title=f"Approval {status.title()}",
        message=f"{user_name}'s quota request was {status} by {approver_name}",
        user_id=user_id,
        user_name=user_name,
        user_email=user_email,
        severity=severity,
        data={
            "credits": f"{credits:.2f}",
            "approver": approver_name,
            "status": status,
            **({"rejection_reason": reason} if reason and not approved else {}),
        },
    )

    return await manager.emit(event)


async def emit_vacation_status_change(
    user_id: str,
    user_name: str,
    user_email: str,
    on_vacation: bool,
    team_name: Optional[str] = None,
) -> Dict[str, NotificationResult]:
    """Emit a vacation status change notification."""
    manager = get_notification_manager()

    event_type = EventType.USER_VACATION_START if on_vacation else EventType.USER_VACATION_END
    action = "started vacation" if on_vacation else "returned from vacation"

    event = NotificationEvent(
        event_type=event_type,
        title="Vacation Status Update",
        message=f"{user_name} has {action}",
        user_id=user_id,
        user_name=user_name,
        user_email=user_email,
        team_name=team_name,
        severity="info",
        data={
            "status": "on_vacation" if on_vacation else "active",
            "vacation_sharing": "enabled" if on_vacation else "disabled",
        },
    )

    return await manager.emit(event)


async def emit_token_transfer(
    sender_id: str,
    sender_name: str,
    sender_email: str,
    recipient_id: str,
    recipient_name: str,
    recipient_email: str,
    amount: float,
    message: Optional[str] = None,
    sender_remaining: Optional[float] = None,
    recipient_new_total: Optional[float] = None,
) -> Dict[str, NotificationResult]:
    """
    Emit credit reallocation notifications to both sender and recipient.

    Sends two notifications:
    1. TOKEN_TRANSFER_SENT to sender (credits reallocated out)
    2. TOKEN_TRANSFER_RECEIVED to recipient (credits received)
    """
    manager = get_notification_manager()
    results = {}

    # Notification for sender
    sent_event = NotificationEvent(
        event_type=EventType.TOKEN_TRANSFER_SENT,
        title="Credits Reallocated",
        message=f"You reallocated {amount:.2f} credits to {recipient_name}",
        user_id=sender_id,
        user_name=sender_name,
        user_email=sender_email,
        severity="info",
        data={
            "amount": f"{amount:.2f}",
            "recipient_name": recipient_name,
            "recipient_email": recipient_email,
            **(
                {"remaining_quota": f"{sender_remaining:.2f}"}
                if sender_remaining is not None
                else {}
            ),
            **({"message": message} if message else {}),
        },
    )

    # Notification for recipient
    received_event = NotificationEvent(
        event_type=EventType.TOKEN_TRANSFER_RECEIVED,
        title="Credits Received",
        message=f"You received {amount:.2f} credits from {sender_name}",
        user_id=recipient_id,
        user_name=recipient_name,
        user_email=recipient_email,
        severity="info",
        data={
            "amount": f"{amount:.2f}",
            "sender_name": sender_name,
            "sender_email": sender_email,
            **(
                {"new_quota_total": f"{recipient_new_total:.2f}"}
                if recipient_new_total is not None
                else {}
            ),
            **({"message": message} if message else {}),
        },
    )

    # Emit both events
    sent_results = await manager.emit(sent_event)
    received_results = await manager.emit(received_event)

    results.update({f"sent_{k}": v for k, v in sent_results.items()})
    results.update({f"received_{k}": v for k, v in received_results.items()})

    return results
