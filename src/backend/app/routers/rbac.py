"""
[AI GENERATED]
Model: GitHub Copilot (GPT-4.1)
Logic: Implements RBAC management endpoints for roles, permissions, assignments. Enables CRUD for roles/permissions, user-role and role-permission assignment, and permission checks. All endpoints require admin by default; future: add fine-grained permission checks.
Why: Enables enterprise-grade governance, least-privilege, and compliance workflows.
Root Cause: Prior API only supported admin/non-admin; lacked extensibility for custom roles and permissions.
Context: Used by frontend admin UI and backend permission checks. See models.py for RBAC schema. Future: extend for org/team scoping, hierarchical roles, and policy engines.
Model Suitability: GPT-4.1 is suitable for FastAPI RBAC patterns; for advanced policy engines, consider Claude 3 or Gemini 1.5.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..dependencies import get_session, require_admin
from ..models import Permission, Role, RolePermission, User, UserRole

router = APIRouter(prefix="/v1/rbac", tags=["RBAC Management"])


# --- Role Management ---
@router.post("/roles", response_model=Role, dependencies=[Depends(require_admin)])
async def create_role(role: Role, session: Session = Depends(get_session)):
    existing = session.exec(select(Role).where(Role.name == role.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role already exists.")
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


@router.get("/roles", response_model=List[Role], dependencies=[Depends(require_admin)])
async def list_roles(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), session: Session = Depends(get_session)
):
    return session.exec(select(Role).offset(skip).limit(limit)).all()


@router.delete("/roles/{role_id}", dependencies=[Depends(require_admin)])
async def delete_role(role_id: str, session: Session = Depends(get_session)):
    role = session.get(Role, uuid.UUID(role_id))
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    session.delete(role)
    session.commit()
    return {"message": "Role deleted"}


# --- Permission Management ---
@router.post("/permissions", response_model=Permission, dependencies=[Depends(require_admin)])
async def create_permission(permission: Permission, session: Session = Depends(get_session)):
    existing = session.exec(select(Permission).where(Permission.name == permission.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists.")
    session.add(permission)
    session.commit()
    session.refresh(permission)
    return permission


@router.get("/permissions", response_model=List[Permission], dependencies=[Depends(require_admin)])
async def list_permissions(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), session: Session = Depends(get_session)
):
    return session.exec(select(Permission).offset(skip).limit(limit)).all()


@router.delete("/permissions/{permission_id}", dependencies=[Depends(require_admin)])
async def delete_permission(permission_id: str, session: Session = Depends(get_session)):
    permission = session.get(Permission, uuid.UUID(permission_id))
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found.")
    session.delete(permission)
    session.commit()
    return {"message": "Permission deleted"}


# --- User-Role Assignment ---
@router.post("/users/{user_id}/roles/{role_id}", dependencies=[Depends(require_admin)])
async def assign_role_to_user(user_id: str, role_id: str, session: Session = Depends(get_session)):
    user = session.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    role = session.get(Role, uuid.UUID(role_id))
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    existing = session.exec(
        select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role.id)
    ).first()
    if existing:
        return {"message": "User already has this role."}
    user_role = UserRole(user_id=user.id, role_id=role.id)
    session.add(user_role)
    session.commit()
    return {"message": "Role assigned to user."}


@router.delete("/users/{user_id}/roles/{role_id}", dependencies=[Depends(require_admin)])
async def remove_role_from_user(
    user_id: str, role_id: str, session: Session = Depends(get_session)
):
    user_role = session.exec(
        select(UserRole).where(
            UserRole.user_id == uuid.UUID(user_id), UserRole.role_id == uuid.UUID(role_id)
        )
    ).first()
    if not user_role:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    session.delete(user_role)
    session.commit()
    return {"message": "Role removed from user."}


# --- Role-Permission Assignment ---
@router.post("/roles/{role_id}/permissions/{permission_id}", dependencies=[Depends(require_admin)])
async def assign_permission_to_role(
    role_id: str, permission_id: str, session: Session = Depends(get_session)
):
    role = session.get(Role, uuid.UUID(role_id))
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    permission = session.get(Permission, uuid.UUID(permission_id))
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found.")
    existing = session.exec(
        select(RolePermission).where(
            RolePermission.role_id == role.id, RolePermission.permission_id == permission.id
        )
    ).first()
    if existing:
        return {"message": "Role already has this permission."}
    role_perm = RolePermission(role_id=role.id, permission_id=permission.id)
    session.add(role_perm)
    session.commit()
    return {"message": "Permission assigned to role."}


@router.delete(
    "/roles/{role_id}/permissions/{permission_id}", dependencies=[Depends(require_admin)]
)
async def remove_permission_from_role(
    role_id: str, permission_id: str, session: Session = Depends(get_session)
):
    role_perm = session.exec(
        select(RolePermission).where(
            RolePermission.role_id == uuid.UUID(role_id),
            RolePermission.permission_id == uuid.UUID(permission_id),
        )
    ).first()
    if not role_perm:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    session.delete(role_perm)
    session.commit()
    return {"message": "Permission removed from role."}
