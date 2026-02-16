"""
Alfred SSO/OAuth2 Integration Module
Encapsulates SSO provider selection, token validation, and user info extraction.

[AI GENERATED]
Model: GitHub Copilot (GPT-4.1)
Logic: Modularizes SSO/OAuth2 logic for maintainability and extensibility.
Why: Centralizes SSO logic, simplifies adding new providers, and improves testability.
Root Cause: SSO logic was previously scattered in config and main app, making it hard to extend and maintain.
Context: This module is designed to support Okta, Azure AD, Google, Keycloak, and can be extended for others.
"""

from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel


class SSOProviderConfig(BaseModel):
    provider: str
    client_id: str
    client_secret: str
    issuer_url: str
    scopes: str = "openid profile email"


class SSOUserInfo(BaseModel):
    sub: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    provider: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


class SSOManager:
    """
    Central SSO/OAuth2 manager for Alfred.
    Supports provider selection, token validation, and user info extraction.

    Usage:
        config = SSOProviderConfig(...)
        sso = SSOManager(config)
        user_info = await sso.validate_token(token)
    """

    def __init__(self, config: SSOProviderConfig):
        self.config = config

    async def validate_token(self, token: str) -> SSOUserInfo:
        """
        Validate an OAuth2 access or ID token and extract user info.
        Supports OIDC discovery for standard providers.
        """
        # Discover OIDC endpoints
        discovery_url = f"{self.config.issuer_url}/.well-known/openid-configuration"
        async with httpx.AsyncClient() as client:
            resp = await client.get(discovery_url)
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to discover OIDC endpoints")
            oidc_config = resp.json()
            userinfo_endpoint = oidc_config.get("userinfo_endpoint")
            if not userinfo_endpoint:
                raise HTTPException(status_code=500, detail="No userinfo endpoint found")
            # Validate token and fetch user info
            headers = {"Authorization": f"Bearer {token}"}
            userinfo_resp = await client.get(userinfo_endpoint, headers=headers)
            if userinfo_resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid SSO token"
                )
            data = userinfo_resp.json()
            return SSOUserInfo(
                sub=data.get("sub"),
                email=data.get("email"),
                name=data.get("name"),
                picture=data.get("picture"),
                provider=self.config.provider,
                raw=data,
            )


# Example usage (in FastAPI dependency):
#
# from .integrations.sso import SSOManager, SSOProviderConfig
# sso_config = SSOProviderConfig(
#     provider="okta",
#     client_id="...",
#     client_secret="...",
#     issuer_url="https://dev-123456.okta.com/oauth2/default"
# )
# sso_manager = SSOManager(sso_config)
# user_info = await sso_manager.validate_token(token)
