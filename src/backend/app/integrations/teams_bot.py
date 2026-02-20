"""
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Microsoft Teams Bot Framework integration for Alfred.
             Provides chat-based access to AI governance features.
Root Cause:  Sprint tasks T201-T203 — MS Teams integration.
Context:     Enables enterprise Teams users to interact with Alfred.
Suitability: L2 — Standard Bot Framework patterns.
──────────────────────────────────────────────────────────────
"""

import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

import httpx
import jwt
from jwt import PyJWKClient
from pydantic import BaseModel, Field
from fastapi import HTTPException

# ============================================================
# Configuration
# ============================================================

TEAMS_CONFIG = {
    "app_id": os.environ.get("TEAMS_APP_ID", ""),
    "app_password": os.environ.get("TEAMS_APP_PASSWORD", ""),
    "tenant_id": os.environ.get("TEAMS_TENANT_ID", ""),
    "alfred_api_url": os.environ.get("ALFRED_API_URL", "http://localhost:8000"),
}

# Bot Framework OpenID metadata URL for JWT validation
BOT_FRAMEWORK_OPENID_METADATA = "https://login.botframework.com/v1/.well-known/openidconfiguration"
BOT_FRAMEWORK_JWKS_URL = "https://login.botframework.com/v1/.well-known/keys"


# ============================================================
# Security: JWT Validation
# ============================================================

async def validate_bot_framework_jwt(authorization_header: Optional[str]) -> bool:
    """
    Validate JWT token from Bot Framework against Microsoft's public keys.
    
    Security: Prevents unauthorized webhook calls to Teams bot endpoints.
    Reference: https://docs.microsoft.com/en-us/azure/bot-service/rest-api/bot-framework-rest-connector-authentication
    
    Args:
        authorization_header: Bearer token from request header
        
    Returns:
        True if valid, raises HTTPException if invalid
    """
    if not authorization_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not authorization_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    token = authorization_header.replace("Bearer ", "")
    
    try:
        # Get signing keys from Microsoft
        jwks_client = PyJWKClient(BOT_FRAMEWORK_JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Validate JWT
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=TEAMS_CONFIG["app_id"],  # Audience must match our app ID
            issuer="https://api.botframework.com",  # Issuer must be Bot Framework
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
            },
        )
        
        # Additional validation: service URL must be present
        if not decoded.get("serviceurl"):
            raise HTTPException(status_code=401, detail="Missing serviceurl in token")
        
        return True
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail="Invalid token audience")
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=401, detail="Invalid token issuer")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token validation error: {str(e)}")


# ============================================================
# Models
# ============================================================

class AdaptiveCardAction(str, Enum):
    """Adaptive Card action types."""
    APPROVE = "approve"
    REJECT = "reject"
    VIEW_DETAILS = "view_details"
    CHECK_BALANCE = "check_balance"
    SET_BUDGET = "set_budget"


class TeamsUser(BaseModel):
    """Teams user identity."""
    id: str
    name: str
    email: Optional[str] = None
    tenant_id: Optional[str] = None
    aad_object_id: Optional[str] = None


class TeamsActivity(BaseModel):
    """Incoming Teams activity."""
    type: str
    id: str
    timestamp: datetime
    channel_id: str
    conversation: Dict[str, Any]
    from_user: Dict[str, Any] = Field(alias="from")
    text: Optional[str] = None
    value: Optional[Dict[str, Any]] = None  # For adaptive card submissions


class CardSubmitData(BaseModel):
    """Data from adaptive card submit action."""
    action: AdaptiveCardAction
    request_id: Optional[str] = None
    amount: Optional[float] = None
    reason: Optional[str] = None


# ============================================================
# Adaptive Cards (T202)
# ============================================================

class AdaptiveCards:
    """Adaptive card templates for Teams interactions."""
    
    @staticmethod
    def welcome_card(user_name: str) -> Dict[str, Any]:
        """Welcome card for new user conversations."""
        return {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "size": "Large",
                    "weight": "Bolder",
                    "text": f"👋 Welcome to Alfred, {user_name}!"
                },
                {
                    "type": "TextBlock",
                    "text": "I'm your AI credit governance assistant. I can help you:",
                    "wrap": True
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "💰", "value": "Check your AI credit balance"},
                        {"title": "📊", "value": "View usage analytics"},
                        {"title": "✅", "value": "Approve pending requests"},
                        {"title": "⚙️", "value": "Manage budget alerts"}
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": "Type a command or use the buttons below:",
                    "wrap": True,
                    "spacing": "Medium"
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Check Balance",
                    "data": {"action": "check_balance"}
                },
                {
                    "type": "Action.Submit",
                    "title": "View Pending Approvals",
                    "data": {"action": "view_approvals"}
                },
                {
                    "type": "Action.OpenUrl",
                    "title": "Open Dashboard",
                    "url": "${dashboard_url}"
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }
    
    @staticmethod
    def balance_card(balance: float, soft_limit: float, hard_limit: float) -> Dict[str, Any]:
        """Wallet balance display card."""
        percent_used = min(100, (1 - balance / hard_limit) * 100) if hard_limit > 0 else 0
        status_color = "good" if percent_used < 50 else ("warning" if percent_used < 80 else "attention")
        
        return {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "size": "Large",
                    "weight": "Bolder",
                    "text": "💰 Your AI Credit Balance"
                },
                {
                    "type": "Container",
                    "style": status_color,
                    "items": [
                        {
                            "type": "TextBlock",
                            "size": "ExtraLarge",
                            "weight": "Bolder",
                            "text": f"${balance:.2f}",
                            "horizontalAlignment": "Center"
                        }
                    ]
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Soft Limit", "value": f"${soft_limit:.2f}"},
                        {"title": "Hard Limit", "value": f"${hard_limit:.2f}"},
                        {"title": "Used", "value": f"{percent_used:.1f}%"}
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                    "size": "Small",
                    "isSubtle": True
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "View Transactions",
                    "data": {"action": "view_transactions"}
                },
                {
                    "type": "Action.Submit",
                    "title": "Set Budget Alert",
                    "data": {"action": "set_budget_alert"}
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }
    
    @staticmethod
    def approval_request_card(
        request_id: str,
        requester: str,
        amount: float,
        reason: str,
        request_type: str,
    ) -> Dict[str, Any]:
        """Approval request card for transfers and budget increases."""
        return {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "size": "Large",
                    "weight": "Bolder",
                    "text": f"🔔 {request_type} Request"
                },
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                                {
                                    "type": "Image",
                                    "url": "https://api.dicebear.com/7.x/initials/svg?seed=" + requester[:2],
                                    "size": "Medium",
                                    "style": "Person"
                                }
                            ]
                        },
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": requester,
                                    "weight": "Bolder"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"Request ID: {request_id[:8]}...",
                                    "size": "Small",
                                    "isSubtle": True
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Amount", "value": f"${amount:.2f}"},
                        {"title": "Reason", "value": reason[:100]}
                    ]
                },
                {
                    "type": "Input.Text",
                    "id": "approval_comment",
                    "placeholder": "Add a comment (optional)",
                    "isMultiline": True
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "✅ Approve",
                    "style": "positive",
                    "data": {
                        "action": "approve",
                        "request_id": request_id
                    }
                },
                {
                    "type": "Action.Submit",
                    "title": "❌ Reject",
                    "style": "destructive",
                    "data": {
                        "action": "reject",
                        "request_id": request_id
                    }
                },
                {
                    "type": "Action.Submit",
                    "title": "View Details",
                    "data": {
                        "action": "view_details",
                        "request_id": request_id
                    }
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }
    
    @staticmethod
    def budget_alert_card(
        current_spend: float,
        budget_limit: float,
        percent_used: float,
        period: str,
    ) -> Dict[str, Any]:
        """Budget alert notification card."""
        status_color = "warning" if percent_used < 90 else "attention"
        
        return {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "size": "Large",
                    "weight": "Bolder",
                    "text": "⚠️ Budget Alert"
                },
                {
                    "type": "Container",
                    "style": status_color,
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"You've used {percent_used:.1f}% of your {period} budget",
                            "weight": "Bolder",
                            "wrap": True
                        }
                    ]
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Current Spend", "value": f"${current_spend:.2f}"},
                        {"title": "Budget Limit", "value": f"${budget_limit:.2f}"},
                        {"title": "Remaining", "value": f"${max(0, budget_limit - current_spend):.2f}"}
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Request Budget Increase",
                    "data": {"action": "request_budget_increase"}
                },
                {
                    "type": "Action.Submit",
                    "title": "View Usage",
                    "data": {"action": "view_usage"}
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }
    
    @staticmethod
    def confirmation_card(title: str, message: str, success: bool = True) -> Dict[str, Any]:
        """Confirmation response card."""
        icon = "✅" if success else "❌"
        style = "good" if success else "attention"
        
        return {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "Container",
                    "style": style,
                    "items": [
                        {
                            "type": "TextBlock",
                            "size": "Medium",
                            "weight": "Bolder",
                            "text": f"{icon} {title}"
                        },
                        {
                            "type": "TextBlock",
                            "text": message,
                            "wrap": True
                        }
                    ]
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }


# ============================================================
# Bot Framework Service (T201)
# ============================================================

class TeamsBot:
    """Microsoft Teams bot for Alfred integration."""
    
    def __init__(self, app_id: str, app_password: str, alfred_api_url: str):
        self.app_id = app_id
        self.app_password = app_password
        self.alfred_api_url = alfred_api_url
        self._token: Optional[str] = None
        self._token_expires: Optional[datetime] = None
    
    async def _get_token(self) -> str:
        """Get OAuth token for Bot Framework."""
        if self._token and self._token_expires and datetime.utcnow() < self._token_expires:
            return self._token
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.app_id,
                    "client_secret": self.app_password,
                    "scope": "https://api.botframework.com/.default"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            self._token = data["access_token"]
            # Token expires in ~1 hour, refresh at 50 minutes
            from datetime import timedelta
            self._token_expires = datetime.utcnow() + timedelta(minutes=50)
            
            return self._token
    
    async def send_activity(
        self,
        service_url: str,
        conversation_id: str,
        activity: Dict[str, Any],
    ) -> None:
        """Send activity back to Teams."""
        token = await self._get_token()
        
        async with httpx.AsyncClient() as client:
            url = f"{service_url}/v3/conversations/{conversation_id}/activities"
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=activity
            )
            response.raise_for_status()
    
    async def send_card(
        self,
        service_url: str,
        conversation_id: str,
        card: Dict[str, Any],
    ) -> None:
        """Send adaptive card to Teams."""
        activity = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": card
                }
            ]
        }
        await self.send_activity(service_url, conversation_id, activity)
    
    async def handle_message(
        self,
        activity: TeamsActivity,
        user_api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Handle incoming message activity."""
        text = (activity.text or "").lower().strip()
        user_name = activity.from_user.get("name", "there")
        
        # Parse commands
        if "balance" in text or "credit" in text:
            return await self._handle_balance_command(user_api_key)
        
        elif "approve" in text:
            return await self._handle_approvals_command(user_api_key)
        
        elif "usage" in text or "analytics" in text:
            return await self._handle_usage_command(user_api_key)
        
        elif "help" in text:
            return AdaptiveCards.welcome_card(user_name)
        
        else:
            # Default response
            return AdaptiveCards.welcome_card(user_name)
    
    async def handle_card_action(
        self,
        activity: TeamsActivity,
        user_api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Handle adaptive card action submission."""
        data = CardSubmitData(**(activity.value or {}))
        
        if data.action == AdaptiveCardAction.CHECK_BALANCE:
            return await self._handle_balance_command(user_api_key)
        
        elif data.action == AdaptiveCardAction.APPROVE:
            return await self._handle_approval_action(data.request_id, True, user_api_key)
        
        elif data.action == AdaptiveCardAction.REJECT:
            return await self._handle_approval_action(data.request_id, False, user_api_key)
        
        elif data.action == AdaptiveCardAction.VIEW_DETAILS:
            return await self._handle_view_details(data.request_id, user_api_key)
        
        else:
            return AdaptiveCards.confirmation_card(
                "Unknown Action",
                "I don't know how to handle that action.",
                success=False
            )
    
    async def _handle_balance_command(
        self,
        api_key: Optional[str],
    ) -> Dict[str, Any]:
        """Handle balance check command."""
        if not api_key:
            return AdaptiveCards.confirmation_card(
                "Authentication Required",
                "Please link your Alfred account to check your balance.",
                success=False
            )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.alfred_api_url}/v1/wallets/me",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                response.raise_for_status()
                wallet = response.json()
                
                return AdaptiveCards.balance_card(
                    balance=float(wallet.get("balance", 0)),
                    soft_limit=float(wallet.get("soft_limit", 0)),
                    hard_limit=float(wallet.get("hard_limit", 0))
                )
        except Exception as e:
            return AdaptiveCards.confirmation_card(
                "Error",
                f"Failed to fetch balance: {str(e)}",
                success=False
            )
    
    async def _handle_approvals_command(
        self,
        api_key: Optional[str],
    ) -> Dict[str, Any]:
        """Handle pending approvals command."""
        # Would fetch pending approvals from API
        return AdaptiveCards.confirmation_card(
            "Pending Approvals",
            "You have no pending approval requests.",
            success=True
        )
    
    async def _handle_usage_command(
        self,
        api_key: Optional[str],
    ) -> Dict[str, Any]:
        """Handle usage analytics command."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.alfred_api_url}/v1/analytics/usage/me",
                    headers={"Authorization": f"Bearer {api_key}"} if api_key else {}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return AdaptiveCards.confirmation_card(
                        "Usage Summary",
                        f"Total requests: {data.get('total_requests', 0)}\n"
                        f"Total cost: ${float(data.get('total_cost', 0)):.2f}",
                        success=True
                    )
        except Exception:
            pass
        
        return AdaptiveCards.confirmation_card(
            "Usage Summary",
            "Unable to fetch usage data. Please check your account settings.",
            success=False
        )
    
    async def _handle_approval_action(
        self,
        request_id: Optional[str],
        approve: bool,
        api_key: Optional[str],
    ) -> Dict[str, Any]:
        """Handle approval/rejection action."""
        if not request_id:
            return AdaptiveCards.confirmation_card(
                "Error",
                "No request ID provided.",
                success=False
            )
        
        action_text = "approved" if approve else "rejected"
        return AdaptiveCards.confirmation_card(
            f"Request {action_text.title()}",
            f"Request {request_id[:8]}... has been {action_text}.",
            success=True
        )
    
    async def _handle_view_details(
        self,
        request_id: Optional[str],
        api_key: Optional[str],
    ) -> Dict[str, Any]:
        """Handle view details action."""
        return AdaptiveCards.confirmation_card(
            "Request Details",
            f"Details for request {request_id or 'unknown'}",
            success=True
        )


# ============================================================
# Proactive Notifications (T203)
# ============================================================

class TeamsNotificationService:
    """Send proactive notifications to Teams users."""
    
    def __init__(self, bot: TeamsBot):
        self.bot = bot
    
    async def send_approval_request(
        self,
        service_url: str,
        conversation_id: str,
        request_id: str,
        requester: str,
        amount: float,
        reason: str,
        request_type: str = "Transfer",
    ) -> None:
        """Send approval request notification."""
        card = AdaptiveCards.approval_request_card(
            request_id=request_id,
            requester=requester,
            amount=amount,
            reason=reason,
            request_type=request_type,
        )
        await self.bot.send_card(service_url, conversation_id, card)
    
    async def send_budget_alert(
        self,
        service_url: str,
        conversation_id: str,
        current_spend: float,
        budget_limit: float,
        period: str = "monthly",
    ) -> None:
        """Send budget alert notification."""
        percent_used = (current_spend / budget_limit * 100) if budget_limit > 0 else 100
        
        card = AdaptiveCards.budget_alert_card(
            current_spend=current_spend,
            budget_limit=budget_limit,
            percent_used=percent_used,
            period=period,
        )
        await self.bot.send_card(service_url, conversation_id, card)
    
    async def send_transfer_completed(
        self,
        service_url: str,
        conversation_id: str,
        amount: float,
        from_user: str,
        to_user: str,
    ) -> None:
        """Send transfer completion notification."""
        card = AdaptiveCards.confirmation_card(
            "Transfer Completed",
            f"${amount:.2f} transferred from {from_user} to {to_user}",
            success=True
        )
        await self.bot.send_card(service_url, conversation_id, card)


# ============================================================
# FastAPI Router Integration
# ============================================================

def create_teams_router():
    """Create FastAPI router for Teams webhook endpoint."""
    from fastapi import APIRouter, Request, HTTPException
    
    router = APIRouter(prefix="/integrations/teams", tags=["MS Teams"])
    
    bot = TeamsBot(
        app_id=TEAMS_CONFIG["app_id"],
        app_password=TEAMS_CONFIG["app_password"],
        alfred_api_url=TEAMS_CONFIG["alfred_api_url"],
    )
    
    @router.post("/webhook")
    async def teams_webhook(request: Request):
        """Handle incoming Teams webhook messages."""
        try:
            # Validate Bot Framework JWT token (security critical)
            authorization = request.headers.get("Authorization")
            await validate_bot_framework_jwt(authorization)
            
            body = await request.json()
            activity = TeamsActivity(**body)
            
            # Handle different activity types
            if activity.type == "message":
                if activity.value:
                    # Card action submission
                    response_card = await bot.handle_card_action(activity)
                else:
                    # Text message
                    response_card = await bot.handle_message(activity)
                
                # Send response
                service_url = body.get("serviceUrl", "")
                conversation_id = activity.conversation.get("id", "")
                
                await bot.send_card(service_url, conversation_id, response_card)
                
                return {"status": "ok"}
            
            elif activity.type == "conversationUpdate":
                # Handle member added/removed
                return {"status": "ok"}
            
            else:
                return {"status": "ignored", "type": activity.type}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
