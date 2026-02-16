"""
Alfred Telegram Integration
Send notifications to Telegram via Bot API.
"""

import asyncio
from typing import Dict, List, Optional

import httpx

from .base import EventType, NotificationEvent, NotificationProvider


class TelegramNotifier(NotificationProvider):
    """
    Telegram notification provider using Bot API.

    Supports:
    - Bot API for sending messages
    - Markdown formatting
    - Chat/Group/Channel targeting
    - Silent notifications

    Configuration:
        TELEGRAM_BOT_TOKEN: Bot token from @BotFather
        TELEGRAM_CHAT_ID: Default chat/group/channel ID
        TELEGRAM_ALERTS_CHAT_ID: Separate chat for critical alerts (optional)

    Setup:
        1. Create a bot via @BotFather on Telegram
        2. Get the bot token
        3. Add the bot to your group/channel
        4. Get the chat ID (use @userinfobot or the getUpdates API)
    """

    TELEGRAM_API_BASE = "https://api.telegram.org/bot"

    # Severity to emoji mapping
    SEVERITY_EMOJI = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "critical": "🚨",
    }

    # Event type to emoji mapping
    EVENT_EMOJI = {
        EventType.QUOTA_WARNING: "⚠️",
        EventType.QUOTA_EXCEEDED: "🚫",
        EventType.QUOTA_RESET: "✅",
        EventType.TOKEN_TRANSFER_SENT: "💸",
        EventType.TOKEN_TRANSFER_RECEIVED: "🎁",
        EventType.APPROVAL_REQUESTED: "📝",
        EventType.APPROVAL_APPROVED: "✅",
        EventType.APPROVAL_REJECTED: "❌",
        EventType.USER_VACATION_START: "🏖️",
        EventType.USER_VACATION_END: "👋",
        EventType.USER_SUSPENDED: "🔒",
        EventType.TEAM_POOL_WARNING: "⚠️",
        EventType.TEAM_POOL_DEPLETED: "🚫",
        EventType.SYSTEM_ERROR: "🔴",
        EventType.HIGH_LATENCY: "🐢",
    }

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        alerts_chat_id: Optional[str] = None,
        parse_mode: str = "MarkdownV2",
        disable_notification: bool = False,
        timeout: float = 10.0,
    ):
        """
        Initialize Telegram notifier.

        Args:
            bot_token: Telegram bot token from @BotFather
            chat_id: Default chat ID to send messages to
            alerts_chat_id: Separate chat ID for critical alerts
            parse_mode: Message parse mode (MarkdownV2, HTML, Markdown)
            disable_notification: Send messages silently
            timeout: HTTP request timeout in seconds
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.alerts_chat_id = alerts_chat_id
        self.parse_mode = parse_mode
        self.disable_notification = disable_notification
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def name(self) -> str:
        return "telegram"

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    @property
    def api_url(self) -> str:
        """Get the Telegram API base URL for this bot."""
        return f"{self.TELEGRAM_API_BASE}{self.bot_token}"

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _get_chat_for_event(self, event: NotificationEvent) -> Optional[str]:
        """Determine which chat to use based on event severity."""
        if event.severity in ("error", "critical") and self.alerts_chat_id:
            return self.alerts_chat_id
        return self.chat_id

    def _escape_markdown(self, text: str) -> str:
        """Escape special characters for MarkdownV2."""
        # Characters that need escaping in MarkdownV2
        special_chars = [
            "_",
            "*",
            "[",
            "]",
            "(",
            ")",
            "~",
            "`",
            ">",
            "#",
            "+",
            "-",
            "=",
            "|",
            "{",
            "}",
            ".",
            "!",
        ]
        for char in special_chars:
            text = text.replace(char, f"\\{char}")
        return text

    def _format_message(self, event: NotificationEvent) -> str:
        """Format the notification message for Telegram."""
        emoji = self.EVENT_EMOJI.get(event.event_type, "📢")
        severity_emoji = self.SEVERITY_EMOJI.get(event.severity, "ℹ️")

        # Escape text for MarkdownV2
        title = self._escape_markdown(event.title)
        message = self._escape_markdown(event.message)

        lines = [
            f"{emoji} *{title}*",
            "",
            message,
            "",
        ]

        # Add metadata
        if event.user_name:
            user_name = self._escape_markdown(event.user_name)
            lines.append(f"👤 *User:* {user_name}")

        if event.team_name:
            team_name = self._escape_markdown(event.team_name)
            lines.append(f"👥 *Team:* {team_name}")

        # Add data fields
        if event.data:
            lines.append("")
            lines.append("*Details:*")
            for key, value in list(event.data.items())[:6]:
                key_escaped = self._escape_markdown(key.replace("_", " ").title())
                value_escaped = self._escape_markdown(str(value))
                lines.append(f"• {key_escaped}: `{value_escaped}`")

        # Footer
        lines.append("")
        timestamp = event.timestamp.strftime("%Y\\-%m\\-%d %H:%M UTC")
        event_id = self._escape_markdown(event.event_id[:8])
        lines.append(f"_{severity_emoji} {event.severity.upper()} \\| {timestamp}_")
        lines.append(f"_Alfred \\| Event: {event_id}_")

        return "\n".join(lines)

    def _format_message_html(self, event: NotificationEvent) -> str:
        """Format the notification message as HTML (fallback)."""
        emoji = self.EVENT_EMOJI.get(event.event_type, "📢")
        severity_emoji = self.SEVERITY_EMOJI.get(event.severity, "ℹ️")

        lines = [
            f"{emoji} <b>{event.title}</b>",
            "",
            event.message,
            "",
        ]

        if event.user_name:
            lines.append(f"👤 <b>User:</b> {event.user_name}")

        if event.team_name:
            lines.append(f"👥 <b>Team:</b> {event.team_name}")

        if event.data:
            lines.append("")
            lines.append("<b>Details:</b>")
            for key, value in list(event.data.items())[:6]:
                lines.append(f"• {key.replace('_', ' ').title()}: <code>{value}</code>")

        lines.append("")
        timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M UTC")
        lines.append(f"<i>{severity_emoji} {event.severity.upper()} | {timestamp}</i>")
        lines.append(f"<i>Alfred | Event: {event.event_id[:8]}</i>")

        return "\n".join(lines)

    async def send(self, event: NotificationEvent) -> bool:
        """Send a notification to Telegram."""
        if not self.is_configured:
            return False

        chat_id = self._get_chat_for_event(event)
        if not chat_id:
            return False

        try:
            client = await self._get_client()

            # Try MarkdownV2 first, fall back to HTML if it fails
            text = self._format_message(event)
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "MarkdownV2",
                "disable_notification": self.disable_notification,
            }

            response = await client.post(f"{self.api_url}/sendMessage", json=payload)

            if response.status_code == 200:
                result = response.json()
                return result.get("ok", False)

            # Fallback to HTML if MarkdownV2 fails
            if response.status_code == 400:
                text_html = self._format_message_html(event)
                payload["text"] = text_html
                payload["parse_mode"] = "HTML"

                fallback_response = await client.post(f"{self.api_url}/sendMessage", json=payload)

                if fallback_response.status_code == 200:
                    result = fallback_response.json()
                    return result.get("ok", False)

            return False

        except Exception:
            return False

    async def send_batch(self, events: List[NotificationEvent]) -> Dict[str, bool]:
        """Send multiple notifications to Telegram."""
        results = {}

        for event in events:
            results[event.event_id] = await self.send(event)
            await asyncio.sleep(0.05)  # Telegram allows ~30 messages/second

        return results

    def format_message(self, event: NotificationEvent) -> str:
        """Format message for Telegram."""
        return self._format_message_html(event)


# Factory function
def create_telegram_notifier(
    bot_token: Optional[str] = None,
    chat_id: Optional[str] = None,
    alerts_chat_id: Optional[str] = None,
) -> Optional[TelegramNotifier]:
    """
    Create a Telegram notifier if configured.

    Returns None if no configuration is provided.
    """
    if not bot_token or not chat_id:
        return None

    return TelegramNotifier(
        bot_token=bot_token,
        chat_id=chat_id,
        alerts_chat_id=alerts_chat_id,
    )
