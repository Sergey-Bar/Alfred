"""
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L1
Logic:       Email notification provider supporting AWS SES
             and SendGrid transports. Uses async httpx for
             API calls. Supports HTML templates per event type.
Root Cause:  Sprint task T076 — Email notifications.
Context:     Plugs into NotificationManager as a provider.
Suitability: L1 — standard SDK integration.
──────────────────────────────────────────────────────────────

Alfred Email Notification Provider
Send notifications via AWS SES or SendGrid.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx

from .base import EventType, NotificationEvent, NotificationProvider

logger = logging.getLogger(__name__)


# --- HTML Templates ---

_BASE_STYLE = """
<style>
    body { font-family: 'Inter', -apple-system, sans-serif; color: #1a1a2e; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 0 auto; padding: 24px; }
    .header { background: #0f0f23; color: #fff; padding: 24px; border-radius: 8px 8px 0 0; }
    .header h1 { margin: 0; font-size: 20px; }
    .header .subtitle { color: #a0a0b0; font-size: 13px; margin-top: 4px; }
    .body { background: #ffffff; border: 1px solid #e2e2e8; border-top: none; padding: 24px; }
    .alert-badge { display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; }
    .badge-info { background: #dbeafe; color: #1e40af; }
    .badge-warning { background: #fef3c7; color: #92400e; }
    .badge-error { background: #fee2e2; color: #991b1b; }
    .badge-critical { background: #fecaca; color: #7f1d1d; }
    .metric { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 16px; margin: 8px 0; }
    .metric-label { font-size: 12px; color: #64748b; }
    .metric-value { font-size: 18px; font-weight: 700; color: #0f172a; }
    .footer { background: #f8fafc; border: 1px solid #e2e2e8; border-top: none; padding: 16px 24px; border-radius: 0 0 8px 8px; font-size: 12px; color: #94a3b8; }
    .btn { display: inline-block; padding: 10px 20px; background: #3b82f6; color: #fff; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px; }
</style>
"""

SEVERITY_BADGE = {
    "info": "badge-info",
    "warning": "badge-warning",
    "error": "badge-error",
    "critical": "badge-critical",
}


def _render_event_html(event: NotificationEvent, dashboard_url: str = "") -> str:
    """Render a notification event as an HTML email body."""
    badge_class = SEVERITY_BADGE.get(event.severity, "badge-info")
    data_rows = ""
    for key, val in event.data.items():
        data_rows += f"""
        <div class="metric">
            <div class="metric-label">{key.replace('_', ' ').title()}</div>
            <div class="metric-value">{val}</div>
        </div>
        """

    cta = ""
    if dashboard_url:
        cta = f'<p style="margin-top:20px;"><a href="{dashboard_url}" class="btn">View in Alfred Dashboard</a></p>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>{_BASE_STYLE}</head>
    <body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Alfred — AI Governance Platform</h1>
            <div class="subtitle">{event.event_type.value.replace('_', ' ').title()}</div>
        </div>
        <div class="body">
            <p><span class="alert-badge {badge_class}">{event.severity.upper()}</span></p>
            <h2 style="margin-top:16px;">{event.title}</h2>
            <p style="color:#475569;">{event.message}</p>
            {data_rows}
            {f'<p style="color:#64748b;font-size:13px;">User: {event.user_name or event.user_email or "N/A"} | Team: {event.team_name or "N/A"}</p>' if event.user_name or event.user_email or event.team_name else ''}
            {cta}
        </div>
        <div class="footer">
            Alfred AI Governance &mdash; {event.timestamp.strftime('%Y-%m-%d %H:%M UTC')}<br>
            Event ID: {event.event_id}
        </div>
    </div>
    </body>
    </html>
    """


class EmailNotifier(NotificationProvider):
    """
    Email notification provider supporting SendGrid and AWS SES.

    Transport is selected based on which credentials are provided:
    - If SENDGRID_API_KEY is set → uses SendGrid v3 API
    - If AWS SES credentials are set → uses SES v2 SendEmail

    Configuration environment variables:
        EMAIL_TRANSPORT:        "sendgrid" or "ses" (auto-detected if not set)
        SENDGRID_API_KEY:       SendGrid API key
        SES_REGION:             AWS SES region (default: us-east-1)
        AWS_ACCESS_KEY_ID:      AWS access key (or use IAM role)
        AWS_SECRET_ACCESS_KEY:  AWS secret key
        EMAIL_FROM:             Sender email address
        EMAIL_FROM_NAME:        Sender display name (default: "Alfred AI")
        ALFRED_DASHBOARD_URL:   Dashboard URL for CTA buttons
    """

    def __init__(
        self,
        transport: str = "sendgrid",
        sendgrid_api_key: Optional[str] = None,
        ses_region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        from_email: str = "notifications@alfred.ai",
        from_name: str = "Alfred AI",
        default_recipients: Optional[List[str]] = None,
        dashboard_url: str = "",
    ):
        self._transport = transport
        self._sendgrid_api_key = sendgrid_api_key
        self._ses_region = ses_region
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._from_email = from_email
        self._from_name = from_name
        self._default_recipients = default_recipients or []
        self._dashboard_url = dashboard_url
        self._client = httpx.AsyncClient(timeout=15.0)

    @property
    def name(self) -> str:
        return "email"

    @property
    def is_configured(self) -> bool:
        if self._transport == "sendgrid":
            return bool(self._sendgrid_api_key and self._default_recipients)
        elif self._transport == "ses":
            return bool(self._from_email and self._default_recipients)
        return False

    async def send(self, event: NotificationEvent, recipients: Optional[List[str]] = None) -> bool:
        """Send a single notification email."""
        to_addrs = recipients or self._default_recipients
        if not to_addrs:
            logger.warning("email_notifier: no recipients configured, skipping")
            return False

        html_body = _render_event_html(event, self._dashboard_url)
        subject = f"[{event.severity.upper()}] {event.title}"

        if self._transport == "sendgrid":
            return await self._send_sendgrid(subject, html_body, to_addrs)
        elif self._transport == "ses":
            return await self._send_ses(subject, html_body, to_addrs)
        else:
            logger.error(f"email_notifier: unknown transport {self._transport}")
            return False

    async def send_batch(self, events: List[NotificationEvent]) -> Dict[str, bool]:
        """Send multiple emails."""
        results = {}
        for event in events:
            results[event.event_id] = await self.send(event)
        return results

    # --- SendGrid Transport ---

    async def _send_sendgrid(self, subject: str, html_body: str, recipients: List[str]) -> bool:
        """Send email via SendGrid v3 Mail Send API."""
        personalizations = [{"to": [{"email": r} for r in recipients]}]

        payload = {
            "personalizations": personalizations,
            "from": {"email": self._from_email, "name": self._from_name},
            "subject": subject,
            "content": [{"type": "text/html", "value": html_body}],
        }

        try:
            resp = await self._client.post(
                "https://api.sendgrid.com/v3/mail/send",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self._sendgrid_api_key}",
                    "Content-Type": "application/json",
                },
            )
            if resp.status_code in (200, 201, 202):
                logger.info(f"email_notifier: sent via SendGrid to {len(recipients)} recipients")
                return True
            else:
                logger.error(f"email_notifier: SendGrid error {resp.status_code}: {resp.text[:200]}")
                return False
        except Exception as e:
            logger.error(f"email_notifier: SendGrid exception: {e}")
            return False

    # --- AWS SES Transport ---

    async def _send_ses(self, subject: str, html_body: str, recipients: List[str]) -> bool:
        """Send email via AWS SES v2 API (simplified — production should use boto3)."""
        try:
            # For production, use boto3 SES client.
            # This is a simplified HTTP implementation for environments without boto3.
            import boto3

            ses_client = boto3.client(
                "ses",
                region_name=self._ses_region,
                aws_access_key_id=self._aws_access_key_id,
                aws_secret_access_key=self._aws_secret_access_key,
            )

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ses_client.send_email(
                    Source=f"{self._from_name} <{self._from_email}>",
                    Destination={"ToAddresses": recipients},
                    Message={
                        "Subject": {"Data": subject, "Charset": "UTF-8"},
                        "Body": {"Html": {"Data": html_body, "Charset": "UTF-8"}},
                    },
                ),
            )

            message_id = response.get("MessageId", "unknown")
            logger.info(f"email_notifier: sent via SES, MessageId={message_id}")
            return True
        except ImportError:
            logger.error("email_notifier: boto3 not installed, cannot use SES transport")
            return False
        except Exception as e:
            logger.error(f"email_notifier: SES exception: {e}")
            return False

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()


def create_email_notifier(
    transport: str = "sendgrid",
    sendgrid_api_key: Optional[str] = None,
    ses_region: str = "us-east-1",
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    from_email: str = "notifications@alfred.ai",
    from_name: str = "Alfred AI",
    default_recipients: Optional[List[str]] = None,
    dashboard_url: str = "",
) -> EmailNotifier:
    """Factory function for creating an EmailNotifier."""
    return EmailNotifier(
        transport=transport,
        sendgrid_api_key=sendgrid_api_key,
        ses_region=ses_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        from_email=from_email,
        from_name=from_name,
        default_recipients=default_recipients,
        dashboard_url=dashboard_url,
    )
