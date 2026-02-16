"""
[AI GENERATED]
Model: GitHub Copilot (GPT-4.1)
Logic: Implements notification and alert management endpoints for admin and user notifications. Supports CRUD for notification channels, sending test notifications, and listing user notifications. Integrates with backend notification manager and supports Slack/Teams/Email/Webhook channels.
Why: Enables real-time alerting, compliance, and operational transparency for admins and users.
Root Cause: No unified API existed for managing or delivering notifications and alerts.
Context: Used by frontend notification center and backend integrations. Future: extend for granular alert rules, templates, and user preferences.
Model Suitability: For REST API patterns, GPT-4.1 is sufficient; for advanced notification logic, consider Claude 3 or Gemini 1.5.
"""

from typing import List

from fastapi import APIRouter, Body, Depends
from sqlmodel import Session

from ..dependencies import get_current_user, get_session, require_admin
from ..integrations import get_notification_manager
from ..models import User

router = APIRouter(prefix="/v1/notifications", tags=["Notifications"])


# --- Notification Channel Management (Admin) ---
@router.get("/channels", dependencies=[Depends(require_admin)])
async def list_channels(session: Session = Depends(get_session)):
    nm = get_notification_manager()
    return nm.list_channels()


@router.post("/channels", dependencies=[Depends(require_admin)])
async def add_channel(channel: dict = Body(...), session: Session = Depends(get_session)):
    nm = get_notification_manager()
    return nm.add_channel(channel)


@router.delete("/channels/{channel_id}", dependencies=[Depends(require_admin)])
async def delete_channel(channel_id: str, session: Session = Depends(get_session)):
    nm = get_notification_manager()
    return nm.delete_channel(channel_id)


@router.post("/channels/{channel_id}/test", dependencies=[Depends(require_admin)])
async def test_channel(channel_id: str, session: Session = Depends(get_session)):
    nm = get_notification_manager()
    return nm.send_test_notification(channel_id)


# --- User Notification Feed ---
@router.get("/feed", response_model=List[dict])
async def get_user_notifications(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    nm = get_notification_manager()
    return nm.get_user_feed(user.id)


# --- Send Notification (Admin) ---
@router.post("/send", dependencies=[Depends(require_admin)])
async def send_notification(payload: dict = Body(...), session: Session = Depends(get_session)):
    nm = get_notification_manager()
    return nm.send(payload)
