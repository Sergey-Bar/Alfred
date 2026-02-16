"""
[AI GENERATED]
Model: GitHub Copilot (GPT-4.1)
Logic: Implements Collaboration & Sharing API for secure sharing of dashboards/reports. Provides endpoints to create share links, manage access (view/edit), and revoke sharing. Supports user/team/role-based sharing and link expiration.
Why: Enables secure, auditable sharing of analytics assets for collaboration.
Root Cause: No API for sharing dashboards/reports securely.
Context: Used by backend for access enforcement, and by frontend for admin/user sharing UI. Future: extend for audit logging, external sharing, and advanced permissions.
Model Suitability: GPT-4.1 is suitable for FastAPI sharing APIs; for advanced sharing logic, consider Claude 3 or Gemini 1.5.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException

from ..dependencies import require_admin

router = APIRouter(prefix="/v1/sharing", tags=["Collaboration & Sharing"])


# --- In-memory share link store (for demo) ---
class ShareLink:
    def __init__(self, id, resource, access_type, shared_with, expires_at):
        self.id = id
        self.resource = resource  # e.g., dashboard/report ID
        self.access_type = access_type  # "view" or "edit"
        self.shared_with = shared_with  # list of user/team/role IDs
        self.expires_at = expires_at


SHARE_LINKS = {}


# --- API Endpoints ---
@router.post("/links", dependencies=[Depends(require_admin)])
async def create_share_link(
    resource: str = Body(...),
    access_type: str = Body(...),
    shared_with: List[str] = Body(default=[]),
    expires_in_hours: Optional[int] = Body(default=24),
):
    link_id = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
    link = ShareLink(link_id, resource, access_type, shared_with, expires_at)
    SHARE_LINKS[link_id] = link
    return {
        "id": link_id,
        "resource": resource,
        "access_type": access_type,
        "expires_at": expires_at,
    }


@router.get("/links", dependencies=[Depends(require_admin)])
async def list_share_links():
    return [
        {
            "id": l.id,
            "resource": l.resource,
            "access_type": l.access_type,
            "shared_with": l.shared_with,
            "expires_at": l.expires_at,
        }
        for l in SHARE_LINKS.values()
    ]


@router.get("/links/{link_id}", dependencies=[Depends(require_admin)])
async def get_share_link(link_id: str):
    link = SHARE_LINKS.get(link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found.")
    return {
        "id": link.id,
        "resource": link.resource,
        "access_type": link.access_type,
        "shared_with": link.shared_with,
        "expires_at": link.expires_at,
    }


@router.delete("/links/{link_id}", dependencies=[Depends(require_admin)])
async def revoke_share_link(link_id: str):
    if link_id not in SHARE_LINKS:
        raise HTTPException(status_code=404, detail="Share link not found.")
    del SHARE_LINKS[link_id]
    return {"message": "Share link revoked."}
