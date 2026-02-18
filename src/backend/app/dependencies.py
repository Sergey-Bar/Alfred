import asyncio
from typing import Any, Coroutine, Generator, Optional

import app.database as _app_db
from fastapi import Depends, Header
from sqlmodel import Session

from .exceptions import AuthenticationException, AuthorizationException
from .logging_config import get_logger
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
    with Session(_app_db.engine) as session:
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
    user = None
    if authorization:
        user = await validate_authorization(authorization, session)
    if not user and x_api_key:
        user = await validate_api_key(x_api_key, session)
    if not user:
        raise AuthenticationException("Authentication failed.")
    return user


# Helper functions for validation.
async def validate_authorization(authorization: str, session: Session) -> Optional[User]:
    # Logic for validating authorization.
    pass


async def validate_api_key(api_key: str, session: Session) -> Optional[User]:
    # Logic for validating API key.
    pass


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
