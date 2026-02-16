import asyncio
import uuid
from typing import Any, Coroutine, Generator, Optional

from fastapi import Depends, Header
from sqlmodel import Session, select

from .database import engine
from .exceptions import AuthenticationException, AuthorizationException
from .integrations import sso_manager
from .logging_config import get_logger
from .logic import AuthManager
from .models import User

logger = get_logger(__name__)

# Registry to prevent background tasks from being garbage collected prematurely
_background_tasks: set[asyncio.Task] = set()


def create_background_task(coro: Coroutine[Any, Any, Any]) -> asyncio.Task:
    """
    Fire-and-Forget Task Monitor.

    [BUG-012 FIX] Implemented a task registry to prevent memory leaks and
    ensure that tasks are not prematurely garbage collected. Includes
    lifecycle logging for observability.
    """

    async def task_wrapper():
        try:
            await coro
        except Exception as e:
            logger.error(f"Background Job Failed: {str(e)}", exc_info=True)

    task = asyncio.create_task(task_wrapper())
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task


def get_session() -> Generator:
    """Injected database session utilizing the connection pool."""
    with Session(engine) as session:
        yield session


async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    session: Session = Depends(get_session),
) -> User:
    """
    Unified Authentication Engine.

    Precedence:
    1. Header: Authorization Bearer (SSO Token - JWT Validation)
    2. Header: Authorization Bearer (Legacy/Script API Key)
    3. Header: X-API-Key (Classic Integration)
    """
    api_key = None
    user: Optional[User] = None

    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        # A. SSO Integration Path
        if sso_manager:
            try:
                sso_user = await sso_manager.validate_token(token)
                # JIT User Provisioning: Automate onboarding if domain is trusted
                user = session.exec(select(User).where(User.email == sso_user.email)).first()
                if not user:
                    _, api_key_hash = AuthManager.generate_api_key()
                    user = User(
                        id=uuid.uuid4(),
                        email=sso_user.email,
                        name=sso_user.name or sso_user.email.split("@")[0],
                        api_key_hash=api_key_hash,
                    )
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                    logger.info(f"Provisioned new JIT user: {user.email}")
            except Exception:
                # [BUG-003 FIX] Security Hardening: Only fallback if it's not a JWT
                if token.count(".") == 2:
                    raise AuthenticationException(
                        "Identity Verification Failed: Secure token invalid or expired."
                    )
                api_key = token
        else:
            api_key = token
    elif x_api_key:
        api_key = x_api_key

    # B. API Key Path (If SSO failed or wasn't present)
    if api_key and not user:
        api_key_hash = AuthManager.hash_api_key(api_key)
        user = session.exec(select(User).where(User.api_key_hash == api_key_hash)).first()

    if not user:
        raise AuthenticationException("Access Denied: Valid SSO token or API Key required.")

    if user.status.value == "suspended":
        raise AuthorizationException("Account Restricted: Please contact your administrative lead.")

    return user


def get_privacy_mode(
    x_privacy_mode: Optional[str] = Header(None, alias="X-Privacy-Mode"),
    user: User = Depends(get_current_user),
) -> bool:
    """
    Dynamic Content Governance.

    Determines if request payloads should be scrubbed before logging.
    Priority: Header Override > Global Org Default > User Preference.
    """
    if x_privacy_mode and x_privacy_mode.lower() == "strict":
        return True
    return user.strict_privacy_default


def require_admin(user: User = Depends(get_current_user)) -> User:
    """RBAC Firewall: Restricts access to administrative endpoints."""
    if not user.is_admin:
        raise AuthorizationException("Access Denied: Insufficient Administrative Permissions.")
    return user
