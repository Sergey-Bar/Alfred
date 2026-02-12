"""
TokenPool Microsoft Teams Integration
Send notifications to Teams via Incoming Webhooks with Adaptive Cards.
"""

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from .base import NotificationProvider, NotificationEvent, EventType


class TeamsNotifier(NotificationProvider):
    """
    Microsoft Teams notification provider using Incoming Webhooks.
    
    Supports:
    - Incoming Webhooks
    - Adaptive Cards for rich formatting
    - Channel-specific routing
    - Action buttons
    
    Configuration:
        TEAMS_WEBHOOK_URL: Default webhook URL
        TEAMS_WEBHOOK_URL_ALERTS: Webhook for critical alerts (optional)
    """
    
    # Severity to color mapping (Adaptive Card accent colors)
    SEVERITY_COLORS = {
        "info": "accent",      # Blue
        "warning": "warning",  # Yellow/Orange
        "error": "attention",  # Red
        "critical": "attention", # Red
    }
    
    # Event type to theme color (hex for MessageCard fallback)
    EVENT_COLORS = {
        EventType.QUOTA_WARNING: "FFA500",
        EventType.QUOTA_EXCEEDED: "FF0000",
        EventType.QUOTA_RESET: "36A64F",
        EventType.TOKEN_TRANSFER_SENT: "439FE0",
        EventType.TOKEN_TRANSFER_RECEIVED: "36A64F",
        EventType.APPROVAL_REQUESTED: "439FE0",
        EventType.APPROVAL_APPROVED: "36A64F",
        EventType.APPROVAL_REJECTED: "FF0000",
        EventType.USER_VACATION_START: "9B59B6",
        EventType.USER_VACATION_END: "36A64F",
        EventType.USER_SUSPENDED: "FF0000",
        EventType.TEAM_POOL_WARNING: "FFA500",
        EventType.TEAM_POOL_DEPLETED: "FF0000",
        EventType.SYSTEM_ERROR: "FF0000",
        EventType.HIGH_LATENCY: "FFA500",
    }
    
    # Event type icons (emoji for display)
    EVENT_ICONS = {
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
        webhook_url: Optional[str] = None,
        alerts_webhook_url: Optional[str] = None,
        timeout: float = 10.0
    ):
        """
        Initialize Teams notifier.
        
        Args:
            webhook_url: Primary Teams webhook URL
            alerts_webhook_url: Separate webhook for critical alerts
            timeout: HTTP request timeout in seconds
        """
        self.webhook_url = webhook_url
        self.alerts_webhook_url = alerts_webhook_url
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def name(self) -> str:
        return "teams"
    
    @property
    def is_configured(self) -> bool:
        return bool(self.webhook_url)
    
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
    
    def _build_adaptive_card(self, event: NotificationEvent) -> Dict[str, Any]:
        """Build an Adaptive Card for Teams."""
        icon = self.EVENT_ICONS.get(event.event_type, "📢")
        color = self.SEVERITY_COLORS.get(event.severity, "accent")
        
        # Build the card body
        body = [
            {
                "type": "TextBlock",
                "text": f"{icon} {event.title}",
                "weight": "bolder",
                "size": "large",
                "wrap": True,
                "style": "heading"
            },
            {
                "type": "TextBlock",
                "text": event.message,
                "wrap": True,
                "spacing": "medium"
            }
        ]
        
        # Add a fact set for metadata
        facts = []
        
        if event.user_name:
            facts.append({
                "title": "User",
                "value": event.user_name
            })
        
        if event.user_email:
            facts.append({
                "title": "Email",
                "value": event.user_email
            })
        
        if event.team_name:
            facts.append({
                "title": "Team",
                "value": event.team_name
            })
        
        facts.append({
            "title": "Time",
            "value": event.timestamp.strftime("%Y-%m-%d %H:%M UTC")
        })
        
        facts.append({
            "title": "Severity",
            "value": event.severity.upper()
        })
        
        if facts:
            body.append({
                "type": "FactSet",
                "facts": facts,
                "spacing": "medium"
            })
        
        # Add additional data if present
        if event.data:
            data_facts = []
            for key, value in list(event.data.items())[:8]:  # Limit fields
                data_facts.append({
                    "title": key.replace("_", " ").title(),
                    "value": str(value)
                })
            
            if data_facts:
                body.append({
                    "type": "TextBlock",
                    "text": "Details",
                    "weight": "bolder",
                    "spacing": "large"
                })
                body.append({
                    "type": "FactSet",
                    "facts": data_facts
                })
        
        # Add footer
        body.append({
            "type": "TextBlock",
            "text": f"Event ID: {event.event_id[:8]} | TokenPool",
            "size": "small",
            "isSubtle": True,
            "spacing": "large",
            "horizontalAlignment": "right"
        })
        
        # Build the adaptive card
        adaptive_card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": body,
            "msteams": {
                "width": "Full"
            }
        }
        
        return adaptive_card
    
    def _build_payload(self, event: NotificationEvent) -> Dict[str, Any]:
        """Build the Teams webhook payload with Adaptive Card."""
        adaptive_card = self._build_adaptive_card(event)
        theme_color = self.EVENT_COLORS.get(event.event_type, "0078D7")
        
        # Teams webhook expects this wrapper format
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": adaptive_card
                }
            ]
        }
        
        return payload
    
    def _build_legacy_payload(self, event: NotificationEvent) -> Dict[str, Any]:
        """Build a legacy MessageCard payload (fallback for older connectors)."""
        theme_color = self.EVENT_COLORS.get(event.event_type, "0078D7")
        icon = self.EVENT_ICONS.get(event.event_type, "📢")
        
        sections = [
            {
                "activityTitle": f"{icon} {event.title}",
                "activitySubtitle": event.timestamp.strftime("%Y-%m-%d %H:%M UTC"),
                "text": event.message,
                "facts": []
            }
        ]
        
        if event.user_name:
            sections[0]["facts"].append({
                "name": "User",
                "value": event.user_name
            })
        
        if event.team_name:
            sections[0]["facts"].append({
                "name": "Team",
                "value": event.team_name
            })
        
        sections[0]["facts"].append({
            "name": "Severity",
            "value": event.severity.upper()
        })
        
        # Add data as facts
        for key, value in list(event.data.items())[:5]:
            sections[0]["facts"].append({
                "name": key.replace("_", " ").title(),
                "value": str(value)
            })
        
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": theme_color,
            "summary": event.title,
            "sections": sections
        }
        
        return payload
    
    async def send(self, event: NotificationEvent) -> bool:
        """Send a notification to Teams."""
        if not self.is_configured:
            return False
        
        webhook_url = self._get_webhook_for_event(event)
        if not webhook_url:
            return False
        
        try:
            client = await self._get_client()
            payload = self._build_payload(event)
            
            response = await client.post(webhook_url, json=payload)
            
            # Teams returns 200 OK on success, sometimes with empty body
            if response.status_code == 200:
                return True
            
            # If Adaptive Card fails, try legacy MessageCard
            if response.status_code in (400, 415):
                legacy_payload = self._build_legacy_payload(event)
                fallback_response = await client.post(webhook_url, json=legacy_payload)
                return fallback_response.status_code == 200
            
            return False
            
        except Exception as e:
            # Log error but don't raise - notifications shouldn't break main flow
            return False
    
    async def send_batch(self, events: List[NotificationEvent]) -> Dict[str, bool]:
        """Send multiple notifications to Teams."""
        results = {}
        
        # Send sequentially to avoid overwhelming the webhook
        for event in events:
            results[event.event_id] = await self.send(event)
            await asyncio.sleep(0.2)  # Teams has stricter rate limits
        
        return results
    
    def format_message(self, event: NotificationEvent) -> str:
        """Format message for Teams (Markdown-like syntax)."""
        icon = self.EVENT_ICONS.get(event.event_type, "📢")
        lines = [
            f"**{icon} {event.title}**",
            "",
            event.message,
            "",
        ]
        
        if event.user_name:
            lines.append(f"**User:** {event.user_name}")
        
        if event.team_name:
            lines.append(f"**Team:** {event.team_name}")
        
        lines.append(f"**Time:** {event.timestamp.strftime('%Y-%m-%d %H:%M UTC')}")
        
        return "\n".join(lines)


# Factory function for easy instantiation
def create_teams_notifier(
    webhook_url: Optional[str] = None,
    alerts_webhook_url: Optional[str] = None,
) -> Optional[TeamsNotifier]:
    """
    Create a Teams notifier if configured.
    
    Returns None if no configuration is provided.
    """
    if not webhook_url:
        return None
    
    return TeamsNotifier(
        webhook_url=webhook_url,
        alerts_webhook_url=alerts_webhook_url,
    )
