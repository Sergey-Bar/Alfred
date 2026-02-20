"""
──────────────────────────────────────────────────────────────
Model:       Claude Sonnet 4.5
Tier:        L4 (Critical - Security/Auth)
Logic:       JWT token creation and validation utilities for SSO/RBAC.
             Provides secure JWT session management for authenticated users.
Root Cause:  Sprint task T214 - Complete security TODOs in SSO/RBAC code
Context:     Security-critical authentication infrastructure. Must use
             secure defaults, validate all tokens, handle expiration properly.
Suitability: L4 appropriate - authentication is security-critical, requires
             careful error handling and security best practices
──────────────────────────────────────────────────────────────
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt
from fastapi import HTTPException, status

from .config import settings


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token for authenticated users.
    
    Args:
        data: Claims to include in the token (email, user_id, roles, etc.)
        expires_delta: Token expiration time (default: from config)
        
    Returns:
        Encoded JWT token string
        
    Security:
    - Uses HS256 algorithm by default
    - Includes expiration time (exp claim)
    - Includes issued at time (iat claim)
    - Adds unique token ID (jti claim) for revocation tracking
    """
    to_encode = data.copy()
    
    # Set expiration
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": _generate_token_id(),  # Unique token ID for revocation
    })
    
    # Encode JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid, expired, or malformed
        
    Security:
    - Validates signature
    - Checks expiration
    - Verifies algorithm matches expected
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require_exp": True,
                "require_iat": True,
            }
        )
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token validation error: {str(e)}",
        )


def _generate_token_id() -> str:
    """Generate a unique token ID for JWT jti claim."""
    import secrets
    return secrets.token_urlsafe(16)


def get_token_expiration_time(expires_delta: Optional[timedelta] = None) -> datetime:
    """
    Get the expiration time for a token.
    
    Args:
        expires_delta: Custom expiration delta (default: from config)
        
    Returns:
        Expiration datetime in UTC
    """
    if expires_delta:
        return datetime.now(timezone.utc) + expires_delta
    else:
        return datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
