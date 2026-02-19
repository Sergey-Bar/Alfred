"""
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L1
Logic:       Configurable webhook notification provider.
             POSTs JSON event payloads to user-defined URLs
             with HMAC-SHA256 signature, retry with backoff.
Root Cause:  Sprint task T077 — Webhook notifications.
Context:     Plugs into NotificationManager for arbitrary
             HTTP integrations (PagerDuty, Zapier, custom).
Suitability: L1 — standard HTTP POST with retry.
──────────────────────────────────────────────────────────────

Alfred Webhook Notification Provider
Send notifications via configurable HTTP POST webhooks.
"""

import hashlib
import hmac
import json
import logging
import time
from typing import Any, Dict, List, Optional

import httpx

from .base import EventType, NotificationEvent, NotificationProvider

logger = logging.getLogger(__name__)


class WebhookNotifier(NotificationProvider):
    """
    Webhook notification provider.

    Sends JSON payloads to configurable HTTP endpoints with:
    - HMAC-SHA256 request signing (X-Alfred-Signature header)
    - Exponential backoff retry (configurable max retries)
    - Configurable timeout per endpoint
    - Event type filtering per webhook

    Configuration:
        WEBHOOK_URL:    Target endpoint URL
        WEBHOOK_SECRET: HMAC signing secret (optional)
    """

    def __init__(
        self,
        url: str,
        secret: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
        timeout: float = 10.0,
        event_filter: Optional[List[EventType]] = None,
        webhook_name: str = "default",
    ):
        """
        Args:
            url:          Target webhook URL.
            secret:       HMAC-SHA256 signing secret. If set, adds
                          X-Alfred-Signature to every request.
            headers:      Additional HTTP headers.
            max_retries:  Max retry attempts on failure.
            timeout:      Request timeout in seconds.
            event_filter: If set, only these event types are sent.
            webhook_name: Human label for logging.
        """
        self._url = url
        self._secret = secret
        self._extra_headers = headers or {}
        self._max_retries = max_retries
        self._timeout = timeout
        self._event_filter = set(event_filter) if event_filter else None
        self._webhook_name = webhook_name
        self._client = httpx.AsyncClient(timeout=self._timeout)

    @property
    def name(self) -> str:
        return f"webhook:{self._webhook_name}"

    @property
    def is_configured(self) -> bool:
        return bool(self._url)

    def supports_event(self, event_type: EventType) -> bool:
        if self._event_filter is None:
            return True
        return event_type in self._event_filter

    def _sign_payload(self, payload_bytes: bytes) -> str:
        """Compute HMAC-SHA256 signature."""
        return hmac.new(
            self._secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

    def _build_payload(self, event: NotificationEvent) -> Dict[str, Any]:
        """Build the webhook JSON payload."""
        return {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "severity": event.severity,
            "title": event.title,
            "message": event.message,
            "user_id": event.user_id,
            "user_email": event.user_email,
            "user_name": event.user_name,
            "team_id": event.team_id,
            "team_name": event.team_name,
            "data": event.data,
            "timestamp": event.timestamp.isoformat(),
            "source": "alfred",
        }

    async def send(self, event: NotificationEvent) -> bool:
        """Send a webhook POST with retry + backoff."""
        payload = self._build_payload(event)
        payload_bytes = json.dumps(payload, default=str).encode("utf-8")

        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "X-Alfred-Event": event.event_type.value,
            "X-Alfred-Event-ID": event.event_id,
            **self._extra_headers,
        }

        if self._secret:
            headers["X-Alfred-Signature"] = f"sha256={self._sign_payload(payload_bytes)}"

        last_error: Optional[str] = None
        for attempt in range(1, self._max_retries + 1):
            try:
                resp = await self._client.post(
                    self._url,
                    content=payload_bytes,
                    headers=headers,
                )
                if 200 <= resp.status_code < 300:
                    logger.info(
                        f"webhook:{self._webhook_name}: delivered event "
                        f"{event.event_id} (attempt {attempt})"
                    )
                    return True
                else:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
                    logger.warning(
                        f"webhook:{self._webhook_name}: attempt {attempt} "
                        f"failed: {last_error}"
                    )
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"webhook:{self._webhook_name}: attempt {attempt} "
                    f"exception: {last_error}"
                )

            # Exponential backoff: 1s, 2s, 4s ...
            if attempt < self._max_retries:
                backoff = 2 ** (attempt - 1)
                import asyncio
                await asyncio.sleep(backoff)

        logger.error(
            f"webhook:{self._webhook_name}: exhausted {self._max_retries} retries "
            f"for event {event.event_id}: {last_error}"
        )
        return False

    async def send_batch(self, events: List[NotificationEvent]) -> Dict[str, bool]:
        """Send multiple events sequentially."""
        results = {}
        for event in events:
            results[event.event_id] = await self.send(event)
        return results

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()


def create_webhook_notifier(
    url: str,
    secret: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    max_retries: int = 3,
    timeout: float = 10.0,
    event_filter: Optional[List[EventType]] = None,
    webhook_name: str = "default",
) -> WebhookNotifier:
    """Factory function for creating a WebhookNotifier."""
    return WebhookNotifier(
        url=url,
        secret=secret,
        headers=headers,
        max_retries=max_retries,
        timeout=timeout,
        event_filter=event_filter,
        webhook_name=webhook_name,
    )
