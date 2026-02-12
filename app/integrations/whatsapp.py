"""
Alfred WhatsApp Integration
Send notifications to WhatsApp via WhatsApp Business Cloud API.
"""

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from .base import NotificationProvider, NotificationEvent, EventType


class WhatsAppNotifier(NotificationProvider):
    """
    WhatsApp notification provider using WhatsApp Business Cloud API.
    
    Supports:
    - WhatsApp Business Cloud API (Meta)
    - Template messages (required for business-initiated conversations)
    - Text messages (for user-initiated conversation windows)
    - Interactive messages
    
    Configuration:
        WHATSAPP_PHONE_NUMBER_ID: WhatsApp Business Phone Number ID
        WHATSAPP_ACCESS_TOKEN: Meta Graph API access token
        WHATSAPP_RECIPIENT_NUMBER: Default recipient phone number (with country code)
    
    Setup:
        1. Create a Meta Business account
        2. Set up WhatsApp Business API in Meta Developer Console
        3. Get Phone Number ID and Access Token
        4. Create message templates in WhatsApp Manager (for business-initiated messages)
    
    Note: WhatsApp requires pre-approved templates for business-initiated messages.
          Free-form text only works within 24h of user's last message.
    """
    
    WHATSAPP_API_BASE = "https://graph.facebook.com/v18.0"
    
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
        phone_number_id: Optional[str] = None,
        access_token: Optional[str] = None,
        recipient_number: Optional[str] = None,
        alerts_recipient_number: Optional[str] = None,
        template_name: Optional[str] = None,
        template_language: str = "en",
        timeout: float = 10.0
    ):
        """
        Initialize WhatsApp notifier.
        
        Args:
            phone_number_id: WhatsApp Business Phone Number ID
            access_token: Meta Graph API access token
            recipient_number: Default recipient phone number (e.g., "1234567890")
            alerts_recipient_number: Separate number for critical alerts
            template_name: Pre-approved template name for business-initiated messages
            template_language: Template language code
            timeout: HTTP request timeout in seconds
        """
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.recipient_number = recipient_number
        self.alerts_recipient_number = alerts_recipient_number
        self.template_name = template_name
        self.template_language = template_language
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def name(self) -> str:
        return "whatsapp"
    
    @property
    def is_configured(self) -> bool:
        return bool(
            self.phone_number_id and 
            self.access_token and 
            self.recipient_number
        )
    
    @property
    def api_url(self) -> str:
        """Get the WhatsApp API URL for sending messages."""
        return f"{self.WHATSAPP_API_BASE}/{self.phone_number_id}/messages"
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                }
            )
        return self._client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    def _get_recipient_for_event(self, event: NotificationEvent) -> Optional[str]:
        """Determine which recipient to use based on event severity."""
        if event.severity in ("error", "critical") and self.alerts_recipient_number:
            return self.alerts_recipient_number
        return self.recipient_number
    
    def _format_text_message(self, event: NotificationEvent) -> str:
        """Format the notification as plain text for WhatsApp."""
        emoji = self.EVENT_EMOJI.get(event.event_type, "📢")
        severity_emoji = self.SEVERITY_EMOJI.get(event.severity, "ℹ️")
        
        lines = [
            f"{emoji} *{event.title}*",
            "",
            event.message,
            "",
        ]
        
        if event.user_name:
            lines.append(f"👤 *User:* {event.user_name}")
        
        if event.team_name:
            lines.append(f"👥 *Team:* {event.team_name}")
        
        if event.data:
            lines.append("")
            for key, value in list(event.data.items())[:5]:
                lines.append(f"• *{key.replace('_', ' ').title()}:* {value}")
        
        lines.append("")
        timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M UTC")
        lines.append(f"_{severity_emoji} {event.severity.upper()} | {timestamp}_")
        lines.append(f"_Alfred_")
        
        return "\n".join(lines)
    
    def _build_text_payload(
        self,
        recipient: str,
        event: NotificationEvent
    ) -> Dict[str, Any]:
        """Build payload for text message."""
        text = self._format_text_message(event)
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text
            }
        }
    
    def _build_template_payload(
        self,
        recipient: str,
        event: NotificationEvent
    ) -> Dict[str, Any]:
        """
        Build payload for template message.
        
        Note: You need to create and approve a template in WhatsApp Manager first.
        Example template with variables:
        - {{1}} = Title
        - {{2}} = Message
        - {{3}} = User name
        - {{4}} = Timestamp
        """
        if not self.template_name:
            # Fall back to text message
            return self._build_text_payload(recipient, event)
        
        timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M UTC")
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "template",
            "template": {
                "name": self.template_name,
                "language": {
                    "code": self.template_language
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": event.title},
                            {"type": "text", "text": event.message},
                            {"type": "text", "text": event.user_name or "System"},
                            {"type": "text", "text": timestamp},
                        ]
                    }
                ]
            }
        }
    
    async def send(self, event: NotificationEvent) -> bool:
        """Send a notification to WhatsApp."""
        if not self.is_configured:
            return False
        
        recipient = self._get_recipient_for_event(event)
        if not recipient:
            return False
        
        try:
            client = await self._get_client()
            
            # Try text message first (works within 24h window)
            payload = self._build_text_payload(recipient, event)
            
            response = await client.post(self.api_url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                # Check if message was accepted
                messages = result.get("messages", [])
                return len(messages) > 0 and messages[0].get("id") is not None
            
            # If text fails (outside 24h window), try template
            if response.status_code in (400, 403) and self.template_name:
                template_payload = self._build_template_payload(recipient, event)
                
                template_response = await client.post(
                    self.api_url,
                    json=template_payload
                )
                
                if template_response.status_code == 200:
                    result = template_response.json()
                    messages = result.get("messages", [])
                    return len(messages) > 0 and messages[0].get("id") is not None
            
            return False
            
        except Exception as e:
            return False
    
    async def send_batch(self, events: List[NotificationEvent]) -> Dict[str, bool]:
        """Send multiple notifications to WhatsApp."""
        results = {}
        
        # WhatsApp has rate limits - be conservative
        for event in events:
            results[event.event_id] = await self.send(event)
            await asyncio.sleep(0.5)  # ~2 messages per second to be safe
        
        return results
    
    def format_message(self, event: NotificationEvent) -> str:
        """Format message for WhatsApp."""
        return self._format_text_message(event)


# Factory function
def create_whatsapp_notifier(
    phone_number_id: Optional[str] = None,
    access_token: Optional[str] = None,
    recipient_number: Optional[str] = None,
    alerts_recipient_number: Optional[str] = None,
    template_name: Optional[str] = None,
) -> Optional[WhatsAppNotifier]:
    """
    Create a WhatsApp notifier if configured.
    
    Returns None if no configuration is provided.
    """
    if not phone_number_id or not access_token or not recipient_number:
        return None
    
    return WhatsAppNotifier(
        phone_number_id=phone_number_id,
        access_token=access_token,
        recipient_number=recipient_number,
        alerts_recipient_number=alerts_recipient_number,
        template_name=template_name,
    )
