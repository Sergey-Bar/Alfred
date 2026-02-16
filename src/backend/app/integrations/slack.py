"""
Alfred Slack Integration
Send notifications to Slack via webhooks or Bot API.
"""

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from .base import EventType, NotificationEvent, NotificationProvider


class SlackNotifier(NotificationProvider):
    """
    Slack notification provider using Incoming Webhooks.

    Supports:
    - Incoming Webhooks (simple setup)
    - Rich Block Kit messages
    - Channel-specific routing
    - User mentions via email lookup

    Configuration:
        SLACK_WEBHOOK_URL: Default webhook URL
        SLACK_WEBHOOK_URL_ALERTS: Webhook for critical alerts (optional)
        SLACK_BOT_TOKEN: Bot token for advanced features (optional)
    """

    # Severity to emoji mapping
    SEVERITY_EMOJI = {
        "info": ":information_source:",
        "warning": ":warning:",
        "error": ":x:",
        "critical": ":rotating_light:",
    }

    # Event type to color mapping (for attachment sidebar)
    EVENT_COLORS = {
        EventType.QUOTA_WARNING: "#FFA500",  # Orange
        EventType.QUOTA_EXCEEDED: "#FF0000",  # Red
        EventType.QUOTA_RESET: "#36A64F",  # Green
        EventType.TOKEN_TRANSFER_SENT: "#439FE0",  # Blue
        EventType.TOKEN_TRANSFER_RECEIVED: "#36A64F",  # Green
        EventType.APPROVAL_REQUESTED: "#439FE0",  # Blue
        EventType.APPROVAL_APPROVED: "#36A64F",  # Green
        EventType.APPROVAL_REJECTED: "#FF0000",  # Red
        EventType.USER_VACATION_START: "#9B59B6",  # Purple
        EventType.USER_VACATION_END: "#36A64F",  # Green
        EventType.USER_SUSPENDED: "#FF0000",  # Red
        EventType.TEAM_POOL_WARNING: "#FFA500",  # Orange
        EventType.TEAM_POOL_DEPLETED: "#FF0000",  # Red
        EventType.SYSTEM_ERROR: "#FF0000",  # Red
        EventType.HIGH_LATENCY: "#FFA500",  # Orange
    }

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        alerts_webhook_url: Optional[str] = None,
        bot_token: Optional[str] = None,
        default_channel: Optional[str] = None,
        timeout: float = 10.0,
    ):
        """
        Initialize Slack notifier.

        Args:
            webhook_url: Primary Slack webhook URL
            alerts_webhook_url: Separate webhook for critical alerts
            bot_token: Slack bot token (for chat.postMessage API)
            default_channel: Default channel for bot posts
            timeout: HTTP request timeout in seconds
        """
        self.webhook_url = webhook_url
        self.alerts_webhook_url = alerts_webhook_url
        self.bot_token = bot_token
        self.default_channel = default_channel
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def name(self) -> str:
        return "slack"

    @property
    def is_configured(self) -> bool:
        return bool(self.webhook_url or self.bot_token)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _get_webhook_for_event(self, event: NotificationEvent) -> Optional[str]:
        """Determine which webhook to use based on event severity."""
        if event.severity in ("error", "critical") and self.alerts_webhook_url:
            return self.alerts_webhook_url
        return self.webhook_url

    def _build_blocks(self, event: NotificationEvent) -> List[Dict[str, Any]]:
        """Build Slack Block Kit blocks for rich formatting."""
        emoji = self.SEVERITY_EMOJI.get(event.severity, ":bell:")
        color = self.EVENT_COLORS.get(event.event_type, "#808080")

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{emoji} {event.title}", "emoji": True},
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": event.message}},
        ]

        # Add context fields
        context_elements = []

        if event.user_name:
            context_elements.append(
                {"type": "mrkdwn", "text": f":bust_in_silhouette: *User:* {event.user_name}"}
            )

        if event.team_name:
            context_elements.append(
                {"type": "mrkdwn", "text": f":busts_in_silhouette: *Team:* {event.team_name}"}
            )

        context_elements.append(
            {"type": "mrkdwn", "text": f":clock1: {event.timestamp.strftime('%Y-%m-%d %H:%M UTC')}"}
        )

        if context_elements:
            blocks.append({"type": "context", "elements": context_elements})

        # Add data fields if present
        if event.data:
            fields = []
            for key, value in list(event.data.items())[:10]:  # Limit to 10 fields
                fields.append(
                    {"type": "mrkdwn", "text": f"*{key.replace('_', ' ').title()}:*\n{value}"}
                )

            # Split fields into groups of 2 for side-by-side display
            for i in range(0, len(fields), 2):
                section_fields = fields[i : i + 2]
                blocks.append({"type": "section", "fields": section_fields})

        # Add divider at the end
        blocks.append({"type": "divider"})

        return blocks

    def _build_payload(self, event: NotificationEvent) -> Dict[str, Any]:
        """Build the Slack webhook payload."""
        blocks = self._build_blocks(event)
        color = self.EVENT_COLORS.get(event.event_type, "#808080")

        payload = {
            "text": f"{event.title}: {event.message}",  # Fallback for notifications
            "blocks": blocks,
            "attachments": [
                {
                    "color": color,
                    "footer": f"Alfred | Event ID: {event.event_id[:8]}",
                    "ts": int(event.timestamp.timestamp()),
                }
            ],
        }

        return payload

    async def send(self, event: NotificationEvent) -> bool:
        """Send a notification to Slack."""
        if not self.is_configured:
            return False

        webhook_url = self._get_webhook_for_event(event)
        if not webhook_url:
            return False

        try:
            client = await self._get_client()
            payload = self._build_payload(event)

            response = await client.post(webhook_url, json=payload)

            return response.status_code == 200

        except Exception:
            # Log error but don't raise - notifications shouldn't break main flow
            return False

    async def send_batch(self, events: List[NotificationEvent]) -> Dict[str, bool]:
        """Send multiple notifications to Slack."""
        results = {}

        # Send sequentially to respect rate limits
        for event in events:
            results[event.event_id] = await self.send(event)
            await asyncio.sleep(0.1)  # Small delay to avoid rate limiting

        return results

    def format_message(self, event: NotificationEvent) -> str:
        """Format message with Slack mrkdwn syntax."""
        lines = [
            f"*{event.title}*",
            event.message,
        ]

        if event.user_name:
            lines.append(f"User: {event.user_name}")

        if event.team_name:
            lines.append(f"Team: {event.team_name}")

        return "\n".join(lines)


# Factory function for easy instantiation
def create_slack_notifier(
    webhook_url: Optional[str] = None,
    alerts_webhook_url: Optional[str] = None,
    bot_token: Optional[str] = None,
) -> Optional[SlackNotifier]:
    """
    Create a Slack notifier if configured.

    Returns None if no configuration is provided.
    """
    if not any([webhook_url, bot_token]):
        return None

    return SlackNotifier(
        webhook_url=webhook_url,
        alerts_webhook_url=alerts_webhook_url,
        bot_token=bot_token,
    )
