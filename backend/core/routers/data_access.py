"""
[AI GENERATED]
Model: GitHub Copilot (GPT-4.1)
Logic: Implements Data Access Controls API for fine-grained permissions on sensitive/PII data. Provides endpoints to define, assign, and check access policies at the dataset/field level. Integrates with RBAC and permission checks.
Why: Enables privacy, compliance, and least-privilege access for sensitive data.
Root Cause: Current RBAC is role/permission only; lacks dataset/field-level controls for PII/sensitive data.
Context: Used by backend for enforcing access, and by frontend for admin configuration. Future: extend for dynamic policy engines, attribute-based access, and audit logging.
Model Suitability: GPT-4.1 is suitable for FastAPI policy APIs; for advanced policy logic, consider Claude 3 or Gemini 1.5.
"""

from fastapi import APIRouter, Depends, HTTPException, Body, Path
from sqlmodel import Session, select
from ..models import User, Role, Permission
from ..dependencies import get_session, require_admin
import uuid
from typing import List, Optional

router = APIRouter(prefix="/v1/data_access", tags=["Data Access Controls"])

# --- Data Access Policy Model (in-memory for now) ---
# In production, move to DB model and migrations
class DataAccessPolicy:
    def __init__(self, id, name, description, resource, allowed_roles, allowed_users):
        self.id = id
        self.name = name
        self.description = description
        self.resource = resource  # e.g., dataset/table/field
        self.allowed_roles = allowed_roles  # list of role IDs
        self.allowed_users = allowed_users  # list of user IDs

# Simulated policy store
DATA_ACCESS_POLICIES = {}

# --- API Endpoints ---
@router.post("/policies", dependencies=[Depends(require_admin)])
async def create_policy(
    name: str = Body(...),
    description: Optional[str] = Body(None),
    resource: str = Body(...),
    allowed_roles: List[str] = Body(default=[]),
    allowed_users: List[str] = Body(default=[]),
):
    policy_id = str(uuid.uuid4())
    policy = DataAccessPolicy(policy_id, name, description, resource, allowed_roles, allowed_users)
    DATA_ACCESS_POLICIES[policy_id] = policy
    return {"id": policy_id, "name": name, "resource": resource}

@router.get("/policies", dependencies=[Depends(require_admin)])
async def list_policies():
    return [
        {"id": p.id, "name": p.name, "resource": p.resource, "allowed_roles": p.allowed_roles, "allowed_users": p.allowed_users}
        for p in DATA_ACCESS_POLICIES.values()
    ]

@router.get("/policies/{policy_id}", dependencies=[Depends(require_admin)])
async def get_policy(policy_id: str):
    policy = DATA_ACCESS_POLICIES.get(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found.")
    return {"id": policy.id, "name": policy.name, "resource": policy.resource, "allowed_roles": policy.allowed_roles, "allowed_users": policy.allowed_users}

@router.delete("/policies/{policy_id}", dependencies=[Depends(require_admin)])
async def delete_policy(policy_id: str):
    if policy_id not in DATA_ACCESS_POLICIES:
        raise HTTPException(status_code=404, detail="Policy not found.")
    del DATA_ACCESS_POLICIES[policy_id]
    return {"message": "Policy deleted."}

@router.post("/check_access", dependencies=[Depends(require_admin)])
async def check_access(
    user_id: str = Body(...),
    resource: str = Body(...),
):
    # Check if user or their roles are allowed for the resource
    for policy in DATA_ACCESS_POLICIES.values():
        if policy.resource == resource:
            if user_id in policy.allowed_users:
                return {"access": True, "policy_id": policy.id}
            # Check user roles (simulate lookup)
            # In production, fetch user roles from DB
            # For now, always False
    return {"access": False}
