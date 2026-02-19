import asyncio
import os
from typing import Any, Coroutine, Generator, Optional

import app.database as _app_db
from fastapi import Depends, Header
from sqlmodel import Session, select

from .exceptions import AuthenticationException, AuthorizationException
from .logging_config import get_logger
from .models import User

logger = get_logger(__name__)

# Registry to prevent background tasks from being garbage collected prematurely
_background_tasks: set[asyncio.Task] = set()

# JWT configuration — load from environment
_JWT_SECRET = os.getenv("JWT_SECRET", "")
_JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


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
    with Session(_app_db.get_engine()) as session:
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
    """Validate Authorization header (Bearer token).

    Precedence:
    1. Try as API key (legacy tests use 'Bearer <api_key>')
    2. Decode as JWT and look up user by email claim
    """
    if not authorization:
        return None
    if not authorization.lower().startswith("bearer "):
        return None

    token = authorization.split(" ", 1)[1].strip()

    # Try API key flow first (legacy/script usage)
    user = await validate_api_key(token, session)
    if user:
        return user

    # JWT validation
    if not _JWT_SECRET:
        logger.debug("validate_authorization: JWT_SECRET not configured, skipping JWT flow")
        return None

    try:
        import jwt

        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
        email = payload.get("sub") or payload.get("email")
        if not email:
            logger.debug("validate_authorization: JWT missing 'sub'/'email' claim")
            return None

        from .models import User as UserModel

        user = session.exec(select(UserModel).where(UserModel.email == email)).first()
        if user:
            logger.debug("validate_authorization: JWT validated for %s", email)
        else:
            logger.debug("validate_authorization: no user found for JWT email=%s", email)
        return user
    except ImportError:
        logger.warning("validate_authorization: PyJWT not installed — JWT validation unavailable")
        return None
    except Exception as exc:
        logger.debug("validate_authorization: JWT decode failed: %s", exc)
        return None


async def validate_api_key(api_key: str, session: Session) -> Optional[User]:
    """Validate an API key by hashing and looking up in the database."""
    if not api_key:
        return None
    try:
        from .logic import AuthManager
        from .models import User as UserModel

        api_hash = AuthManager.hash_api_key(api_key)
        logger.debug("validate_api_key: computed hash=%s", api_hash)

        # Test override: allow a single API key defined in environment to bypass DB
        # lookup for adapter/QA tests. Returns a minimal User with admin privileges.
        test_key = os.getenv("ALFRED_TEST_API_KEY")
        if test_key and test_key == api_key:
            try:
                u = UserModel(
                    email="admin@example.com",
                    name="Admin (test)",
                    api_key_hash=api_hash,
                    is_admin=True,
                )
                logger.debug("validate_api_key: test override matched, returning synthetic admin")
                return u
            except Exception:
                logger.debug("validate_api_key: test override synthetic user creation failed")

        # SQLModel query — single source of truth
        u = session.exec(select(UserModel).where(UserModel.api_key_hash == api_hash)).first()
        logger.debug("validate_api_key: query result=%s", bool(u))
        return u
    except Exception:
        logger.debug("validate_api_key: exception during validation", exc_info=True)
        return None


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
