"""
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       SCIM 2.0 provisioning endpoint for IdP-driven
             user and group (team) lifecycle management.
Root Cause:  Sprint task T152 — SCIM provisioning.
Context:     Enables enterprise SSO providers (Okta, Azure AD)
             to auto-provision/deprovision Alfred users and teams.
Suitability: L3 — integration complexity, enterprise auth.
──────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/scim/v2", tags=["SCIM 2.0 Provisioning"])


# ───────────────────── SCIM Schemas ─────────────────────

SCIM_SCHEMA_USER = "urn:ietf:params:scim:schemas:core:2.0:User"
SCIM_SCHEMA_GROUP = "urn:ietf:params:scim:schemas:core:2.0:Group"
SCIM_SCHEMA_LIST = "urn:ietf:params:scim:api:messages:2.0:ListResponse"
SCIM_SCHEMA_PATCH = "urn:ietf:params:scim:api:messages:2.0:PatchOp"
SCIM_SCHEMA_ERROR = "urn:ietf:params:scim:api:messages:2.0:Error"


class SCIMName(BaseModel):
    givenName: str = ""
    familyName: str = ""
    formatted: Optional[str] = None


class SCIMEmail(BaseModel):
    value: str
    type: str = "work"
    primary: bool = True


class SCIMUserResource(BaseModel):
    """SCIM 2.0 User Resource (RFC 7643)."""
    schemas: list[str] = [SCIM_SCHEMA_USER]
    id: Optional[str] = None
    externalId: Optional[str] = None
    userName: str
    name: Optional[SCIMName] = None
    emails: list[SCIMEmail] = []
    active: bool = True
    displayName: Optional[str] = None
    title: Optional[str] = None
    groups: list[dict[str, str]] = []
    meta: Optional[dict[str, Any]] = None


class SCIMMember(BaseModel):
    value: str  # User ID
    display: Optional[str] = None


class SCIMGroupResource(BaseModel):
    """SCIM 2.0 Group Resource (RFC 7643)."""
    schemas: list[str] = [SCIM_SCHEMA_GROUP]
    id: Optional[str] = None
    externalId: Optional[str] = None
    displayName: str
    members: list[SCIMMember] = []
    meta: Optional[dict[str, Any]] = None


class SCIMListResponse(BaseModel):
    schemas: list[str] = [SCIM_SCHEMA_LIST]
    totalResults: int = 0
    startIndex: int = 1
    itemsPerPage: int = 100
    Resources: list[dict[str, Any]] = []


class SCIMPatchOp(BaseModel):
    schemas: list[str] = [SCIM_SCHEMA_PATCH]
    Operations: list[dict[str, Any]]


class SCIMError(BaseModel):
    schemas: list[str] = [SCIM_SCHEMA_ERROR]
    detail: str
    status: str


# ───────────────────── SCIM Service ─────────────────────

class SCIMService:
    """SCIM 2.0 provisioning service for user/group lifecycle."""

    def __init__(self):
        # In-memory store for development. Replace with DB in production.
        self._users: dict[str, dict[str, Any]] = {}
        self._groups: dict[str, dict[str, Any]] = {}

    # ─── Users ───

    def create_user(self, user: SCIMUserResource) -> dict[str, Any]:
        """Create a new user from SCIM provisioning."""
        # Check for duplicate
        for existing in self._users.values():
            if existing.get("userName") == user.userName:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with userName '{user.userName}' already exists",
                )

        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        user_data = {
            "schemas": [SCIM_SCHEMA_USER],
            "id": user_id,
            "externalId": user.externalId,
            "userName": user.userName,
            "name": user.name.model_dump() if user.name else {},
            "emails": [e.model_dump() for e in user.emails],
            "active": user.active,
            "displayName": user.displayName or user.userName,
            "title": user.title,
            "groups": [],
            "meta": {
                "resourceType": "User",
                "created": now,
                "lastModified": now,
                "location": f"/scim/v2/Users/{user_id}",
            },
        }

        self._users[user_id] = user_data
        logger.info("scim_user_created", user_id=user_id, userName=user.userName)

        return user_data

    def get_user(self, user_id: str) -> dict[str, Any]:
        user = self._users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def list_users(
        self,
        start_index: int = 1,
        count: int = 100,
        filter_str: Optional[str] = None,
    ) -> SCIMListResponse:
        users = list(self._users.values())

        # Basic filter support: userName eq "value"
        if filter_str:
            users = self._apply_filter(users, filter_str, "userName")

        total = len(users)
        page = users[start_index - 1: start_index - 1 + count]

        return SCIMListResponse(
            totalResults=total,
            startIndex=start_index,
            itemsPerPage=count,
            Resources=page,
        )

    def update_user(self, user_id: str, user: SCIMUserResource) -> dict[str, Any]:
        existing = self._users.get(user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="User not found")

        now = datetime.now(timezone.utc).isoformat()
        existing.update({
            "userName": user.userName,
            "name": user.name.model_dump() if user.name else existing.get("name", {}),
            "emails": [e.model_dump() for e in user.emails] if user.emails else existing.get("emails", []),
            "active": user.active,
            "displayName": user.displayName or user.userName,
            "title": user.title,
            "externalId": user.externalId or existing.get("externalId"),
        })
        existing.setdefault("meta", {})["lastModified"] = now

        logger.info("scim_user_updated", user_id=user_id)
        return existing

    def patch_user(self, user_id: str, patch: SCIMPatchOp) -> dict[str, Any]:
        existing = self._users.get(user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="User not found")

        for op in patch.Operations:
            operation = op.get("op", "").lower()
            path = op.get("path", "")
            value = op.get("value")

            if operation == "replace":
                if path == "active":
                    existing["active"] = value
                elif path == "userName":
                    existing["userName"] = value
                elif path == "name.givenName":
                    existing.setdefault("name", {})["givenName"] = value
                elif path == "name.familyName":
                    existing.setdefault("name", {})["familyName"] = value
                elif path == "displayName":
                    existing["displayName"] = value
                elif not path and isinstance(value, dict):
                    # Bulk replace
                    for k, v in value.items():
                        if k in existing:
                            existing[k] = v
            elif operation == "add":
                if path == "emails":
                    existing.setdefault("emails", []).extend(
                        value if isinstance(value, list) else [value]
                    )
            elif operation == "remove":
                if path == "emails":
                    existing["emails"] = []

        existing.setdefault("meta", {})["lastModified"] = datetime.now(timezone.utc).isoformat()
        logger.info("scim_user_patched", user_id=user_id)
        return existing

    def delete_user(self, user_id: str) -> None:
        if user_id not in self._users:
            raise HTTPException(status_code=404, detail="User not found")

        # Remove user from all groups
        for group in self._groups.values():
            group["members"] = [
                m for m in group.get("members", []) if m.get("value") != user_id
            ]

        del self._users[user_id]
        logger.info("scim_user_deleted", user_id=user_id)

    # ─── Groups ───

    def create_group(self, group: SCIMGroupResource) -> dict[str, Any]:
        group_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        group_data = {
            "schemas": [SCIM_SCHEMA_GROUP],
            "id": group_id,
            "externalId": group.externalId,
            "displayName": group.displayName,
            "members": [m.model_dump() for m in group.members],
            "meta": {
                "resourceType": "Group",
                "created": now,
                "lastModified": now,
                "location": f"/scim/v2/Groups/{group_id}",
            },
        }

        self._groups[group_id] = group_data
        logger.info("scim_group_created", group_id=group_id, name=group.displayName)

        return group_data

    def get_group(self, group_id: str) -> dict[str, Any]:
        group = self._groups.get(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        return group

    def list_groups(
        self,
        start_index: int = 1,
        count: int = 100,
        filter_str: Optional[str] = None,
    ) -> SCIMListResponse:
        groups = list(self._groups.values())

        if filter_str:
            groups = self._apply_filter(groups, filter_str, "displayName")

        total = len(groups)
        page = groups[start_index - 1: start_index - 1 + count]

        return SCIMListResponse(
            totalResults=total,
            startIndex=start_index,
            itemsPerPage=count,
            Resources=page,
        )

    def update_group(self, group_id: str, group: SCIMGroupResource) -> dict[str, Any]:
        existing = self._groups.get(group_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Group not found")

        existing.update({
            "displayName": group.displayName,
            "members": [m.model_dump() for m in group.members],
            "externalId": group.externalId or existing.get("externalId"),
        })
        existing.setdefault("meta", {})["lastModified"] = datetime.now(timezone.utc).isoformat()

        logger.info("scim_group_updated", group_id=group_id)
        return existing

    def patch_group(self, group_id: str, patch: SCIMPatchOp) -> dict[str, Any]:
        existing = self._groups.get(group_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Group not found")

        for op in patch.Operations:
            operation = op.get("op", "").lower()
            path = op.get("path", "")
            value = op.get("value")

            if operation == "add" and path == "members":
                members = value if isinstance(value, list) else [value]
                existing_ids = {m.get("value") for m in existing.get("members", [])}
                for member in members:
                    if member.get("value") not in existing_ids:
                        existing.setdefault("members", []).append(member)
            elif operation == "remove" and path and path.startswith("members"):
                # path format: members[value eq "user-id"]
                import re
                match = re.search(r'value\s+eq\s+"([^"]+)"', path)
                if match:
                    remove_id = match.group(1)
                    existing["members"] = [
                        m for m in existing.get("members", [])
                        if m.get("value") != remove_id
                    ]
            elif operation == "replace":
                if path == "displayName":
                    existing["displayName"] = value
                elif path == "members":
                    existing["members"] = value if isinstance(value, list) else [value]

        existing.setdefault("meta", {})["lastModified"] = datetime.now(timezone.utc).isoformat()
        logger.info("scim_group_patched", group_id=group_id)
        return existing

    def delete_group(self, group_id: str) -> None:
        if group_id not in self._groups:
            raise HTTPException(status_code=404, detail="Group not found")
        del self._groups[group_id]
        logger.info("scim_group_deleted", group_id=group_id)

    # ─── Utilities ───

    @staticmethod
    def _apply_filter(
        resources: list[dict[str, Any]],
        filter_str: str,
        field_name: str,
    ) -> list[dict[str, Any]]:
        """Apply basic SCIM filter: field eq "value"."""
        import re
        match = re.match(rf'{field_name}\s+eq\s+"([^"]+)"', filter_str)
        if match:
            target_value = match.group(1)
            return [r for r in resources if r.get(field_name) == target_value]
        return resources


# ─── Singleton service instance ───
_scim_service = SCIMService()


def get_scim_service() -> SCIMService:
    return _scim_service


# ───────────────────── SCIM Bearer Token Auth ─────────────────────

async def verify_scim_bearer(authorization: str = Header(...)) -> str:
    """Verify SCIM bearer token from IdP."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid SCIM bearer token",
        )
    token = authorization[7:]
    # In production: validate token against stored SCIM tokens
    if len(token) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid SCIM bearer token",
        )
    return token


# ───────────────────── User Endpoints ─────────────────────

@router.post("/Users", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: SCIMUserResource,
    _token: str = Depends(verify_scim_bearer),
    service: SCIMService = Depends(get_scim_service),
):
    """Create a user via SCIM provisioning."""
    return service.create_user(user)


@router.get("/Users/{user_id}")
async def get_user(
    user_id: str,
    _token: str = Depends(verify_scim_bearer),
    service: SCIMService = Depends(get_scim_service),
):
    """Get a user by ID."""
    return service.get_user(user_id)


@router.get("/Users")
async def list_users(
    startIndex: int = 1,
    count: int = 100,
    filter: Optional[str] = None,
    _token: str = Depends(verify_scim_bearer),
    service: SCIMService = Depends(get_scim_service),
):
    """List users with optional filtering."""
    return service.list_users(startIndex, count, filter)


@router.put("/Users/{user_id}")
async def update_user(
    user_id: str,
    user: SCIMUserResource,
    _token: str = Depends(verify_scim_bearer),
    service: SCIMService = Depends(get_scim_service),
):
    """Replace a user via SCIM."""
    return service.update_user(user_id, user)


@router.patch("/Users/{user_id}")
async def patch_user(
    user_id: str,
    patch: SCIMPatchOp,
    _token: str = Depends(verify_scim_bearer),
    service: SCIMService = Depends(get_scim_service),
):
    """Patch a user via SCIM."""
    return service.patch_user(user_id, patch)


@router.delete("/Users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    _token: str = Depends(verify_scim_bearer),
    service: SCIMService = Depends(get_scim_service),
):
    """Delete (deprovision) a user via SCIM."""
    service.delete_user(user_id)


# ───────────────────── Group Endpoints ─────────────────────

@router.post("/Groups", status_code=status.HTTP_201_CREATED)
async def create_group(
    group: SCIMGroupResource,
    _token: str = Depends(verify_scim_bearer),
    service: SCIMService = Depends(get_scim_service),
):
    """Create a group (team) via SCIM provisioning."""
    return service.create_group(group)


@router.get("/Groups/{group_id}")
async def get_group(
    group_id: str,
    _token: str = Depends(verify_scim_bearer),
    service: SCIMService = Depends(get_scim_service),
):
    """Get a group by ID."""
    return service.get_group(group_id)


@router.get("/Groups")
async def list_groups(
    startIndex: int = 1,
    count: int = 100,
    filter: Optional[str] = None,
    _token: str = Depends(verify_scim_bearer),
    service: SCIMService = Depends(get_scim_service),
):
    """List groups with optional filtering."""
    return service.list_groups(startIndex, count, filter)


@router.put("/Groups/{group_id}")
async def update_group(
    group_id: str,
    group: SCIMGroupResource,
    _token: str = Depends(verify_scim_bearer),
    service: SCIMService = Depends(get_scim_service),
):
    """Replace a group via SCIM."""
    return service.update_group(group_id, group)


@router.patch("/Groups/{group_id}")
async def patch_group(
    group_id: str,
    patch: SCIMPatchOp,
    _token: str = Depends(verify_scim_bearer),
    service: SCIMService = Depends(get_scim_service),
):
    """Patch a group via SCIM (add/remove members)."""
    return service.patch_group(group_id, patch)


@router.delete("/Groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: str,
    _token: str = Depends(verify_scim_bearer),
    service: SCIMService = Depends(get_scim_service),
):
    """Delete a group via SCIM."""
    service.delete_group(group_id)


# ───────────────────── Service Provider Config ─────────────────────

@router.get("/ServiceProviderConfig")
async def service_provider_config():
    """SCIM 2.0 Service Provider Configuration (RFC 7643 §5)."""
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
        "documentationUri": "https://docs.alfred.ai/scim",
        "patch": {"supported": True},
        "bulk": {"supported": False, "maxOperations": 0, "maxPayloadSize": 0},
        "filter": {"supported": True, "maxResults": 200},
        "changePassword": {"supported": False},
        "sort": {"supported": False},
        "etag": {"supported": False},
        "authenticationSchemes": [
            {
                "type": "oauthbearertoken",
                "name": "OAuth Bearer Token",
                "description": "SCIM bearer token authentication",
                "specUri": "https://tools.ietf.org/html/rfc6750",
                "primary": True,
            }
        ],
    }


@router.get("/ResourceTypes")
async def resource_types():
    """SCIM 2.0 Resource Types."""
    return {
        "schemas": [SCIM_SCHEMA_LIST],
        "totalResults": 2,
        "Resources": [
            {
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"],
                "id": "User",
                "name": "User",
                "endpoint": "/Users",
                "schema": SCIM_SCHEMA_USER,
            },
            {
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"],
                "id": "Group",
                "name": "Group",
                "endpoint": "/Groups",
                "schema": SCIM_SCHEMA_GROUP,
            },
        ],
    }


@router.get("/Schemas")
async def schemas():
    """SCIM 2.0 Schemas endpoint."""
    return {
        "schemas": [SCIM_SCHEMA_LIST],
        "totalResults": 2,
        "Resources": [
            {
                "id": SCIM_SCHEMA_USER,
                "name": "User",
                "description": "Alfred User Account",
            },
            {
                "id": SCIM_SCHEMA_GROUP,
                "name": "Group",
                "description": "Alfred Team / Group",
            },
        ],
    }
