import json
import uuid
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlmodel import Session, select

from ..dependencies import get_current_user, get_session, require_admin, create_background_task
from ..logic import AuthManager
from ..logging_config import get_logger
from ..models import User, UserStatus
from ..schemas import (
    ApiKeyResponse,
    QuotaStatusResponse,
    UserCreate,
    UserCreateResponse,
    UserResponse,
    UserUpdate,
    UserProfileUpdate
)

logger = get_logger(__name__)
router = APIRouter(prefix="/v1", tags=["Identity & Access Management"])

@router.post("/admin/users", response_model=UserCreateResponse, dependencies=[Depends(require_admin)])
async def create_user(
    user_data: UserCreate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
):
    """
    Onboard New Organizational Participant.
    
    Creates a user record and generates a unique API secret.
    Compliance: Automatically records a 'create_user' event in the immutable audit log.
    """
    # Defensive check: Prevent identity collisions
    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Identity Conflict: A user with this email already exists.")

    api_key, api_key_hash = AuthManager.generate_api_key()
    
    user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        name=user_data.name,
        personal_quota=user_data.personal_quota or 1000.00,
        api_key_hash=api_key_hash,
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)

    # Compliance: Write to immutable audit trail
    try:
        from ..audit import log_audit
        log_audit(
            session=session,
            actor_user_id=admin_user.id,
            action="identity.provision",
            target_type="user",
            target_id=str(user.id),
            details={"email": user.email, "name": user.name},
        )
    except Exception as e:
        # [BUG-007 FIX] Visibility into audit trail failures
        logger.error(f"Compliance: Provision audit failed: {str(e)}")

    # Map to response with cleartext key (Only time it's shown)
    def safe_json_parse(data: Optional[str]) -> dict:
        if not data: return {}
        try: return json.loads(data)
        except Exception: return {}

    return UserCreateResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        status=user.status.value,
        personal_quota=user.personal_quota,
        used_tokens=user.used_tokens,
        available_quota=user.available_quota,
        default_priority=user.default_priority.value,
        preferences=safe_json_parse(user.preferences_json),
        api_key=api_key
    )

@router.post("/admin/users/{user_id}/rotate_api_key", response_model=ApiKeyResponse, dependencies=[Depends(require_admin)])
async def rotate_api_key(
    user_id: str,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user)
):
    """
    Security Key Rotation Interface.
    
    Used for scheduled maintenance or in response to potential credential exposure.
    Invalidates the old hash immediately upon commit.
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Identifier Format.")

    user = session.get(User, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="Entity not found.")
        
    api_key, api_key_hash = AuthManager.generate_api_key()
    user.api_key_hash = api_key_hash
    
    try:
        session.add(user)
        session.commit()
        
        from ..audit import log_audit
        log_audit(
            session=session,
            actor_user_id=admin_user.id,
            action="identity.rotate_key",
            target_type="user",
            target_id=str(user.id),
        )
    except Exception as e:
        logger.error(f"Compliance: Rotation audit failed: {str(e)}")

    return ApiKeyResponse(
        api_key=api_key,
        message="Confidential: This secret will not be displayed again. Store securely."
    )

@router.get("/admin/users", response_model=List[UserResponse], dependencies=[Depends(require_admin)])
async def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=500),
    session: Session = Depends(get_session)
):
    """Retreive global identity list with usage metrics (Paginated)."""
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    
    def safe_json_parse(data: Optional[str]) -> dict:
        if not data: return {}
        try: return json.loads(data)
        except Exception: return {}

    return [
        UserResponse(
            id=str(u.id), email=u.email, name=u.name, 
            status=u.status.value, personal_quota=u.personal_quota,
            used_tokens=u.used_tokens, available_quota=u.available_quota,
            default_priority=u.default_priority.value,
            preferences=safe_json_parse(u.preferences_json)
        ) for u in users
    ]

@router.put("/admin/users/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
async def update_user(
    user_id: str = Path(..., pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    user_data: UserUpdate = Body(...),
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
):
    """Modify user state (Quota adjustments, status changes)."""
    # Regex in Path ensures we only process valid UUID strings
    user = session.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="Subject not found.")

    if user_data.name is not None: user.name = user_data.name
    if user_data.status is not None: user.status = UserStatus(user_data.status)
    if user_data.personal_quota is not None: user.personal_quota = user_data.personal_quota
    
    session.add(user)
    session.commit()
    session.refresh(user)

    # Compliance: Log the mutation
    try:
        from ..audit import log_audit
        log_audit(
            session=session,
            actor_user_id=admin_user.id,
            action="identity.update",
            target_type="user",
            target_id=str(user.id),
            details={"updated_fields": list(user_data.model_dump(exclude_unset=True).keys())}
        )
    except Exception as e:
        logger.error(f"Compliance: Update audit failed: {str(e)}")

    def safe_json_parse(data: Optional[str]) -> dict:
        if not data: return {}
        try: return json.loads(data)
        except Exception: return {}

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        status=user.status.value,
        personal_quota=user.personal_quota,
        used_tokens=user.used_tokens,
        available_quota=user.available_quota,
        default_priority=user.default_priority.value,
        preferences=safe_json_parse(user.preferences_json)
    )

@router.delete("/admin/users/{user_id}", dependencies=[Depends(require_admin)])
async def delete_user(
    user_id: str,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
):
    """Delete a user (admin endpoint)."""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Identifier Format.")

    user = session.get(User, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="Entity not found.")

    # Guard: Prevent self-deletion for safety
    if user.id == admin_user.id:
        raise HTTPException(status_code=400, detail="Safety Protocol: Self-deprovisioning restricted.")

    deleted_id = str(user.id)
    deleted_email = user.email
    session.delete(user)
    session.commit()

    try:
        from ..audit import log_audit
        log_audit(
            session=session,
            actor_user_id=admin_user.id,
            action="identity.deprovision",
            target_type="user",
            target_id=deleted_id,
            details={"email": deleted_email},
        )
    except Exception as e:
        logger.error(f"Compliance: Deprovision audit failed: {str(e)}")

    return {"message": "User deleted successfully"}

@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    user: User = Depends(get_current_user)
):
    """Get current user information."""
    def safe_json_parse(data: Optional[str]) -> dict:
        if not data: return {}
        try: return json.loads(data)
        except Exception: return {}

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        status=user.status.value,
        personal_quota=user.personal_quota,
        used_tokens=user.used_tokens,
        available_quota=user.available_quota,
        default_priority=user.default_priority.value,
        preferences=safe_json_parse(user.preferences_json)
    )

@router.put("/users/me", response_model=UserResponse)
async def update_my_profile(
    updates: UserProfileUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update current user profile."""
    if updates.email is not None and updates.email != user.email:
        # Check if email is taken
        existing = session.exec(select(User).where(User.email == updates.email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = updates.email
    
    if updates.name is not None:
        user.name = updates.name
        
    if updates.preferences is not None:
        user.preferences_json = json.dumps(updates.preferences)
        
    session.add(user)
    session.commit()
    session.refresh(user)
    
    def safe_json_parse(data: Optional[str]) -> dict:
        if not data: return {}
        try: return json.loads(data)
        except Exception: return {}
        
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        status=user.status.value,
        personal_quota=user.personal_quota,
        used_tokens=user.used_tokens,
        available_quota=user.available_quota,
        default_priority=user.default_priority.value,
        preferences=safe_json_parse(user.preferences_json)
    )

@router.get("/users/me/quota", response_model=QuotaStatusResponse)
async def get_quota_status(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get detailed quota status including team and vacation sharing."""
    from ..logic import QuotaManager
    qm = QuotaManager(session)
    
    return QuotaStatusResponse(
        personal_quota=user.personal_quota,
        used_tokens=user.used_tokens,
        available_quota=user.available_quota,
        team_pool_available=qm._get_total_team_pool(user),
        vacation_share_available=qm._get_vacation_share_credits(user),
        status=user.status.value
    )

@router.post("/users/me/status")
async def update_user_status(
    status: UserStatus,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update current user's status (e.g., set to vacation)."""
    user.status = status
    session.add(user)
    session.commit()
    
    # Send notification if status changed to vacation
    if status == UserStatus.ON_VACATION:
        from ..metrics import vacation_mode_activations
        vacation_mode_activations.labels(user_id=str(user.id)).inc()

        from ..integrations import emit_vacation_status_change
        create_background_task(emit_vacation_status_change(
            user_id=str(user.id),
            user_name=user.name,
            user_email=user.email,
            on_vacation=True
        ))
        
    return {"message": f"Status updated to {status.value}"}

@router.post("/users/me/privacy")
async def update_privacy_preference(
    mode: Optional[str] = Query(None, alias='mode'),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update user's default privacy preference."""
    if mode is None:
        raise HTTPException(status_code=400, detail="Mode parameter required")
        
    user.strict_privacy_default = (mode.lower() == "strict")
    session.add(user)
    session.commit()
    
    return {"strict_privacy": user.strict_privacy_default}
